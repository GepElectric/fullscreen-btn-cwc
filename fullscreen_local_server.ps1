param(
    [int]$Port = 8767
)

function Write-HttpJsonResponse {
    param(
        [Parameter(Mandatory = $true)][System.Net.Sockets.NetworkStream]$Stream,
        [int]$StatusCode = 200,
        [string]$StatusText = "OK",
        [Parameter(Mandatory = $true)]$Data
    )

    $json = $Data | ConvertTo-Json -Depth 6 -Compress
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $headerText = @(
        "HTTP/1.1 $StatusCode $StatusText"
        "Content-Type: application/json; charset=utf-8"
        "Content-Length: $($bodyBytes.Length)"
        "Access-Control-Allow-Origin: *"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS"
        "Access-Control-Allow-Headers: *"
        "Connection: close"
        ""
        ""
    ) -join "`r`n"

    $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($headerText)
    $Stream.Write($headerBytes, 0, $headerBytes.Length)
    $Stream.Write($bodyBytes, 0, $bodyBytes.Length)
    $Stream.Flush()
}

function Invoke-FullscreenToggle {
    $shell = New-Object -ComObject WScript.Shell
    Start-Sleep -Milliseconds 120
    $shell.SendKeys("{F11}")
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), $Port)
$listener.Start()

Write-Host "Fullscreen helper listening on http://127.0.0.1:$Port/"

try {
    while ($true) {
        $client = $listener.AcceptTcpClient()

        try {
            $stream = $client.GetStream()
            $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII, $false, 1024, $true)

            $requestLine = $reader.ReadLine()
            if ([string]::IsNullOrWhiteSpace($requestLine)) {
                Write-HttpJsonResponse -Stream $stream -StatusCode 400 -StatusText "Bad Request" -Data @{ error = "Empty request." }
                continue
            }

            $requestParts = $requestLine.Split(" ")
            $method = if ($requestParts.Length -ge 1) { $requestParts[0].ToUpperInvariant() } else { "" }
            $rawTarget = if ($requestParts.Length -ge 2) { $requestParts[1] } else { "/" }
            $uri = [System.Uri]::new("http://127.0.0.1:$Port$rawTarget")
            $path = $uri.AbsolutePath

            while ($true) {
                $headerLine = $reader.ReadLine()
                if ($null -eq $headerLine -or $headerLine -eq "") {
                    break
                }
            }

            if ($method -eq "OPTIONS") {
                Write-HttpJsonResponse -Stream $stream -StatusCode 204 -StatusText "No Content" -Data @{}
                continue
            }

            if ($path -eq "/health") {
                Write-HttpJsonResponse -Stream $stream -Data @{
                    ok = $true
                    port = $Port
                    helper = "fullscreen"
                }
                continue
            }

            if ($path -eq "/fullscreen/toggle") {
                Invoke-FullscreenToggle
                Write-HttpJsonResponse -Stream $stream -Data @{
                    ok = $true
                    action = "toggle"
                }
                continue
            }

            Write-HttpJsonResponse -Stream $stream -StatusCode 404 -StatusText "Not Found" -Data @{
                error = "Not found."
            }
        } catch {
            try {
                if ($stream) {
                    Write-HttpJsonResponse -Stream $stream -StatusCode 500 -StatusText "Internal Server Error" -Data @{
                        error = $_.Exception.Message
                    }
                }
            } catch {
            }
        } finally {
            if ($reader) {
                $reader.Dispose()
            }
            if ($stream) {
                $stream.Dispose()
            }
            $client.Close()
        }
    }
} finally {
    $listener.Stop()
}

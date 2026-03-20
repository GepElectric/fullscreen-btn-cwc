@echo off
setlocal

set "PYTHONW=C:\Users\Mazda\AppData\Local\Programs\Python\Python314\pythonw.exe"
set "WORKDIR=%~dp0"
set "SCRIPT=fullscreen_local_server.py"

for /f "tokens=2 delims=," %%A in ('tasklist /fo csv /nh /fi "IMAGENAME eq pythonw.exe" ^| findstr /i "pythonw.exe"') do (
    taskkill /f /pid %%~A >nul 2>&1
)
for /f "tokens=2 delims=," %%A in ('tasklist /fo csv /nh /fi "IMAGENAME eq python.exe" ^| findstr /i "python.exe"') do (
    taskkill /f /pid %%~A >nul 2>&1
)

if exist "%PYTHONW%" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Start-Process -FilePath '%PYTHONW%' -WorkingDirectory '%WORKDIR%' -ArgumentList '%SCRIPT%' -PassThru; Start-Sleep -Milliseconds 1200; try { (Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8767/health').Content | Out-Null; Write-Host 'Fullscreen helper started.' } catch { Write-Error 'Fullscreen helper did not start correctly.'; if ($p -and !$p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }; exit 1 }"
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = Start-Process -FilePath 'python' -WorkingDirectory '%WORKDIR%' -ArgumentList '%SCRIPT%' -PassThru; Start-Sleep -Milliseconds 1200; try { (Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8767/health').Content | Out-Null; Write-Host 'Fullscreen helper started.' } catch { Write-Error 'Fullscreen helper did not start correctly.'; if ($p -and !$p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }; exit 1 }"
)

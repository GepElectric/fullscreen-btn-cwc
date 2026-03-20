@echo off
setlocal

set "GUID={B5EE6DEF-00EB-4880-AC1E-39A6AF506363}"
set "SRC=%~dp0{B5EE6DEF-00EB-4880-AC1E-39A6AF506363}"
set "DEST=C:\Ballsh Share Folder\Ballsh_BCK_V21\UserFiles\CustomControls"
set "ZIPNAME=%GUID%.zip"
set "TMPZIP=%SRC%\%ZIPNAME%"
set "DESTZIP=%DEST%\%ZIPNAME%"

echo ====================================
echo  ScreenControl CWC Deploy
echo ====================================
echo.
echo Source:  %SRC%
echo Target:  %DESTZIP%
echo.

:: Delete old zip if exists
if exist "%TMPZIP%" del /q "%TMPZIP%"

:: Create zip using PowerShell (zip only manifest.json, assets/, control/)
echo Zipping...
powershell -NoProfile -Command ^
  "$src = '%SRC%'; " ^
  "$zip = '%TMPZIP%'; " ^
  "Add-Type -AssemblyName System.IO.Compression.FileSystem; " ^
  "$archive = [System.IO.Compression.ZipFile]::Open($zip, 'Create'); " ^
  "function Add-Entry($file, $entry) { " ^
  "  [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $file, $entry, 'Optimal') | Out-Null " ^
  "} " ^
  "Add-Entry (Join-Path $src 'manifest.json') 'manifest.json'; " ^
  "Get-ChildItem (Join-Path $src 'assets') -File | ForEach-Object { " ^
  "  Add-Entry $_.FullName ('assets/' + $_.Name) " ^
  "}; " ^
  "Get-ChildItem (Join-Path $src 'control') -File -Recurse | ForEach-Object { " ^
  "  $rel = $_.FullName.Substring((Join-Path $src 'control\').Length); " ^
  "  Add-Entry $_.FullName ('control/' + $rel.Replace('\','/')) " ^
  "}; " ^
  "$archive.Dispose(); " ^
  "Write-Host ('Created: ' + $zip); " ^
  "Write-Host ('Size: ' + [math]::Round((Get-Item $zip).Length / 1MB, 2) + ' MB')"

if not exist "%TMPZIP%" (
  echo ERROR: Zip creation failed!
  pause
  exit /b 1
)

:: Copy to TIA project
echo.
echo Copying to TIA project...
copy /y "%TMPZIP%" "%DESTZIP%"

if %errorlevel% equ 0 (
  echo.
  echo ====================================
  echo  DONE! Deployed to CustomControls
  echo ====================================
) else (
  echo ERROR: Copy failed!
)

echo.
pause

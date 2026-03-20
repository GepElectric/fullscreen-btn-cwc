# Full Screen Button CWC

`Full screen btn` is a WinCC Unified Custom Web Control that triggers reliable fullscreen enter/exit behavior using a dedicated local helper backend.

## Repository Contents

- `deploy_cwc.bat`: builds and copies the CWC ZIP to the WinCC `CustomControls` folder
- `{B5EE6DEF-00EB-4880-AC1E-39A6AF506363}/`: CWC manifest and frontend assets
- `fullscreen_local_server.py`: primary local fullscreen helper
- `fullscreen_local_server.ps1`: legacy helper variant
- `start_fullscreen_local_server.bat`: starts and validates the local helper
- `_ModuleTemplate_extract/`: companion/module packaging source
- `FullscreenModule.zip`: built module package

## What It Does

- enters fullscreen through a local helper
- exits fullscreen through a local helper
- falls back to browser fullscreen APIs if the helper is unavailable
- supports explicit `enter`, `exit`, and `toggle` behavior

## Local Development

1. Start the helper with `start_fullscreen_local_server.bat`
2. Deploy the CWC with `deploy_cwc.bat`
3. Test the helper health endpoint at `http://127.0.0.1:8767/health`

## Notes

- the Python helper is the active backend
- the packaged module is intended for deployment alongside the CWC
- the PowerShell helper is retained only as an older implementation

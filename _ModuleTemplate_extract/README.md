Fullscreen Module

This Companion/Hosted module starts a localhost helper on `127.0.0.1:8767`
for the `Full screen btn` CWC.

The CWC is expected to target this helper first. If the helper is not
available, only then should the browser fullscreen fallback be used.

What it provides:
- `/health`
- `/fullscreen/enter`
- `/fullscreen/exit`
- `/fullscreen/toggle`

The helper sends `F11` on the local Windows machine, which is more reliable
for browser fullscreen than using the browser Fullscreen API from inside a CWC.

Hosted commands:
- `open_main_window`
- `toggle_fullscreen`
- `get_status`
- `shutdown`

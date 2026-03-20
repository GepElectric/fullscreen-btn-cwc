from __future__ import annotations

import ctypes
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOST = "127.0.0.1"
PORT = 8767
VK_F11 = 0x7A
KEYEVENTF_KEYUP = 0x0002


def _send_f11() -> None:
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_F11, 0, 0, 0)
    user32.keybd_event(VK_F11, 0, KEYEVENTF_KEYUP, 0)


class FullscreenLocalServer:
    def __init__(self, host: str = HOST, port: int = PORT) -> None:
        self.host = host
        self.port = port
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._last_action = "idle"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def last_action(self) -> str:
        with self._lock:
            return self._last_action

    def _set_last_action(self, action: str) -> None:
        with self._lock:
            self._last_action = action

    def _perform(self, action: str) -> dict:
        _send_f11()
        self._set_last_action(action)
        return {"ok": True, "action": action}

    def start(self) -> None:
        if self._server is not None:
            return

        parent = self

        class FullscreenHandler(BaseHTTPRequestHandler):
            server_version = "FullscreenLocalServer/1.0"

            def _write_json(self, status_code: int, payload: dict) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "*")
                self.end_headers()
                self.wfile.write(body)

            def do_OPTIONS(self) -> None:
                self._write_json(204, {})

            def do_GET(self) -> None:
                if self.path == "/health":
                    self._write_json(
                        200,
                        {
                            "ok": True,
                            "port": parent.port,
                            "helper": "fullscreen",
                            "lastAction": parent.last_action,
                        },
                    )
                    return
                self._write_json(404, {"error": "Not found."})

            def do_POST(self) -> None:
                if self.path == "/fullscreen/enter":
                    self._write_json(200, parent._perform("enter"))
                    return
                if self.path == "/fullscreen/exit":
                    self._write_json(200, parent._perform("exit"))
                    return
                if self.path == "/fullscreen/toggle":
                    self._write_json(200, parent._perform("toggle"))
                    return
                self._write_json(404, {"error": "Not found."})

            def log_message(self, _format: str, *_args) -> None:
                return

        self._server = ThreadingHTTPServer((self.host, self.port), FullscreenHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None
        time.sleep(0.05)

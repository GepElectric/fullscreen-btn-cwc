import ctypes
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
import time


HOST = "127.0.0.1"
PORT = 8767
VK_F11 = 0x7A
KEYEVENTF_KEYUP = 0x0002


def send_f11():
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_F11, 0, 0, 0)
    user32.keybd_event(VK_F11, 0, KEYEVENTF_KEYUP, 0)


def perform_toggle():
    send_f11()
    return {"ok": True, "action": "toggle"}


def perform_enter():
    send_f11()
    return {"ok": True, "action": "enter"}


def perform_exit():
    send_f11()
    return {"ok": True, "action": "exit"}


class FullscreenHandler(BaseHTTPRequestHandler):
    server_version = "FullscreenLocalServer/1.0"

    def _write_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._write_json(204, {})

    def do_GET(self):
        if self.path == "/health":
            self._write_json(200, {"ok": True, "port": PORT, "helper": "fullscreen"})
            return

        self._write_json(404, {"error": "Not found."})

    def do_POST(self):
        if self.path == "/fullscreen/enter":
            self._write_json(200, perform_enter())
            return

        if self.path == "/fullscreen/exit":
            self._write_json(200, perform_exit())
            return

        if self.path == "/fullscreen/toggle":
            self._write_json(200, perform_toggle())
            return

        self._write_json(404, {"error": "Not found."})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    try:
        server = ThreadingHTTPServer((HOST, PORT), FullscreenHandler)
    except OSError as error:
        print(f"Failed to bind fullscreen helper on {HOST}:{PORT}: {error}", file=sys.stderr)
        sys.exit(1)

    print(f"Fullscreen helper listening on http://{HOST}:{PORT}/")

    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        time.sleep(0.05)
        server.server_close()

#!/usr/bin/env python3
"""CyFun Dashboard server — serves static files and auto-saves scores to disk.

Configuration (environment variables):
    HOST  Interface to bind to (default: 127.0.0.1; the Docker image sets 0.0.0.0)
    PORT  TCP port (default: 8088)
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8088"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "scores.json")
MAX_BODY_BYTES = 5 * 1024 * 1024  # scores.json is a few KB; refuse anything absurd


def validate_payload(data):
    """Return an error string if `data` is not a valid scores payload, else None."""
    if not isinstance(data, dict):
        return "payload must be a JSON object"
    if not isinstance(data.get("scores", {}), dict):
        return "'scores' must be an object"
    if "level" in data and data["level"] not in ("Basic", "Important", "Essential"):
        return "'level' must be Basic, Important or Essential"
    return None


class CyFunHandler(SimpleHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/save":
            self._send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._send_json(400, {"error": "invalid Content-Length"})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send_json(413 if length > MAX_BODY_BYTES else 400,
                            {"error": "invalid body size"})
            return
        try:
            data = json.loads(self.rfile.read(length))
            error = validate_payload(data)
            if error:
                self._send_json(400, {"error": error})
                return
            # Serialise first so a failure never truncates the existing file.
            # Written in place (no rename) so single-file Docker bind mounts work.
            serialized = json.dumps(data, indent=2)
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                f.write(serialized)
            self._send_json(200, {"ok": True})
        except json.JSONDecodeError as e:
            self._send_json(400, {"error": f"invalid JSON: {e}"})
        except Exception as e:  # noqa: BLE001 - report any I/O failure to the client
            self._send_json(500, {"error": str(e)})

    def end_headers(self):
        # Always revalidate: scores.json changes underneath the browser cache.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_request(self, code="-", size="-"):
        # Only log failed requests, not every successful one.
        status = str(getattr(code, "value", code))
        if status.startswith(("2", "3")):
            return
        super().log_request(code, size)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    server = HTTPServer((HOST, PORT), CyFunHandler)
    print(f"CyFun Dashboard running at http://{'localhost' if HOST in ('127.0.0.1', '0.0.0.0') else HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()

#!/usr/bin/env python3
"""CyFun Dashboard server — serves static files and auto-saves scores to disk."""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8088
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")


class CyFunHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                with open(SAVE_FILE, "w") as f:
                    json.dump(data, f, indent=2)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Only log errors, not every request
        if args and "200" not in str(args[1]):
            super().log_message(format, *args)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("", PORT), CyFunHandler)
    print(f"CyFun Dashboard running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()

#!/usr/bin/env python3

import http.server
import os
import socketserver

try:
    from sync_dashboard import generate_dashboard
except ModuleNotFoundError:
    from tools.sync_dashboard import generate_dashboard


PORT = 8000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path in {"/habits/dashboard.html", "/habits/dashboard.md"}:
            generate_dashboard()
        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    generate_dashboard()
    with ReusableTCPServer(("", PORT), NoCacheHandler) as httpd:
        print(f"Serving dashboard at http://localhost:{PORT}/habits/dashboard.html")
        print("Press Ctrl+C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

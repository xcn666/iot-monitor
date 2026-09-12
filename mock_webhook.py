#!/usr/bin/env python3
# mock_webhook.py - 本地模拟 webhook 服务器(测试推送用)
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        print(f"[收到推送] {body}", flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    print("模拟 webhook 服务器: http://localhost:8899/hook", flush=True)
    HTTPServer(("0.0.0.0", 8899), Handler).serve_forever()

#!/usr/bin/env python
"""
auto_import.py — PWA 照片接收伺服器 v1.1
監聽手機上傳的照片，儲存至當日待分類相片
"""
import os, json, re, socket
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE = r"C:\M\各店日巡"
PHOTO_DIR = os.path.join(BASE, "照片分類模板")
TEMP_DIR = os.path.join(BASE, "當日待分類相片")
LOG_FILE = os.path.expanduser("~/Desktop/auto_import_log.txt")
HOST, PORT = "0.0.0.0", 8765

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()

class ImportHandler(BaseHTTPRequestHandler):
    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_response(200)
            self.send_cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            ip = get_local_ip()
            self.wfile.write(f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>auto_import</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:sans-serif;max-width:600px;margin:20px;}}
.ok{{background:#e6f4ea;color:#137333;padding:12px;border-radius:8px;margin:8px 0;}}
.ip{{background:#e8f0fe;color:#1967d2;padding:12px;border-radius:8px;margin:8px 0;}}</style>
</head><body>
<h2>📡 auto_import 接收端</h2>
<div class="ok">✅ 伺服器運行中</div>
<div class="ip">📱 手機同步頁面填入：<strong>{ip}:{PORT}</strong></div>
<div class="ip">📂 照片儲存：{TEMP_DIR}</div>
</body></html>""".encode())
            return
        if path == "/health":
            self.send_response(200)
            self.send_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status":"ok"}).encode())
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        self.send_cors()
        path = urlparse(self.path).path
        if path == "/api/upload":
            self.handle_upload()
            return
        self.send_response(404)
        self.end_headers()

    def handle_upload(self):
        try:
            ct = self.headers.get("Content-Type", "")
            if "boundary=" not in ct:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"no boundary"}')
                return
            boundary = ct.split("boundary=")[1].split(";")[0].strip()
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)

            os.makedirs(TEMP_DIR, exist_ok=True)
            uploaded = []
            for part in body.split(("--" + boundary).encode()):
                if b"Content-Disposition" not in part:
                    continue
                m = re.search(rb'filename="([^"]*)"', part)
                if not m:
                    continue
                fname = m.group(1).decode('utf-8', errors='replace')
                blank = part.find(b'\r\n\r\n')
                if blank == -1:
                    continue
                data = part[blank+4:].rstrip(b'\r\n- ')
                if not data:
                    continue
                sp = os.path.join(TEMP_DIR, fname)
                with open(sp, 'wb') as f:
                    f.write(data)
                uploaded.append(fname)
                log(f"  {fname} ({len(data):,} bytes)")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            res = json.dumps({"status":"ok","count":len(uploaded),"files":uploaded}, ensure_ascii=False)
            self.wfile.write(res.encode())
            log(f"✅ {len(uploaded)} 張")
        except Exception as e:
            log(f"❌ {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error":str(e)}).encode())

    def log_message(self, fmt, *args):
        log(f"[{self.client_address[0]}] {fmt % args}")

if __name__ == "__main__":
    os.makedirs(PHOTO_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    ip = get_local_ip()
    log(f"🚀 auto_import 啟動 http://{ip}:{PORT}")
    log(f"📂 {TEMP_DIR}")
    HTTPServer((HOST, PORT), ImportHandler).serve_forever()

#!/usr/bin/env python
"""
pwa_server.py — 整合伺服器 v2.0
在 port 8080 上同時提供：
  - GET /*       → PWA 靜態檔案（C:\M\PWA\）
  - POST /api/upload → 接收 WiFi 同步照片上傳
  - OPTIONS /*   → CORS preflight

解決 Chrome Private Network Access 跨埠阻擋問題。
合併 PWA 前端 + 上傳接收端在同一個埠，避免跨埠 fetch 被 Chrome 阻擋。
"""
import os, json, re, socket, mimetypes
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ── 路徑設定 ──────────────────────────────────
PWA_DIR = r"C:\M\PWA"
TEMP_DIR = r"C:\M\各店日巡\當日待分類相片"
LOG_FILE = os.path.expanduser("~/Desktop/pwa_server_log.txt")
HOST, PORT = "0.0.0.0", 8080


# ── 工具函式 ──────────────────────────────────
def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


# ── HTTP Handler ──────────────────────────────
class PwaHandler(BaseHTTPRequestHandler):
    """處理 PWA 靜態檔案服務與上傳接收的 HTTP handler。"""

    # ── CORS ──────────────────────────────
    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # 允許 Service Worker fetch 跨來源
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        """處理 CORS preflight 請求。"""
        self.send_response(200, "OK")
        self.send_cors()
        self.end_headers()

    # ── GET：靜態檔案 ──────────────────────
    def do_GET(self):
        path = urlparse(self.path).path

        # 根路徑 → index.html
        if path == "/":
            path = "/index.html"

        # 路徑穿越防護
        safe_path = os.path.normpath(os.path.join(PWA_DIR, path.lstrip("/")))
        if not safe_path.startswith(os.path.normpath(PWA_DIR)):
            self.send_error(403, "Forbidden")
            return

        # /health 端點（auto_import 相容）
        if path == "/health":
            self.send_response(200)
            self.send_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "port": PORT}).encode())
            return

        # 服務靜態檔案
        if os.path.isfile(safe_path):
            self.send_response(200)
            self.send_cors()
            content_type, _ = mimetypes.guess_type(safe_path)
            self.send_header("Content-Type", content_type or "application/octet-stream")
            self.end_headers()
            with open(safe_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Not Found")

    # ── POST：上傳接收 ─────────────────────
    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/upload":
            self.handle_upload()
        else:
            self.send_response(404)
            self.send_cors()
            self.end_headers()

    def handle_upload(self):
        """處理 multipart/form-data 照片上傳。"""
        try:
            ct = self.headers.get("Content-Type", "")
            if "boundary=" not in ct:
                self.send_response(400)
                self.send_cors()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error":"no boundary"}')
                return

            boundary = ct.split("boundary=")[1].split(";")[0].strip()
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)

            os.makedirs(TEMP_DIR, exist_ok=True)
            uploaded = []

            # 解析 multipart 各段落
            separator = ("--" + boundary).encode()
            for part in body.split(separator):
                if b"Content-Disposition" not in part:
                    continue
                # 取檔名
                m = re.search(rb'filename="([^"]*)"', part)
                if not m:
                    continue
                fname = m.group(1).decode("utf-8", errors="replace")

                # 找到 body 空白行（標頭與資料的分界）
                blank = part.find(b"\r\n\r\n")
                if blank == -1:
                    continue
                data = part[blank + 4 :].rstrip(b"\r\n- ")
                if not data:
                    continue

                save_path = os.path.join(TEMP_DIR, fname)
                with open(save_path, "wb") as f:
                    f.write(data)
                uploaded.append(fname)
                log(f"📥 {fname} ({len(data):,} bytes)")

            self.send_response(200)
            self.send_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            res = json.dumps(
                {"status": "ok", "count": len(uploaded), "files": uploaded},
                ensure_ascii=False,
            )
            self.wfile.write(res.encode())
            log(f"✅ {len(uploaded)} 張上傳完成")

        except Exception as e:
            log(f"❌ {e}")
            self.send_response(500)
            self.send_cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, fmt, *args):
        log(f"[{self.client_address[0]}] {fmt % args}")


# ── 啟動入口 ──────────────────────────────────
if __name__ == "__main__":
    ip = get_local_ip()
    os.makedirs(TEMP_DIR, exist_ok=True)

    log("=" * 50)
    log(f"🚀 PWA 整合伺服器啟動 v2.0")
    log(f"📡 PWA 拍照頁面:  http://{ip}:{PORT}")
    log(f"📡 上傳端點:     http://{ip}:{PORT}/api/upload")
    log(f"📂 上傳儲存目錄: {TEMP_DIR}")
    log(f"📝 日誌檔案:     {LOG_FILE}")
    log("=" * 50)

    server = HTTPServer((HOST, PORT), PwaHandler)
    server.serve_forever()

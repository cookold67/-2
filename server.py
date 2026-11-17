import os
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

def setup_environment():
    with open("secret.env", "w", encoding="utf-8") as f:
        f.write("DB_MASTER_PASSWORD=TopSecretPass99!\n")
    
    os.makedirs("public", exist_ok=True)
    with open("public/info.txt", "w", encoding="utf-8") as f:
        f.write("Публичная информация системы.\n")

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'AdminSecret2026', 'superadmin')")
cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest', 'user')")
conn.commit()

class VulnerableHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/file":
            params = parse_qs(parsed_url.query)
            filename = params.get("name", [""])[0]
            base_dir = os.path.abspath("public")
            filepath = os.path.abspath(os.path.join(base_dir, filename))

            if not filepath.startswith(base_dir + os.sep):
                self._send_json(403, {"error": "Доступ запрещен"})
                return

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self._send_json(200, {"file": filename, "content": content})
            except FileNotFoundError:
                self._send_json(404, {"error": "Файл не найден"})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Маршрут не найден"})

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Некорректный JSON"})
                return

            username = data.get("username", "")
            password = data.get("password", "")

            query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            try:
                cursor.execute(query, (username, password))
                user = cursor.fetchone()
                if user:
                    self._send_json(200, {"status": "authenticated", "user": user[0], "role": user[1]})
                else:
                    self._send_json(401, {"status": "denied", "message": "Неверный логин или пароль"})
            except sqlite3.Error as e:
                self._send_json(500, {"error": str(e)})
        else:
            self._send_json(404, {"error": "Маршрут не найден"})

if __name__ == "__main__":
    setup_environment()
    server = HTTPServer(("127.0.0.1", 8080), VulnerableHandler)
    print("Сервер запущен на http://127.0.0.1:8080")
    server.serve_forever()

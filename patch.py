with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

old_1 = 'filepath = os.path.join("public", filename)'
new_1 = '''base_dir = os.path.abspath("public")
            filepath = os.path.abspath(os.path.join(base_dir, filename))

            if not filepath.startswith(base_dir + os.sep):
                self._send_json(403, {"error": "Доступ запрещен"})
                return'''

old_2 = '''query = f"SELECT username, role FROM users WHERE username = '{username}' AND password = '{password}'"
            try:
                cursor.execute(query)'''
new_2 = '''query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            try:
                cursor.execute(query, (username, password))'''

assert old_1 in code and old_2 in code, "Код уже пропатчен или не совпадает"
code = code.replace(old_1, new_1).replace(old_2, new_2)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Патч успешно применен к server.py!")

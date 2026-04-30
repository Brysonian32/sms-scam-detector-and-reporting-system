import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("scams.db")
conn.execute(
    "INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)",
    ("Capello", "brysonkipchirchir39@gmail.com", generate_password_hash("Bryce"), 1)
)
conn.commit()
conn.close()
print("Admin created successfully.")

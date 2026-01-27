# seed.py
import sqlite3
import os
import datetime

DB_PATH = os.getenv("DB_PATH", "users.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

demo_users = [
    ("+911234567890", "Alice"),
    ("+919876543210", "Bob"),
    ("+919999888877", "Charlie"),
]

for phone, name in demo_users:
    cur.execute("SELECT id FROM users WHERE phone = ?", (phone,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (phone, name, created_at) VALUES (?, ?, ?)",
                    (phone, name, datetime.datetime.utcnow().isoformat()))
        print(f"Inserted demo user {phone} / {name}")
    else:
        print(f"User {phone} already exists")

conn.commit()
conn.close()

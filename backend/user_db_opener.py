# user_db_opener.py
import sqlite3
import sys
import os

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "users.db"

if not os.path.exists(DB_PATH):
    print(f"DB not found at {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("Tables:")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(" -", row[0])

print("\nUsers:")
for r in cur.execute("SELECT id, phone, name, created_at FROM users ORDER BY id"):
    print(r)

conn.close()

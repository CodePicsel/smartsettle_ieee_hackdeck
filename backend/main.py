# main.py
import os
import time
import random
import sqlite3
import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Depends, Header
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt

# load .env
load_dotenv(".env")

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes")
DB_PATH = os.getenv("DB_PATH", "users.db")
OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "300"))
OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "30"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

# Init DB (ensure schema applied)
if not os.path.exists(DB_PATH):
    open(DB_PATH, "a").close()

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
# Create basic schema if not present
cur.executescript(open("schema.sql", "r").read())
conn.commit()

# In-memory OTP store for demo (use Redis in production)
otp_store = {}  # phone -> {otp, expires, sent_at, attempts}

app = FastAPI(title="SmartSettle - OTP Auth Demo")

class RequestOTPBody(BaseModel):
    phone: str

class VerifyOTPBody(BaseModel):
    phone: str
    otp: str
    name: Optional[str] = None

def current_ts() -> int:
    return int(time.time())

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def create_jwt_for_user(user_id: int, phone: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "phone": phone,
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@app.post("/auth/request-otp")
def request_otp(body: RequestOTPBody):
    phone = body.phone.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="phone is required")

    now = current_ts()
    entry = otp_store.get(phone)
    if entry and now - entry.get("sent_at", 0) < OTP_RESEND_COOLDOWN_SECONDS:
        raise HTTPException(status_code=429, detail=f"OTP requested too recently. Wait {OTP_RESEND_COOLDOWN_SECONDS}s.")

    otp = generate_otp()
    otp_store[phone] = {
        "otp": otp,
        "expires": now + OTP_TTL_SECONDS,
        "sent_at": now,
        "attempts": 0
    }

    # Simulate SMS: print to server logs
    print(f"[SIMULATED SMS] OTP for {phone} is {otp} (valid for {OTP_TTL_SECONDS}s)")

    return {"otp_sent": True, "message": "OTP sent (simulated). Replace with SMS provider for production."}


@app.post("/auth/verify-otp")
def verify_otp(body: VerifyOTPBody):
    phone = body.phone.strip()
    otp = body.otp.strip()

    if not phone or not otp:
        raise HTTPException(status_code=400, detail="phone and otp are required")

    entry = otp_store.get(phone)
    now = current_ts()

    if not entry or entry.get("expires", 0) < now:
        otp_store.pop(phone, None)
        raise HTTPException(status_code=400, detail="OTP invalid or expired. Request a new OTP.")

    if entry.get("otp") != otp:
        entry["attempts"] = entry.get("attempts", 0) + 1
        if entry["attempts"] >= OTP_MAX_ATTEMPTS:
            otp_store.pop(phone, None)
            raise HTTPException(status_code=400, detail="Too many incorrect attempts. OTP invalidated.")
        raise HTTPException(status_code=400, detail="OTP does not match.")

    # OTP correct: create or lookup user
    cur.execute("SELECT id, phone, name FROM users WHERE phone = ?", (phone,))
    row = cur.fetchone()
    if row:
        user = {"id": row[0], "phone": row[1], "name": row[2]}
    else:
        created_at = datetime.datetime.utcnow().isoformat()
        cur.execute("INSERT INTO users (phone, name, created_at) VALUES (?, ?, ?)", (phone, body.name, created_at))
        conn.commit()
        user_id = cur.lastrowid
        user = {"id": user_id, "phone": phone, "name": body.name}

    token = create_jwt_for_user(user["id"], phone)

    otp_store.pop(phone, None)

    return {"access_token": token, "token_type": "bearer", "user": user}


# DEV helper endpoints (only if DEV_MODE true)
@app.get("/auth/debug-otp")
def debug_otp(phone: str = Query(...)):
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")
    entry = otp_store.get(phone)
    if not entry:
        raise HTTPException(status_code=404, detail="No OTP for this phone")
    return {"phone": phone, "otp": entry["otp"], "expires_at": entry["expires"], "sent_at": entry["sent_at"]}

@app.get("/debug/users")
def debug_users():
    if not DEV_MODE:
        raise HTTPException(status_code=404, detail="Not found")
    cur.execute("SELECT id, phone, name, created_at FROM users ORDER BY id ASC")
    rows = cur.fetchall()
    users = [{"id": r[0], "phone": r[1], "name": r[2], "created_at": r[3]} for r in rows]
    return {"count": len(users), "users": users}

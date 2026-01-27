# main.py
import os
import time
import random
import sqlite3
import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Header, Depends, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt

# -------------------------
# Load env
# -------------------------
load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days default
DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes")
DB_PATH = os.getenv("DB_PATH", "users.db")
OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "300"))
OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "30"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
TEMP_TOKEN_EXPIRE_MINUTES = int(os.getenv("TEMP_TOKEN_EXPIRE_MINUTES", "1000"))  # expires quickly for registration

# -------------------------
# DB init (SQLite demo)
# -------------------------
if not os.path.exists(DB_PATH):
    open(DB_PATH, "a").close()

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
# simple schema
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP NOT NULL
);
""")
conn.commit()

# -------------------------
# OTP store (in-memory demo)
# -------------------------
otp_store = {}  # phone -> {otp, expires, sent_at, attempts}

app = FastAPI(title="SmartSettle - OTP + Conditional Registration")

# -------------------------
# Pydantic models
# -------------------------
class RequestOTPBody(BaseModel):
    phone: str

class VerifyOTPBody(BaseModel):
    phone: str
    otp: str

class RegisterBody(BaseModel):
    name: str

# -------------------------
# Helpers
# -------------------------
def current_ts() -> int:
    return int(time.time())

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def create_jwt_for_user(user_id: int, phone: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "phone": phone,
        "purpose": "access",
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_temp_token_for_phone(phone: str) -> str:
    """
    Short-lived token proving the phone was OTP-verified and can be used to register.
    purpose = otp_register
    """
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=TEMP_TOKEN_EXPIRE_MINUTES)
    payload = {
        "phone": phone,
        "purpose": "otp_register",
        "exp": int(expire.timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# -------------------------
# Auth endpoints
# -------------------------
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

    # Simulate SMS for demo — replace with provider API for production
    print(f"[SIMULATED SMS] OTP for {phone} is {otp} (valid for {OTP_TTL_SECONDS}s)")

    return {"otp_sent": True, "message": "OTP sent (simulated). In production integrate an SMS provider."}


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

    # OTP is correct. Do NOT auto-create user now.
    # Check if user exists:
    cur.execute("SELECT id, phone, name FROM users WHERE phone = ?", (phone,))
    row = cur.fetchone()

    # consume OTP (single-use)
    otp_store.pop(phone, None)

    if row:
        # user exists -> issue full access token
        user = {"id": row[0], "phone": row[1], "name": row[2]}
        token = create_jwt_for_user(user["id"], phone)
        return {"user_exists": True, "access_token": token, "token_type": "bearer", "user": user}
    else:
        # user does not exist -> issue a short-lived temp token for registration
        temp_token = create_temp_token_for_phone(phone)
        return {"user_exists": False, "temp_token": temp_token, "phone": phone, "message": "OTP verified. Register user with /auth/register using this temp_token."}


@app.post("/auth/register")
def register_user(body: RegisterBody, authorization: Optional[str] = Header(None)):
    """
    Register a new user after OTP verification.
    The frontend should send the temp_token as Authorization: Bearer <temp_token>
    """
    # Get temp token from Authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header with temp token")

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format. Use: Bearer <temp_token>")

    temp_token = authorization.split(" ", 1)[1].strip()
    payload = decode_jwt(temp_token)

    # ensure purpose is correct
    if payload.get("purpose") != "otp_register":
        raise HTTPException(status_code=401, detail="Invalid token purpose")

    phone = payload.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Temp token missing phone claim")

    # Safety: check user doesn't already exist (race)
    cur.execute("SELECT id FROM users WHERE phone = ?", (phone,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    # create user
    created_at = datetime.datetime.utcnow().isoformat()
    cur.execute("INSERT INTO users (phone, name, created_at) VALUES (?, ?, ?)", (phone, body.name, created_at))
    conn.commit()
    user_id = cur.lastrowid
    user = {"id": user_id, "phone": phone, "name": body.name}

    # issue full access token
    access_token = create_jwt_for_user(user_id, phone)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

# -------------------------
# Dev helper endpoints
# -------------------------
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

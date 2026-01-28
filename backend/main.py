# # main.py
# import os
# import time
# import random
# import sqlite3
# import datetime
# from typing import Optional

# from fastapi import FastAPI, HTTPException, Query, Header
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import jwt

# # CORS middleware
# from fastapi.middleware.cors import CORSMiddleware

# # -------------------------
# # Load env
# # -------------------------
# load_dotenv(".env")

# SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days default
# DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes")
# DB_PATH = os.getenv("DB_PATH", "users.db")
# OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "300"))
# OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "30"))
# OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
# # TEMP token lifetime (minutes)
# TEMP_TOKEN_EXPIRE_MINUTES = int(os.getenv("TEMP_TOKEN_EXPIRE_MINUTES", "1000"))

# # -------------------------
# # DB init (SQLite demo)
# # -------------------------
# if not os.path.exists(DB_PATH):
#     open(DB_PATH, "a").close()

# conn = sqlite3.connect(DB_PATH, check_same_thread=False)
# cur = conn.cursor()
# # simple schema
# cur.executescript("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     phone TEXT UNIQUE NOT NULL,
#     name TEXT,
#     created_at TIMESTAMP NOT NULL
# );
# """)
# conn.commit()

# # -------------------------
# # OTP store (in-memory demo)
# # -------------------------
# otp_store = {}  # phone -> {otp, expires, sent_at, attempts}

# app = FastAPI(title="SmartSettle - OTP + Conditional Registration")

# # -------------------------
# # CORS setup
# # -------------------------
# # Read comma-separated origins from env or fall back to common dev origins
# cors_env = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
# origins = [o.strip() for o in cors_env.split(",") if o.strip()]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,         # or ["*"] for quick dev (not recommended with allow_credentials=True)
#     allow_credentials=True,        # allows sending Authorization header/cookies from browser
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------------------
# # Pydantic models
# # -------------------------
# class RequestOTPBody(BaseModel):
#     phone: str

# class VerifyOTPBody(BaseModel):
#     phone: str
#     otp: str

# class RegisterBody(BaseModel):
#     name: str

# # -------------------------
# # Helpers
# # -------------------------
# def current_ts() -> int:
#     return int(time.time())

# def generate_otp() -> str:
#     return f"{random.randint(0, 999999):06d}"

# def create_jwt_for_user(user_id: int, phone: str) -> str:
#     expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     payload = {
#         "sub": str(user_id),
#         "phone": phone,
#         "purpose": "access",
#         "exp": int(expire.timestamp())
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# def create_temp_token_for_phone(phone: str) -> str:
#     """
#     Short-lived token proving the phone was OTP-verified and can be used to register.
#     purpose = otp_register
#     """
#     expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=TEMP_TOKEN_EXPIRE_MINUTES)
#     payload = {
#         "phone": phone,
#         "purpose": "otp_register",
#         "exp": int(expire.timestamp())
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# def decode_jwt(token: str) -> dict:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# # -------------------------
# # Auth endpoints
# # -------------------------
# @app.post("/auth/request-otp")
# def request_otp(body: RequestOTPBody):
#     phone = body.phone.strip()
#     if not phone:
#         raise HTTPException(status_code=400, detail="phone is required")

#     now = current_ts()
#     entry = otp_store.get(phone)
#     if entry and now - entry.get("sent_at", 0) < OTP_RESEND_COOLDOWN_SECONDS:
#         raise HTTPException(status_code=429, detail=f"OTP requested too recently. Wait {OTP_RESEND_COOLDOWN_SECONDS}s.")

#     otp = generate_otp()
#     otp_store[phone] = {
#         "otp": otp,
#         "expires": now + OTP_TTL_SECONDS,
#         "sent_at": now,
#         "attempts": 0
#     }

#     # Simulate SMS for demo — replace with provider API for production
#     print(f"[SIMULATED SMS] OTP for {phone} is {otp} (valid for {OTP_TTL_SECONDS}s)")

#     return {"otp_sent": True, "message": "OTP sent (simulated). In production integrate an SMS provider."}


# @app.post("/auth/verify-otp")
# def verify_otp(body: VerifyOTPBody):
#     phone = body.phone.strip()
#     otp = body.otp.strip()

#     if not phone or not otp:
#         raise HTTPException(status_code=400, detail="phone and otp are required")

#     entry = otp_store.get(phone)
#     now = current_ts()

#     if not entry or entry.get("expires", 0) < now:
#         otp_store.pop(phone, None)
#         raise HTTPException(status_code=400, detail="OTP invalid or expired. Request a new OTP.")

#     if entry.get("otp") != otp:
#         entry["attempts"] = entry.get("attempts", 0) + 1
#         if entry["attempts"] >= OTP_MAX_ATTEMPTS:
#             otp_store.pop(phone, None)
#             raise HTTPException(status_code=400, detail="Too many incorrect attempts. OTP invalidated.")
#         raise HTTPException(status_code=400, detail="OTP does not match.")

#     # OTP is correct. Do NOT auto-create user now.
#     # Check if user exists:
#     cur.execute("SELECT id, phone, name FROM users WHERE phone = ?", (phone,))
#     row = cur.fetchone()

#     # consume OTP (single-use)
#     otp_store.pop(phone, None)

#     if row:
#         # user exists -> issue full access token
#         user = {"id": row[0], "phone": row[1], "name": row[2]}
#         token = create_jwt_for_user(user["id"], phone)
#         return {"user_exists": True, "access_token": token, "token_type": "bearer", "user": user}
#     else:
#         # user does not exist -> issue a short-lived temp token for registration
#         temp_token = create_temp_token_for_phone(phone)
#         return {"user_exists": False, "temp_token": temp_token, "phone": phone, "message": "OTP verified. Register user with /auth/register using this temp_token."}


# @app.post("/auth/register")
# def register_user(body: RegisterBody, authorization: Optional[str] = Header(None)):
#     """
#     Register a new user after OTP verification.
#     The frontend should send the temp_token as Authorization: Bearer <temp_token>
#     """
#     # Get temp token from Authorization header
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Missing Authorization header with temp token")

#     if not authorization.lower().startswith("bearer "):
#         raise HTTPException(status_code=401, detail="Invalid Authorization header format. Use: Bearer <temp_token>")

#     temp_token = authorization.split(" ", 1)[1].strip()
#     payload = decode_jwt(temp_token)

#     # ensure purpose is correct
#     if payload.get("purpose") != "otp_register":
#         raise HTTPException(status_code=401, detail="Invalid token purpose")

#     phone = payload.get("phone")
#     if not phone:
#         raise HTTPException(status_code=400, detail="Temp token missing phone claim")

#     # Safety: check user doesn't already exist (race)
#     cur.execute("SELECT id FROM users WHERE phone = ?", (phone,))
#     if cur.fetchone():
#         raise HTTPException(status_code=400, detail="User already exists")

#     # create user
#     created_at = datetime.datetime.utcnow().isoformat()
#     cur.execute("INSERT INTO users (phone, name, created_at) VALUES (?, ?, ?)", (phone, body.name, created_at))
#     conn.commit()
#     user_id = cur.lastrowid
#     user = {"id": user_id, "phone": phone, "name": body.name}

#     # issue full access token
#     access_token = create_jwt_for_user(user_id, phone)
#     return {"access_token": access_token, "token_type": "bearer", "user": user}

# # -------------------------
# # Dev helper endpoints
# # -------------------------
# @app.get("/auth/debug-otp")
# def debug_otp(phone: str = Query(...)):
#     if not DEV_MODE:
#         raise HTTPException(status_code=404, detail="Not found")
#     entry = otp_store.get(phone)
#     if not entry:
#         raise HTTPException(status_code=404, detail="No OTP for this phone")
#     return {"phone": phone, "otp": entry["otp"], "expires_at": entry["expires"], "sent_at": entry["sent_at"]}

# @app.get("/debug/users")
# def debug_users():
#     if not DEV_MODE:
#         raise HTTPException(status_code=404, detail="Not found")
#     cur.execute("SELECT id, phone, name, created_at FROM users ORDER BY id ASC")
#     rows = cur.fetchall()
#     users = [{"id": r[0], "phone": r[1], "name": r[2], "created_at": r[3]} for r in rows]
#     return {"count": len(users), "users": users}

# main.py
import os
import time
import random
import sqlite3
import datetime
from typing import Optional, List
from decimal import Decimal, ROUND_HALF_UP, getcontext

from fastapi import FastAPI, HTTPException, Query, Header
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

# set Decimal precision for money math
getcontext().prec = 28

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
# TEMP token lifetime (minutes)
TEMP_TOKEN_EXPIRE_MINUTES = int(os.getenv("TEMP_TOKEN_EXPIRE_MINUTES", "1000"))

# -------------------------
# DB init (SQLite demo)
# -------------------------
if not os.path.exists(DB_PATH):
    open(DB_PATH, "a").close()

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

# Create schema: users + offers + loans + installments + repayments
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lender_id INTEGER NOT NULL,
  amount_available NUMERIC(12,2) NOT NULL,
  currency TEXT DEFAULT 'INR',
  annual_interest_rate REAL NOT NULL,
  duration_months INTEGER NOT NULL,
  installments_count INTEGER NOT NULL,
  periodicity TEXT DEFAULT 'MONTHLY',
  min_borrow_amount NUMERIC(12,2),
  max_borrow_amount NUMERIC(12,2),
  installment_amount NUMERIC(12,2),
  status TEXT DEFAULT 'active',
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  offer_id INTEGER,
  lender_id INTEGER NOT NULL,
  borrower_id INTEGER NOT NULL,
  principal NUMERIC(12,2) NOT NULL,
  currency TEXT DEFAULT 'INR',
  annual_interest_rate REAL NOT NULL,
  duration_months INTEGER NOT NULL,
  installments_count INTEGER NOT NULL,
  installment_amount NUMERIC(12,2) NOT NULL,
  start_date DATE,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS installments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  loan_id INTEGER NOT NULL,
  installment_no INTEGER NOT NULL,
  due_date DATE NOT NULL,
  expected_amount NUMERIC(12,2) NOT NULL,
  paid_amount NUMERIC(12,2) DEFAULT 0,
  paid_at TIMESTAMP,
  status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS repayments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  loan_id INTEGER NOT NULL,
  payer_id INTEGER NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  note TEXT
);
""")
conn.commit()

# -------------------------
# OTP store (in-memory demo)
# -------------------------
otp_store = {}  # phone -> {otp, expires, sent_at, attempts}

app = FastAPI(title="SmartSettle - OTP + Offers (Lending Packages)")

# -------------------------
# CORS setup
# -------------------------
cors_env = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [o.strip() for o in cors_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class CreateOfferBody(BaseModel):
    amount_available: Decimal
    annual_interest_rate: float
    duration_months: int
    installments_count: int
    periodicity: Optional[str] = "MONTHLY"
    min_borrow_amount: Optional[Decimal] = None
    max_borrow_amount: Optional[Decimal] = None
    description: Optional[str] = None

class FundOfferBody(BaseModel):
    amount_requested: Decimal
    start_date: Optional[str] = None  # YYYY-MM-DD

# -------------------------
# Helpers: time, otp, jwt
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

def require_access_user(authorization: Optional[str]) -> dict:
    """
    Validate Authorization: Bearer <access_token> and return user dict {id, phone, name}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_jwt(token)
    if payload.get("purpose") != "access":
        raise HTTPException(status_code=401, detail="Token is not an access token")
    user_id = int(payload.get("sub"))
    cur.execute("SELECT id, phone, name FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return {"id": row[0], "phone": row[1], "name": row[2]}

# -------------------------
# Money helpers (Decimal)
# -------------------------
def quant_dec(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def add_months_to_date(d: datetime.date, months: int) -> datetime.date:
    # naive add months preserving end-of-month behavior
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31,
                      29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                      31,30,31,30,31,31,30,31,30,31][month-1])
    return datetime.date(year, month, day)

def compute_emi_schedule(principal: Decimal, annual_rate_percent: float, installments: int, start_date: Optional[str] = None):
    """
    Returns dict with emi, total_paid, total_interest, schedule list.
    schedule items contain installment_no, due_date (ISO), emi, interest, principal_component, outstanding_after
    """
    P = Decimal(principal)
    r = Decimal(annual_rate_percent) / Decimal(100) / Decimal(12)  # monthly rate
    n = int(installments)
    if r == 0:
        emi = (P / n)
    else:
        one_plus_r_n = (Decimal(1) + r) ** n
        emi = (P * r * one_plus_r_n / (one_plus_r_n - Decimal(1)))
    emi = quant_dec(emi)

    outstanding = P
    schedule = []
    total_paid = Decimal(0)
    total_interest = Decimal(0)

    sd = datetime.date.fromisoformat(start_date) if start_date else datetime.date.today()

    for i in range(1, n+1):
        interest = quant_dec((outstanding * r))
        principal_comp = quant_dec(emi - interest)
        # handle last payment rounding: pay remaining outstanding as principal component
        if i == n:
            principal_comp = quant_dec(outstanding)
            emi = quant_dec(principal_comp + interest)
        outstanding = quant_dec(outstanding - principal_comp)
        due_date = add_months_to_date(sd, i-1)
        schedule.append({
            "installment_no": i,
            "due_date": due_date.isoformat(),
            "emi": float(emi),
            "interest": float(interest),
            "principal_component": float(principal_comp),
            "outstanding_after": float(outstanding)
        })
        total_paid += emi
        total_interest += interest

    return {
        "principal": float(P),
        "annual_rate_percent": float(annual_rate_percent),
        "installments": n,
        "emi": float(emi),
        "total_paid": float(quant_dec(total_paid)),
        "total_interest": float(quant_dec(total_interest)),
        "schedule": schedule
    }

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
        # keep same status code, but include ok:false in response body
        raise HTTPException(status_code=400, detail={"ok": False, "error": "phone and otp are required"})

    entry = otp_store.get(phone)
    now = current_ts()

    if not entry or entry.get("expires", 0) < now:
        otp_store.pop(phone, None)
        raise HTTPException(status_code=400, detail={"ok": False, "error": "OTP invalid or expired. Request a new OTP."})

    if entry.get("otp") != otp:
        entry["attempts"] = entry.get("attempts", 0) + 1
        if entry["attempts"] >= OTP_MAX_ATTEMPTS:
            otp_store.pop(phone, None)
            raise HTTPException(status_code=400, detail={"ok": False, "error": "Too many incorrect attempts. OTP invalidated."})
        raise HTTPException(status_code=400, detail={"ok": False, "error": "OTP does not match."})

    # OTP is correct. Do NOT auto-create user now.
    cur.execute("SELECT id, phone, name FROM users WHERE phone = ?", (phone,))
    row = cur.fetchone()

    # consume OTP (single-use)
    otp_store.pop(phone, None)

    if row:
        # user exists -> issue full access token
        user = {"id": row[0], "phone": row[1], "name": row[2]}
        token = create_jwt_for_user(user["id"], phone)
        return {"ok": True, "user_exists": True, "access_token": token, "token_type": "bearer", "user": user}
    else:
        # user does not exist -> issue a short-lived temp token for registration
        temp_token = create_temp_token_for_phone(phone)
        return {"ok": True, "user_exists": False, "temp_token": temp_token, "phone": phone, "message": "OTP verified. Register user with /auth/register using this temp_token."}


@app.post("/auth/register")
def register_user(body: RegisterBody, authorization: Optional[str] = Header(None)):
    """
    Register a new user after OTP verification.
    The frontend should send the temp_token as Authorization: Bearer <temp_token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header with temp token")

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format. Use: Bearer <temp_token>")

    temp_token = authorization.split(" ", 1)[1].strip()
    payload = decode_jwt(temp_token)

    if payload.get("purpose") != "otp_register":
        raise HTTPException(status_code=401, detail="Invalid token purpose")

    phone = payload.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Temp token missing phone claim")

    # Safety: check user doesn't already exist (race)
    cur.execute("SELECT id FROM users WHERE phone = ?", (phone,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    created_at = datetime.datetime.utcnow().isoformat()
    cur.execute("INSERT INTO users (phone, name, created_at) VALUES (?, ?, ?)", (phone, body.name, created_at))
    conn.commit()
    user_id = cur.lastrowid
    user = {"id": user_id, "phone": phone, "name": body.name}

    access_token = create_jwt_for_user(user_id, phone)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

# -------------------------
# Offers endpoints
# -------------------------
@app.post("/offers")
def create_offer(body: CreateOfferBody, authorization: Optional[str] = Header(None)):
    """
    Create a lending offer (lender posts a package). Requires access token.
    """
    user = require_access_user(authorization)
    # Basic validation
    if body.amount_available <= 0:
        raise HTTPException(status_code=400, detail="amount_available must be > 0")
    if not (0 <= body.annual_interest_rate <= 100):
        raise HTTPException(status_code=400, detail="annual_interest_rate must be between 0 and 100")
    if body.duration_months <= 0 or body.installments_count <= 0:
        raise HTTPException(status_code=400, detail="duration_months and installments_count must be > 0")
    if body.min_borrow_amount and body.min_borrow_amount > body.amount_available:
        raise HTTPException(status_code=400, detail="min_borrow_amount cannot exceed amount_available")
    if body.max_borrow_amount and body.max_borrow_amount > body.amount_available:
        # allow max equal to available; not more than available
        pass

    # compute suggested installment (EMI) for whole amount_available (informational)
    emi_info = compute_emi_schedule(Decimal(body.amount_available), float(body.annual_interest_rate), body.installments_count)
    installment_amount = Decimal(str(emi_info["emi"]))

    cur.execute("""
        INSERT INTO offers (lender_id, amount_available, currency, annual_interest_rate, duration_months, installments_count,
                            periodicity, min_borrow_amount, max_borrow_amount, installment_amount, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user["id"],
        float(body.amount_available),
        "INR",
        float(body.annual_interest_rate),
        body.duration_months,
        body.installments_count,
        body.periodicity,
        float(body.min_borrow_amount) if body.min_borrow_amount is not None else None,
        float(body.max_borrow_amount) if body.max_borrow_amount is not None else None,
        float(quant_dec(installment_amount)),
        body.description
    ))
    conn.commit()
    offer_id = cur.lastrowid
    return {
        "offer_id": offer_id,
        "lender_id": user["id"],
        "amount_available": float(body.amount_available),
        "installment_amount": float(quant_dec(installment_amount)),
        "status": "active",
        "created_at": datetime.datetime.utcnow().isoformat()
    }

@app.get("/offers")
def list_offers(limit: int = 10, offset: int = 0, sort: str = "created_desc"):
    """
    Public marketplace listing.
    sort: created_desc | rate_asc | rate_desc
    """
    order_sql = "o.created_at DESC"
    if sort == "rate_asc":
        order_sql = "o.annual_interest_rate ASC"
    elif sort == "rate_desc":
        order_sql = "o.annual_interest_rate DESC"

    sql = f"""
    SELECT o.id, o.lender_id, u.name, o.amount_available, o.annual_interest_rate,
           o.duration_months, o.installment_amount, o.periodicity, o.description, o.created_at
    FROM offers o
    JOIN users u ON u.id = o.lender_id
    WHERE o.status = 'active'
    ORDER BY {order_sql}
    LIMIT ? OFFSET ?
    """
    cur.execute(sql, (limit, offset))
    rows = cur.fetchall()
    offers = []
    for r in rows:
        offers.append({
            "offer_id": r[0],
            "lender": {"id": r[1], "name": r[2]},
            "amount_available": float(r[3]),
            "annual_interest_rate": float(r[4]),
            "duration_months": r[5],
            "installment_amount": float(r[6]) if r[6] is not None else None,
            "periodicity": r[7],
            "description": r[8],
            "created_at": r[9]
        })
    return {"offers": offers, "next_offset": offset + len(offers)}

@app.get("/offers/latest")
def latest_offers(limit: int = 10):
    return list_offers(limit=limit, offset=0, sort="created_desc")

@app.get("/offers/{offer_id}")
def get_offer(offer_id: int):
    cur.execute("""
    SELECT o.id, o.lender_id, u.name, o.amount_available, o.annual_interest_rate,
           o.duration_months, o.installment_amount, o.periodicity, o.min_borrow_amount, o.max_borrow_amount,
           o.description, o.created_at
    FROM offers o
    JOIN users u ON u.id = o.lender_id
    WHERE o.id = ?
    """, (offer_id,))
    r = cur.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Offer not found")
    return {
        "offer_id": r[0],
        "lender": {"id": r[1], "name": r[2]},
        "amount_available": float(r[3]),
        "annual_interest_rate": float(r[4]),
        "duration_months": r[5],
        "installment_amount": float(r[6]) if r[6] is not None else None,
        "periodicity": r[7],
        "min_borrow_amount": float(r[8]) if r[8] is not None else None,
        "max_borrow_amount": float(r[9]) if r[9] is not None else None,
        "description": r[10],
        "created_at": r[11]
    }

@app.post("/offers/{offer_id}/fund")
def fund_offer(offer_id: int, body: FundOfferBody, authorization: Optional[str] = Header(None)):
    """
    Borrower accepts (funds) part or whole of an offer.
    This operation is transactional.
    """
    borrower = require_access_user(authorization)

    # Validate requested amount
    amount_req = Decimal(body.amount_requested)
    if amount_req <= 0:
        raise HTTPException(status_code=400, detail="amount_requested must be > 0")

    # Optional start_date parse
    if body.start_date:
        try:
            start_date = datetime.date.fromisoformat(body.start_date)
        except Exception:
            raise HTTPException(status_code=400, detail="start_date must be YYYY-MM-DD")
    else:
        start_date = datetime.date.today()

    try:
        conn.execute("BEGIN IMMEDIATE")  # lock DB for this transaction (SQLite)
        # fetch current offer
        cur.execute("SELECT id, lender_id, amount_available, annual_interest_rate, duration_months, installments_count, min_borrow_amount, max_borrow_amount FROM offers WHERE id = ? AND status = 'active'", (offer_id,))
        row = cur.fetchone()
        if not row:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=404, detail="Offer not found or not active")
        _, lender_id, amount_available, annual_rate, duration_months, installments_count, min_b, max_b = row
        amount_available = Decimal(str(amount_available))
        if lender_id == borrower["id"]:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail="Cannot borrow from your own offer")
        # check min/max rules
        if min_b is not None and amount_req < Decimal(str(min_b)):
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail=f"amount_requested smaller than minimum allowed ({min_b})")
        if max_b is not None and amount_req > Decimal(str(max_b)):
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=400, detail=f"amount_requested larger than maximum allowed ({max_b})")
        if amount_req > amount_available:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=409, detail="Not enough amount available in this offer")

        # deduct from offer
        new_available = quant_dec(amount_available - amount_req)
        cur.execute("UPDATE offers SET amount_available = ? WHERE id = ?", (float(new_available), offer_id))

        # create loan
        emi_info = compute_emi_schedule(amount_req, float(annual_rate), int(installments_count), start_date.isoformat())
        installment_amount = Decimal(str(emi_info["emi"]))
        cur.execute("""
            INSERT INTO loans (offer_id, lender_id, borrower_id, principal, annual_interest_rate, duration_months,
                                installments_count, installment_amount, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            offer_id,
            lender_id,
            borrower["id"],
            float(amount_req),
            float(annual_rate),
            duration_months,
            installments_count,
            float(quant_dec(installment_amount)),
            start_date.isoformat()
        ))
        loan_id = cur.lastrowid

        # create installments rows
        for item in emi_info["schedule"]:
            cur.execute("""
                INSERT INTO installments (loan_id, installment_no, due_date, expected_amount)
                VALUES (?, ?, ?, ?)
            """, (loan_id, item["installment_no"], item["due_date"], float(quant_dec(Decimal(str(item["emi"]))))))
        conn.commit()

        return {
            "loan_id": loan_id,
            "offer_id": offer_id,
            "principal": float(amount_req),
            "installment_amount": float(quant_dec(installment_amount)),
            "installments_count": installments_count,
            "start_date": start_date.isoformat(),
            "status": "active"
        }
    except HTTPException:
        # re-raise
        raise
    except Exception as e:
        conn.execute("ROLLBACK")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

# -------------------------
# Simple loan / repayment endpoints (read + repay)
# -------------------------
@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    cur.execute("SELECT id, offer_id, lender_id, borrower_id, principal, annual_interest_rate, installments_count, installment_amount, start_date, status FROM loans WHERE id = ?", (loan_id,))
    r = cur.fetchone()
    if not r:
        raise HTTPException(status_code=404, detail="Loan not found")
    loan = {
        "loan_id": r[0],
        "offer_id": r[1],
        "lender_id": r[2],
        "borrower_id": r[3],
        "principal": float(r[4]),
        "annual_interest_rate": float(r[5]),
        "installments_count": r[6],
        "installment_amount": float(r[7]),
        "start_date": r[8],
        "status": r[9]
    }
    # attach installments
    cur.execute("SELECT installment_no, due_date, expected_amount, paid_amount, paid_at, status FROM installments WHERE loan_id = ? ORDER BY installment_no", (loan_id,))
    rows = cur.fetchall()
    inst = []
    for x in rows:
        inst.append({
            "installment_no": x[0],
            "due_date": x[1],
            "expected_amount": float(x[2]),
            "paid_amount": float(x[3]),
            "paid_at": x[4],
            "status": x[5]
        })
    loan["installments"] = inst
    return loan

@app.post("/loans/{loan_id}/repay")
def repay_loan(loan_id: int, body: dict, authorization: Optional[str] = Header(None)):
    """
    Body: { "amount": 1500.00, "note": "partial" }
    Applies amount to oldest pending installment(s) using integer paise arithmetic to avoid rounding drift.
    """
    payer = require_access_user(authorization)
    raw_amount = body.get("amount", None)
    if raw_amount is None:
        raise HTTPException(status_code=400, detail="amount is required in body")
    try:
        amount = Decimal(str(raw_amount))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid amount")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    # Confirm loan exists and get borrower
    cur.execute("SELECT borrower_id FROM loans WHERE id = ?", (loan_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Loan not found")
    borrower_id = row[0]

    # Optionally restrict who can record repayment (demo currently permissive).
    # For now allow borrower or any authenticated (keep existing behavior). In production tighten this.
    # if payer["id"] != borrower_id:
    #     raise HTTPException(status_code=403, detail="Only borrower may make repayments")

    created_at = datetime.datetime.utcnow().isoformat()

    # Record repayment (audit)
    cur.execute(
        "INSERT INTO repayments (loan_id, payer_id, amount, created_at, note) VALUES (?, ?, ?, ?, ?)",
        (loan_id, payer["id"], float(amount), created_at, body.get("note"))
    )

    # Convert to paise (integer) to avoid fractional rounding drift
    remaining_paise = int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    # Fetch pending installments in order
    cur.execute("SELECT id, expected_amount, paid_amount FROM installments WHERE loan_id = ? AND status IN ('pending','partial') ORDER BY installment_no", (loan_id,))
    rows = cur.fetchall()

    applied_paise = 0
    last_updated_installment_id = None

    for ins in rows:
        ins_id, expected_amt, paid_amt = ins
        expected_paise = int((Decimal(str(expected_amt)) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        paid_paise = int((Decimal(str(paid_amt or 0)) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

        need = expected_paise - paid_paise
        if need <= 0:
            continue

        apply = min(need, remaining_paise)
        if apply <= 0:
            break

        new_paid_paise = paid_paise + apply
        new_paid_decimal = Decimal(new_paid_paise) / Decimal(100)
        status = "paid" if new_paid_paise >= expected_paise else "partial"

        # Update installment with new paid amount and status; set paid_at to this repayment time
        cur.execute("UPDATE installments SET paid_amount = ?, paid_at = ?, status = ? WHERE id = ?",
                    (float(new_paid_decimal), created_at if apply > 0 else None, status, ins_id))

        applied_paise += apply
        remaining_paise -= apply
        last_updated_installment_id = ins_id

        if remaining_paise <= 0:
            break

    conn.commit()

    applied = float(Decimal(applied_paise) / Decimal(100))
    remaining_unapplied = float(Decimal(remaining_paise) / Decimal(100))

    return {"status": "ok", "applied": applied, "remaining_unapplied": remaining_unapplied}

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

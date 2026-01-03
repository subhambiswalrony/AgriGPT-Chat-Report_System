import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# Email Configuration
EMAIL_ID = os.getenv("EMAIL_ID")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI missing")

if not MONGO_DB:
    raise ValueError("❌ MONGO_DB missing")

if not EMAIL_ID:
    raise ValueError("❌ EMAIL_ID missing")

if not EMAIL_APP_PASSWORD:
    raise ValueError("❌ EMAIL_APP_PASSWORD missing")

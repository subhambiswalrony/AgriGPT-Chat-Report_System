import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from utils.config import EMAIL_ID, EMAIL_APP_PASSWORD, OTP_EXPIRY_MINUTES
from services.db_service import db
from pymongo import ASCENDING

# Initialize TTL index for automatic deletion after 24 hours
def setup_otp_collection():
    """Setup TTL index to auto-delete OTP documents after 24 hours"""
    try:
        # First, try to drop any existing conflicting index
        try:
            existing_indexes = list(db.otp_verifications.list_indexes())
            for idx in existing_indexes:
                # Drop any TTL index that isn't the correct one
                if 'expireAfterSeconds' in idx and idx['name'] != 'otp_ttl_index':
                    db.otp_verifications.drop_index(idx['name'])
                    print(f"⚠ Dropped conflicting index: {idx['name']}")
        except:
            pass  # Ignore errors when dropping indexes
        
        # Create TTL index on expires_at field - documents will be deleted after they expire
        db.otp_verifications.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=86400,  # 24 hours in seconds
            name="otp_ttl_index"
        )
        print("✓ OTP TTL index created/verified (24 hours)")
    except Exception as e:
        # Check if it's just a "index already exists" error
        if "already exists" in str(e).lower():
            print("✓ OTP TTL index already exists")
        else:
            print(f"⚠ TTL index setup error: {str(e)}")

# Setup collection on import
setup_otp_collection()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email_otp(email, otp):
    try:
        body = f"""
🌾 AgriGPT Verification Code 🌾

Your OTP is: {otp}
Valid for {OTP_EXPIRY_MINUTES} minutes.

Do not share this code with anyone.
"""
        msg = MIMEText(body)
        msg["Subject"] = "AgriGPT OTP Verification"
        msg["From"] = EMAIL_ID
        msg["To"] = email

        print(f"📧 Attempting to send email to {email}")
        print(f"📧 Using email: {EMAIL_ID}")
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ID, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {email}")
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        raise

def create_and_send_otp(email, purpose):
    """Generate OTP, save to database, and send via email"""
    try:
        otp = generate_otp()
        expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Prepare OTP document
        otp_document = {
            "email": email,
            "otp": otp,
            "purpose": purpose,
            "expires_at": expiry,
            "verified": False,
            "created_at": datetime.utcnow()
        }
        
        # Insert OTP into database
        result = db.otp_verifications.insert_one(otp_document)
        
        if result.inserted_id:
            print(f"✅ OTP saved to database with ID: {result.inserted_id}")
            print(f"✓ OTP generated for {email}: {otp} (expires at {expiry})")
            print(f"📋 Purpose: {purpose}")
            
            # Verify the document was actually saved
            saved_doc = db.otp_verifications.find_one({"_id": result.inserted_id})
            if saved_doc:
                print(f"✅ Verified: OTP document exists in database")
            else:
                print(f"⚠️ Warning: OTP was inserted but cannot be retrieved")
        else:
            print(f"❌ Failed to insert OTP into database")
            raise Exception("Failed to save OTP to database")
        
        # Send email after successful database save
        send_email_otp(email, otp)
        
        return {
            "success": True,
            "otp_id": str(result.inserted_id),
            "expires_at": expiry
        }
        
    except Exception as e:
        print(f"❌ Error in create_and_send_otp: {str(e)}")
        raise Exception(f"Failed to create OTP: {str(e)}")

import jwt, bcrypt
import random
from datetime import datetime, timedelta, timezone
from utils.config import JWT_SECRET_KEY, JWT_EXPIRY_HOURS
from services.db_service import user_collection, chat_collection, report_collection, db
from bson import ObjectId

# Import the proper OTP service functions
from services.otp_service import create_and_send_otp as otp_create_and_send


def signup_user(email, password, name):
    if user_collection.find_one({"email": email}):
        raise Exception("User already exists")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "email": email,
        "password": hashed,
        "name": name,
        "profilePicture": "",
        "created_at": datetime.utcnow(),
        "last_login": None
    }

    result = user_collection.insert_one(user)
    token = generate_token(str(result.inserted_id))

    return {
        "user_id": str(result.inserted_id),
        "email": email,
        "name": name,
        "profilePicture": "",
        "token": token
    }


def login_user(email, password):
    user = user_collection.find_one({"email": email})
    if not user:
        raise Exception("User not registered")
    if not bcrypt.checkpw(password.encode(), user["password"]):
        raise Exception("Invalid credentials")

    # Update last login timestamp
    user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    token = generate_token(str(user["_id"]))
    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name"),
        "profilePicture": user.get("profilePicture", ""),
        "token": token
    }


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def update_user_profile(user_id, name, email, profile_picture=None):
    """Update user's name, email, and profile picture"""
    try:
        # Check if email is already taken by another user
        existing_user = user_collection.find_one({"email": email, "_id": {"$ne": ObjectId(user_id)}})
        if existing_user:
            raise Exception("Email already in use by another account")

        # Prepare update data
        update_data = {
            "name": name,
            "email": email
        }
        
        # Add profile picture if provided
        if profile_picture is not None:
            update_data["profilePicture"] = profile_picture

        # Update user profile
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count == 0 and result.matched_count == 0:
            raise Exception("User not found")

        return {
            "success": True,
            "message": "Profile updated successfully",
            "name": name,
            "email": email,
            "profilePicture": profile_picture if profile_picture is not None else ""
        }
    except Exception as e:
        raise Exception(str(e))


def change_user_password(user_id, current_password, new_password):
    """Change user's password"""
    try:
        # Get user from database
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise Exception("User not found")

        # Verify current password
        if not bcrypt.checkpw(current_password.encode(), user["password"]):
            raise Exception("Current password is incorrect")

        # Hash new password
        hashed_new_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

        # Update password in database
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_new_password}}
        )

        if result.modified_count == 0:
            raise Exception("Failed to update password")

        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except Exception as e:
        raise Exception(str(e))


def delete_user_account(user_id):
    """Delete user account and all associated data (chat history and reports)"""
    try:
        # Verify user exists
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise Exception("User not found")

        # Delete all chat history for this user
        chat_delete_result = chat_collection.delete_many({"user_id": user_id})
        print(f"✓ Deleted {chat_delete_result.deleted_count} chat records for user: {user_id}")

        # Delete all farming reports for this user
        report_delete_result = report_collection.delete_many({"user_id": user_id})
        print(f"✓ Deleted {report_delete_result.deleted_count} report records for user: {user_id}")

        # Delete the user account
        user_delete_result = user_collection.delete_one({"_id": ObjectId(user_id)})
        if user_delete_result.deleted_count == 0:
            raise Exception("Failed to delete user account")

        print(f"✓ User account deleted successfully: {user_id}")

        return {
            "success": True,
            "message": "Account and all associated data deleted successfully",
            "deleted": {
                "chats": chat_delete_result.deleted_count,
                "reports": report_delete_result.deleted_count
            }
        }
    except Exception as e:
        raise Exception(str(e))


def send_otp_email(email):
    """Generate and send OTP to user's email"""
    try:
        # Check if user exists
        user = user_collection.find_one({"email": email})
        if not user:
            raise Exception("No account found with this email")
        
        # Use the proper database-backed OTP service
        result = otp_create_and_send(email, "password_reset")
        
        return {
            "success": True,
            "message": "OTP sent successfully to your email",
            "email": email,
            "otp_id": result["otp_id"],
            "expires_at": result["expires_at"].isoformat()
        }
    except Exception as e:
        raise Exception(str(e))


def verify_otp_code(email, otp):
    """Verify OTP code"""
    try:
        print(f"🔍 Verifying OTP for email: {email}")
        
        # Find OTP in database
        record = db.otp_verifications.find_one({
            "email": email,
            "otp": otp,
            "verified": False
        })

        if not record:
            print(f"❌ No matching OTP found for {email}")
            raise Exception("Invalid OTP. Please try again.")

        # Check if OTP has expired
        if record["expires_at"] < datetime.utcnow():
            print(f"⏰ OTP expired for {email}")
            raise Exception("OTP has expired. Please request a new one.")

        # Mark OTP as verified
        db.otp_verifications.update_one(
            {"_id": record["_id"]},
            {"$set": {"verified": True}}
        )
        
        print(f"✅ OTP verified successfully for {email}")
        
        return {
            "success": True,
            "message": "OTP verified successfully",
            "email": email
        }
    except Exception as e:
        raise Exception(str(e))

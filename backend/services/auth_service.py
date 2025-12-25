import jwt, bcrypt
from datetime import datetime, timedelta
from utils.config import JWT_SECRET_KEY, JWT_EXPIRY_HOURS
from services.db_service import user_collection
from bson import ObjectId


def signup_user(email, password, name):
    if user_collection.find_one({"email": email}):
        raise Exception("User already exists")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "email": email,
        "password": hashed,
        "name": name,
        "created_at": datetime.utcnow(),
        "last_login": None
    }

    result = user_collection.insert_one(user)
    token = generate_token(str(result.inserted_id))

    return {
        "user_id": str(result.inserted_id),
        "email": email,
        "name": name,
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
        "token": token
    }


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def update_user_profile(user_id, name, email):
    """Update user's name and email"""
    try:
        # Check if email is already taken by another user
        existing_user = user_collection.find_one({"email": email, "_id": {"$ne": ObjectId(user_id)}})
        if existing_user:
            raise Exception("Email already in use by another account")

        # Update user profile
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "name": name,
                "email": email
            }}
        )

        if result.modified_count == 0:
            raise Exception("No changes made")

        return {
            "success": True,
            "message": "Profile updated successfully",
            "name": name,
            "email": email
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

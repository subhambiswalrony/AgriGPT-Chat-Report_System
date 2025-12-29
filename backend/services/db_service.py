from pymongo import MongoClient
from datetime import datetime, timezone
from utils.config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

chat_collection = db.chat_history
user_collection = db.users
report_collection = db.farming_reports


def save_chat(user_id, question, answer, response_type, language, input_type="text"):
    try:
        result = chat_collection.insert_one({
            "user_id": user_id,
            "input_type": input_type,
            "question": question,
            "answer": answer,
            "response_type": response_type,
            "language": language,
            "timestamp": datetime.now(timezone.utc)
        })
        print(f"✓ Chat saved for user: {user_id}, ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"✗ Error saving chat: {str(e)}")
        raise


def get_chat_history(user_id):
    return list(
        chat_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1)
    )


def save_report(user_id, crop_name, region, report_data, language):
    """Save farming report to database"""
    try:
        result = report_collection.insert_one({
            "user_id": user_id,
            "crop_name": crop_name,
            "region": region,
            "report_data": report_data,
            "language": language,
            "timestamp": datetime.now(timezone.utc)
        })
        print(f"✓ Report saved for user: {user_id}, Crop: {crop_name}, Region: {region}, ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"✗ Error saving report: {str(e)}")
        raise


def get_user_reports(user_id):
    """Get all reports for a user"""
    return list(
        report_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1)
    )

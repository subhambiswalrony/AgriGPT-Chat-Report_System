from flask import Blueprint, request, jsonify
from services.otp_service import create_and_send_otp
from services.db_service import db
from datetime import datetime

otp_bp = Blueprint("otp", __name__)

@otp_bp.route("/api/send-otp", methods=["POST"])
def send_otp():
    try:
        data = request.json
        
        if not data or "email" not in data or "purpose" not in data:
            return jsonify({"error": "Email and purpose are required"}), 400
        
        result = create_and_send_otp(data["email"], data["purpose"])
        
        return jsonify({
            "message": "OTP sent successfully",
            "otp_id": result["otp_id"],
            "expires_at": result["expires_at"].isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in send_otp endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@otp_bp.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    try:
        data = request.json
        
        if not data or "email" not in data or "otp" not in data:
            return jsonify({"error": "Email and OTP are required"}), 400

        print(f"🔍 Verifying OTP for email: {data['email']}")
        
        # Check total OTP records for debugging
        total_otps = db.otp_verifications.count_documents({"email": data["email"]})
        print(f"📊 Total OTP records for {data['email']}: {total_otps}")
        
        record = db.otp_verifications.find_one({
            "email": data["email"],
            "otp": data["otp"],
            "verified": False
        })

        if not record:
            print(f"❌ No matching OTP found for {data['email']}")
            return jsonify({"error": "Invalid OTP"}), 400

        if record["expires_at"] < datetime.utcnow():
            print(f"⏰ OTP expired for {data['email']}")
            return jsonify({"error": "OTP expired"}), 400

        db.otp_verifications.update_one(
            {"_id": record["_id"]},
            {"$set": {"verified": True}}
        )
        
        print(f"✅ OTP verified successfully for {data['email']}")
        return jsonify({"message": "OTP verified successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error in verify_otp endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Utility routes for debugging and maintenance

@otp_bp.route("/api/otp/status", methods=["GET"])
def otp_status():
    """Get OTP collection status (for debugging)"""
    try:
        total_otps = db.otp_verifications.count_documents({})
        verified_otps = db.otp_verifications.count_documents({"verified": True})
        unverified_otps = db.otp_verifications.count_documents({"verified": False})
        expired_otps = db.otp_verifications.count_documents({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        # Check if TTL index exists
        indexes = list(db.otp_verifications.list_indexes())
        ttl_index_exists = any(idx.get("expireAfterSeconds") is not None for idx in indexes)
        
        return jsonify({
            "collection": "otp_verifications",
            "total_documents": total_otps,
            "verified": verified_otps,
            "unverified": unverified_otps,
            "expired": expired_otps,
            "ttl_index_enabled": ttl_index_exists,
            "indexes": [{"name": idx["name"], "key": idx["key"]} for idx in indexes]
        }), 200
        
    except Exception as e:
        print(f"❌ Error in otp_status endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@otp_bp.route("/api/otp/cleanup", methods=["POST"])
def cleanup_expired_otps():
    """Manually cleanup expired OTPs (TTL index should handle this automatically)"""
    try:
        result = db.otp_verifications.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        print(f"🧹 Cleaned up {result.deleted_count} expired OTP records")
        
        return jsonify({
            "message": "Cleanup completed",
            "deleted_count": result.deleted_count
        }), 200
        
    except Exception as e:
        print(f"❌ Error in cleanup_expired_otps endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

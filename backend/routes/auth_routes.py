from flask import Blueprint, request, jsonify
from services.auth_service import signup_user, login_user, update_user_profile, change_user_password
import jwt
from functools import wraps
from utils.config import JWT_SECRET_KEY

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            request.current_user = payload
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        return jsonify(signup_user(data["email"], data["password"], data.get("name")))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        return jsonify(login_user(data["email"], data["password"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/update-profile", methods=["PUT"])
@token_required
def update_profile():
    try:
        data = request.get_json()
        user_id = request.current_user["user_id"]
        result = update_user_profile(user_id, data.get("name"), data.get("email"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/change-password", methods=["PUT"])
@token_required
def change_password():
    try:
        data = request.get_json()
        user_id = request.current_user["user_id"]
        result = change_user_password(user_id, data.get("currentPassword"), data.get("newPassword"))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

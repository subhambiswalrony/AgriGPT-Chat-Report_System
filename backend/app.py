from flask import Flask, request, jsonify
from flask_cors import CORS

# Core feature handlers
from chat import handle_chat
from voice import handle_voice
from report import generate_farming_report

# Services
from services.db_service import (
    get_chat_history, 
    get_chat_sessions, 
    get_chat_by_id,
    delete_chat_session
)

# Auth
from routes.auth_routes import auth_bp, token_required, verify_token

app = Flask(__name__)
CORS(app)

# Register authentication blueprint
app.register_blueprint(auth_bp)

# -------------------- HEALTH CHECK --------------------
@app.route("/")
def health():
    return {"status": "AgriGPT Backend Running 🌾"}

# -------------------- CHAT API --------------------
@app.route("/api/chat", methods=["POST"])
def chat_api():
    try:
        token = request.headers.get("Authorization")
        user_id = "trial_user"  # default for unauthenticated users

        if token and token.startswith("Bearer "):
            token_str = token.split(" ")[1]
            user_data = verify_token(token_str)
            if user_data:
                user_id = user_data["user_id"]

        data = request.json
        message = data.get("message")
        chat_id = data.get("chat_id")  # Optional: for continuing existing chat

        if not message:
            return jsonify({"error": "Message is required"}), 400

        result = handle_chat(user_id, message, chat_id)
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error in chat_api: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -------------------- CHAT SESSIONS API --------------------
@app.route("/api/chats", methods=["GET"])
@token_required
def get_chats():
    """Get all chat sessions for authenticated user"""
    try:
        user_id = request.current_user["user_id"]
        sessions = get_chat_sessions(user_id)
        return jsonify(sessions)

    except Exception as e:
        print(f"❌ Error in get_chats: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/chats/<chat_id>", methods=["GET"])
@token_required
def get_chat(chat_id):
    """Get full chat history for a specific chat session"""
    try:
        user_id = request.current_user["user_id"]
        chat_data = get_chat_by_id(chat_id)
        
        if not chat_data:
            return jsonify({"error": "Chat not found"}), 404
        
        # Verify user owns this chat
        if chat_data["session"]["user_id"] != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        return jsonify(chat_data)

    except Exception as e:
        print(f"❌ Error in get_chat: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
@token_required
def delete_chat(chat_id):
    """Delete a chat session"""
    try:
        user_id = request.current_user["user_id"]
        success = delete_chat_session(chat_id, user_id)
        
        if success:
            return jsonify({"message": "Chat deleted successfully"})
        else:
            return jsonify({"error": "Chat not found"}), 404

    except Exception as e:
        print(f"❌ Error in delete_chat: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -------------------- VOICE API --------------------
@app.route("/api/voice", methods=["POST"])
@token_required
def voice_api():
    try:
        user_id = request.current_user["user_id"]
        audio = request.files.get("audio")

        if not audio:
            return jsonify({"error": "Audio file is required"}), 400

        result = handle_voice(audio, user_id)
        return jsonify(result)

    except Exception as e:
        print(f"❌ Error in voice_api: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -------------------- CHAT HISTORY --------------------
@app.route("/api/history", methods=["GET"])
@token_required
def history():
    try:
        user_id = request.current_user["user_id"]
        history = get_chat_history(user_id)
        return jsonify(history)

    except Exception as e:
        print(f"❌ Error in history_api: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -------------------- REPORT GENERATION --------------------
@app.route("/api/report", methods=["POST"])
def report_api():
    try:
        token = request.headers.get("Authorization")
        user_id = "trial_user"  # default access

        if token and token.startswith("Bearer "):
            token_str = token.split(" ")[1]
            user_data = verify_token(token_str)
            if user_data:
                user_id = user_data["user_id"]

        data = request.json

        crop_name = data.get("cropName")
        region = data.get("region")
        language = data.get("language")  # optional

        if not crop_name or not region:
            return jsonify({"error": "Crop name and region are required"}), 400

        report = generate_farming_report(
            user_id=user_id,
            crop_name=crop_name,
            region=region,
            language=language
        )

        if "error" in report:
            return jsonify(report), 500

        return jsonify(report)

    except Exception as e:
        print(f"❌ Error in report_api: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -------------------- REPORT HISTORY --------------------
@app.route("/api/reports", methods=["GET"])
@token_required
def report_history():
    try:
        user_id = request.current_user["user_id"]
        from services.db_service import get_user_reports
        reports = get_user_reports(user_id)
        return jsonify(reports)

    except Exception as e:
        print(f"❌ Error in report_history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )

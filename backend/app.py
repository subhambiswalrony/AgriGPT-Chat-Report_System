from flask import Flask, request, jsonify
from flask_cors import CORS

# Core feature handlers
from chat import handle_chat
from voice import handle_voice
from report import generate_farming_report

# Services
from services.db_service import get_chat_history

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

        if not message:
            return jsonify({"error": "Message is required"}), 400

        reply = handle_chat(user_id, message)
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"❌ Error in chat_api: {str(e)}")
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


# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    app.run(debug=True)

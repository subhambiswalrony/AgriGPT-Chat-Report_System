from services.llm_service import get_ai_response
from services.db_service import (
    save_chat, 
    create_chat_session, 
    update_chat_session, 
    generate_chat_title, 
    get_recent_chat_messages
)
from langdetect import detect

# Language-wise fallback messages (ALL Indian languages)
FALLBACK_MESSAGES = {
    "English": "🌾 I am AgriGPT 🌾 and I only assist with agricultural and farming-related queries.",
    "Hindi": "🌾 मैं AgriGPT हूँ और मैं केवल कृषि और खेती से संबंधित प्रश्नों में सहायता करता हूँ।",
    "Odia": "🌾 ମୁଁ AgriGPT 🌾 ଏବଂ ମୁଁ କେବଳ କୃଷି ଏବଂ ଚାଷ ସମ୍ବନ୍ଧୀୟ ପ୍ରଶ୍ନରେ ସହାୟତା କରେ।",
    "Bengali": "🌾 আমি AgriGPT 🌾 এবং আমি শুধুমাত্র কৃষি ও চাষাবাদ সংক্রান্ত প্রশ্নে সহায়তা করি।",
    "Tamil": "🌾 நான் AgriGPT 🌾 மற்றும் நான் வேளாண்மை மற்றும் விவசாயம் தொடர்பான கேள்விகளுக்கு மட்டுமே உதவுகிறேன்।",
    "Telugu": "🌾 నేను AgriGPT 🌾 మరియు నేను వ్యవసాయం మరియు సాగుకు సంబంధించిన ప్రశ్నలకే సహాయం చేస్తాను।",
    "Kannada": "🌾 ನಾನು AgriGPT 🌾 ಮತ್ತು ನಾನು ಕೃಷಿ ಮತ್ತು ಬೆಳೆಗಾರಿಕೆ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ ಮಾತ್ರ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ।",
    "Malayalam": "🌾 ഞാൻ AgriGPT 🌾 ആണ്, ഞാൻ കൃഷിയും കാർഷികവുമായി ബന്ധപ്പെട്ട ചോദ്യങ്ങൾക്ക് മാത്രമേ സഹായം നൽകൂ।",
    "Marathi": "🌾 मी AgriGPT 🌾 आहे आणि मी फक्त शेती व कृषी संबंधित प्रश्नांमध्येच मदत करतो।",
    "Gujarati": "🌾 હું AgriGPT 🌾 છું અને હું માત્ર ખેતી અને કૃષિ સંબંધિત પ્રશ્નોમાં મદદ કરું છું।",
    "Punjabi": "🌾 ਮੈਂ AgriGPT 🌾 ਹਾਂ ਅਤੇ ਮੈਂ ਸਿਰਫ਼ ਖੇਤੀਬਾੜੀ ਨਾਲ ਸੰਬੰਧਿਤ ਸਵਾਲਾਂ ਵਿੱਚ ਹੀ ਮਦਦ ਕਰਦਾ ਹਾਂ।",
    "Urdu": "🌾 میں AgriGPT 🌾 ہوں اور میں صرف زراعت اور کاشتکاری سے متعلق سوالات میں مدد کرتا ہوں۔",
    "Assamese": "🌾 মই AgriGPT 🌾 আৰু মই কেৱল কৃষি আৰু খেতি সম্পৰ্কীয় প্ৰশ্নত সহায় কৰোঁ।"
}

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "or": "Odia",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "as": "Assamese"
}


def detect_language(message: str) -> str:
    """
    Odia-safe language detection
    """

    # Only Odia Unicode detection
    for ch in message:
        if '\u0B00' <= ch <= '\u0B7F':
            return "Odia"

    # Other languages handled by langdetect
    try:
        lang_code = detect(message)
        return LANGUAGE_MAP.get(lang_code, "English")
    except Exception:
        return "English"


def build_context_aware_prompt(current_message: str, language: str, chat_history: list) -> str:
    """
    Build a structured prompt with conversation context.
    
    Args:
        current_message: The user's current message
        language: Detected language for response
        chat_history: List of previous messages [{"role": "user"/"assistant", "message": "..."}]
    
    Returns:
        Formatted prompt string with context
    """
    prompt_parts = []
    
    # 1. System instructions for AgriGPT personality
    prompt_parts.append(
        f"You are AgriGPT, a friendly agricultural assistant for Indian farmers. "
        f"Your purpose is to help with farming-related questions.\n"
        f"\nWhen introducing yourself or responding to greetings/questions about your capabilities:\n"
        f"- Say 'I am AgriGPT, your agricultural assistant'\n"
        f"- Mention you can help with: crop selection, soil & fertilizers, pest management, "
        f"irrigation, government schemes, and weather impact on farming\n"
        f"- Be warm, friendly, and conversational\n"
        f"- For 'how are you' type questions, respond naturally (e.g., 'I am fine and ready to help with your farming questions!')\n"
        f"- For 'what can you do' or 'your service', explain your agricultural assistance capabilities\n"
        f"- For general conversation starters like 'so let's begin', encourage them to ask their farming queries\n"
    )
    
    # 2. Language instruction (critical for multilingual support)
    prompt_parts.append(
        f"\nCRITICAL LANGUAGE RULE: You MUST respond COMPLETELY and ENTIRELY in {language} language only. "
        f"Do NOT mix languages. Do NOT switch languages mid-response. "
        f"Every single word must be in {language}.\n"
    )
    
    # 3. Conversation context (if exists)
    if chat_history and len(chat_history) > 0:
        prompt_parts.append("\n=== CONVERSATION HISTORY ===")
        for msg in chat_history:
            role_label = "User" if msg["role"] == "user" else "AgriGPT"
            prompt_parts.append(f"{role_label}: {msg['message']}")
        prompt_parts.append("=== END OF HISTORY ===\n")
    
    # 4. Current user message
    prompt_parts.append(f"\nCurrent User Question:\n{current_message}")
    
    # 5. Instruction for contextual understanding
    if chat_history:
        prompt_parts.append(
            "\nIMPORTANT: Use the conversation history above to understand context, "
            "references (like 'this', 'that', 'earlier'), and provide relevant answers. "
            f"Respond ONLY in {language} language."
        )
    
    return "\n".join(prompt_parts)


def handle_chat(user_id: str, message: str, chat_id: str = None) -> dict:
    """
    Process chat with session support:
    - detect input language (Odia-safe)
    - send ALL queries to Gemini API (including greetings, capability queries)
    - force same-language response from Gemini
    - use localized fallback only for non-agricultural queries
    - save chat history with chat_id
    - create new session if chat_id is None and user is authenticated
    - return chat_id with response
    """

    if not message or not message.strip():
        language = "English"
        response = FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["English"])
        response_type = "fallback"
    else:
        language = detect_language(message)
        
        # Retrieve recent conversation history for context (last 10 messages = ~5 pairs)
        chat_history = []
        if chat_id and user_id != "trial_user":
            try:
                chat_history = get_recent_chat_messages(chat_id, limit=10)
                if chat_history:
                    print(f"✓ Retrieved {len(chat_history)} recent messages for context")
                else:
                    print("ℹ No previous messages in this chat session")
            except Exception as e:
                print(f"✗ Error retrieving chat history: {str(e)}")
                chat_history = []
        else:
            if chat_id is None:
                print(f"ℹ New chat session - no history available")
            else:
                print(f"ℹ Trial user - limited history")

        # Build context-aware prompt with AgriGPT personality
        prompt = build_context_aware_prompt(message, language, chat_history)
        
        print(f"📤 Sending to Gemini API (with {len(chat_history)} context messages)")
        response = get_ai_response(prompt, chat_history=chat_history)

        # If Gemini indicates non-agriculture → localized fallback
        # Check if response matches any fallback message (in any language)
        is_fallback = any(
            fallback_msg.lower().replace(" ", "") in response.lower().replace(" ", "")
            for fallback_msg in FALLBACK_MESSAGES.values()
        )
        
        if is_fallback:
            response = FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["English"])
            response_type = "fallback"
        else:
            response_type = "ai"

    # Only save chat history for authenticated users (not trial users)
    if user_id != "trial_user":
        # Create new chat session if chat_id is None
        if chat_id is None:
            title = generate_chat_title(message, language)
            chat_id = create_chat_session(user_id, title, language)
        else:
            # Update existing session's updated_at
            update_chat_session(chat_id)
        
        # Save the messages
        save_chat(user_id, message, response, response_type, language, chat_id=chat_id)
    
    return {
        "reply": response,
        "chat_id": chat_id,
        "language": language
    }


"""For testing purposes only"""

# if __name__ == "__main__":
#     print(handle_chat("test_user", "Who is the PM of India?"))
#     print(handle_chat("test_user", "ଭାରତର ପ୍ରଧାନମନ୍ତ୍ରୀ କିଏ?"))
#     print(handle_chat("test_user", "भारत के प्रधानमंत्री कौन हैं?"))

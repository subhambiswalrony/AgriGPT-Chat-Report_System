from services.llm_service import get_ai_response
from services.db_service import save_chat
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


def handle_chat(user_id: str, message: str) -> str:
    """
    Process chat:
    - detect input language (Odia-safe)
    - force same-language response from Gemini
    - use localized fallback
    - save chat history
    """

    if not message or not message.strip():
        language = "English"
        response = FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["English"])
        response_type = "fallback"
    else:
        language = detect_language(message)

        prompt = (
            f"IMPORTANT: You MUST respond COMPLETELY and ENTIRELY in {language} language only. "
            f"Do NOT mix languages. Do NOT switch languages mid-response. "
            f"Every single word in your response must be in {language}.\n\n"
            f"User query:\n{message}"
        )

        response = get_ai_response(prompt)

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
        save_chat(user_id, message, response, response_type, language)
    
    return response


"""For testing purposes only"""

# if __name__ == "__main__":
#     print(handle_chat("test_user", "Who is the PM of India?"))
#     print(handle_chat("test_user", "ଭାରତର ପ୍ରଧାନମନ୍ତ୍ରୀ କିଏ?"))
#     print(handle_chat("test_user", "भारत के प्रधानमंत्री कौन हैं?"))

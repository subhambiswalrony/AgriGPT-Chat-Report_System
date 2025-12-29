from services.llm_service import get_ai_response
from services.db_service import save_report
from langdetect import detect

# Language mapping
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

def detect_language(text: str) -> str:
    """Detect language from text"""
    # Odia Unicode block
    for ch in text:
        if '\u0B00' <= ch <= '\u0B7F':
            return "Odia"

    try:
        return LANGUAGE_MAP.get(detect(text), "English")
    except Exception:
        return "English"


def generate_farming_report(user_id: str, crop_name: str, region: str, language: str = None) -> dict:
    """Generate comprehensive farming report using Gemini AI"""
    
    if not crop_name or not region:
        return {"error": "Crop name and region are required"}

    # Use provided language or detect from input
    if not language:
        language = detect_language(f"{crop_name} {region}")
    
    print(f"\n{'='*60}")
    print(f"📊 Generating Report:")
    print(f"   Crop: {crop_name}")
    print(f"   Region: {region}")
    print(f"   Language: {language}")
    print(f"   User: {user_id}")
    print(f"{'='*60}")

    # Language-specific instruction
    lang_instruction = f"Write EVERY single word in {language} language ONLY. Do NOT mix any other language."
    if language == "English":
        lang_instruction = "Write EVERY word in English only. Do NOT use Hindi, Odia, or any other language."
    elif language == "Hindi":
        lang_instruction = "हर शब्द केवल हिंदी में लिखें। अंग्रेजी या अन्य भाषा का उपयोग न करें।"

    prompt = f"""You are an expert agricultural advisor for Indian farmers.

**CRITICAL REQUIREMENT:**
{lang_instruction}

Generate a detailed farming report for:
- Crop: {crop_name}
- Region: {region}

Provide exactly 4 points for each of these 4 categories (write in {language} only):

**Category 1 - Sowing Advice:**
- Best sowing time and season
- Seed depth and spacing
- Row spacing
- Watering after sowing
Start each point with these emojis in order: 🌱 📏 🌾 💧

**Category 2 - Fertilizer Plan:**
- Nitrogen quantity (kg/hectare)
- Phosphorus quantity
- Potash quantity
- Organic manure recommendations
Start each point with these emojis in order: 🧪 🟡 🔴 🌿

**Category 3 - Weather Protection:**
- Sun/heat protection
- Rain/drainage management
- Cold weather protection
- Wind protection
Start each point with these emojis in order: ☀️ 🌧️ ❄️ 🌪️

**Category 4 - Farming Calendar:**
- Week 1-2 activities
- Week 3-4 activities
- Week 5-8 activities
- Week 12-16 harvest
Start each point with these emojis in order: 📅 🌱 💧 🌾

**IMPORTANT:** Format your response EXACTLY like this:

SOWING_ADVICE:
🌱 [advice in {language}]
📏 [advice in {language}]
🌾 [advice in {language}]
💧 [advice in {language}]

FERTILIZER_PLAN:
🧪 [plan in {language}]
🟡 [plan in {language}]
🔴 [plan in {language}]
🌿 [plan in {language}]

WEATHER_TIPS:
☀️ [tip in {language}]
🌧️ [tip in {language}]
❄️ [tip in {language}]
🌪️ [tip in {language}]

FARMING_CALENDAR:
📅 [schedule in {language}]
🌱 [schedule in {language}]
💧 [schedule in {language}]
🌾 [schedule in {language}]
"""

    try:
        # Get AI response
        response = get_ai_response(prompt)
        
        # Debug output
        print(f"\n✓ AI Response received ({len(response)} chars)")
        print(f"First 200 chars: {response[:200]}...")
        
        # Parse the response
        report_data = parse_report_response(response, crop_name, region, language)
        
        # Save to database (only for authenticated users)
        if user_id != "trial_user":
            try:
                save_report(user_id, crop_name, region, report_data, language)
                print(f"✓ Report saved to database for user: {user_id}")
            except Exception as e:
                print(f"⚠️ Failed to save report: {e}")

        print(f"✓ Report generated successfully")
        print(f"{'='*60}\n")
        
        return report_data

    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to generate report: {str(e)}"}


def parse_report_response(response: str, crop_name: str, region: str, language: str) -> dict:
    """Parse AI response into structured report data"""
    
    report = {
        "crop": crop_name,
        "region": region,
        "language": language,
        "sowingAdvice": [],
        "fertilizerPlan": [],
        "weatherTips": [],
        "calendar": []
    }

    try:
        print(f"\n🔍 Parsing response...")
        
        # Section header patterns
        section_map = {
            "sowingAdvice": ["SOWING_ADVICE", "SOWING ADVICE", "Sowing Advice"],
            "fertilizerPlan": ["FERTILIZER_PLAN", "FERTILIZER PLAN", "Fertilizer Plan"],
            "weatherTips": ["WEATHER_TIPS", "WEATHER TIPS", "Weather Tips"],
            "calendar": ["FARMING_CALENDAR", "FARMING CALENDAR", "Farming Calendar", "CALENDAR"]
        }

        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line is a section header
            section_found = False
            for section_key, patterns in section_map.items():
                if any(pattern in line for pattern in patterns):
                    current_section = section_key
                    section_found = True
                    print(f"  ✓ Found section: {section_key}")
                    break
            
            if section_found:
                continue

            # Add content to current section
            if current_section:
                # Clean line (remove bullets, numbers, extra spaces)
                cleaned = line.lstrip('•-*0123456789.').strip()
                
                # Skip very short lines or lines with section keywords
                if len(cleaned) < 10:
                    continue
                if any(kw in cleaned.upper() for kw in ['SOWING', 'FERTILIZER', 'WEATHER', 'FARMING', 'CALENDAR']):
                    continue
                
                report[current_section].append(cleaned)
                print(f"    → {section_key}: {cleaned[:60]}...")

        # Show parsing results
        print(f"\n📊 Parse Results:")
        print(f"  Sowing: {len(report['sowingAdvice'])} items")
        print(f"  Fertilizer: {len(report['fertilizerPlan'])} items")
        print(f"  Weather: {len(report['weatherTips'])} items")
        print(f"  Calendar: {len(report['calendar'])} items")

        # Use fallback if any section is empty
        if not all([report['sowingAdvice'], report['fertilizerPlan'], 
                   report['weatherTips'], report['calendar']]):
            print(f"⚠️ Some sections empty, using fallback data")
            fallback = get_fallback_data(crop_name, language)
            
            if not report['sowingAdvice']:
                report['sowingAdvice'] = fallback['sowingAdvice']
            if not report['fertilizerPlan']:
                report['fertilizerPlan'] = fallback['fertilizerPlan']
            if not report['weatherTips']:
                report['weatherTips'] = fallback['weatherTips']
            if not report['calendar']:
                report['calendar'] = fallback['calendar']

        return report

    except Exception as e:
        print(f"❌ Parse error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "crop": crop_name,
            "region": region,
            "language": language,
            **get_fallback_data(crop_name, language)
        }


def get_fallback_data(crop_name: str, language: str) -> dict:
    """Get language-specific fallback data"""
    
    fallbacks = {
        "English": {
            "sowingAdvice": [
                f"🌱 Sow {crop_name} during appropriate season for best yield",
                "📏 Maintain proper seed depth (2-3 cm) and plant spacing",
                "🌾 Keep 30-45 cm distance between rows for healthy growth",
                "💧 Provide adequate water immediately after sowing"
            ],
            "fertilizerPlan": [
                "🧪 Apply 120-150 kg Nitrogen per hectare in split doses",
                "🟡 Use 60-80 kg Phosphorus per hectare at sowing time",
                "🔴 Apply 40-60 kg Potash per hectare for better quality",
                "🌿 Add 5-7 tons organic manure before land preparation"
            ],
            "weatherTips": [
                "☀️ Provide shade or use mulching during extreme heat",
                "🌧️ Ensure proper drainage system during heavy rainfall",
                "❄️ Protect crop from frost using smoke or irrigation",
                "🌪️ Install windbreaks to protect from strong winds"
            ],
            "calendar": [
                "📅 Week 1-2: Land preparation and sowing activities",
                "🌱 Week 3-4: Germination and first weeding operation",
                "💧 Week 5-8: Regular irrigation and fertilizer application",
                "🌾 Week 12-16: Maturity signs and harvest preparation"
            ]
        },
        "Hindi": {
            "sowingAdvice": [
                f"🌱 {crop_name} की बुआई उपयुक्त मौसम में करें",
                "📏 बीज की गहराई 2-3 सेमी और उचित दूरी बनाए रखें",
                "🌾 पंक्तियों के बीच 30-45 सेमी की दूरी रखें",
                "💧 बुआई के तुरंत बाद हल्की सिंचाई करें"
            ],
            "fertilizerPlan": [
                "🧪 नाइट्रोजन 120-150 किग्रा प्रति हेक्टेयर विभाजित मात्रा में",
                "🟡 फास्फोरस 60-80 किग्रा प्रति हेक्टेयर बुआई के समय",
                "🔴 पोटाश 40-60 किग्रा प्रति हेक्टेयर गुणवत्ता के लिए",
                "🌿 जैविक खाद 5-7 टन प्रति हेक्टेयर जुताई से पहले"
            ],
            "weatherTips": [
                "☀️ अधिक गर्मी में छाया या मल्चिंग का प्रयोग करें",
                "🌧️ भारी बारिश में जल निकासी की व्यवस्था सुनिश्चित करें",
                "❄️ पाले से बचाव के लिए धुआं या सिंचाई करें",
                "🌪️ तेज हवा से बचाव के लिए वायु अवरोधक लगाएं"
            ],
            "calendar": [
                "📅 सप्ताह 1-2: भूमि तैयारी और बुआई कार्य",
                "🌱 सप्ताह 3-4: अंकुरण और प्रथम निराई",
                "💧 सप्ताह 5-8: नियमित सिंचाई और खाद प्रयोग",
                "🌾 सप्ताह 12-16: परिपक्वता और कटाई की तैयारी"
            ]
        },
        "Odia": {
            "sowingAdvice": [
                f"🌱 {crop_name} ଉପଯୁକ୍ତ ଋତୁରେ ବୁଣନ୍ତୁ",
                "📏 ବିହନ ଗଭୀରତା 2-3 ସେମି ଏବଂ ଦୂରତା ବଜାୟ ରଖନ୍ତୁ",
                "🌾 ଧାଡ଼ି ମଧ୍ୟରେ 30-45 ସେମି ଦୂରତା ରଖନ୍ତୁ",
                "💧 ବୁଣିବା ପରେ ତୁରନ୍ତ ହାଲକା ଜଳସେଚନ କରନ୍ତୁ"
            ],
            "fertilizerPlan": [
                "🧪 ନାଇଟ୍ରୋଜେନ୍ 120-150 କିଗ୍ରା ପ୍ରତି ହେକ୍ଟର",
                "🟡 ଫସଫରସ୍ 60-80 କିଗ୍ରା ବୁଣିବା ସମୟରେ",
                "🔴 ପୋଟାସ୍ 40-60 କିଗ୍ରା ଗୁଣବତ୍ତା ପାଇଁ",
                "🌿 ଜୈବିକ ଖତ 5-7 ଟନ୍ ଚାଷ ପୂର୍ବରୁ"
            ],
            "weatherTips": [
                "☀️ ଅଧିକ ଗରମରେ ଛାଇ କିମ୍ବା ମଲଚିଂ ବ୍ୟବହାର କରନ୍ତୁ",
                "🌧️ ଅଧିକ ବର୍ଷାରେ ଜଳ ନିଷ୍କାସନ ସୁନିଶ୍ଚିତ କରନ୍ତୁ",
                "❄️ କୁହୁଡ଼ିରୁ ରକ୍ଷା ପାଇଁ ଧୂଆଁ କିମ୍ବା ଜଳସେଚନ",
                "🌪️ ପ୍ରବଳ ପବନରୁ ରକ୍ଷା ପାଇଁ ବାୟୁ ପ୍ରତିବନ୍ଧକ"
            ],
            "calendar": [
                "📅 ସପ୍ତାହ 1-2: ଜମି ପ୍ରସ୍ତୁତି ଏବଂ ବୁଣିବା",
                "🌱 ସପ୍ତାହ 3-4: ଅଙ୍କୁରଣ ଏବଂ ପ୍ରଥମ ନିଡ଼ାଣି",
                "💧 ସପ୍ତାହ 5-8: ନିୟମିତ ଜଳସେଚନ ଏବଂ ସାର",
                "🌾 ସପ୍ତାହ 12-16: ପରିପକ୍ୱତା ଏବଂ ଅମଳ ପ୍ରସ୍ତୁତି"
            ]
        }
    }
    
    return fallbacks.get(language, fallbacks["English"])

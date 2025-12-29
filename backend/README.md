# 🌾 AgriGPT - Agricultural Expert Chatbot Backend

A multilingual AI-powered chatbot designed to assist Indian farmers with agriculture and farming-related queries. Built with Flask and powered by Google's Gemini AI.

## 🚀 Core Features

### 1. **Multilingual Support**
- Supports 13 Indian languages including:
  - English, Hindi, Odia, Bengali, Tamil, Telugu
  - Kannada, Malayalam, Marathi, Gujarati, Punjabi, Urdu, Assamese
- Automatic language detection with Odia-safe Unicode handling
- Responds in the same language as the user's query
- Language-specific fallback messages for non-agriculture queries

### 2. **AI-Powered Chat**
- Google Gemini 2.5-flash integration for intelligent responses
- Specialized agricultural knowledge base covering:
  - Crop cultivation practices
  - Fertilizers and soil types
  - Irrigation techniques
  - Pest and disease management
  - Weather impact on farming
  - Indian government agriculture schemes
  - Regional soil composition analysis
- Smart filtering: Only responds to agriculture-related queries
- Same-language enforcement (no language mixing)

### 3. **Voice Input Support**
- Speech-to-text transcription using Faster Whisper (offline, free)
- Whisper model: `tiny` (CPU, int8 compute)
- Audio file processing (supports multiple formats)
- Voice queries in multiple Indian languages
- AI-based agriculture query validation for voice inputs

### 4. **User Authentication & Authorization**
- JWT-based authentication system
- Secure user signup and login
- Password encryption with bcrypt
- Token-based API protection
- Token verification with `@token_required` decorator
- Profile management:
  - Update name and email
  - Change password with current password verification
- Automatic timestamp tracking:
  - Account creation time (`created_at`)
  - Last login time (`last_login`)

### 5. **Trial System for Non-Authenticated Users**
- Free trial access for text chat without authentication
- Trial users identified as `user_id="trial_user"`
- Trial user conversations NOT saved to database
- Voice features restricted to authenticated users only
- Seamless upgrade path to full features with authentication

### 6. **Farming Report Generation**
- AI-powered comprehensive farming reports using Gemini AI
- Generates reports in 13 Indian languages
- Report includes 4 key sections:
  - **Sowing Advice**: Timing, depth, spacing, watering (4 points)
  - **Fertilizer Plan**: NPK quantities, organic manure (4 points)
  - **Weather Protection**: Sun, rain, cold, wind (4 points)
  - **Farming Calendar**: Week-by-week activities (4 points)
- Language-specific prompts for accurate native responses
- Flexible parsing with multiple section detection patterns
- Comprehensive debug logging for troubleshooting
- Fallback data for English, Hindi, Odia
- Reports saved to database for authenticated users

### 7. **Chat History Management**
- Complete conversation history stored in MongoDB
- Tracks input types (text vs voice)
- Tracks response types (AI vs Fallback)
- Language detection per conversation
- Timestamped messages for all interactions
- Separate collections for chats and farming reports

### 8. **Database Integration**
- MongoDB for data persistence
- Database: `agrigpt`
- Collections:
  - `users` - User accounts with authentication details and timestamps
  - `chat_history` - Complete conversation logs with metadata
  - `farming_reports` - Generated farming reports with crop/region/language data
- Timezone-aware timestamps using `datetime.now(timezone.utc)`
- Comprehensive error handling and logging

## 📋 API Endpoints

### Health Check
- `GET /` - Server health status

### Authentication (No token required)
- `POST /api/signup` - User registration
  - Body: `{ "email": "user@example.com", "password": "password", "name": "Name" }`
  - Returns: `{ "user_id", "email", "name", "token" }`
  
- `POST /api/login` - User authentication
  - Body: `{ "email": "user@example.com", "password": "password" }`
  - Returns: `{ "user_id", "email", "name", "token" }`

### User Profile (Token required)
- `PUT /api/update-profile` - Update user profile
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ "name": "New Name", "email": "new@example.com" }`
  - Returns: `{ "success": true, "message", "name", "email" }`
  
- `PUT /api/change-password` - Change password
  - Headers: `Authorization: Bearer <token>`
  - Body: `{ "currentPassword": "old", "newPassword": "new" }`
  - Returns: `{ "success": true, "message" }`

### Chat (Trial & Authenticated)
- `POST /api/chat` - Send text message
  - Headers: `Authorization: Bearer <token>` (optional, defaults to trial user)
  - Body: `{ "message": "Your farming question" }`
  - Returns: `{ "reply": "AI response" }`

- `POST /api/voice` - Send voice input (authenticated users only)
  - Headers: `Authorization: Bearer <token>` (required)
  - Body: `multipart/form-data` with `audio` file
  - Returns: `{ "transcription": "...", "response": "...", "language": "..." }`

- `GET /api/history` - Retrieve chat history (authenticated users only)
  - Headers: `Authorization: Bearer <token>` (required)
  - Returns: Array of chat objects with timestamps

### Report Generation (Trial & Authenticated)
- `POST /api/report` - Generate farming report
  - Headers: `Authorization: Bearer <token>` (optional, defaults to trial user)
  - Body: `{ "cropName": "Rice", "region": "Odisha", "language": "English" }`
  - Returns: Report object with 4 sections (sowing, fertilizer, weather, calendar)

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running
- Google Gemini API key

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd "Major Project/backend"
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the `backend` directory:
   ```env
   # Gemini AI Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # MongoDB Configuration
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB=agrigpt
   
   # JWT Configuration (Optional)
   JWT_SECRET_KEY=your-secret-key-here
   JWT_EXPIRY_HOURS=24
   ```

5. **Start MongoDB**
   ```bash
   # Windows
   mongod
   
   # Linux/Mac
   sudo systemctl start mongod
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

   Server will start at: `http://localhost:5000`

## 📦 Dependencies

- **flask** - Web framework
- **flask-cors** - Cross-origin resource sharing
- **google-generativeai** - Gemini AI integration
- **pymongo** - MongoDB driver
- **pyjwt** - JWT token handling
- **bcrypt** - Password hashing
- **faster-whisper** - Speech recognition (offline STT)
- **langdetect** - Language detection
- **pydub** - Audio processing
- **python-dotenv** - Environment variable management
- **weasyprint** - PDF generation support
- **numpy, scipy, sounddevice, torch** - Audio processing dependencies

## 📁 Project Structure

```
backend/
├── app.py                  # Main Flask application with all routes
├── chat.py                 # Text chat handler with language detection
├── voice.py                # Voice input handler with Whisper STT
├── report.py               # Farming report generation with Gemini AI
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore              # Git ignore file
├── routes/
│   └── auth_routes.py      # Authentication & profile endpoints
├── services/
│   ├── __init__.py         # Service package initializer
│   ├── auth_service.py     # User auth logic with timestamps
│   ├── db_service.py       # MongoDB operations (3 collections)
│   ├── llm_service.py      # Gemini AI integration & system prompt
│   └── pdf_service.py      # PDF generation utilities
└── utils/
    ├── __init__.py         # Utils package initializer
    └── config.py           # Environment configuration loader
```

## 🔐 Authentication Flow

1. **Signup**: POST `/api/signup` with `{email, password, name}`
   - Checks for existing user
   - Hashes password with bcrypt
   - Returns JWT token and user details
   - Creates timestamp for account creation

2. **Login**: POST `/api/login` with `{email, password}`
   - Verifies credentials
   - Updates last login timestamp
   - Returns JWT token

3. **Profile Management**:
   - Update profile: PUT `/api/update-profile`
   - Change password: PUT `/api/change-password` (requires current password)

4. **Protected Endpoints**: Include token in header
   ```
   Authorization: Bearer <your-jwt-token>
   ```

5. **Trial Access**: Chat and report endpoints work without authentication
   - Text chat accessible without token (trial user)
   - Voice features require authentication
   - Trial users not saved to database

## 🧪 Testing with Postman

### 1. Signup
```json
POST http://localhost:5000/api/signup
Content-Type: application/json

{
  "email": "farmer@example.com",
  "password": "secure123",
  "name": "John Farmer"
}
```

### 2. Login
```json
POST http://localhost:5000/api/login
Content-Type: application/json

{
  "email": "farmer@example.com",
  "password": "secure123"
}
```

### 3. Update Profile
```json
PUT http://localhost:5000/api/update-profile
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "John Updated",
  "email": "newfarmer@example.com"
}
```

### 4. Change Password
```json
PUT http://localhost:5000/api/change-password
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "currentPassword": "secure123",
  "newPassword": "newsecure456"
}
```

### 5. Chat (Agricultural Query)
```json
POST http://localhost:5000/api/chat
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "message": "धान की खेती के लिए कौन सी मिट्टी सबसे अच्छी है?"
}
```

### 6. Generate Farming Report
```json
POST http://localhost:5000/api/report
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "cropName": "Rice",
  "region": "Odisha",
  "language": "English"
}
```

### 7. Get Chat History
```
GET http://localhost:5000/api/history
Authorization: Bearer <your-token>
```

### 8. Voice Input (requires audio file)
```
POST http://localhost:5000/api/voice
Authorization: Bearer <your-token>
Content-Type: multipart/form-data

audio: <audio-file.wav>
```

## 🌐 Language Support Examples

### Supported Languages (13)
- **English**: "What is the best fertilizer for rice?"
- **Hindi (हिन्दी)**: "धान के लिए सबसे अच्छा उर्वरक कौन सा है?"
- **Odia (ଓଡ଼ିଆ)**: "ଧାନ ପାଇଁ ସର୍ବୋତ୍ତମ ସାର କେଉଁଟି?"
- **Bengali (বাংলা)**: "ধানের জন্য সেরা সার কোনটি?"
- **Tamil (தமிழ்)**: "நெல் விவசாயத்திற்கு சிறந்த உரம் எது?"
- **Telugu (తెలుగు)**: "వరికి ఉత్తమ ఎరువు ఏది?"
- **Kannada (ಕನ್ನಡ)**: "ಅಕ್ಕಿಗೆ ಉತ್ತಮ ಗೊಬ್ಬರ ಯಾವುದು?"
- **Malayalam (മലയാളം)**: "നെല്ലിന് മികച്ച വളം എന്താണ്?"
- **Marathi (मराठी)**: "तांदळासाठी सर्वोत्तम खत कोणते?"
- **Gujarati (ગુજરાતી)**: "ચોખા માટે શ્રેષ્ઠ ખાતર કયું છે?"
- **Punjabi (ਪੰਜਾਬੀ)**: "ਚੌਲਾਂ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਖਾਦ ਕਿਹੜੀ ਹੈ?"
- **Urdu (اردو)**: "چاول کے لیے بہترین کھاد کون سی ہے؟"
- **Assamese (অসমীয়া)**: "ধানৰ বাবে সৰ্বশ্ৰেষ্ঠ সাৰ কি?"

## 📊 Database Schema

MongoDB Database: `agrigpt`

### Users Collection
```json
{
  "_id": ObjectId,
  "email": "farmer@example.com",
  "password": "hashed_bcrypt_password",
  "name": "John Farmer",
  "created_at": ISODate("2024-01-01T00:00:00.000Z"),
  "last_login": ISODate("2024-01-15T10:30:00.000Z")
}
```

### Chat History Collection
```json
{
  "_id": ObjectId,
  "user_id": "65abc123...",
  "input_type": "text",  // or "voice"
  "question": "धान की खेती कैसे करें?",
  "answer": "धान की खेती के लिए...",
  "response_type": "ai",  // or "fallback"
  "language": "Hindi",
  "timestamp": ISODate("2024-01-15T10:35:00.000Z")
}
```

### Farming Reports Collection
```json
{
  "_id": ObjectId,
  "user_id": "65abc123...",
  "crop_name": "Rice",
  "region": "Odisha",
  "language": "English",
  "report_data": {
    "sowingAdvice": [
      { "emoji": "🌱", "text": "Best sowing time..." },
      { "emoji": "📏", "text": "Seed depth and spacing..." },
      { "emoji": "🌾", "text": "Row spacing..." },
      { "emoji": "💧", "text": "Watering..." }
    ],
    "fertilizerPlan": [...],
    "weatherProtection": [...],
    "farmingCalendar": [...]
  },
  "timestamp": ISODate("2024-01-15T11:00:00.000Z")
}
```

## 🎯 Core Functionality Details

### 1. Language Detection System
- **Odia Unicode Detection**: Special handling for Odia (`\u0B00-\u0B7F`)
- **LangDetect Library**: Automatic detection for other languages
- **Fallback**: Defaults to English if detection fails
- **Same-Language Response**: AI forced to respond in detected language

### 2. Agriculture Validation
- **AI-Based Filtering**: Uses Gemini AI to validate agriculture-related queries
- **Localized Fallbacks**: Rejection messages in user's language
- **Domain Restriction**: Only agriculture/farming topics allowed

### 3. Voice Processing Pipeline
1. Upload audio file (any format)
2. Convert to WAV using pydub
3. Transcribe with Faster Whisper (offline)
4. Detect language from audio metadata
5. Validate agriculture domain with AI
6. Generate response in same language
7. Save to database with voice metadata

### 4. Report Generation Process
1. Receive crop name, region, language
2. Generate language-specific prompt
3. Request Gemini AI for comprehensive report
4. Parse response into 4 sections (16 points total)
5. Apply fallback data if parsing fails
6. Save report to database (authenticated users only)
7. Return structured JSON report

### 5. Trial vs Authenticated Users
| Feature | Trial Users | Authenticated Users |
|---------|-------------|---------------------|
| Text Chat | ✅ Free (10 messages) | ✅ Unlimited |
| Voice Input | ❌ Restricted | ✅ Available |
| Chat History | ❌ Not saved | ✅ Saved to DB |
| Report Generation | ✅ Available | ✅ Available |
| Report Saving | ❌ Not saved | ✅ Saved to DB |
| Profile Management | ❌ N/A | ✅ Update profile/password |

## 🔧 Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongosh

# In mongosh:
show dbs
use agrigpt
show collections
```

### Test Database Connectivity
```bash
python test_db.py
```
This script will:
- Test MongoDB connection
- Show document counts for all collections
- Display recent entries
- Test insert/delete operations

### Gemini API Issues
- Verify API key in `.env` file
- Check API quota at Google AI Studio
- Ensure internet connection for Gemini requests

### Language Detection Issues
- For Odia: Ensure Unicode text input
- For other languages: Check langdetect installation
- Default fallback is English

### Voice Processing Issues
- Ensure audio file is in supported format (WAV, MP3, etc.)
- Check Faster Whisper model installation
- Verify audio file size (< 10MB recommended)

## 🚀 Deployment Notes

### Production Configuration
1. Change `JWT_SECRET_KEY` to a strong random string
2. Set `debug=False` in `app.run()`
3. Use production MongoDB instance
4. Enable HTTPS for secure token transmission
5. Set up proper CORS origins
6. Use environment-specific `.env` files

### Recommended Production Setup
- **Web Server**: Gunicorn or uWSGI
- **Reverse Proxy**: Nginx
- **Database**: MongoDB Atlas (cloud) or self-hosted
- **SSL/TLS**: Let's Encrypt certificates
- **Monitoring**: Application logging and error tracking

## 📝 Development Tips

### Adding New Languages
1. Add language to `LANGUAGE_MAP` in `chat.py` and `report.py`
2. Add fallback message in `FALLBACK_MESSAGES`
3. Test language detection
4. Add language-specific prompts for reports

### Debugging Report Generation
- Check console output for debug logs
- Monitor section detection patterns
- Review AI response preview (first 200 chars)
- Check fallback warnings

### Testing Authentication
```python
# Generate test token
import jwt
from datetime import datetime, timedelta

payload = {
    "user_id": "test123",
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, "your-secret", algorithm="HS256")
print(token)
```

## 📚 Additional Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
- [JWT.io](https://jwt.io/) - JWT token debugger

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All new features include proper error handling
- Language support is comprehensive
- Agriculture domain validation works correctly

## 📄 License

This project is part of a Major Project for educational purposes.

## 👥 Support

For issues or questions:
- Check troubleshooting section above
- Review database schema and API documentation
- Test with `test_db.py` script
- Verify environment variables in `.env`

---

**Built with ❤️ for Indian Farmers** 🌾
  "created_at": ISODate,
  "last_login": ISODate
}
```

### Chat History Collection
```json
{
  "_id": ObjectId,
  "user_id": "user_object_id",
  "question": "User's question",
  "answer": "AI's response",
  "response_type": "ai" | "fallback",
  "language": "Hindi",
  "timestamp": ISODate
}
```

### Users Connections Collection
```json
{
  "_id": ObjectId,
  "user_id": "user_object_id",
  "connection_data": {},
  "timestamp": ISODate
}
```

## 🐛 Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check MONGO_URI in `.env` file

### Gemini API Error
- Verify GEMINI_API_KEY is correct
- Check API quota limits

### Language Detection Issues
- Ensure `langdetect` is installed
- Odia text uses special Unicode handling

### Audio Processing Error
- Install ffmpeg for audio format support
- Check audio file format compatibility

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is part of a Major Project for educational purposes.

## 👨‍💻 Developer

Created with ❤️ for Indian farmers

---

**Note**: Replace `<your-token>` and API keys with actual values when testing.
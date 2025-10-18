# Heidi AI Integration Project

This project demonstrates full integration with the [Heidi AI API](https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api) including authentication, session management, AI consultation, audio transcription, and consult note generation.

**✨ Featured Demo: Post-Surgery Care Assistant** - Transform discharge instructions into personalized care plans with AI-powered Q&A support.

## 🧠 Features

- **Token-based authentication (JWT)** - Secure API access
- **Session creation, update, and retrieval** - Manage patient sessions
- **Audio transcription workflow** - Convert speech to text
- **Consult note generation using Heidi templates** - Generate medical notes
- **Ask Heidi AI Assistant (streamed response)** - Real-time AI responses
- **Interactive Care Plan Demo** - Document processing to structured care plans
- **Medical Q&A Chat** - Patient question answering system

## 🚀 Quick Start - Running the Demo

### Prerequisites
- Python 3.8+
- pip package manager
- Heidi AI API credentials

### 1. Clone and Setup
```bash
git clone <https://github.com/xl-c111/heidi_AI_integration_project.git>
cd heidi_AI_integration_project

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### 2. Configure Environment
Copy the provided template and edit it with the credentials your reviewer or teammate shared:
```bash
cp .env.example .env
```

Update `.env` with:
- `HEIDI_API_KEY` – your organization’s Heidi API key  
- `HEIDI_EMAIL` – the user email registered with Heidi  
- `HEIDI_USER_ID` – the corresponding Heidi user UID

> **Tip for testers:** No credentials? Reach out to the maintainer for temporary sandbox values—most endpoints require them.

### 3. Test API Connection
```bash
# Verify your Heidi API credentials work
python3 tests/sse_parser_test.py

# Should output: "🎉🎉🎉 SUCCESS! 🎉🎉🎉"
```

### 4. Start the Demo
```bash
# Start the Flask application
python3 run.py

# Application will be available at: http://localhost:5000
```

### 5. Access the Demo
Open your browser and visit:
- **Main Demo**: http://localhost:5000/demo
- **API Test**: http://localhost:5000/test-jwt
- **Session Test**: http://localhost:5000/test-session

## 🎯 Demo Usage

### Document Processing to Care Plan
1. **Visit**: http://localhost:5000/demo
2. **Paste discharge instructions** in the text area (or use one of the examples below)
3. **Click "Generate Care Plan"** → Watch AI create structured care plan
4. **Ask questions** in the chat section → Get medical guidance

### Sample Discharge Instructions for Testing
```
Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food.
Take Amoxicillin 500mg three times daily for 7 days. Short walks recommended every 2 hours.
No lifting over 10 pounds for 2 weeks. Follow-up appointment in 1 week.
Watch for fever over 101°F, redness, or unusual swelling around incision site.
```

**More examples**:
- **Appendectomy**: Laparoscopic procedure with Acetaminophen, lifting restrictions
- **Hip Replacement**: Physical therapy, walker use, blood thinners
- **Gallbladder Surgery**: Dietary restrictions, wound care, activity levels
- **Cataract Surgery**: Eye drops, protective shield, activity restrictions

### Question Examples
Try asking these questions in the chat:
- "How much pain is normal after surgery?"
- "When can I start walking more?"
- "What signs of infection should I watch for?"
- "Can I take my medication with food?"

## 📁 Project Structure

```text
heidi-ai-integration/
├── .env.example                 # Sample environment configuration
├── .env                         # Local overrides (not committed)
├── .gitignore
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── run.py                        # Flask application entry point
├── config.py                     # Configuration settings
│
├── app/                          # Main application package
│   ├── __init__.py              # App factory
│   ├── api/                     # Heidi API integration
│   │   ├── auth.py              # JWT authentication
│   │   ├── session.py           # Session management
│   │   ├── ask_heidi.py         # AI chat functionality (SSE parsing)
│   │   ├── transcript.py        # Audio transcription
│   │   └── consult.py           # Consult note generation
│   │
│   ├── routes/                  # Flask route handlers
│   │   ├── demo.py              # Main demo endpoints
│   │   ├── auth.py              # Authentication routes
│   │   ├── session.py           # Session management routes
│   │   └── transcript.py        # Transcription routes
│   │
│   ├── templates/               # HTML templates
│   │   └── demo.html            # Interactive demo interface
│   │
│   └── storage.py               # In-memory data storage
│
└── tests/                       # Test scripts
    ├── sse_parser_test.py       # Complete API flow test
    ├── debug_tests.py           # API debugging tools
    └── test_api.py              # Basic API tests
```

## 🔧 API Endpoints

### Demo Endpoints
- `GET /demo` - Interactive care plan demo
- `POST /process-document` - Convert discharge instructions to care plan
- `POST /ask-question` - Medical Q&A chat

### Testing Endpoints
- `GET /test-jwt` - Verify JWT authentication
- `GET /test-session` - Test session creation
- `GET /get-token` - Get raw JWT token

### Heidi API Integration
- `POST /ask_heidi` - Direct AI assistant access
- `POST /consult/generate` - Generate consult notes
- `POST /transcript/upload` - Audio transcription
- `GET /consult/templates` - Available note templates

## 🧪 Testing

### Run Complete API Test
```bash
python3 tests/sse_parser_test.py
```
**Expected output**: JWT ✅ → Session ✅ → Care Plan ✅ → Q&A ✅

### Debug API Issues
```bash
python3 tests/debug_tests.py
```

### Test Individual Components
```bash
# Test authentication only
python3 tests/test_api.py

# Test with debugging
python3 tests/debug_response.py
```

## 🏥 Demo Features Showcase

### 1. Document Intelligence
- **Input**: Raw discharge instructions (text)
- **Processing**: Heidi AI analysis with medical knowledge
- **Output**: Structured care plan with sections:
  - 💊 Medication schedules with timing
  - 🚶 Activity guidelines and restrictions
  - 🩹 Wound care instructions
  - ⚠️ Warning signs to monitor
  - 📅 Follow-up appointment reminders

### 2. Medical Q&A Chat
- **Smart responses** to common post-surgery questions
- **Context-aware** advice based on procedure type
- **Safety-focused** with healthcare provider referrals
- **Real-time processing** with Server-Sent Events (SSE)

### 3. Professional UI
- **Responsive design** works on mobile and desktop
- **Loading animations** and progress indicators
- **Error handling** with user-friendly messages
- **Accessibility features** for healthcare settings

## 🔍 Troubleshooting

### Common Issues

**"Template Error: demo.html"**
```bash
# Make sure templates directory exists
mkdir -p app/templates
# Copy demo.html to app/templates/demo.html
```

**"JWT Failed" or Authentication Errors**
```bash
# Verify your .env file has correct credentials
cat .env
# Test credentials directly
python3 tests/debug_tests.py
```

**"Session Creation Failed"**
```bash
# Test session endpoint
curl -X GET http://localhost:5000/test-session
```

**Import Errors**
```bash
# Install missing dependencies
pip3 install flask python-dotenv requests
```

### Environment Variables Required
```bash
HEIDI_API_KEY=your_actual_api_key
HEIDI_EMAIL=your_registered_email
HEIDI_USER_ID=your_user_identifier
```

## 🎉 Demo Success Indicators

When everything is working correctly, you should see:

1. **Demo loads** at http://localhost:5000/demo with professional UI
2. **Document processing** generates real AI care plans (not mock data)
3. **Questions return** detailed medical guidance from Heidi AI
4. **No console errors** in browser developer tools
5. **API tests pass** with "🎉 SUCCESS!" messages

## 🚀 Production Considerations

For production deployment:
- Replace in-memory storage with database (PostgreSQL/MySQL)
- Implement proper user authentication and sessions
- Add rate limiting and API quotas
- Set up proper logging and monitoring
- Use environment-specific configuration
- Implement proper error tracking

## 📞 Support

- **API Issues**: Check Heidi AI documentation
- **Setup Problems**: Verify all dependencies installed
- **Demo Not Working**: Run test scripts first
- **Need Features**: Check existing routes and endpoints

---

**Ready to demo?** Run `python3 run.py` and visit http://localhost:5000/demo! 🏥✨

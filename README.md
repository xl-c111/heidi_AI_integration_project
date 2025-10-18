# Heidi AI Integration Project

This project demonstrates a comprehensive integration with the [Heidi AI API](https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api) for post-surgery care management, featuring document processing, AI-powered care plan generation, voice transcription, and interactive patient Q&A.

**✨ Featured Demo: AI-Powered Post-Surgery Care Assistant** - Transform discharge instructions into personalized care plans with voice-enabled Q&A support and audio transcription capabilities.

## 🧠 Core Features

### Backend API Integration
- **JWT Authentication** - Secure token-based API access
- **Session Management** - Create, update, and retrieve patient sessions
- **Server-Sent Events (SSE) Parsing** - Real-time AI response streaming
- **Audio Transcription Workflow** - Convert speech to text with full workflow support
- **AI Chat Integration** - Powered by Heidi's medical AI with enhanced error handling

### Interactive Demo Application
- **Document Processing** - Upload discharge papers or paste text for AI analysis
- **Care Plan Generation** - AI creates structured, personalized recovery plans
- **Voice Questions** - Record audio questions or upload audio files
- **Text Chat** - Type questions for instant AI medical guidance
- **Beautiful UI** - Professional, responsive design optimized for healthcare

### Advanced Features
- **Multiple Input Methods** - Text, voice recording, and file upload
- **Smart Response Formatting** - Structured care plans with medication schedules, activity guidelines, wound care, and warning signs
- **Error Recovery** - Comprehensive error handling with fallback strategies
- **Real-time Processing** - Live audio transcription and AI response generation

## 🚀 Quick Start

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

### 3. Run Tests
```bash
# Execute the pytest suite (mocks Heidi API calls)
pytest
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
- **API Health Check**: http://localhost:5000/health
- **Environment Check**: http://localhost:5000/env-check

## 🎯 Demo Walkthrough

1. Visit http://localhost:5000/demo  
2. Provide a discharge summary (upload PDF/image or paste text)  
3. Select “Generate Care Plan” to see a structured response  
4. Record or upload audio to test the transcription pipeline  
5. Ask follow-up questions in chat; responses stream via SSE

### Sample Inputs
- **Discharge snippet**  
  `Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food.`
- **Follow-up question**  
  `"How much pain is normal after surgery?"`
- **Audio types**: MP3, WAV, M4A, AAC (≤10 MB)

## 🗂️ Project Structure

```
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
│   ├── __init__.py              # App factory with blueprint registration
│   │
│   ├── api/                     # Heidi API integration layer
│   │   ├── __init__.py          # API base configuration
│   │   ├── auth.py              # JWT authentication handler
│   │   ├── session.py           # Session lifecycle management
│   │   ├── ask_heidi.py         # AI chat with SSE parsing
│   │   ├── transcript.py        # Audio transcription workflow
│   │   └── consult.py           # Medical consultation features
│   │
│   ├── routes/                  # Flask route handlers
│   │   ├── __init__.py          # Routes package initialization
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── session.py           # Session management routes
│   │   ├── ask_heidi.py         # AI interaction endpoints
│   │   ├── transcript.py        # Audio processing routes
│   │   ├── consult.py           # Medical consultation routes
│   │   ├── demo.py              # Main demo application
│   │   └── document.py          # Document processing routes
│   │
│   ├── templates/               # HTML templates
│   │   └── demo.html            # Interactive demo interface
│   │
│   └── storage.py               # In-memory data storage (demo)
│
├── tests/                       # Pytest suite (mocked Heidi API)
│   ├── conftest.py              # Shared fixtures and env setup
│   ├── test_auth.py             # JWT authentication coverage
│   ├── test_session.py          # Session lifecycle tests
│   ├── test_ask_heidi.py        # SSE parsing and AI responses
│   └── test_transcript.py       # Audio transcription workflow
│
└── html/                        # Additional UI prototypes
    ├── user_dashboard.html
    ├── community_frontend.html
    └── hospital_frontend.html
```

## 🔧 Key Endpoints

| Category | Endpoint | Notes |
| --- | --- | --- |
| Demo UI | `GET /demo` | Main healthcare assistant |
| Documents | `POST /process-document` | Generate care plan from discharge text |
| Q&A | `POST /ask-question` | Patient-friendly AI replies |
| Audio | `POST /transcribe-audio` | Upload or record voice questions |
| Health | `GET /health` | App heartbeat |
| Environment | `GET /env-check` | Validate env vars |
| Sessions | `POST /sessions`, `GET /sessions/<id>` | REST helpers for clinical sessions |

## 🧪 Testing

Run the mocked suite:
```bash
pytest
```

Coverage highlights:
- JWT acquisition and failure handling
- Session lifecycle (create, fetch, update)
- Ask Heidi SSE + JSON parsing
- Audio transcription start/upload/finish steps

Add optional integration tests (marked, skipped by default) if you need to hit Heidi’s sandbox.

## 🎨 Frontend Notes
- Responsive layout tuned for desktop and tablet
- Drag-and-drop uploads with progress indicators
- Streaming responses rendered in real time
- Accessible color palette and typography

## 🔍 Troubleshooting

### Common Issues
| Symptom | Quick Check |
| --- | --- |
| Demo returns 500 | Confirm templates exist and Flask logs have no import errors |
| Auth failures | `pytest tests/test_auth.py -q` and verify `.env` values |
| Audio upload errors | `pytest tests/test_transcript.py -q` and confirm file < 10 MB |
| Stale sessions | Hit `GET /test-session` to verify the Heidi session API |

### Environment Checklist
```
HEIDI_API_KEY=...
HEIDI_EMAIL=...
HEIDI_USER_ID=...
```

## ✅ Readiness Checklist
- Demo reachable at `/demo` with no console errors
- `/process-document` returns structured care plans
- `/ask-question` streams coherent responses
- `/transcribe-audio` returns transcript text
- `pytest` passes locally

## 🚀 Production Considerations

| Focus | Next Steps |
| --- | --- |
| Infrastructure | Persistent DB, Redis cache, centralized logging |
| Security | Authn/Authz, rate limiting, HTTPS, secret management |
| Scalability | Containerize, add load balancing, async audio pipeline |
| Observability | Structured logging, metrics, alerting |

## 📞 Support & Development

### API Documentation
- **Heidi AI API**: Check official documentation for endpoint specifications
- **Audio Formats**: Supports MP3, WAV, M4A, AAC up to 10MB
- **Response Format**: Server-Sent Events (SSE) for real-time streaming

### Development Tips
- Use `pytest -k ask_heidi` for quick AI-client checks
- Tail Flask logs for upstream API issues
- Capture browser console logs when debugging UI flows
- Keep sample PDFs/audio handy for manual QA

---

**Ready to demo?** Run `python3 run.py` and visit http://localhost:5000/demo 🏥✨

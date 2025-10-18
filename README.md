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
- **API Health Check**: http://localhost:5000/health
- **Environment Check**: http://localhost:5000/env-check

## 🎯 Demo Usage Guide

### 1. Document Processing to Care Plan
1. **Visit**: http://localhost:5000/demo
2. **Input Options**:
   - Upload discharge papers (PDF, JPG, PNG)
   - Paste discharge instructions in the text area
   - Use provided examples for testing
3. **Click "Generate Care Plan"** → Watch AI create structured care plan
4. **Review Results** → Get organized medication schedules, activity guidelines, wound care instructions

### 2. Voice & Audio Questions
1. **Record Live**: Click microphone button to record questions
2. **Upload Audio**: Drag and drop audio files (MP3, WAV, M4A, AAC)
3. **Type Questions**: Use text input for quick queries
4. **Get AI Responses**: Receive medical guidance powered by Heidi AI

### Sample Test Data

#### Discharge Instructions Examples
```
Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food.
Take Amoxicillin 500mg three times daily for 7 days. Short walks recommended every 2 hours.
No lifting over 10 pounds for 2 weeks. Follow-up appointment in 1 week.
Watch for fever over 101°F, redness, or unusual swelling around incision site.
```

**Additional Test Cases**:
- **Appendectomy**: Post-laparoscopic care with dietary restrictions
- **Hip Replacement**: Physical therapy protocols and mobility aids
- **Gallbladder Surgery**: Post-surgical diet and activity modifications
- **Cataract Surgery**: Eye care and vision protection guidelines

#### Question Examples
- "How much pain is normal after surgery?"
- "When can I start walking more?"
- "What signs of infection should I watch for?"
- "Can I take my medication with food?"
- "How long does recovery typically take?"

## 📁 Project Architecture

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
├── tests/                       # Comprehensive test suite
│   ├── sse_parser_test.py       # Complete API workflow validation
│   ├── debug_hedi_api.py        # API debugging and diagnostics
│   ├── test_audio_feature.py    # Audio transcription testing
│   ├── complete_test.py         # End-to-end integration test
│   └── test_api.py              # Basic API connectivity test
│
└── html/                        # Additional frontend demos
    ├── user_dashboard.html       # Patient dashboard mockup
    ├── community_frontend.html   # Community care interface
    └── hospital_frontend.html    # Hospital staff interface
```

## 🔧 API Endpoints

### Demo Application
- `GET /demo` - Interactive care plan demo
- `POST /process-document` - Convert discharge instructions to care plan
- `POST /ask-question` - Medical Q&A chat interface
- `POST /transcribe-audio` - Audio file transcription

### System Health & Debugging
- `GET /health` - Application health check
- `GET /env-check` - Environment variables validation
- `GET /test-jwt` - JWT authentication test
- `GET /test-session` - Session creation test
- `POST /test-complete-flow` - End-to-end workflow test

### Core API Integration
- `POST /ask_heidi` - Direct AI assistant access
- `POST /ask_heidi_enhanced` - AI with fallback strategies
- `POST /consult/generate` - Generate medical consultation notes
- `GET /consult/templates` - Available consultation templates
- `POST /transcript/upload` - Audio file processing

## 🧪 Testing & Validation

### Run Complete Integration Test
```bash
python3 tests/sse_parser_test.py
```
**Expected Flow**: JWT ✅ → Session ✅ → Care Plan ✅ → Q&A ✅

### Debug API Issues
```bash
python3 tests/debug_hedi_api.py
```

### Test Audio Features
```bash
python3 tests/test_audio_feature.py
```

### Validate Individual Components
```bash
# Test authentication
python3 tests/test_api.py

# Test complete workflow
python3 tests/complete_test.py
```

## 🎨 Frontend Features

### Professional UI Design
- **Responsive Layout** - Works seamlessly on desktop and mobile
- **Loading Animations** - Progress indicators for all async operations
- **Error Handling** - User-friendly error messages with recovery suggestions
- **Accessibility** - Proper contrast ratios and semantic markup

### Interactive Elements
- **Drag & Drop** - File upload with visual feedback
- **Voice Recording** - Real-time audio capture with visual indicators
- **Progress Tracking** - Visual progress bars for multi-step processes
- **Dynamic Content** - Real-time updates without page refresh

### Care Plan Visualization
- **Structured Sections** - Organized medication, activity, and care instructions
- **Color-Coded Categories** - Visual differentiation of care plan sections
- **Responsive Cards** - Hover effects and smooth transitions
- **Mobile-Optimized** - Touch-friendly interface for mobile devices

## 🔍 Troubleshooting

### Common Issues & Solutions

**Demo Page Not Loading**
```bash
# Ensure templates directory exists
ls app/templates/demo.html

# If missing, check file path and permissions
```

**Authentication Failures**
```bash
# Verify environment variables
python3 tests/debug_hedi_api.py

# Check API credentials are current and valid
```

**Audio Transcription Issues**
```bash
# Test audio workflow
python3 tests/test_audio_feature.py

# Verify supported file formats: MP3, WAV, M4A, AAC
```

**Session Creation Problems**
```bash
# Test session endpoint directly
curl -X GET http://localhost:5000/test-session
```

### Environment Setup Verification
```bash
# Required environment variables
HEIDI_API_KEY=your_actual_api_key
HEIDI_EMAIL=your_registered_email
HEIDI_USER_ID=your_user_identifier
```

### Performance Optimization
- Audio files are limited to 10MB for optimal processing
- Sessions automatically handle JWT token refresh
- SSE parsing ensures efficient real-time communication
- Error recovery mechanisms prevent cascading failures

## 🎉 Success Indicators

When everything is working correctly:

1. **Demo loads** at http://localhost:5000/demo with professional healthcare UI
2. **Document processing** generates real AI care plans (not mock data)
3. **Voice questions** return detailed medical guidance from Heidi AI
4. **Audio transcription** converts speech to text accurately
5. **No console errors** in browser developer tools
6. **API tests pass** with "🎉 SUCCESS!" messages in terminal

## 🚀 Production Considerations

For deployment to production environments:

### Infrastructure
- Replace in-memory storage with persistent database (PostgreSQL/MySQL)
- Implement Redis for session management and caching
- Set up proper logging and monitoring (ELK stack or similar)
- Configure environment-specific settings with proper secrets management

### Security
- Implement proper user authentication and authorization
- Add rate limiting and API quotas
- Set up HTTPS/TLS encryption
- Implement proper error tracking without exposing sensitive information

### Scalability
- Containerize with Docker for consistent deployments
- Set up load balancing for multiple instances
- Implement async processing for audio transcription
- Add CDN for static assets and improved performance

## 📞 Support & Development

### API Documentation
- **Heidi AI API**: Check official documentation for endpoint specifications
- **Audio Formats**: Supports MP3, WAV, M4A, AAC up to 10MB
- **Response Format**: Server-Sent Events (SSE) for real-time streaming

### Development Tips
- Use `python3 tests/debug_hedi_api.py` for comprehensive API debugging
- Monitor browser console for frontend JavaScript errors
- Check Flask logs for backend API communication issues
- Test with sample data before using real patient information

### Feature Requests
The codebase is designed for extensibility:
- Additional medical specialties can be added to the AI prompts
- More file formats can be supported with minimal changes
- Dashboard features are already prototyped in the html/ directory
- Integration with other healthcare APIs is straightforward

---

**Ready to demo?** Run `python3 run.py` and visit http://localhost:5000/demo! 🏥✨

# Heidi AI Integration Project

This project demonstrates full integration with the [Heidi AI API](https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api) including authentication, session management, AI consultation, audio transcription, and consult note generation. It also includes the ability to embed the Heidi Widget.

## 🧠 Features

- Token-based authentication (JWT)
- Session creation, update, and retrieval
- Audio transcription workflow
- Consult note generation using Heidi templates
- Ask Heidi AI Assistant (streamed response)
- Heidi Widget demo and integration

## 📁 Project Structure

```text
heidi-ai-integration/
├── .env                          # API credentials and config values
├── .gitignore
├── README.md                     # Project overview and setup guide
├── requirements.txt              # Python dependencies
│
├── app.py                        # Flask application entry point
│
├── heidi_client/                 # Heidi API integration logic
│   ├── __init__.py
│   ├── config.py                 # Load values from .env
│   ├── auth.py                   # get_token()
│   ├── session.py                # create/update session
│   ├── transcription.py          # upload and retrieve transcript
│   ├── consult_note.py           # generate consult notes
│   ├── ask_ai.py                 # ask_heidi() logic
│
├── routes/                       # Flask API route handlers
│   ├── __init__.py
│   ├── auth.py                   # /get-jwt-token
│   ├── consult.py                # /generate-note
│   ├── transcription.py          # /upload-audio, /get-transcript
│   ├── ask.py                    # /ask-ai
│   ├── context.py                # /get-context/<patient_id> ← new: provide patient context
│   ├── notes.py                  # /save-note, /save-document ← new: store pushed notes/docs
│   ├── session_cache.py          # session tracking / restore support ← new
│
├── static/                       # Static assets (served to browser)
│   ├── js/
│   │   └── heidi_widget.js       # Frontend widget logic: open, callbacks, setPatient, etc.
│   ├── css/
│   └── audio/
│
├── templates/                    # Jinja2 HTML templates
│   └── index.html                # Widget demo UI (injects Heidi + controls)
│
├── scripts/                      # CLI tools for quick testing
│   ├── ask_ai.py
│   ├── test_session.py
│   ├── upload_audio.py
│   └── generate_note.py
│
├── tests/                        # Unit/integration tests
│   ├── test_auth.py
│   ├── test_notes.py             # ← new: test saving pushed note/doc
│   └── test_context.py           # ← new: test patient context API
│
└── migrations/                   # (optional) For database schema tracking if using DB

```

## ✅ What Can Be Prebuilt Before the Hackathon?

| Part                          | Can Prebuild? | Notes                                              |
|-------------------------------|---------------|----------------------------------------------------|
| `app.py` (Flask app)          | ✅ Yes        | Register blueprints, set up app factory            |
| `heidi_client/*.py`           | ✅ Yes        | Token, session, ask_ai, transcription modules      |
| `scripts/*.py` (CLI utils)    | ✅ Yes        | Useful for module testing                          |
| `templates/index.html`        | ✅ Yes        | Widget embed and testing                           |
| `.env` & `config.py`          | ✅ Yes        | Load keys securely (exclude `.env` from GitHub)    |
| `routes/*.py` (Flask routes)  | ✅ Yes        | Define endpoints early and refine as needed        |

> ⚠️ **Note:** Never commit `.env` or real credentials to version control.

## 🚀 Getting Started

1. Clone this repository
2. Create a `.env` file with your API credentials:

```bash
HEIDI_API_KEY=your_key
HEIDI_EMAIL=your_email
HEIDI_USER_ID=your_user_id
```

3. Install dependencies:
```bash
pip3 install -r requirements.txt
```

4. Run the Flask app:
```bash
python3 app.py
```

---

Need help implementing a specific route or feature? Open an issue or contact the maintainer.

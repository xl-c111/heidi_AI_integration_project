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
├── .env                        # API credentials (not pushed to GitHub)
├── .gitignore
├── README.md                   # Project overview and usage guide
├── requirements.txt            # Python dependencies
│
├── app.py                      # Flask application entry point
│
├── heidi_client/               # Heidi API integration logic
│   ├── __init__.py
│   ├── config.py               # Load API_KEY, EMAIL, etc. from .env
│   ├── auth.py                 # get_token()
│   ├── session.py              # create_session(), update_session()
│   ├── transcription.py        # upload, finish, and retrieve transcript
│   ├── consult_note.py         # generate consult notes
│   ├── ask_ai.py               # ask_heidi() logic for AI Q&A
│
├── routes/                     # Flask route handlers
│   ├── __init__.py
│   ├── sessions.py             # /create-session, /update-session
│   ├── consult.py              # /generate-note
│   ├── transcription.py        # /upload-audio, /get-transcript
│   ├── ask.py                  # /ask-ai
│
├── static/                     # Static assets (for widget and audio)
│   ├── js/
│   ├── css/
│   └── audio/
│
├── templates/                  # HTML templates (widget demo page)
│   └── index.html              # Optionally embed widget here
│
├── scripts/                    # CLI/utility scripts
│   ├── ask_ai.py               # Ask Heidi via CLI
│   ├── test_session.py         # Create & update a session
│   ├── upload_audio.py         # Upload audio & transcribe
│   └── generate_note.py        # Generate consult note
│
└── tests/                      # Optional: Unit tests
    └── test_auth.py
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
pip install -r requirements.txt
```

4. Run the Flask app:
```bash
python app.py
```

---

Need help implementing a specific route or feature? Open an issue or contact the maintainer.

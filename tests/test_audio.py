import os
from dotenv import load_dotenv
from app.api.auth import get_jwt_token
from app.api.session import create_session
from app.api.transcript import (
    start_transcription,
    upload_audio,
    finish_transcription,
    get_transcript
)

load_dotenv()  # Load environment variables from .env

def main():
    # Step 1: Get JWT token
    jwt_token = get_jwt_token()
    if isinstance(jwt_token, str) and (jwt_token.startswith("Error") or jwt_token.startswith("Exception")):
        print("Failed to get token:", jwt_token)
        return

    print("✅ JWT token obtained.")

    # Step 2: Create session
    session_id = create_session(jwt_token)
    if isinstance(session_id, dict) and session_id.get("error"):
        print("❌ Failed to create session:", session_id)
        return

    print(f"✅ Session created: {session_id}")

    # Step 3: Start transcription
    recording_id = start_transcription(jwt_token, session_id)
    if isinstance(recording_id, dict) and recording_id.get("error"):
        print("❌ Failed to start transcription:", recording_id)
        return

    print(f"✅ Transcription started. Recording ID: {recording_id}")

    # Step 4: Upload audio file
    file_path = os.path.join("static", "Going_Down_Stairs.mp3")
    if not os.path.exists(file_path):
        print(f"❌ Audio file not found: {file_path}")
        return

    print("⏫ Uploading audio...")
    upload_response = upload_audio(jwt_token, session_id, recording_id, file_path)
    print("✅ Upload response:", upload_response)

    # Step 5: Finish transcription
    finish_response = finish_transcription(jwt_token, session_id, recording_id)
    print("✅ Finish response:", finish_response)

    # Step 6: Get transcript
    transcript = get_transcript(jwt_token, session_id)
    print("📄 Transcript result:\n", transcript)

if __name__ == "__main__":
    main()

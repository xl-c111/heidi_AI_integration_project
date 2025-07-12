# routes/transcript.py
import os
from flask import Blueprint, request, jsonify
from app.api.transcript import start_transcription, upload_audio, finish_transcription, get_transcript
from app.api.auth import get_jwt_token
from app.api.consult import get_consult_note_templates, generate_consult_note
from app.api.session import create_session

transcript_bp = Blueprint('transcript', __name__)


@transcript_bp.route('/transcript/start', methods=['POST'])
def route_start_transcription():
    jwt = get_jwt_token()
    session_id = request.json.get("session_id")
    result = start_transcription(jwt, session_id)
    return jsonify({"recording_id": result})


@transcript_bp.route('/transcript/upload', methods=['POST'])
def route_upload_audio():
    jwt = get_jwt_token()
    session_id = request.form.get("session_id")
    recording_id = request.form.get("recording_id")
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file provided"}), 400

    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    result = upload_audio(jwt, session_id, recording_id, file_path)
    return jsonify(result)


@transcript_bp.route('/transcript/finish', methods=['POST'])
def route_finish_transcription():
    jwt = get_jwt_token()
    data = request.json
    session_id = data.get("session_id")
    recording_id = data.get("recording_id")
    result = finish_transcription(jwt, session_id, recording_id)
    return jsonify(result)


@transcript_bp.route('/transcript/view', methods=['GET'])
def route_view_transcript():
    jwt = get_jwt_token()
    session_id = request.args.get("session_id")
    result = get_transcript(jwt, session_id)
    return jsonify(result)


@transcript_bp.route('/demo/full-transcript', methods=['POST'])
def full_transcription_demo():
    jwt = get_jwt_token()

    # Step 1: Create session
    session_id = create_session(jwt)
    if not session_id:
        return jsonify({"error": True, "message": "Failed to create session"})

    # Step 2: Start transcription
    recording_id = start_transcription(jwt, session_id)
    if not recording_id:
        return jsonify({"error": True, "message": "Failed to start transcription"})

    # Step 3: Handle uploaded audio
    uploaded_file = request.files.get('audio')
    if not uploaded_file or not uploaded_file.filename.endswith('.mp3'):
        return jsonify({"error": True, "message": "No valid MP3 file provided"})

    # Save to a temp location
    temp_path = os.path.join('/tmp', uploaded_file.filename)
    uploaded_file.save(temp_path)

    upload_result = upload_audio(jwt, session_id, recording_id, temp_path)
    if not upload_result.get("is_success"):
        return jsonify({"error": True, "message": "Audio upload failed", "details": upload_result})

    # Step 4: Finish transcription
    finish_result = finish_transcription(jwt, session_id, recording_id)
    if not finish_result.get("is_success"):
        return jsonify({"error": True, "message": "Failed to finish transcription"})

    # Step 5: Get first consult note template
    templates = get_consult_note_templates(jwt)
    if not templates or "templates" not in templates or len(templates["templates"]) == 0:
        return jsonify({"error": True, "message": "No consult templates found"})

    template_id = templates["templates"][0]["id"]

    # Step 6: Generate consult note
    note = generate_consult_note(
        jwt, session_id, template_id, voice_style="BRIEF", brain="LEFT")
    print(note)
    return jsonify({"note": note})

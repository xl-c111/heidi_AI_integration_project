from flask import Blueprint, jsonify, request

from app.api.consult import generate_consult_note, get_consult_note_templates
from app.services.common import ensure_session, fetch_jwt_token
from app.services.transcription import (
    finish_transcription_service,
    start_transcription_service,
    transcript_lookup_service,
    upload_audio_service,
)

transcript_bp = Blueprint("transcript", __name__)


def _jsonify_service(result):
    payload, status = result
    return jsonify(payload), status


@transcript_bp.route("/transcript/start", methods=["POST"])
def route_start_transcription():
    jwt_token, error = fetch_jwt_token()
    if error:
        return _jsonify_service(error)

    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    return _jsonify_service(start_transcription_service(jwt_token, session_id))


@transcript_bp.route("/transcript/upload", methods=["POST"])
def route_upload_audio():
    jwt_token, error = fetch_jwt_token()
    if error:
        return _jsonify_service(error)

    session_id = request.form.get("session_id")
    recording_id = request.form.get("recording_id")
    file = request.files.get("file")

    if not session_id or not recording_id:
        return jsonify({"error": "session_id and recording_id are required"}), 400

    return _jsonify_service(
        upload_audio_service(jwt_token, session_id, recording_id, file)
    )


@transcript_bp.route("/transcript/finish", methods=["POST"])
def route_finish_transcription():
    jwt_token, error = fetch_jwt_token()
    if error:
        return _jsonify_service(error)

    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    recording_id = data.get("recording_id")

    if not session_id or not recording_id:
        return jsonify({"error": "session_id and recording_id are required"}), 400

    return _jsonify_service(
        finish_transcription_service(jwt_token, session_id, recording_id)
    )


@transcript_bp.route("/transcript/view", methods=["GET"])
def route_view_transcript():
    jwt_token, error = fetch_jwt_token()
    if error:
        return _jsonify_service(error)

    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id query parameter is required"}), 400

    return _jsonify_service(transcript_lookup_service(jwt_token, session_id))


@transcript_bp.route("/demo/full-transcript", methods=["POST"])
def full_transcription_demo():
    jwt_token, error = fetch_jwt_token()
    if error:
        return _jsonify_service(error)

    session_id, session_error = ensure_session(jwt_token, None)
    if session_error:
        return _jsonify_service(session_error)

    start_payload, status = start_transcription_service(jwt_token, session_id)
    if status != 200 or not start_payload.get("success"):
        return jsonify(start_payload), status
    recording_id = start_payload["recording_id"]

    uploaded_file = request.files.get("audio")
    if not uploaded_file or not uploaded_file.filename.lower().endswith(".mp3"):
        return jsonify({"error": True, "message": "No valid MP3 file provided"}), 400

    upload_payload, upload_status = upload_audio_service(
        jwt_token, session_id, recording_id, uploaded_file
    )
    if upload_status != 200 or not upload_payload.get("success"):
        return jsonify(upload_payload), upload_status

    finish_payload, finish_status = finish_transcription_service(
        jwt_token, session_id, recording_id
    )
    if finish_status != 200 or not finish_payload.get("success"):
        return jsonify(finish_payload), finish_status

    templates = get_consult_note_templates(jwt_token)
    if (
        not templates
        or "templates" not in templates
        or len(templates["templates"]) == 0
    ):
        return jsonify({"error": True, "message": "No consult templates found"}), 404

    template_id = templates["templates"][0]["id"]

    note = generate_consult_note(
        jwt_token, session_id, template_id, voice_style="BRIEF", brain="LEFT"
    )
    return jsonify({"note": note})

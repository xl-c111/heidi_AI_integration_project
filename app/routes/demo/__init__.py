import logging
import os
import traceback

from flask import Blueprint, jsonify, render_template, request

from app.services.demo_flows import (
    ask_question_flow,
    audio_transcription_test,
    build_debug_report,
    complete_flow_test,
    get_jwt_overview,
    get_session_overview,
    process_document_flow,
    transcribe_audio_flow,
)

demo_bp = Blueprint("demo", __name__)
logger = logging.getLogger(__name__)


def _dispatch(service_fn, *args, **kwargs):
    try:
        payload, status = service_fn(*args, **kwargs)
        return jsonify(payload), status
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Demo service execution failed")
        return (
            jsonify(
                {
                    "error": f"Server error: {str(exc)}",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@demo_bp.route("/demo")
def demo_home():
    """Serve the demo HTML page."""
    try:
        return render_template("demo.html")
    except Exception as exc:  # pragma: no cover - template failure path
        return f"""
        <h1>Template Error: {str(exc)}</h1>
        <p>Make sure you have templates/demo.html file</p>
        <p>Current working directory: {os.getcwd()}</p>
        <p>Try these working endpoints:</p>
        <ul>
            <li><a href="/test-jwt">Test JWT</a></li>
            <li><a href="/test-session">Test Session</a></li>
            <li><a href="/debug-api">Debug API</a></li>
        </ul>
        """


@demo_bp.route("/transcribe-audio", methods=["POST"])
def transcribe_audio():
    """Handle audio file upload and transcription."""
    return _dispatch(
        transcribe_audio_flow,
        request.files.get("audio_file"),
        request.form.get("session_id"),
    )


@demo_bp.route("/debug-api")
def debug_api():
    """Comprehensive API debugging endpoint."""
    return _dispatch(build_debug_report)


@demo_bp.route("/test-jwt")
def test_jwt():
    """Enhanced JWT test endpoint."""
    return _dispatch(get_jwt_overview)


@demo_bp.route("/test-session")
def test_session():
    """Enhanced session test endpoint."""
    return _dispatch(get_session_overview)


@demo_bp.route("/process-document", methods=["POST"])
def process_document():
    """Generate a care plan from uploaded document text."""
    if request.is_json and request.json is not None:
        document_text = request.json.get("document_text", "")
    else:
        document_text = request.form.get("document_text", "")
    return _dispatch(process_document_flow, document_text)


@demo_bp.route("/ask-question", methods=["POST"])
def ask_question():
    """Enhanced question answering with comprehensive error handling."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    return _dispatch(ask_question_flow, data.get("question", ""), data.get("session_id"))


@demo_bp.route("/test-complete-flow", methods=["POST"])
def test_complete_flow():
    """Test the complete flow from JWT to AI response."""
    return _dispatch(complete_flow_test)


@demo_bp.route("/test-audio-transcription", methods=["POST"])
def test_audio_transcription():
    """Test audio transcription with a sample file."""
    sample_path = "static/Going_Down_Stairs.mp3"
    return _dispatch(audio_transcription_test, sample_path)

from flask import Blueprint, request, jsonify
from app.api.auth import get_jwt_token
from app.api.ask_heidi import ask_ai_stream

ask_heidi_bp = Blueprint('ask_heidi', __name__)


@ask_heidi_bp.route('/ask_heidi', methods=['POST'])
def ask_heidi():
    jwt_token = get_jwt_token()
    if not jwt_token:
        return jsonify({"error": "Unauthorized"}), 401

    session_id = request.json.get('session_id')
    ai_command_text = request.json.get('ai_command_text')
    content = request.json.get('content')
    content_type = request.json.get('content_type')

    if not session_id or not ai_command_text or not content or not content_type:
        return jsonify({"error": "Missing required parameters"}), 400

    response = ask_ai_stream(jwt_token, session_id,
                             ai_command_text, content, content_type)

    if response.get("error"):
        return jsonify(response), response.get("status_code", 500)

    return jsonify(response)

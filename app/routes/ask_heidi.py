# app/routes/ask_heidi.py - Fixed blueprint and imports
from flask import Blueprint, request, jsonify
from app.api.auth import get_jwt_token
from app.api.ask_heidi import ask_ai_stream, test_ask_ai_with_fallbacks
import traceback

# Create the blueprint
ask_heidi_bp = Blueprint('ask_heidi', __name__)

@ask_heidi_bp.route('/ask_heidi', methods=['POST'])
def ask_heidi():
    """Original ask_heidi endpoint"""
    try:
        jwt_token = get_jwt_token()
        if not jwt_token or 'Error' in str(jwt_token):
            return jsonify({"error": "Unauthorized", "details": str(jwt_token)}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        session_id = data.get('session_id')
        ai_command_text = data.get('ai_command_text')
        content = data.get('content')
        content_type = data.get('content_type', 'MARKDOWN')

        if not session_id or not ai_command_text or not content:
            return jsonify({"error": "Missing required parameters: session_id, ai_command_text, content"}), 400

        response = ask_ai_stream(jwt_token, session_id, ai_command_text, content, content_type)

        if response.get("error"):
            return jsonify(response), response.get("status_code", 500)

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500

@ask_heidi_bp.route('/ask_heidi_enhanced', methods=['POST'])
def ask_heidi_enhanced():
    """Enhanced ask_heidi endpoint with fallbacks"""
    try:
        jwt_token = get_jwt_token()
        if not jwt_token or 'Error' in str(jwt_token):
            return jsonify({"error": "Unauthorized", "details": str(jwt_token)}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        session_id = data.get('session_id')
        ai_command_text = data.get('ai_command_text')
        content = data.get('content')

        if not session_id or not ai_command_text or not content:
            return jsonify({"error": "Missing required parameters: session_id, ai_command_text, content"}), 400

        # Use the enhanced version with fallbacks
        response = test_ask_ai_with_fallbacks(jwt_token, session_id, ai_command_text, content)

        if response.get("error"):
            return jsonify(response), response.get("status_code", 500)

        return jsonify(response)

    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500
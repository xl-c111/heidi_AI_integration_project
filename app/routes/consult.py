from flask import Blueprint, jsonify, request
from app.api.auth import get_jwt_token
from app.api.consult import get_consult_note_templates, generate_consult_note, create_session

consult_bp = Blueprint('consult', __name__)

@consult_bp.route('/consult/templates', methods=['GET'])
def templates():
    jwt = get_jwt_token()
    print(jwt)
    result = get_consult_note_templates(jwt)
    return jsonify(result)

@consult_bp.route('/consult/generate', methods=['POST'])
def generate():
    jwt = get_jwt_token()
    data = request.get_json()
    session_id = data.get('session_id')
    template_id = data.get('template_id')
    voice = data.get('voice_style', 'GOLDILOCKS')
    brain = data.get('brain', 'LEFT')
    addition = data.get('addition', '')

    if not session_id or not template_id:
        return jsonify({"error": "session_id and template_id are required"}), 400

    result = generate_consult_note(jwt, session_id, template_id, voice, brain, addition)
    return jsonify(result)


# routes/consult.py

@consult_bp.route('/consult/session', methods=['POST'])
def start_session():
    jwt = get_jwt_token()
    session_id = create_session(jwt)
    
    if isinstance(session_id, str):
        return jsonify({"session_id": session_id})
    else:
        return jsonify(session_id), 400


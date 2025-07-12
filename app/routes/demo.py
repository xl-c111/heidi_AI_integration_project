# app/routes/demo.py - Single route that does everything for the demo
from flask import Blueprint, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import base64
from app.api.auth import get_jwt_token
from app.api.ask_heidi import ask_ai_stream
from app.api.session import create_session

demo_bp = Blueprint('demo', __name__)

# Simple HTML template for the demo
DEMO_TEMPLATE = open('demo.html', 'r').read()  # Your HTML from above

@demo_bp.route('/')
def demo_home():
    return DEMO_TEMPLATE

@demo_bp.route('/process-document', methods=['POST'])
def process_document():
    """Super simple route - take text input and generate care plan"""

    # For hackathon speed, just take manual text input instead of OCR
    document_text = request.form.get('document_text') or request.json.get('document_text', '')

    if not document_text:
        return jsonify({'error': 'No document text provided'}), 400

    try:
        # Get JWT and create session
        jwt_token = get_jwt_token()
        if not jwt_token or 'Error' in str(jwt_token):
            return jsonify({'error': 'Authentication failed'}), 401

        session_id = create_session(jwt_token)
        if isinstance(session_id, dict) and session_id.get("error"):
            return jsonify({'error': 'Session creation failed', 'details': session_id}), 500

        # Create care plan prompt
        care_plan_prompt = """
        You are a medical care assistant. Based on the following discharge document, create a structured post-surgery care plan.

        Format your response as a JSON object with these sections:
        - medications: array of {name, dosage, frequency, instructions}
        - activities: array of {activity, frequency, restrictions}
        - wound_care: array of care instructions
        - warning_signs: array of symptoms to watch for
        - appointments: array of {type, timing}

        Document content:
        """ + document_text

        # Get AI response
        ai_response = ask_ai_stream(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text=care_plan_prompt,
            content=document_text,
            content_type="text"
        )

        return jsonify({
            'success': True,
            'care_plan': ai_response,
            'session_id': session_id,
            'extracted_text': document_text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/ask-question', methods=['POST'])
def ask_question():
    """Simple text-based question answering"""

    question = request.json.get('question', '')
    session_id = request.json.get('session_id')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    try:
        jwt_token = get_jwt_token()

        if not session_id:
            session_id = create_session(jwt_token)

        medical_prompt = f"""
        You are a helpful post-surgery care assistant. Answer this patient question with:
        1. Supportive, reassuring tone
        2. Practical advice
        3. When to contact healthcare provider
        4. Keep it concise but helpful

        Patient question: {question}
        """

        ai_response = ask_ai_stream(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text=medical_prompt,
            content=question,
            content_type="text"
        )

        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
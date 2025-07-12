# app/routes/demo.py - With Debug and Fixed Paths
from flask import Blueprint, request, jsonify, render_template
import os
from app.api.auth import get_jwt_token
from app.api.ask_heidi import ask_ai_stream
from app.api.session import create_session

demo_bp = Blueprint('demo', __name__)

@demo_bp.route('/demo')
def demo_home():
    """Serve the demo HTML"""
    try:
        return render_template('demo.html')
    except Exception as e:
        return f"""
        <h1>Template Error: {str(e)}</h1>
        <p>Make sure you have templates/demo.html file</p>
        <p>Current working directory: {os.getcwd()}</p>
        <p>Try these working endpoints:</p>
        <ul>
            <li><a href="/test-jwt">Test JWT</a></li>
            <li><a href="/test-session">Test Session</a></li>
        </ul>
        """

@demo_bp.route('/test-jwt')
def test_jwt():
    """Quick JWT test endpoint"""
    jwt_token = get_jwt_token()
    return jsonify({
        'jwt_token': jwt_token,
        'has_error': 'Error' in str(jwt_token),
        'env_check': {
            'api_key_set': bool(os.getenv("HEIDI_API_KEY")),
            'email_set': bool(os.getenv("HEIDI_EMAIL")),
            'user_id_set': bool(os.getenv("HEIDI_USER_ID"))
        }
    })

@demo_bp.route('/test-session')
def test_session():
    """Quick session test endpoint"""
    jwt_token = get_jwt_token()
    if 'Error' in str(jwt_token):
        return jsonify({'error': 'JWT failed', 'details': jwt_token})

    session_id = create_session(jwt_token)
    return jsonify({
        'jwt_token': jwt_token[:20] + '...' if isinstance(jwt_token, str) else jwt_token,
        'session_result': session_id
    })

@demo_bp.route('/process-document', methods=['POST'])
def process_document():
    """Process document and generate care plan"""
    print("=== PROCESS DOCUMENT CALLED ===")

    # Get document text from request
    if request.is_json and request.json is not None:
        document_text = request.json.get('document_text', '')
    else:
        document_text = request.form.get('document_text', '')

    print(f"Document text received: {document_text[:100]}...")

    if not document_text:
        return jsonify({'error': 'No document text provided'}), 400

    try:
        # Step 1: Get JWT
        print("Getting JWT token...")
        jwt_token = get_jwt_token()
        print(f"JWT result: {str(jwt_token)[:50]}...")

        if not jwt_token or 'Error' in str(jwt_token):
            return jsonify({'error': 'Authentication failed', 'details': str(jwt_token)}), 401

        # Step 2: Create session
        print("Creating session...")
        session_id = create_session(jwt_token)
        print(f"Session result: {session_id}")

        if isinstance(session_id, dict) and session_id.get("error"):
            return jsonify({'error': 'Session creation failed', 'details': session_id}), 500

        # Step 3: Create care plan prompt
        care_plan_prompt = f"""
        You are a medical care assistant. Based on the following discharge document, create a structured post-surgery care plan.

        Please provide a helpful care plan with:
        1. Medication schedule and instructions
        2. Activity guidelines and restrictions
        3. Wound care instructions
        4. Warning signs to watch for
        5. Follow-up appointment reminders

        Make it clear, practical, and reassuring for a patient recovering at home.

        Document content: {document_text}
        """

        # Step 4: Get AI response
        print("Calling Ask AI...")
        ai_response = ask_ai_stream(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text=care_plan_prompt,
            content=document_text,
            content_type="text"
        )

        print(f"AI response: {str(ai_response)[:200]}...")

        if ai_response.get("error"):
            return jsonify({'error': 'AI request failed', 'details': ai_response}), 500

        return jsonify({
            'success': True,
            'care_plan': ai_response,
            'session_id': session_id,
            'extracted_text': document_text
        })

    except Exception as e:
        print(f"Exception in process_document: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@demo_bp.route('/ask-question', methods=['POST'])
def ask_question():
    """Simple text-based question answering"""
    print("=== ASK QUESTION CALLED ===")

    data = request.get_json()
    question = data.get('question', '')
    session_id = data.get('session_id')

    print(f"Question: {question}")
    print(f"Session ID: {session_id}")

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    try:
        jwt_token = get_jwt_token()

        if not session_id:
            session_id = create_session(jwt_token)
            print(f"Created new session: {session_id}")

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
            content_type="MARKDOWN"  # Fixed!
        )

        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id
        })

    except Exception as e:
        print(f"Exception in ask_question: {str(e)}")
        return jsonify({'error': str(e)}), 500

@demo_bp.route('/test-audio-demo', methods=['POST'])
def test_audio_demo():
    """Test voice processing using a static audio file"""
    print("=== TEST AUDIO DEMO CALLED ===")

    try:
        # Get JWT and session
        jwt_token = get_jwt_token()
        if 'Error' in str(jwt_token):
            return jsonify({'error': 'Authentication failed'}), 401

        # Get or create session
        session_id = request.json.get('session_id') if request.is_json else None
        if not session_id:
            session_id = create_session(jwt_token)
            if isinstance(session_id, dict) and session_id.get("error"):
                return jsonify({'error': 'Session creation failed'}), 500

        # Use the static test audio file
        audio_file_path = "static/Do_I_need_more_Panamax.mp3"

        # Check if file exists
        if not os.path.exists(audio_file_path):
            return jsonify({'error': f'Test audio file not found: {audio_file_path}'}), 400

        print(f"Using test audio file: {audio_file_path}")
        print(f"File size: {os.path.getsize(audio_file_path)} bytes")

        try:
            # Use Heidi's transcription workflow
            from app.api.transcript import start_transcription, upload_audio, finish_transcription, get_transcript

            print("Starting transcription...")
            recording_id = start_transcription(jwt_token, session_id)
            if isinstance(recording_id, dict) and recording_id.get("error"):
                return jsonify({'error': 'Transcription start failed', 'details': recording_id}), 500

            print(f"Recording ID: {recording_id}")

            # Upload audio for transcription
            print("Uploading test audio...")
            upload_result = upload_audio(jwt_token, session_id, recording_id, audio_file_path)
            print(f"Upload result: {upload_result}")

            if not upload_result.get("is_success", False):
                return jsonify({'error': 'Audio upload failed', 'details': upload_result}), 500

            # Add delay for processing
            import time
            time.sleep(3)

            # Finish transcription
            print("Finishing transcription...")
            finish_result = finish_transcription(jwt_token, session_id, recording_id)
            print(f"Finish result: {finish_result}")

            # Don't fail if finish returns false - continue anyway
            if not finish_result.get("is_success", False):
                print("Finish transcription returned false, but continuing...")

            # Add another delay
            time.sleep(5)

            # Get the transcript
            print("Getting transcript...")
            transcript_result = get_transcript(jwt_token, session_id)
            print(f"Transcript result: {transcript_result}")

            if isinstance(transcript_result, dict) and transcript_result.get("error"):
                return jsonify({'error': 'Getting transcript failed', 'details': transcript_result}), 500

            patient_question = transcript_result.get("transcript", "")
            if not patient_question:
                # Use a fallback question for demo
                patient_question = "Do I need more pain medication?"
                print("No transcript found, using fallback question")

            print(f"Transcribed question: {patient_question}")

            # Create AI prompt for medical Q&A
            medical_prompt = f"""
            You are a helpful post-surgery care assistant. Answer this patient question with:
            1. Supportive, reassuring tone
            2. Practical advice
            3. When to contact healthcare provider
            4. Keep it concise but helpful

            Patient question: {patient_question}
            """

            # Get AI response using ask_ai_stream
            print("Getting AI response...")
            ai_response = ask_ai_stream(
                jwt_token=jwt_token,
                session_id=session_id,
                ai_command_text=medical_prompt,
                content=patient_question,
                content_type="MARKDOWN"
            )

            print(f"AI response: {str(ai_response)[:200]}...")

            if ai_response.get("error"):
                return jsonify({'error': 'AI request failed', 'details': ai_response}), 500

            return jsonify({
                'success': True,
                'patient_question': patient_question,
                'response': ai_response,
                'session_id': session_id,
                'test_file_used': audio_file_path
            })

        except Exception as e:
            print(f"Error in transcription workflow: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Transcription error: {str(e)}'}), 500

    except Exception as e:
        print(f"Exception in test_audio_demo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


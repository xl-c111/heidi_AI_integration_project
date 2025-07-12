# app/routes/demo.py - ENHANCED with better error handling and debugging
from flask import Blueprint, request, jsonify, render_template
import os
import traceback
from app.api.auth import get_jwt_token
from app.api.ask_heidi import ask_ai_stream, test_ask_ai_with_fallbacks
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
            <li><a href="/debug-api">Debug API</a></li>
        </ul>
        """

@demo_bp.route('/debug-api')
def debug_api():
    """Comprehensive API debugging endpoint"""
    try:
        debug_info = {
            "environment_check": {},
            "jwt_test": {},
            "session_test": {},
            "ask_ai_test": {}
        }

        # Check environment variables
        env_vars = ["HEIDI_API_KEY", "HEIDI_EMAIL", "HEIDI_USER_ID"]
        for var in env_vars:
            value = os.getenv(var)
            debug_info["environment_check"][var] = {
                "set": bool(value),
                "length": len(value) if value else 0,
                "preview": f"{value[:10]}..." if value and len(value) > 10 else value
            }

        # Test JWT
        jwt_token = get_jwt_token()
        debug_info["jwt_test"] = {
            "success": not ('Error' in str(jwt_token)),
            "token_preview": str(jwt_token)[:30] + "..." if isinstance(jwt_token, str) and len(jwt_token) > 30 else str(jwt_token),
            "token_type": type(jwt_token).__name__
        }

        if debug_info["jwt_test"]["success"]:
            # Test session creation
            session_id = create_session(jwt_token)
            debug_info["session_test"] = {
                "success": isinstance(session_id, str) and not session_id.get("error", False),
                "session_id": session_id if isinstance(session_id, str) else str(session_id),
                "session_type": type(session_id).__name__
            }

            if debug_info["session_test"]["success"]:
                # Test Ask AI
                ai_response = ask_ai_stream(
                    jwt_token=jwt_token,
                    session_id=session_id,
                    ai_command_text="Say hello in one sentence",
                    content="Test content",
                    content_type="MARKDOWN"
                )

                debug_info["ask_ai_test"] = {
                    "success": ai_response.get("success", False),
                    "response_preview": str(ai_response)[:200] + "..." if len(str(ai_response)) > 200 else str(ai_response),
                    "error": ai_response.get("error", False),
                    "format": ai_response.get("format", "unknown")
                }

        return jsonify({
            "status": "debug_complete",
            "timestamp": str(os.times()),
            "debug_info": debug_info
        })

    except Exception as e:
        return jsonify({
            "error": "Debug failed",
            "exception": str(e),
            "traceback": traceback.format_exc()
        }), 500

@demo_bp.route('/test-jwt')
def test_jwt():
    """Enhanced JWT test endpoint"""
    try:
        jwt_token = get_jwt_token()
        return jsonify({
            'success': not ('Error' in str(jwt_token)),
            'jwt_token': str(jwt_token)[:50] + "..." if len(str(jwt_token)) > 50 else str(jwt_token),
            'token_type': type(jwt_token).__name__,
            'env_check': {
                'api_key_set': bool(os.getenv("HEIDI_API_KEY")),
                'email_set': bool(os.getenv("HEIDI_EMAIL")),
                'user_id_set': bool(os.getenv("HEIDI_USER_ID"))
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@demo_bp.route('/test-session')
def test_session():
    """Enhanced session test endpoint"""
    try:
        jwt_token = get_jwt_token()
        if 'Error' in str(jwt_token):
            return jsonify({'error': 'JWT failed', 'details': jwt_token}), 401

        session_id = create_session(jwt_token)
        return jsonify({
            'success': isinstance(session_id, str),
            'jwt_token': str(jwt_token)[:20] + '...' if isinstance(jwt_token, str) else str(jwt_token),
            'session_result': session_id,
            'session_type': type(session_id).__name__
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@demo_bp.route('/process-document', methods=['POST'])
def process_document():
    """Enhanced document processing with comprehensive error handling"""
    print("=== PROCESS DOCUMENT CALLED ===")

    try:
        # Get document text from request
        if request.is_json and request.json is not None:
            document_text = request.json.get('document_text', '')
        else:
            document_text = request.form.get('document_text', '')

        print(f"Document text received: {len(document_text)} characters")
        print(f"First 100 chars: {document_text[:100]}")

        if not document_text or len(document_text.strip()) < 10:
            return jsonify({
                'error': 'Document text is too short or empty',
                'received_length': len(document_text),
                'minimum_required': 10
            }), 400

        # Step 1: Get JWT with error handling
        print("Getting JWT token...")
        jwt_token = get_jwt_token()
        print(f"JWT result type: {type(jwt_token)}")
        print(f"JWT result: {str(jwt_token)[:100]}...")

        if not jwt_token or 'Error' in str(jwt_token):
            return jsonify({
                'error': 'Authentication failed',
                'details': str(jwt_token),
                'suggestion': 'Check your API credentials in .env file'
            }), 401

        # Step 2: Create session with error handling
        print("Creating session...")
        session_id = create_session(jwt_token)
        print(f"Session result type: {type(session_id)}")
        print(f"Session result: {session_id}")

        if isinstance(session_id, dict) and session_id.get("error"):
            return jsonify({
                'error': 'Session creation failed',
                'details': session_id,
                'suggestion': 'JWT token may be expired or invalid'
            }), 500

        if not isinstance(session_id, str):
            return jsonify({
                'error': 'Invalid session ID format',
                'received_type': type(session_id).__name__,
                'received_value': str(session_id)
            }), 500

        # Step 3: Create enhanced care plan prompt
        care_plan_prompt = """
        You are a medical care assistant. Based on the following discharge document, create a structured post-surgery care plan.

        Please provide a helpful care plan with these sections:
        1. **Medication Schedule**: List medications with dosage, frequency, and special instructions
        2. **Activity Guidelines**: What activities are allowed/restricted and when
        3. **Wound Care**: How to care for surgical sites and dressings
        4. **Warning Signs**: Symptoms that require immediate medical attention
        5. **Follow-up Care**: Appointment reminders and next steps

        Make it clear, practical, and reassuring for a patient recovering at home.
        Use bullet points and clear headings for easy reading.
        """

        # Step 4: Get AI response with fallback content types
        print("Calling Ask AI with fallbacks...")
        ai_response = test_ask_ai_with_fallbacks(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text=care_plan_prompt,
            content=document_text
        )

        print(f"AI response success: {ai_response.get('success', False)}")
        print(f"AI response keys: {list(ai_response.keys())}")

        if ai_response.get("error"):
            return jsonify({
                'error': 'AI request failed',
                'details': ai_response,
                'suggestion': 'Try again or check if session is still valid'
            }), 500

        # Extract response content
        response_content = ai_response.get('response', '')
        if isinstance(response_content, dict):
            # If response is a dict, try to extract content
            response_content = (
                response_content.get('content') or
                response_content.get('text') or
                response_content.get('data') or
                str(response_content)
            )

        return jsonify({
            'success': True,
            'care_plan': response_content,
            'session_id': session_id,
            'extracted_text': document_text,
            'response_format': ai_response.get('format', 'unknown'),
            'response_length': len(str(response_content))
        })

    except Exception as e:
        print(f"Exception in process_document: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'exception_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500

@demo_bp.route('/ask-question', methods=['POST'])
def ask_question():
    """Enhanced question answering with comprehensive error handling"""
    print("=== ASK QUESTION CALLED ===")

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        question = data.get('question', '').strip()
        session_id = data.get('session_id')

        print(f"Question: {question}")
        print(f"Session ID: {session_id}")

        if not question or len(question) < 3:
            return jsonify({
                'error': 'Question is too short or empty',
                'received_length': len(question),
                'minimum_required': 3
            }), 400

        # Get JWT token
        jwt_token = get_jwt_token()
        if not jwt_token or 'Error' in str(jwt_token):
            return jsonify({
                'error': 'Authentication failed',
                'details': str(jwt_token)
            }), 401

        # Create new session if none provided
        if not session_id:
            session_id = create_session(jwt_token)
            print(f"Created new session: {session_id}")

            if isinstance(session_id, dict) and session_id.get("error"):
                return jsonify({
                    'error': 'Session creation failed',
                    'details': session_id
                }), 500

        # Enhanced medical prompt
        medical_prompt = f"""
        You are a helpful post-surgery care assistant. Answer this patient question with:

        1. A supportive, reassuring tone
        2. Practical, actionable advice
        3. Clear guidance on when to contact healthcare provider
        4. Keep response concise but comprehensive
        5. Use bullet points for clarity when appropriate

        Patient question: {question}

        Provide a helpful response that addresses their concern while emphasizing safety.
        """

        # Get AI response with fallbacks
        ai_response = test_ask_ai_with_fallbacks(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text=medical_prompt,
            content=question
        )

        if ai_response.get("error"):
            return jsonify({
                'error': 'Failed to get AI response',
                'details': ai_response
            }), 500

        # Extract response content
        response_content = ai_response.get('response', '')
        if isinstance(response_content, dict):
            response_content = (
                response_content.get('content') or
                response_content.get('text') or
                response_content.get('data') or
                str(response_content)
            )

        return jsonify({
            'success': True,
            'response': response_content,
            'session_id': session_id,
            'question_received': question,
            'response_format': ai_response.get('format', 'unknown')
        })

    except Exception as e:
        print(f"Exception in ask_question: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'exception_type': type(e).__name__
        }), 500

@demo_bp.route('/test-complete-flow', methods=['POST'])
def test_complete_flow():
    """Test the complete flow from JWT to AI response"""
    print("=== TESTING COMPLETE FLOW ===")

    try:
        # Test data
        test_document = """
        Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food.
        Take Amoxicillin 500mg three times daily for 7 days. Short walks recommended every 2 hours.
        No lifting over 10 pounds for 2 weeks. Follow-up appointment in 1 week.
        Watch for fever over 101°F, redness, or unusual swelling around incision site.
        """

        test_question = "How much pain is normal after knee surgery?"

        flow_results = {
            "step1_jwt": {},
            "step2_session": {},
            "step3_care_plan": {},
            "step4_question": {}
        }

        # Step 1: JWT
        jwt_token = get_jwt_token()
        flow_results["step1_jwt"] = {
            "success": not ('Error' in str(jwt_token)),
            "token_preview": str(jwt_token)[:30] + "..." if isinstance(jwt_token, str) else str(jwt_token)
        }

        if not flow_results["step1_jwt"]["success"]:
            return jsonify({"error": "JWT failed", "flow_results": flow_results}), 401

        # Step 2: Session
        session_id = create_session(jwt_token)
        flow_results["step2_session"] = {
            "success": isinstance(session_id, str),
            "session_id": session_id if isinstance(session_id, str) else str(session_id)
        }

        if not flow_results["step2_session"]["success"]:
            return jsonify({"error": "Session creation failed", "flow_results": flow_results}), 500

        # Step 3: Care plan generation
        care_plan_response = test_ask_ai_with_fallbacks(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text="Create a brief care plan for this patient",
            content=test_document
        )

        flow_results["step3_care_plan"] = {
            "success": care_plan_response.get("success", False),
            "response_preview": str(care_plan_response.get("response", ""))[:100] + "..." if care_plan_response.get("response") else "No response",
            "format": care_plan_response.get("format", "unknown")
        }

        # Step 4: Question answering
        qa_response = test_ask_ai_with_fallbacks(
            jwt_token=jwt_token,
            session_id=session_id,
            ai_command_text="Answer this patient question helpfully",
            content=test_question
        )

        flow_results["step4_question"] = {
            "success": qa_response.get("success", False),
            "response_preview": str(qa_response.get("response", ""))[:100] + "..." if qa_response.get("response") else "No response",
            "format": qa_response.get("format", "unknown")
        }

        overall_success = all([
            flow_results["step1_jwt"]["success"],
            flow_results["step2_session"]["success"],
            flow_results["step3_care_plan"]["success"],
            flow_results["step4_question"]["success"]
        ])

        return jsonify({
            "overall_success": overall_success,
            "flow_results": flow_results,
            "message": "Complete flow test finished",
            "next_steps": "Check individual step results for any failures"
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
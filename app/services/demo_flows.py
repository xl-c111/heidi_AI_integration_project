import logging
import os
from typing import Any, Dict, Optional, Tuple

from werkzeug.datastructures import FileStorage

from app.api.ask_heidi import ask_ai_stream, ask_ai_with_fallbacks
from app.api.auth import get_jwt_token
from app.services.common import ensure_session, fetch_jwt_token
from app.services.transcription import (
    finish_transcription_service,
    start_transcription_service,
    transcript_lookup_service,
    upload_audio_from_path_service,
    upload_audio_service,
)

logger = logging.getLogger(__name__)

JsonResponse = Tuple[Dict[str, Any], int]


def _extract_transcript_text(transcript_result: Any) -> str:
    if isinstance(transcript_result, dict):
        for key in ("transcript", "text", "content", "speech_to_text"):
            value = transcript_result.get(key)
            if value:
                return str(value)
        return str(transcript_result)
    return str(transcript_result)


def _extract_ai_content(response_content: Any) -> str:
    if isinstance(response_content, dict):
        for key in ("content", "text", "data"):
            value = response_content.get(key)
            if value:
                return str(value)
        return str(response_content)
    return str(response_content)


def transcribe_audio_flow(audio_file: Optional[FileStorage], session_id: Optional[str]) -> JsonResponse:
    if not audio_file:
        return {"success": False, "error": "No audio file provided"}, 400
    if not audio_file.filename:
        return {"success": False, "error": "No audio file selected"}, 400

    jwt_token, error = fetch_jwt_token()
    if error:
        return error

    session_id_value, error = ensure_session(jwt_token, session_id)
    if error:
        return error

    start_payload, status = start_transcription_service(jwt_token, session_id_value)
    if status != 200 or not start_payload.get("success"):
        return start_payload, status
    recording_id = start_payload["recording_id"]

    upload_payload, status = upload_audio_service(
        jwt_token, session_id_value, recording_id, audio_file
    )
    if status != 200 or not upload_payload.get("success"):
        return upload_payload, status

    finish_payload, status = finish_transcription_service(jwt_token, session_id_value, recording_id)
    if status != 200 or not finish_payload.get("success"):
        return finish_payload, status

    transcript_payload, status = transcript_lookup_service(jwt_token, session_id_value)
    if status != 200 or not transcript_payload.get("success"):
        return transcript_payload, status

    transcript_text = _extract_transcript_text(transcript_payload.get("transcript")).strip()
    if not transcript_text or transcript_text == "{}":
        return (
            {
                "success": False,
                "error": "No speech detected in audio file",
                "suggestion": "Please try recording again with clearer speech",
            },
            400,
        )

    return (
        {
            "success": True,
            "transcript": transcript_text,
            "session_id": session_id_value,
            "recording_id": recording_id,
        },
        200,
    )


def build_debug_report() -> JsonResponse:
    debug_info: Dict[str, Any] = {
        "environment_check": {},
        "jwt_test": {},
        "session_test": {},
        "ask_ai_test": {},
    }

    for var in ("HEIDI_API_KEY", "HEIDI_EMAIL", "HEIDI_USER_ID"):
        value = os.getenv(var)
        debug_info["environment_check"][var] = {
            "set": bool(value),
            "length": len(value) if value else 0,
            "preview": f"{value[:10]}..." if value and len(value) > 10 else value,
        }

    jwt_token = get_jwt_token()
    jwt_success = not ("Error" in str(jwt_token))
    debug_info["jwt_test"] = {
        "success": jwt_success,
        "token_preview": str(jwt_token)[:30] + "..." if isinstance(jwt_token, str) and len(str(jwt_token)) > 30 else str(jwt_token),
        "token_type": type(jwt_token).__name__,
    }

    if jwt_success:
        session_id, session_error = ensure_session(jwt_token, None)
        if session_error:
            payload, status = session_error
            debug_info["session_test"] = {
                "success": False,
                "status": status,
                "details": payload,
            }
        else:
            debug_info["session_test"] = {
                "success": True,
                "session_id": session_id,
                "session_type": type(session_id).__name__,
            }

            ai_response = ask_ai_stream(
                jwt_token=jwt_token,
                session_id=session_id,  # type: ignore[arg-type]
                ai_command_text="Say hello in one sentence",
                content="Test content",
                content_type="MARKDOWN",
            )
            debug_info["ask_ai_test"] = {
                "success": ai_response.get("success", False),
                "response_preview": str(ai_response)[:200] + "..." if len(str(ai_response)) > 200 else str(ai_response),
                "error": ai_response.get("error", False),
                "format": ai_response.get("format", "unknown"),
            }

    return (
        {
            "status": "debug_complete",
            "timestamp": str(os.times()),
            "debug_info": debug_info,
        },
        200,
    )


def get_jwt_overview() -> JsonResponse:
    jwt_token = get_jwt_token()
    return (
        {
            "success": not ("Error" in str(jwt_token)),
            "jwt_token": str(jwt_token)[:50] + "..." if len(str(jwt_token)) > 50 else str(jwt_token),
            "token_type": type(jwt_token).__name__,
            "env_check": {
                "api_key_set": bool(os.getenv("HEIDI_API_KEY")),
                "email_set": bool(os.getenv("HEIDI_EMAIL")),
                "user_id_set": bool(os.getenv("HEIDI_USER_ID")),
            },
        },
        200,
    )


def get_session_overview() -> JsonResponse:
    jwt_token, error = fetch_jwt_token()
    if error:
        return error

    session_id, session_error = ensure_session(jwt_token, None)
    if session_error:
        return session_error

    return (
        {
            "success": True,
            "jwt_token": str(jwt_token)[:20] + "..." if isinstance(jwt_token, str) else str(jwt_token),
            "session_result": session_id,
            "session_type": type(session_id).__name__,
        },
        200,
    )


CARE_PLAN_PROMPT = """
You are a medical care assistant. Based on the following discharge document, create a structured post-surgery care plan.

Please provide a helpful care plan with these sections:
1. Medication Schedule: List medications with dosage, frequency, and special instructions
2. Activity Guidelines: What activities are allowed/restricted and when
3. Wound Care: How to care for surgical sites and dressings
4. Warning Signs: Symptoms that require immediate medical attention
5. Follow-up Care: Appointment reminders and next steps

Make it clear, practical, and reassuring for a patient recovering at home.
Use bullet points and clear headings for easy reading.
""".strip()


def process_document_flow(document_text: str) -> JsonResponse:
    if not document_text or len(document_text.strip()) < 10:
        return (
            {
                "error": "Document text is too short or empty",
                "received_length": len(document_text),
                "minimum_required": 10,
            },
            400,
        )

    jwt_token, error = fetch_jwt_token()
    if error:
        return error

    session_id, error = ensure_session(jwt_token, None)
    if error:
        return error

    ai_response = ask_ai_with_fallbacks(
        jwt_token=jwt_token,  # type: ignore[arg-type]
        session_id=session_id,  # type: ignore[arg-type]
        ai_command_text=CARE_PLAN_PROMPT,
        content=document_text,
    )

    if ai_response.get("error"):
        return (
            {
                "error": "AI request failed",
                "details": ai_response,
                "suggestion": "Try again or check if session is still valid",
            },
            500,
        )

    response_content = _extract_ai_content(ai_response.get("response", ""))
    return (
        {
            "success": True,
            "care_plan": response_content,
            "session_id": session_id,
            "extracted_text": document_text,
            "response_format": ai_response.get("format", "unknown"),
            "response_length": len(str(response_content)),
        },
        200,
    )


def ask_question_flow(question: str, session_id: Optional[str]) -> JsonResponse:
    cleaned_question = question.strip()
    if not cleaned_question:
        return {"error": "Question cannot be empty"}, 400

    jwt_token, error = fetch_jwt_token()
    if error:
        return error

    session_id_value, error = ensure_session(jwt_token, session_id)
    if error:
        return error

    prompt = f"""
You are a helpful post-surgery care assistant. Answer this patient question with:

1. A supportive, reassuring tone
2. Practical, actionable advice
3. Clear guidance on when to contact healthcare provider
4. Keep response concise but comprehensive
5. Use bullet points for clarity when appropriate

Patient question: {cleaned_question}

Provide a helpful response that addresses their concern while emphasizing safety.
""".strip()

    ai_response = ask_ai_with_fallbacks(
        jwt_token=jwt_token,  # type: ignore[arg-type]
        session_id=session_id_value,  # type: ignore[arg-type]
        ai_command_text=prompt,
        content=cleaned_question,
    )

    if ai_response.get("error"):
        return (
            {
                "error": "Failed to get AI response",
                "details": ai_response,
            },
            500,
        )

    response_content = _extract_ai_content(ai_response.get("response", ""))
    return (
        {
            "success": True,
            "response": response_content,
            "session_id": session_id_value,
            "question_received": cleaned_question,
            "response_format": ai_response.get("format", "unknown"),
        },
        200,
    )


def complete_flow_test() -> JsonResponse:
    document_sample = (
        "Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food. "
        "Take Amoxicillin 500mg three times daily for 7 days. Short walks recommended every 2 hours. "
        "No lifting over 10 pounds for 2 weeks. Follow-up appointment in 1 week. "
        "Watch for fever over 101°F, redness, or unusual swelling around incision site."
    )
    question_sample = "How much pain is normal after knee surgery?"

    flow_results: Dict[str, Any] = {
        "step1_jwt": {},
        "step2_session": {},
        "step3_care_plan": {},
        "step4_question": {},
    }

    jwt_token = get_jwt_token()
    jwt_success = not ("Error" in str(jwt_token))
    flow_results["step1_jwt"] = {
        "success": jwt_success,
        "token_preview": str(jwt_token)[:30] + "..." if isinstance(jwt_token, str) else str(jwt_token),
    }
    if not jwt_success:
        return {"error": "JWT failed", "flow_results": flow_results}, 401

    session_id, session_error = ensure_session(jwt_token, None)
    session_success = session_error is None
    flow_results["step2_session"] = {
        "success": session_success,
        "session_id": session_id if session_success else None,
        "details": None if session_success else session_error[0],
    }
    if not session_success:
        return {"error": "Session creation failed", "flow_results": flow_results}, session_error[1]

    care_plan_response = ask_ai_with_fallbacks(
        jwt_token=jwt_token,  # type: ignore[arg-type]
        session_id=session_id,  # type: ignore[arg-type]
        ai_command_text="Create a brief care plan for this patient",
        content=document_sample,
    )
    flow_results["step3_care_plan"] = {
        "success": care_plan_response.get("success", False),
        "response_preview": str(care_plan_response.get("response", ""))[:100] + "..."
        if care_plan_response.get("response")
        else "No response",
        "format": care_plan_response.get("format", "unknown"),
    }

    qa_response = ask_ai_with_fallbacks(
        jwt_token=jwt_token,  # type: ignore[arg-type]
        session_id=session_id,  # type: ignore[arg-type]
        ai_command_text="Answer this patient question helpfully",
        content=question_sample,
    )
    flow_results["step4_question"] = {
        "success": qa_response.get("success", False),
        "response_preview": str(qa_response.get("response", ""))[:100] + "..."
        if qa_response.get("response")
        else "No response",
        "format": qa_response.get("format", "unknown"),
    }

    overall_success = all(
        (
            flow_results["step1_jwt"]["success"],
            flow_results["step2_session"]["success"],
            flow_results["step3_care_plan"]["success"],
            flow_results["step4_question"]["success"],
        )
    )

    return (
        {
            "overall_success": overall_success,
            "flow_results": flow_results,
            "message": "Complete flow test finished",
            "next_steps": "Check individual step results for any failures",
        },
        200,
    )


def audio_transcription_test(sample_path: str) -> JsonResponse:
    if not os.path.exists(sample_path):
        return (
            {
                "error": "Test audio file not found",
                "expected_path": sample_path,
                "suggestion": "Upload an audio file via the /transcribe-audio endpoint instead",
            },
            404,
        )

    jwt_token, error = fetch_jwt_token()
    if error:
        return error

    session_id, error = ensure_session(jwt_token, None)
    if error:
        return error

    start_payload, status = start_transcription_service(jwt_token, session_id)
    if status != 200 or not start_payload.get("success"):
        return start_payload, status
    recording_id = start_payload["recording_id"]

    upload_payload, status = upload_audio_from_path_service(
        jwt_token, session_id, recording_id, sample_path
    )
    if status != 200 or not upload_payload.get("success"):
        return upload_payload, status

    finish_payload, status = finish_transcription_service(jwt_token, session_id, recording_id)
    if status != 200 or not finish_payload.get("success"):
        return finish_payload, status

    transcript_payload, status = transcript_lookup_service(jwt_token, session_id)
    if status != 200 or not transcript_payload.get("success"):
        return transcript_payload, status

    return (
        {
            "success": True,
            "message": "Audio transcription test completed",
            "session_id": session_id,
            "recording_id": recording_id,
            "transcript": transcript_payload.get("transcript"),
        },
        200,
    )

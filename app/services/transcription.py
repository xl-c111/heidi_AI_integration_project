import logging
import os
import tempfile
from typing import Any, Dict, Tuple

from werkzeug.datastructures import FileStorage

from app.api.transcript import (
    finish_transcription,
    get_transcript,
    start_transcription,
    upload_audio,
)

logger = logging.getLogger(__name__)

JsonResponse = Tuple[Dict[str, Any], int]


def start_transcription_service(jwt_token: str, session_id: str) -> JsonResponse:
    """Start the transcription workflow and return a recording id."""
    result = start_transcription(jwt_token, session_id)

    if isinstance(result, dict) and result.get("error"):
        return result, result.get("status_code", 500)

    if not isinstance(result, str) or not result:
        return (
            {
                "success": False,
                "error": "Failed to start transcription",
                "details": result,
            },
            500,
        )

    return {"success": True, "recording_id": result}, 200


def _format_upload_result(result: Any, failure_message: str) -> JsonResponse:
    if isinstance(result, dict):
        is_success = result.get("is_success")
        if is_success is True:
            return {"success": True, "details": result}, 200
        if is_success is False:
            return (
                {
                    "success": False,
                    "error": failure_message,
                    "details": result,
                },
                500,
            )

        if result.get("error"):
            return result, result.get("status_code", 500)

    return (
        {
            "success": False,
            "error": failure_message,
            "details": result,
        },
        500,
    )


def upload_audio_from_path_service(
    jwt_token: str,
    session_id: str,
    recording_id: str,
    file_path: str,
    *,
    index: str = "0",
) -> JsonResponse:
    """Upload an audio chunk from a filesystem path."""
    if not os.path.exists(file_path):
        return (
            {
                "success": False,
                "error": "Audio file not found",
                "path": file_path,
            },
            400,
        )

    result = upload_audio(jwt_token, session_id, recording_id, file_path, index)
    return _format_upload_result(result, "Audio upload failed")


def upload_audio_service(
    jwt_token: str,
    session_id: str,
    recording_id: str,
    file_storage: FileStorage,
    *,
    index: str = "0",
) -> JsonResponse:
    """Upload audio from an incoming Flask FileStorage object."""
    if not file_storage:
        return {"success": False, "error": "No audio file provided"}, 400

    if not file_storage.filename:
        return {"success": False, "error": "No audio file selected"}, 400

    suffix = os.path.splitext(file_storage.filename)[1] or ".wav"

    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            file_storage.save(temp_file.name)
            temp_path = temp_file.name
            logger.debug("Temporary audio saved to %s", temp_path)

        return upload_audio_from_path_service(
            jwt_token, session_id, recording_id, temp_path, index=index
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.debug("Temporary audio removed: %s", temp_path)
            except OSError as exc:  # pragma: no cover - best effort cleanup
                logger.warning("Failed to remove temp file %s: %s", temp_path, exc)


def finish_transcription_service(
    jwt_token: str,
    session_id: str,
    recording_id: str,
) -> JsonResponse:
    """Mark the transcription as complete."""
    result = finish_transcription(jwt_token, session_id, recording_id)

    if isinstance(result, dict):
        if result.get("is_success") is True:
            return {"success": True, "details": result}, 200
        if result.get("error"):
            return result, result.get("status_code", 500)

    return (
        {
            "success": False,
            "error": "Failed to finish transcription",
            "details": result,
        },
        500,
    )


def transcript_lookup_service(jwt_token: str, session_id: str) -> JsonResponse:
    """Retrieve the transcript for a session."""
    result = get_transcript(jwt_token, session_id)

    if isinstance(result, dict) and result.get("error"):
        return result, result.get("status_code", 500)

    return {"success": True, "transcript": result}, 200

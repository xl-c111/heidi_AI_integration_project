import logging
from typing import Any, Dict, Optional, Tuple

from app.api.auth import get_jwt_token
from app.api.session import create_session

logger = logging.getLogger(__name__)

JsonResponse = Tuple[Dict[str, Any], int]


def fetch_jwt_token() -> Tuple[Optional[str], Optional[JsonResponse]]:
    """Return a JWT token or an error response tuple."""
    jwt_token = get_jwt_token()
    if not jwt_token or "Error" in str(jwt_token):
        logger.error("JWT retrieval failed: %s", jwt_token)
        return None, (
            {
                "success": False,
                "error": "Authentication failed",
                "details": str(jwt_token),
            },
            401,
        )
    return jwt_token, None


def ensure_session(jwt_token: str, session_id: Optional[str]) -> Tuple[Optional[str], Optional[JsonResponse]]:
    """Ensure a valid session id, creating one when necessary."""
    if session_id:
        return session_id, None

    new_session_id = create_session(jwt_token)
    if isinstance(new_session_id, dict) and new_session_id.get("error"):
        logger.error("Session creation failed: %s", new_session_id)
        return None, (
            {
                "success": False,
                "error": "Session creation failed",
                "details": new_session_id,
            },
            500,
        )

    if not isinstance(new_session_id, str):
        logger.error("Unexpected session id type: %s", type(new_session_id))
        return None, (
            {
                "success": False,
                "error": "Invalid session ID format",
                "received_type": type(new_session_id).__name__,
                "received_value": str(new_session_id),
            },
            500,
        )

    return new_session_id, None

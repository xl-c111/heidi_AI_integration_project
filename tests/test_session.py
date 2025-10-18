import responses

from app.api import BASE_URL
from app.api.session import create_session, get_session_details, update_session


def test_create_session_success(http_mock):
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions",
        json={"session_id": "session-123"},
        status=201,
    )

    session_id = create_session("jwt-token")

    assert session_id == "session-123"


def test_create_session_failure(http_mock):
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions",
        status=500,
        json={"error": "internal"},
    )

    result = create_session("jwt-token")

    assert result["error"] is True
    assert result["status_code"] == 500


def test_get_session_details_success(http_mock):
    http_mock.add(
        responses.GET,
        f"{BASE_URL}/sessions/session-123",
        json={"id": "session-123", "status": "READY"},
        status=200,
    )

    details = get_session_details("jwt-token", "session-123")

    assert details["status"] == "READY"


def test_update_session_success(http_mock):
    http_mock.add(
        responses.PATCH,
        f"{BASE_URL}/sessions/session-123",
        json={"id": "session-123", "duration": 60},
        status=200,
    )

    result = update_session(
        jwt_token="jwt-token",
        session_id="session-123",
        duration=60,
    )

    assert result["duration"] == 60

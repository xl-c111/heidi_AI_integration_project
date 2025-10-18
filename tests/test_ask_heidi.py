import responses

from app.api import BASE_URL
from app.api.ask_heidi import ask_ai_stream, parse_sse_response


def test_parse_sse_response_combines_chunks():
    body = (
        'data: {"data": "First part "}\n\n'
        'data: {"data": "and second"}\n\n'
    )

    combined = parse_sse_response(body)

    assert combined == "First part and second"


def test_ask_ai_stream_sse_format(http_mock):
    body = 'data: {"data": "Care plan"}\n\n'
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions/session-123/ask-ai",
        body=body,
        status=200,
        content_type="text/event-stream",
    )

    result = ask_ai_stream(
        jwt_token="jwt-token",
        session_id="session-123",
        ai_command_text="Generate care plan",
        content="Document content",
    )

    assert result["success"] is True
    assert result["response"] == "Care plan"
    assert result["format"] == "sse"


def test_ask_ai_stream_json_format(http_mock):
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions/session-123/ask-ai",
        json={"response": {"content": "All good"}},
        status=200,
        content_type="application/json",
    )

    result = ask_ai_stream(
        jwt_token="jwt-token",
        session_id="session-123",
        ai_command_text="Generate care plan",
        content="Document content",
    )

    assert result["success"] is True
    assert result["response"] == {"response": {"content": "All good"}}
    assert result["format"] == "json"


def test_ask_ai_stream_handles_errors(http_mock):
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions/session-123/ask-ai",
        status=401,
        json={"message": "unauthorized"},
    )

    result = ask_ai_stream(
        jwt_token="jwt-token",
        session_id="session-123",
        ai_command_text="Generate care plan",
        content="Document content",
    )

    assert result["error"] is True
    assert result["status_code"] == 401

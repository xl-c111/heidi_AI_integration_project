import json

from app.api.ask_heidi import ask_ai_stream, parse_sse_response


def test_parse_sse_response_combines_chunks():
    body = (
        'data: {"data": "First part "}\n\n'
        'data: {"data": "and second"}\n\n'
    )

    combined = parse_sse_response(body)

    assert combined == "First part and second"


def test_ask_ai_stream_sse_format(monkeypatch):
    lines = ['data: {"data": "Care plan"}', ""]

    response = _DummyResponse(
        status_code=200,
        headers={"Content-Type": "text/event-stream"},
        lines=lines,
    )

    monkeypatch.setattr(
        "app.api.ask_heidi.requests.post",
        lambda *args, **kwargs: response,
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


def test_ask_ai_stream_json_format(monkeypatch):
    response = _DummyResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        json_payload={"response": {"content": "All good"}},
    )

    monkeypatch.setattr(
        "app.api.ask_heidi.requests.post",
        lambda *args, **kwargs: response,
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


def test_ask_ai_stream_handles_errors(monkeypatch):
    response = _DummyResponse(
        status_code=401,
        headers={"Content-Type": "application/json"},
        json_payload={"message": "unauthorized"},
    )

    monkeypatch.setattr(
        "app.api.ask_heidi.requests.post",
        lambda *args, **kwargs: response,
    )

    result = ask_ai_stream(
        jwt_token="jwt-token",
        session_id="session-123",
        ai_command_text="Generate care plan",
        content="Document content",
    )

    assert result["error"] is True
    assert result["status_code"] == 401


class _DummyResponse:
    def __init__(self, status_code=200, headers=None, lines=None, json_payload=None, text_body=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._lines = lines or []
        self._json_payload = json_payload
        self._text_body = text_body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def iter_lines(self, decode_unicode=False):
        for line in self._lines:
            yield line if decode_unicode else line.encode()

    def json(self):
        if self._json_payload is None:
            raise json.JSONDecodeError("No JSON payload", "", 0)
        return self._json_payload

    @property
    def text(self):
        if self._text_body is not None:
            return self._text_body
        if self._json_payload is not None:
            return json.dumps(self._json_payload)
        return "\n".join(self._lines)

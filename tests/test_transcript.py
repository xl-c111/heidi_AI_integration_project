import responses

from app.api import BASE_URL
from app.api.transcript import (
    finish_transcription,
    get_transcript,
    start_transcription,
    upload_audio,
)


def test_start_transcription_returns_recording_id(http_mock):
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions/session-123/restful-segment-transcription",
        json={"recording_id": "rec-123"},
        status=200,
    )

    recording_id = start_transcription("jwt-token", "session-123")

    assert recording_id == "rec-123"


def test_upload_audio_posts_file(http_mock, tmp_path):
    audio_path = tmp_path / "sample.mp3"
    audio_path.write_bytes(b"\x00\x01")

    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions/session-123/restful-segment-transcription/rec-123:transcribe",
        json={"is_success": True},
        status=200,
    )

    result = upload_audio("jwt-token", "session-123", "rec-123", str(audio_path))

    assert result["is_success"] is True


def test_finish_transcription_returns_payload(http_mock):
    http_mock.add(
        responses.POST,
        f"{BASE_URL}/sessions/session-123/restful-segment-transcription/rec-123:finish",
        json={"is_success": True, "message": "done"},
        status=200,
    )

    result = finish_transcription("jwt-token", "session-123", "rec-123")

    assert result["is_success"] is True


def test_get_transcript_returns_json(http_mock):
    http_mock.add(
        responses.GET,
        f"{BASE_URL}/sessions/session-123/transcript",
        json={"transcript": "Patient feels better."},
        status=200,
    )

    result = get_transcript("jwt-token", "session-123")

    assert result["transcript"] == "Patient feels better."

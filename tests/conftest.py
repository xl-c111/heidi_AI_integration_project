import os
import sys
from pathlib import Path

import pytest
import responses


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(autouse=True)
def heidi_env(monkeypatch):
    """Provide default Heidi credentials for tests."""
    monkeypatch.setenv("HEIDI_API_KEY", "test-api-key")
    monkeypatch.setenv("HEIDI_EMAIL", "clinician@example.com")
    monkeypatch.setenv("HEIDI_USER_ID", "user-123")
    # Allow overriding via env but fall back to real base URL to match client defaults
    monkeypatch.setenv(
        "HEIDI_BASE_URL",
        os.getenv(
            "HEIDI_BASE_URL",
            "https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api",
        ),
    )
    yield


@pytest.fixture
def http_mock():
    """Wrap requests calls with the responses library."""
    with responses.RequestsMock() as rsps:
        yield rsps

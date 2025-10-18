import responses

from app.api import BASE_URL
from app.api.auth import get_jwt_token


def test_get_jwt_token_success(http_mock):
    http_mock.add(
        responses.GET,
        f"{BASE_URL}/jwt",
        json={"token": "jwt-token"},
        status=200,
    )

    token = get_jwt_token()

    assert token == "jwt-token"


def test_get_jwt_token_failure(http_mock):
    http_mock.add(
        responses.GET,
        f"{BASE_URL}/jwt",
        status=401,
        json={"message": "unauthorized"},
    )

    token = get_jwt_token()

    assert token.startswith("Error:")

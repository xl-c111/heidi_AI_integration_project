# debug_test.py - Try different header formats
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "HEIDI_BASE_URL",
    "https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api",
)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and provide valid credentials."
        )
    return value


API_KEY = require_env("HEIDI_API_KEY")
EMAIL = require_env("HEIDI_EMAIL")
USER_ID = require_env("HEIDI_USER_ID")

def test_jwt_variations():
    print("=== Testing Different JWT Header Formats ===")
    url = f"{BASE_URL}/jwt"

    params = {"email": EMAIL, "third_party_internal_id": USER_ID}

    # Try different header formats
    header_variations = [
        {"Heidi-Api-Key": API_KEY},
        {"heidi-api-key": API_KEY},
        {"X-API-Key": API_KEY},
        {"Authorization": f"Bearer {API_KEY}"},
        {"Authorization": API_KEY},
        {"API-Key": API_KEY},
        {"x-api-key": API_KEY},
        {"Heidi-API-Key": API_KEY},  # Different capitalization
    ]

    for i, headers in enumerate(header_variations, 1):
        print(f"\n--- Attempt {i}: {headers} ---")
        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                token = response.json().get("token")
                print(f"✅ SUCCESS with headers: {headers}")
                print(f"Token: {token[:30]}...")
                return token, headers

        except Exception as e:
            print(f"Exception: {e}")

    print("❌ All header formats failed")
    return None, None

def test_with_curl_equivalent():
    print("\n=== Testing with Raw Request ===")

    # Let's see exactly what we're sending
    url = f"{BASE_URL}/jwt"
    params = {"email": EMAIL, "third_party_internal_id": USER_ID}
    headers = {"Heidi-Api-Key": API_KEY}

    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Headers: {headers}")
    print(f"Full URL: {url}?email={EMAIL}&third_party_internal_id={USER_ID}")

    # Manual construction to see what's happening
    full_url = f"{url}?email={EMAIL}&third_party_internal_id={USER_ID}"

    try:
        response = requests.get(full_url, headers=headers)
        print(f"\nManual URL Status: {response.status_code}")
        print(f"Manual URL Response: {response.text}")
        print(f"Response Headers: {dict(response.headers)}")

    except Exception as e:
        print(f"Exception: {e}")

def test_api_key_validation():
    print("\n=== Testing API Key Validation ===")

    # Test if the API key itself is valid by trying different endpoints
    test_urls = [
        f"{BASE_URL}/jwt",
        f"{BASE_URL}/health",  # Sometimes APIs have health endpoints
        f"{BASE_URL}/",
    ]

    headers = {"Heidi-Api-Key": API_KEY}

    for test_url in test_urls:
        print(f"\nTesting: {test_url}")
        try:
            response = requests.get(test_url, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    print("🔍 Debugging Heidi API Header Issues...\n")

    # Test 1: Try different header formats
    token, working_headers = test_jwt_variations()

    # Test 2: Raw request debugging
    test_with_curl_equivalent()

    # Test 3: API key validation
    test_api_key_validation()

    if token:
        print(f"\n🎉 Found working format: {working_headers}")
    else:
        print(f"\n❌ Need to investigate API key or endpoint")
        print(f"API Key being used: {API_KEY}")
        print(f"Email being used: {EMAIL}")
        print(f"User ID being used: {USER_ID}")

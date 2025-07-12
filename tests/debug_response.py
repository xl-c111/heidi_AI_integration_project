# debug_response.py - Let's see what we're actually getting back
import requests

BASE_URL = "https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api"
API_KEY = "MI0QanRHLm4ovFkBVqcBrx3LCiWLT8eu"
EMAIL = "marwa.almahmoud@hotmail.com"
USER_ID = "marwa-hack"

def get_jwt_token():
    url = f"{BASE_URL}/jwt"
    headers = {"Heidi-Api-Key": API_KEY}
    params = {"email": EMAIL, "third_party_internal_id": USER_ID}

    response = requests.get(url, headers=headers, params=params)
    return response.json()["token"]

def create_session(jwt_token):
    url = f"{BASE_URL}/sessions"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Heidi-Api-Key": API_KEY
    }
    payload = {"email": EMAIL, "third_party_internal_id": USER_ID}

    response = requests.post(url, headers=headers, json=payload)
    return response.json()["session_id"]

def debug_ask_ai_response(jwt_token, session_id):
    print("=== Debugging Ask AI Response ===")
    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "ai_command_text": "Create a brief post-surgery care plan",
        "content": "Patient discharged after knee surgery. Needs medication schedule and activity guidance.",
        "content_type": "MARKDOWN"
    }

    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    response = requests.post(url, headers=headers, json=payload)

    print(f"\n=== RESPONSE DEBUG ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Raw Response Text: '{response.text}'")
    print(f"Response Length: {len(response.text)}")
    print(f"Response Type: {type(response.text)}")

    if response.text.strip():
        print(f"Response (first 500 chars): {response.text[:500]}")
        try:
            json_response = response.json()
            print(f"✅ Valid JSON: {json_response}")
            return json_response
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")

            # Try to figure out what we got
            if response.text.startswith('data:'):
                print("🔍 Looks like Server-Sent Events (SSE) format")
                lines = response.text.split('\n')
                for line in lines[:10]:  # Show first 10 lines
                    print(f"  Line: '{line}'")
            elif response.text.startswith('{'):
                print("🔍 Looks like malformed JSON")
            else:
                print("🔍 Unknown response format")

            return None
    else:
        print("❌ Empty response")
        return None

if __name__ == "__main__":
    print("🔍 Debugging Ask AI Response Format...\n")

    jwt_token = get_jwt_token()
    session_id = create_session(jwt_token)

    print(f"JWT Token: {jwt_token[:50]}...")
    print(f"Session ID: {session_id}\n")

    result = debug_ask_ai_response(jwt_token, session_id)

    if result:
        print("\n✅ Successfully parsed response!")
    else:
        print("\n❌ Need to handle different response format")
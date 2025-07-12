import requests
from app.api import BASE_URL
import os


def create_session(jwt_token):
    # FIXED: Remove /templates from URL path
    url = f"{BASE_URL}/sessions"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }

    # Add payload instead of params
    payload = {
        "email": os.getenv("HEIDI_EMAIL"),
        "third_party_internal_id": os.getenv("HEIDI_USER_ID")
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Session creation response: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            # Try both possible response formats
            session_id = response_data.get("session_id") or response_data.get("id")
            return session_id
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }


def get_session_details(jwt_token, session_id):
    url = f"{BASE_URL}/sessions/{session_id}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }


def update_session(
    jwt_token: str,
    session_id: str,
    duration: int = None,
    language_code: str = None,
    output_language_code: str = None,
    patient: dict = None,
    clinician_notes: list = None,
    generate_output_without_recording: bool = None
):
    url = f"{BASE_URL}/sessions/{session_id}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }
    payload = {}
    if duration is not None:
        payload["duration"] = duration
    if language_code is not None:
        payload["language_code"] = language_code
    if output_language_code is not None:
        payload["output_language_code"] = output_language_code
    if patient is not None:
        payload["patient"] = patient
    if clinician_notes is not None:
        payload["clinician_notes"] = clinician_notes
    if generate_output_without_recording is not None:
        payload["generate_output_without_recording"] = generate_output_without_recording

    try:
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text
            }
    except Exception as e:
        return {
            "error": True,
            "message": str(e)
        }
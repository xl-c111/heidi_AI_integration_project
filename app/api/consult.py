import requests
from app.api import BASE_URL
import os
from app.api.session import create_session


def get_consult_note_templates(jwt_token):
    url = f"{BASE_URL}/templates/consult-note-templates"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }
    print("API KEY:" + os.getenv("HEIDI_API_KEY"))
    params = {
        "email": os.getenv("HEIDI_EMAIL"),
        "third_party_internal_id": os.getenv("HEIDI_USER_ID")
    }

    try:
        response = requests.get(url, headers=headers, params=params)
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


def generate_consult_note(jwt_token, session_id, template_id, voice_style="GOLDILOCKS", brain="LEFT", addition=""):
    url = f"{BASE_URL}/sessions/{session_id}/consult-note"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }

    payload = {
        "generation_method": "TEMPLATE",
        "addition": addition,
        "template_id": template_id,
        "voice_style": voice_style,
        "brain": brain
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
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

import requests
from app.api import BASE_URL
import os
def start_transcription(jwt_token, session_id):
    url = f"{BASE_URL}/sessions/{session_id}/restful-segment-transcription"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("recording_id")
    else:
        return {
            "error": True,
            "status_code": response.status_code,
            "message": response.text
        }

def upload_audio(jwt_token, session_id, recording_id, file_path, index="0"):
    url = f"{BASE_URL}/sessions/{session_id}/restful-segment-transcription/{recording_id}:transcribe"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }
    files = {
        "file": open(file_path, "rb")
    }
    data = {
        "index": index
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()

def finish_transcription(jwt_token, session_id, recording_id):
    url = f"{BASE_URL}/sessions/{session_id}/restful-segment-transcription/{recording_id}:finish"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }

    response = requests.post(url, headers=headers)
    return response.json()

def get_transcript(jwt_token, session_id):
    url = f"{BASE_URL}/sessions/{session_id}/transcript"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }

    response = requests.get(url, headers=headers)
    return response.json()

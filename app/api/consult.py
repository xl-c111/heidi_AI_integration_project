
import os
import requests

from app.api import BASE_URL

def generate_consult_note(jwt_token):
    url = f"{BASE_URL}/templates/consult-note-templates"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "template": "general",  # Other templates might include 'mental_health', etc.
        "transcript": "Patient complains of shortness of breath and chest discomfort during exercise. No known history of heart disease."
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

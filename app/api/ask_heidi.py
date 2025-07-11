import requests
from app.api import BASE_URL
import os

def ask_ai_stream(jwt_token, session_id, ai_command_text, content, content_type):
    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
        }
    payload = {
        "ai_command_text": ai_command_text,
        "content": content,
        "content_type": content_type
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

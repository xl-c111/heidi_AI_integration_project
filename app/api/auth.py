import os
import requests
from app.api import BASE_URL

def get_jwt_token():
    url = f"{BASE_URL}/jwt"

    headers = {
        "Heidi-Api-Key": os.getenv("HEIDI_API_KEY")
    }
    params = {
        "email": os.getenv("HEIDI_EMAIL"),
        "third_party_internal_id": os.getenv("HEIDI_USER_ID")
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("token")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"
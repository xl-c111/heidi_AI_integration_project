# app/api/ask_heidi.py - FIXED with SSE parsing
import requests
import json
from app.api import BASE_URL
import os

def parse_sse_response(sse_text):
    """Parse Server-Sent Events format and extract the actual content"""
    lines = sse_text.strip().split('\n')
    combined_content = ""

    for line in lines:
        line = line.strip()
        if line.startswith('data: '):
            # Extract JSON from each data line
            json_str = line[6:]  # Remove 'data: ' prefix
            try:
                data_obj = json.loads(json_str)
                if 'data' in data_obj:
                    combined_content += data_obj['data']
            except json.JSONDecodeError:
                # Skip malformed lines
                continue

    return combined_content.strip()

def ask_ai_stream(jwt_token, session_id, ai_command_text, content, content_type="MARKDOWN"):
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
            # Check if it's SSE format
            content_type_header = response.headers.get('content-type', '').lower()

            if 'text/event-stream' in content_type_header:
                # Parse SSE response
                parsed_content = parse_sse_response(response.text)
                return {
                    "success": True,
                    "response": parsed_content,
                    "format": "sse"
                }
            else:
                # Try to parse as regular JSON
                try:
                    return response.json()
                except:
                    # Fallback to raw text
                    return {
                        "success": True,
                        "response": response.text,
                        "format": "text"
                    }
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
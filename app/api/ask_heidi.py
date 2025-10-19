import json
from typing import List
import requests
from app.api import BASE_URL


def _extract_sse_chunk(raw_payload: str) -> str:
    """Extract text content from an individual SSE data payload."""
    try:
        data_obj = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        print(f"  Failed to parse SSE chunk: {exc}")
        return ""

    if isinstance(data_obj, dict):
        if isinstance(data_obj.get("data"), str):
            print(f"  Parsed chunk: {data_obj['data'][:50]}...")
            return data_obj["data"]
        if isinstance(data_obj.get("content"), str):
            print(f"  Parsed content: {data_obj['content'][:50]}...")
            return data_obj["content"]
    elif isinstance(data_obj, str):
        print(f"  Parsed string chunk: {data_obj[:50]}...")
        return data_obj

    print(f"  Unknown data format: {data_obj}")
    return ""


def _consume_sse_stream(response: requests.Response) -> str:
    """Iterate through the SSE stream and concatenate payloads."""
    combined_chunks: List[str] = []
    try:
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            # keep only lines with data: prefix
            if not line.startswith("data:"):
                continue
            chunk = _extract_sse_chunk(line[5:].lstrip())
            if chunk:
                combined_chunks.append(chunk)
    except (requests.exceptions.ChunkedEncodingError, json.JSONDecodeError) as exc:
        print(f"Error while streaming SSE: {exc}")
        return ""

    return "".join(combined_chunks)


def parse_sse_response(sse_text: str) -> str:
    """Parse Server-Sent Events format and extract the actual content."""
    print("=== PARSING SSE RESPONSE ===")
    print(f"Raw response length: {len(sse_text)}")
    print(f"First 200 chars: {sse_text[:200]}")

    lines = sse_text.strip().split("\n")
    combined_content = ""
    data_lines_found = 0

    for line in lines:
        line = line.strip()
        if line.startswith("data:"):
            data_lines_found += 1
            # take the raw JSON payload and extract only useful content field
            chunk = _extract_sse_chunk(line[5:].lstrip())
            if chunk:
                combined_content += chunk

    print(f"Data lines found: {data_lines_found}")
    print(f"Combined content length: {len(combined_content)}")

    return combined_content.strip()


def ask_ai_stream(jwt_token, session_id, ai_command_text, content, content_type="MARKDOWN"):
    """
    Enhanced Ask AI function with comprehensive error handling and multiple format support
    """
    print(f"=== ASK AI STREAM CALLED ===")
    print(f"Session ID: {session_id}")
    print(f"Content type: {content_type}")
    print(f"AI command: {ai_command_text[:100]}...")
    print(f"Content: {content[:100]}...")

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

    print(f"Request URL: {url}")
    print(f"Request headers: {headers}")
    print(f"Request payload: {payload}")

    try:
        # Increase timeout for potentially slow AI responses
        with requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=(10, 70),
        ) as response:

            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            if response.status_code == 200:
                # Check content type header to determine parsing strategy
                raw_content_type = ""
                for header_key, header_value in response.headers.items():
                    if header_key.lower() == "content-type":
                        raw_content_type = header_value
                        # stop looping once you found header
                        break

                normalized_content_type = raw_content_type.lower()
                print(f"Content-Type header: {raw_content_type}")

                if 'text/event-stream' in normalized_content_type:
                    print("Detected SSE format response")
                    parsed_content = _consume_sse_stream(response)
                    if parsed_content:
                        return {
                            "success": True,
                            "response": parsed_content,
                            "format": "sse",
                        }
                    print("SSE parsing returned empty content")
                    return {
                        "error": True,
                        "message": "SSE response was empty after parsing",
                        "status_code": response.status_code
                    }

                if 'application/json' in normalized_content_type:
                    print("Detected JSON format response")
                    try:
                        json_response = response.json()
                        return {
                            "success": True,
                            "response": json_response,
                            "format": "json"
                        }
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing failed: {e}")
                        text_body = response.text
                        return {
                            "success": True,
                            "response": text_body,
                            "format": "text",
                            "warning": "Expected JSON but got raw text"
                        }

                print("Detected raw text response")
                text_body = response.text
                if text_body.strip():
                    return {
                        "success": True,
                        "response": text_body,
                        "format": "text"
                    }

                return {
                    "error": True,
                    "message": "Empty response received",
                    "status_code": response.status_code
                }

            if response.status_code == 401:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": "Authentication failed - JWT token may be expired",
                    "suggestion": "Try refreshing the JWT token"
                }

            if response.status_code == 404:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": "Session not found - session may have expired",
                    "suggestion": "Create a new session"
                }

            return {
                "error": True,
                "status_code": response.status_code,
                "message": response.text,
                "suggestion": "Check API documentation for status code meaning"
            }

    except requests.exceptions.Timeout:
        return {
            "error": True,
            "message": "Request timeout - AI response took too long",
            "suggestion": "Try again with simpler content or check network connection"
        }

    except requests.exceptions.ConnectionError:
        return {
            "error": True,
            "message": "Connection error - unable to reach Heidi API",
            "suggestion": "Check internet connection and API status"
        }

    except Exception as e:
        return {
            "error": True,
            "message": f"Unexpected error: {str(e)}",
            "suggestion": "Check logs for more details"
        }


def test_ask_ai_with_fallbacks(jwt_token, session_id, ai_command_text, content):
    """
    Test Ask AI with multiple content types as fallbacks
    """
    print(f"=== TESTING ASK AI WITH FALLBACKS ===")

    # Try different content types in order of preference
    content_types = ["MARKDOWN", "TEXT", "PLAIN_TEXT"]

    for content_type in content_types:
        print(f"\nTrying content type: {content_type}")

        result = ask_ai_stream(jwt_token, session_id,
                               ai_command_text, content, content_type)

        if result.get("success"):
            print(f"✅ Success with content type: {content_type}")
            return result
        else:
            print(
                f"❌ Failed with {content_type}: {result.get('message', 'Unknown error')}")

    # If all content types fail, return the last error
    return {
        "error": True,
        "message": "All content types failed",
        "suggestion": "Check JWT token and session validity"
    }

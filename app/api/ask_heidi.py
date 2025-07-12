# app/api/ask_heidi.py - ENHANCED with better error handling and debugging
# Make sure this file replaces your existing app/api/ask_heidi.py
import requests
import json
from app.api import BASE_URL
import os
import time

def parse_sse_response(sse_text):
    """Parse Server-Sent Events format and extract the actual content"""
    print(f"=== PARSING SSE RESPONSE ===")
    print(f"Raw response length: {len(sse_text)}")
    print(f"First 200 chars: {sse_text[:200]}")

    lines = sse_text.strip().split('\n')
    combined_content = ""
    data_lines_found = 0

    for line in lines:
        line = line.strip()
        if line.startswith('data: '):
            data_lines_found += 1
            # Extract JSON from each data line
            json_str = line[6:]  # Remove 'data: ' prefix
            try:
                data_obj = json.loads(json_str)
                if 'data' in data_obj:
                    combined_content += data_obj['data']
                    print(f"  Parsed chunk: {data_obj['data'][:50]}...")
                elif 'content' in data_obj:
                    combined_content += data_obj['content']
                    print(f"  Parsed content: {data_obj['content'][:50]}...")
                else:
                    print(f"  Unknown data format: {data_obj}")
            except json.JSONDecodeError as e:
                print(f"  Failed to parse line: {line} - Error: {e}")
                continue

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
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response length: {len(response.text)}")

        if response.status_code == 200:
            # Check content type header to determine parsing strategy
            content_type_header = response.headers.get('content-type', '').lower()
            print(f"Content-Type header: {content_type_header}")

            if 'text/event-stream' in content_type_header or 'data:' in response.text:
                print("Detected SSE format response")
                # Parse SSE response
                parsed_content = parse_sse_response(response.text)
                if parsed_content:
                    return {
                        "success": True,
                        "response": parsed_content,
                        "format": "sse",
                        "raw_length": len(response.text)
                    }
                else:
                    print("SSE parsing returned empty content")
                    return {
                        "error": True,
                        "message": "SSE response was empty after parsing",
                        "raw_response": response.text[:500],
                        "status_code": response.status_code
                    }

            elif 'application/json' in content_type_header:
                print("Detected JSON format response")
                # Try to parse as regular JSON
                try:
                    json_response = response.json()
                    return {
                        "success": True,
                        "response": json_response,
                        "format": "json"
                    }
                except json.JSONDecodeError as e:
                    print(f"JSON parsing failed: {e}")
                    # Fallback to raw text
                    return {
                        "success": True,
                        "response": response.text,
                        "format": "text",
                        "warning": "Expected JSON but got raw text"
                    }

            else:
                print("Detected raw text response")
                # Fallback to raw text
                if response.text.strip():
                    return {
                        "success": True,
                        "response": response.text,
                        "format": "text"
                    }
                else:
                    return {
                        "error": True,
                        "message": "Empty response received",
                        "status_code": response.status_code
                    }

        elif response.status_code == 401:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": "Authentication failed - JWT token may be expired",
                "suggestion": "Try refreshing the JWT token"
            }

        elif response.status_code == 404:
            return {
                "error": True,
                "status_code": response.status_code,
                "message": "Session not found - session may have expired",
                "suggestion": "Create a new session"
            }

        else:
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

        result = ask_ai_stream(jwt_token, session_id, ai_command_text, content, content_type)

        if result.get("success"):
            print(f"✅ Success with content type: {content_type}")
            return result
        else:
            print(f"❌ Failed with {content_type}: {result.get('message', 'Unknown error')}")

    # If all content types fail, return the last error
    return {
        "error": True,
        "message": "All content types failed",
        "suggestion": "Check JWT token and session validity"
    }
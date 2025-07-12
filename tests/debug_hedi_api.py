# debug_heidi_api.py - Comprehensive debugging for Heidi API issues
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api"

class HeidiAPIDebugger:
    def __init__(self):
        self.api_key = os.getenv("HEIDI_API_KEY")
        self.email = os.getenv("HEIDI_EMAIL")
        self.user_id = os.getenv("HEIDI_USER_ID")
        self.jwt_token = None
        self.session_id = None

    def print_separator(self, title):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def check_environment(self):
        self.print_separator("STEP 1: ENVIRONMENT CHECK")

        env_vars = {
            "HEIDI_API_KEY": self.api_key,
            "HEIDI_EMAIL": self.email,
            "HEIDI_USER_ID": self.user_id
        }

        all_good = True
        for var_name, var_value in env_vars.items():
            if var_value:
                print(f"✅ {var_name}: {'*' * 20}{var_value[-4:] if len(var_value) > 4 else var_value}")
            else:
                print(f"❌ {var_name}: NOT SET")
                all_good = False

        if not all_good:
            print(f"\n⚠️  Missing environment variables. Check your .env file!")
            return False

        print(f"\n✅ All environment variables are set")
        return True

    def test_jwt_authentication(self):
        self.print_separator("STEP 2: JWT AUTHENTICATION TEST")

        url = f"{BASE_URL}/jwt"
        headers = {"Heidi-Api-Key": self.api_key}
        params = {
            "email": self.email,
            "third_party_internal_id": self.user_id
        }

        print(f"🔗 URL: {url}")
        print(f"📤 Headers: {headers}")
        print(f"📤 Params: {params}")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            print(f"📥 Response Text (first 200 chars): {response.text[:200]}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.jwt_token = data.get("token")
                    if self.jwt_token:
                        print(f"✅ JWT Success! Token: {self.jwt_token[:30]}...")
                        return True
                    else:
                        print(f"❌ JWT token not found in response: {data}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            else:
                print(f"❌ JWT Failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - Heidi API might be slow")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return False

    def test_session_creation(self):
        self.print_separator("STEP 3: SESSION CREATION TEST")

        if not self.jwt_token:
            print(f"❌ No JWT token available for session creation")
            return False

        url = f"{BASE_URL}/sessions"
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "Heidi-Api-Key": self.api_key
        }
        payload = {
            "email": self.email,
            "third_party_internal_id": self.user_id
        }

        print(f"🔗 URL: {url}")
        print(f"📤 Headers: {headers}")
        print(f"📤 Payload: {payload}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📥 Response Text: {response.text}")

            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    # Try different possible session ID keys
                    self.session_id = data.get("session_id") or data.get("id") or data.get("sessionId")

                    if self.session_id:
                        print(f"✅ Session Success! ID: {self.session_id}")
                        return True
                    else:
                        print(f"❌ Session ID not found in response: {data}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            else:
                print(f"❌ Session Creation Failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.Timeout:
            print(f"❌ Request timeout during session creation")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return False

    def test_ask_ai_with_different_formats(self):
        self.print_separator("STEP 4: ASK AI TEST WITH MULTIPLE FORMATS")

        if not self.jwt_token or not self.session_id:
            print(f"❌ Missing JWT token or session ID")
            return False

        url = f"{BASE_URL}/sessions/{self.session_id}/ask-ai"

        # Test different content types that might work
        test_cases = [
            {
                "name": "MARKDOWN format",
                "content_type": "MARKDOWN",
                "ai_command_text": "Create a brief care plan",
                "content": "Patient discharged after surgery. Needs basic care instructions."
            },
            {
                "name": "TEXT format",
                "content_type": "TEXT",
                "ai_command_text": "Create a brief care plan",
                "content": "Patient discharged after surgery. Needs basic care instructions."
            },
            {
                "name": "PLAIN_TEXT format",
                "content_type": "PLAIN_TEXT",
                "ai_command_text": "Create a brief care plan",
                "content": "Patient discharged after surgery. Needs basic care instructions."
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test_case['name']} ---")

            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "ai_command_text": test_case["ai_command_text"],
                "content": test_case["content"],
                "content_type": test_case["content_type"]
            }

            print(f"📤 Content Type: {test_case['content_type']}")
            print(f"📤 Payload: {payload}")

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=45)

                print(f"📥 Status: {response.status_code}")
                print(f"📥 Response length: {len(response.text)}")
                print(f"📥 Content-Type header: {response.headers.get('content-type', 'N/A')}")

                if response.status_code == 200:
                    # Check response format
                    if 'text/event-stream' in response.headers.get('content-type', '').lower():
                        print(f"📥 SSE Response detected")
                        parsed_content = self.parse_sse_response(response.text)
                        if parsed_content:
                            print(f"✅ SUCCESS with {test_case['name']}!")
                            print(f"📄 Parsed content (first 200 chars): {parsed_content[:200]}...")
                            return True
                        else:
                            print(f"❌ Failed to parse SSE content")
                    else:
                        try:
                            data = response.json()
                            print(f"✅ SUCCESS with {test_case['name']}!")
                            print(f"📄 JSON response: {str(data)[:200]}...")
                            return True
                        except json.JSONDecodeError:
                            print(f"📄 Raw text response (first 200 chars): {response.text[:200]}...")
                            if response.text.strip():
                                print(f"✅ Got response with {test_case['name']} (raw text)")
                                return True
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text[:200]}")

            except requests.exceptions.Timeout:
                print(f"❌ Timeout for {test_case['name']}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error for {test_case['name']}: {e}")

        print(f"\n❌ All Ask AI tests failed")
        return False

    def parse_sse_response(self, sse_text):
        """Parse Server-Sent Events format"""
        lines = sse_text.strip().split('\n')
        combined_content = ""

        for line in lines:
            line = line.strip()
            if line.startswith('data: '):
                json_str = line[6:]  # Remove 'data: ' prefix
                try:
                    data_obj = json.loads(json_str)
                    if 'data' in data_obj:
                        combined_content += data_obj['data']
                except json.JSONDecodeError:
                    continue

        return combined_content.strip()

    def run_comprehensive_test(self):
        print(f"🧪 HEIDI API COMPREHENSIVE DEBUG TEST")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Environment check
        if not self.check_environment():
            return False

        # Step 2: JWT authentication
        if not self.test_jwt_authentication():
            return False

        # Step 3: Session creation
        if not self.test_session_creation():
            return False

        # Step 4: Ask AI test
        if not self.test_ask_ai_with_different_formats():
            return False

        self.print_separator("🎉 ALL TESTS PASSED!")
        print(f"✅ Environment: OK")
        print(f"✅ JWT Authentication: OK")
        print(f"✅ Session Creation: OK")
        print(f"✅ Ask AI: OK")
        print(f"\n🚀 Your Heidi API integration is working!")
        print(f"📋 Session ID for further testing: {self.session_id}")
        print(f"🔑 JWT token valid for ~1 hour")

        return True

if __name__ == "__main__":
    debugger = HeidiAPIDebugger()
    success = debugger.run_comprehensive_test()

    if not success:
        print(f"\n🔧 DEBUGGING SUGGESTIONS:")
        print(f"1. Check your .env file has correct credentials")
        print(f"2. Verify API key is still valid")
        print(f"3. Try running: python3 tests/sse_parser_test.py")
        print(f"4. Check Heidi API documentation for changes")
        print(f"5. Test with a simple curl command first")
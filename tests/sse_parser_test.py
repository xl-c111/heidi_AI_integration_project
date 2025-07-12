# sse_parser_test.py - Parse Server-Sent Events from Heidi API
import requests
import json

BASE_URL = "https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api"
API_KEY = "MI0QanRHLm4ovFkBVqcBrx3LCiWLT8eu"
EMAIL = "marwa.almahmoud@hotmail.com"
USER_ID = "marwa-hack"

def parse_sse_response(sse_text):
    """Parse Server-Sent Events format and extract the actual content"""
    print("=== Parsing SSE Response ===")

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
                    print(f"  Chunk: '{data_obj['data']}'")
            except json.JSONDecodeError as e:
                print(f"  ❌ Failed to parse line: {line} - Error: {e}")

    print(f"\n=== COMBINED RESULT ===")
    print(combined_content)
    print("=" * 50)

    return combined_content

def get_jwt_token():
    response = requests.get(f"{BASE_URL}/jwt",
                          headers={"Heidi-Api-Key": API_KEY},
                          params={"email": EMAIL, "third_party_internal_id": USER_ID})
    return response.json()["token"]

def create_session(jwt_token):
    response = requests.post(f"{BASE_URL}/sessions",
                           headers={"Authorization": f"Bearer {jwt_token}",
                                  "Content-Type": "application/json",
                                  "Heidi-Api-Key": API_KEY},
                           json={"email": EMAIL, "third_party_internal_id": USER_ID})
    return response.json()["session_id"]

def test_care_plan_generation(jwt_token, session_id):
    print("=== Testing Care Plan Generation with SSE Parsing ===")

    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

    care_plan_prompt = """
    You are a medical care assistant. Create a structured post-surgery care plan with:
    1. Medication schedule with specific times
    2. Activity guidelines and restrictions
    3. Wound care instructions
    4. Warning signs to watch for
    5. Follow-up appointment reminders

    Make it practical and easy to follow.
    """

    document_content = """
    Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food.
    Take Amoxicillin 500mg three times daily for 7 days. Short walks recommended every 2 hours.
    No lifting over 10 pounds for 2 weeks. Follow-up appointment in 1 week.
    """

    payload = {
        "ai_command_text": care_plan_prompt,
        "content": document_content,
        "content_type": "MARKDOWN"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        care_plan_content = parse_sse_response(response.text)
        print("\n🎯 FINAL CARE PLAN:")
        print("🏥" + "=" * 60)
        print(care_plan_content)
        print("=" * 60)
        return care_plan_content
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return None

def test_question_answering(jwt_token, session_id):
    print("\n=== Testing Question Answering ===")

    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

    payload = {
        "ai_command_text": "Answer this patient question about post-surgery recovery. Be supportive and practical.",
        "content": "How much pain is normal after knee surgery and when should I be worried?",
        "content_type": "MARKDOWN"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        answer_content = parse_sse_response(response.text)
        print("\n💬 Q&A RESULT:")
        print("❓ Question: How much pain is normal after knee surgery?")
        print("🤖 Heidi AI Answer:")
        print("-" * 50)
        print(answer_content)
        print("-" * 50)
        return answer_content
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("🔧 Testing Heidi API with SSE Parsing...\n")

    jwt_token = get_jwt_token()
    session_id = create_session(jwt_token)

    print(f"✅ Setup complete - Session: {session_id}\n")

    # Test 1: Care plan generation
    care_plan = test_care_plan_generation(jwt_token, session_id)

    # Test 2: Question answering
    qa_result = test_question_answering(jwt_token, session_id)

    if care_plan and qa_result:
        print(f"\n🎉🎉🎉 SUCCESS! 🎉🎉🎉")
        print(f"✅ JWT Authentication: Working")
        print(f"✅ Session Creation: Working")
        print(f"✅ SSE Response Parsing: Working")
        print(f"✅ Care Plan Generation: Working")
        print(f"✅ Question Answering: Working")
        print(f"\n🚀 Ready to integrate into Flask app!")
    else:
        print(f"\n⚠️ Some features need debugging...")
# fixed_complete_test.py - With correct content_type
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "HEIDI_BASE_URL",
    "https://registrar.api.heidihealth.com/api/v2/ml-scribe/open-api",
)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and provide valid credentials."
        )
    return value


API_KEY = require_env("HEIDI_API_KEY")
EMAIL = require_env("HEIDI_EMAIL")
USER_ID = require_env("HEIDI_USER_ID")

def get_jwt_token():
    print("=== Step 1: Getting JWT Token ===")
    url = f"{BASE_URL}/jwt"

    headers = {"Heidi-Api-Key": API_KEY}
    params = {"email": EMAIL, "third_party_internal_id": USER_ID}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        token = response.json()["token"]
        print(f"✅ JWT Success!")
        return token
    else:
        print(f"❌ JWT Failed: {response.text}")
        return None

def create_session(jwt_token):
    print("\n=== Step 2: Creating Session ===")
    url = f"{BASE_URL}/sessions"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Heidi-Api-Key": API_KEY
    }

    payload = {"email": EMAIL, "third_party_internal_id": USER_ID}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        data = response.json()
        session_id = data.get("session_id")
        print(f"✅ Session Success! ID: {session_id}")
        return session_id
    else:
        print(f"❌ Session Failed: {response.text}")
        return None

def test_ask_ai_simple(jwt_token, session_id):
    print("\n=== Step 3: Testing Ask AI (Fixed) ===")
    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    # FIXED: Use "MARKDOWN" instead of "text"
    payload = {
        "ai_command_text": "Create a brief post-surgery care plan",
        "content": "Patient discharged after knee surgery. Needs medication schedule and activity guidance.",
        "content_type": "MARKDOWN"  # FIXED!
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("✅ Ask AI Success!")
        print("AI Response:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        return result
    else:
        print(f"❌ Ask AI Failed: {response.text}")
        return None

def demo_care_plan_generation(jwt_token, session_id):
    print("\n=== Step 4: Demo Care Plan Generation ===")
    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    care_plan_prompt = """
    You are a medical care assistant. Based on the following discharge document, create a structured post-surgery care plan.

    Please provide a helpful care plan with:
    1. Medication schedule and instructions
    2. Activity guidelines and restrictions
    3. Wound care instructions
    4. Warning signs to watch for
    5. Follow-up appointment reminders

    Make it clear, practical, and reassuring for a patient recovering at home.
    """

    document_content = """
    Patient discharged after knee surgery. Take Ibuprofen 400mg every 6 hours with food.
    Take Amoxicillin 500mg three times daily for 7 days. Short walks recommended every 2 hours.
    No lifting over 10 pounds for 2 weeks. Follow-up appointment in 1 week.
    Watch for fever over 101°F, redness, or unusual swelling around incision site.
    """

    payload = {
        "ai_command_text": care_plan_prompt,
        "content": document_content,
        "content_type": "MARKDOWN"  # FIXED!
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Care Plan Status: {response.status_code}")

    if response.status_code == 200:
        care_plan = response.json()
        print("✅ Care Plan Generated Successfully!")
        print("\n🎯 GENERATED CARE PLAN:")
        print("=" * 60)

        # Extract and display the response nicely
        if isinstance(care_plan, dict):
            if 'response' in care_plan:
                print(care_plan['response'])
            elif 'content' in care_plan:
                print(care_plan['content'])
            elif 'text' in care_plan:
                print(care_plan['text'])
            else:
                print(care_plan)
        else:
            print(care_plan)

        print("=" * 60)
        return care_plan
    else:
        print(f"❌ Care Plan Failed: {response.text}")
        return None

def test_question_answer(jwt_token, session_id):
    print("\n=== Step 5: Testing Question Answering ===")
    url = f"{BASE_URL}/sessions/{session_id}/ask-ai"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    medical_prompt = """
    You are a helpful post-surgery care assistant. Answer this patient question with:
    1. Supportive, reassuring tone
    2. Practical advice
    3. When to contact healthcare provider
    4. Keep it concise but helpful
    """

    patient_question = "How much pain is normal after knee surgery?"

    payload = {
        "ai_command_text": medical_prompt,
        "content": patient_question,
        "content_type": "MARKDOWN"
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Q&A Status: {response.status_code}")

    if response.status_code == 200:
        answer = response.json()
        print("✅ Question Answering Success!")
        print(f"\n❓ Question: {patient_question}")
        print("🤖 Heidi AI Answer:")
        print("-" * 40)

        if isinstance(answer, dict):
            if 'response' in answer:
                print(answer['response'])
            elif 'content' in answer:
                print(answer['content'])
            else:
                print(answer)
        else:
            print(answer)

        print("-" * 40)
        return answer
    else:
        print(f"❌ Q&A Failed: {response.text}")
        return None

if __name__ == "__main__":
    print("🧪 Testing COMPLETE Heidi API Flow (FIXED)...\n")

    # Step 1: Get JWT
    jwt_token = get_jwt_token()
    if not jwt_token:
        exit(1)

    # Step 2: Create Session
    session_id = create_session(jwt_token)
    if not session_id:
        exit(1)

    # Step 3: Test Ask AI (simple)
    ai_response = test_ask_ai_simple(jwt_token, session_id)

    # Step 4: Demo care plan generation
    care_plan = demo_care_plan_generation(jwt_token, session_id)

    # Step 5: Demo question answering
    qa_response = test_question_answer(jwt_token, session_id)

    if care_plan and qa_response:
        print(f"\n🎉🎉🎉 COMPLETE SUCCESS! 🎉🎉🎉")
        print(f"✅ JWT Authentication: Working")
        print(f"✅ Session Creation: Working")
        print(f"✅ Ask AI: Working")
        print(f"✅ Care Plan Generation: Working")
        print(f"✅ Question Answering: Working")
        print(f"\n🚀 Your Heidi API integration is FULLY READY!")
        print(f"\n📋 Demo Details:")
        print(f"   Session ID: {session_id}")
        print(f"   JWT Token: Valid for ~1 hour")
        print(f"   Content Type: Use 'MARKDOWN' for all requests")
        print(f"\n🎯 Ready to build your Flask demo!")
    else:
        print(f"\n⚠️ Some features need debugging...")

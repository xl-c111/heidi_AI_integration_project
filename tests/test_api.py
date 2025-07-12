import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.auth import get_jwt_token
from app.api.session import create_session
from app.api.ask_heidi import ask_ai_stream

def test_heidi_api():
    print("Testing Heidi API...")

    # Test 1: Get JWT
    print("1. Getting JWT token...")
    jwt = get_jwt_token()
    if 'Error' in str(jwt):
        print(f"❌ JWT Failed: {jwt}")
        return False
    print(f"✅ JWT Success: {jwt[:20]}...")

    # Test 2: Create Session
    print("2. Creating session...")
    session_id = create_session(jwt)
    if isinstance(session_id, dict) and session_id.get("error"):
        print(f"❌ Session Failed: {session_id}")
        return False
    print(f"✅ Session Success: {session_id}")

    # Test 3: Ask AI
    print("3. Testing Ask AI...")
    response = ask_ai_stream(
        jwt_token=jwt,
        session_id=session_id,
        ai_command_text="Create a simple medication reminder for a post-surgery patient",
        content="Patient needs pain management after knee surgery",
        content_type="text"
    )

    if response.get("error"):
        print(f"❌ Ask AI Failed: {response}")
        return False
    print(f"✅ Ask AI Success: {str(response)[:100]}...")

    print("\n🎉 All tests passed! Your Heidi API is working!")
    return True

if __name__ == "__main__":
    test_heidi_api()
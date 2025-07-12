# test_audio_feature.py - Test the complete audio workflow
import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:5000"

def test_audio_endpoint():
    """Test the audio transcription endpoint"""
    print("=== Testing Audio Transcription Endpoint ===")

    # Test with a small audio file (you can create a test wav file)
    test_file_path = "test_audio.wav"

    # Create a simple test audio file if it doesn't exist
    if not os.path.exists(test_file_path):
        print(f"Creating test audio file: {test_file_path}")
        # This creates a simple WAV file with silence - replace with actual audio file
        import wave
        import numpy as np

        # Create 3 seconds of silence at 16kHz
        sample_rate = 16000
        duration = 3  # seconds
        samples = np.zeros(int(sample_rate * duration), dtype=np.int16)

        with wave.open(test_file_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(samples.tobytes())

        print(f"✅ Created test audio file: {test_file_path}")

    # Test the transcription endpoint
    with open(test_file_path, 'rb') as audio_file:
        files = {'audio_file': audio_file}
        data = {'session_id': ''}  # Let it create a new session

        response = requests.post(f"{BASE_URL}/transcribe-audio", files=files, data=data)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Audio transcription endpoint working!")
                return result.get('session_id')
            else:
                print(f"❌ Transcription failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")

    return None

def test_complete_audio_workflow():
    """Test the complete audio workflow"""
    print("\n=== Testing Complete Audio Workflow ===")

    # Step 1: Test basic API connectivity
    try:
        response = requests.get(f"{BASE_URL}/test-jwt")
        if response.status_code == 200:
            print("✅ JWT endpoint working")
        else:
            print(f"❌ JWT endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure Flask server is running: python3 run.py")
        return False

    # Step 2: Test session creation
    try:
        response = requests.get(f"{BASE_URL}/test-session")
        if response.status_code == 200:
            print("✅ Session creation working")
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        return False

    # Step 3: Test audio transcription
    session_id = test_audio_endpoint()
    if session_id:
        print("✅ Audio transcription working")

        # Step 4: Test question answering with the session
        question_data = {
            'question': 'How much pain is normal after surgery?',
            'session_id': session_id
        }

        response = requests.post(f"{BASE_URL}/ask-question", json=question_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Question answering working")
                print(f"AI Response: {result.get('response', '')[:100]}...")
                return True
            else:
                print(f"❌ Question answering failed: {result.get('error')}")
        else:
            print(f"❌ Question endpoint failed: {response.status_code}")

    return False

def test_demo_page():
    """Test if the demo page loads"""
    print("\n=== Testing Demo Page ===")

    try:
        response = requests.get(f"{BASE_URL}/demo")
        if response.status_code == 200:
            if "Post-Surgery Care Assistant" in response.text:
                print("✅ Demo page loads correctly")
                print("✅ Audio features should be available")
                return True
            else:
                print("❌ Demo page content incorrect")
        else:
            print(f"❌ Demo page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Demo page test failed: {e}")

    return False

if __name__ == "__main__":
    print("🎤 Testing Audio Features for Post-Surgery Care Assistant\n")

    # Check environment
    required_env = ["HEIDI_API_KEY", "HEIDI_EMAIL", "HEIDI_USER_ID"]
    missing_env = [var for var in required_env if not os.getenv(var)]

    if missing_env:
        print(f"❌ Missing environment variables: {missing_env}")
        print("Please check your .env file")
        sys.exit(1)

    print("✅ Environment variables set")

    # Run tests
    demo_working = test_demo_page()
    workflow_working = test_complete_audio_workflow()

    print(f"\n🎯 FINAL RESULTS:")
    print(f"✅ Demo Page: {'Working' if demo_working else 'Failed'}")
    print(f"✅ Audio Workflow: {'Working' if workflow_working else 'Failed'}")

    if demo_working and workflow_working:
        print(f"\n🎉 SUCCESS! Audio features are ready!")
        print(f"🔗 Visit: {BASE_URL}/demo")
        print(f"🎤 You can now:")
        print(f"   • Record voice questions")
        print(f"   • Upload audio files")
        print(f"   • Get AI responses to spoken questions")
    else:
        print(f"\n⚠️ Some features need debugging")
        print(f"💡 Try running the Flask server: python3 run.py")
        print(f"💡 Check that all API credentials are correct")

    # Clean up test file
    if os.path.exists("test_audio.wav"):
        os.remove("test_audio.wav")
        print(f"🧹 Cleaned up test file")
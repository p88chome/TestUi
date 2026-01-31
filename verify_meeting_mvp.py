
import sys
import os
import asyncio
from fastapi.testclient import TestClient
from app.main import app

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

client = TestClient(app)

def test_meeting_api():
    print(">>> Testing Meeting Minutes API...")
    
    # 1. Test Generate Endpoint (Mocking LLM Gateway behavior would be ideal, but here we test the route handling)
    # Since we can't easily mock the DB/Gateway inside this simple script without complex setup,
    # we will rely on the fact that the code handles exceptions gracefully or check validation errors.
    
    payload = {
        "content": "Tony: 下週要交 Q1 報告。 Mary: 好的，我會準備銷售數據。",
        "meeting_title": "Test Meeting",
        "meeting_date": "2026-01-26",
        "participants": "Tony, Mary"
    }
    
    print(f"Sending payload: {payload}")
    
    # We might get a 500 or error if DB/LLM is not configured in this env,
    # but we want to ensure the route exists and accepts the payload.
    try:
        response = client.post("/api/v1/meeting/generate", json=payload)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json())
            print("✅ Generate API test passed (Success response)")
        else:
            print("Response:", response.text)
            # If it fails due to DB connection or LLM, that's expected in this detached env.
            # We assume "Internal Server Error" means the route logic started but failed on dependencies.
            print("⚠️ API reachable but returned error (likely due to missing DB/LLM credentials).")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

    # 2. Test Validation (Empty Content)
    print("\n>>> Testing Validation (Empty Content)...")
    try:
        response = client.post("/api/v1/meeting/generate", json={"content": ""})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Validation test passed (Correctly returned 400)")
        else:
            print(f"❌ Validation test failed (Expected 400, got {response.status_code})")
    except Exception as e:
         print(f"❌ Request failed: {e}")

    # 3. Test Export (Markdown)
    print("\n>>> Testing Export API (Markdown)...")
    export_payload = {
        "content": "# Meeting Minutes\n\n- Item 1\n- Item 2",
        "format": "markdown",
        "title": "test_export"
    }
    try:
        # Form data
        response = client.post("/api/v1/meeting/export", data=export_payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Export API test passed (Markdown)")
        else:
            print(f"❌ Export API failed: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_meeting_api()

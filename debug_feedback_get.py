import requests
import sys
import os

# Setup path to import app modules
sys.path.append(os.getcwd())

from app.core.security import create_access_token
from app.core.database import SessionLocal
from app.models.user import User
from app.models.feedback import Feedback

BASE_URL = "http://127.0.0.1:8000/api/v1"
EMAIL = "luiszhang@deloitte.com.tw"

def test_feedback_get():
    db = SessionLocal()
    user = db.query(User).filter(User.email == EMAIL).first()
    if not user:
        print(f"User {EMAIL} not found!")
        return
        
    print(f"User found: {user.email} (Admin: {user.is_superuser})")
    
    # Create Token
    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET /feedback
    print("Testing GET /feedback...")
    try:
        r = requests.get(f"{BASE_URL}/feedback", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f"GET Success! Count: {len(data)}")
            if len(data) > 0:
                print(f"First item: {data[0]}")
        else:
            print(f"GET Failed: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"GET Error: {e}")

if __name__ == "__main__":
    test_feedback_get()

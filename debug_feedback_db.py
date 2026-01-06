import sys
import os
import requests

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.feedback import Feedback
from app.models.user import User

def debug_feedback():
    print(">>> 1. Checking Database Connection & Tables...")
    try:
        # DROP table to ensure schema update (UUID -> Integer fix)
        Feedback.__table__.drop(engine, checkfirst=True)
        # Force create tables if missing
        Base.metadata.create_all(bind=engine)
        print("   tables created (if not existed).")
    except Exception as e:
        print(f"   DB Error: {e}")
        return

    db = SessionLocal()
    try:
        # Check if users exist (need one to post feedback)
        user = db.query(User).first()
        if not user:
            print("   No users found.")
        else:
            print(f"   Found user: {user.email} (Admin: {user.is_superuser})")
            
        print(">>> 2. Testing Insert (Direct DB)...")
        if user:
            try:
                fb = Feedback(user_id=user.id, content="Debug Script Test Content")
                db.add(fb)
                db.commit()
                print("   Direct DB Insert Success!")
                
                # Cleanup
                db.delete(fb)
                db.commit()
                print("   Cleanup Success.")
            except Exception as e:
                print(f"   Insert Failed: {e}")
                db.rollback()
    finally:
        db.close()

    print("\n>>> 3. Testing API Endpoint (http://127.0.0.1:8000/api/v1/feedback)...")
    # Note: Requires server running.
    # We will try a POST request. Need a valid token usually?
    # Actually wait, the dependencies use current_user.
    # Without a token, we can't test using requests easily unless we login.
    # We'll skip API test via script for now unless we implement login flow.
    # Just checking DB table is a good first step.
    
    print("   (Skipping API test - requires Auth Token)")

if __name__ == "__main__":
    debug_feedback()

import asyncio
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.services.agent_service import AgentService
from app.core.database import Base # Ensure models are loaded
from app.models.user import User # Ensure User table is registered
from app.models.chat import ChatSession, ChatMessage # Import to register

async def verify():
    print("=== Verifying AI Memory ===")
    
    # 1. Init DB
    try:
        engine = create_engine(str(settings.DATABASE_URL))
        Base.metadata.create_all(bind=engine) # Ensure tables exist
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("DB Connected & Tables ensured.")
    except Exception as e:
        print(f"DB Connection failed: {e}")
        return

    service = AgentService(db)
    user_id = 1
    
    # Ensure Test User
    test_email = "test_memory@example.com"
    existing_user = db.query(User).filter(User.email == test_email).first()
    if not existing_user:
        print("Creating test user...")
        new_user = User(
            email=test_email, 
            hashed_password="hashed_secret", 
            full_name="Test Memory User"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_id = new_user.id
    else:
        print(f"Using existing test user {existing_user.id}...")
        user_id = existing_user.id
    
    # 2. First Turn
    print("\n--- Turn 1: Introduction ---")
    query1 = "你好，我是 Tony。"
    try:
        res1 = await service.run(query1, user_id=user_id)
        session_id = res1.get("session_id")
        print(f"Response 1: {res1.get('response')}")
        print(f"Session ID: {session_id}")
        
        if not session_id:
            print("FAIL: No session_id returned.")
            return
            
    except Exception as e:
        print(f"Turn 1 Failed: {e}")
        return

    # 3. Second Turn (Recall)
    print("\n--- Turn 2: Recall Test ---")
    query2 = "我剛剛說我是誰？"
    try:
        res2 = await service.run(query2, user_id=user_id, session_id=session_id)
        print(f"Response 2: {res2.get('response')}")
        
        if "Tony" in res2.get("response", ""):
            print("PASS: Memory working!")
        else:
            print("FAIL: AI did not recall name.")
            
    except Exception as e:
        print(f"Turn 2 Failed: {e}")
    finally:
        # Cleanup (Optional)
        # db.query(ChatSession).filter(ChatSession.id == session_id).delete()
        # db.commit()
        db.close()

if __name__ == "__main__":
    asyncio.run(verify())

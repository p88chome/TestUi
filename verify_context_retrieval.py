import asyncio
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.services.agent_service import AgentService
from app.core.database import Base
from app.models.user import User

async def verify():
    print("=== Verifying Context Retrieval with Tools ===")
    
    # 1. Init DB
    try:
        engine = create_engine(str(settings.DATABASE_URL))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("DB Connected.")
    except Exception as e:
        print(f"DB Connection failed: {e}")
        return

    service = AgentService(db)
    user_id = 1
    
    # Ensure Test User
    test_email = "test_memory_tool@example.com"
    existing_user = db.query(User).filter(User.email == test_email).first()
    if not existing_user:
        new_user = User(email=test_email, hashed_password="pw", full_name="Test Tool User")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_id = new_user.id
    else:
        user_id = existing_user.id
    
    session_id = None

    # Turn 1: Identity
    print("\n--- Turn 1: Introduction (I am Tony) ---")
    try:
        res1 = await service.run("你好，我是 Tony。", user_id=user_id)
        session_id = res1.get("session_id")
        print(f"Response: {res1.get('response')}")
    except Exception as e:
        print(f"Turn 1 Error: {e}")
        return

    # Turn 2: Tool Usage (Math)
    print("\n--- Turn 2: Tool Usage (15 + 24) ---")
    try:
        res2 = await service.run("15 + 24 等於多少？", user_id=user_id, session_id=session_id)
        print(f"Tool Used: {res2.get('tool_used')}")
        print(f"Response: {res2.get('response')}")
        
        # We don't strictly require tool usage here for the memory test, but it helps simulate the user scenario
        # If no SymPy, the LLM might just calculate it. 
        # But provided "Used skill: sympy" was in user logs, it should use it.
    except Exception as e:
        print(f"Turn 2 Error: {e}")

    # Turn 3: Recall
    print("\n--- Turn 3: Recall (Who am I?) ---")
    try:
        res3 = await service.run("我剛剛說我是誰？", user_id=user_id, session_id=session_id)
        response_text = res3.get("response", "")
        print(f"Response: {response_text}")
        
        if "Tony" in response_text:
            print("[SUCCESS] Memory persisted through tool usage!")
        else:
            print("[FAILURE] Memory lost.")
            
    except Exception as e:
        print(f"Turn 3 Error: {e}")

    db.close()

if __name__ == "__main__":
    asyncio.run(verify())

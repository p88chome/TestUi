from app.core.database import SessionLocal
from app.services.agent_service import AgentService
import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

async def test():
    print("Starting Agent Debug...")
    db = SessionLocal()
    try:
        service = AgentService(db)
        # The user query that failed
        query = "請幫我解這個微積分：積分 x^3 + cos(x)"
        print(f"Query: {query}")
        
        # We need to see the printed debug info from AgentService
        # AgentService has print statements now
        
        # Pass a fake user_id (assuming 1 exists or it doesn't matter for logging failure)
        # Actually user_id is just for logging, it might fail if user 1 doesn't exist depending on FK?
        # UsageLog usually requires valid user_id.
        # Let's check if we can get a valid user.
        from app.models.user import User
        user = db.query(User).first()
        user_id = user.id if user else 1
        
        print(f"Using User ID: {user_id}")
        
        result = await service.run(query, user_id=user_id)
        print("\n--- FINAL RESULT ---")
        print(result)
        
    except Exception as e:
        print("\n--- ERROR ---")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test())

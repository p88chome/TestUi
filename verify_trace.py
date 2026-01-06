import asyncio
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.services.agent_service import AgentService
from app.services.skill_loader import load_skills
from app.core.database import Base
from app.models.user import User
from app.models.chat import ChatMessage
from app.models.skill import SkillExecution
from app.models.stats import UsageLog

async def verify():
    print("=== Verifying Observability (Trace ID) ===")
    
    # 1. Update Schema Manually (Mock Auto-Migration)
    engine = create_engine(str(settings.DATABASE_URL))
    
    # Simple rigorous migration (Safe for sqlite/dev pg, not prod)
    # We will try to add columns if not exist. 
    # But since we use SQL, let's just use raw connection or assume user creates new db or we rely on create_all works for new tables, 
    # but for existing tables we need ALTER.
    # For this verification script, let's just run SQL directly.
    
    from sqlalchemy import text # Import text

    with engine.connect() as conn:
        print("Migrating DB schema...")
        # 1. Chat Messages
        try:
            conn.execute(text("ALTER TABLE chat_messages ADD COLUMN trace_id VARCHAR"))
            conn.commit()
            print("Added trace_id to chat_messages.")
        except Exception as e:
            print(f"Skipping chat_messages update (might exist): {e}")
            
        # 2. Usage Logs
        try:
            conn.execute(text("ALTER TABLE usage_logs ADD COLUMN trace_id VARCHAR"))
            conn.commit()
            print("Added trace_id to usage_logs.")
        except Exception as e:
            print(f"Skipping usage_logs update (might exist): {e}")
            
        # 3. Skill Executions
        try:
            conn.execute(text("ALTER TABLE skill_executions ADD COLUMN trace_id VARCHAR"))
            conn.commit()
            print("Added trace_id to skill_executions.")
        except Exception as e:
            print(f"Skipping skill_executions update (might exist): {e}")
            
        print("Schema ensured.")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Load Skills
    load_skills(db)

    service = AgentService(db)
    user_id = 1 # Test user
    
    print("\n--- Sending Request (Triggers Tool) ---")
    query = "列出所有可用技能"
    
    try:
        res = await service.run(query, user_id=user_id)
        trace_id = res.get("trace_id")
        tool_used = res.get("tool_used")
        print(f"Request Finished. Trace ID: {trace_id}")
        print(f"Tool Used: {tool_used}")
        print(f"Response: {res.get('response')}")
        
        if not trace_id:
            print("FAIL: No trace_id returned from AgentService.")
            return

        print("\n--- Verifying Logs ---")
        
        # 1. Verify User Message
        user_msg = db.query(ChatMessage).filter(ChatMessage.trace_id == trace_id, ChatMessage.role == "user").first()
        if user_msg:
            print(f"[PASS] ChatMessage (User) Linked: {user_msg.id}")
        else:
            print(f"[FAIL] ChatMessage (User) NOT Linked.")

        # 2. Verify Assistant Message
        asst_msg = db.query(ChatMessage).filter(ChatMessage.trace_id == trace_id, ChatMessage.role == "assistant").first()
        if asst_msg:
            print(f"[PASS] ChatMessage (Assistant) Linked: {asst_msg.id}")
        else:
            print(f"[FAIL] ChatMessage (Assistant) NOT Linked.")
            
        # 3. Verify Usage Log
        usage = db.query(UsageLog).filter(UsageLog.trace_id == trace_id).first()
        if usage:
            print(f"[PASS] UsageLog Linked: {usage.id} (Tokens: {usage.total_tokens})")
        else:
            print(f"[FAIL] UsageLog NOT Linked.")
            
        # 4. Verify Skill Execution (SymPy)
        skill_exec = db.query(SkillExecution).filter(SkillExecution.trace_id == trace_id).first()
        if skill_exec:
            print(f"[PASS] SkillExecution Linked: {skill_exec.id} (Skill: {skill_exec.skill_name})")
        else:
            print(f"[FAIL] SkillExecution NOT Linked (Maybe SymPy wasn't called?).")

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify())

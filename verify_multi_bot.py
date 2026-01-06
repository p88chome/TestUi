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
from app.models.chat import ChatSession
from app.models.assistant import Assistant
from app.models.skill import Skill

async def setup_bots(db):
    print("Setting up bots...")
    
    # 1. Get Skills
    skills = db.query(Skill).all()
    skill_map = {s.name: s for s in skills}
    
    # 2. Create Legal Bot
    legal_bot = db.query(Assistant).filter(Assistant.id == "legal_bot").first()
    if not legal_bot:
        legal_bot = Assistant(
            id="legal_bot",
            name="Legal Assistant",
            description="Specialist in contracts and legal documents.",
            instruction="You are a Legal Assistant. Only answer legal questions. Be formal."
        )
        db.add(legal_bot)
        
    # Assign Skills
    legal_skills = ["legal_contract_review", "docx_writer", "pdf_manager"]
    legal_bot.skills = [skill_map[s] for s in legal_skills if s in skill_map]
    
    # 3. Create Finance Bot
    finance_bot = db.query(Assistant).filter(Assistant.id == "finance_bot").first()
    if not finance_bot:
        finance_bot = Assistant(
            id="finance_bot",
            name="Finance Assistant",
            description="Specialist in finance and spreadsheets.",
            instruction="You are a Finance Assistant. Only answer financial questions. Be precise."
        )
        db.add(finance_bot)

    # Assign Skills
    finance_skills = ["excel_handler", "pdf_manager"]
    finance_bot.skills = [skill_map[s] for s in finance_skills if s in skill_map]
    
    db.commit()
    print("Bots setup complete.")
    return legal_bot, finance_bot

async def verify():
    print("=== Verifying Multi-Bot ===")
    
    try:
        engine = create_engine(str(settings.DATABASE_URL))
        Base.metadata.create_all(bind=engine)
        
        # Manual Migration for existing table
        with engine.connect() as conn:
            from sqlalchemy import text
            try:
                conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN assistant_id VARCHAR"))
                conn.commit()
                print("Migrated: Added assistant_id to chat_sessions")
            except Exception as e:
                # Ignore if exists
                print(f"Migration note: {e}")
                
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("DB Connected.")
    except Exception as e:
        print(f"DB Connection failed: {e}")
        return

    # Setup
    await setup_bots(db)
    
    # Ensure User
    user_id = 1
    test_user = db.query(User).filter(User.id == user_id).first()
    if not test_user:
         # Create dummy if cleaned up
         pass 

    service = AgentService(db)
    
    # Test 1: Legal Bot doing Legal Task
    print("\n--- Test 1: Legal Bot Reviewing Contract ---")
    query1 = "我要審審這份NDA合約，請確認有無風險"
    # We deliberately don't give content to trigger 'tool: none' but 'explanation' response
    # Or, we ask "What skills do you have?" to see if it lists only legal skills.
    query1 = "列出你會的技能" 
    
    res1 = await service.run(query1, user_id=user_id, assistant_id="legal_bot")
    print(f"Legal Bot Answer: {res1.get('response')}")
    
    # Expectation: Only legal skills listed
    
    # Test 2: Finance Bot doing Legal Task (Should Fail/Chat)
    print("\n--- Test 2: Finance Bot Reviewing Contract ---")
    query2 = "幫我審閱合約"
    res2 = await service.run(query2, user_id=user_id, assistant_id="finance_bot")
    print(f"Finance Bot Answer: {res2.get('response')}")
    
    # Expectation: Should say it can't or doesn't have the tool
    
    db.close()

if __name__ == "__main__":
    asyncio.run(verify())

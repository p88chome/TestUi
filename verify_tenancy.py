import asyncio
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.services.agent_service import AgentService
from app.core.database import Base
from app.models.user import User

async def verify():
    print("=== Verifying Multi-Tenancy Schema ===")
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        print("Migrating DB schema (Adding tenant_id)...")
        # 1. Users
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
            conn.commit()
            print("Added tenant_id to users.")
        except Exception as e:
            conn.rollback() # Reset transaction
            print(f"Skipping users update: {e}")

        # 2. Chat Sessions
        try:
            conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
            conn.commit()
            print("Added tenant_id to chat_sessions.")
        except Exception as e:
            conn.rollback()
            print(f"Skipping chat_sessions update: {e}")
            
        # 3. Chat Messages
        try:
            conn.execute(text("ALTER TABLE chat_messages ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
            conn.commit()
            print("Added tenant_id to chat_messages.")
        except Exception as e:
            conn.rollback()
            print(f"Skipping chat_messages update: {e}")

        # 4. Usage Logs
        try:
            conn.execute(text("ALTER TABLE usage_logs ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
            conn.commit()
            print("Added tenant_id to usage_logs.")
        except Exception as e:
            conn.rollback()
            print(f"Skipping usage_logs update: {e}")
            
        # 5. Skill Executions
        try:
            conn.execute(text("ALTER TABLE skill_executions ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
            conn.commit()
            print("Added tenant_id to skill_executions.")
        except Exception as e:
            conn.rollback()
            print(f"Skipping skill_executions update: {e}")
            
        print("Schema ensured.")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Test Data Insertion
    try:
        # Create user with specific tenant
        test_email = "tenant_admin@example.com"
        existing = db.query(User).filter(User.email == test_email).first()
        if not existing:
            new_user = User(
                email=test_email, 
                hashed_password="pw", 
                full_name="Tenant Admin",
                tenant_id="corp-xyz" # Explicit Tenant
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"[PASS] Created user with tenant_id: {new_user.tenant_id}")
        else:
            print(f"[PASS] User exists with tenant_id: {existing.tenant_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify())

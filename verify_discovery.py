import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.services.skill_loader import load_skills, execute_skill
from app.core.database import Base

def verify():
    print("=== Verifying Skill Discovery ===")
    
    # 1. Init DB connection
    # Assuming connection string is valid in settings
    try:
        engine = create_engine(str(settings.DATABASE_URL))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("DB Connected.")
    except Exception as e:
        print(f"DB Connection failed: {e}")
        return

    # 2. Load Skills (Register new skill)
    print("Loading skills...")
    try:
        load_skills(db)
        print("Skills loaded.")
    except Exception as e:
        print(f"Load skills failed: {e}")
        db.close()
        return

    # 3. Test list_available_skills
    print("Executing 'list_available_skills'...")
    try:
        result = execute_skill("list_available_skills", {"filter": ""}, db)
        print(f"Result: {result}")
        
        if result and "skills" in result and len(result["skills"]) > 0:
            print("PASS: Successfully retrieved skills list.")
            # Check if 'pdf' is in there
            names = [s['name'] for s in result['skills']]
            if "pdf_manager" in names and "list_available_skills" in names:
                print("PASS: Found expected skills.")
            else:
                print(f"WARNING: Expected skills missing. Found: {names}")
        else:
            print("FAIL: Result empty or invalid format.")
            
    except Exception as e:
        print(f"FAIL: Execution error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()

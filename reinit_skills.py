from app.core.database import SessionLocal
from app.services.skill_loader import load_skills
import sys
import os

sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("Reloading skills...")
    db = SessionLocal()
    try:
        load_skills(db)
        print("Skills reloaded successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

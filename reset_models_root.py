import sys
import os

# Add current dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.domain import AIModel

def reset_models():
    db = SessionLocal()
    try:
        # 1. Delete all existing models
        db.query(AIModel).delete()
        db.commit()
        print("Cleared all AI Models.")

        # 2. Add only GPT-4.1
        gpt4 = AIModel(
            name="GPT-4.1", 
            deployment_name="gpt-4.1", 
            api_version="2024-12-01-preview", 
            is_active=True
        )
        db.add(gpt4)
        db.commit()
        print(f"Added Model: {gpt4.name} (Active)")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_models()

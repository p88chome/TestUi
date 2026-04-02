import logging
import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models.domain import AIModel, LLMProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    db = SessionLocal()
    try:
        logger.info("Dropping old ai_models table to sync schema...")
        # Since we are in dev, we drop and recreate to handle schema changes easily
        db.execute(text("DROP TABLE IF EXISTS ai_models CASCADE"))
        db.commit()

        logger.info("Creating new ai_models table with updated schema...")
        # Re-create all tables that don't exist (this will recreate ai_models)
        Base.metadata.create_all(bind=engine)

        logger.info("Seeding initial models...")
        models_data = [
            {
                "name": "GPT-4.1 (Azure)",
                "provider": LLMProvider.AZURE,
                "deployment_name": "gpt-4.1",
                "api_version": "2024-12-01-preview",
                "description": "Standard Azure OpenAI GPT-4.1",
                "is_active": True,
                "is_reasoning_model": False,
            },
            {
                "name": "GPT-4.5 (Azure)",
                "provider": LLMProvider.AZURE,
                "deployment_name": "gpt-4.5",
                "api_version": "2024-12-01-preview",
                "description": "Latest Azure OpenAI GPT-4.5",
                "is_active": False,
                "is_reasoning_model": False,
            },
            {
                "name": "Gemini 1.5 Flash (Google)",
                "provider": LLMProvider.GOOGLE,
                "model_name": "gemini-1.5-flash",
                "description": "Google Gemini 1.5 Flash via AI Studio",
                "is_active": False,
                "is_reasoning_model": False,
            }
        ]

        for m in models_data:
            db_model = AIModel(**m)
            db.add(db_model)
        
        db.commit()
        logger.info("Migration and Seeding completed successfully!")
        print("\n✅ 資料庫已同步！現在重新進入頁面就不會看到 'Failed to load model' 了。")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

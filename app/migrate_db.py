import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.core.database import engine
import logging

logger = logging.getLogger(__name__)

def migrate():
    print("Migrating database to add plan columns...")
    print("Migrating database to add plan columns...")
    
    # plan_name
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("ALTER TABLE users ADD COLUMN plan_name VARCHAR DEFAULT 'Starter'"))
                print("Added column plan_name")
    except Exception as e:
        print(f"Skipping plan_name: {e}")

    # plan_price
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("ALTER TABLE users ADD COLUMN plan_price VARCHAR DEFAULT 'Free'"))
                print("Added column plan_price")
    except Exception as e:
        print(f"Skipping plan_price: {e}")

    # plan_expiry
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("ALTER TABLE users ADD COLUMN plan_expiry VARCHAR"))
                print("Added column plan_expiry")
    except Exception as e:
        print(f"Skipping plan_expiry: {e}")

    # tenant_id (Critical for multi-tenancy)
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("ALTER TABLE users ADD COLUMN tenant_id VARCHAR DEFAULT 'default'"))
                connection.execute(text("CREATE INDEX ix_users_tenant_id ON users (tenant_id)"))
                print("Added column tenant_id")
    except Exception as e:
        print(f"Skipping tenant_id: {e}")

    # components configuration
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("ALTER TABLE components ADD COLUMN configuration JSONB DEFAULT '{}'"))
                print("Added column configuration to components")
    except Exception as e:
        # Fallback for SQLite or if JSONB not supported/other error
        try:
             with engine.connect() as connection:
                with connection.begin():
                    connection.execute(text("ALTER TABLE components ADD COLUMN configuration JSON DEFAULT '{}'"))
                    print("Added column configuration to components (JSON)")
        except Exception as e2:
             print(f"Skipping components configuration: {e} | {e2}")
                
    # 3. Add configuration column to components if not exists
    # ... existing code ...
    
    # 4. Add skill_id to components
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("ALTER TABLE components ADD COLUMN skill_id UUID"))
                print("Added column skill_id to components")
    except Exception as e:
        print(f"Skipping skill_id: {e}")

    with engine.connect() as conn:
        # Check if ai_models table exists
        result = conn.execute(text("SELECT to_regclass('public.ai_models')"))
        if not result.scalar():
            logger.info("Creating ai_models table...")
            # We can use Base.metadata.create_all for this table specifically if we import it, 
            # or just rely on global create_all in main.py. 
            # But let's be safe and let main.py handle it via Base.metadata.create_all(bind=engine)
            # which is called in app.main startup.
            # So actual migration here is only needed for ALTERing existing tables.
            # Since this is a NEW table, Base.metadata.create_all in main.py will handle it if it doesn't exist.
            pass
        
    logger.info("Migration check completed (New tables handled by startup event)")

    print("Migration complete.")

if __name__ == "__main__":
    migrate()

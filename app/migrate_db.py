import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.core.database import engine

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
                
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

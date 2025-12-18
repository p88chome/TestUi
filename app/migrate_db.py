import os
import sys

# Ensure app is in path
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.core.database import engine

def migrate():
    print("Migrating database to add plan columns...")
    with engine.connect() as connection:
        with connection.begin():
            # Check and add plan_name
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN plan_name VARCHAR DEFAULT 'Starter'"))
                print("Added column plan_name")
            except Exception as e:
                print(f"Skipping plan_name (probably exists): {e}")

            # Check and add plan_price
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN plan_price VARCHAR DEFAULT 'Free'"))
                print("Added column plan_price")
            except Exception as e:
                print(f"Skipping plan_price (probably exists): {e}")

            # Check and add plan_expiry
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN plan_expiry VARCHAR"))
                print("Added column plan_expiry")
            except Exception as e:
                print(f"Skipping plan_expiry (probably exists): {e}")
                
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

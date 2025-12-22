
from app.core.database import SessionLocal
from app.models.domain import AIModel
from app.models.user import User

def check_data():
    db = SessionLocal()
    try:
        print("--- AI Models ---")
        models = db.query(AIModel).all()
        for m in models:
            print(f"ID: {m.id} | Name: {m.name} | Active: {m.is_active} | Deployment: {m.deployment_name}")

        print("\n--- Users (Admin Check) ---")
        users = db.query(User).all()
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Superuser: {u.is_superuser} | Active: {u.is_active}")

    finally:
        db.close()

if __name__ == "__main__":
    check_data()

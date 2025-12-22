
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.stats import UsageLog
from app.models.user import User
from app.models.domain import Component, Workflow, RunExecution
from sqlalchemy import func

def debug_stats():
    db = SessionLocal()
    try:
        print("--- Debugging Token Usage Stats ---")
        
        # 1. Check Use Logs
        logs = db.query(UsageLog).all()
        print(f"\n[UsageLogs] Count: {len(logs)}")
        for log in logs:
            print(f"  - ID: {log.id}, UserID: {log.user_id}, App: {log.app_name}, Tokens: {log.total_tokens}, Cost: {log.estimated_cost}")

        # 2. Check Users
        users = db.query(User).all()
        print(f"\n[Users] Count: {len(users)}")
        for u in users:
            print(f"  - ID: {u.id}, Email: {u.email}")

        # 3. Check Components (Contract Helper)
        comp = db.query(Component).filter(Component.name == "Contract Helper").first()
        if comp:
            print(f"\n[Component: Contract Helper]")
            print(f"  - ID: {comp.id}")
            print(f"  - Kind: {comp.configuration.get('kind')}")
            print(f"  - Config: {comp.configuration}")
        else:
            print("\n[Component: Contract Helper] NOT FOUND")

        # 4. Check Recent Runs
        runs = db.query(RunExecution).order_by(RunExecution.started_at.desc()).limit(5).all()
        print(f"\n[Recent Runs] Count: {len(runs)}")
        for r in runs:
            print(f"  - ID: {r.id}, Status: {r.status}, Finished: {r.finished_at}")
            # Check if there are logs in the run
            if r.log:
                print(f"    - Steps: {len(r.log)}")
                for step in r.log:
                    print(f"      - Step: {step.get('component')}, Status: {step.get('status')}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_stats()

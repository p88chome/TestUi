import sys
import os

# Ensure current directory is in path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.stats import UsageLog
from app.models.user import User
from app.models.domain import Component, Workflow, RunExecution
from app.models.news import PlatformNews
from sqlalchemy import func

def debug_stats():
    # Ensure tables exist
    print("Checking DB Schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("--- Debugging Token Usage Stats ---")
        
        # 0. Check Platform News
        news = db.query(PlatformNews).all()
        print(f"\n[Platform News] Count: {len(news)}")
        for n in news:
            print(f"  - [{n.id}] {n.title} (Published: {n.is_published})")
        
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

        # 3.5 Check Workflows
        workflows = db.query(Workflow).all()
        print(f"\n[Workflows] Count: {len(workflows)}")
        for w in workflows:
            print(f"  - Workflow: {w.name} (ID: {w.id})")
            for step in w.steps:
                # Resolve component name
                comp = db.query(Component).filter(Component.id == step.get('component_id')).first()
                comp_name = comp.name if comp else "Unknown"
                print(f"    - Step {step.get('step_id')}: {comp_name} (CompID: {step.get('component_id')})")

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

    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_stats()

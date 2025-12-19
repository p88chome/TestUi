import sys
import os
import json
from uuid import UUID

# Ensure root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.core.database import SessionLocal
from app.models.domain import RunExecution

def main():
    db = SessionLocal()
    try:
        # Get latest run
        run = db.query(RunExecution).order_by(RunExecution.started_at.desc()).first()
        if not run:
            print("No runs found")
            return
            
        print(f"Run ID: {run.id}")
        print(f"Run Status: {run.status}")
        print(f"Input Payload: {json.dumps(run.input_payload, indent=2, default=str)}")
        print("LOGS:")
        print(json.dumps(run.log, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

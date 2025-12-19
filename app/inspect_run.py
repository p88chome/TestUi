import sys
import os
import json
from uuid import UUID

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.domain import RunExecution

def main():
    db = SessionLocal()
    run_id = "5a3a852d-9df4-4fab-aaf1-e731499d3538"
    try:
        run = db.query(RunExecution).filter(RunExecution.id == UUID(run_id)).first()
        if not run:
            print(f"Run {run_id} not found")
            return
            
        print(f"Run Status: {run.status}")
        print("LOGS:")
        print(json.dumps(run.log, indent=2, default=str))
    except Exception as e:
        print(e)
    finally:
        db.close()

if __name__ == "__main__":
    main()

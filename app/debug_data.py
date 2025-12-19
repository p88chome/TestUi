import sys
import os
import logging
from uuid import UUID

# Ensure app is in path (Robust way)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.domain import Workflow, RunExecution, Component

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_data(workflow_id_str):
    db = SessionLocal()
    try:
        # 1. Check Workflow
        print(f"--- Checking Workflow {workflow_id_str} ---")
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id_str).first()
        if not workflow:
            print("Workflow NOT FOUND")
        else:
            print(f"Name: {workflow.name}")
            print(f"Steps Count: {len(workflow.steps)}")
            print(f"Steps Content: {workflow.steps}")
            
            # Verify components exist
            for step in workflow.steps:
                comp_id = step.get('component_id')
                comp = db.query(Component).filter(Component.id == comp_id).first()
                print(f"  Step {step.get('step_id')}: Component {comp_id} -> {'Found: ' + comp.name if comp else 'MISSING'}")

        # 2. Check Latest Run
        print(f"\n--- Checking Latest Run for Workflow ---")
        run = db.query(RunExecution).filter(RunExecution.workflow_id == workflow_id_str).order_by(RunExecution.started_at.desc()).first()
        if not run:
            print("No runs found")
        else:
            print(f"Run ID: {run.id}")
            print(f"Status: {run.status}")
            print(f"Input Payload: {run.input_payload}")
            print(f"Logs Count: {len(run.log)}")
            print(f"Logs Content: {run.log}")
            print(f"Output: {run.output_payload}")

    finally:
        db.close()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        if len(sys.argv) > 1:
            wf_id = sys.argv[1]
            debug_data(wf_id)
        else:
            print("\n--- Listing All Workflows ---")
            wfs = db.query(Workflow).all()
            for wf in wfs:
                print(f"ID: {wf.id} | Name: {wf.name} | Steps: {len(wf.steps)}")
                
            print("\n--- Latest Run ---")
            run = db.query(RunExecution).order_by(RunExecution.started_at.desc()).first()
            if run:
                 print(f"Run ID: {run.id} | Status: {run.status} | Workflow: {run.workflow_id}")
                 print(f"Logs: {run.log}")
            else:
                 print("No runs found.")
    finally:
        db.close()

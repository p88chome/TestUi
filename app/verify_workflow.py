import sys
import os
import logging
from uuid import uuid4

# Ensure app is in path (Robust way)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.domain import Component, Workflow
from app.services.workflow_engine import WorkflowEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify():
    db = SessionLocal()
    try:
        # 1. Fetch Components
        aiocr = db.query(Component).filter(Component.name == "AIOCR Component").first()
        contract_helper = db.query(Component).filter(Component.name == "Contract Helper").first()
        
        if not aiocr or not contract_helper:
            logger.error("Components not found! Did you run initial_data.py?")
            return

        # 2. Create Test Workflow
        workflow_name = f"Test Flow {uuid4().hex[:8]}"
        steps = [
            {
                "step_id": "step_1",
                "component_id": str(aiocr.id),
                "config": {}, # No override
            },
            {
                "step_id": "step_2",
                "component_id": str(contract_helper.id),
                "config": {}
            }
        ]
        
        workflow = Workflow(
            name=workflow_name,
            description="Auto-generated test workflow",
            steps=steps
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        logger.info(f"Created Workflow: {workflow.name} (ID: {workflow.id})")

        # 3. Run Workflow
        engine = WorkflowEngine(db)
        input_payload = {"image_url": "http://example.com/contract.jpg"}
        
        logger.info("Starting Workflow Execution...")
        run = engine.run_workflow(workflow.id, input_payload)
        
        logger.info(f"Execution Finished. Status: {run.status}")
        logger.info(f"Final Output: {run.output_payload}")
        
        # 4. Verify Logs
        logger.info("\n--- Execution Logs ---")
        for log in run.log:
            step_id = log.get("step_id")
            comp = log.get("component")
            output = log.get("output")
            input_data = log.get("input")
            
            logger.info(f"Step: {step_id} ({comp})")
            logger.info(f"  Input: {input_data}")
            logger.info(f"  Output: {output}")
            
            # Validation Logic
            if step_id == "step_2":
                # Check if Step 2 received output from Step 1
                prev_out = input_data.get("prev_output")
                if prev_out and prev_out.get("mock") is True:
                     logger.info("  [PASS] Step 2 received previous output correctly.")
                else:
                     logger.error("  [FAIL] Step 2 did NOT receive previous output.")

    finally:
        db.close()

if __name__ == "__main__":
    verify()

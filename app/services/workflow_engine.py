from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.domain import Workflow, RunExecution, RunStatus, Component
from app.schemas.all import RunExecutionCreate
import json

class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_workflow(self, workflow_id: UUID, input_payload: dict) -> RunExecution:
        # 1. Fetch workflow
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # 2. Create RunExecution record
        run_record = RunExecution(
            workflow_id=workflow_id,
            status=RunStatus.RUNNING,
            input_payload=input_payload,
            log=[],
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(run_record)
        self.db.commit()
        self.db.refresh(run_record)

        try:
            # 3. Simulate execution step-by-step
            current_data = input_payload
            logs = []

            for step in workflow.steps:
                # step is a dict from JSONB: {'step_id', 'component_id', 'config', 'input_mapping'}
                step_idx = step.get('step_id')
                comp_id = step.get('component_id')
                config = step.get('config', {})
                
                # Fetch component (optional validation)
                component = self.db.query(Component).filter(Component.id == comp_id).first()
                comp_name = component.name if component else "Unknown Component"

                # Simulate executing component
                step_log = {
                    "step_id": step_idx,
                    "component": comp_name,
                    "status": "success",
                    "input": current_data,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

                # Setup mock output
                output_data = {
                    "mock": True,
                    "processed_by": comp_name,
                    "previous_input": current_data,
                    "config_used": config
                }
                
                step_log["output"] = output_data
                logs.append(step_log)
                
                # Pass output as input to next step (simplified mapping)
                current_data = output_data

            # 4. Finalize Success
            run_record.status = RunStatus.SUCCESS
            run_record.output_payload = current_data
            run_record.log = logs
            run_record.finished_at = datetime.now(timezone.utc)

        except Exception as e:
            # Handle Failure
            run_record.status = RunStatus.FAILED
            run_record.log = logs + [{"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}]
            run_record.finished_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(run_record)
        return run_record

def get_workflow_engine(db: Session):
    return WorkflowEngine(db)

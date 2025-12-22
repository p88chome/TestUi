from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.domain import Workflow, RunExecution, RunStatus, Component
from app.schemas.all import RunExecutionCreate
import json

class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_workflow(self, workflow_id: UUID, input_payload: dict, user_id: int | None = None) -> RunExecution:
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
            previous_step_output = {}
            logs = []

            for step in workflow.steps:
                # step is a dict: {'step_id', 'component_id', 'config', 'input_mapping'}
                step_idx = step.get('step_id')
                comp_id = step.get('component_id')
                
                # Fetch component
                component = self.db.query(Component).filter(Component.id == comp_id).first()
                if not component:
                    raise ValueError(f"Component {comp_id} not found")

                comp_name = component.name
                
                # Resolve Inputs
                # Structure: {"original_input": ..., "prev_output": ...}
                step_input = {
                    "original_input": input_payload,
                    "prev_output": previous_step_output
                }

                # Resolve Effective Input (Flattened for MVP usage)
                # This allows components to access keys directly like "image_path"
                effective_input = {}
                effective_input.update(input_payload)
                if isinstance(previous_step_output, dict):
                    effective_input.update(previous_step_output)

                # TODO: proper input validation based on step['input_mapping']

                # Execution
                start_time = datetime.now(timezone.utc)
                try:
                    output_data = self.execute_step(component, effective_input, user_id)
                    status = "success"
                    error_msg = None
                except Exception as step_e:
                    output_data = None
                    status = "failed"
                    error_msg = str(step_e)
                    # For MVP, we stop on failure
                    raise step_e

                step_log = {
                    "step_id": step_idx,
                    "component": comp_name,
                    "status": status,
                    "input": step_input,
                    "output": output_data,
                    "error": error_msg,
                    "timestamp": start_time.isoformat(),
                    "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                }
                logs.append(step_log)
                
                # Update for next step
                previous_step_output = output_data

            # 4. Finalize Success
            run_record.status = RunStatus.SUCCESS
            run_record.output_payload = previous_step_output
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

    def execute_step(self, component: Component, input_data: dict, user_id: int | None = None) -> dict:
        config = component.configuration or {}
        kind = config.get("kind")

        if kind == "http":
            import httpx
            url = config.get("url")
            method = config.get("method", "POST")
            headers = config.get("headers", {"Content-Type": "application/json"})
            
            if not url:
                raise ValueError("Missing URL in component configuration")

            if method.upper() == "POST":
                response = httpx.post(url, json=input_data, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            elif method.upper() == "GET":
                # For GET we might pass params? MVP assumes POST usually.
                response = httpx.get(url, params=input_data, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            else:
                raise ValueError(f"Unsupported method {method}")

        elif kind == "azure_openai":
            import httpx
            import os
            from app.models.domain import AIModel
            from app.models.stats import UsageLog

            # 1. Determine Model Info (Deployment & API Version)
            target_model_id = config.get("model_id")
            ai_model = None
            
            if target_model_id:
                ai_model = self.db.query(AIModel).filter(AIModel.id == target_model_id).first()
            
            if not ai_model:
                # Fallback to default active
                ai_model = self.db.query(AIModel).filter(AIModel.is_active == True).first()
            
            if not ai_model:
                raise ValueError("No AIModel configuration found (active or specified)")

            # 2. Get Credentials from Env (Security Best Practice)
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            
            if not api_key or not endpoint:
                raise ValueError("Missing AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT in environment")

            # 3. Construct URL
            endpoint = endpoint.rstrip('/')
            deployment = ai_model.deployment_name
            api_version = ai_model.api_version
            
            url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
            
            # 4. Prepare Payload
            req_payload = {}
            if "messages" in input_data:
                # Direct pass-through
                req_payload = input_data
            else:
                # Template mode
                user_content = input_data.get("prompt") or json.dumps(input_data)
                
                req_payload = {
                    "messages": [
                        {"role": "system", "content": config.get("system_prompt", "You are a helpful AI assistant.")},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": config.get("temperature", 0.7)
                }

            headers = {
                "Content-Type": "application/json",
                "api-key": api_key
            }

            response = httpx.post(url, json=req_payload, headers=headers, timeout=60.0)
            
            if response.status_code != 200:
                 raise ValueError(f"Azure API Error: {response.text}")
            
            json_response = response.json()

            # 5. Log Token Usage (if user_id provided)
            if user_id:
                usage = json_response.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                
                total_tokens = usage.get("total_tokens", 0)
                
                # Cost Estimation
                from app.core.cost_calculator import calculate_ai_cost
                estimated_cost = calculate_ai_cost(ai_model.name, prompt_tokens, completion_tokens)
                
                log_entry = UsageLog(
                    user_id=user_id,
                    app_name=component.name, # Use component name (e.g., "Contract Helper")
                    model_name=ai_model.name,
                    tokens_input=prompt_tokens,
                    tokens_output=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=estimated_cost
                )
                self.db.add(log_entry)
                self.db.commit()

            return json_response

        elif kind == "ocr_api":
            import httpx
            import os
            from pathlib import Path

            url = config.get("url")
            if not url:
                raise ValueError("Missing 'url' in configuration for OCR API")

            # Expecting input_data to have 'image_path'
            image_path_str = input_data.get("image_path") or input_data.get("image_url")
            if not image_path_str:
                debug_keys = list(input_data.keys())
                raise ValueError(f"Input must contain 'image_path' or 'image_url'. Received input keys: {debug_keys}")

            image_path = Path(image_path_str)
            if not image_path.exists():
                # Try relative to cwd
                image_path = Path(os.getcwd()) / image_path_str
                if not image_path.exists():
                     raise ValueError(f"Image file not found: {image_path_str}")

            # Prepare Multipart Upload
            # We use httpx synchronously here
            import mimetypes
            
            # Guess mime type based on extension
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                # Fallback defaults
                ext = image_path.suffix.lower()
                if ext == '.pdf':
                    mime_type = 'application/pdf'
                elif ext in ['.jpg', '.jpeg']:
                    mime_type = 'image/jpeg'
                elif ext == '.png':
                    mime_type = 'image/png'
                else:
                    mime_type = 'application/octet-stream'

            try:
                with open(image_path, 'rb') as f:
                    # 'file' is the key expected by the server
                    # tuple format: (filename, file_content, content_type)
                    files = {'file': (image_path.name, f, mime_type)} 
                    response = httpx.post(url, files=files, timeout=60.0)
                
                if response.status_code != 200:
                    raise ValueError(f"OCR API Error ({response.status_code}): {response.text}")
                
                return response.json()
            except Exception as e:
                raise ValueError(f"Failed to call OCR API: {str(e)}")

        elif kind == "mock":
            return config.get("payload", {})

        else:
            # Fallback or unknown
            return {"error": f"Unknown component kind: {kind}"}

def get_workflow_engine(db: Session):
    return WorkflowEngine(db)

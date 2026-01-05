from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.domain import Workflow, RunExecution, RunStatus, Component
from app.models.skill import Skill, SkillType
from app.schemas.all import RunExecutionCreate
import json

class WorkflowEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_workflow(self, workflow_id: UUID, input_payload: dict, user_id: int | None = None, task_package_id: UUID | None = None) -> RunExecution:
        # 1. Fetch workflow
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # 1.1 Fetch TaskPackage (Business Context) if provided
        manual_context = None
        task_package_name = None
        
        if task_package_id:
            from app.models.task import TaskPackage
            tp = self.db.query(TaskPackage).filter(TaskPackage.id == task_package_id).first()
            if tp and tp.manual_content:
                manual_context = tp.manual_content
                task_package_name = tp.name

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
            # 3. Dynamic Execution
            current_data = input_payload
            previous_step_output = {}
            logs = []
            
            # Map steps for random access
            # Valid steps format: list of dicts. We assume step_id is unique int.
            steps_map = {s.get('step_id'): s for s in workflow.steps}
            sorted_step_ids = sorted(steps_map.keys())
            
            if not sorted_step_ids:
                 pass # Empty workflow
            
            current_step_id = sorted_step_ids[0] if sorted_step_ids else None
            steps_run_count = 0
            MAX_STEPS = 50 # Prevent infinite loops

            while current_step_id is not None:
                if steps_run_count > MAX_STEPS:
                    raise RuntimeError("Workflow exceeded maximum step limit (infinite loop detection)")
                
                step = steps_map.get(current_step_id)
                if not step:
                    break # Should not happen if logic is correct

                steps_run_count += 1
                comp_id = step.get('component_id')
                
                # Fetch component
                component = self.db.query(Component).filter(Component.id == comp_id).first()
                if not component:
                    raise ValueError(f"Component {comp_id} not found")

                comp_name = component.name
                
                # Resolve Inputs
                step_input = {
                    "original_input": input_payload,
                    "prev_output": previous_step_output
                }

                # Resolve Effective Input
                effective_input = {}
                effective_input.update(input_payload)
                if isinstance(previous_step_output, dict):
                    effective_input.update(previous_step_output)

                # Execution
                start_time = datetime.now(timezone.utc)
                try:
                    output_data = self.execute_step(component, effective_input, user_id, manual_context)
                    status = "success"
                    error_msg = None
                except Exception as step_e:
                    output_data = None
                    status = "failed"
                    error_msg = str(step_e)
                    # For MVP, stop on failure
                    # In future, we could have failure handlers in 'next_step_selector'
                    raise step_e

                step_log = {
                    "step_id": current_step_id,
                    "component": comp_name,
                    "status": status,
                    "input": step_input,
                    "output": output_data,
                    "error": error_msg,
                    "timestamp": start_time.isoformat(),
                    "duration_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
                    "used_manual": task_package_name if manual_context else None,
                }
                logs.append(step_log)
                
                # Update context
                previous_step_output = output_data

                # Determine Next Step
                current_step_id = self._determine_next_step(step, output_data, sorted_step_ids)

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

    def execute_step(self, component: Component, input_data: dict, user_id: int | None = None, manual_context: str | None = None) -> dict:
        # Priority: Skill-based execution
        if component.skill_id and component.skill:
            return self._execute_skill(component.skill, component.configuration, input_data, user_id, manual_context)

        # Fallback: Legacy "kind" based execution
        config = component.configuration or {}
        kind = config.get("kind")

        if kind == "http":
            return self._run_http(config, input_data)

        elif kind == "azure_openai":
            return self._run_azure_openai(config, input_data, user_id, component.name)

        elif kind == "ocr_api":
            return self._run_ocr_api(config, input_data)

        elif kind == "mock":
            return config.get("payload", {})

        else:
            return {"error": f"Unknown component kind: {kind}"}

    def _execute_skill(self, skill: Skill, comp_config: dict, input_data: dict, user_id: int | None, manual_context: str | None = None) -> dict:
        # Merge configurations (Component config overrides Skill config)
        final_config = skill.configuration.copy()
        final_config.update(comp_config or {})
        
        if skill.skill_type == SkillType.LLM_PROMPT:
            # Inject Manual into System Prompt
            if manual_context:
                base_prompt = final_config.get("system_template") or final_config.get("system_prompt") or "You are a helpful AI assistant."
                # Append Manual
                final_config["system_prompt"] = f"{base_prompt}\n\n=== BUSINESS MANUAL (SOP) ===\n{manual_context}\n\n=== INSTRUCTIONS ===\nFollow the manual strictly."
            
            return self._run_azure_openai(final_config, input_data, user_id, skill.name)
        
        elif skill.skill_type == SkillType.API_CALL:
            return self._run_http(final_config, input_data)
            
        elif skill.skill_type == SkillType.PYTHON_FUNC:
            # Placeholder for Python function execution
            module_name = final_config.get("module")
            func_name = final_config.get("function")
            return {"error": "PYTHON_FUNC not strictly implemented yet", "debug": f"Would run {module_name}.{func_name}"}
        
        else:
            return {"error": f"Unsupported Skill Type: {skill.skill_type}"}

    def _run_http(self, config: dict, input_data: dict) -> dict:
        import httpx
        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {"Content-Type": "application/json"})
        
        if not url:
            raise ValueError("Missing URL in configuration")

        if method.upper() == "POST":
            response = httpx.post(url, json=input_data, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        elif method.upper() == "GET":
            response = httpx.get(url, params=input_data, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        else:
            raise ValueError(f"Unsupported method {method}")

    def _run_azure_openai(self, config: dict, input_data: dict, user_id: int | None, app_name: str) -> dict:
        import httpx
        import os
        from app.models.domain import AIModel
        from app.models.stats import UsageLog

        # 1. Determine Model Info
        target_model_id = config.get("model_id")
        ai_model = None
        
        if target_model_id:
            ai_model = self.db.query(AIModel).filter(AIModel.id == target_model_id).first()
        
        if not ai_model:
            ai_model = self.db.query(AIModel).filter(AIModel.is_active == True).first()
        
        if not ai_model:
            raise ValueError("No AIModel configuration found (active or specified)")

        # 2. Get Credentials
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
            req_payload = input_data
        else:
            user_content = input_data.get("prompt") or json.dumps(input_data)
            # Support template from config
            system_prompt = config.get("system_template") or config.get("system_prompt") or "You are a helpful AI assistant."
            
            req_payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
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

        # 5. Log Token Usage
        if user_id:
            usage = json_response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            from app.core.cost_calculator import calculate_ai_cost
            estimated_cost = calculate_ai_cost(ai_model.name, prompt_tokens, completion_tokens)
            
            log_entry = UsageLog(
                user_id=user_id,
                app_name=app_name, 
                model_name=ai_model.name,
                tokens_input=prompt_tokens,
                tokens_output=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost
            )
            self.db.add(log_entry)
            self.db.commit()

        return json_response

    def _run_ocr_api(self, config: dict, input_data: dict) -> dict:
        import httpx
        import os
        from pathlib import Path
        import mimetypes

        url = config.get("url")
        if not url:
            raise ValueError("Missing 'url' in configuration for OCR API")

        image_path_str = input_data.get("image_path") or input_data.get("image_url")
        if not image_path_str:
            debug_keys = list(input_data.keys())
            raise ValueError(f"Input must contain 'image_path' or 'image_url'. Received input keys: {debug_keys}")

        image_path = Path(image_path_str)
        if not image_path.exists():
            image_path = Path(os.getcwd()) / image_path_str
            if not image_path.exists():
                    raise ValueError(f"Image file not found: {image_path_str}")

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
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
                files = {'file': (image_path.name, f, mime_type)} 
                response = httpx.post(url, files=files, timeout=60.0)
            
            if response.status_code != 200:
                raise ValueError(f"OCR API Error ({response.status_code}): {response.text}")
            
            return response.json()
        except Exception as e:
            raise ValueError(f"Failed to call OCR API: {str(e)}")

    def _determine_next_step(self, current_step: dict, output_data: dict | None, sorted_step_ids: list[int]) -> int | None:
        """
        Determine the next step ID based on:
        1. 'next_step_id' + 'condition'
        2. Sequential fallback
        """
        current_id = current_step.get('step_id')
        explicit_next = current_step.get('next_step_id')
        condition = current_step.get('condition') # e.g. {"field": "status", "value": "approve", "operator": "=="}

        # 1. Check Condition for Explicit Jump
        if explicit_next is not None:
            if condition:
                # Evaluate condition
                if self._evaluate_condition(condition, output_data):
                    return explicit_next
                else:
                    # Condition failed, fall through to sequential
                    pass 
            else:
                # Unconditional jump
                return explicit_next
        
        # 2. Sequential Fallback
        # Find current index and return next
        try:
            curr_idx = sorted_step_ids.index(current_id)
            if curr_idx + 1 < len(sorted_step_ids):
                return sorted_step_ids[curr_idx + 1]
        except ValueError:
            pass
            
        return None # End of workflow

    def _evaluate_condition(self, condition: dict, data: dict | None) -> bool:
        if not data or not isinstance(data, dict):
            return False
            
        field = condition.get('field')
        value = condition.get('value')
        operator = condition.get('operator', '==')
        
        actual_value = data.get(field)
        
        if operator == '==':
            return str(actual_value) == str(value)
        elif operator == '!=':
            return str(actual_value) != str(value)
        elif operator == 'contains':
            return str(value) in str(actual_value)
        
        return False

def get_workflow_engine(db: Session):
    return WorkflowEngine(db)

import sys
import os
from uuid import uuid4
import json

# Ensure current directory is in path so we can import 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.domain import Workflow, Component, RunExecution, EndpointType
from app.models.skill import Skill, SkillType
from app.models.task import TaskPackage
from app.services.workflow_engine import WorkflowEngine

def verify():
    # Make sure tables exist (in case migration didn't run via main.py yet)
    # Using existing engine
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("=== Architecture Upgrade Verification ===")
        print("1. Creating Test Skill...")
        # A simple "Mock LLM" skill
        skill = Skill(
            id=uuid4(),
            name=f"verify_skill_{uuid4().hex[:8]}",
            description="A test skill for verification",
            category="test",
            skill_type=SkillType.LLM_PROMPT,
            configuration={"system_prompt": "Original System Prompt"},
            active=True
        )
        db.add(skill)
        db.commit()
        print(f"   -> Created Skill: {skill.name} ({skill.id})")

        print("\n2. Creating Component wrapping the Skill...")
        comp = Component(
            id=uuid4(),
            name=f"verify_comp_{uuid4().hex[:8]}",
            description="Wrapper component",
            endpoint_type=EndpointType.CLOUD_LLM, # Legacy field, less relevant now
            skill_id=skill.id,
            # Component config overrides Skill config
            configuration={"model_id": None, "kind": "mock", "payload": {"response": "Mocked Response", "reasoning": "Test passed"}} 
        )
        
        db.add(comp)
        db.commit() 
        print(f"   -> Created Component linked to Skill: {comp.name}")

        print("\n3. Creating TaskPackage with Manual...")
        tp = TaskPackage(
            id=uuid4(),
            name=f"verify_tp_{uuid4().hex[:8]}",
            description="Test Package",
            department="QA",
            manual_content="IMPORTANT: Always answer with 'Verified'."
        )
        db.add(tp)
        db.commit()
        print(f"   -> Created TaskPackage: {tp.name} (Manual len: {len(tp.manual_content)})")

        print("\n4. Creating Workflow...")
        # Step 1: Run the component
        step_1_id = 1
        workflow = Workflow(
            id=uuid4(),
            name=f"verify_wf_{uuid4().hex[:8]}",
            description="Verification Workflow",
            steps=[
                {
                    "step_id": step_1_id,
                    "component_id": str(comp.id),
                    "config": {},
                    "input_mapping": {},
                    # Test branching logic: if output has 'verified', go to nowhere (end)
                    "condition": {"field": "status", "value": "success", "operator": "=="},
                    "next_step_id": None 
                }
            ]
        )
        db.add(workflow)
        db.commit()
        print(f"   -> Created Workflow: {workflow.name}")

        print("\n5. Running Workflow (Simulation)...")
        engine_svc = WorkflowEngine(db)
        
        # Monkey Patch _run_azure_openai to Mock output without API keys
        def mock_azure_run(config, input_data, user_id, app_name):
            print(f"      [MockLLM] System Prompt Injection Check: {'=== BUSINESS MANUAL' in config.get('system_prompt', '')}")
            return {"content": "Verified", "usage": {}}
            
        engine_svc._run_azure_openai = mock_azure_run
        
        # Run
        try:
            run = engine_svc.run_workflow(
                workflow_id=workflow.id,
                input_payload={"prompt": "Hello"},
                task_package_id=tp.id
            )
            print(f"   -> Run Status: {run.status}")
            print(f"   -> Logs: {len(run.log)} steps executed")
            
            if run.log:
                last_log = run.log[-1]
                used_manual = last_log.get('used_manual')
                print(f"   -> Verified 'used_manual' in log: {used_manual}")
                
                if used_manual == tp.name:
                    print("   ✅ SUCCESS: Manual name logged correctly!")
                else:
                    print(f"   ❌ FAILURE: Expected manual {tp.name}, got {used_manual}")
            else:
                 print("   ❌ FAILURE: No logs generated.")
            
        except Exception as e:
            print(f"   ❌ Execution Failed: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify()

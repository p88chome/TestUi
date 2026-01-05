import os
import importlib.util
from sqlalchemy.orm import Session
from app.models.skill import Skill, SkillType
from app.core.config import settings

SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")

import yaml

def parse_skill_md(file_path: str) -> dict:
    """
    Parses a skill.md file using PyYAML for the frontmatter.
    Format:
    ---
    key: value
    input_schema: ...
    ---
    # Instructions
    ...
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    metadata = {}
    instructions = ""

    # Split by '---'
    # Expected: ['', 'yaml_content', 'markdown_body'] if file starts with ---
    # Split by '---'
    parts = content.split("---")
    
    yaml_text = ""
    
    if len(parts) >= 3 and parts[0].strip() == "":
        # Standard Frontmatter: starts with ---
        # ['', 'yaml', 'body']
        yaml_text = parts[1]
        instructions = "---".join(parts[2:]).strip()
    elif len(parts) >= 2:
        # Implicit Frontmatter: starts with content, ends with ---
        # ['yaml', 'body']
        yaml_text = parts[0]
        instructions = "---".join(parts[1:]).strip()
    else:
        # No frontmatter found
        yaml_text = ""
        instructions = content

    if yaml_text:
        try:
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                metadata = parsed
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {file_path}: {e}")
            
    metadata["instructions"] = instructions

        
    return metadata

def load_skills(db: Session):
    """
    Scans the skills directory and updates the database.
    """
    if not os.path.exists(SKILLS_DIR):
        os.makedirs(SKILLS_DIR)
        return

    print(f"Scanning skills in {SKILLS_DIR}...")
    
    for entry in os.scandir(SKILLS_DIR):
        if entry.is_dir():
            skill_dir = entry.path
            md_path = os.path.join(skill_dir, "skill.md")
            run_path = os.path.join(skill_dir, "run.py")
            
            if os.path.exists(md_path) and os.path.exists(run_path):
                # Valid skill folder
                try:
                    meta = parse_skill_md(md_path)
                    
                    skill_name = meta.get("name", entry.name) 
                    category = meta.get("category", "uncategorized")
                    
                    # Upsert Skill
                    existing = db.query(Skill).filter(Skill.name == skill_name).first()
                    if not existing:
                        print(f"Registering new skill: {skill_name}")
                        new_skill = Skill(
                            name=skill_name,
                            description=meta.get("description", ""),
                            category=category,
                            skill_type=SkillType.PYTHON_FUNC,
                            input_schema=meta.get("input_schema", {}), # ADDED
                            configuration={
                                "folder_path": skill_dir,
                                "instructions": meta.get("instructions", "")
                            },
                            is_active=True
                        )
                        db.add(new_skill)
                    else:
                        print(f"Updating skill: {skill_name}")
                        existing.description = meta.get("description", "")
                        existing.category = category
                        existing.input_schema = meta.get("input_schema", {}) # ADDED
                        existing.configuration = {
                            "folder_path": skill_dir,
                            "instructions": meta.get("instructions", "")
                        }
                        existing.is_active = True
                        db.add(existing)
                        
                    db.commit()
                except Exception as e:
                    print(f"Failed to load skill {entry.name}: {e}")
                    db.rollback()

def execute_skill(skill_name: str, input_data: dict, db: Session):
    """
    Executes a skill by name.
    """
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill or not skill.is_active:
        raise ValueError(f"Skill {skill_name} not found or inactive")
        
    folder_path = skill.configuration.get("folder_path")
    if not folder_path or not os.path.exists(folder_path):
        folder_path = os.path.join(SKILLS_DIR, skill_name)
        if not os.path.exists(folder_path):
             raise ValueError(f"Skill code not found at {folder_path}")

    run_script = os.path.join(folder_path, "run.py")
    
    # --- Logging Start ---
    from app.models.skill import SkillExecution
    import time
    
    execution_record = SkillExecution(
        skill_name=skill_name,
        input_data=input_data,
        status="RUNNING"
    )
    db.add(execution_record)
    db.commit()
    db.refresh(execution_record)
    
    start_time = time.time()
    result = None
    status = "SUCCESS"
    logs = ""
    error_detail = None

    try:
        # Dynamic import
        spec = importlib.util.spec_from_file_location("skill_module", run_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, "execute"):
            result = module.execute(input_data)
        else:
            raise ValueError("run.py must contain an 'execute(input_data)' function")
            
    except Exception as e:
        status = "ERROR"
        error_detail = str(e)
        logs = f"Error: {str(e)}"
        raise e
    finally:
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)
        
        execution_record.output_data = result if status == "SUCCESS" else {"error": error_detail}
        execution_record.status = status
        execution_record.logs = logs
        execution_record.execution_time_ms = duration_ms # Mapped as JSON in model but int is fine? Wait, I defined it as JSON in model error.
        # Fix model first or cast? I defined it as JSON in the previous tool call, which is weird for int. 
        # Actually I check the previous tool call, I set execution_time_ms: Mapped[int] = mapped_column(JSON... 
        # Wait, if I say mapped_column(JSON) it expects valid JSON. Integer is valid JSON.
        
        db.add(execution_record)
        db.commit()
    
    return result

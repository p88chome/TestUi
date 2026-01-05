from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import os
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.skill import Skill
from app.services.skill_loader import load_skills, execute_skill
from pydantic import BaseModel

router = APIRouter(prefix="/skills", tags=["skills"])

class SkillRunRequest(BaseModel):
    input: dict

@router.get("/")
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).filter(Skill.is_active == True).all()

@router.post("/refresh")
def refresh_skills(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Scans the files system and updates the library.
    """
    load_skills(db)
    return {"status": "refreshing", "message": "Skills scan complete"}

@router.post("/{skill_name}/run")
def run_skill_endpoint(skill_name: str, req: SkillRunRequest, db: Session = Depends(get_db)):
    try:
        result = execute_skill(skill_name, req.input, db)
        return {"status": "success", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class SkillFileUpdate(BaseModel):
    content: str

@router.get("/{skill_name}/files")
def list_skill_files(skill_name: str, db: Session = Depends(get_db)):
    """
    Lists all files in the skill directory recursively.
    """
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    folder_path = skill.configuration.get("folder_path")
    if not folder_path or not os.path.exists(folder_path):
         raise HTTPException(status_code=400, detail="Skill folder path invalid")

    files_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Get relative path
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            files_list.append(rel_path.replace("\\", "/"))
            
    return {"files": sorted(files_list)}

@router.get("/{skill_name}/file")
def get_skill_file(skill_name: str, path: str = "skill.md", db: Session = Depends(get_db)):
    """
    Reads the content of a file within the skill directory.
    """
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    folder_path = skill.configuration.get("folder_path")
    if not folder_path:
         raise HTTPException(status_code=400, detail="Skill folder path not configured")

    # Security check: Ensure path does not go outside
    target_path = os.path.abspath(os.path.join(folder_path, path))
    if not target_path.startswith(os.path.abspath(folder_path)):
         raise HTTPException(status_code=403, detail="Access denied: Path traversal attempt")

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content, "path": path}
    except UnicodeDecodeError:
        return {"content": "(Binary or non-UTF8 file not displayable)", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@router.put("/{skill_name}/file")
def update_skill_file(skill_name: str, update: SkillFileUpdate, path: str = "skill.md", background_tasks: BackgroundTasks = None, db: Session = Depends(get_db)):
    """
    Updates a specific file and triggers a reload if it's skill.md.
    """
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    folder_path = skill.configuration.get("folder_path")
    if not folder_path:
         raise HTTPException(status_code=400, detail="Skill folder path not configured")

    target_path = os.path.abspath(os.path.join(folder_path, path))
    if not target_path.startswith(os.path.abspath(folder_path)):
         raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Create directories if they don't exist (e.g. creating new resources/foo.md)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(update.content)
            
        # Only reload if skill.md changed, or maybe we just always reload to be safe? 
        # Reloading is cheap enough.
        if background_tasks:
            background_tasks.add_task(load_skills, db)
        
        return {"status": "success", "message": f"File {path} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

import logging
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.skill import Skill
from app.services.skill_loader import load_skills, execute_skill
from app.api import deps
from app.models.user import User
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skills", tags=["skills"])

class SkillRunRequest(BaseModel):
    input: dict

class SkillFileUpdate(BaseModel):
    content: str

@router.get("/")
def list_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return db.query(Skill).filter(Skill.is_active == True).all()

@router.post("/refresh")
def refresh_skills(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    load_skills(db)
    return {"status": "refreshing", "message": "Skills scan complete"}

@router.post("/{skill_name}/run")
def run_skill_endpoint(
    skill_name: str,
    req: SkillRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    try:
        result = execute_skill(skill_name, req.input, db)
        return {"status": "success", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Skill execution error: %s", skill_name, exc_info=True)
        raise HTTPException(status_code=500, detail="Skill execution failed")

@router.get("/{skill_name}/files")
def list_skill_files(
    skill_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    folder_path = skill.configuration.get("folder_path")
    if not folder_path or not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Skill folder path invalid")

    files_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            files_list.append(rel_path.replace("\\", "/"))

    return {"files": sorted(files_list)}

@router.get("/{skill_name}/file")
def get_skill_file(
    skill_name: str,
    path: str = "skill.md",
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    folder_path = skill.configuration.get("folder_path")
    if not folder_path:
        raise HTTPException(status_code=400, detail="Skill folder path not configured")

    target_path = Path(os.path.join(folder_path, path)).resolve()
    if not target_path.is_relative_to(Path(folder_path).resolve()):
        raise HTTPException(status_code=403, detail="Access denied: Path traversal attempt")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        return {"content": target_path.read_text(encoding="utf-8"), "path": path}
    except UnicodeDecodeError:
        return {"content": "(Binary or non-UTF8 file not displayable)", "path": path}
    except Exception:
        logger.error("Error reading skill file", exc_info=True)
        raise HTTPException(status_code=500, detail="Error reading file")

ALLOWED_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json"}

@router.put("/{skill_name}/file")
def update_skill_file(
    skill_name: str,
    update: SkillFileUpdate,
    path: str = "skill.md",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    folder_path = skill.configuration.get("folder_path")
    if not folder_path:
        raise HTTPException(status_code=400, detail="Skill folder path not configured")

    target_path = Path(os.path.join(folder_path, path)).resolve()
    if not target_path.is_relative_to(Path(folder_path).resolve()):
        raise HTTPException(status_code=403, detail="Access denied")

    if target_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(update.content, encoding="utf-8")

        if background_tasks:
            background_tasks.add_task(load_skills, db)

        return {"status": "success", "message": f"File {path} updated"}
    except Exception:
        logger.error("Error writing skill file", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to write file")

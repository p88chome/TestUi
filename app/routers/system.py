from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/readme")
def get_readme():
    """
    Get the content of the project README.md file.
    """
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        # Try one level up if we are in app/
        readme_path = "../README.md"
        
    if not os.path.exists(readme_path):
        # Explicit absolute path fallback for debugging locally if needed, 
        # but relative *should* work if CWD is project root.
        # Let's try to be robust.
        return {"content": "# README not found\n\nCould not locate README.md file."}

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

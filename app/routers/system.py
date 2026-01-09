from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/readme")
def get_readme():
    """
    Get the content of the project README.md file.
    """
    candidates = []
    
    # Strategy: Start from this file's directory and walk up 5 levels
    try:
        current_search_dir = os.path.dirname(os.path.abspath(__file__))
        for _ in range(5):
            check_path = os.path.join(current_search_dir, "README.md")
            candidates.append(check_path)
            
            if os.path.exists(check_path) and os.path.isfile(check_path):
                # Found it!
                try:
                    with open(check_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    return {"content": content}
                except:
                    pass
            
            # Move up one level
            parent = os.path.dirname(current_search_dir)
            if parent == current_search_dir: # Reached system root
                break
            current_search_dir = parent
    except:
        pass

    # Backup Strategy: Check CWD and standard defaults
    backup_paths = [
        "README.md",
        "./README.md", 
        "../README.md",
        "/opt/render/project/src/README.md",
        "/app/README.md"
    ]
    
    for path in backup_paths:
        candidates.append(path)
        if os.path.exists(path) and os.path.isfile(path):
             try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"content": content}
             except:
                pass
    
    # Failure
    debug_info = "\n- ".join(candidates)
    return {
        "content": f"# Documentation Not Found\n\nCould not locate README.md.\n\nChecked paths:\n- {debug_info}\n\nCurrent CWD: {os.getcwd()}"
    }

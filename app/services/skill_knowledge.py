"""
Skill Knowledge Service
Provides access to the global_skills knowledge base for enhanced AI capabilities.
This service indexes and searches the Antigravity Awesome Skills collection.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from functools import lru_cache
import yaml

logger = logging.getLogger(__name__)

# Path to global_skills directory (relative to project root)
GLOBAL_SKILLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "global_skills", "skills", "skills"
)


def parse_skill_frontmatter(file_path: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from a SKILL.md file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by '---'
        parts = content.split("---")
        
        if len(parts) >= 3 and parts[0].strip() == "":
            yaml_text = parts[1]
            body = "---".join(parts[2:]).strip()
        elif len(parts) >= 2:
            yaml_text = parts[0]
            body = "---".join(parts[1:]).strip()
        else:
            return {"body": content}
        
        metadata = {}
        if yaml_text:
            try:
                parsed = yaml.safe_load(yaml_text)
                if isinstance(parsed, dict):
                    metadata = parsed
            except yaml.YAMLError:
                pass
        
        metadata["body"] = body
        metadata["file_path"] = file_path
        return metadata
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        return {}


@lru_cache(maxsize=1)
def get_skill_index() -> Dict[str, Dict[str, Any]]:
    """
    Build and cache an index of all available global skills.
    Returns a dictionary mapping skill names to their metadata.
    """
    index = {}
    
    if not os.path.exists(GLOBAL_SKILLS_DIR):
        logger.warning(f"Global skills directory not found: {GLOBAL_SKILLS_DIR}")
        return index
    
    for entry in os.scandir(GLOBAL_SKILLS_DIR):
        if entry.is_dir():
            skill_md = os.path.join(entry.path, "SKILL.md")
            if os.path.exists(skill_md):
                try:
                    meta = parse_skill_frontmatter(skill_md)
                    skill_name = meta.get("name", entry.name)
                    index[skill_name] = {
                        "name": skill_name,
                        "description": meta.get("description", ""),
                        "folder": entry.name,
                        "path": entry.path,
                        "file_path": skill_md
                    }
                except Exception as e:
                    logger.error(f"Error indexing skill {entry.name}: {e}")
    
    logger.info(f"Indexed {len(index)} global skills")
    return index


def search_skills(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for skills matching the query.
    Uses simple keyword matching on skill name and description.
    """
    index = get_skill_index()
    results = []
    query_lower = query.lower()
    
    for skill_name, skill_info in index.items():
        score = 0
        
        # Check skill name
        if query_lower in skill_name.lower():
            score += 10
        
        # Check description
        desc = skill_info.get("description", "")
        if query_lower in desc.lower():
            score += 5
        
        # Check keywords in query
        keywords = query_lower.split()
        for keyword in keywords:
            if keyword in skill_name.lower():
                score += 3
            if keyword in desc.lower():
                score += 1
        
        if score > 0:
            results.append({**skill_info, "score": score})
    
    # Sort by score, descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def get_skill_content(skill_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the full content of a specific skill including instructions.
    Implements progressive disclosure - only loads full content when needed.
    """
    index = get_skill_index()
    
    skill_info = index.get(skill_name)
    if not skill_info:
        # Try fuzzy match
        for name, info in index.items():
            if skill_name.lower() in name.lower() or name.lower() in skill_name.lower():
                skill_info = info
                break
    
    if not skill_info:
        return None
    
    skill_md = skill_info.get("file_path")
    if not skill_md or not os.path.exists(skill_md):
        return None
    
    # Load full content
    full_meta = parse_skill_frontmatter(skill_md)
    
    return {
        "name": skill_info["name"],
        "description": skill_info.get("description", ""),
        "folder": skill_info.get("folder"),
        "instructions": full_meta.get("body", ""),
        "metadata": {k: v for k, v in full_meta.items() if k not in ["body", "file_path"]}
    }


def get_skill_categories() -> Dict[str, List[str]]:
    """
    Get all skills organized by category.
    Categories are inferred from folder naming conventions.
    """
    index = get_skill_index()
    categories = {}
    
    for skill_name, skill_info in index.items():
        folder = skill_info.get("folder", "")
        
        # Infer category from folder name
        if "-official" in folder:
            category = "official"
        elif folder.startswith("mcp-"):
            category = "mcp"
        elif any(x in folder for x in ["firebase", "supabase", "vercel", "aws"]):
            category = "cloud"
        elif any(x in folder for x in ["react", "vue", "angular", "frontend"]):
            category = "frontend"
        elif any(x in folder for x in ["security", "pentest", "audit"]):
            category = "security"
        elif any(x in folder for x in ["stripe", "payment"]):
            category = "payments"
        else:
            category = "general"
        
        if category not in categories:
            categories[category] = []
        categories[category].append(skill_name)
    
    return categories


def get_reference_for_task(task_keywords: List[str]) -> Optional[str]:
    """
    Get relevant skill reference content for a specific task.
    This is used to enhance Agent's knowledge during task execution.
    
    Args:
        task_keywords: Keywords describing the task (e.g., ["pdf", "table", "extract"])
    
    Returns:
        Relevant instructions text or None if no match
    """
    # Search for relevant skills
    query = " ".join(task_keywords)
    results = search_skills(query, limit=3)
    
    if not results:
        return None
    
    # Get content from top matching skill
    top_skill = results[0]
    skill_content = get_skill_content(top_skill["name"])
    
    if skill_content:
        return f"""
[Reference from {skill_content['name']} skill]
{skill_content['instructions'][:2000]}
{'...(truncated)' if len(skill_content['instructions']) > 2000 else ''}
"""
    
    return None

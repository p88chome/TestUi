import os
import yaml

def execute(input_data: dict) -> dict:
    """
    Scans the sibling directories in 'app/skills/' to list available skills.
    """
    filter_keyword = input_data.get("filter", "").lower()
    
    # Path to app/skills/ (current dir is app/skills/skill_discovery)
    current_dir = os.path.dirname(__file__)
    skills_root = os.path.dirname(current_dir)
    
    found_skills = []
    
    if not os.path.exists(skills_root):
         return {"error": "Skills directory not found"}

    for entry in os.scandir(skills_root):
        if entry.is_dir() and not entry.name.startswith("__"):
            md_path = os.path.join(entry.path, "skill.md")
            if os.path.exists(md_path):
                try:
                    # Minimal parse to get name/desc
                    with open(md_path, "r", encoding="utf-8") as f:
                        # Quick parse frontmatter
                        lines = f.readlines()
                    
                    meta = {}
                    in_frontmatter = False
                    yaml_lines = []
                    
                    # Robust YAML extraction
                    separator_count = 0
                    if lines and lines[0].strip() == "---":
                        for line in lines:
                            if line.strip() == "---":
                                separator_count += 1
                                if separator_count == 2:
                                    break
                                continue
                            if separator_count == 1:
                                yaml_lines.append(line)
                    else:
                        # Implicit frontmatter?
                        for line in lines:
                             if line.strip() == "---":
                                 break
                             yaml_lines.append(line)

                    if yaml_lines:
                        meta = yaml.safe_load("".join(yaml_lines))
                    
                    name = meta.get("name", entry.name)
                    desc = meta.get("description", "No description")
                    
                    # Filtering
                    if filter_keyword:
                        if filter_keyword in name.lower() or filter_keyword in desc.lower():
                            found_skills.append({"name": name, "description": desc})
                    else:
                        found_skills.append({"name": name, "description": desc})
                        
                except Exception as e:
                    # Skip malformed
                    continue
    
    return {
        "count": len(found_skills),
        "skills": found_skills
    }

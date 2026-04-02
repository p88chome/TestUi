import json
import httpx
from app.core.config import settings

def execute(input_data: dict) -> dict:
    """
    Executes a SymPy task.
    Input: {"query": "..."}
    """
    query = input_data.get("query", "")
    
    system_prompt = """You are an expert SymPy Consultant.
    Your task is to provide Python code solutions using the SymPy library.
    
    Output Format (JSON):
    {
      "summary": "Brief summary",
      "code": "Python code",
      "explanation": "Explanation"
    }
    """
    
    user_prompt = f"Question: {query}\n\nPlease provide a solution:"

    # 1. Get DB session for model selection
    from app.core.database import SessionLocal
    from app.services.llm_service import call_llm_sync
    
    db = SessionLocal()
    try:
        result = call_llm_sync(
            db=db,
            input_text=user_prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=1000
        )
        content = result['choices'][0]['message']['content']
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

import json
import httpx
from app.core.config import settings

def execute(input_data: dict) -> dict:
    """
    Executes an Astropy task.
    Input: {"query": "..."}
    """
    query = input_data.get("query", "")
    
    system_prompt = """你是一位專業的 Astropy 天文計算顧問。
    你的任務是使用 Python 的 Astropy 函式庫來為使用者的問題提供程式碼解決方案。
    
    輸出格式 (JSON):
    {
      "summary": "簡短摘要 (中文)",
      "code": "Python 程式碼",
      "explanation": "詳細解釋 (中文)"
    }
    """
    
    user_prompt = f"Question: {query}\n\nPlease provide a solution:"

    # Call LLM
    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    api_version = getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    if not api_key:
         return {"error": "No Azure API Key"}

    url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise ValueError(f"LLM Error: {resp.text}")
            
            result = resp.json()
            content = result['choices'][0]['message']['content']
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
            
    except Exception as e:
        return {"error": str(e)}

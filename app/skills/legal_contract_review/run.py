import json
import asyncio
from app.services.azure_integration import call_azure_openai, call_azure_ocr
from app.core.database import SessionLocal
# We might need to handle file reading if file_url is actually a local path or we need to download it.
# For simplicity, assuming 'text' is provided OR we simulate OCR call if we had a file handling logic here.
# Since we don't have a standardized "download" tool yet, we will focus on 'text' input 
# BUT we will check if 'file_url' is passed to simulate the orchestration.

def execute(input_data: dict) -> dict:
    """
    Reviews a contract.
    Input: {"text": "..."} OR {"file_url": "..."}
    """
    text = input_data.get("text", "")
    file_url = input_data.get("file_url", "")
    
    # 1. Orchestrate OCR if needed
    if not text and file_url:
        # In a real app, we would download the file_url here.
        # For this MVP, if it represents a local path or we skip downloading:
        # We'll just define a placeholder or try to read if local.
        import os
        if os.path.exists(file_url):
            # It's a local file, let's OCR it!
            # Since call_azure_ocr is async, we need the async/sync hack again or just read text if it's txt.
            # Assuming PDF/Image -> OCR.
             pass 
        else:
            # Mocking OCR for demonstration if user provides a URL that isn't a file path we can reach
            pass
            
    if not text:
        # Fail gracefully or provide a demo text if testing
        if "demo" in str(input_data):
             text = "This AGREEMENT is made on 2023-01-01 between Us and Them. Term: 1 year, Auto-Renew: Yes. Liability: Unlimited."
        else:
             raise ValueError("Input 'text' is required (File processing not fully implemented in this MVP skill)")

    # 2. Prepare Prompt with SOP and Resources
    
    # Dynamic Resource Loading
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resource_path = os.path.join(current_dir, "resources", "risk_matrix.md")
    
    risk_matrix_content = ""
    if os.path.exists(resource_path):
        with open(resource_path, "r", encoding="utf-8") as f:
            risk_matrix_content = f.read()
    else:
        # Fallback if resource is missing
        risk_matrix_content = "- (Risk Matrix file not found, use general legal judgment)"

    system_prompt = f"""你是一位初階法務顧問 (Junior Legal Counsel)。
    請根據以下規則審閱下方的合約文字：

    【審閱重點】
    1. 識別 當事人、日期、終止條款。
    2. 檢查 合規性：雙向保密、付款條件 Net 30。
    
    【風險矩陣 (Risk Matrix)】
    請嚴格依照下方定義進行風險標記：
    {risk_matrix_content}
    
    【輸出 JSON 格式】
    {{
      "summary": "...",
      "parties": [],
      "key_dates": {{}},
      "risk_score": 1-10,
      "risk_factors": [{{"clause": "...", "risk_level": "High/Medium/Low", "explanation": "..."}}],
      "recommendations": []
    }}
    請用繁體中文回答 Summary 和 Explanation。
    """
    
    user_prompt = f"合約內容:\n{text}\n\n請分析:"

    # 3. Call LLM (Sync Wrapper)
    from app.core.config import settings
    import httpx

    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    # Use getattr to avoid AttributeError if server config is stale (not reloaded)
    deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    api_version = getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    if not api_key:
         return {"error": "No Azure API Key", "text": text}

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
        "temperature": 0.1,
        "max_tokens": 1500
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise ValueError(f"LLM Error: {resp.text}")
            
            result = resp.json()
            content = result['choices'][0]['message']['content']
            
            # Cleanup JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

import json
from app.services.azure_integration import call_azure_openai
from app.core.database import SessionLocal

def execute(input_data: dict) -> dict:
    """
    Extracts structured data from receipt text.
    Input: {"text": "..."}
    """
    text = input_data.get("text", "")
    if not text:
        raise ValueError("Input 'text' is required")

    # Load SOP from skill.md (In a real implementation we might parse this dynamically, 
    # but for now we embed the core prompt logic here or assume system prompt handles it.
    # To truly follow the 'Skill' pattern, we should read the instructions from the description/config)
    
    # Simple Prompt Construction
    # Simple Prompt Construction
    system_prompt = """你是一個專業的收據資料提取 AI。
    你的目標是從收據文字中提取結構化的 JSON 資料。
    請遵守以下規則：
    - 提取 商家名稱 (Merchant)、日期 (Date YYYY-MM-DD)、總金額 (Total Amount) 和 幣別 (Currency)。
    - 僅輸出純 JSON 格式，不要包含 markdown 標記。
    - 如果無法識別某些欄位，請留空或使用 null。
    """
    
    user_prompt = f"Receipt Text:\n{text}\n\nExtract JSON:"

    # Call LLM
    # We need a db session for logging stats (optional but good practice)
    # Since run.py is independent, we create a new session or pass it in if architected that way.
    # The current execute_skill signature is execute(input_data, db=None) - wait, loader calls execute(input_data).
    # Ideally loader should inject context. For MVP, we'll skip DB logging or create a local session.
    
    try:
        # Note: call_azure_openai is async, but this execute is sync. 
        # We need to run it synchronously.
        import asyncio
        
        async def run_llm():
            db = SessionLocal()
            try:
                response = await call_azure_openai(
                    db=db,
                    input_text=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.1
                )
                return response
            finally:
                db.close()

        # Check if we have an event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                 # We are likely inside a fastAPI async context already? 
                 # But execute_skill was imported dynamically. 
                 # If this is called from an async endpoint, we should fix execute_skill to be async.
                 # For now, let's assume we can't easily await here without refactoring loader.
                 # HACK: Use a synchronous HTTP client or assume this runs in a threadpool.
                 # Let's try to run it. If it fails, we know why.
                 pass
        except RuntimeError:
             pass

        # To avoid async complexity in this MVP step, let's use a direct sync request 
        # OR update the loader to await. The loader is sync.
        # Let's use `httpx` sync client directly to Azure OpenAI to avoid `await`.
        
        from app.core.config import settings
        import httpx

        api_key = settings.AZURE_OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT
        deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        api_version = settings.AZURE_OPENAI_API_VERSION

        if not api_key:
             return {"error": "No Azure API Key", "data": {"merchant": "Mock Store", "total": 99.99}}

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
            "max_tokens": 800
        }

        with httpx.Client() as client:
            resp = client.post(url, headers=headers, json=payload, timeout=30.0)
            if resp.status_code != 200:
                raise ValueError(f"LLM Error: {resp.text}")
            
            result = resp.json()
            content = result['choices'][0]['message']['content']
            
            # Clean content (remove markdown ```json ... ```)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)

    except Exception as e:
        return {"status": "error", "message": str(e)}


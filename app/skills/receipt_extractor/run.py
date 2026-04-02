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

    from app.core.database import SessionLocal
    from app.services.llm_service import call_llm_sync
    
    db = SessionLocal()
    try:
        result = call_llm_sync(
            db=db,
            input_text=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=800
        )
        content = result['choices'][0]['message']['content']
        
        # Clean content (remove markdown ```json ... ```)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


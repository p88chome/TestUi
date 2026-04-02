from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.azure_integration import call_azure_openai, call_azure_ocr
from app.api import deps
from app.models.user import User
import json

router = APIRouter(prefix="/chat", tags=["chat"])

SMART_SYSTEM_PROMPT = """You are an advanced Enterprise AI Assistant.
Analyze the user's message and any attached document content (provided below).

**AUTO-DETECTION LOGIC**:
1. If the document looks like a **Contract** or Legal Document -> Adopt the persona of a **Senior Legal Expert**. Focus on identifying parties, key terms, and risk clauses.
2. If the document looks like a **Receipt, Invoice, or Financial Statement** -> Adopt the persona of a **Finance Assistant**. Focus on extracting merchant, date, total amount, and category.
3. If the document type is unclear or if no document is attached -> Remain a **Helpful General Assistant**. Do not force a specific persona unless the context is clear.

Always provide professional, concise, and structured responses.
"""

@router.post("/message")
async def chat_message(
    message: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Enterprise Chat Endpoint.
    - Supports Text-only chat.
    - Supports Text + File (OCR Analysis).
    - Uses Auto-Detection to select the best persona (Legal/Finance/General).
    """
    
    context_text = message
    
    # 1. Handle File Upload (OCR)
    if file:
        try:
            content = await file.read()
            ocr_result = await call_azure_ocr(content)
            
            # Append OCR context to the user message
            # We format it clearly so the LLM knows what is user text and what is document text
            context_text += f"\n\n[ATTACHED DOCUMENT CONTENT (OCR)]:\n{ocr_result['full_text']}\n[END DOCUMENT]"
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File Analysis Failed: {str(e)}")

    # 2. Call Azure OpenAI with Smart Prompt
    try:
        response = await call_azure_openai(
            db=db,
            user_id=current_user.id, # Added: Crucial for per-user dashboard
            input_text=context_text,
            system_prompt=SMART_SYSTEM_PROMPT,
            temperature=0.5,
            app_name="Enterprise Chat" # Added for better analytics
        )
        
        # Extract the assistant's reply
        reply = response.get("choices", [])[0].get("message", {}).get("content", "")
        
        # 3. Cost Estimation (Calculated from LLM response)
        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        model_name = response.get("model", "gpt-4")
        from app.core.cost_calculator import calculate_ai_cost
        estimated_cost = calculate_ai_cost(model_name, prompt_tokens, completion_tokens)
        
        return {
            "role": "assistant",
            "content": reply,
            "ocr_processed": bool(file),
            "usage_info": {
                "tokens": total_tokens,
                "cost": estimated_cost
            }
        }
        
    except Exception as e:
        # Log error but don't crash if stats fail? 
        # Ideally we want to know, so let it raise or print
        print(f"Error processing chat or logging stats: {e}")
        raise HTTPException(status_code=500, detail=f"AI Processing Failed: {str(e)}")

import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.azure_integration import call_azure_openai, call_azure_ocr
from app.api import deps
from app.models.user import User
import json

logger = logging.getLogger(__name__)

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
    
    # 1. Handle File Upload (OCR)
    # OCR content is passed as a separate message (not appended to user input)
    # to prevent prompt injection via crafted document content.
    messages = None
    if file:
        try:
            content = await file.read()
            ocr_result = await call_azure_ocr(content)
            doc_text = ocr_result['full_text'][:8000]  # cap to avoid token abuse
            messages = [
                {"role": "system", "content": SMART_SYSTEM_PROMPT},
                {"role": "user", "content": message},
                {"role": "user", "content": f"[Attached document content for analysis]\n{doc_text}"},
            ]
        except Exception as e:
            logger.error("OCR processing failed", exc_info=True)
            raise HTTPException(status_code=500, detail="File analysis failed")

    # 2. Call Azure OpenAI with Smart Prompt
    try:
        call_kwargs = dict(
            db=db,
            user_id=current_user.id,
            system_prompt=SMART_SYSTEM_PROMPT,
            temperature=0.5,
            app_name="Enterprise Chat",
        )
        if messages:
            call_kwargs["messages"] = messages
        else:
            call_kwargs["input_text"] = message

        response = await call_azure_openai(**call_kwargs)
        
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
        logger.error("Chat processing failed", exc_info=True)
        raise HTTPException(status_code=500, detail="AI processing failed")

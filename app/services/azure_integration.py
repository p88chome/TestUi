import os
import json
import httpx
import time
from sqlalchemy.orm import Session
from app.models.domain import AIModel
from app.core.config import settings

# -----------------------------------------------------------------------------
# Azure OpenAI Integration
# -----------------------------------------------------------------------------

from app.services.llm_service import call_llm

async def call_azure_openai(
    db: Session,
    user_id: int | None = None, # Added
    input_text: str | None = None,
    messages: list[dict] | None = None,
    system_prompt: str = "You are a helpful AI assistant.",
    model_id: str | None = None,
    temperature: float = 0.7,
    app_name: str = "Assistant"
) -> dict:
    """
    Calls unified LLM service. 
    Maintained for backward compatibility.
    """
    return await call_llm(
        db=db,
        user_id=user_id, # Added
        input_text=input_text,
        messages=messages,
        system_prompt=system_prompt,
        model_id=model_id,
        temperature=temperature,
        app_name=app_name
    )


# -----------------------------------------------------------------------------
# Azure Computer Vision (OCR) Integration
# -----------------------------------------------------------------------------

async def call_azure_ocr(file_content: bytes) -> dict:
    """
    Calls Azure Computer Vision Read API (v3.2).
    Used by: Workflow Engine (AIOCR), Chat Router (File Analysis).
    """
    
    # 1. Get Credentials
    endpoint = settings.AZURE_VISION_ENDPOINT
    api_key = settings.AZURE_VISION_KEY
    
    if not endpoint or not api_key:
        raise ValueError("Azure Vision credentials not configured (AZURE_VISION_ENDPOINT, AZURE_VISION_KEY)")

    endpoint = endpoint.rstrip("/")
    analyze_url = f"{endpoint}/vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/octet-stream"
    }

    # 2. Submit Operation (POST)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(analyze_url, content=file_content, headers=headers)
        except Exception as e:
            raise ValueError(f"Failed to contact Azure Vision: {str(e)}")

        if response.status_code != 202:
            raise ValueError(f"Azure Vision Error ({response.status_code}): {response.text}")

        operation_url = response.headers.get("Operation-Location")
        if not operation_url:
            raise ValueError("Azure did not return Operation-Location header")

        # 3. Poll for Result (GET)
        max_retries = 30
        poll_interval = 1
        
        for _ in range(max_retries):
            time.sleep(poll_interval)
            
            poll_res = await client.get(operation_url, headers={"Ocp-Apim-Subscription-Key": api_key})
            
            if poll_res.status_code != 200:
                raise ValueError(f"Polling failed: {poll_res.text}")
            
            analysis = poll_res.json()
            status = analysis.get("status")
            
            if status == "succeeded":
                return format_ocr_result(analysis)
            
            if status == "failed":
                raise ValueError("Azure Analysis Failed (Status: failed)")
        
        raise ValueError("OCR Analysis timed out")

def format_ocr_result(analysis: dict) -> dict:
    read_results = analysis.get("analyzeResult", {}).get("readResults", [])
    full_text = []
    lines = []
    
    for page in read_results:
        for line in page.get("lines", []):
            text = line.get("text", "")
            full_text.append(text)
            lines.append(text)
            
    return {
        "status": "success",
        "full_text": "\n".join(full_text),
        "lines": lines,
        "raw_data": analysis
    }

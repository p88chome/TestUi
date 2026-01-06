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

async def call_azure_openai(
    db: Session,
    input_text: str,
    messages: list[dict] | None = None,
    system_prompt: str = "You are a helpful AI assistant.",
    model_id: str | None = None,
    temperature: float = 0.7
) -> dict:
    """
    Calls Azure OpenAI Chat Completions API.
    Used by: Workflow Engine (Universal Azure LLM), Chat Router (Enterprise Chat).
    Supports either manual 'messages' list OR simple 'input_text' + 'system_prompt'.
    """

    # 1. Determine Model
    ai_model = None
    if model_id:
        ai_model = db.query(AIModel).filter(AIModel.id == model_id).first()
    
    if not ai_model:
        # Fallback to default active
        ai_model = db.query(AIModel).filter(AIModel.is_active == True).first()
    
    if not ai_model:
        raise ValueError("No active AIModel configuration found.")

    # 2. Get Credentials
    api_key = settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    
    if not api_key or not endpoint:
        raise ValueError("Missing Azure OpenAI Credentials (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT) in settings.")

    # 3. Construct URL
    endpoint = endpoint.rstrip('/')
    url = f"{endpoint}/openai/deployments/{ai_model.deployment_name}/chat/completions?api-version={ai_model.api_version}"

    print(f"DEBUG: Calling Azure OpenAI Model: {ai_model.name}, Deployment: {ai_model.deployment_name}")
    print(f"DEBUG: Full URL: {url}") # CAREFUL: Don't log API Key, but URL is okay-ish for local debug (contains deployment name)

    # 4. Prepare Payload
    if messages:
        payload = {
            "messages": messages,
            "temperature": temperature
        }
    else:
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            "temperature": temperature
        }

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # 5. Call API
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=60.0)
        
        if response.status_code != 200:
             raise ValueError(f"Azure OpenAI Error ({response.status_code}): {response.text}")
        
        return response.json()


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

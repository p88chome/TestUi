import time
import httpx
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/ocr", tags=["ocr"])

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
):
    """
    Analyzes an image or PDF using Azure Computer Vision (Read API).
    Handles:
    1. Upload to Azure (POST)
    2. Polling for result (GET)
    3. Returning structured data
    """
    
    # 1. Get Config
    endpoint = settings.AZURE_VISION_ENDPOINT
    api_key = settings.AZURE_VISION_KEY
    
    if not endpoint or not api_key:
        raise HTTPException(status_code=500, detail="Azure Vision credentials not configured in .env")

    # Clean endpoint
    endpoint = endpoint.rstrip("/")
    if "cognitiveservices.azure.com" not in endpoint:
        # User might provide just the name, but usually full URL. 
        # Assume full URL for now based on user input.
        pass

    # URL for Read API v3.2
    # https://{endpoint}/vision/v3.2/read/analyze
    analyze_url = f"{endpoint}/vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/octet-stream"
    }

    # 2. Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    # 3. Call Azure (Submit Operation)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(analyze_url, content=file_content, headers=headers)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to contact Azure: {e}")

        if response.status_code != 202:
            raise HTTPException(status_code=response.status_code, detail=f"Azure Vision Error: {response.text}")

        # 4. Get Operation-Location
        operation_url = response.headers.get("Operation-Location")
        if not operation_url:
            raise HTTPException(status_code=500, detail="Azure did not return Operation-Location")

        # 5. Poll for Result
        max_retries = 30
        poll_interval = 1
        
        for _ in range(max_retries):
            # Wait before polling
            time.sleep(poll_interval)
            
            poll_res = await client.get(operation_url, headers={"Ocp-Apim-Subscription-Key": api_key})
            
            if poll_res.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Polling failed: {poll_res.text}")
            
            analysis = poll_res.json()
            status = analysis.get("status")
            
            if status == "succeeded":
                # Success!
                return format_ocr_result(analysis)
            
            if status == "failed":
                raise HTTPException(status_code=500, detail="Azure Analysis Failed")
            
            # If "running" or "notStarted", continue loop
        
        raise HTTPException(status_code=504, detail="Analysis timed out")

def format_ocr_result(analysis: dict):
    """
    Format the complex Azure JSON into a simpler summary + raw data
    """
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
        "raw_data": analysis  # Keep raw data for advanced use cases
    }

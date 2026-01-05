import time
import httpx
import os
from app.core.config import settings

def execute(input_data: dict) -> dict:
    """
    Analyzes an image or PDF using Azure Computer Vision (Read API).
    Input: {"file_path": "..."} OR {"file_url": "..."}
    """
    file_path = input_data.get("file_path")
    file_url = input_data.get("file_url")
    
    # 1. Get Config
    endpoint = settings.AZURE_VISION_ENDPOINT
    api_key = settings.AZURE_VISION_KEY
    
    if not endpoint or not api_key:
         # For Mock / Demo purposes if no keys are present, return fake data
        if settings.EXECUTION_MODE == "mock" or not api_key:
             return {
                 "status": "success",
                 "full_text": "MOCK OCR RESULT: Receipt #12345\nTotal: $500.00",
                 "lines": ["MOCK OCR RESULT", "Receipt #12345", "Total: $500.00"],
                 "note": "Running in mock mode (no Azure keys found)"
             }
        raise ValueError("Azure Vision credentials not configured in .env")

    # Clean endpoint
    endpoint = endpoint.rstrip("/")
    analyze_url = f"{endpoint}/vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/octet-stream"
    }

    # 2. Prepare Content
    content = None
    if file_path:
        if not os.path.exists(file_path):
             raise ValueError(f"File not found: {file_path}")
        with open(file_path, "rb") as f:
            content = f.read()
    else:
        raise ValueError("Must provide file_path")

    # 3. Synchronous wrapper for async calls (since run.py is currently sync in loader)
    # Ideally loader should support async, but for now we use httpx.Client or run async
    # Let's use httpx.Client (sync) for simplicity in this MVP script
    
    with httpx.Client() as client:
        try:
            response = client.post(analyze_url, content=content, headers=headers)
        except Exception as e:
            raise ValueError(f"Failed to contact Azure: {e}")

        if response.status_code != 202:
            raise ValueError(f"Azure Vision Error: {response.text}")

        operation_url = response.headers.get("Operation-Location")
        if not operation_url:
            raise ValueError("Azure did not return Operation-Location")

        # 5. Poll
        max_retries = 30
        poll_interval = 1
        
        for _ in range(max_retries):
            time.sleep(poll_interval)
            poll_res = client.get(operation_url, headers={"Ocp-Apim-Subscription-Key": api_key})
            
            if poll_res.status_code != 200:
                raise ValueError(f"Polling failed: {poll_res.text}")
            
            analysis = poll_res.json()
            status = analysis.get("status")
            
            if status == "succeeded":
                return format_ocr_result(analysis)
            
            if status == "failed":
                raise ValueError("Azure Analysis Failed")
        
        raise ValueError("Analysis timed out")

def format_ocr_result(analysis: dict):
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

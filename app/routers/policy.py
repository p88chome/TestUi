"""
Policy Gap Analysis API Router
提供制度差異分析的專屬 API
"""

import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/policy", tags=["policy"])


@router.post("/analyze")
async def analyze_policy_gap(
    policy_file: UploadFile = File(..., description="管理辦法文件 (docx)"),
    interview_files: List[UploadFile] = File(..., description="訪談紀錄文件列表 (docx)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    制度差異分析 API
    
    上傳管理辦法和訪談紀錄，AI 自動比對差異並產出 Markdown 修改建議報告。
    
    - **policy_file**: 管理辦法文件 (docx 格式)
    - **interview_files**: 訪談紀錄文件列表 (docx 格式，可多份)
    
    Returns:
        Markdown 格式的差異分析報告
    """
    
    # 驗證檔案類型
    def validate_docx(file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(status_code=400, detail="檔案名稱無效")
        if not file.filename.lower().endswith('.docx'):
            raise HTTPException(
                status_code=400, 
                detail=f"不支援的檔案格式: {file.filename}。僅支援 .docx 格式"
            )
    
    validate_docx(policy_file)
    for f in interview_files:
        validate_docx(f)
    
    # 建立暫存目錄
    temp_dir = os.path.join(os.getcwd(), "temp", "policy_analysis")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 儲存上傳的檔案
    session_id = str(uuid.uuid4())
    saved_files = []
    
    try:
        # 儲存管理辦法
        policy_filename = f"{session_id}_policy_{policy_file.filename}"
        policy_path = os.path.join(temp_dir, policy_filename)
        with open(policy_path, "wb") as f:
            content = await policy_file.read()
            f.write(content)
        saved_files.append(policy_path)
        
        # 儲存訪談紀錄
        interview_paths = []
        for i, interview_file in enumerate(interview_files):
            interview_filename = f"{session_id}_interview_{i}_{interview_file.filename}"
            interview_path = os.path.join(temp_dir, interview_filename)
            with open(interview_path, "wb") as f:
                content = await interview_file.read()
                f.write(content)
            interview_paths.append(interview_path)
            saved_files.append(interview_path)
        
        # 呼叫 skill 執行分析
        from app.skills.policy_gap_analysis.run import execute
        
        result = execute({
            "policy_file_path": policy_path,
            "interview_file_paths": interview_paths
        })
        
        # 清理暫存檔案
        for file_path in saved_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "report": result.get("report", ""),
                "format": "markdown",
                "policy_file": policy_file.filename,
                "interview_files": [f.filename for f in interview_files],
                "generated_at": result.get("generated_at", datetime.now().isoformat())
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"分析失敗: {result.get('message', '未知錯誤')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        # 清理暫存檔案
        for file_path in saved_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        
        raise HTTPException(
            status_code=500,
            detail=f"處理檔案時發生錯誤: {str(e)}"
        )


@router.post("/analyze-text")
async def analyze_policy_gap_text(
    policy_content: str = Form(..., description="管理辦法文字內容"),
    interview_content: str = Form(..., description="訪談紀錄文字內容"),
    policy_name: str = Form("管理辦法", description="管理辦法名稱"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    制度差異分析 API (純文字版本)
    
    直接輸入管理辦法和訪談紀錄的文字內容，AI 自動比對差異並產出 Markdown 修改建議報告。
    
    - **policy_content**: 管理辦法文字內容
    - **interview_content**: 訪談紀錄文字內容
    - **policy_name**: 管理辦法名稱 (選填)
    """
    
    if not policy_content.strip():
        raise HTTPException(status_code=400, detail="管理辦法內容不可為空")
    if not interview_content.strip():
        raise HTTPException(status_code=400, detail="訪談紀錄內容不可為空")
    
    # 建構 Prompt 直接呼叫 LLM
    from app.core.config import settings
    import httpx
    
    system_prompt = """你是一位資深的內控顧問與稽核專家。

你的任務是比對「管理辦法」與「訪談紀錄」之間的差異，找出：
1. 制度有規定但實務未落實的地方
2. 實務有執行但制度未明文規定的地方
3. 制度與實務不一致之處
4. 建議新增或修改的條款

## 分析原則
- 精確對應：每個差異必須指出管理辦法的具體條款位置
- 客觀中立：如實呈現差異，不做主觀臆測
- 具體可行：建議修改必須具體，可直接採用

## 輸出格式 (Markdown)

# 制度差異分析報告

**分析日期**: [今天日期]
**管理辦法**: [文件名稱]

---

## 一、管理辦法摘要

(列出管理辦法的主要條款結構，每條簡要說明)

---

## 二、差異分析

| 條款位置 | 管理辦法規定 | 訪談實務發現 | 差異類型 | 建議修改 |
|---------|-------------|-------------|---------|---------|

### 詳細說明

(對每個重要差異進行詳細說明)

---

## 三、建議新增條款

(訪談中提到但管理辦法沒有的控制點，建議新增)

---

## 四、總結與優先順序

| 優先級 | 修改項目 | 理由 |
|-------|---------|------|

---

請用繁體中文輸出，保持專業客觀的語氣。"""

    user_prompt = f"""請根據以下資料進行制度差異分析：

## 管理辦法
**文件名稱**: {policy_name}

{policy_content}

---

## 訪談紀錄

{interview_content}

---

請產出完整的差異分析報告。"""

    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    api_version = getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="未設定 Azure OpenAI API Key")
    
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
        "max_tokens": 4000
    }
    
    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail=f"LLM API Error: {resp.text}")
            
            result = resp.json()
            report_content = result['choices'][0]['message']['content']
            
            return {
                "status": "success",
                "report": report_content,
                "format": "markdown",
                "policy_name": policy_name,
                "generated_at": datetime.now().isoformat()
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析時發生錯誤: {str(e)}")

"""
Policy Gap Analysis API Router
提供制度差異分析的專屬 API
"""

import io
import os
import re
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/policy", tags=["policy"])

ACCEPTED_EXTS = ('.docx', '.pdf')


def _validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="檔案名稱無效")
    if not file.filename.lower().endswith(ACCEPTED_EXTS):
        raise HTTPException(
            status_code=400,
            detail=f"不支援的檔案格式：{file.filename}。支援 .docx 和 .pdf"
        )


def _extract_text_from_bytes(filename: str, content: bytes) -> str:
    """從 DOCX 或 PDF 位元組中擷取純文字。"""
    name_lower = filename.lower()
    if name_lower.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"無法解析 DOCX：{e}")
    if name_lower.endswith('.pdf'):
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
            return "\n".join(parts)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"無法解析 PDF：{e}")
    return content.decode('utf-8', errors='ignore')


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
    
    # 驗證檔案類型（DOCX / PDF）
    _validate_file(policy_file)
    for f in interview_files:
        _validate_file(f)
    
    try:
        # 在記憶體中解析管理辦法
        policy_raw = await policy_file.read()
        policy_content = _extract_text_from_bytes(policy_file.filename, policy_raw)
        
        # 在記憶體中解析所有訪談紀錄
        interview_contents = []
        for i_f in interview_files:
            i_raw = await i_f.read()
            text = _extract_text_from_bytes(i_f.filename, i_raw)
            interview_contents.append(f"【訪談紀錄: {i_f.filename}】\n{text}")
            
        combined_interviews = "\n\n---\n\n".join(interview_contents)
        
        # 直接呼叫與 analyze_policy_gap_text 相同的 LLM 邏輯 (不經過磁碟存檔)
        from app.core.config import settings
        import httpx
        
        # 使用與 text route 相同的 Prompt (或從 run.py 複製過來)
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
**文件名稱**: {policy_file.filename}

{policy_content}

---

## 訪談紀錄

{combined_interviews}

---

請產出完整的差異分析報告。"""

        api_key = settings.AZURE_OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT
        deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
        api_version = getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not api_key:
            return {"status": "error", "error": "未設定 Azure OpenAI API Key"}
            
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
            with httpx.Client(timeout=180.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    return {"status": "error", "error": f"LLM API Error: {resp.text}"}
                
                result = resp.json()
                report_content = result['choices'][0]['message']['content']
                
                return {
                    "status": "success",
                    "report": report_content,
                    "format": "markdown",
                    "policy_file": policy_file.filename,
                    "interview_files": [f.filename for f in interview_files],
                    "generated_at": datetime.now().isoformat()
                }
        except Exception as httpx_err:
             return {"status": "error", "error": f"呼叫 AI 服務發生錯誤 (可能是超時): {str(httpx_err)}"}
             
    except Exception as e:
        # 回傳 200 OK 附帶 error 訊息，避免 Azure 攔截 500 並消除 CORS 標頭
        return {
            "status": "error", 
            "error": f"處理檔案時發生內部錯誤：{str(e)}"
        }


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


# ─── Word Export ─────────────────────────────────────────────────────────────

from pydantic import BaseModel

class ExportDocxRequest(BaseModel):
    report: str               # The full Markdown report text
    policy_name: str = "制度差異分析報告"


@router.post("/export-docx")
async def export_policy_docx(
    request: ExportDocxRequest,
    current_user: User = Depends(get_current_user),
):
    """
    將 Markdown 格式的差異分析報告轉換為可下載的 Word (.docx) 文件。
    使用 python-docx 產生帶有標題、表格、段落的完整 Word 文件。
    """
    from docx import Document as DocxDocument
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = DocxDocument()

    # ── Page setup ──
    section = doc.sections[0]
    section.page_width  = Inches(8.27)   # A4
    section.page_height = Inches(11.69)
    section.left_margin = section.right_margin = Inches(1.0)
    section.top_margin  = section.bottom_margin = Inches(1.0)

    # ── Map Markdown to Word ──
    lines = request.report.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # H1
        if line.startswith('# ') and not line.startswith('## '):
            h = doc.add_heading(line[2:].strip(), level=1)
            h.runs[0].font.color.rgb = RGBColor(0x00, 0x5B, 0x2D)

        # H2
        elif line.startswith('## ') and not line.startswith('### '):
            h = doc.add_heading(line[3:].strip(), level=2)
            h.runs[0].font.color.rgb = RGBColor(0x00, 0x5B, 0x2D)

        # H3
        elif line.startswith('### '):
            h = doc.add_heading(line[4:].strip(), level=3)

        # Horizontal rule
        elif line.strip() == '---':
            doc.add_paragraph('─' * 40)

        # Table  (| col | col | …)
        elif line.strip().startswith('|') and '|' in line[1:]:
            # Collect all consecutive table lines
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_raw = lines[i].strip()
                # Skip separator rows like |---|---|
                if not re.match(r'^\|[\s\-|:]+\|$', row_raw):
                    cells = [c.strip() for c in row_raw.strip('|').split('|')]
                    table_lines.append(cells)
                i += 1

            if table_lines:
                ncols = max(len(r) for r in table_lines)
                tbl = doc.add_table(rows=len(table_lines), cols=ncols)
                tbl.style = 'Table Grid'
                for ri, row_cells in enumerate(table_lines):
                    for ci, cell_text in enumerate(row_cells):
                        cell = tbl.cell(ri, ci)
                        cell.text = cell_text
                        if ri == 0:  # Header row bold
                            for run in cell.paragraphs[0].runs:
                                run.bold = True
                doc.add_paragraph('')  # spacing after table
            continue  # i already advanced inside table loop

        # Bullet list
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            doc.add_paragraph(line.strip()[2:], style='List Bullet')

        # Numbered list
        elif re.match(r'^\d+\.\s', line.strip()):
            doc.add_paragraph(re.sub(r'^\d+\.\s', '', line.strip()), style='List Number')

        # Bold inline **text**
        elif line.strip():
            p = doc.add_paragraph()
            # Parse inline bold
            parts = re.split(r'\*\*(.+?)\*\*', line.strip())
            for pi, part in enumerate(parts):
                run = p.add_run(part)
                if pi % 2 == 1:   # odd index = bold content
                    run.bold = True
            p.runs[0].font.size = Pt(10.5) if p.runs else None
        else:
            doc.add_paragraph('')  # blank line → spacing

        i += 1

    # ── Stream response ──
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    safe_name = request.policy_name.replace('/', '_').replace('\\', '_')
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{safe_name}_{date_str}.docx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


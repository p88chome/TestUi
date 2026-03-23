# -*- coding: utf-8 -*-
"""
Policy Gap Analysis Skill
制度與實務差異分析 - 比對管理辦法與訪談紀錄，產出修改建議報告
"""

import os
import json
from datetime import datetime


def read_docx(file_path: str) -> str:
    """讀取 docx 文件內容"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件: {file_path}")
    
    from docx import Document
    doc = Document(file_path)
    content = []
    for para in doc.paragraphs:
        if para.text.strip():
            content.append(para.text)
    return "\n".join(content)


def execute(input_data: dict) -> dict:
    """
    執行制度差異分析
    
    Args:
        input_data: {
            "policy_file_path": str,  # 管理辦法文件路徑
            "interview_file_paths": list[str]  # 訪談紀錄文件路徑列表
        }
    
    Returns:
        dict: {"status": "success", "report": "markdown content"}
    """
    policy_path = input_data.get("policy_file_path", "")
    interview_paths = input_data.get("interview_file_paths", [])
    
    # 驗證輸入
    if not policy_path:
        raise ValueError("必須提供管理辦法文件路徑 (policy_file_path)")
    if not interview_paths:
        raise ValueError("必須提供至少一份訪談紀錄 (interview_file_paths)")
    
    # 讀取管理辦法
    policy_content = read_docx(policy_path)
    policy_filename = os.path.basename(policy_path)
    
    # 讀取所有訪談紀錄
    interviews = []
    interview_filenames = []
    for path in interview_paths:
        content = read_docx(path)
        interviews.append(content)
        interview_filenames.append(os.path.basename(path))
    
    combined_interviews = "\n\n---\n\n".join([
        f"【訪談紀錄 {i+1}: {interview_filenames[i]}】\n{content}"
        for i, content in enumerate(interviews)
    ])
    
    # 建構 Prompt
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
**訪談紀錄**: [訪談1], [訪談2], ...

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

## 五、更新後流程圖

請根據管理辦法內容和建議修改，繪製更新後的作業流程圖。

使用 Mermaid flowchart 語法，格式如下：

```mermaid
flowchart TD
    A[開始] --> B{決策點}
    B -->|是| C[步驟1]
    B -->|否| D[步驟2]
    C --> E[結束]
    D --> E
```

**流程圖繪製要求 (重要)**：
1. **務必**將流程圖代碼包裹在 ```mermaid 和 ``` 之間，否則無法顯示！
2. 使用 flowchart TD (由上到下)
3. 使用中文標籤
4. 包含主要的審核/決策節點
5. 標註負責單位（如果有）
6. 用不同形狀表示：
   - 方框 `[]` 表示作業步驟
   - 菱形 `{}` 表示決策點
   - 圓角 `()` 表示開始/結束
   - 平行四邊形 `[/  /]` 表示文件產出

---

請用繁體中文輸出，保持專業客觀的語氣。"""

    user_prompt = f"""請根據以下資料進行制度差異分析：

## 管理辦法
**文件名稱**: {policy_filename}

{policy_content}

---

## 訪談紀錄

{combined_interviews}

---

請產出完整的差異分析報告。"""

    # 呼叫 LLM
    from app.core.config import settings
    import httpx
    
    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    api_version = getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    if not api_key:
        return {"status": "error", "message": "未設定 Azure OpenAI API Key"}
    
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
                raise ValueError(f"LLM API Error: {resp.text}")
            
            result = resp.json()
            report_content = result['choices'][0]['message']['content']
            
            return {
                "status": "success",
                "report": report_content,
                "policy_file": policy_filename,
                "interview_files": interview_filenames,
                "generated_at": datetime.now().isoformat()
            }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

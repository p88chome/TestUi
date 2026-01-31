"""
Meeting Minutes Skill - 會議紀錄助手
將會議對話文字轉換為結構化會議紀錄
"""

from datetime import datetime

def execute(input_data: dict, db=None, trace_id: str = None) -> dict:
    """
    執行會議紀錄生成。
    
    Args:
        input_data: 包含 content, meeting_title, meeting_date, participants
        db: 資料庫 session (用於呼叫 LLM Gateway)
        trace_id: 追蹤 ID
    
    Returns:
        dict: 包含生成的會議紀錄
    """
    content = input_data.get("content", "")
    meeting_title = input_data.get("meeting_title", "")
    meeting_date = input_data.get("meeting_date", datetime.now().strftime("%Y-%m-%d"))
    participants = input_data.get("participants", "")
    
    if not content or not content.strip():
        return {
            "status": "error",
            "error": "請提供會議內容 (content 參數不可為空)"
        }
    
    # 構建提示詞
    prompt = _build_prompt(content, meeting_title, meeting_date, participants)
    
    # 如果有 db session，使用 LLM Gateway
    if db:
        try:
            from app.services.gateway import LLMGateway
            import asyncio
            
            gateway = LLMGateway(db)
            messages = [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ]
            
            # 同步呼叫非同步函數
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(gateway.chat(messages=messages, temperature=0.3))
            finally:
                loop.close()
            
            # 解析回應
            choices = response.get("choices", [])
            if choices:
                minutes_content = choices[0].get("message", {}).get("content", "")
                return {
                    "status": "success",
                    "meeting_minutes": minutes_content,
                    "format": "markdown",
                    "meeting_title": meeting_title or "會議紀錄",
                    "meeting_date": meeting_date
                }
            else:
                return {
                    "status": "error",
                    "error": "LLM 未返回有效內容"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": f"生成會議紀錄時發生錯誤: {str(e)}"
            }
    else:
        # 無 DB 連線時，回傳模板 (用於測試)
        return _generate_template(content, meeting_title, meeting_date, participants)


def _build_prompt(content: str, title: str, date: str, participants: str) -> dict:
    """建構 LLM 提示詞"""
    
    system_prompt = """你是一位專業的會議紀錄助理，專門協助內控團隊整理會議內容。

你的任務是將非結構化的會議對話或文字，轉換為清晰、專業的會議紀錄。

## 輸出要求
請使用以下 Markdown 格式輸出：

```
## 會議主題
[根據內容推斷或使用提供的標題]

**日期**: [會議日期]
**出席者**: [從對話中識別的人員，或使用提供的列表]

### 討論事項
- [重點摘要，條列式]
- [每個議題一行]

### 決議事項
1. [明確的決議內容]
2. [包含具體行動]

### 待辦追蹤
| 負責人 | 待辦事項 | 截止日 |
|--------|----------|--------|
| [人名] | [具體任務] | [日期或待定] |
```

## 注意事項
1. 使用繁體中文
2. 保持客觀、專業的語調
3. 不要遺漏重要決議
4. 若內容提及具體日期或負責人，務必記錄
5. 若資訊不明確，使用「待確認」標註"""

    user_prompt = f"""請根據以下會議內容，產出結構化會議紀錄：

{f'**會議標題**: {title}' if title else ''}
{f'**會議日期**: {date}' if date else ''}
{f'**出席者**: {participants}' if participants else ''}

---
**會議內容**：

{content}
"""

    return {
        "system": system_prompt,
        "user": user_prompt
    }


def _generate_template(content: str, title: str, date: str, participants: str) -> dict:
    """無 LLM 時生成基本模板 (用於測試)"""
    
    template = f"""## 會議主題
{title if title else '(待 AI 分析)'}

**日期**: {date}
**出席者**: {participants if participants else '(待 AI 識別)'}

### 討論事項
- (AI 將分析會議內容並產生摘要)

### 決議事項
1. (AI 將識別決議事項)

### 待辦追蹤
| 負責人 | 待辦事項 | 截止日 |
|--------|----------|--------|
| - | (待 AI 分析) | - |

---
*原始內容長度: {len(content)} 字元*
"""
    
    return {
        "status": "success",
        "meeting_minutes": template,
        "format": "markdown",
        "note": "此為模板輸出，實際使用時將由 AI 生成完整內容"
    }

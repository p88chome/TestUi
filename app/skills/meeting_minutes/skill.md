name: meeting_minutes
description: 會議紀錄助手：將會議文字、對話轉換為結構化會議紀錄，包含議題、決議、待辦事項。
category: productivity
input_schema:
  content: "會議對話或文字內容 (必填)"
  meeting_title: "(選填) 會議標題"
  meeting_date: "(選填) 會議日期"
  participants: "(選填) 出席者列表"
---
# Meeting Minutes 會議紀錄助手

## 功能說明

此技能可將會議的對話文字或逐字稿轉換為結構化的會議紀錄。

## 輸入參數

| 參數 | 必填 | 說明 |
|------|------|------|
| content | ✅ | 會議對話或逐字稿內容 |
| meeting_title | ❌ | 會議標題 (若未提供，AI 會自動推斷) |
| meeting_date | ❌ | 會議日期 |
| participants | ❌ | 出席者列表 |

## 輸出格式

```markdown
## 會議主題
[自動推斷或使用者提供]

**日期**: YYYY-MM-DD
**出席者**: A, B, C...

### 討論事項
- 議題一摘要
- 議題二摘要

### 決議事項
1. 決議內容

### 待辦追蹤
| 負責人 | 待辦事項 | 截止日 |
|--------|----------|--------|
| A      | 完成報告 | 01/30  |
```

## 使用範例

**輸入**:
```json
{
  "content": "Tony: 今天主要討論 Q1 預算...\nMary: 我建議增加 10%...",
  "meeting_title": "Q1 預算會議"
}
```

**輸出**: 結構化會議紀錄 (Markdown 格式)

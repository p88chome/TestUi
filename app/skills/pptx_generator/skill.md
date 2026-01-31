---
name: pptx_generator
description: >
  PowerPoint 簡報自動生成工具：根據內容大綱自動建立專業簡報。
  適用於自動生成簡報、客戶提案、報告簡報、培訓教材等場景。
  當使用者提及 PPT、PowerPoint、簡報、投影片、提案時使用此技能。
category: document
keywords:
  - pptx
  - powerpoint
  - 簡報
  - 投影片
  - 提案
  - 報告
  - 培訓
triggers:
  - "建立簡報"
  - "生成 PPT"
  - "製作投影片"
  - "客戶提案"
  - "報告簡報"
input_schema:
  operation: "操作類型 ('create_from_outline', 'create_from_template', 'add_slide')"
  title: "簡報標題"
  slides: "投影片內容列表，每個包含 title, content, layout"
  template_path: "(選填) 模板檔案路徑"
  output_path: "(選填) 輸出檔案路徑"
  theme: "(選填) 主題風格 'professional', 'creative', 'minimal'"

---

# PPTX Generator Skill

## 功能說明

自動生成 PowerPoint 簡報，支援：
- 從大綱內容生成完整簡報
- 多種投影片版型（標題、內容、兩欄、圖文）
- 專業配色主題
- 自動添加頁碼和標題

## 操作類型

### 1. create_from_outline
根據大綱內容自動生成完整簡報

**輸入範例：**
```json
{
  "operation": "create_from_outline",
  "title": "2024 年度報告",
  "slides": [
    {"title": "簡介", "content": ["公司概況", "本年度成就"], "layout": "title"},
    {"title": "財務表現", "content": ["營收成長 25%", "淨利潤提升"], "layout": "bullet"},
    {"title": "未來展望", "content": "持續創新，擴展市場", "layout": "content"}
  ],
  "theme": "professional"
}
```

### 2. add_slide
為現有簡報添加投影片

### 3. create_from_template
使用現有模板生成簡報

## 版型選項 (layout)

| 版型 | 說明 |
|------|------|
| title | 標題頁（大標題 + 副標題）|
| bullet | 項目符號列表 |
| content | 純文字內容 |
| two_column | 雙欄對比 |
| image_text | 圖文並排 |
| section | 章節分隔頁 |

## 主題選項 (theme)

| 主題 | 配色 |
|------|------|
| professional | 深藍 + 白色（商務風格）|
| creative | 紫色 + 橘色（創意風格）|
| minimal | 黑白灰（極簡風格）|
| deloitte | Deloitte Green（企業風格）|

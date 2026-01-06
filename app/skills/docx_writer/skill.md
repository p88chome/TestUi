name: docx_writer
description: 處理 Word 文件：生成報告、插入表格、段落排版。
category: legal
input_schema:
  operation: "操作類型 ('create_report', 'append_table')"
  output_path: "輸出文件路徑"
  content: "內容列表 (Paragraphs)"
  headers: "(選填) 表格標題 (List of strings)"
  rows: "(選填) 表格資料 (List of lists)"
---
# Docx Writer 指南

## 支援操作

### 1. create_report
建立一份新的報告文件。
- **輸入**:
    - `output_path`: 檔案儲存路徑 (e.g. "report.docx")
    - `content`: 段落列表。支援簡單的格式標記 (例如開頭用 "# " 表示標題)。
        - 範例: `["# 查核報告", "本所已完成...", "## 查核結果", "無異常。"]`
- **輸出**: 成功訊息。

### 2. append_table
在現有文件 (或新文件) 中插入表格。
- **輸入**:
    - `output_path`: 目標文件 (若不存在則建立)
    - `headers`: 表格欄位名稱
    - `rows`: 表格資料內容 (List of Lists)
- **輸出**: 成功訊息。

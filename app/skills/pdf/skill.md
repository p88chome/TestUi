name: pdf_manager
description: 處理 PDF 文件：提取文字、讀取 Metadata、合併文件。
category: document
input_schema:
  operation: "操作類型 ('extract_text', 'get_metadata', 'merge')"
  files: "PDF 檔案路徑列表"
  output_path: "(選填) 合併後的輸出路徑"
---
# PDF Manager 指南

## 支援操作

### 1. extract_text
從 PDF 中提取文字。優先使用 `pdfplumber` 進行高品質提取。
- **輸入**: `files` (單個或多個 PDF 路徑)
- **輸出**: 字典，鍵為檔名，值為提取出的文字內容。

### 2. get_metadata
讀取 PDF 的 Metadata (Title, Author, Pages 等)。
- **輸入**: `files` (單個或多個 PDF 路徑)
- **輸出**: 字典，鍵為檔名，值為 Metadata 字典。

### 3. merge
將多個 PDF 合併為一個。
- **輸入**: 
    - `files` (按順序排列的 PDF 路徑列表)
    - `output_path` (儲存路徑，選填，預設為 `merged_output.pdf`)
- **輸出**: 成功訊息及輸出路徑。

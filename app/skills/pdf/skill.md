---
name: pdf_manager
description: >
  PDF 文件處理工具包：提取文字和表格、讀取 Metadata、合併/分割文件。
  適用於讀取 PDF 內容、分析 PDF 結構、合併多個 PDF、從 PDF 提取表格資料等場景。
  當使用者提及 PDF、文件提取、表格識別、合併 PDF 時使用此技能。
category: document
keywords:
  - pdf
  - 文件
  - 提取文字
  - 表格
  - 合併
  - metadata
  - 文件處理
triggers:
  - "讀取 PDF"
  - "提取 PDF 內容"
  - "合併 PDF"
  - "PDF 表格"
  - "文件資訊"
input_schema:
  operation: "操作類型 ('extract_text', 'extract_tables', 'get_metadata', 'merge', 'split')"
  files: "PDF 檔案路徑列表"
  output_path: "(選填) 輸出路徑"
  pages: "(選填) 頁面範圍，如 '1-5' 或 [1, 3, 5]"
---

# PDF Manager 指南

## 概述

這個技能專門用於處理 PDF 文件。使用 `pdfplumber` 進行高品質文字和表格提取，使用 `pypdf` 進行 PDF 操作（合併、分割、旋轉）。

**核心能力**：
- 提取 PDF 文字內容（保留排版）
- 提取 PDF 表格（轉為結構化資料）
- 讀取 PDF Metadata
- 合併多個 PDF
- 分割 PDF（按頁面）

## 支援操作

### 1. extract_text
從 PDF 中提取文字。優先使用 `pdfplumber` 進行高品質提取。
- **輸入**: `files` (單個或多個 PDF 路徑)
- **輸出**: 字典，鍵為檔名，值為提取出的文字內容。

**使用場景**：
- 需要讀取 PDF 文件內容
- 將 PDF 轉為可搜尋的文字

### 2. extract_tables
從 PDF 中提取表格資料。
- **輸入**: `files` (單個或多個 PDF 路徑)
- **輸出**: 字典，鍵為檔名，值為表格列表（每個表格是 List of Lists）。

**使用場景**：
- PDF 中包含財務報表
- 需要將 PDF 表格轉為 Excel
- 分析 PDF 中的結構化資料

### 3. get_metadata
讀取 PDF 的 Metadata (Title, Author, Pages 等)。
- **輸入**: `files` (單個或多個 PDF 路徑)
- **輸出**: 字典，鍵為檔名，值為 Metadata 字典。

### 4. merge
將多個 PDF 合併為一個。
- **輸入**: 
    - `files` (按順序排列的 PDF 路徑列表)
    - `output_path` (儲存路徑，選填，預設為 `merged_output.pdf`)
- **輸出**: 成功訊息及輸出路徑。

### 5. split
將 PDF 分割為多個單頁 PDF。
- **輸入**: 
    - `files` (單個 PDF 路徑)
    - `output_path` (輸出目錄，選填)
    - `pages` (選填，指定要分割的頁面)
- **輸出**: 分割後的檔案路徑列表。

## 注意事項

⚠️ **掃描版 PDF**：如果 PDF 是掃描圖片，可能需要先使用 OCR 處理。

⚠️ **大型檔案**：處理大型 PDF 可能需要較長時間，請耐心等待。

⚠️ **加密 PDF**：加密的 PDF 需要先解密才能處理。

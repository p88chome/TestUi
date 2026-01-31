---
name: excel_handler
description: >
  Excel 試算表處理工具：讀取、寫入、資料分析、統計計算。
  適用於讀取 Excel 資料、寫入報表、資料分析、欄位統計等場景。
  當使用者提及 Excel、試算表、XLSX、資料分析、報表時使用此技能。
category: finance
keywords:
  - excel
  - xlsx
  - 試算表
  - 資料分析
  - 報表
  - 統計
  - 財務
  - 表格
triggers:
  - "讀取 Excel"
  - "寫入 Excel"
  - "資料分析"
  - "Excel 報表"
  - "統計資料"
  - "匯出 Excel"
input_schema:
  operation: "操作類型 ('read_sheet', 'write_sheet', 'analyze', 'list_sheets')"
  file_path: "Excel 檔案路徑"
  data: "(選填) 寫入時的資料 (List of Lists or List of Dicts)"
  sheet_name: "(選填) 工作表名稱"
  columns: "(選填) 指定讀取的欄位列表"
---

# Excel Handler 指南

## 概述

這個技能專門用於處理 Excel 試算表。使用 `pandas` 進行資料操作和分析，使用 `openpyxl` 進行 Excel 檔案讀寫。

**核心能力**：
- 讀取 Excel 工作表
- 寫入資料到 Excel
- 資料統計分析
- 多工作表處理

## 支援操作

### 1. read_sheet
讀取 Excel 工作表內容。
- **輸入**: 
    - `file_path`: 檔案路徑
    - `sheet_name` (選填): 預設讀取第一個 Sheet
    - `columns` (選填): 指定讀取的欄位
- **輸出**: JSON 格式的資料 (Records 格式，即 List of Dicts)。

**使用場景**：
- 讀取財務報表資料
- 載入資料進行後續處理

### 2. write_sheet
將資料寫入 Excel (會覆蓋或建立新檔案)。
- **輸入**:
    - `file_path`: 目標路徑
    - `data`: 資料內容 (支援 List of Dicts)
    - `sheet_name` (選填): 預設為 "Sheet1"
- **輸出**: 成功訊息。

**使用場景**：
- 匯出分析結果
- 建立報表

### 3. analyze
對 Excel 資料進行統計分析。
- **輸入**:
    - `file_path`: 檔案路徑
    - `sheet_name` (選填): 工作表名稱
- **輸出**: 資料統計資訊（欄位類型、平均值、最大最小值等）

**使用場景**：
- 快速瞭解資料概況
- 財務資料統計

### 4. list_sheets
列出 Excel 檔案中的所有工作表。
- **輸入**: `file_path`: 檔案路徑
- **輸出**: 工作表名稱列表

## 最佳實踐

### 公式處理
- 讀取資料時預設讀取計算後的值
- 寫入時使用 Excel 公式而非硬編碼值

### 資料格式
- 日期欄位會自動轉換為 ISO 格式字串
- 數值欄位保持原始精度
- 空值會轉換為 null

## 注意事項

⚠️ **大型檔案**：處理超過 10 萬行的資料可能需要較長時間。

⚠️ **公式保留**：write_sheet 會覆蓋現有內容，原有公式會遺失。

⚠️ **編碼問題**：確保檔案路徑不包含特殊字元。

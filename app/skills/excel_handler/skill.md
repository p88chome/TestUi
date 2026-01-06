name: excel_handler
description: 處理 Excel 文件：讀取、寫入、財務分析。
category: finance
input_schema:
  operation: "操作類型 ('read_sheet', 'write_sheet')"
  file_path: "Excel 檔案路徑"
  data: "(選填) 寫入時的資料 (List of Lists or List of Dicts)"
  sheet_name: "(選填) 工作表名稱"
---
# Excel Handler 指南

## 支援操作

### 1. read_sheet
讀取 Excel 工作表內容。
- **輸入**: 
    - `file_path`: 檔案路徑
    - `sheet_name` (選填): 預設讀取第一個 Sheet
- **輸出**: JSON 格式的資料 (Records 格式，即 List of Dicts)。

### 2. write_sheet
將資料寫入 Excel (會覆蓋或建立新檔案)。
- **輸入**:
    - `file_path`: 目標路徑
    - `data`: 資料內容 (支援 List of Dicts)
    - `sheet_name` (選填): 預設為 "Sheet1"
- **輸出**: 成功訊息。

### 3. analyze_financials (Future)
(保留擴充：計算財務比率)

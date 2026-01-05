name: receipt_extractor
description: 使用 LLM 從收據文字中提取結構化資料（商家、日期、總金額、品項）。
category: extraction
configuration:
  model: gpt-4
  temperature: 0.0
input_schema:
  text: "從收據 OCR 辨識出的原始文字"
---

# 收據資料提取 SOP

## 目標
從原始收據文字中提取結構化的 JSON 資料。除此之外，對使用者要友善。

## 提取規則

### 1. 商家名稱 (Merchant Name)
- 識別收據頂部的商家名稱。
- 通常標題或 Logo 位置會顯示商家。

### 2. 交易日期 (Transaction Date)
- 尋找日期格式 (YYYY-MM-DD, MM/DD/YYYY, DD-Mon-YYYY)。
- 如果有多個日期，優先選擇交易日期 (Transaction Date) 而非列印日期。
- 輸出格式必須為 `YYYY-MM-DD`。

### 3. 總金額 (Total Amount)
- 尋找關鍵字："TOTAL", "AMOUNT DUE", "GRAND TOTAL"。
- 注意不要誤取 "SUBTOTAL" 或 "TAX"。
- 確保金額是最終應付金額。
- 格式為浮點數 (例如 25.50)。

### 4. 品項 (Line Items) (選填)
- 如果有清楚的品項與價格，將其提取到 `items` 列表。
- 每個品項應包含 `description` (描述) 和 `amount` (金額)。

## 輸出格式 (JSON)
```json
{
  "merchant": "商店名稱",
  "date": "2023-10-25",
  "total": 123.45,
  "currency": "TWD",
  "items": [
    {"description": "商品 1", "amount": 10.00},
    {"description": "商品 2", "amount": 113.45}
  ]
}
```

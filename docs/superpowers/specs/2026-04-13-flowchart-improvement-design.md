# Flowchart Generator 改善設計

**日期：** 2026-04-13
**狀態：** 已核准
**範圍：** AI 生成品質（A1）+ PPTX 匯出（B1 主 / B2 備用）

---

## 背景

目前流程圖生成器有兩個核心問題：

1. **AI 生成品質不穩** — DECOMPOSE 和 RENDER 兩個 prompt 硬編碼在 `app/routers/flowchart.py`，無法在不重新部署的情況下迭代；prompt 缺乏業務規則與範例，導致節點漏接、決策分支不完整、泳道角色命名不一致。

2. **PPTX 匯出品質差** — 存在 oval shape double-add bug；節點採純垂直堆疊（忽略連線順序）；箭頭為直線穿越其他節點；泳道無背景色；配色非 Deloitte 品牌色。

前端互動（拖移、編輯節點）已由 Vue Flow 處理，不在本次範圍內。

---

## 設計

### 改動 1：建立 flowchart_generator skill（A1）

#### 目標
將 AI 提示詞移出 Python 程式碼，放入可即時編輯的 `skill.md`，並注入業務規則與 few-shot 範例，提升生成品質。

#### 檔案結構

```
app/skills/flowchart_generator/
  skill.md          ← 兩段 prompt + 業務規則 + few-shot 範例
  run.py            ← execute() 解析 skill.md 並呼叫 LLM
  examples/
    cs104_sales_order.json    ← 銷售接單作業範例
    ca101_asset_acquisition.json  ← 固定資產取得作業範例
```

#### skill.md 內容結構

```
---
name: flowchart_generator
description: 將內控 SOP 文件轉換成泳道流程圖（nodes/edges JSON + Mermaid）
category: enterprise
keywords: [flowchart, 流程圖, SOP, 內控, swimlane, 作業程序]
input_schema:
  doc_text: string
  additional_context: string
  modification: string
---

# DECOMPOSE_PROMPT
（拆解文件為結構化步驟的完整 system prompt）

# RENDER_PROMPT
（將步驟渲染為 nodes/edges + Mermaid 的完整 system prompt）

# BUSINESS_RULES
（ISO 9001 對應規則，待與顧問確認後可更新）

# FEW_SHOT_EXAMPLES
（真實文件範例 — 見下方）
```

#### ISO 9001 業務規則（初版）

- 每條流程必有且只有一個 `start` 節點與一個 `end` 節點
- 控制重點（核准 / 審查 / 複核）→ `is_decision: true`，分支條件必須同時填入 `condition_yes` 和 `condition_no`
- 使用表單或產出文件 → `generates_document` 填正式表單名稱
- 泳道（lane）命名使用職位，例如「申請人」、「部門主管」、「財務部」，不使用部門縮寫
- 決策節點 `action` 文字必須以「？」結尾
- 退回流程必須連回原始申請步驟（不得懸空終止）
- 動作描述限 15 字以內

> ⚠️ 業務規則待與公司顧問確認後可直接在前端 Skill 編輯器更新 skill.md，無需重新部署後端。

#### Few-shot 範例來源

| 範例 | 來源文件 | 描述 |
|------|----------|------|
| 銷售接單作業 | 竑騰科技 CS-104 | 報價→審核→接單，含產品牌價表、報價單 |
| 固定資產取得 | 卡訊電子 CA-101 | 請購→審核→驗收入帳，含固資請購單 |

#### flowchart.py 改法

- 移除 `DECOMPOSE_PROMPT` 和 `RENDER_PROMPT` 常數
- 新增 helper `_load_flowchart_prompts(db)` 從 skill 讀取：

```python
def _load_flowchart_prompts(db: Session) -> tuple[str, str]:
    skill = db.query(Skill).filter_by(name="flowchart_generator").first()
    if not skill:
        return FALLBACK_DECOMPOSE, FALLBACK_RENDER  # 內建備用
    instructions = skill.configuration.get("instructions", "")
    # skill.md 用 "# DECOMPOSE_PROMPT" / "# RENDER_PROMPT" 分節
    decompose = _extract_section(instructions, "DECOMPOSE_PROMPT")
    render    = _extract_section(instructions, "RENDER_PROMPT")
    return decompose or FALLBACK_DECOMPOSE, render or FALLBACK_RENDER
```

- `_extract_section(text, name)` 抓取 `# {name}` 到下一個 `# ` 之間的內容
- skill 載入失敗或 section 缺失時自動 fallback，避免服務中斷
- `run.py` 的 `execute()` 為佔位實作（flowchart 路由直接呼叫 router，不走 `/skills/{name}/run` endpoint）

---

### 改動 2：修 PPTX 渲染邏輯（B1）

#### 修正項目

| 問題 | 修正方式 |
|------|----------|
| oval double-add bug | 改用 `MSO_AUTO_SHAPE_TYPE` 常數，移除重複 `add_shape` 邏輯 |
| 節點純垂直堆疊 | BFS 拓撲排序：從 start 節點沿 edges 決定各節點的 y 座標層級 |
| 箭頭直線穿越節點 | 改用 `MSO_CONNECTOR_TYPE.ELBOW`（彎折箭頭） |
| 泳道無背景色 | 每個 lane 在節點下方繪製淡色背景矩形（顏色交替，透明度 15%） |
| 配色非品牌色 | 改為 Deloitte 色系（見下表） |

#### Deloitte 配色

| 節點類型 | 填充色 | 說明 |
|----------|--------|------|
| start | `#86BC25` | Deloitte Green |
| end | `#000000` | Black |
| process | `#2C2C2C` | Charcoal |
| control | `#F5A623` | Warning Orange（決策點） |
| document | `#666666` | Gray（文件節點） |

#### 節點定位演算法

```
1. 找出所有無 incoming edge 的節點 → 視為 start 層（y=0）
2. BFS 遍歷 edges，每個節點的 y 層 = max(前驅節點層) + 1
3. 同層節點在各自的 lane 內水平居中
4. document 節點（側分支）放在觸發節點右側，不佔主流 y 層
```

---

### 改動 3：B2 備用匯出（複雜流程）

#### 使用時機
當 B1 的 python-pptx 渲染在複雜流程（跨泳道多、回流節點多）下視覺效果仍不理想，提供「高保真圖片」模式。

#### 後端

新增 endpoint：

```
POST /flowchart/export-pptx-image
Body: { image_base64: string, title: string }
```

邏輯：將 base64 圖片嵌入 PPTX slide，填滿可用區域，slide 頂部加標題文字框。

#### 前端

- 匯出按鈕旁新增 toggle：「可編輯圖形」（B1）/ 「高保真圖片」（B2）
- 選擇 B2 時：呼叫 `html2canvas` 對 Vue Flow 畫布截圖 → base64 → POST 至新 endpoint
- 匯出的 PPTX 內容為圖片，形狀不可編輯（在 UI 上明確說明）

---

## 執行順序

1. **改動 1（skill.md + flowchart.py 重構）** — 獨立；完成後 AI 品質立即提升，且 prompt 可在前端即時編輯
2. **改動 2（B1 PPTX 修正）** — 獨立；可與改動 1 並行執行，不互相依賴
3. **改動 3（B2 備用匯出）** — 獨立；優先度最低，待 B1 效果驗證後再執行

---

## 不在範圍內

- 前端 Vue Flow 畫布互動（已完成）
- Meeting AI / Policy Analysis 改善
- Multi-tenant skill 授權機制（另案規劃）
- RBAC 角色權限系統（另案規劃）

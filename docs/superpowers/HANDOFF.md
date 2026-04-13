# Agent Handoff — Flowchart Generator 改善

**日期：** 2026-04-13
**狀態：** Brainstorm + Plan 完成，等待執行

---

## 你接手的任務

執行流程圖生成器的三項改善。**所有設計決策已完成，不需要再 brainstorm。**

---

## 關鍵文件（先讀這兩個）

| 文件 | 路徑 | 說明 |
|------|------|------|
| 設計 Spec | `docs/superpowers/specs/2026-04-13-flowchart-improvement-design.md` | 為什麼這樣做 |
| **Implementation Plan** | `docs/superpowers/plans/2026-04-13-flowchart-improvement.md` | **你要執行的內容，逐步有 code** |

---

## 三個獨立 Task，互不依賴

### Task 1 — skill.md（A1）⭐ 最重要，先做

把硬編碼的 AI prompt 搬進可即時編輯的 skill 檔。

**你要建立的檔案：**
```
app/skills/flowchart_generator/skill.md   ← Plan 裡有完整內容，直接複製
app/skills/flowchart_generator/run.py
app/skills/flowchart_generator/examples/cs104_sales_order.json
app/skills/flowchart_generator/examples/ca101_asset_acquisition.json
```

**你要修改：**
- `app/routers/flowchart.py` — 加 `_extract_section()` + `_load_flowchart_prompts()`，更新兩個 endpoint

**測試：** `tests/test_flowchart.py`（Plan 內有完整測試 code）

---

### Task 2 — PPTX 修正（B1）

重寫 `export_pptx` 函數（Plan 內有完整替換 code）：
- 加 `_topo_sort_layers()` 函數（BFS 拓撲排序節點位置）
- 修 oval double-add bug（改用 `MSO_AUTO_SHAPE_TYPE` 常數）
- 泳道加淡色背景矩形
- 箭頭改 `MSO_CONNECTOR_TYPE.ELBOW`
- 換 Deloitte 配色

**測試：** Plan 內有 3 個 topo sort 單元測試

---

### Task 3 — B2 圖片匯出（備用）

優先度最低，前兩個做完再做。

- 後端：新增 `POST /flowchart/export-pptx-image` endpoint
- 前端：`FlowchartGeneratorPage.vue` 加 toggle + `html2canvas` 截圖邏輯
- 需先 `npm install html2canvas`

---

## 現有程式碼要知道的事

| 事項 | 說明 |
|------|------|
| 後端框架 | FastAPI，主要入口 `app/main.py` |
| 流程圖 router | `app/routers/flowchart.py`，獨立不走 skill 系統 |
| Skill 載入機制 | `app/services/skill_loader.py` — 掃描 `app/skills/*/skill.md` + `run.py` |
| 測試 | `pytest`，`pytest.ini` 在根目錄，test db 用 `tests/conftest.py` 的 `db_session` fixture |
| 前端 | Vue 3 + PrimeVue，位於 `frontend/src/` |
| Vue Flow | 已安裝但需 `npm install`（node_modules 不完整）|
| 範例文件 | `archive/` 資料夾有真實內控文件（.docx），skill.md 的 few-shot 範例就是從這裡來的 |

---

## 執行方式

使用 `superpowers:executing-plans` skill 或 `superpowers:subagent-driven-development` skill。

Plan 每個 step 都有完整 code，不需要自己想怎麼寫，照著做即可。

**執行順序：Task 1 → Task 2 → Task 3**（Task 1 和 2 也可並行）

---

## 完成後的驗收標準

```bash
pytest tests/test_flowchart.py -v
# 預期：9 tests PASSED
```

前端手動測試：
1. 上傳任意 .docx 內控文件
2. AI 生成流程圖（節點/泳道正確）
3. 匯出 PPTX → 確認泳道有背景色、箭頭不穿越節點
4. 切換高保真模式 → 匯出 PPTX → 確認是圖片版本

# Flowchart Generator 改善 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 將流程圖的 AI prompt 搬入可即時編輯的 skill.md（A1），修正 PPTX 匯出的 bug 與視覺問題（B1），並新增高保真圖片匯出備用模式（B2）。

**Architecture:** A1 建立 `flowchart_generator` skill，`flowchart.py` 從 DB 讀取 prompt；B1 重寫 `export_pptx` 函數加入拓撲排序與泳道背景；B2 新增 `export-pptx-image` endpoint，前端用 html2canvas 截圖傳入。三個任務互相獨立，可並行。

**Tech Stack:** FastAPI, python-pptx, SQLAlchemy, Vue 3, html2canvas, pytest

---

## 檔案地圖

| 動作 | 路徑 | 說明 |
|------|------|------|
| 新建 | `app/skills/flowchart_generator/skill.md` | 完整 prompt + 業務規則 + few-shot |
| 新建 | `app/skills/flowchart_generator/run.py` | execute() 佔位實作 |
| 新建 | `app/skills/flowchart_generator/examples/cs104_sales_order.json` | 範例 1 |
| 新建 | `app/skills/flowchart_generator/examples/ca101_asset_acquisition.json` | 範例 2 |
| 修改 | `app/routers/flowchart.py` | 移除硬編碼 prompt，加 `_extract_section` / `_load_flowchart_prompts` / PPTX 修正 / B2 endpoint |
| 新建 | `tests/test_flowchart.py` | 單元測試 |

---

## Task 1：建立 flowchart_generator skill（A1）

**Files:**
- Create: `app/skills/flowchart_generator/skill.md`
- Create: `app/skills/flowchart_generator/run.py`
- Create: `app/skills/flowchart_generator/examples/cs104_sales_order.json`
- Create: `app/skills/flowchart_generator/examples/ca101_asset_acquisition.json`
- Test: `tests/test_flowchart.py`

---

- [ ] **Step 1.1：建立 skill 目錄與 run.py**

```python
# app/skills/flowchart_generator/run.py
"""
Flowchart Generator Skill
execute() 為佔位實作 — 實際流程圖生成走 /flowchart/analyze router，
此 skill 的價值在於讓 skill.md 的 prompt 可透過前端即時編輯。
"""

def execute(input_data: dict) -> dict:
    return {
        "status": "info",
        "message": "Flowchart generation is handled by /flowchart/analyze endpoint. Edit skill.md to update AI prompts."
    }
```

- [ ] **Step 1.2：建立 skill.md**

```markdown
<!-- app/skills/flowchart_generator/skill.md -->
name: flowchart_generator
description: 將內控 SOP 文件轉換成泳道流程圖（nodes/edges JSON + Mermaid）
category: enterprise
keywords: [flowchart, 流程圖, SOP, 內控, swimlane, 作業程序, ISO9001]
input_schema:
  doc_text: string
  additional_context: string
  modification: string
---

# DECOMPOSE_PROMPT

你是一位資深的內部控制顧問，專精 ISO 9001 品質管理系統與台灣上市公司內控制度。
請仔細閱讀以下的作業程序說明（可能是 SOP、內控制度文件、Email 或逐字稿），
將其拆解成一個清晰的、結構化的流程步驟清單。

## 輸出格式（只輸出 JSON，不加任何 Markdown 語法或多餘說明）

{
  "title": "流程名稱",
  "summary": "一段話說明這個流程的目的與範圍",
  "steps": [
    {
      "id": "step_1",
      "action": "動作描述，精簡（15字以內）",
      "role": "負責職位（用於泳道分組）",
      "is_decision": false,
      "condition_yes": null,
      "condition_no": null,
      "next_ids": ["step_2"],
      "generates_document": null
    },
    {
      "id": "step_2",
      "action": "主管審核申請單？",
      "role": "部門主管",
      "is_decision": true,
      "condition_yes": "step_3",
      "condition_no": "step_1",
      "next_ids": ["step_3", "step_1"],
      "generates_document": "採購申請單"
    }
  ]
}

## ISO 9001 業務規則（必須遵守）

1. 每條流程必有且只有一個 start 步驟（無 incoming 連線）與一個 end 步驟
2. 控制重點（核准／審查／複核）必須設為 is_decision: true
3. is_decision 為 true 時，condition_yes 和 condition_no 都必須填入對應的 step id，不得為 null
4. generates_document 只填正式表單或文件名稱（如「產品牌價表」「固資請購單」），不填動作描述
5. role（泳道）命名使用職位（申請人、部門主管、財務部、會計單位），不使用部門縮寫
6. action 文字：決策節點必須以「？」結尾；一般步驟用動詞開頭，15 字以內
7. 退回流程（condition_no）必須連回原始申請步驟，不得連到 end 或懸空

## Few-Shot 範例

### 範例 1：CS-104 銷售接單作業

輸入文件摘要：
「營運業務部依據產品別、單位成本、市場行情編制產品牌價表，經財務單位會簽並核准後公告。
接獲客戶訂單後，確認庫存與交期，若可接受則建立內部訂單，若不可接受則通知客戶。」

輸出：
{
  "title": "銷售接單作業",
  "summary": "規範從產品報價、訂單審查到建立內部訂單的完整銷售前置流程",
  "steps": [
    {"id":"s1","action":"編制產品牌價表","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s2"],"generates_document":"產品牌價表"},
    {"id":"s2","action":"財務會簽核准？","role":"財務單位","is_decision":true,"condition_yes":"s3","condition_no":"s1","next_ids":["s3","s1"],"generates_document":null},
    {"id":"s3","action":"公告牌價並報價","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s4"],"generates_document":"報價單"},
    {"id":"s4","action":"訂單可接受？","role":"營運業務部","is_decision":true,"condition_yes":"s5","condition_no":"s6","next_ids":["s5","s6"],"generates_document":null},
    {"id":"s5","action":"建立內部訂單","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s7"],"generates_document":"內部訂單"},
    {"id":"s6","action":"通知客戶無法接單","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s7"],"generates_document":null},
    {"id":"s7","action":"結束","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":[],"generates_document":null}
  ]
}

### 範例 2：CA-101 不動產、廠房及設備取得作業

輸入文件摘要：
「保管單位填具列管固資請購單，經財務部確認是否符合固資定義及預算，再送權責主管核准。
核准後轉採購及付款循環辦理，完成驗收後入帳列管。」

輸出：
{
  "title": "不動產、廠房及設備取得作業",
  "summary": "規範固定資產從請購申請、預算確認、主管核准到驗收入帳的完整流程",
  "steps": [
    {"id":"a1","action":"填具固資請購單","role":"保管單位","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a2"],"generates_document":"列管固資請購單"},
    {"id":"a2","action":"符合固資定義且在預算內？","role":"財務部","is_decision":true,"condition_yes":"a3","condition_no":"a1","next_ids":["a3","a1"],"generates_document":null},
    {"id":"a3","action":"送權責主管審核","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a4"],"generates_document":null},
    {"id":"a4","action":"主管核准？","role":"權責主管","is_decision":true,"condition_yes":"a5","condition_no":"a1","next_ids":["a5","a1"],"generates_document":null},
    {"id":"a5","action":"轉採購及付款循環","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a6"],"generates_document":null},
    {"id":"a6","action":"驗收並入帳列管","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a7"],"generates_document":"固資盤點清冊"},
    {"id":"a7","action":"結束","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":[],"generates_document":null}
  ]
}

# RENDER_PROMPT

你是流程圖繪製專家，專精內控泳道流程圖。根據以下的結構化流程步驟清單，同時產出兩種格式：
1. nodes/edges JSON（用於前端 Vue Flow 渲染）
2. Mermaid flowchart 語法（用於文字視圖）

## nodes/edges 格式規則

- 節點 type 只能是：start / end / process / control / document
- control：決策點（is_decision: true）；diamond 形狀
- document：文件節點（generates_document 不為 null）；parallelogram 形狀；以側邊虛線連到產生它的步驟，不在主流上
- 每個節點必須有 lane 欄位（對應步驟的 role）
- start / end 節點各只能有一個

## Mermaid 格式規則

- 使用 flowchart TD（由上至下）
- 決策點用菱形 {動作}
- 文件節點用 /文件名/，用虛線連接（-.->）
- start 用 ([開始])，end 用 ([結束])，套用 classDef

## 輸出格式（只輸出 JSON，不加任何 Markdown 語法）

{
  "explanation": "用繁體中文說明這個流程圖的主要結構、涉及角色與關鍵控制點",
  "nodes": [
    {"id": "node_1", "type": "start", "label": "開始", "lane": "申請人"},
    {"id": "node_2", "type": "process", "label": "填寫申請單", "lane": "申請人"},
    {"id": "node_3", "type": "control", "label": "主管審核?", "lane": "部門主管"},
    {"id": "node_4", "type": "document", "label": "採購申請單", "lane": "申請人"},
    {"id": "node_5", "type": "end", "label": "結束", "lane": "採購部"}
  ],
  "edges": [
    {"from": "node_1", "to": "node_2", "label": ""},
    {"from": "node_2", "to": "node_3", "label": ""},
    {"from": "node_2", "to": "node_4", "label": "產出"},
    {"from": "node_3", "to": "node_5", "label": "核准"},
    {"from": "node_3", "to": "node_2", "label": "退回"}
  ],
  "mermaid": "flowchart TD\n  node_1([開始]):::start --> node_2[填寫申請單]\n  node_2 --> node_3{主管審核?}\n  node_2 -.->|產出| node_4[/採購申請單/]\n  node_3 -->|核准| node_5([結束]):::end\n  node_3 -->|退回| node_2\n  classDef start fill:#86BC25,color:#fff\n  classDef end fill:#000,color:#fff"
}

# BUSINESS_RULES

（同 DECOMPOSE_PROMPT 中的 ISO 9001 業務規則，此區塊供顧問確認後更新）
待與公司顧問確認後，可直接在前端 Skill 編輯器修改此 skill.md，無需重新部署後端。
```

- [ ] **Step 1.3：建立 few-shot JSON 範例檔**

```json
// app/skills/flowchart_generator/examples/cs104_sales_order.json
{
  "source": "竑騰科技 CS-104 銷售接單作業",
  "steps": {
    "title": "銷售接單作業",
    "summary": "規範從產品報價、訂單審查到建立內部訂單的完整銷售前置流程",
    "steps": [
      {"id":"s1","action":"編制產品牌價表","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s2"],"generates_document":"產品牌價表"},
      {"id":"s2","action":"財務會簽核准？","role":"財務單位","is_decision":true,"condition_yes":"s3","condition_no":"s1","next_ids":["s3","s1"],"generates_document":null},
      {"id":"s3","action":"公告牌價並報價","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s4"],"generates_document":"報價單"},
      {"id":"s4","action":"訂單可接受？","role":"營運業務部","is_decision":true,"condition_yes":"s5","condition_no":"s6","next_ids":["s5","s6"],"generates_document":null},
      {"id":"s5","action":"建立內部訂單","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s7"],"generates_document":"內部訂單"},
      {"id":"s6","action":"通知客戶無法接單","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["s7"],"generates_document":null},
      {"id":"s7","action":"結束","role":"營運業務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":[],"generates_document":null}
    ]
  }
}
```

```json
// app/skills/flowchart_generator/examples/ca101_asset_acquisition.json
{
  "source": "卡訊電子 CA-101 不動產、廠房及設備取得作業",
  "steps": {
    "title": "不動產、廠房及設備取得作業",
    "summary": "規範固定資產從請購申請、預算確認、主管核准到驗收入帳的完整流程",
    "steps": [
      {"id":"a1","action":"填具固資請購單","role":"保管單位","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a2"],"generates_document":"列管固資請購單"},
      {"id":"a2","action":"符合固資定義且在預算內？","role":"財務部","is_decision":true,"condition_yes":"a3","condition_no":"a1","next_ids":["a3","a1"],"generates_document":null},
      {"id":"a3","action":"送權責主管審核","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a4"],"generates_document":null},
      {"id":"a4","action":"主管核准？","role":"權責主管","is_decision":true,"condition_yes":"a5","condition_no":"a1","next_ids":["a5","a1"],"generates_document":null},
      {"id":"a5","action":"轉採購及付款循環","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a6"],"generates_document":null},
      {"id":"a6","action":"驗收並入帳列管","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":["a7"],"generates_document":"固資盤點清冊"},
      {"id":"a7","action":"結束","role":"財務部","is_decision":false,"condition_yes":null,"condition_no":null,"next_ids":[],"generates_document":null}
    ]
  }
}
```

- [ ] **Step 1.4：寫失敗測試**

```python
# tests/test_flowchart.py
import pytest
from app.routers.flowchart import _extract_section, _load_flowchart_prompts
from app.models.skill import Skill, SkillType

SAMPLE_SKILL_MD = """# DECOMPOSE_PROMPT
This is decompose content.
Multi-line content here.

# RENDER_PROMPT
This is render content.
Also multi-line.

# BUSINESS_RULES
Some rules.
"""

def test_extract_section_decompose():
    result = _extract_section(SAMPLE_SKILL_MD, "DECOMPOSE_PROMPT")
    assert "This is decompose content." in result
    assert "RENDER_PROMPT" not in result

def test_extract_section_render():
    result = _extract_section(SAMPLE_SKILL_MD, "RENDER_PROMPT")
    assert "This is render content." in result
    assert "DECOMPOSE_PROMPT" not in result

def test_extract_section_missing():
    result = _extract_section(SAMPLE_SKILL_MD, "NONEXISTENT")
    assert result == ""

def test_load_flowchart_prompts_uses_fallback_when_no_skill(db_session):
    decompose, render = _load_flowchart_prompts(db_session)
    assert len(decompose) > 50   # fallback has content
    assert len(render) > 50

def test_load_flowchart_prompts_reads_from_skill(db_session):
    skill = Skill(
        name="flowchart_generator",
        description="test",
        category="enterprise",
        skill_type=SkillType.PYTHON_FUNC,
        configuration={"instructions": SAMPLE_SKILL_MD},
        is_active=True
    )
    db_session.add(skill)
    db_session.commit()

    decompose, render = _load_flowchart_prompts(db_session)
    assert "This is decompose content." in decompose
    assert "This is render content." in render
```

- [ ] **Step 1.5：執行測試確認失敗**

```
pytest tests/test_flowchart.py -v
```

預期：`ImportError` 或 `AttributeError`（`_extract_section` 尚未定義）

- [ ] **Step 1.6：在 flowchart.py 加入 `_extract_section` 和 `_load_flowchart_prompts`**

在 `app/routers/flowchart.py` 中，在現有的 `DECOMPOSE_PROMPT` 和 `RENDER_PROMPT` 常數**之前**插入：

```python
# ─── Fallback prompts (used when skill not found in DB) ─────────────────────
# Keep these as fallback so the service never breaks even if skill.md is missing.
_FALLBACK_DECOMPOSE = DECOMPOSE_PROMPT   # will be defined below as before
_FALLBACK_RENDER = RENDER_PROMPT         # will be defined below as before
```

然後在兩個常數定義**之後**加入以下函數（在 `_get_llm_url_and_headers` 之前）：

```python
# ─── Skill-based Prompt Loading ──────────────────────────────────────────────

def _extract_section(text: str, section_name: str) -> str:
    """
    Extract content between '# SECTION_NAME' and the next '# ' heading.
    Returns empty string if section not found.
    """
    import re
    pattern = rf"#\s+{re.escape(section_name)}\s*\n(.*?)(?=\n#\s|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _load_flowchart_prompts(db: Session) -> tuple[str, str]:
    """
    Load DECOMPOSE and RENDER prompts from the flowchart_generator skill in DB.
    Falls back to hardcoded prompts if skill is missing or sections not found.
    """
    try:
        from app.models.skill import Skill
        skill = db.query(Skill).filter(Skill.name == "flowchart_generator", Skill.is_active == True).first()
        if not skill:
            return DECOMPOSE_PROMPT, RENDER_PROMPT
        instructions = skill.configuration.get("instructions", "")
        decompose = _extract_section(instructions, "DECOMPOSE_PROMPT")
        render = _extract_section(instructions, "RENDER_PROMPT")
        return (
            decompose if decompose else DECOMPOSE_PROMPT,
            render if render else RENDER_PROMPT,
        )
    except Exception:
        return DECOMPOSE_PROMPT, RENDER_PROMPT
```

- [ ] **Step 1.7：更新 `_decompose_to_steps` 和 `_render_steps_to_diagram` 接受 prompt 參數**

將現有的兩個函數簽名改為接受 prompt 參數：

```python
async def _decompose_to_steps(gateway, user_id: int, doc_text: str,
                               extra: str = "", prompt: str = None) -> dict:
    system_prompt = prompt if prompt else DECOMPOSE_PROMPT
    user_content = f"請將以下內容拆解成結構化流程步驟清單：\n\n---\n{doc_text}\n---"
    if extra:
        user_content += f"\n\n補充說明：{extra}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    resp = await gateway.chat(messages=messages, user_id=user_id, temperature=0.1, app_name="Flowchart-Decompose")
    raw = resp["choices"][0]["message"]["content"]
    return _parse_llm_json(raw)


async def _render_steps_to_diagram(gateway, user_id: int, steps_data: dict,
                                    modification: str = "", prompt: str = None) -> dict:
    system_prompt = prompt if prompt else RENDER_PROMPT
    steps_json = json.dumps(steps_data, ensure_ascii=False, indent=2)
    user_content = f"請根據以下結構化步驟清單，產出流程圖的 nodes/edges JSON 以及 Mermaid 語法：\n\n```json\n{steps_json}\n```"
    if modification:
        user_content += f"\n\n⚠️ 使用者補充修改要求：{modification}\n（請先按修改要求調整步驟結構，再輸出圖形格式）"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    resp = await gateway.chat(messages=messages, user_id=user_id, temperature=0.1, app_name="Flowchart-Render")
    raw = resp["choices"][0]["message"]["content"]
    return _parse_llm_json(raw)
```

- [ ] **Step 1.8：更新 `analyze_document` endpoint 使用 skill prompt**

在 `analyze_document` 函數的 `gateway = LLMGateway(db)` 行之後加入：

```python
decompose_prompt, render_prompt = _load_flowchart_prompts(db)
```

然後將兩個 LLM 呼叫改為傳入 prompt：

```python
steps_data = await _decompose_to_steps(
    gateway, current_user.id, doc_text, additional_context or "",
    prompt=decompose_prompt
)
diagram_data = await _render_steps_to_diagram(
    gateway, current_user.id, steps_data,
    prompt=render_prompt
)
```

在 `flowchart_chat` endpoint 的對應位置同樣加入 `_load_flowchart_prompts(db)` 並傳入。

- [ ] **Step 1.9：執行測試確認通過**

```
pytest tests/test_flowchart.py::test_extract_section_decompose \
       tests/test_flowchart.py::test_extract_section_render \
       tests/test_flowchart.py::test_extract_section_missing \
       tests/test_flowchart.py::test_load_flowchart_prompts_uses_fallback_when_no_skill \
       tests/test_flowchart.py::test_load_flowchart_prompts_reads_from_skill \
       -v
```

預期：5 tests PASSED

- [ ] **Step 1.10：刷新 skill 讓 DB 載入**

```bash
# 啟動後端後執行（或在 /skills/refresh endpoint 觸發）
curl -X POST http://localhost:8000/api/v1/skills/refresh \
     -H "Authorization: Bearer <token>"
```

確認 `flowchart_generator` 出現在 `GET /api/v1/skills/` 回傳清單中。

- [ ] **Step 1.11：Commit**

```bash
git add app/skills/flowchart_generator/ \
        app/routers/flowchart.py \
        tests/test_flowchart.py
git commit -m "feat: move flowchart prompts to skill.md with ISO9001 rules and few-shot examples"
```

---

## Task 2：修 PPTX 渲染邏輯（B1）

**Files:**
- Modify: `app/routers/flowchart.py` — `export_pptx` 函數全部重寫
- Test: `tests/test_flowchart.py` — 新增 PPTX 測試

---

- [ ] **Step 2.1：寫失敗測試**

在 `tests/test_flowchart.py` 新增：

```python
from fastapi.testclient import TestClient
from app.main import app
from app.routers.flowchart import _topo_sort_layers
import io

# ── Topo sort tests ──────────────────────────────────────────────────────────

def test_topo_sort_linear():
    nodes = [
        {"id": "n1", "type": "start"},
        {"id": "n2", "type": "process"},
        {"id": "n3", "type": "end"},
    ]
    edges = [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "n3"},
    ]
    layers = _topo_sort_layers(nodes, edges)
    assert layers["n1"] == 0
    assert layers["n2"] == 1
    assert layers["n3"] == 2

def test_topo_sort_with_decision_branch():
    nodes = [
        {"id": "n1", "type": "start"},
        {"id": "n2", "type": "control"},
        {"id": "n3", "type": "process"},   # yes branch
        {"id": "n4", "type": "process"},   # no branch (back to n1)
        {"id": "n5", "type": "end"},
    ]
    edges = [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "n3", "label": "是"},
        {"from": "n2", "to": "n1", "label": "否"},
        {"from": "n3", "to": "n5"},
    ]
    layers = _topo_sort_layers(nodes, edges)
    assert layers["n1"] == 0
    assert layers["n2"] == 1
    assert layers["n3"] == 2
    assert layers["n5"] == 3

def test_topo_sort_document_node_follows_source():
    nodes = [
        {"id": "n1", "type": "start"},
        {"id": "n2", "type": "process"},
        {"id": "doc1", "type": "document"},
        {"id": "n3", "type": "end"},
    ]
    edges = [
        {"from": "n1", "to": "n2"},
        {"from": "n2", "to": "doc1", "label": "產出"},
        {"from": "n2", "to": "n3"},
    ]
    layers = _topo_sort_layers(nodes, edges)
    assert layers["doc1"] == layers["n2"]   # document same layer as source
```

- [ ] **Step 2.2：執行測試確認失敗**

```
pytest tests/test_flowchart.py::test_topo_sort_linear -v
```

預期：`ImportError: cannot import name '_topo_sort_layers'`

- [ ] **Step 2.3：在 flowchart.py 加入 `_topo_sort_layers`**

在 `_parse_llm_json` 函數**之前**加入：

```python
# ─── PPTX Layout Helper ──────────────────────────────────────────────────────

def _topo_sort_layers(nodes: list, edges: list) -> dict:
    """
    BFS topological sort — returns {node_id: layer_index}.
    document nodes share the layer of their source node.
    Back-edges (loops) are skipped to avoid infinite loops.
    """
    from collections import defaultdict, deque

    doc_node_ids = {n["id"] for n in nodes if n.get("type") == "document"}
    main_node_ids = {n["id"] for n in nodes if n.get("type") != "document"}

    in_degree: dict[str, int] = defaultdict(int)
    adjacency: dict[str, list] = defaultdict(list)

    visited_edges = set()
    for edge in edges:
        f, t = edge.get("from", ""), edge.get("to", "")
        if f in main_node_ids and t in main_node_ids:
            key = (f, t)
            if key not in visited_edges:
                visited_edges.add(key)
                adjacency[f].append(t)
                in_degree[t] += 1

    # Start nodes: main nodes with no incoming edges
    layers: dict[str, int] = {}
    queue: deque = deque()
    for nid in main_node_ids:
        if in_degree[nid] == 0:
            layers[nid] = 0
            queue.append(nid)

    processed = set()
    while queue:
        nid = queue.popleft()
        if nid in processed:
            continue
        processed.add(nid)
        current_layer = layers.get(nid, 0)
        for neighbor in adjacency[nid]:
            new_layer = current_layer + 1
            if layers.get(neighbor, -1) < new_layer:
                layers[neighbor] = new_layer
            in_degree[neighbor] -= 1
            if in_degree[neighbor] <= 0:
                queue.append(neighbor)

    # Document nodes: inherit layer from their first source main node
    for edge in edges:
        f, t = edge.get("from", ""), edge.get("to", "")
        if t in doc_node_ids and f in layers:
            layers[t] = layers[f]

    return layers
```

- [ ] **Step 2.4：執行 topo sort 測試**

```
pytest tests/test_flowchart.py::test_topo_sort_linear \
       tests/test_flowchart.py::test_topo_sort_with_decision_branch \
       tests/test_flowchart.py::test_topo_sort_document_node_follows_source \
       -v
```

預期：3 tests PASSED

- [ ] **Step 2.5：完整重寫 `export_pptx` 函數**

將 `app/routers/flowchart.py` 中 `@router.post("/export-pptx")` 到函數結束（`return StreamingResponse(...)`）整段替換為：

```python
@router.post("/export-pptx")
async def export_pptx(
    request: ExportPptxRequest,
    current_user: User = Depends(get_current_user),
):
    """將 AI 產出的 nodes/edges 轉換為可編輯的 PowerPoint 泳道流程圖"""
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR_TYPE
    from collections import defaultdict

    # ── Config ──────────────────────────────────────────────────────────────
    SLIDE_W_IN = 13.33
    SLIDE_H_IN = 7.5
    MARGIN_TOP_IN = 0.7
    MARGIN_LR_IN = 0.3
    HEADER_H_IN = 0.35
    NODE_W_IN = 1.9
    NODE_H_IN = 0.52

    # Deloitte palette
    SHAPE_COLORS = {
        "start":    RGBColor(0x86, 0xBC, 0x25),  # Deloitte Green
        "end":      RGBColor(0x00, 0x00, 0x00),  # Black
        "process":  RGBColor(0x2C, 0x2C, 0x2C),  # Charcoal
        "control":  RGBColor(0xF5, 0xA6, 0x23),  # Orange (decision)
        "document": RGBColor(0x66, 0x66, 0x66),  # Gray
    }
    TEXT_COLOR = RGBColor(0xFF, 0xFF, 0xFF)
    EDGE_COLOR = RGBColor(0x44, 0x44, 0x44)
    LANE_BG_COLORS = [
        RGBColor(0xF5, 0xF9, 0xF0),  # light green tint
        RGBColor(0xFA, 0xFA, 0xFA),  # near white
    ]

    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W_IN)
    prs.slide_height = Inches(SLIDE_H_IN)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    SLIDE_W = prs.slide_width
    SLIDE_H = prs.slide_height
    MARGIN_TOP = Inches(MARGIN_TOP_IN)
    MARGIN_LR = Inches(MARGIN_LR_IN)
    HEADER_H = Inches(HEADER_H_IN)
    NODE_W = Inches(NODE_W_IN)
    NODE_H = Inches(NODE_H_IN)

    nodes = request.nodes
    edges = request.edges

    # ── Group nodes by lane ─────────────────────────────────────────────────
    lane_groups: dict[str, list] = defaultdict(list)
    for node in nodes:
        lane = node.get("lane") or "未分類"
        lane_groups[lane].append(node)
    lanes = list(lane_groups.keys())
    n_lanes = max(len(lanes), 1)

    USABLE_W = SLIDE_W - MARGIN_LR * 2
    LANE_W = USABLE_W / n_lanes

    # ── Slide title ─────────────────────────────────────────────────────────
    title_box = slide.shapes.add_textbox(
        MARGIN_LR, Inches(0.08), USABLE_W, Inches(0.5)
    )
    tf = title_box.text_frame
    tf.text = request.title
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # ── Topo sort for Y positioning ─────────────────────────────────────────
    node_layers = _topo_sort_layers(nodes, edges)
    max_layer = max(node_layers.values(), default=0)

    CONTENT_TOP = MARGIN_TOP + HEADER_H + Inches(0.1)
    CONTENT_H = SLIDE_H - CONTENT_TOP - Inches(0.2)
    layer_step = CONTENT_H / max(max_layer + 1, 1)

    def layer_cy(layer: int) -> int:
        return int(CONTENT_TOP + layer * layer_step + layer_step / 2)

    # ── Lane backgrounds + headers ──────────────────────────────────────────
    for lane_idx, lane_name in enumerate(lanes):
        lane_left = int(MARGIN_LR + LANE_W * lane_idx)
        lane_top = int(MARGIN_TOP)
        lane_w = int(LANE_W)
        lane_h = int(SLIDE_H - MARGIN_TOP - Inches(0.15))

        # Background rectangle (insert at back of z-order)
        bg = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            lane_left, lane_top, lane_w, lane_h
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = LANE_BG_COLORS[lane_idx % 2]
        bg.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
        bg.line.width = Pt(0.5)
        # Move bg to behind all other shapes
        sp_tree = slide.shapes._spTree
        sp_tree.remove(bg._element)
        sp_tree.insert(2, bg._element)

        # Lane header label
        hdr = slide.shapes.add_textbox(
            lane_left + 4, lane_top + 2, lane_w - 8, int(HEADER_H)
        )
        htf = hdr.text_frame
        htf.text = lane_name
        hp = htf.paragraphs[0]
        hp.alignment = PP_ALIGN.CENTER
        hrun = hp.runs[0]
        hrun.font.size = Pt(9)
        hrun.font.bold = True
        hrun.font.color.rgb = RGBColor(0x2C, 0x2C, 0x2C)

    # ── Node shapes ─────────────────────────────────────────────────────────
    node_positions: dict[str, tuple[int, int]] = {}

    # Track per-lane per-layer node counts for horizontal offset
    lane_layer_count: dict[tuple, int] = defaultdict(int)

    for node in nodes:
        node_id = node["id"]
        node_type = node.get("type", "process")
        lane = node.get("lane") or "未分類"
        label = node.get("label", "")

        lane_idx = lanes.index(lane) if lane in lanes else 0
        lane_cx = int(MARGIN_LR + LANE_W * lane_idx + LANE_W / 2)
        layer = node_layers.get(node_id, 0)

        # Document nodes: offset to the right of their lane center
        if node_type == "document":
            slot = lane_layer_count[(lane_idx, layer, "doc")]
            lane_layer_count[(lane_idx, layer, "doc")] += 1
            cx = lane_cx + int(NODE_W * 0.6) * (slot + 1)
        else:
            cx = lane_cx

        cy = layer_cy(layer)
        node_positions[node_id] = (cx, cy)

        left = int(cx - NODE_W / 2)
        top = int(cy - NODE_H / 2)
        w = int(NODE_W)
        h = int(NODE_H)
        color = SHAPE_COLORS.get(node_type, SHAPE_COLORS["process"])

        # Select shape type
        if node_type in ("start", "end"):
            shape_type = MSO_AUTO_SHAPE_TYPE.OVAL
        elif node_type == "control":
            shape_type = MSO_AUTO_SHAPE_TYPE.DIAMOND
        elif node_type == "document":
            shape_type = MSO_AUTO_SHAPE_TYPE.PARALLELOGRAM
        else:
            shape_type = MSO_AUTO_SHAPE_TYPE.RECTANGLE

        shape = slide.shapes.add_shape(shape_type, left, top, w, h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.color.rgb = color

        tf = shape.text_frame
        tf.word_wrap = True
        tf.text = label
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.size = Pt(8)
        run.font.bold = True
        run.font.color.rgb = TEXT_COLOR

    # ── Connectors ──────────────────────────────────────────────────────────
    for edge in edges:
        f_id = edge.get("from", "")
        t_id = edge.get("to", "")
        if f_id not in node_positions or t_id not in node_positions:
            continue

        x1, y1 = node_positions[f_id]
        x2, y2 = node_positions[t_id]

        # Document edges: dashed straight connector
        from_node = next((n for n in nodes if n["id"] == f_id), {})
        to_node = next((n for n in nodes if n["id"] == t_id), {})
        is_doc_edge = to_node.get("type") == "document"

        conn_type = MSO_CONNECTOR_TYPE.STRAIGHT if is_doc_edge else MSO_CONNECTOR_TYPE.ELBOW
        connector = slide.shapes.add_connector(conn_type, x1, y1, x2, y2)
        connector.line.color.rgb = EDGE_COLOR
        connector.line.width = Pt(1.2)
        if is_doc_edge:
            connector.line.dash_style = 4  # dashed

        # Edge label
        edge_label = edge.get("label", "")
        if edge_label:
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            lbl = slide.shapes.add_textbox(
                mid_x - int(Inches(0.45)), mid_y - int(Inches(0.14)),
                int(Inches(0.9)), int(Inches(0.28))
            )
            ltf = lbl.text_frame
            ltf.text = edge_label
            lp = ltf.paragraphs[0]
            lp.alignment = PP_ALIGN.CENTER
            lr = lp.runs[0]
            lr.font.size = Pt(7)
            lr.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # ── Stream PPTX ─────────────────────────────────────────────────────────
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    filename = f"flowchart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

- [ ] **Step 2.6：執行所有 flowchart 測試**

```
pytest tests/test_flowchart.py -v
```

預期：所有測試 PASSED（topo sort 3 個 + skill 5 個 = 8 個）

- [ ] **Step 2.7：Commit**

```bash
git add app/routers/flowchart.py tests/test_flowchart.py
git commit -m "fix: rewrite PPTX export with topo sort, swimlane backgrounds, elbow connectors, Deloitte colors"
```

---

## Task 3：B2 圖片匯出備用模式

**Files:**
- Modify: `app/routers/flowchart.py` — 新增 `export-pptx-image` endpoint
- Modify: `frontend/src/pages/FlowchartGeneratorPage.vue` — 新增匯出 toggle + html2canvas 呼叫
- Test: `tests/test_flowchart.py` — 新增 B2 endpoint 測試

---

- [ ] **Step 3.1：寫失敗測試**

在 `tests/test_flowchart.py` 新增：

```python
import base64

def test_export_pptx_image_returns_pptx(client_with_auth):
    # 1x1 white pixel PNG, base64 encoded
    tiny_png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
        "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
    )
    resp = client_with_auth.post(
        "/api/v1/flowchart/export-pptx-image",
        json={"image_base64": tiny_png_b64, "title": "Test Flowchart"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    assert len(resp.content) > 1000  # non-empty PPTX
```

> `client_with_auth` fixture: 在 `tests/conftest.py` 中已有 db_session fixture，若無 client_with_auth 則先 skip 此測試，在完成 Step 3.2 後補上 fixture。

- [ ] **Step 3.2：新增 endpoint 到 flowchart.py**

在 `export_pptx` 函數**之後**加入：

```python
class ExportPptxImageRequest(BaseModel):
    image_base64: str
    title: str = "流程圖"


@router.post("/export-pptx-image")
async def export_pptx_image(
    request: ExportPptxImageRequest,
    current_user: User = Depends(get_current_user),
):
    """
    接收前端截圖（base64 PNG），嵌入 PPTX slide 作為高保真圖片匯出。
    圖形不可在 PPTX 中編輯，但外觀 100% 還原 Vue Flow 畫布效果。
    """
    import base64 as b64lib
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

    try:
        img_bytes = b64lib.b64decode(request.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="無效的 base64 圖片資料")

    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Title text box at top
    title_box = slide.shapes.add_textbox(
        Inches(0.3), Inches(0.05), Inches(12.73), Inches(0.45)
    )
    tf = title_box.text_frame
    tf.text = request.title
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Embed image filling remaining slide area
    img_stream = io.BytesIO(img_bytes)
    slide.shapes.add_picture(
        img_stream,
        Inches(0.1), Inches(0.55),
        Inches(13.13), Inches(6.9)
    )

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)

    filename = f"flowchart_hq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

- [ ] **Step 3.3：前端 — 安裝 html2canvas**

```bash
cd frontend && npm install html2canvas
```

- [ ] **Step 3.4：前端 — 在 FlowchartGeneratorPage.vue 加入匯出 toggle**

在現有的「匯出 PPTX」按鈕旁邊加入 toggle，找到匯出按鈕的模板區塊，替換為：

```vue
<!-- 匯出區塊 -->
<div class="flex align-items-center gap-2">
  <!-- 匯出模式 toggle -->
  <div class="export-mode-toggle flex align-items-center gap-2 text-sm text-color-secondary">
    <span>可編輯圖形</span>
    <InputSwitch v-model="useImageExport" />
    <span>高保真圖片</span>
  </div>

  <Button
    label="匯出 PPTX"
    icon="pi pi-download"
    :loading="exporting"
    @click="handleExport"
    :disabled="!nodes.length"
  />
</div>
```

在 `<script setup>` 中加入：

```typescript
import InputSwitch from 'primevue/inputswitch';
import html2canvas from 'html2canvas';

const useImageExport = ref(false);
const exporting = ref(false);

// 找到 Vue Flow 畫布的容器 ref（假設已有 ref="flowContainer"）
const flowContainer = ref<HTMLElement | null>(null);

const handleExport = async () => {
  exporting.value = true;
  try {
    if (useImageExport.value) {
      await exportAsImage();
    } else {
      await exportAsShapes();   // 現有的 B1 匯出邏輯
    }
  } finally {
    exporting.value = false;
  }
};

const exportAsImage = async () => {
  const el = flowContainer.value;
  if (!el) return;

  const canvas = await html2canvas(el, {
    scale: 2,          // 2x 解析度
    useCORS: true,
    backgroundColor: '#ffffff',
  });

  const imageBase64 = canvas.toDataURL('image/png').split(',')[1];
  const title = diagramTitle.value || '流程圖';  // 使用現有的 title ref

  const response = await fetch('/api/v1/flowchart/export-pptx-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.state.token}`,
    },
    body: JSON.stringify({ image_base64: imageBase64, title }),
  });

  if (!response.ok) throw new Error('匯出失敗');

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `flowchart_hq_${Date.now()}.pptx`;
  a.click();
  URL.revokeObjectURL(url);
};
```

> 注意：`exportAsShapes` 即現有的 PPTX 匯出函數，只需確認名稱一致即可。`diagramTitle` 和 `authStore` 假設為頁面中已存在的 ref/store。若名稱不同，對應調整。

- [ ] **Step 3.5：在 Vue Flow 容器加上 ref**

找到 FlowchartGeneratorPage.vue 中 Vue Flow 的父容器（`<VueFlow>` 或包住它的 `<div>`），加上 `ref="flowContainer"`：

```vue
<div ref="flowContainer" class="flowchart-canvas">
  <VueFlow ... />
</div>
```

- [ ] **Step 3.6：執行後端測試**

```
pytest tests/test_flowchart.py -v
```

預期：全部 PASSED（含 B2 endpoint 測試）

- [ ] **Step 3.7：手動測試 B2 匯出**

1. 啟動後端與前端 dev server
2. 上傳任意內控文件生成流程圖
3. 切換 toggle 到「高保真圖片」
4. 點擊「匯出 PPTX」
5. 確認下載的 PPTX 開啟後 slide 顯示流程圖圖片，非空白

- [ ] **Step 3.8：Commit**

```bash
git add app/routers/flowchart.py \
        frontend/src/pages/FlowchartGeneratorPage.vue \
        frontend/package.json \
        frontend/package-lock.json \
        tests/test_flowchart.py
git commit -m "feat: add high-fidelity image PPTX export (B2) with frontend toggle"
```

---

## 執行完整測試套件

```
pytest tests/test_flowchart.py -v
```

預期輸出（最終）：
```
tests/test_flowchart.py::test_extract_section_decompose PASSED
tests/test_flowchart.py::test_extract_section_render PASSED
tests/test_flowchart.py::test_extract_section_missing PASSED
tests/test_flowchart.py::test_load_flowchart_prompts_uses_fallback_when_no_skill PASSED
tests/test_flowchart.py::test_load_flowchart_prompts_reads_from_skill PASSED
tests/test_flowchart.py::test_topo_sort_linear PASSED
tests/test_flowchart.py::test_topo_sort_with_decision_branch PASSED
tests/test_flowchart.py::test_topo_sort_document_node_follows_source PASSED
tests/test_flowchart.py::test_export_pptx_image_returns_pptx PASSED
```

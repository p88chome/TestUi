"""
Flowchart Generator API Router
提供 AI 互動式流程圖產生服務（內控專用版）
- /analyze  : 上傳文件 → AI 產出初始流程圖
- /chat     : 多輪對話修改流程圖
- /export-pptx : 匯出可編輯 PPTX（真正圖形，非圖片）
"""

import io
import json
import re
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.core.config import settings
import httpx

router = APIRouter(prefix="/flowchart", tags=["flowchart"])


# ─── LLM Helper ─────────────────────────────────────────────────────────────

def _get_llm_url_and_headers():
    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    api_version = getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    if not api_key:
        raise HTTPException(status_code=500, detail="未設定 Azure OpenAI API Key")
    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": api_key}
    return url, headers


# ─── Document Text Extraction ─────────────────────────────────────────────

def _extract_text(filename: str, content: bytes) -> str:
    name_lower = filename.lower()
    if name_lower.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore")
    if name_lower.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"無法解析 DOCX 檔案: {e}")
    if name_lower.endswith(".pdf"):
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        parts.append(t)
            return "\n".join(parts)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"無法解析 PDF 檔案: {e}")
    return content.decode("utf-8", errors="ignore")


# ─── System Prompt（內控專用版）──────────────────────────────────────────────

SYSTEM_PROMPT = """你是一位資深的內部控制顧問，專精於協助企業繪製符合內控標準的流程圖。

你的任務是根據使用者提供的內控二階文件（作業程序說明書），分析業務流程並產生流程圖。

## 流程圖圖示規則（嚴格遵守，不得違反）

使用 Mermaid flowchart TDflowchart，並依以下規則對應圖示：

| 節點類型 | Mermaid 語法 | 用途 |
|---------|-------------|------|
| 開始/結束 | `A([開始])` 或 `Z([結束])` | 流程的起點與終點 |
| 作業流程步驟 | `B[送出申請]` | 一般作業節點 |
| 控制點/決策 | `C{主管審核?}` | 內控控制點、審核判斷 |
| 表單/文件 | `D[/申請表/]` | 需要填寫或產出的文件 |
| 連線 | `-->` | 一律使用實線，禁止虛線 |
| 泳道 | `subgraph 申請人` ... `end` | 區分不同權責單位 |

## 控制點識別原則
- 每個重要的審核、核准、驗證動作 → 使用菱形 `{...}`
- 菱形的 Yes/No 分支代表通過或退回
- 風險（Risk）不畫在流程圖內，僅在說明中提及

## 泳道（Swimlane）原則
- 從文件中識別出參與的角色/部門，用 subgraph 分組
- 每個 subgraph 代表一個權責單位

## 輸出格式（必須嚴格遵守，只輸出 JSON，不加任何其他文字）

```json
{
  "explanation": "流程說明（繁體中文）：識別到的主要流程步驟、控制點、泳道分組",
  "mermaid_code": "flowchart TD\\n  subgraph 申請人\\n    A([開始]) --> B[填寫申請表]\\n  end\\n  ...",
  "nodes": [
    {"id": "A", "type": "start", "label": "開始", "lane": "申請人"},
    {"id": "B", "type": "process", "label": "填寫申請表", "lane": "申請人"},
    {"id": "C", "type": "control", "label": "主管審核?", "lane": "主管"},
    {"id": "D", "type": "document", "label": "申請表", "lane": "申請人"},
    {"id": "Z", "type": "end", "label": "結束", "lane": ""}
  ],
  "edges": [
    {"from": "A", "to": "B", "label": ""},
    {"from": "B", "to": "C", "label": ""},
    {"from": "C", "to": "Z", "label": "通過"},
    {"from": "C", "to": "B", "label": "退回"}
  ]
}
```

節點 type 只能是：start / end / process / control / document
"""


# ─── LLM JSON Parser ─────────────────────────────────────────────────────────

def _parse_llm_json(raw: str) -> dict:
    raw = raw.strip()
    # Strip markdown fences
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON block from prose
        match = re.search(r'\{[\s\S]+\}', raw)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {
            "explanation": raw,
            "mermaid_code": "flowchart TD\n  A([開始]) --> Z([無法解析，請重試])",
            "nodes": [],
            "edges": []
        }


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(..., description="內控二階文件 (docx / pdf / txt)"),
    additional_context: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="檔案名稱無效")
    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="檔案大小不得超過 15MB")

    doc_text = _extract_text(file.filename, content)
    if not doc_text.strip():
        raise HTTPException(status_code=422, detail="無法從檔案中擷取文字內容")

    if len(doc_text) > 12000:
        doc_text = doc_text[:12000] + "\n\n[...文件內容已截斷...]"

    user_content = f"請根據以下內控二階文件，分析業務流程並產生符合內控標準的流程圖：\n\n---\n{doc_text}\n---"
    if additional_context:
        user_content += f"\n\n補充說明：{additional_context}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    url, headers = _get_llm_url_and_headers()
    payload = {"messages": messages, "temperature": 0.2, "max_tokens": 4000}

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"LLM API Error: {resp.text}")
        result = resp.json()

    raw_reply = result["choices"][0]["message"]["content"]
    parsed = _parse_llm_json(raw_reply)
    messages.append({"role": "assistant", "content": raw_reply})

    return {
        "status": "success",
        "explanation": parsed.get("explanation", ""),
        "mermaid_code": parsed.get("mermaid_code", ""),
        "nodes": parsed.get("nodes", []),
        "edges": parsed.get("edges", []),
        "messages": messages,
        "filename": file.filename,
        "generated_at": datetime.now().isoformat(),
    }


class ChatRequest(BaseModel):
    messages: List[dict]
    user_message: str


@router.post("/chat")
async def flowchart_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not request.user_message.strip():
        raise HTTPException(status_code=400, detail="訊息不可為空")

    messages = list(request.messages)
    messages.append({"role": "user", "content": request.user_message})

    url, headers = _get_llm_url_and_headers()
    payload = {"messages": messages, "temperature": 0.2, "max_tokens": 4000}

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"LLM API Error: {resp.text}")
        result = resp.json()

    raw_reply = result["choices"][0]["message"]["content"]
    parsed = _parse_llm_json(raw_reply)
    messages.append({"role": "assistant", "content": raw_reply})

    return {
        "status": "success",
        "explanation": parsed.get("explanation", ""),
        "mermaid_code": parsed.get("mermaid_code", ""),
        "nodes": parsed.get("nodes", []),
        "edges": parsed.get("edges", []),
        "messages": messages,
    }


# ─── PPTX Export ─────────────────────────────────────────────────────────────

class ExportPptxRequest(BaseModel):
    nodes: List[dict]
    edges: List[dict]
    title: str = "內控流程圖"


@router.post("/export-pptx")
async def export_pptx(
    request: ExportPptxRequest,
    current_user: User = Depends(get_current_user),
):
    """
    將 AI 產出的 nodes/edges 轉換為真正可編輯的 PowerPoint 流程圖（圖形非圖片）
    """
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from collections import defaultdict

    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # ── Color palette ──
    COLORS = {
        "start":    RGBColor(0x2E, 0x7D, 0x32),
        "end":      RGBColor(0xC6, 0x28, 0x28),
        "process":  RGBColor(0x15, 0x65, 0xC0),
        "control":  RGBColor(0xF5, 0x7F, 0x17),
        "document": RGBColor(0x6A, 0x1B, 0x9A),
    }
    TEXT_COLOR = RGBColor(0xFF, 0xFF, 0xFF)
    EDGE_COLOR = RGBColor(0x42, 0x42, 0x42)

    # ── Group nodes by swimlane ──
    lane_groups: dict[str, list] = defaultdict(list)
    for node in request.nodes:
        lane = node.get("lane", "") or "未分類"
        lane_groups[lane].append(node)

    lanes = list(lane_groups.keys())
    n_lanes = max(len(lanes), 1)

    SLIDE_W = prs.slide_width
    SLIDE_H = prs.slide_height
    MARGIN_TOP = Inches(0.8)
    MARGIN_LEFT = Inches(0.4)
    HEADER_H = Inches(0.4)
    LANE_W = (SLIDE_W - MARGIN_LEFT * 2) / n_lanes
    NODE_W = Inches(1.8)
    NODE_H = Inches(0.55)
    node_positions: dict[str, tuple] = {}

    # ── Slide title ──
    txBox = slide.shapes.add_textbox(MARGIN_LEFT, Inches(0.1), SLIDE_W - MARGIN_LEFT * 2, Inches(0.55))
    tf = txBox.text_frame
    tf.text = request.title
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].runs[0]
    run.font.size = Pt(18)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    # ── Lane headers + nodes ──

    def add_node_shape(slide, node, cx, cy):
        node_type = node.get("type", "process")
        label = node.get("label", "")
        color = COLORS.get(node_type, COLORS["process"])

        left = int(cx - NODE_W / 2)
        top = int(cy - NODE_H / 2)
        w = int(NODE_W)
        h = int(NODE_H)

        if node_type in ("start", "end"):
            # Rounded rectangle (stadium)
            shape = slide.shapes.add_shape(
                9,  # MSO_SHAPE_TYPE rounded rectangle ≈ 9 but we'll use oval for start/end
                left, top, w, h
            )
            # Use oval for true oval
            from pptx.util import Emu
            sp = shape._element
            sp.getparent().remove(sp)
            # Re-add as oval
            shape = slide.shapes.add_shape(9, left, top, w, h)  # 9 = oval in add_shape
        elif node_type == "control":
            # Diamond — rotated rectangle workaround via freeform
            shape = slide.shapes.add_shape(4, left, top, w, h)  # 4 = diamond in MSO_AUTO_SHAPE_TYPE
        elif node_type == "document":
            shape = slide.shapes.add_shape(3, left, top, w, h)  # 3 = parallelogram
        else:
            shape = slide.shapes.add_shape(1, left, top, w, h)  # 1 = rectangle

        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.color.rgb = color

        tf = shape.text_frame
        tf.word_wrap = True
        tf.text = label
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.color.rgb = TEXT_COLOR

        return shape

    for lane_idx, lane_name in enumerate(lanes):
        nodes_in_lane = lane_groups[lane_name]
        lane_left = MARGIN_LEFT + LANE_W * lane_idx
        lane_center_x = lane_left + LANE_W / 2

        # Lane header
        header_box = slide.shapes.add_textbox(
            int(lane_left) + 4, int(MARGIN_TOP),
            int(LANE_W) - 8, int(HEADER_H)
        )
        htf = header_box.text_frame
        htf.text = lane_name
        hp = htf.paragraphs[0]
        hp.alignment = PP_ALIGN.CENTER
        hrun = hp.runs[0]
        hrun.font.size = Pt(10)
        hrun.font.bold = True
        hrun.font.color.rgb = RGBColor(0x42, 0x42, 0x42)

        # Lane divider line
        line = slide.shapes.add_connector(
            1,  # STRAIGHT
            int(lane_left), int(MARGIN_TOP),
            int(lane_left), int(SLIDE_H - Inches(0.3))
        )
        line.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
        line.line.width = Pt(0.5)

        # Place nodes top → down
        node_content_top = MARGIN_TOP + HEADER_H + Inches(0.15)
        available_h = SLIDE_H - node_content_top - Inches(0.3)
        n_nodes = len(nodes_in_lane)
        step = available_h / max(n_nodes, 1)

        for node_idx, node in enumerate(nodes_in_lane):
            cy = node_content_top + step * node_idx + step / 2
            cx = lane_center_x
            add_node_shape(slide, node, int(cx), int(cy))
            node_positions[node["id"]] = (int(cx), int(cy))

    # ── Edges (connectors) ──
    for edge in request.edges:
        from_id = edge.get("from", "")
        to_id = edge.get("to", "")
        if from_id not in node_positions or to_id not in node_positions:
            continue
        x1, y1 = node_positions[from_id]
        x2, y2 = node_positions[to_id]

        connector = slide.shapes.add_connector(1, x1, y1, x2, y2)
        connector.line.color.rgb = EDGE_COLOR
        connector.line.width = Pt(1.5)

        label = edge.get("label", "")
        if label:
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            lbl = slide.shapes.add_textbox(mid_x - Inches(0.4), mid_y - Inches(0.15), Inches(0.8), Inches(0.3))
            ltf = lbl.text_frame
            ltf.text = label
            lp = ltf.paragraphs[0]
            lp.alignment = PP_ALIGN.CENTER
            lr = lp.runs[0]
            lr.font.size = Pt(8)
            lr.font.color.rgb = RGBColor(0x75, 0x75, 0x75)

    # ── Save and stream ──
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)

    filename = f"flowchart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

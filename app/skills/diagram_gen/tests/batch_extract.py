# -*- coding: utf-8 -*-
"""批次從 docx 抽取所有 CS-1xx / CA-1xx 子作業 → 跑 extract_graph → 存 JSON + Mermaid

用法:
  python -m app.skills.diagram_gen.tests.batch_extract archive/竑騰_內部控制制度_銷售及收款循環_V.2.0.docx
"""

import json
import re
import sys
import time
from pathlib import Path

from docx import Document

from app.skills.diagram_gen.extractor import extract_graph
from app.skills.diagram_gen.mermaid_renderer import to_mermaid

OUT_ROOT = Path(__file__).parent / "out"
OUT_DIR = OUT_ROOT / "batch"  # 預設;main() 會依 docx 名建子目錄

# CS-101 / CA-101 等 — 中英文混合
CODE_RE = re.compile(r"([A-Z]{2})-?(\d{3})")


def extract_sections(docx_path: Path) -> list[dict]:
    """從 docx 掃所有 3 欄子作業表格,每個表格 → 一筆 {code, title, text}"""
    doc = Document(docx_path)
    sections = []

    for t in doc.tables:
        if len(t.columns) != 3 or len(t.rows) < 3:
            continue

        # Row 0 通常是 title(3 cell 重複)
        title = t.rows[0].cells[0].text.strip()
        m = CODE_RE.search(title)
        if not m:
            continue
        code = f"{m.group(1)}-{m.group(2)}"

        # Row 1 是欄位表頭;Row 2 才是內容
        body_row = t.rows[2]
        procedure = body_row.cells[0].text.strip()
        # control_points = body_row.cells[1].text.strip()  # 不餵給 LLM
        forms = body_row.cells[2].text.strip()

        text = f"{title}\n\n作業程序:\n{procedure}\n\n參考欄位:\n{forms}"
        sections.append({"code": code, "title": title, "text": text})

    return sections


def run_one(sec: dict) -> dict:
    code = sec["code"].lower().replace("-", "")  # cs101
    stem = OUT_DIR / code

    try:
        t0 = time.time()
        g = extract_graph(sec["text"])
        dt = time.time() - t0
    except Exception as e:
        return {"code": sec["code"], "ok": False, "error": str(e)[:200]}

    (stem.with_suffix(".json")).write_text(
        json.dumps(g.model_dump(by_alias=True), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (stem.with_suffix(".mmd")).write_text(to_mermaid(g), encoding="utf-8")
    (stem.with_suffix(".txt")).write_text(sec["text"], encoding="utf-8")

    return {
        "code": sec["code"],
        "ok": True,
        "nodes": len(g.nodes),
        "edges": len(g.edges),
        "lanes": g.lanes,
        "starts": sum(1 for n in g.nodes if n.type == "start"),
        "decisions": sum(1 for n in g.nodes if n.type == "decision"),
        "elapsed_s": round(dt, 1),
    }


def main(docx_path: str, out_name: str | None = None) -> int:
    global OUT_DIR
    path = Path(docx_path)
    if not path.exists():
        print(f"[ERR] 找不到 {path}")
        return 2

    sub = out_name or path.stem
    OUT_DIR = OUT_ROOT / sub
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sections = extract_sections(path)
    print(f"[INFO] 共 {len(sections)} 個子作業")
    print(f"[INFO] 輸出目錄 {OUT_DIR}\n")

    results = []
    for i, sec in enumerate(sections, 1):
        print(f"[{i}/{len(sections)}] {sec['code']} ...", end=" ", flush=True)
        r = run_one(sec)
        results.append(r)
        if r["ok"]:
            print(
                f"OK  nodes={r['nodes']:2} edges={r['edges']:2} "
                f"lanes={len(r['lanes'])} starts={r['starts']} "
                f"decisions={r['decisions']}  {r['elapsed_s']}s"
            )
        else:
            print(f"FAIL {r['error']}")

    # Summary
    print("\n=== Summary ===")
    ok_count = sum(1 for r in results if r["ok"])
    print(f"  成功 {ok_count}/{len(results)}")
    for r in results:
        if r["ok"]:
            print(f"  {r['code']}: {r['nodes']} nodes / {r['edges']} edges / lanes={r['lanes']}")
        else:
            print(f"  {r['code']}: FAIL {r['error']}")

    # Save summary JSON
    (OUT_DIR / "_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSummary → {OUT_DIR}/_summary.json")
    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        args = ["archive/竑騰_內部控制制度_銷售及收款循環_V.2.0.docx"]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(main(args[0], name))

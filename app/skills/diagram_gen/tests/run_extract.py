# -*- coding: utf-8 -*-
"""CLI:跑 gold 抽取測試
用法:python -m app.skills.diagram_gen.tests.run_extract cs101
"""

import json
import os
import sys
from pathlib import Path

from app.skills.diagram_gen.extractor import extract_graph
from app.skills.diagram_gen.mermaid_renderer import to_mermaid
from app.skills.diagram_gen.compare import compare
from app.skills.diagram_gen.schema import Graph

GOLD_DIR = Path(__file__).parent / "gold"
OUT_DIR = Path(__file__).parent / "out"
OUT_DIR.mkdir(exist_ok=True)


def run(case: str) -> int:
    input_path = GOLD_DIR / f"{case}_input.txt"
    expected_path = GOLD_DIR / f"{case}_expected.json"

    if not input_path.exists():
        print(f"[ERR] 找不到 {input_path}")
        return 2

    text = input_path.read_text(encoding="utf-8")
    print(f"[INFO] 抽取 {case} ...")
    actual = extract_graph(text)

    # 存結果
    actual_json_path = OUT_DIR / f"{case}_actual.json"
    actual_json_path.write_text(
        json.dumps(actual.model_dump(by_alias=True), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] JSON → {actual_json_path}")

    mmd_path = OUT_DIR / f"{case}_actual.mmd"
    mmd_path.write_text(to_mermaid(actual), encoding="utf-8")
    print(f"[OK] Mermaid → {mmd_path}")

    # 比對 gold
    if expected_path.exists():
        gold = Graph.model_validate(json.loads(expected_path.read_text(encoding="utf-8")))
        report = compare(gold, actual)
        print("\n=== 比對結果 ===")
        for k, v in report.items():
            print(f"  {k}: {v}")
        # 也存 gold 的 mermaid 方便雙開比對
        gold_mmd = OUT_DIR / f"{case}_gold.mmd"
        gold_mmd.write_text(to_mermaid(gold), encoding="utf-8")
        print(f"\n[OK] Gold Mermaid → {gold_mmd}")
        return 0 if report["overall"] >= 0.8 else 1

    print("[WARN] 無 gold 檔,跳過比對")
    return 0


if __name__ == "__main__":
    case = sys.argv[1] if len(sys.argv) > 1 else "cs101"
    sys.exit(run(case))

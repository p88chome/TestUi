# -*- coding: utf-8 -*-
"""分析所有 batch 輸出,找結構性問題 — 不是對不對,是「合不合理」"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "out"

COMPANIES = {
    "竑騰(銷售)": "batch",
    "舊振南(銷售)": "jzn",
    "卡訊(固資)": "kx",
}


def analyze(graph: dict) -> dict:
    nodes = graph["nodes"]
    edges = graph["edges"]
    by_id = {n["id"]: n for n in nodes}

    types = {}
    for n in nodes:
        types[n["type"]] = types.get(n["type"], 0) + 1

    # 結構指標
    starts = types.get("start", 0)
    ends = types.get("end", 0)
    decisions = types.get("decision", 0)

    # 斷邊(指向不存在 id)
    orphan_edges = [e for e in edges if e["from"] not in by_id or e["to"] not in by_id]

    # 孤立節點(無任何 edge)
    connected = {e["from"] for e in edges} | {e["to"] for e in edges}
    isolated = [n["id"] for n in nodes if n["id"] not in connected]

    # self-loop
    self_loops = [e for e in edges if e["from"] == e["to"]]

    # Decision Y/N 同源(指向同節點)
    from collections import defaultdict
    dec_targets = defaultdict(list)
    for e in edges:
        n = by_id.get(e["from"])
        if n and n["type"] == "decision":
            dec_targets[e["from"]].append(e.get("to"))
    dec_yn_same = [d for d, tgts in dec_targets.items() if len(set(tgts)) < len(tgts)]

    # start 無前驅(正常);end 無後繼(正常)
    # process 無前驅(應有)
    in_deg = defaultdict(int)
    out_deg = defaultdict(int)
    for e in edges:
        in_deg[e["to"]] += 1
        out_deg[e["from"]] += 1
    no_in_non_start = [
        n["id"] for n in nodes
        if n["type"] not in ("start",) and in_deg[n["id"]] == 0
    ]
    no_out_non_end = [
        n["id"] for n in nodes
        if n["type"] not in ("end",) and out_deg[n["id"]] == 0
    ]

    edge_node_ratio = round(len(edges) / max(len(nodes), 1), 2)

    issues = []
    if starts > 5:
        issues.append(f"start 過多({starts})")
    if ends == 0:
        issues.append("無 end")
    if len(nodes) > 35:
        issues.append(f"節點爆炸({len(nodes)})")
    if edge_node_ratio > 1.8:
        issues.append(f"edge 密度異常({edge_node_ratio})")
    if orphan_edges:
        issues.append(f"斷邊 {len(orphan_edges)}")
    if isolated:
        issues.append(f"孤立節點 {len(isolated)}")
    if self_loops:
        issues.append(f"self-loop {len(self_loops)}")
    if dec_yn_same:
        issues.append(f"decision Y/N 同源 {len(dec_yn_same)}")
    if len(no_in_non_start) > 0:
        issues.append(f"無前驅非 start {len(no_in_non_start)}")
    if len(no_out_non_end) > 0:
        issues.append(f"無後繼非 end {len(no_out_non_end)}")

    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "starts": starts,
        "ends": ends,
        "decisions": decisions,
        "e_n_ratio": edge_node_ratio,
        "issues": issues,
    }


def main():
    overall = []
    for company, sub in COMPANIES.items():
        print(f"\n=== {company} ({sub}) ===")
        d = OUT / sub
        if not d.exists():
            print(f"  (skip - 目錄不存在)")
            continue
        files = sorted(f for f in d.glob("*.json") if f.name != "_summary.json")
        for f in files:
            g = json.loads(f.read_text(encoding="utf-8"))
            r = analyze(g)
            issue_str = ", ".join(r["issues"]) if r["issues"] else "✅"
            print(
                f"  {f.stem.upper():7} n={r['nodes']:3} e={r['edges']:3} "
                f"s={r['starts']} d={r['decisions']} r={r['e_n_ratio']}  {issue_str}"
            )
            overall.append({"company": company, "code": f.stem.upper(), **r})

    print("\n=== 整體統計 ===")
    total = len(overall)
    clean = sum(1 for r in overall if not r["issues"])
    print(f"  總數 {total},  結構乾淨 {clean} ({round(100*clean/total)}%)")

    print("\n  Top 3 issue 類型:")
    from collections import Counter
    counter = Counter()
    for r in overall:
        for i in r["issues"]:
            key = i.split("(")[0].strip()
            counter[key] += 1
    for k, v in counter.most_common(10):
        print(f"    {v:2} × {k}")

    (OUT / "_analysis.json").write_text(
        json.dumps(overall, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()

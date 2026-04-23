# -*- coding: utf-8 -*-
"""Graph 比對 (gold vs actual) — semantic matching by type + fuzzy label."""

import re
import unicodedata
from difflib import SequenceMatcher

from .schema import Graph


# 同義詞歸一化 — 內控文件常見同義詞
SYNONYMS = {
    "核准": "簽核",
    "核決": "簽核",
    "審核": "簽核",
    "批准": "簽核",
    "審批": "簽核",
    "確認": "簽核",
    # 業務同義
    "檢修": "維修",
    "採購": "進貨",
    "紀錄": "記錄",
    "製作": "建立",
    "更新": "建立",
    "擬定": "制定",
    "入帳": "帳務",
    "資訊": "處理",
    "送交": "提交",
}

FUZZY_THRESHOLD = 0.35


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _norm_label(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\s、。,.:;!?/()\[\]「」【】『』]", "", s)
    s = s.lower()
    for k, v in SYNONYMS.items():
        s = s.replace(k, v)
    return s


def _ratio(a: str, b: str) -> float:
    return max(SequenceMatcher(None, a, b).ratio(), _jaccard(a, b))


def _build_id_map(gold: Graph, actual: Graph) -> dict[str, str]:
    """Match actual → gold by (type, label). 先 exact, 再 fuzzy >= threshold。
    每個 gold 節點最多配到一個 actual。greedy by best ratio。"""
    gold_used: set[str] = set()
    gold_by_type: dict[str, list] = {}
    for n in gold.nodes:
        gold_by_type.setdefault(n.type, []).append(n)

    mapping: dict[str, str] = {}

    # Pass 1: exact normalized label match
    for a in actual.nodes:
        a_norm = _norm_label(a.label)
        candidates = [g for g in gold_by_type.get(a.type, []) if g.id not in gold_used]
        exact = next((g for g in candidates if _norm_label(g.label) == a_norm), None)
        if exact:
            mapping[a.id] = exact.id
            gold_used.add(exact.id)

    # Pass 2: fuzzy label match for remaining actuals
    for a in actual.nodes:
        if a.id in mapping:
            continue
        a_norm = _norm_label(a.label)
        candidates = [g for g in gold_by_type.get(a.type, []) if g.id not in gold_used]
        if not candidates:
            continue
        best = max(candidates, key=lambda g: _ratio(a_norm, _norm_label(g.label)))
        best_score = _ratio(a_norm, _norm_label(best.label))
        if best_score >= FUZZY_THRESHOLD:
            mapping[a.id] = best.id
            gold_used.add(best.id)

    return mapping


def _edge_set(g: Graph, remap: dict[str, str] | None = None) -> set[tuple[str, str, str]]:
    out = set()
    for e in g.edges:
        f = remap.get(e.from_, e.from_) if remap else e.from_
        t = remap.get(e.to, e.to) if remap else e.to
        out.add((f, t, _norm_label(e.label or "")))
    return out


def compare(gold: Graph, actual: Graph) -> dict:
    id_map = _build_id_map(gold, actual)

    matched_gold_ids = set(id_map.values())
    gold_coverage = len(matched_gold_ids) / max(len(gold.nodes), 1)

    matched_actual_ids = set(id_map.keys())
    precision = len(matched_actual_ids) / max(len(actual.nodes), 1)

    # Missing (in gold, no match in actual)
    missing = [(n.type, n.label) for n in gold.nodes if n.id not in matched_gold_ids]
    extra = [(n.type, n.label) for n in actual.nodes if n.id not in matched_actual_ids]

    g_edges = _edge_set(gold)
    a_edges = _edge_set(actual, remap=id_map)
    edge_common = g_edges & a_edges
    edge_missing = g_edges - a_edges
    edge_extra = a_edges - g_edges

    node_score = gold_coverage  # recall of gold
    edge_score = len(edge_common) / max(len(g_edges), 1)

    return {
        "gold_nodes": len(gold.nodes),
        "actual_nodes": len(actual.nodes),
        "matched_nodes": len(matched_gold_ids),
        "node_precision": round(precision, 3),
        "missing_nodes": [f"{t}:{l}" for t, l in missing],
        "extra_nodes": [f"{t}:{l}" for t, l in extra],
        "gold_edges": len(g_edges),
        "actual_edges": len(a_edges),
        "edge_match": len(edge_common),
        "missing_edges": sorted(edge_missing),
        "extra_edges": sorted(edge_extra),
        "node_score": round(node_score, 3),
        "edge_score": round(edge_score, 3),
        "overall": round((node_score + edge_score) / 2, 3),
    }

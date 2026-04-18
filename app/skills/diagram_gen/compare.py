# -*- coding: utf-8 -*-
"""Graph 比對(gold vs actual)"""

from .schema import Graph


def _edge_set(g: Graph) -> set[tuple[str, str, str]]:
    return {(e.from_, e.to, (e.label or "")) for e in g.edges}


def _node_map(g: Graph) -> dict[str, str]:
    # id → (type, label) 正規化:label 去空白
    return {n.id: f"{n.type}:{n.label.strip()}" for n in g.nodes}


def compare(gold: Graph, actual: Graph) -> dict:
    g_nodes = _node_map(gold)
    a_nodes = _node_map(actual)

    common_ids = set(g_nodes) & set(a_nodes)
    missing = set(g_nodes) - set(a_nodes)
    extra = set(a_nodes) - set(g_nodes)

    type_match = sum(
        1 for i in common_ids if g_nodes[i].split(":")[0] == a_nodes[i].split(":")[0]
    )

    g_edges = _edge_set(gold)
    a_edges = _edge_set(actual)
    edge_common = g_edges & a_edges

    node_score = len(common_ids) / max(len(g_nodes), 1)
    edge_score = len(edge_common) / max(len(g_edges), 1)

    return {
        "gold_nodes": len(g_nodes),
        "actual_nodes": len(a_nodes),
        "node_id_overlap": len(common_ids),
        "node_type_match": type_match,
        "missing_node_ids": sorted(missing),
        "extra_node_ids": sorted(extra),
        "gold_edges": len(g_edges),
        "actual_edges": len(a_edges),
        "edge_exact_match": len(edge_common),
        "missing_edges": sorted(g_edges - a_edges),
        "extra_edges": sorted(a_edges - g_edges),
        "node_score": round(node_score, 3),
        "edge_score": round(edge_score, 3),
        "overall": round((node_score + edge_score) / 2, 3),
    }

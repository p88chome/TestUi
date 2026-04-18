# -*- coding: utf-8 -*-
"""Graph ↔ Vue Flow payload 轉換
前端 node type 映射:
  skill           → frontend
  start           → start
  end             → end
  process         → process
  decision        → control      (菱形)
  doc (embedded)  → document     (展開為獨立節點)
"""

from .schema import Graph


TYPE_MAP = {
    "start": "start",
    "end": "end",
    "process": "process",
    "decision": "control",
}


def to_vueflow_payload(g: Graph) -> dict:
    """將 Graph → 前端 nodes/edges 陣列
    docs 展開為獨立 document 節點,用虛線 edge 連主節點"""
    nodes: list[dict] = []
    edges: list[dict] = []

    for n in g.nodes:
        nodes.append({
            "id": n.id,
            "type": TYPE_MAP.get(n.type, n.type),
            "label": n.label,
            "lane": n.lane or "預設部門",
        })
        for i, d in enumerate(n.docs):
            doc_id = f"{n.id}_doc{i}"
            nodes.append({
                "id": doc_id,
                "type": "document",
                "label": d,
                "lane": n.lane or "預設部門",
            })
            edges.append({
                "from": n.id,
                "to": doc_id,
                "label": "",
            })

    for e in g.edges:
        edges.append({
            "from": e.from_,
            "to": e.to,
            "label": e.label or "",
            "annotation": e.annotation or "",
        })

    return {
        "title": g.title,
        "lanes": g.lanes,
        "nodes": nodes,
        "edges": edges,
    }

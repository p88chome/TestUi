# -*- coding: utf-8 -*-
"""Graph → Vue Flow payload
前端 node type 映射:
  start           → start
  end             → end
  process         → process
  decision        → control      (菱形)

docs 不再展開為獨立節點,直接塞在 process node 的 `docs` 欄位,
由前端以貼紙形式渲染在節點旁邊,避免 Vue Flow 多生一堆邊造成視覺擁擠。
"""

from .schema import Graph


TYPE_MAP = {
    "start": "start",
    "end": "end",
    "process": "process",
    "decision": "control",
}


def to_vueflow_payload(g: Graph) -> dict:
    nodes: list[dict] = []
    for n in g.nodes:
        nodes.append({
            "id": n.id,
            "type": TYPE_MAP.get(n.type, n.type),
            "label": n.label,
            "lane": n.lane or "預設部門",
            "docs": list(n.docs or []),
        })

    edges: list[dict] = [
        {
            "from": e.from_,
            "to": e.to,
            "label": e.label or "",
            "annotation": e.annotation or "",
        }
        for e in g.edges
    ]

    return {
        "title": g.title,
        "lanes": g.lanes,
        "nodes": nodes,
        "edges": edges,
    }

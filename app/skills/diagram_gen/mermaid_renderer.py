# -*- coding: utf-8 -*-
"""Graph → Mermaid flowchart (debug 比對用)"""

from .schema import Graph, Node

MERMAID_RESERVED = {"end", "subgraph", "direction", "class", "style", "click", "linkStyle"}


def _safe(node_id: str) -> str:
    return f"_{node_id}" if node_id in MERMAID_RESERVED else node_id


def _shape(n: Node) -> str:
    label = n.label.replace('"', "'")
    nid = _safe(n.id)
    if n.type == "start" or n.type == "end":
        return f'{nid}(["{label}"])'
    if n.type == "decision":
        return f'{nid}{{"{label}"}}'
    return f'{nid}["{label}"]'


def to_mermaid(g: Graph) -> str:
    lines = ["flowchart TD"]
    lines.append(f'    %% {g.title}')

    # 節點(含 docs 用虛節點掛旁邊)
    for n in g.nodes:
        lines.append(f"    {_shape(n)}")
        for i, d in enumerate(n.docs):
            doc_id = f"{n.id}_doc{i}"
            lines.append(f'    {doc_id}[/"📄 {d}"/]')
            lines.append(f"    {_safe(n.id)} -.-> {doc_id}")

    # Edge
    for e in g.edges:
        arrow = f"-->"
        if e.label:
            arrow = f"-->|{e.label}|"
        lines.append(f"    {_safe(e.from_)} {arrow} {_safe(e.to)}")
        if e.annotation:
            lines.append(f"    %% annotation on {e.from_}->{e.to}: {e.annotation}")

    # Lane 分組(Mermaid subgraph)
    if g.lanes:
        lane_nodes: dict[str, list[str]] = {ln: [] for ln in g.lanes}
        for n in g.nodes:
            if n.lane and n.lane in lane_nodes:
                lane_nodes[n.lane].append(n.id)
        block = ["", "    %% Lanes"]
        for ln, ids in lane_nodes.items():
            if not ids:
                continue
            block.append(f'    subgraph {ln}["{ln}"]')
            block.extend(f"        {_safe(i)}" for i in ids)
            block.append("    end")
        lines.extend(block)

    return "\n".join(lines)

# -*- coding: utf-8 -*-
"""Flowchart graph schema — LLM 輸出需符合此結構"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


NodeType = Literal["start", "end", "process", "decision", "doc"]


class Node(BaseModel):
    id: str
    type: NodeType
    label: str
    lane: Optional[str] = None
    docs: list[str] = Field(default_factory=list)


class Edge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    label: Optional[str] = None
    annotation: Optional[str] = None

    class Config:
        populate_by_name = True


class Graph(BaseModel):
    title: str
    lanes: list[str] = Field(default_factory=list)
    nodes: list[Node]
    edges: list[Edge]

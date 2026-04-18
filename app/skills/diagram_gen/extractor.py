# -*- coding: utf-8 -*-
"""LLM 抽取流程圖 JSON"""

import json
import os
import httpx

from .schema import Graph

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "extract_v1.md")


def load_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def extract_graph(text: str, *, temperature: float = 0.1, max_tokens: int = 3000) -> Graph:
    """
    輸入子作業純文字 → 回 Graph 物件
    失敗 raise ValueError
    """
    from app.core.config import settings

    api_key = settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME or "gpt-4.1"
    api_version = settings.AZURE_OPENAI_API_VERSION

    if not api_key or not endpoint:
        raise ValueError("Azure OpenAI 未設定 (API_KEY / ENDPOINT)")

    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": api_key}
    payload = {
        "messages": [
            {"role": "system", "content": load_prompt()},
            {"role": "user", "content": text},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }

    with httpx.Client(timeout=120.0, verify=False) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise ValueError(f"LLM API Error {resp.status_code}: {resp.text}")
        data = resp.json()

    raw = data["choices"][0]["message"]["content"].strip()
    # 防守:若 LLM 仍包了 code fence
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip().rstrip("`").strip()

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 輸出非合法 JSON: {e}\n原始:\n{raw}") from e

    return Graph.model_validate(obj)

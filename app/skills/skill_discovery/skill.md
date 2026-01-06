name: list_available_skills
description: 查詢目前 Agent 擁有的所有技能清單與說明。當使用者詢問「你有什麼功能？」或「Show me skills」時使用。
category: system
input_schema:
  filter: "(選填) 關鍵字過濾，例如 'pdf' 或 'math'"
---
# Skill Discovery 指南

這個技能用於讓 Agent "自我反省" (Introspection)。
當使用者詢問 Agent 具備什麼能力時，呼叫此技能。

## 輸出
回傳一個包含所有可用技能及其描述的列表。

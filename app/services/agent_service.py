from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.services.skill_loader import execute_skill
from app.services.azure_integration import call_azure_openai
from app.core.config import settings
from app.models.stats import UsageLog
from app.core.cost_calculator import calculate_ai_cost
import json

class AgentService:
    def __init__(self, db: Session):
        self.db = db

    async def run(self, user_query: str, user_id: int) -> dict:
        """
        Agent 調度流程：
        1. 取得可用工具
        2. 規劃 (選擇工具)
        3. 執行工具
        4. 回應
        """
        # 1. 取得工具
        skills = self.db.query(Skill).filter(Skill.is_active == True).all()
        tools_desc = []
        for s in skills:
            # 格式： - name: description (Args: {schema})
            schema_str = json.dumps(s.input_schema) if s.input_schema else "{}"
            tools_desc.append(f"- {s.name}: {s.description} (Args: {schema_str})")
        
        tools_str = "\n".join(tools_desc)
        print(f"DEBUG: Tools Description:\n{tools_str}") # 新增除錯訊息
        
        # 2. 規劃提示詞
        system_prompt = f"""你是中央代理大腦 (Central Agent Brain)。
你的目標是選擇最合適的工具來回答使用者的問題。

可用工具：
{tools_str}

規則：
1. 僅回傳一個 JSON 物件。不要使用 markdown，也不要在 JSON 之外提供任何解釋。
2. JSON 格式：
   {{
      "thought": "我選擇這個工具的原因...",
      "tool": "tool_name_from_list_above",
      "args": {{ "key": "value" }} // 完全符合工具輸入 schema 的參數。請勿自行創造新的鍵值。
   }}
3. 如果 schema 包含 'text' 和 'file_url' 鍵，且使用者輸入包含相關內容，請在 'text' 欄位填入 "__INPUT_TEXT__" 作為佔位符，不需要複製完整內容。
4. 如果沒有匹配的工具，或使用者僅表示"有一份文件"但尚未提供內容，請回傳 "tool": "none" 並在 "args" 中提供 "explanation" 欄位，引導使用者提供文件。
5. 嚴禁在沒有實際文件內容的情況下呼叫 legal_contract_review 或 ocr_processor。
"""

        try:
            llm_response = await call_azure_openai(
                db=self.db,
                input_text=user_query,
                system_prompt=system_prompt,
                temperature=0.0
            )
        except Exception as e:
            return {
                "response": "抱歉，我在連接 AI 模型時發生錯誤。",
                "error": f"LLM Call Failed: {str(e)}"
            }
        
        # 解析決策
        try:
            # 記錄 Token 使用量與成本
            usage = llm_response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            model_name = llm_response.get("model", "gpt-4")
            
            estimated_cost = calculate_ai_cost(model_name, prompt_tokens, completion_tokens)
            
            # 寫入 UsageLog
            if user_id:
                try:
                    log_entry = UsageLog(
                        user_id=user_id,
                        app_name="Agent",
                        model_name=model_name,
                        tokens_input=prompt_tokens,
                        tokens_output=completion_tokens,
                        total_tokens=total_tokens,
                        estimated_cost=estimated_cost
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                except Exception as log_err:
                    print(f"Failed to log usage stats: {log_err}")
                    # 不阻擋流程

            # Azure OpenAI 結構: {"choices": [{"message": {"content": "..."}}]}
            choices = llm_response.get("choices", [])
            if choices and len(choices) > 0:
                content = choices[0].get("message", {}).get("content", "{}")
            else:
                 content = "{}"
            
            print(f"DEBUG: Raw LLM Response: {content}") # 新增除錯訊息
            # 清理 JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            decision = json.loads(content)
        except Exception as e:
            return {
                "response": "抱歉，我在思考時感到困惑。",
                "error": str(e),
                "raw_decision": content
            }
            
        tool_name = decision.get("tool")
        tool_args = decision.get("args", {})

        # 處理 __INPUT_TEXT__ 佔位符
        for key, value in tool_args.items():
            if value == "__INPUT_TEXT__":
                tool_args[key] = user_query
        
        if not tool_name or tool_name == "none":
            # 優先使用 LLM 提供的解釋，支援多種常見鍵名
            explanation = tool_args.get("explanation") or tool_args.get("message") or tool_args.get("msg")
            if not explanation:
                explanation = "我目前沒有專門的工具處理這個問題，但我可以嘗試提供一般性的協助。"
                
            return {
                "response": explanation,
                "agent_thought": decision.get("thought")
            }
            
        # 3. 執行
        try:
            result = execute_skill(tool_name, tool_args, self.db)
            
            # 4. 回應合成 (Synthesize Response)
            # 使用 LLM 將工具結果轉化為自然語言
            synthesis_prompt = f"""你是使用者的 AI 助理。
你剛剛使用了工具 '{tool_name}' 來解決使用者的問題。

使用者問題: {user_query}

工具執行結果:
{json.dumps(result, ensure_ascii=False, indent=2)}

請根據執行結果，用繁體中文回答使用者的問題。
- 確保回答自然、流暢。
- 如果結果包含程式碼，請使用 Markdown code block 呈現。
- 如果結果包含警告或風險，請清楚提示。
"""
            try:
                synthesis_response = await call_azure_openai(
                    db=self.db,
                    # Let's use input_text as empty and put everything in prompt, or slightly better:
                    system_prompt="You are a helpful AI assistant interpreting tool results.",
                    input_text=synthesis_prompt,
                    temperature=0.7 
                )
                
                final_reply = synthesis_response.get("choices", [])[0].get("message", {}).get("content", "")
                
                # 記錄第二階段 Token
                if user_id:
                     syn_usage = synthesis_response.get("usage", {})
                     # Calculate and log... (reuse logic or just simple log)
                     # For brevity, let's keep it simple or extract a helper method later.
                     # Duplicate logging logic for now to ensure tracking.
                     try:
                        syn_log = UsageLog(
                            user_id=user_id,
                            app_name="Agent (Synthesis)",
                            model_name=synthesis_response.get("model", "gpt-4"),
                            tokens_input=syn_usage.get("prompt_tokens", 0),
                            tokens_output=syn_usage.get("completion_tokens", 0),
                            total_tokens=syn_usage.get("total_tokens", 0),
                            estimated_cost=calculate_ai_cost(synthesis_response.get("model", "gpt-4"), syn_usage.get("prompt_tokens", 0), syn_usage.get("completion_tokens", 0))
                        )
                        self.db.add(syn_log)
                        self.db.commit()
                     except Exception:
                        pass # Ignore logging error
                
                display_response = final_reply

            except Exception as e:
                # Fallback if synthesis fails
                display_response = f"工具執行成功，但彙整回答時發生錯誤: {str(e)}\n\n原始結果:\n{json.dumps(result, ensure_ascii=False)}"

            return {
                "response": display_response,
                "tool_used": tool_name,
                "tool_result": result,
                "agent_thought": decision.get("thought")
            }
        except Exception as e:
            return {
                "response": f"我嘗試使用 {tool_name} 但失敗了。",
                "error": str(e)
            }

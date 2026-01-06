from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.models.chat import ChatSession, ChatMessage
from app.models.assistant import Assistant # NEW
from app.services.skill_loader import execute_skill
from app.services.gateway import LLMGateway # Use Gateway
from app.core.config import settings
from app.models.stats import UsageLog
from app.core.cost_calculator import calculate_ai_cost
import json
import uuid

class AgentService:
    def __init__(self, db: Session):
        self.db = db

    async def run(self, user_query: str, user_id: int, session_id: str = None, assistant_id: str = None) -> dict:
        """
        Agent 調度流程 (含記憶與角色)：
        1. 處理 Session (取得或新建，綁定 Assistant)
        2. 載入 Assistant 設定 (決定 Prompt 與 Skills)
        3. 載入歷史訊息
        4. 取得可用工具 (Filtered)
        5. 規劃 (選擇工具)
        6. 執行工具
        7. 回應
        8. 儲存對話
        """
        # 0. Trace & Session Logic
        trace_id = str(uuid.uuid4())
        assistant = None
        if assistant_id:
             assistant = self.db.query(Assistant).filter(Assistant.id == assistant_id).first()
        
        if not session_id:
            # Create new session
            new_session = ChatSession(
                user_id=user_id, 
                title=user_query[:50],
                assistant_id=assistant_id # Bind session to assistant
            )
            self.db.add(new_session)
            self.db.commit()
            self.db.refresh(new_session)
            session_id = new_session.id
        else:
            # Validate session
            session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                new_session = ChatSession(id=session_id, user_id=user_id, title=user_query[:50], assistant_id=assistant_id)
                self.db.add(new_session)
                self.db.commit()
            else:
                # If session exists, respect its bound assistant, unless explicitly switching (future feature)
                # For now, if request doesn't specify assistant, use session's. 
                # If request specifies, effectively we might be switching or validation. 
                # Let's pivot to: Session's assistant_id is the source of truth if established.
                if session.assistant_id:
                     assistant_id = session.assistant_id
                     assistant = self.db.query(Assistant).filter(Assistant.id == assistant_id).first()
        
        # Save User Message
        user_msg = ChatMessage(session_id=session_id, role="user", content=user_query, trace_id=trace_id)
        self.db.add(user_msg)
        self.db.commit()

        # Load Context (Clean objects for message construction)
        history_msgs = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        history_msgs.reverse()

        # Build History Messages List for API
        history_payload = []
        for msg in history_msgs:
            role = "assistant" if msg.role == "assistant" else "user"
            history_payload.append({"role": role, "content": msg.content})

            
        
        # 1. 取得工具 (Skill Routing)
        if assistant and assistant.skills:
            # If assistant has specific skills assigned, use ONLY those
            skills = assistant.skills
        else:
            # Fallback: All active skills (General Bot)
            skills = self.db.query(Skill).filter(Skill.is_active == True).all()
            
        tools_desc = []
        for s in skills:
            # 格式： - name: description (Args: {schema})
            schema_str = json.dumps(s.input_schema) if s.input_schema else "{}"
            tools_desc.append(f"- {s.name}: {s.description} (Args: {schema_str})")
        
        tools_str = "\n".join(tools_desc)
        
        # 2. 規劃提示詞 (Prompt Engineering)
        base_system_prompt = f"""你是中央代理大腦 (Central Agent Brain)。
你的職責是判斷使用者的需求，並決定由你自己回答，還是調用專門的工具。"""

        # Overlay Assistant Persona
        if assistant and assistant.instruction:
             base_system_prompt = assistant.instruction

        system_prompt = f"""{base_system_prompt}

你擁有的專業工具箱：
{tools_str}

決策原則 (Decision Principles)：
1. **必須使用工具的情況**：
   - 任務有明確的輸入與結構化輸出需求 (例如：讀取特定 PDF、分析 Excel、審閱合約風險、數學計算)。
   - 使用者明確要求執行特定動作 (例如：「列出所有技能」、「幫我生成報告」、「OCR 這張圖」)。
   - 需要精確的領域知識處理 (Finance, Legal, Scientific)。
   
2. **不應使用工具的情況 (直接回答)**：
   - 一般閒聊、問候 (例如：「你好」、「你是誰」)。
   - 詢問抽象概念、架構設計或建議 (例如：「Agent 要怎麼設計比較好？」、「為什麼你會這樣回答？」)。
   - 使用者尚未提供必要檔案或內容 (例如：「幫我審閱合約」，但沒給合約內容 -> 請直接引導使用者上傳，回傳 "tool": "none")。

3. **記憶回溯 (Memory Recall)**：
   - 若使用者詢問「我是誰」、「我們剛才在聊什麼」，請直接根據對話歷史回答，回傳 "tool": "none" 並在 args 中填寫回答。

思考流程：
- 先在心中分析使用者的意圖 (Intent Analysis)。
- 檢查是否有匹配的工具名稱與描述。
- 判斷是否具備足夠的參數來呼叫工具。

輸出規則：
1. 僅回傳一個 JSON 物件。不要使用 markdown。
2. JSON 格式：
   {{
      "thought": "簡短描述你的判斷過程：使用者想做什麼？為什麼選擇(或不選擇)這個工具？",
      "tool": "tool_name" 或 "none",
      "args": {{ ... }} // 若 tool 為 "none"，請在 args 中放入 "explanation" 欄位來回答使用者。
   }}
3. 如果工具需要 'text' 或 'file_url' 但使用者輸入中已包含文字，請用 "__INPUT_TEXT__" 作為佔位符。
4. 嚴禁在沒有實際文件內容的情況下呼叫 legal_contract_review 或 ocr_processor。
"""

        # Construct Decision Messages
        decision_messages = [{"role": "system", "content": system_prompt}]
        decision_messages.extend(history_payload)
        decision_messages.append({"role": "user", "content": user_query})

        try:
            gateway = LLMGateway(self.db)
            llm_response = await gateway.chat(
                messages=decision_messages,
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
                        app_name=f"Agent-{assistant.name}" if assistant else "Agent-General",
                        model_name=model_name,
                        tokens_input=prompt_tokens,
                        tokens_output=completion_tokens,
                        total_tokens=total_tokens,
                        estimated_cost=estimated_cost,
                        trace_id=trace_id # Add Trace ID
                    )
                    self.db.add(log_entry)
                    self.db.commit()
                except Exception as log_err:
                    print(f"Failed to log usage stats: {log_err}")
                
            choices = llm_response.get("choices", [])
            if choices and len(choices) > 0:
                content = choices[0].get("message", {}).get("content", "{}")
            else:
                 content = "{}"
            
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
        
        final_reply = ""
        result = {}
        
        if not tool_name or tool_name == "none":
            explanation = tool_args.get("explanation") or tool_args.get("message") or tool_args.get("msg")
            if not explanation:
                explanation = "我目前沒有專門的工具處理這個問題，但我可以嘗試提供一般性的協助。"
            
            final_reply = explanation
        else:
            # 3. 執行
            try:
                result = execute_skill(tool_name, tool_args, self.db, trace_id=trace_id)
                
                # 4. 回應合成
                synthesis_prompt = f"""你是使用者的 AI 助理。
你剛剛使用了工具 '{tool_name}' 來解決使用者的問題。
請根據執行結果，用繁體中文回答使用者的問題。
- 確保回答自然、流暢。
- 如果結果包含程式碼，請使用 Markdown code block 呈現。
- 如果結果包含警告或風險，請清楚提示。
"""
                # Construct Synthesis Messages with History
                synthesis_messages = [{"role": "system", "content": synthesis_prompt}]
                synthesis_messages.extend(history_payload)
                synthesis_messages.append({"role": "user", "content": user_query})
                synthesis_messages.append({"role": "system", "content": f"工具 '{tool_name}' 執行結果:\n{json.dumps(result, ensure_ascii=False, indent=2)}"})

                try:
                    synthesis_response = await gateway.chat(
                        messages=synthesis_messages,
                        temperature=0.7 
                    )
                    
                    final_reply = synthesis_response.get("choices", [])[0].get("message", {}).get("content", "")
                    
                    # Log synthesis usage...
    
                except Exception as e:
                    final_reply = f"工具執行成功，但彙整回答時發生錯誤: {str(e)}\n\n原始結果:\n{json.dumps(result, ensure_ascii=False)}"

            except Exception as e:
                 final_reply = f"我嘗試使用 {tool_name} 但失敗了。錯誤資訊: {str(e)}"
                 result = {"error": str(e)}

        # Save Assistant Response
        asst_msg = ChatMessage(session_id=session_id, role="assistant", content=final_reply, tool_calls=decision if tool_name != "none" else None, trace_id=trace_id)
        self.db.add(asst_msg)
        self.db.commit()

        return {
            "response": final_reply,
            "tool_used": tool_name if tool_name != "none" else None,
            "tool_result": result,
            "agent_thought": decision.get("thought"),
            "session_id": session_id,
            "trace_id": trace_id, # Return to UI
            "assistant_id": assistant.id if assistant else None
        }

# -*- coding: utf-8 -*-
"""
PPT 生成 API Router - AI 智能版
支援：
1. 手動輸入內容生成
2. AI 自動搜尋網路 + 生成內容
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import json
import httpx

router = APIRouter(prefix="/ppt", tags=["PPT Generator"])


class SlideContent(BaseModel):
    title: str
    content: Optional[List[str]] = []
    layout: str = "bullet"  # title, bullet, content, two_column, section


class PPTGenerateRequest(BaseModel):
    title: str
    subtitle: Optional[str] = ""
    slides: List[SlideContent]
    theme: str = "professional"  # professional, creative, minimal, deloitte


class PPTGenerateResponse(BaseModel):
    status: str
    message: str
    file_path: Optional[str] = None
    slide_count: Optional[int] = None
    download_url: Optional[str] = None


@router.post("/generate", response_model=PPTGenerateResponse)
async def generate_ppt(request: PPTGenerateRequest):
    """
    根據大綱生成 PowerPoint 簡報
    """
    try:
        from app.skills.pptx_generator.run import execute
        
        # 準備輸入資料
        slides_data = [
            {
                "title": slide.title,
                "content": slide.content,
                "layout": slide.layout
            }
            for slide in request.slides
        ]
        
        # 生成唯一的輸出檔名
        import uuid
        filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
        output_dir = os.path.join(tempfile.gettempdir(), "ppt_output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        input_data = {
            "operation": "create_from_outline",
            "title": request.title,
            "subtitle": request.subtitle,
            "slides": slides_data,
            "theme": request.theme,
            "output_path": output_path
        }
        
        result = execute(input_data)
        
        if result.get("status") == "success":
            return PPTGenerateResponse(
                status="success",
                message="簡報生成成功",
                file_path=result.get("file_path"),
                slide_count=result.get("slide_count"),
                download_url=f"/api/v1/ppt/download/{filename}"
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "生成失敗"))
            
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"python-pptx 未安裝: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_ppt(filename: str):
    """
    下載生成的 PPT 檔案
    """
    output_dir = os.path.join(tempfile.gettempdir(), "ppt_output")
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="檔案不存在或已過期")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@router.get("/themes")
async def get_themes():
    """
    取得可用的主題列表
    """
    return {
        "themes": [
            {"id": "professional", "name": "專業商務", "description": "深藍配色，適合正式場合"},
            {"id": "creative", "name": "創意活潑", "description": "紫橘配色，適合創意提案"},
            {"id": "minimal", "name": "極簡風格", "description": "黑白灰配色，簡潔大方"},
            {"id": "deloitte", "name": "Deloitte", "description": "Deloitte Green 企業風格"}
        ]
    }


@router.get("/layouts")
async def get_layouts():
    """
    取得可用的版型列表
    """
    return {
        "layouts": [
            {"id": "title", "name": "標題頁", "description": "大標題 + 副標題"},
            {"id": "bullet", "name": "項目符號", "description": "標題 + 項目符號列表"},
            {"id": "content", "name": "純文字", "description": "標題 + 段落文字"},
            {"id": "two_column", "name": "雙欄", "description": "左右對比"},
            {"id": "section", "name": "章節分隔", "description": "章節標題頁"}
        ]
    }


# ============================================================
# AI 智能生成：自動搜尋網路 + LLM 生成內容
# ============================================================

class AIGenerateRequest(BaseModel):
    topic: str  # 用戶只需輸入主題
    slide_count: int = 6  # 希望的投影片數量
    theme: str = "deloitte"
    language: str = "zh-TW"  # 輸出語言


class AIGenerateResponse(BaseModel):
    status: str
    message: str
    file_path: Optional[str] = None
    slide_count: Optional[int] = None
    download_url: Optional[str] = None
    outline: Optional[List[dict]] = None  # 生成的大綱給用戶看


async def search_web(query: str) -> str:
    """使用網路搜尋獲取資料"""
    from app.core.config import settings
    
    # 使用 Tavily API 搜尋（如果有配置）
    tavily_key = getattr(settings, 'TAVILY_API_KEY', None) or os.getenv('TAVILY_API_KEY')
    
    if tavily_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": tavily_key,
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": 5
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    content_parts = []
                    for r in results[:5]:
                        content_parts.append(f"標題: {r.get('title', '')}\n內容: {r.get('content', '')}")
                    return "\n\n---\n\n".join(content_parts)
        except Exception as e:
            print(f"Tavily search error: {e}")
    
    # 如果沒有 Tavily，返回提示
    return f"（無法搜尋網路，將基於主題「{query}」生成通用內容）"


async def generate_outline_with_llm(topic: str, search_results: str, slide_count: int, language: str) -> List[dict]:
    """使用 Azure OpenAI 生成簡報大綱"""
    from app.core.config import settings
    
    # Azure OpenAI 配置
    endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip('/')
    api_key = settings.AZURE_OPENAI_API_KEY
    deployment = getattr(settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
    api_version = "2024-02-15-preview"
    
    system_prompt = f"""你是一位專業的簡報設計師。根據用戶提供的主題和參考資料，生成一份完整的簡報大綱。

要求：
1. 生成 {slide_count} 張投影片的內容
2. 每張投影片包含：標題 (title)、內容要點 (content: 字串陣列，每個要點 15-25 字)、版型 (layout)
3. 版型選項：bullet (項目符號)、content (純文字)、section (章節分隔)
4. 第一張應該是簡介/目的，最後一張是總結/行動方案
5. 內容要專業、有深度、基於提供的參考資料
6. 使用 {language} 語言

請直接返回 JSON 格式的陣列，例如：
[
  {{"title": "簡介", "content": ["要點1", "要點2", "要點3"], "layout": "bullet"}},
  {{"title": "主題一", "content": ["分析內容1", "分析內容2"], "layout": "bullet"}}
]"""

    user_prompt = f"""主題：{topic}

參考資料：
{search_results}

請生成 {slide_count} 張投影片的大綱（JSON 格式）。"""

    try:
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # 解析 JSON（處理 markdown code block）
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                slides = json.loads(content.strip())
                return slides
            else:
                print(f"Azure OpenAI API error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"LLM generation error: {e}")
        import traceback
        traceback.print_exc()
    
    # 如果 LLM 失敗，返回基本大綱
    return [
        {"title": topic, "content": ["自動生成失敗，請手動輸入內容"], "layout": "bullet"}
    ]



@router.post("/ai-generate", response_model=AIGenerateResponse)
async def ai_generate_ppt(request: AIGenerateRequest):
    """
    AI 智能生成簡報：
    1. 根據主題自動搜尋網路資料
    2. 使用 LLM 生成簡報大綱
    3. 自動生成 PowerPoint 檔案
    """
    try:
        # Step 1: 搜尋網路資料
        search_results = await search_web(request.topic)
        
        # Step 2: 使用 LLM 生成大綱
        slides = await generate_outline_with_llm(
            request.topic, 
            search_results, 
            request.slide_count,
            request.language
        )
        
        # Step 3: 生成簡報
        from app.skills.pptx_generator.run import execute
        import uuid
        
        filename = f"ai_ppt_{uuid.uuid4().hex[:8]}.pptx"
        output_dir = os.path.join(tempfile.gettempdir(), "ppt_output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        input_data = {
            "operation": "create_from_outline",
            "title": request.topic,
            "subtitle": "AI 智能生成",
            "slides": slides,
            "theme": request.theme,
            "output_path": output_path
        }
        
        result = execute(input_data)
        
        if result.get("status") == "success":
            return AIGenerateResponse(
                status="success",
                message="AI 簡報生成成功",
                file_path=result.get("file_path"),
                slide_count=result.get("slide_count"),
                download_url=f"/api/v1/ppt/download/{filename}",
                outline=slides
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "生成失敗"))
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

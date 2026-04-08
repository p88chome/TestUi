# 企業級全方位 AI 代理平台 (Enterprise Agentic AI Platform)

歡迎使用 **All平台** —— 這是一個次世代的 AI 應用框架，旨在超越傳統的聊天機器人 (Chatbot)，構建真正具備 **自主思考** 與 **執行能力** 的智慧代理人 (Intelligent Agent)。

本專案整合了多重 AI 模型（Azure OpenAI、Google Gemini）引擎與高度擴充性的模組化工具系統，讓 AI 不僅能「說」，也能即時「規劃」並「執行」任務。

---

## 🚀 專案願景 (Vision)
打造一個企業級的 AI 大腦，它能像專業顧問一樣：
1. **聽得懂**：理解複雜的上下文與多輪對話 (Context Awareness)。
2. **分得清**：根據任務需求，切換不同的專業角色與背後適合的模型 (Role-Based Personnel & Model Routing)。
3. **做得到**：主動呼叫工具 API（如爬蟲、爬梳文件、製作圖表、產生簡報）來完成任務 (Tool Execution)。

---

## ✨ 核心架構：企業應用與元件 (Enterprise Apps & Components)

本平台採用模組化設計，將核心功能封裝為標準化的「元件」，並組合成滿足特定業務需求的「企業應用」：

### 🏢 精選企業應用 (Enterprise Apps)
位於 `/frontend/src/pages/` 與 `/app/routers/`，針對各種企業營運場景的完整解決方案：

| 應用名稱 | 功能描述 | 技術亮點 |
| :--- | :--- | :--- |
| **Flowchart Generator** | 內控流程圖大師 | **AI 結構化生成**：將二階文件或作業說明轉換成具備泳道 (Swimlane)、決策點等規範的 `nodes/edges`。<br>**原生匯出**：非靜態圖片，而是真正匯出成可被 PowerPoint 編輯的立體流程圖。 |
| **Meeting AI** | 智慧會議助手 | 支援背景非同步語音轉文字 (Whisper Task Manager)、多輪對話萃取會議紀要。 |
| **Policy Analysis** | 政策差異分析 | 上傳新舊法規或政策，AI 自動分析增刪修條文，並匯出 Word 差異對比報告。 |
| **PPT Generator** | 智能簡報生成 | 結合 **Tavily API** 即時搜尋網路，產生大綱後自動排版輸出專業模板簡報 (PPTX)。 |
| **Contract Assistant** | 合約審閱助手 | 針對法律合約進行風險條款掃描與法務解釋。 |
| **Expense Helper** | 報帳理單助手 | 結合 OCR 與 AI 自動辨識單據、發票，萃取供應商、金額、稅項等結構化數據。 |

### 🧱 核心技能與架構 (Core Components & Architecture)
提供底層能力支援企業應用，並由統一的 `LLMGateway` 和 `TaskManager` 進行調度。

| 元件名稱 | 對應模組/機制 | 功能描述 |
| :--- | :--- | :--- |
| **多重模型管理** | `/models` & `llm_service.py` | 無縫熱切換 **Azure OpenAI** 與 **Google Gemini** 模型，支援進階 Reasoning (思考模式)，自動計算 Token 消耗用量。 |
| **AIOCR** | `ocr_processor` | 呼叫 Azure Computer Vision 或 Local OCR，把圖像轉換成文字陣列供 AI 使用。 |
| **Background Tasks**| `task_manager.py` | 透過 Async Event Loop 託管需要較長時間處理的任務 (例如 Whisper 語音轉文字)，避免前端逾時。 |
| **AI Web Search**| `web_search` | 整合 **Tavily API** 進行即時網路資料、財報檢索。 |
| **Capability Map** | 前端儀表板 | 即時觀察與管理 Skills, Workflows 的健康狀態與 API 用量分析。 |

---

## ⚙️ 系統配置與啟動 (Configuration & Setup)

本平台支援彈性的環境配置，請複製 `.env.example` 並建立 `.env` 檔案：

### 1. 核心 AI 引擎 (支援多核心，擇一即可啟動)
```ini
# --- Azure OpenAI ---
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# --- Google Gemini ---
GEMINI_API_KEY=your-gemini-key
```
*(在平台中可隨時透過左側邊欄底部的 **Active Model** 選單進行一鍵切換)*

### 2. 核心元件
```ini
# 資料庫 (PostgreSQL 或 本地 SQLite 開發)
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_platform

# 網路搜尋 (用於 PPT 智能生成)
TAVILY_API_KEY=tvly-xxxxxxxxxxxx

# 產生安全金鑰 (生產環境用): python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=your-super-secret-key
```

### 3. 如何啟動

**後端 (FastAPI):**
```bash
# 1. 進入後端資料夾並啟動虛擬環境 (如果有的話)
# 2. 安裝依賴
pip install -r requirements.txt
# 3. 執行後端伺服器 (開發模式)
uvicorn app.main:app --reload
```

**前端 (Vue3 + Vite):**
```bash
# 1. 進入 frontend 資料夾
cd frontend
# 2. 安裝依賴
npm install
# 3. 啟動前端開發伺服器
npm run dev
```

---

## 🏗️ 系統技術棧 (Tech Stack)

- **Frontend (前端)**：
  - **Framework**: Vue.js 3 + TypeScript + Vite
  - **State Management**: Pinia
  - **UI Library**: PrimeVue (企業級深色主題、高度客製化 App-Launcher 與 Sidebar)
  - **Data Viz**: Chart.js, Mermaid, Vue Flow (用於呈現流程圖與架構)

- **Backend (後端)**：
  - **Framework**: FastAPI (Asynchronous)
  - **AI Engines**: Azure OpenAI Service, Google Gemini (via `google-genai` SDK)
  - **ORM**: SQLAlchemy + Alembic (資料庫版控)
  - **Document Generation**: `python-pptx`, `python-docx`

- **部署基礎架構**:
  - Azure App Service, Azure Static Web Apps (帶 GitHub Actions CI/CD)
  - Docker Containerization

---

## 📊 數據與分析 (Analytics & Observability)

本平台內嵌了強大的後台管理功能，讓開發者與管理者能隨時掌控 AI 表現：
- **Dashboard**: 查看 Token 每日使用量、各應用程式的消耗佔比。
- **Models Management**: CRUD 模型管理，支援標記推理模型 (o1/Gemini Pro) 以區分 `max_tokens` 與 `max_completion_tokens` 機制。
- **Users & Feedback**: 使用者回饋與滿意度追蹤系統。

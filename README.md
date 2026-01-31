# 企業級全方位 AI 代理平台 (Enterprise Agentic AI Platform)

歡迎使用 **All平台** —— 這是一個次世代的 AI 應用框架，旨在超越傳統的聊天機器人 (Chatbot)，構建真正具備 **自主思考** 與 **執行能力** 的智慧代理人 (Intelligent Agent)。

本專案整合了 Azure OpenAI 的強大語言能力與模組化的工具系統，讓 AI 不僅能「說」，更能「做」。

## 🚀 專案願景 (Vision)
打造一個企業級的 AI 大腦，它能像專業員工一樣：
1.  **聽得懂**：理解複雜的上下文與多輪對話 (Context Awareness)。
2.  **分得清**：根據任務需求，切換不同的專業角色 (Role-Based Personnel)。
3.  **做得到**：主動呼叫工具 API 來完成任務 (Tool Execution)。

---

## ✨ 核心架構：企業應用與元件 (Enterprise Apps & Components)

本平台採用模組化設計，將核心功能封裝為標準化的「元件」，並組合成滿足特定業務需求的「企業應用」：

### 🏢 企業應用 (Enterprise Apps)
位於 `/frontend/src/pages/` 與 `/app/routers/`，針對特定業務場景的完整解決方案：

| 應用名稱 | 功能描述 | 技術亮點 |
| :--- | :--- | :--- |
| **Meeting AI** | 智慧會議助手 | 會議錄音轉逐字稿、自動生成會議摘要、待辦事項提取。 |
| **Policy Analysis** | 政策差異分析 | 上傳兩份文件（如新舊法規），自動分析增刪修條文與潛在影響。 |
| **PPT Generator** | 智能簡報生成 | **AI 智能生成**：輸入主題，AI 自動搜尋網路並生成完整簡報。<br>**專業模板**：內建 Deloitte 等專業設計模板。 |
| **Contract Assistant** | 合約審閱助手 | 針對法律合約進行風險掃描與條款解釋。 |

### 🧱 核心元件 (Core Components)
提供底層能力支援企業應用：

| 元件名稱 | 對應技能 (Skill) | 功能描述 |
| :--- | :--- | :--- |
| **AIOCR** | `ocr_processor` | 針對票據、掃描文件做文字擷取與欄位結構化。 |
| **AIREAD** | `legal_contract_review` | 長文閱讀、摘要、關鍵條款與風險抽取。 |
| **AI PPT** | `pptx_generator` | 使用 `python-pptx` 與 `Azure OpenAI` 自動生成 PowerPoint 檔案。 |
| **AI Web Search**| `web_search` | 整合 **Tavily API** 進行即時網路資料檢索。 |
| **AI Excel** | `excel_handler` | 讀取/寫入 Excel，自動整理表格、運算欄位。 |
| **AI Intent** | `AgentService` | 判斷使用者意圖並分派任務。 |

---

## ⚙️ 系統配置 (Configuration)

本平台支援彈性的環境配置，請參考 `.env.example` 建立 `.env` 檔案：

### 1. AI 引擎 (Azure OpenAI)
```ini
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### 2. 資料庫 (PostgreSQL)
```ini
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_platform
```

### 3. 網路搜尋 (Tavily) - 用於 PPT 智能生成
```ini
TAVILY_API_KEY=tvly-xxxxxxxxxxxx
```

---

## 🏗️ 系統架構 (System Architecture)

- **Frontend (前端)**：
  - **Framework**: Vue.js 3 + TypeScript
  - **UI Library**: PrimeVue (Deloitte 風格主題)
  - **Routing**: 清晰的應用導航 (`/apps/*`)

- **Backend (後端)**：
  - **Framework**: FastAPI
  - **AI Engine**: Azure OpenAI Service
  - **Template System**: `python-pptx` 專業模板引擎

- **Infrastructure**:
  - Docker Containerization

---

## 💡 應用場景示範 (Use Cases)

### 場景 A：智能簡報製作
> **使用者**：「幫我做一份關於『2024 AI 發展趨勢』的簡報。」
>
> **AI (PPT Generator)**：
> 1. 調用 **Tavily API** 搜尋最新 AI 趨勢。
> 2. 使用 **Azure OpenAI** 規劃 6 頁簡報大綱。
> 3. 調用 **PPTX Generator** 套用 `Deloitte` 專業模板。
> 4. **結果**：生成一份包含標題、圖文排版、雙欄對比的專業 .pptx 檔案供下載。

### 場景 B：法遵政策比對
> **使用者**：上傳新舊兩版「員工行為準則」。
>
> **AI (Policy Analysis)**：
> 1. 解析兩份文件內容。
> 2. 逐條比對差異。
> 3. 輸出差異對照表，標示「新增」、「刪除」、「修改」的條款。

---

## 📊 數據與分析
平台內建儀表板，提供 Token 使用量統計、熱門技能分析與模型效能監控。

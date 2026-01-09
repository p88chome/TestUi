# 企業級全方位 AI 代理平台 (Enterprise Agentic AI Platform)

歡迎使用 **All平台** —— 這是一個次世代的 AI 應用框架，旨在超越傳統的聊天機器人 (Chatbot)，構建真正具備 **自主思考** 與 **執行能力** 的智慧代理人 (Intelligent Agent)。

本專案整合了 Azure OpenAI 的強大語言能力與模組化的工具系統，讓 AI 不僅能「說」，更能「做」。

## 🚀 專案願景 (Vision)
打造一個企業級的 AI 大腦，它能像專業員工一樣：
1.  **聽得懂**：理解複雜的上下文與多輪對話 (Context Awareness)。
2.  **分得清**：根據任務需求，切換不同的專業角色 (Role-Based Personnel)。
3.  **做得到**：主動呼叫工具 API 來完成任務 (Tool Execution)。

---

## ✨ 核心架構：標準元件庫 (Standard Component Library)

本平台的核心理念是將各類 AI 能力封裝為標準化的「元件」，企業可根據業務場景 (如費用申報、合約審閱) 自由組合這些元件：

### 🧱 核心元件 (Core Components)

| 元件名稱 (Component) | 對應技能 (Skill) | 功能描述 (Description) |
| :--- | :--- | :--- |
| **AIOCR** | `ocr_processor`, `receipt_extractor` | 針對票據、掃描文件做文字擷取與欄位結構化。 |
| **AIREAD** | `legal_contract_review`, `pdf_manager` | 長文閱讀、摘要、關鍵條款與風險抽取。 |
| **AI Excel** | `excel_handler` | 讀取/寫入 Excel，自動整理表格、運算欄位。 |
| **AI Intent** | `AgentService (Router)` | 判斷使用者意圖 (問答、查資料、算圖、做表)。 |
| **AI Drawing** * | `matplotlib_skill` (Planned) | 根據資料產生趨勢圖、分佈圖。 |
| **AI to SQL** * | `sql_generator` (Planned) | 自然語言轉 SQL，直接查詢資料庫。 |
| **AI Doc Compare** * | `doc_comparator` (Planned) | 兩份文件版次比對 (如新舊合約差異)。 |
| **AI Science** | `astropy`, `biopython`, `sympy` | 科學計算、天文數據分析、生物資訊處理。 |
| **AI Writer** | `docx_writer` | 自動生成 Word 報告與文檔。 |
| **Skill Discovery** | `skill_discovery` | 動態技能查找與載入。 |

*(標示 `*` 為 Roadmap 開發中項目)*

### 🚀 應用場景組合 (Flow Composition)

#### 1. 費用申報流程 (Expense Flow)
> **組合公式**：`AIOCR` (讀發票) + `AI Excel` (填報表)
> 說明：自動從收據照片提取金額、統編，並填入標準報銷 Excel 檔。

#### 2. 合約審閱流程 (Legal Review Flow)
> **組合公式**：`AIOCR` (讀掃描檔) + `AIREAD` (風險分析)
> 說明：將紙本合約數位化後，自動標註高風險條款與缺失項目。

#### 3. 稽核抽樣分析 (Audit Sampling Flow)
> **組合公式**：`AI to SQL` (撈資料) + `AI Drawing` (畫分佈)
> 說明：「幫我挑出 Q3 金額 > 10萬的異常採購案，並畫出部門分佈圖。」

#### 4. 科學研究流程 (Scientific Research Flow)
> **組合公式**：`AI Science` (計算) + `AI Writer` (寫報告)
> 說明：自動分析實驗數據，利用 Astropy 計算天文參數，並生成實驗報告。

---

## ⚙️ 核心引擎 (Workflow Engine)

本平台具備強大的工作流引擎，支援動態定義與執行任務：

- **Dynamic Workflows**: 透過 JSON 定義工作流步驟 (Steps)，支援條件判斷與迴圈。
- **Task Packages**: 將輸入資料打包，在不同步驟間傳遞。
- **Execution Tracking**: 完整記錄每一步驟的執行結果、日誌與狀態 (Running, Completed, Failed)。

---

## 🌐 社群與支持 (Community & Support)

- **Platform News**: 管理員可發布平台公告與更新資訊。
- **User Feedback**: 內建使用者回饋系統，收集 Bug 回報與功能建議。
---

## 🏗️ 系統架構 (System Architecture)

本平台採用現代化的前後端分離架構：

- **Frontend (前端)**：
  - **Framework**: Vue.js 3 + TypeScript
  - **UI Library**: PrimeVue (現代化、響應式設計)
  - **Features**: 支援即時對話串流、Markdown 渲染、檔案上傳、角色切換。

- **Backend (後端)**：
  - **Framework**: FastAPI (高效能 Python Web 框架)
  - **AI Engine**: Azure OpenAI Service (GPT-4 / GPT-3.5 Turbo)
  - **Database**: PostgreSQL (SQLAlchemy ORM) 用於儲存對話歷史、使用者資料與使用量統計。

- **Infrastructure**:
  - Docker Containerization (部署友善)
  - Azure Cloud Services Integration

---

## 💡 應用場景示範 (Use Cases)

### 場景 A：法務合約初審
> **使用者**：「我是 Tony，請幫我審閱這份供應商合約。」(上傳 PDF)
> 
> **AI (Legal Bot)**：
> 1. 自動呼叫 **OCR Tool** 讀取 PDF 內容。
> 2. 呼叫 **Contract Review Skill** 進行風險分析。
> 3. 綜合兩者結果，輸出：「Tony 您好，這份合約在『賠償上限』條款上有高風險，建議修改...」

### 場景 B：精密計算
> **使用者**：「15 + 24 等於多少？然後把結果乘以 3。」
> 
> **AI (General Bot)**：
> 1. 識別數學意圖，呼叫 **SymPy Tool** 計算 15+24=39。
> 2. 記憶 39，再次呼叫工具計算 39*3。
> 3. 回答：「最終結果是 117。」

---

## 📊 數據與分析 (Dashboard)
平台內建儀表板，提供：
- **Token 使用量統計**：精確追蹤每一筆對話的成本。
- **熱門技能分析**：了解哪些工具最常被員工使用。
- **模型效能監控**。

---

此專案展示了企業如何利用 LLM 技術構建專屬的智慧工作流，不僅提升效率，更將 AI 應用從「玩具」提升至「工具」層級。

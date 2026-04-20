# CLAUDE.md

此檔案提供 Claude Code (claude.ai/code) 在此專案中工作時的指引。

## 專案概述

企業級 AI 平台，包含 **FastAPI 後端**（`/app/`）與 **Vue 3 前端**（`/frontend/`）。支援多供應商 LLM 路由（Azure OpenAI、Google Gemini）、模組化技能系統、文件處理（PPTX、DOCX、PDF），以及具 DAG 執行能力的工作流程。

## 開發指令

### 後端
```bash
# 啟動開發伺服器
uvicorn app.main:app --reload

# 執行所有測試
pytest

# 執行單一測試檔案
pytest tests/test_skills.py -v

# 資料庫遷移
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### 前端
```bash
cd frontend
npm install
npm run dev      # Vite 開發伺服器，埠號 localhost:5173
npm run build    # 型別檢查（vue-tsc）後進行 Vite 打包
npm run preview  # 預覽正式版本
```

### 環境設定
將 `.env.example` 複製為 `.env`，最低需求如下：
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_platform
EXECUTION_MODE=mock   # 或: azure, gemini, on_prem
SECRET_KEY=<產生方式: python -c "import secrets; print(secrets.token_urlsafe(64))">
```

## 架構說明

### 後端（`/app/`）

**進入點**：`app/main.py` — lifespan handler 依序執行 Alembic 遷移 → `init_db()` → 技能載入。CORS 依環境設定（正式環境使用 `CLIENT_ORIGIN` 環境變數）。

**請求流程**：前端 axios（標頭夾帶 JWT）→ FastAPI 路由 → `Depends(deps.get_current_user)` + `Depends(get_db)` → service/ORM → Pydantic 回應。

**路由器**（`app/routers/`）：18 個路由器，統一掛載於 `/api/v1/`。重要項目：`auth`、`users`、`chat`、`agent`、`skills`、`workflows`、`runs`、`flowchart`、`ppt`、`meeting`、`policy`。

**服務層**（`app/services/`）：
- `llm_service.py` — 供應商無關的 LLM 呼叫；依 `AIModel.provider` 欄位路由至 Azure 或 Gemini。Azure 推理模型（o1、o3、o4-mini）使用 `max_completion_tokens`，一般模型使用 `max_tokens`。
- `workflow_engine.py` — DAG 執行與步驟串接
- `agent_service.py` — Agent 推理與工具呼叫
- `skill_loader.py` — 啟動時掃描 `/app/skills/`，解析各技能 `SKILL.md` 的 YAML frontmatter，並寫入資料庫

**模型**（`app/models/`）：核心實體位於 `domain.py`（Workflow、Component、RunExecution、AIModel）。使用者/驗證位於 `user.py`。`stats.py` 的 `UsageLog` 記錄每位使用者每個模型的 token 用量與費用。

**設定**（`app/core/config.py`）：Pydantic `Settings`，支援四種 `EXECUTION_MODE`：`mock`、`azure`、`gemini`、`on_prem`；三種 `EMAIL_PROVIDER`：`smtp`、`azure_acs`、`none`。

### 前端（`/frontend/src/`）

**進入點**：`main.ts` → 建立 Vue app，註冊 Pinia、Vue Router、PrimeVue（Aura 主題），最後掛載。`App.vue` 在載入時從 `localStorage` 恢復使用者 session。

**路由**（`router/index.ts`）：每次路由切換都會呼叫 `/users/me` 驗證 token。路由 `meta` 旗標：`requiresAuth`、`adminOnly`、`requiresPro`。

**狀態管理**（`stores/`）：`auth.ts` 管理 token/使用者；`theme.ts` 處理主題切換。兩者均為 Pinia store，元件層級狀態使用 Composition API 的 `ref()`。

**API 層**（`api/`）：Axios 實例內建 JWT 攔截器（自動從 `localStorage['token']` 注入）。依資源分模組：`agent.ts`、`chat.ts`、`skills.ts`、`models.ts` 等。Base URL 為 `/api/v1`（開發環境由 Vite proxy 轉發至 `localhost:8000`）。

**UI**：PrimeVue 4.x 搭配 Aura 主題。路徑別名 `@` → `src/`。未設定 linter。

### 技能系統（`/app/skills/`）

每個技能為一個目錄，包含帶有 YAML frontmatter（name、description、version、tags）的 `SKILL.md`，以及可選的 `tests/` 測試資料。技能在每次應用程式啟動時由 `skill_loader.py` 自動載入。新增技能只需建立目錄與 `SKILL.md` 即可自動被探索。

### 測試（`/tests/`）

`conftest.py` 提供 `db_session`（SQLite 記憶體模式）與 `mock_skill` fixtures。測試檔案：`test_skills.py`、`test_skills_logic.py`、`test_agent.py`、`test_guardrails.py`。`pytest.ini` 設定 `pythonpath = .`。

## 重要慣例

- 所有 API 路徑前綴為 `/api/v1/...`，定義於 `app/core/config.py` 的 `API_V1_STR`。
- 資料庫 session 透過 `Depends(get_db)` 注入；不可在路由處理器中手動建立 session。
- LLM 呼叫必須經過 `llm_service.py`，不可直接呼叫供應商 SDK，以確保用量記錄與供應商路由正常運作。
- Vue 元件使用 `<script setup>`（Composition API），不使用 Options API。
- 前端頁面放在 `src/pages/`，可重用 UI 元件放在 `src/components/`。

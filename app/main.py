import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from app.core.config import settings
from app.core.logging_config import setup_logging, RequestLoggingMiddleware
from app.routers import components, workflows, runs, auth, users, models, ocr, chat, stats, news, skills, agent, feedback, system, meeting, policy, ppt, flowchart
from app.core.database import SessionLocal
from app.initial_data import init_db

# 初始化結構化日誌（在 import 階段就生效）
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # === STARTUP ===
    logger.info(">>> STARTING APP: Configuring Database & Skills...")
    
    # 1. Run Alembic migration to ensure schema is up to date
    try:
        from sqlalchemy import inspect
        from app.core.database import engine
        
        alembic_cfg = AlembicConfig("alembic.ini")
        
        # 檢查是否為「舊版資料庫」（有 users 表但沒有 alembic_version 表）
        # 這代表 DB 是由舊版 Base.metadata.create_all() 建立的
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        has_alembic = "alembic_version" in tables
        has_existing_tables = "users" in tables
        
        if has_existing_tables and not has_alembic:
            # 舊資料庫 → 標記為基準點 (baseline)，然後執行接下來的升級
            logger.info("Detected existing database without Alembic. Stamping baseline...")
            alembic_command.stamp(alembic_cfg, "1c9bea9a0fd1")
            alembic_command.upgrade(alembic_cfg, "head")
            logger.info("Database migrated from baseline to head.")
        else:
            # 檢查是否發生了「被誤標記為 head 但其實沒有升級」的慘案
            columns = [c["name"] for c in inspector.get_columns("users")]
            if "is_verified" not in columns:
                logger.warning("⚠️ DB schema is missing updates. Forcing stamp to baseline and rolling forward...")
                alembic_command.stamp(alembic_cfg, "1c9bea9a0fd1")
                alembic_command.upgrade(alembic_cfg, "head")
            else:
                # 正常 upgrade
                alembic_command.upgrade(alembic_cfg, "head")
                logger.info("Database migration completed successfully.")
    except Exception as e:
        logger.error(f"Alembic migration failed: {e}")

    # 2. Init DB data and load skills
    db = SessionLocal()
    try:
        init_db(db)
        # 3. Load Skills from File System
        from app.services.skill_loader import load_skills
        load_skills(db)
    except Exception as e:
        logger.error(f"Init DB failed: {e}")
    finally:
        db.close()
    
    logger.info(">>> APP READY")
    
    yield  # Application runs here
    
    # === SHUTDOWN ===
    logger.info(">>> SHUTTING DOWN APP...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS — 根據環境自動決定允許的來源
origins = [settings.CLIENT_ORIGIN]
if settings.ENV == "development":
    # 開發環境才允許 localhost
    origins.append("http://localhost:5173")
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware — 自動記錄每個 API 的回應時間
app.add_middleware(RequestLoggingMiddleware)

# Trust Proxy Headers (Fixed for Azure/SWA)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

@app.middleware("http")
async def set_https_scheme(request, call_next):
    """
    Force HTTPS scheme for generated URLs if we are behind a proxy.
    This fixes the Mixed Content error on redirects.
    """
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto:
        request.scope["scheme"] = forwarded_proto
    return await call_next(request)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
app.include_router(components.router, prefix="/api/v1")
app.include_router(models.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")
app.include_router(meeting.router, prefix="/api/v1")
app.include_router(policy.router, prefix="/api/v1")
app.include_router(ppt.router, prefix="/api/v1")
app.include_router(flowchart.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "AI Platform API is running"}


@app.get("/health")
def health_check():
    """Health check endpoint for Docker/Azure monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENV,
    }

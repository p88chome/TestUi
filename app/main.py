from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import components, workflows, runs, auth, users, models, ocr, chat, stats, news, skills, agent, feedback, system
from app.core.database import engine, Base
from app.models.user import User 
from app.models.stats import UsageLog 
from app.models.news import PlatformNews 
from app.models.skill import Skill
from app.models.feedback import Feedback # Ensure table creation

# Create tables on startup (for MVP simplicity, instead of Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from app.core.database import SessionLocal
from app.initial_data import init_db
from app.migrate_db import migrate

@app.on_event("startup")
def on_startup():
    print(">>> STARTING APP: Configuring Database & Skills...")
    # 1. Run migration to ensure schema is up to date (plan columns)
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed (might be fine if fresh DB): {e}")

    # 2. Init DB data
    db = SessionLocal()
    try:
        init_db(db)
        # 3. Load Skills from File System
        from app.services.skill_loader import load_skills
        load_skills(db)
    except Exception as e:
        print(f"Init DB failed: {e}")
    finally:
        db.close()

# CORS
# In production, set CLIENT_ORIGIN to your frontend domain (e.g. https://mypage.vercel.app)
origins = [
    settings.CLIENT_ORIGIN,
    "http://localhost:5173", # Keep local dev working
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/")
def root():
    return {"message": "AI Platform API is running"}

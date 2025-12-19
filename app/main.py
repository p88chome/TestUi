from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import components, workflows, runs, auth, users, models, ocr, chat
from app.core.database import engine, Base
from app.models.user import User # Ensure User table is created

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
    # 1. Run migration to ensure schema is up to date (plan columns)
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed (might be fine if fresh DB): {e}")

    # 2. Init DB data
    db = SessionLocal()
    try:
        init_db(db)
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

@app.get("/")
def root():
    return {"message": "AI Platform API is running"}

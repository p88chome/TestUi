"""
Alembic Environment Configuration
讓 Alembic 讀取專案的 DATABASE_URL 和所有 SQLAlchemy Models，
支援 autogenerate 自動偵測 schema 變更。
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ===== 匯入專案設定 =====
from app.core.config import settings
from app.core.database import Base

# 匯入所有 Model，確保 Alembic autogenerate 能偵測到
from app.models.user import User  # noqa: F401
from app.models.stats import UsageLog  # noqa: F401
from app.models.news import PlatformNews  # noqa: F401
from app.models.skill import Skill, SkillExecution  # noqa: F401
from app.models.feedback import Feedback  # noqa: F401
from app.models.chat import ChatSession, ChatMessage  # noqa: F401
from app.models.domain import Component, Workflow, RunExecution, AIModel  # noqa: F401
from app.models.task import TaskPackage  # noqa: F401
from app.models.assistant import Assistant  # noqa: F401

# Alembic Config 物件
config = context.config

# 動態設定 database URL（從 .env / 環境變數讀取，而非寫死在 alembic.ini）
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 設定 Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 讓 Alembic 知道我們的 MetaData（用於 autogenerate）
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    離線模式：產生 SQL 腳本，不需要真的連資料庫。
    適合需要 DBA 審查 SQL 的場景。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    線上模式：直接連接資料庫執行 migration。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

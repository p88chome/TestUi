import uuid
import logging
from datetime import timedelta, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import Token, User as UserSchema, UserRegister
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ─── 現有功能：登入 ────────────────────────────────────────────────────────────

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    # Use generic error message to prevent user enumeration attacks
    credentials_exception = HTTPException(
        status_code=400,
        detail="Incorrect email or password"
    )

    if not user:
        logger.warning("Login failed: invalid credentials attempt")
        raise credentials_exception

    if not security.verify_password(form_data.password, user.hashed_password):
        logger.warning("Login failed: invalid credentials attempt")
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Check email verification
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="帳號尚未驗證。請至信箱點擊驗證連結，或重新寄送驗證信。"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/users/me", response_model=UserSchema)
def read_users_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


# ─── 新功能：公開註冊 ──────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserRegister,
    db: Session = Depends(get_db),
) -> Any:
    """
    公開註冊端點。
    建立帳號（未啟用），產生驗證 token，寄出驗證信。
    """
    # 檢查 Email 是否已存在
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        if existing.is_verified:
            raise HTTPException(
                status_code=400,
                detail="此 Email 已被使用。請直接登入，或使用忘記密碼功能。"
            )
        else:
            # 帳號已存在但未驗證 → 重新寄一封驗證信
            _refresh_and_send_verification(existing, db)
            return {
                "message": "驗證信已重新寄出，請至信箱確認。",
                "email": user_in.email
            }

    # 建立新帳號（is_active=False, is_verified=False）
    token = str(uuid.uuid4())
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=False,         # 驗證後才啟用
        is_verified=False,
        is_superuser=False,
        verification_token=token,
        verification_token_expires=expires,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 寄驗證信
    verification_url = f"{settings.CLIENT_ORIGIN}/verify-email?token={token}"
    email_svc = get_email_service()
    await email_svc.send_verification_email(
        to_email=user.email,
        full_name=user.full_name or user.email,
        verification_url=verification_url,
    )

    logger.info(f"New user registered: {user.email}")
    return {
        "message": "註冊成功！驗證信已寄出，請至信箱點擊連結完成驗證。",
        "email": user.email
    }


# ─── 新功能：Email 驗證 ────────────────────────────────────────────────────────

@router.get("/verify-email")
async def verify_email(
    token: str = Query(..., description="Email 驗證 token"),
    db: Session = Depends(get_db),
) -> Any:
    """
    驗證 Email token，驗證通過後啟用帳號。
    """
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="驗證連結無效或已失效，請重新申請驗證信。"
        )

    # 檢查 token 是否過期
    now = datetime.now(timezone.utc)
    expires = user.verification_token_expires

    # 處理 timezone-naive datetime（來自 DB 的可能沒有 tz info）
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if not expires or now > expires:
        raise HTTPException(
            status_code=400,
            detail="驗證連結已過期（有效期 24 小時），請重新申請驗證信。"
        )

    # 驗證通過，啟用帳號
    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    db.refresh(user)

    # 寄歡迎信
    email_svc = get_email_service()
    await email_svc.send_welcome_email(
        to_email=user.email,
        full_name=user.full_name or user.email,
    )

    logger.info(f"User verified: {user.email}")
    return {
        "message": "帳號驗證成功！您現在可以登入使用 AI Platform。",
        "email": user.email
    }


# ─── 新功能：重寄驗證信 ────────────────────────────────────────────────────────

@router.post("/resend-verification")
async def resend_verification(
    email: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    重新寄送驗證信（限未驗證帳號）。
    """
    user = db.query(User).filter(User.email == email).first()

    # 不論是否找到，都回相同訊息（防止 Email 枚舉攻擊）
    generic_message = {
        "message": "如果此 Email 已登記且尚未驗證，我們已重新寄出驗證信。"
    }

    if not user or user.is_verified:
        return generic_message

    _refresh_and_send_verification(user, db)
    return generic_message


# ─── 輔助函式 ──────────────────────────────────────────────────────────────────

def _refresh_and_send_verification(user: User, db: Session):
    """更新驗證 token 並寄信（同步包裝）"""
    import asyncio

    token = str(uuid.uuid4())
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    user.verification_token = token
    user.verification_token_expires = expires
    db.commit()

    verification_url = f"{settings.CLIENT_ORIGIN}/verify-email?token={token}"
    email_svc = get_email_service()

    # 如果在非 async 環境呼叫，用 asyncio.run；否則建立 task
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(
            email_svc.send_verification_email(
                to_email=user.email,
                full_name=user.full_name or user.email,
                verification_url=verification_url,
            )
        )
    except RuntimeError:
        asyncio.run(
            email_svc.send_verification_email(
                to_email=user.email,
                full_name=user.full_name or user.email,
                verification_url=verification_url,
            )
        )

from datetime import timedelta
from typing import Any
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import Token, User as UserSchema

# Configure logger - in production, use structured logging
logger = logging.getLogger(__name__)

router = APIRouter()

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
        # Log failed attempt without exposing which field was wrong
        logger.warning("Login failed: invalid credentials attempt")
        raise credentials_exception
    
    if not security.verify_password(form_data.password, user.hashed_password):
        logger.warning("Login failed: invalid credentials attempt")
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
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

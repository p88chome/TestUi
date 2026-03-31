from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator, ConfigDict, field_validator
import re

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    
    # Subscription Plan
    plan_name: Optional[str] = "Starter"
    plan_price: Optional[str] = "Free"
    plan_expiry: Optional[str] = None
    tenant_id: Optional[str] = "default"

# Properties to receive via API on creation (admin only)
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Public registration schema (no admin fields)
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密碼需至少 8 個字元")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密碼需包含至少一個英文字母")
        if not re.search(r"\d", v):
            raise ValueError("密碼需包含至少一個數字")
        return v

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    plan_name: Optional[str] = None
    plan_price: Optional[str] = None
    plan_expiry: Optional[str] = None
    tenant_id: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# Additional properties to return via API
class User(UserInDBBase):
    organization: Optional[str] = None
    is_verified: Optional[bool] = False

    @model_validator(mode='after')
    def compute_organization(self):
        mapping = {
            "deloitte": "Deloitte",
            "default": "Default Org"
        }
        self.organization = mapping.get(self.tenant_id, self.tenant_id)
        return self
    
    model_config = ConfigDict(from_attributes=True)


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

"""Pydantic schemas for User and Authentication"""

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base user properties"""
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Properties to receive via API on creation"""
    password: str


class UserUpdate(UserBase):
    """Properties to receive via API on update"""
    password: Optional[str] = None


class UserResponse(UserBase):
    """Properties to return via API"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """JWT Token payload"""
    sub: Optional[int] = None

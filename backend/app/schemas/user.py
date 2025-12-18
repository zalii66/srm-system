from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.role import Role


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    is_active: bool = Field(True, description="是否激活")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role_ids: Optional[List[int]] = Field(default=[], description="角色ID列表")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    role_ids: Optional[List[int]] = None


class User(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    roles: List[Role] = []
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


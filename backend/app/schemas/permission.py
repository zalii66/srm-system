from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="权限名称")
    code: str = Field(..., min_length=2, max_length=50, description="权限编码")
    resource: str = Field(..., max_length=100, description="资源")
    action: str = Field(..., max_length=50, description="操作")
    description: Optional[str] = Field(None, description="权限描述")
    is_active: bool = Field(True, description="是否激活")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    resource: Optional[str] = Field(None, max_length=100)
    action: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Permission(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.permission import Permission


class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="角色名称")
    code: str = Field(..., min_length=2, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")
    is_active: bool = Field(True, description="是否激活")


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: Optional[List[Permission]] = None
    
    class Config:
        from_attributes = True


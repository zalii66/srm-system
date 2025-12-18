from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OperationLogBase(BaseModel):
    """操作日志基础模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: Optional[int] = None
    resource_name: Optional[str] = None
    description: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None


class OperationLogCreate(OperationLogBase):
    """创建操作日志"""
    pass


class OperationLog(OperationLogBase):
    """操作日志"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OperationLogQuery(BaseModel):
    """操作日志查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


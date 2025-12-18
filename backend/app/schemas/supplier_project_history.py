from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SupplierProjectHistoryCreate(BaseModel):
    """创建供应商项目历史"""
    supplier_id: int = Field(..., description="供应商ID")
    project_id: int = Field(..., description="项目ID")
    company_id: Optional[int] = Field(None, description="所属公司ID")
    participated_at: Optional[datetime] = None
    is_winner: int = Field(0, ge=0, le=1, description="是否中标")
    contract_amount: Optional[Decimal] = Field(None, ge=0, description="合同金额")
    quality_score: Optional[int] = Field(None, ge=1, le=5, description="质量评分")
    service_score: Optional[int] = Field(None, ge=1, le=5, description="服务评分")
    delivery_score: Optional[int] = Field(None, ge=1, le=5, description="交付评分")
    overall_rating: Optional[str] = Field(None, max_length=20, description="综合评价")
    remarks: Optional[str] = None


class SupplierProjectHistoryUpdate(BaseModel):
    """更新供应商项目历史"""
    is_winner: Optional[int] = Field(None, ge=0, le=1)
    contract_amount: Optional[Decimal] = Field(None, ge=0)
    quality_score: Optional[int] = Field(None, ge=1, le=5)
    service_score: Optional[int] = Field(None, ge=1, le=5)
    delivery_score: Optional[int] = Field(None, ge=1, le=5)
    overall_rating: Optional[str] = Field(None, max_length=20)
    remarks: Optional[str] = None


class SupplierProjectHistory(BaseModel):
    """供应商项目历史"""
    id: int
    supplier_id: int
    project_id: int
    company_id: Optional[int]
    participated_at: Optional[datetime]
    is_winner: int
    contract_amount: Optional[Decimal]
    quality_score: Optional[int]
    service_score: Optional[int]
    delivery_score: Optional[int]
    overall_rating: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


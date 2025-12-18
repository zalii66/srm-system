from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.quotation import QuotationStatus


class QuotationItemCreate(BaseModel):
    """报价明细创建"""
    project_item_id: int = Field(..., description="项目明细ID")
    unit_price: Decimal = Field(..., gt=0, description="单价")
    quantity: Decimal = Field(..., gt=0, description="数量")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="型号")
    remarks: Optional[str] = None


class QuotationItemUpdate(BaseModel):
    """报价明细更新"""
    unit_price: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None, gt=0)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None


class ProjectItemSimple(BaseModel):
    """项目明细简要信息"""
    id: int
    item_no: str
    item_name: str
    specification: Optional[str]
    unit: Optional[str]
    quantity: Decimal
    
    class Config:
        from_attributes = True


class QuotationItem(BaseModel):
    """报价明细"""
    id: int
    quotation_id: int
    project_item_id: int
    unit_price: Decimal
    quantity: Decimal
    amount: Decimal
    brand: Optional[str]
    model: Optional[str]
    remarks: Optional[str]
    project_item: Optional[ProjectItemSimple] = None
    
    class Config:
        from_attributes = True


class QuotationCreate(BaseModel):
    """报价创建"""
    project_id: int = Field(..., description="项目ID")
    tax_rate: Decimal = Field(0.13, ge=0, le=1, description="税率")
    delivery_days: Optional[int] = Field(None, gt=0, description="交货天数")
    payment_terms: Optional[str] = Field(None, max_length=200, description="付款条件")
    warranty_period: Optional[str] = Field(None, max_length=100, description="质保期")
    remarks: Optional[str] = None
    items: List[QuotationItemCreate] = Field(..., min_items=1, description="报价明细")


class QuotationUpdate(BaseModel):
    """报价更新"""
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    delivery_days: Optional[int] = Field(None, gt=0)
    payment_terms: Optional[str] = Field(None, max_length=200)
    warranty_period: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None
    items: Optional[List[QuotationItemCreate]] = Field(None, description="报价明细（可选，如果提供则更新明细）")


class QuotationEvaluate(BaseModel):
    """报价评审"""
    status: QuotationStatus = Field(..., description="评审状态")
    evaluation_comment: str = Field(..., min_length=1, description="评审意见（必填）")


class SupplierSimple(BaseModel):
    """供应商简要信息"""
    id: int
    company_name: str
    
    class Config:
        from_attributes = True


class ProjectSimple(BaseModel):
    """项目简要信息"""
    id: int
    project_name: str
    
    class Config:
        from_attributes = True


class Quotation(BaseModel):
    """报价信息"""
    id: int
    quotation_no: str
    project_id: int
    supplier_id: int
    total_amount: Decimal
    project: Optional[ProjectSimple] = None
    tax_rate: Decimal
    delivery_days: Optional[int]
    payment_terms: Optional[str]
    warranty_period: Optional[str]
    status: QuotationStatus
    attachments: Optional[str]
    remarks: Optional[str]
    submitted_at: Optional[datetime]
    evaluated_by: Optional[int]
    evaluated_at: Optional[datetime]
    evaluation_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[QuotationItem] = []
    supplier: Optional[SupplierSimple] = None
    
    class Config:
        from_attributes = True


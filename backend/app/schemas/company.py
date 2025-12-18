from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    """公司基础信息"""
    company_name: str = Field(..., min_length=2, max_length=200, description="公司名称")
    brand_id: Optional[int] = Field(None, description="所属品牌ID")
    address: Optional[str] = Field(None, max_length=500, description="详细地址")
    description: Optional[str] = None
    is_active: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序")


class CompanyCreate(CompanyBase):
    """创建公司"""
    company_code: str = Field(..., min_length=2, max_length=50, description="公司编码")


class CompanyUpdate(BaseModel):
    """更新公司"""
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    brand_id: Optional[int] = None
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class BrandSimple(BaseModel):
    """品牌简要信息（用于公司列表）"""
    id: int
    brand_name: str
    
    class Config:
        from_attributes = True


class Company(CompanyBase):
    """公司信息"""
    id: int
    company_code: str
    brand: Optional[BrandSimple] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


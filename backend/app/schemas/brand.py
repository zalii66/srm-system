from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    """品牌基础信息"""
    brand_name: str = Field(..., min_length=2, max_length=200, description="品牌名称")
    description: Optional[str] = None
    is_active: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序")


class BrandCreate(BrandBase):
    """创建品牌"""
    brand_code: str = Field(..., min_length=2, max_length=50, description="品牌编码")


class BrandUpdate(BaseModel):
    """更新品牌"""
    brand_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class Brand(BrandBase):
    """品牌信息"""
    id: int
    brand_code: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCategoryBase(BaseModel):
    """项目类别基础信息"""
    category_name: str = Field(..., min_length=2, max_length=200, description="类别名称")
    description: Optional[str] = None
    is_active: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序")


class ProjectCategoryCreate(ProjectCategoryBase):
    """创建项目类别"""
    category_code: str = Field(..., min_length=2, max_length=50, description="类别编码")


class ProjectCategoryUpdate(BaseModel):
    """更新项目类别"""
    category_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ProjectCategory(ProjectCategoryBase):
    """项目类别信息"""
    id: int
    category_code: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectCategorySimple(BaseModel):
    """项目类别简要信息（用于项目详情）"""
    id: int
    category_code: str
    category_name: str
    
    class Config:
        from_attributes = True

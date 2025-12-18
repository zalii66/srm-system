from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.schemas.project_category import ProjectCategorySimple
from app.models.project import ProjectStatus


class ProjectItemCreate(BaseModel):
    """项目明细创建"""
    item_no: Optional[str] = Field(None, max_length=50, description="明细编号（可选，如果不提供则根据项目编号自动生成）")
    item_name: str = Field(..., max_length=200, description="明细名称")
    specification: Optional[str] = Field(None, max_length=500, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., gt=0, description="数量")
    estimated_price: Optional[Decimal] = Field(None, ge=0, description="预估单价")
    description: Optional[str] = None


class ProjectItemUpdate(BaseModel):
    """项目明细更新"""
    item_name: Optional[str] = Field(None, max_length=200)
    specification: Optional[str] = Field(None, max_length=500)
    unit: Optional[str] = Field(None, max_length=20)
    quantity: Optional[Decimal] = Field(None, gt=0)
    estimated_price: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None


class ProjectItem(BaseModel):
    """项目明细"""
    id: int
    project_id: int
    item_no: str
    item_name: str
    specification: Optional[str]
    unit: Optional[str]
    quantity: Decimal
    estimated_price: Optional[Decimal]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    """项目创建"""
    project_name: str = Field(..., min_length=2, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    category_id: Optional[int] = Field(None, description="项目类别ID")
    location: Optional[str] = Field(None, max_length=200, description="项目地点")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    bidding_deadline: Optional[datetime] = None
    branch_office: Optional[str] = Field(None, max_length=100, description="分公司")
    company_id: Optional[int] = Field(None, description="所属公司ID")
    attachments: Optional[str] = Field(None, description="附件文件ID列表（JSON数组）")
    items: List[ProjectItemCreate] = Field(default=[], description="项目明细")


class ProjectUpdate(BaseModel):
    """项目更新
    
    注意：状态字段不建议在更新接口中直接修改，应使用专门的接口：
    - POST /projects/{project_id}/publish - 发布项目（已停止 -> 进行中）
    - POST /projects/{project_id}/stop - 停止项目（进行中/竞标中 -> 已停止）
    - POST /projects/{project_id}/cancel - 取消项目
    如果确实需要修改状态，系统会验证状态转换是否合法。
    """
    project_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = Field(None, description="项目类别ID")
    location: Optional[str] = Field(None, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    bidding_deadline: Optional[datetime] = None
    branch_office: Optional[str] = Field(None, max_length=100)
    company_id: Optional[int] = None
    attachments: Optional[str] = None
    status: Optional[int] = Field(
        None, 
        ge=0, 
        le=5, 
        description="项目状态（0已停止/1进行中/3竞标中/4已完成/5已取消）。注意：建议使用专门的接口修改状态，系统会验证状态转换是否合法。"
    )


class CompanySimple(BaseModel):
    """公司简要信息（用于项目详情）"""
    id: int
    company_name: str
    brand_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class Project(BaseModel):
    """项目信息"""
    id: int
    project_no: str
    project_name: str
    description: Optional[str]
    category_id: Optional[int] = None
    category: Optional[ProjectCategorySimple] = None
    location: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    bidding_deadline: Optional[datetime]
    status: int = Field(..., description="项目状态（0已停止/1进行中/3竞标中/4已完成/5已取消）")
    creator_id: int
    branch_office: Optional[str]
    attachments: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[ProjectItem] = []
    company: Optional[CompanySimple] = None
    
    class Config:
        from_attributes = True


class CreatorSimple(BaseModel):
    """创建人简要信息（用于项目列表）"""
    id: int
    username: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """项目列表项（不包含items明细）"""
    id: int
    project_no: str
    project_name: str
    description: Optional[str]
    category_id: Optional[int] = None
    category: Optional[ProjectCategorySimple] = None
    location: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    bidding_deadline: Optional[datetime]
    status: int = Field(..., description="项目状态（0已停止/1进行中/3竞标中/4已完成/5已取消）")
    creator_id: int
    creator: Optional[CreatorSimple] = None
    branch_office: Optional[str]
    attachments: Optional[str]
    quotation_count: int = Field(default=0, description="报价数量")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


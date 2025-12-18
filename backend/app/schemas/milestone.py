from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MilestoneBase(BaseModel):
    """时间节点基础模型"""
    milestone_name: str = Field(..., min_length=1, max_length=200, description="节点名称")
    description: Optional[str] = Field(None, description="节点描述")
    planned_date: Optional[datetime] = Field(None, description="计划时间")
    actual_date: Optional[datetime] = Field(None, description="实际完成时间")
    status: Optional[int] = Field(0, ge=0, le=4, description="状态：0待开始/1进行中/2已完成/3已延期/4已取消")
    progress: Optional[int] = Field(0, ge=0, le=100, description="完成进度（0-100）")
    sort_order: Optional[int] = Field(0, description="排序")
    is_critical: Optional[bool] = Field(False, description="是否关键节点")
    is_visible_to_supplier: Optional[bool] = Field(True, description="供应商是否可见")


class MilestoneCreate(MilestoneBase):
    """创建时间节点"""
    pass


class MilestoneUpdate(BaseModel):
    """更新时间节点"""
    milestone_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    planned_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    status: Optional[int] = Field(None, ge=0, le=4)
    progress: Optional[int] = Field(None, ge=0, le=100)
    sort_order: Optional[int] = None
    is_critical: Optional[bool] = None
    is_visible_to_supplier: Optional[bool] = None


class Milestone(MilestoneBase):
    """时间节点详情"""
    id: int
    project_id: int
    milestone_code: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MilestoneComplete(BaseModel):
    """标记节点完成"""
    actual_date: Optional[datetime] = Field(None, description="实际完成时间（不传则使用当前时间）")


class MilestoneReorder(BaseModel):
    """批量更新节点顺序"""
    milestone_ids: list[int] = Field(..., description="按新顺序排列的节点ID列表")


class ProjectProgress(BaseModel):
    """项目进度信息"""
    project_id: int
    total_progress: int = Field(..., ge=0, le=100, description="总进度百分比")
    completed_milestones: int = Field(..., description="已完成节点数")
    total_milestones: int = Field(..., description="总节点数")
    critical_milestones: dict = Field(..., description="关键节点统计")
    milestones: list[Milestone] = Field(default=[], description="节点列表")
    
    class Config:
        from_attributes = True


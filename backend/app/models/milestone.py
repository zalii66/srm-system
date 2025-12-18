from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class MilestoneStatus:
    """时间节点状态常量"""
    PENDING = 0      # 待开始（计划时间未到）
    IN_PROGRESS = 1  # 进行中（计划时间已到，但未完成）
    COMPLETED = 2    # 已完成（已标记完成或实际时间已设置）
    DELAYED = 3      # 已延期（计划时间已过，但未完成）
    CANCELLED = 4    # 已取消


class ProjectMilestone(Base):
    """项目时间节点表"""
    __tablename__ = "project_milestones"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, comment="项目ID")
    
    # 基本信息
    milestone_name = Column(String(200), nullable=False, comment="节点名称")
    milestone_code = Column(String(50), nullable=True, comment="节点编号")
    description = Column(Text, nullable=True, comment="节点描述")
    
    # 时间信息
    planned_date = Column(DateTime, nullable=True, comment="计划时间")
    actual_date = Column(DateTime, nullable=True, comment="实际完成时间")
    
    # 状态和进度
    status = Column(Integer, default=MilestoneStatus.PENDING, comment="状态：0待开始/1进行中/2已完成/3已延期/4已取消")
    progress = Column(Integer, default=0, comment="完成进度（0-100）")
    
    # 显示设置
    sort_order = Column(Integer, default=0, comment="排序")
    is_critical = Column(Boolean, default=False, comment="是否关键节点")
    is_visible_to_supplier = Column(Boolean, default=True, comment="供应商是否可见")
    
    # 元数据
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="milestones")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ProjectMilestone {self.milestone_name} - {self.project_id}>"


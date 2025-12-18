from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.db.database import Base


class ProjectStatus:
    """项目状态常量（int类型）
    
    0: 已停止
    1: 进行中
    3: 竞标中
    4: 已完成
    5: 已取消
    """
    STOPPED = 0  # 已停止
    ONGOING = 1  # 进行中
    BIDDING = 3  # 竞标中
    COMPLETED = 4  # 已完成
    CANCELLED = 5  # 已取消


class Project(Base):
    """招标项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_no = Column(String(50), unique=True, index=True, nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    description = Column(Text, nullable=True, comment="项目描述")
    
    # 项目信息
    category_id = Column(Integer, ForeignKey('project_categories.id'), nullable=True, comment="项目类别ID")
    location = Column(String(200), nullable=True, comment="项目地点")
    
    # 时间信息
    start_date = Column(DateTime, nullable=True, comment="项目开始时间")
    end_date = Column(DateTime, nullable=True, comment="项目结束时间")
    bidding_deadline = Column(DateTime, nullable=True, comment="投标截止时间")
    
    # 状态（int类型：0已停止/1进行中/3竞标中/4已完成/5已取消）
    status = Column(Integer, default=ProjectStatus.ONGOING, comment="项目状态")
    
    # 创建人（项目经理）
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment="创建人ID")
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, comment="所属公司ID")
    branch_office = Column(String(100), nullable=True, comment="分公司名称（备用字段）")
    
    # 附件
    attachments = Column(Text, nullable=True, comment="附件路径（JSON数组）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    creator = relationship("User", backref="projects", lazy="joined")
    company = relationship("Company", back_populates="projects", lazy="joined")
    category = relationship("ProjectCategory", lazy="joined")
    items = relationship("ProjectItem", back_populates="project", cascade="all, delete-orphan")
    quotations = relationship("Quotation", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan", order_by="ProjectMilestone.sort_order")
    
    def __repr__(self):
        return f"<Project {self.project_no} - {self.project_name}>"


class ProjectItem(Base):
    """项目明细表"""
    __tablename__ = "project_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, comment="项目ID")
    item_no = Column(String(50), nullable=False, comment="明细编号")
    item_name = Column(String(200), nullable=False, comment="明细名称")
    specification = Column(String(500), nullable=True, comment="规格型号")
    unit = Column(String(20), nullable=True, comment="单位")
    quantity = Column(Numeric(15, 2), nullable=False, comment="数量")
    estimated_price = Column(Numeric(15, 2), nullable=True, comment="预估单价")
    description = Column(Text, nullable=True, comment="说明")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="items")
    quotation_items = relationship("QuotationItem", back_populates="project_item")
    
    def __repr__(self):
        return f"<ProjectItem {self.item_no} - {self.item_name}>"


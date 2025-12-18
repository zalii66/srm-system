from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.db.database import Base
import enum


class QuotationStatus(str, enum.Enum):
    """报价状态"""
    DRAFT = "draft"  # 草稿
    SUBMITTED = "submitted"  # 已提交
    SELECTED = "selected"  # 中标
    REJECTED = "rejected"  # 未中标
    CANCELLED = "cancelled"  # 已取消


class Quotation(Base):
    """供应商报价表"""
    __tablename__ = "quotations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quotation_no = Column(String(50), unique=True, index=True, nullable=False, comment="报价单号")
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, comment="项目ID")
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, comment="供应商ID")
    
    # 报价信息
    total_amount = Column(Numeric(15, 2), nullable=False, comment="报价总金额")
    tax_rate = Column(Numeric(5, 2), default=0.13, comment="税率")
    delivery_days = Column(Integer, nullable=True, comment="交货天数")
    payment_terms = Column(String(200), nullable=True, comment="付款条件")
    warranty_period = Column(String(100), nullable=True, comment="质保期")
    
    # 状态
    status = Column(SQLEnum(QuotationStatus), default=QuotationStatus.DRAFT, comment="报价状态")
    
    # 附件和备注
    attachments = Column(Text, nullable=True, comment="附件路径（JSON数组）")
    remarks = Column(Text, nullable=True, comment="备注说明")
    
    # 提交和评审信息
    submitted_at = Column(DateTime, nullable=True, comment="提交时间")
    evaluated_by = Column(Integer, ForeignKey('users.id'), nullable=True, comment="评审人ID")
    evaluated_at = Column(DateTime, nullable=True, comment="评审时间")
    evaluation_comment = Column(Text, nullable=True, comment="评审意见")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="quotations")
    supplier = relationship("Supplier", backref="quotations")
    evaluator = relationship("User")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quotation {self.quotation_no}>"


class QuotationItem(Base):
    """报价明细表"""
    __tablename__ = "quotation_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quotation_id = Column(Integer, ForeignKey('quotations.id', ondelete='CASCADE'), nullable=False, comment="报价ID")
    project_item_id = Column(Integer, ForeignKey('project_items.id', ondelete='CASCADE'), nullable=False, comment="项目明细ID")
    
    # 报价信息
    unit_price = Column(Numeric(15, 2), nullable=False, comment="单价")
    quantity = Column(Numeric(15, 2), nullable=False, comment="数量")
    amount = Column(Numeric(15, 2), nullable=False, comment="金额")
    
    # 产品信息
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True, comment="品牌ID")
    brand = Column(String(100), nullable=True, comment="品牌名称（备用）")
    model = Column(String(100), nullable=True, comment="型号")
    origin = Column(String(100), nullable=True, comment="产地")
    
    remarks = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    quotation = relationship("Quotation", back_populates="items")
    project_item = relationship("ProjectItem", back_populates="quotation_items")
    brand_info = relationship("Brand", lazy="joined")
    
    def __repr__(self):
        return f"<QuotationItem {self.id}>"


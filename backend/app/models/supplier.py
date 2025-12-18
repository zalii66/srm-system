from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class SupplierStatus:
    """供应商状态常量（int类型）
    
    -1: 待审核
    0: 审核失败
    1: 审核通过
    """
    PENDING = -1  # 待审核
    REJECTED = 0  # 审核失败
    APPROVED = 1  # 审核通过


class Supplier(Base):
    """供应商信息表"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, comment="关联用户ID")
    company_name = Column(String(200), nullable=False, comment="公司名称")
    tax_number = Column(String(50), nullable=True, comment="公司税号")
    contact_person = Column(String(100), nullable=False, comment="联系人")
    contact_phone = Column(String(20), nullable=False, comment="联系电话")
    company_address = Column(String(500), nullable=True, comment="注册地址")
    business_scope = Column(Text, nullable=True, comment="主营产品")
    
    # 银行信息
    bank_account_name = Column(String(100), nullable=True, comment="账户名称")
    bank_name = Column(String(200), nullable=True, comment="开户行")
    bank_account = Column(String(50), nullable=True, comment="银行账号")
    
    # 资质信息
    qualification_docs = Column(Text, nullable=True, comment="资质文件路径（JSON数组）")
    status = Column(Integer, default=SupplierStatus.PENDING, comment="审核状态（-1待审核/0审核失败/1审核通过）")
    
    # 审核信息
    audit_user_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment="审核人ID")
    audit_time = Column(DateTime, nullable=True, comment="审核时间")
    audit_comment = Column(Text, nullable=True, comment="审核意见")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], backref="supplier_profile", lazy="joined")
    audit_user = relationship("User", foreign_keys=[audit_user_id])
    
    def __repr__(self):
        return f"<Supplier {self.company_name}>"


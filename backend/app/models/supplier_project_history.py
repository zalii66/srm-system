from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class SupplierProjectHistory(Base):
    """供应商项目参与历史表"""
    __tablename__ = "supplier_project_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False, comment="供应商ID")
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, comment="项目ID")
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, comment="所属公司ID")
    
    # 参与信息
    participated_at = Column(DateTime, nullable=True, comment="参与时间")
    is_winner = Column(Integer, default=0, comment="是否中标（0-未中标，1-中标）")
    contract_amount = Column(Numeric(15, 2), nullable=True, comment="合同金额")
    
    # 评价信息
    quality_score = Column(Integer, nullable=True, comment="质量评分（1-5）")
    service_score = Column(Integer, nullable=True, comment="服务评分（1-5）")
    delivery_score = Column(Integer, nullable=True, comment="交付评分（1-5）")
    overall_rating = Column(String(20), nullable=True, comment="综合评价（优秀/良好/一般/差）")
    
    # 备注
    remarks = Column(Text, nullable=True, comment="备注说明")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    supplier = relationship("Supplier", backref="project_history")
    project = relationship("Project", backref="supplier_history")
    company = relationship("Company", backref="supplier_history")
    
    def __repr__(self):
        return f"<SupplierProjectHistory supplier_id={self.supplier_id} project_id={self.project_id}>"


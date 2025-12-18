from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Company(Base):
    """公司（分公司）表"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_code = Column(String(50), unique=True, index=True, nullable=False, comment="公司编码")
    company_name = Column(String(200), unique=True, nullable=False, comment="公司名称")
    
    # 关联品牌（先有品牌，再有公司）
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True, comment="所属品牌ID")
    
    # 地址信息
    address = Column(String(500), nullable=True, comment="详细地址")
    
    # 其他信息
    description = Column(Text, nullable=True, comment="公司描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    brand = relationship("Brand", backref="companies")
    projects = relationship("Project", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.company_name}>"


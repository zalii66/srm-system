from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from app.db.database import Base


class Brand(Base):
    """品牌表"""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand_code = Column(String(50), unique=True, index=True, nullable=False, comment="品牌编码")
    brand_name = Column(String(200), unique=True, nullable=False, comment="品牌名称")
    
    # 其他信息
    description = Column(Text, nullable=True, comment="品牌描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self):
        return f"<Brand {self.brand_name}>"


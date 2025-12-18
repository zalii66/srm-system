from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from app.db.database import Base


class ProjectCategory(Base):
    """项目类别表"""
    __tablename__ = "project_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_code = Column(String(50), unique=True, index=True, nullable=False, comment="类别编码")
    category_name = Column(String(200), unique=True, nullable=False, comment="类别名称")
    
    # 其他信息
    description = Column(Text, nullable=True, comment="类别描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self):
        return f"<ProjectCategory {self.category_name}>"

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from app.models.role_permission import role_permission


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False, comment="权限名称")
    code = Column(String(50), unique=True, index=True, nullable=False, comment="权限编码")
    resource = Column(String(100), nullable=False, comment="资源")
    action = Column(String(50), nullable=False, comment="操作")
    description = Column(Text, nullable=True, comment="权限描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission {self.name}>"


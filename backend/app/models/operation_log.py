from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 用户信息
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment="操作用户ID")
    username = Column(String(50), nullable=True, comment="操作用户名")
    
    # 操作信息
    action = Column(String(50), nullable=False, comment="操作类型（create/update/delete/audit/evaluate/submit/cancel）")
    resource_type = Column(String(50), nullable=False, comment="资源类型（project/quotation/supplier/user/role/permission）")
    resource_id = Column(Integer, nullable=True, comment="资源ID")
    resource_name = Column(String(200), nullable=True, comment="资源名称")
    
    # 操作详情
    description = Column(Text, nullable=True, comment="操作描述")
    old_value = Column(Text, nullable=True, comment="旧值（JSON格式）")
    new_value = Column(Text, nullable=True, comment="新值（JSON格式）")
    
    # 请求信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    request_method = Column(String(10), nullable=True, comment="请求方法")
    request_path = Column(String(500), nullable=True, comment="请求路径")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="操作时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    
    # 索引
    __table_args__ = (
        Index('idx_operation_logs_user_id', 'user_id'),
        Index('idx_operation_logs_action', 'action'),
        Index('idx_operation_logs_resource_type', 'resource_type'),
        Index('idx_operation_logs_resource_id', 'resource_id'),
        Index('idx_operation_logs_created_at', 'created_at'),
        Index('idx_operation_logs_user_action', 'user_id', 'action'),
        Index('idx_operation_logs_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<OperationLog {self.id} - {self.action} - {self.resource_type}>"


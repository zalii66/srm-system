"""
操作日志服务
用于记录和管理用户操作日志
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogCreate
import json


class OperationLogService:
    """操作日志服务"""
    
    @staticmethod
    def create_log(
        db: Session,
        user_id: Optional[int],
        username: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        resource_name: Optional[str] = None,
        description: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None
    ) -> OperationLog:
        """创建操作日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            username: 用户名
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            description: 操作描述
            old_value: 旧值（字典）
            new_value: 新值（字典）
            ip_address: IP地址
            user_agent: 用户代理
            request_method: 请求方法
            request_path: 请求路径
        
        Returns:
            OperationLog: 操作日志对象
        """
        # 将字典转换为JSON字符串
        old_value_str = json.dumps(old_value, ensure_ascii=False) if old_value else None
        new_value_str = json.dumps(new_value, ensure_ascii=False) if new_value else None
        
        log = OperationLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            old_value=old_value_str,
            new_value=new_value_str,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path
        )
        
        db.add(log)
        # flush 以获取 log.id，commit 由调用者处理
        db.flush()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_by_id(db: Session, log_id: int) -> Optional[OperationLog]:
        """根据ID获取操作日志"""
        return db.query(OperationLog).filter(OperationLog.id == log_id).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[OperationLog], int]:
        """获取操作日志列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            user_id: 用户ID筛选
            action: 操作类型筛选
            resource_type: 资源类型筛选
            resource_id: 资源ID筛选
            start_date: 开始时间
            end_date: 结束时间
        
        Returns:
            tuple: (日志列表, 总数)
        """
        query = db.query(OperationLog)
        
        # 筛选条件
        filters = []
        if user_id is not None:
            filters.append(OperationLog.user_id == user_id)
        if action:
            filters.append(OperationLog.action == action)
        if resource_type:
            filters.append(OperationLog.resource_type == resource_type)
        if resource_id is not None:
            filters.append(OperationLog.resource_id == resource_id)
        if start_date:
            filters.append(OperationLog.created_at >= start_date)
        if end_date:
            filters.append(OperationLog.created_at <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 获取总数
        total = query.count()
        
        # 获取数据（按时间倒序）
        logs = query.order_by(OperationLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return logs, total
    
    @staticmethod
    def get_by_resource(
        db: Session,
        resource_type: str,
        resource_id: int,
        limit: int = 50
    ) -> List[OperationLog]:
        """获取指定资源的操作日志"""
        return db.query(OperationLog).filter(
            and_(
                OperationLog.resource_type == resource_type,
                OperationLog.resource_id == resource_id
            )
        ).order_by(OperationLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> List[OperationLog]:
        """获取指定用户的操作日志"""
        return db.query(OperationLog).filter(
            OperationLog.user_id == user_id
        ).order_by(OperationLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def delete_old_logs(db: Session, days: int = 90) -> int:
        """删除指定天数之前的日志
        
        Args:
            db: 数据库会话
            days: 保留天数
        
        Returns:
            int: 删除的记录数
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = db.query(OperationLog).filter(
            OperationLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        return deleted_count


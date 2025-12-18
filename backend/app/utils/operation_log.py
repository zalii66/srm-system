"""
操作日志工具函数
提供便捷的操作日志记录方法
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from app.services.operation_log_service import OperationLogService
from app.db.database import SessionLocal


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    if request.client:
        return request.client.host
    return "unknown"


def get_user_agent(request: Request) -> str:
    """获取用户代理"""
    return request.headers.get("user-agent", "unknown")


def log_operation(
    db: Session,
    request: Optional[Request],
    user_id: Optional[int],
    username: Optional[str],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_name: Optional[str] = None,
    description: Optional[str] = None,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None
):
    """记录操作日志（便捷方法）
    
    Args:
        db: 数据库会话
        request: FastAPI请求对象
        user_id: 用户ID
        username: 用户名
        action: 操作类型
        resource_type: 资源类型
        resource_id: 资源ID
        resource_name: 资源名称
        description: 操作描述
        old_value: 旧值
        new_value: 新值
    """
    ip_address = None
    user_agent = None
    request_method = None
    request_path = None
    
    if request:
        try:
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            request_method = request.method
            request_path = str(request.url.path)
        except Exception:
            # 如果获取请求信息失败，使用默认值
            pass
    
    # 记录操作日志
    # 使用独立的数据库会话，确保日志能够独立提交
    # 这样即使主业务已经提交或回滚，日志也能正常记录
    log_db = None
    try:
        # 创建独立的数据库会话
        log_db = SessionLocal()
        OperationLogService.create_log(
            db=log_db,
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path
        )
        # 提交日志操作（使用独立会话）
        log_db.commit()
    except Exception as e:
        # 日志记录失败不应该影响主业务
        # 回滚日志操作，只记录错误，不抛出异常
        if log_db:
            try:
                log_db.rollback()
            except Exception:
                pass
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            f"记录操作日志失败: {str(e)} | "
            f"action={action}, resource_type={resource_type}, resource_id={resource_id}, "
            f"user_id={user_id}, username={username}",
            exc_info=True
        )
    finally:
        # 确保关闭独立的数据库会话
        if log_db:
            try:
                log_db.close()
            except Exception:
                pass


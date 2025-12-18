from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.deps import get_db, get_current_superuser
from app.models.user import User
from app.schemas.operation_log import OperationLog, OperationLogQuery
from app.schemas.response import Response, PageResponse
from app.services.operation_log_service import OperationLogService

router = APIRouter()


@router.get("/", response_model=PageResponse[OperationLog], summary="获取操作日志列表")
def get_operation_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    action: Optional[str] = Query(None, description="操作类型"),
    resource_type: Optional[str] = Query(None, description="资源类型"),
    resource_id: Optional[int] = Query(None, description="资源ID"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    获取操作日志列表（仅管理员）
    
    支持多种筛选条件：
    - 用户ID
    - 操作类型
    - 资源类型
    - 资源ID
    - 时间范围
    """
    skip = (page - 1) * page_size
    
    logs, total = OperationLogService.get_multi(
        db=db,
        skip=skip,
        limit=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date
    )
    
    logs_data = [OperationLog.model_validate(log) for log in logs]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=logs_data
    )


@router.get("/{log_id}", response_model=OperationLog, summary="获取操作日志详情")
def get_operation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """获取操作日志详情（仅管理员）"""
    log = OperationLogService.get_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="操作日志不存在"
        )
    return OperationLog.model_validate(log)


@router.get("/resource/{resource_type}/{resource_id}", response_model=PageResponse[OperationLog], summary="获取资源操作日志")
def get_resource_logs(
    resource_type: str,
    resource_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """获取指定资源的操作日志（仅管理员）"""
    skip = (page - 1) * page_size
    
    logs, total = OperationLogService.get_multi(
        db=db,
        skip=skip,
        limit=page_size,
        resource_type=resource_type,
        resource_id=resource_id
    )
    
    logs_data = [OperationLog.model_validate(log) for log in logs]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=logs_data
    )


@router.get("/user/{user_id}", response_model=PageResponse[OperationLog], summary="获取用户操作日志")
def get_user_logs(
    user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """获取指定用户的操作日志（仅管理员）"""
    skip = (page - 1) * page_size
    
    logs, total = OperationLogService.get_multi(
        db=db,
        skip=skip,
        limit=page_size,
        user_id=user_id
    )
    
    logs_data = [OperationLog.model_validate(log) for log in logs]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=logs_data
    )


@router.delete("/cleanup", response_model=Response, summary="清理旧日志")
def cleanup_old_logs(
    days: int = Query(90, ge=1, le=365, description="保留天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """清理指定天数之前的日志（仅管理员）"""
    deleted_count = OperationLogService.delete_old_logs(db, days)
    return Response(message=f"已删除 {deleted_count} 条旧日志")


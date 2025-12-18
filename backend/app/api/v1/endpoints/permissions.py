from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_superuser
from app.schemas.permission import Permission, PermissionCreate, PermissionUpdate
from app.schemas.response import Response, PageResponse
from app.services.permission_service import PermissionService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PageResponse[Permission], summary="获取权限列表")
def get_permissions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: bool = Query(None, description="是否激活"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    获取权限列表（需要超级管理员权限）
    """
    skip = (page - 1) * page_size
    permissions, total = PermissionService.get_multi(
        db, skip=skip, limit=page_size, is_active=is_active
    )
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=permissions
    )


@router.get("/all", response_model=List[Permission], summary="获取所有权限")
def get_all_permissions(
    is_active: bool = Query(None, description="是否激活"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    获取所有权限（不分页，用于下拉选择等场景）
    """
    permissions = PermissionService.get_all(db, is_active=is_active)
    return permissions


@router.get("/{permission_id}", response_model=Permission, summary="获取权限详情")
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    根据ID获取权限详情
    """
    permission = PermissionService.get_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return permission


@router.post("/", response_model=Permission, summary="创建权限")
def create_permission(
    permission_in: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    创建新权限（需要超级管理员权限）
    """
    return PermissionService.create(db, permission_in)


@router.put("/{permission_id}", response_model=Permission, summary="更新权限")
def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    更新权限信息（需要超级管理员权限）
    """
    return PermissionService.update(db, permission_id, permission_in)


@router.delete("/{permission_id}", summary="删除权限")
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    删除权限（需要超级管理员权限）
    """
    PermissionService.delete(db, permission_id)
    return Response(message="删除成功")


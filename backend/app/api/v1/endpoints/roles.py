from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_superuser
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.response import Response, PageResponse
from app.services.role_service import RoleService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PageResponse[Role], summary="获取角色列表")
def get_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    获取角色列表（需要超级管理员权限）
    """
    skip = (page - 1) * page_size
    roles, total = RoleService.get_multi(db, skip=skip, limit=page_size)
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=roles
    )


@router.get("/{role_id}", response_model=Role, summary="获取角色详情")
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    根据ID获取角色详情
    """
    role = RoleService.get_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role


@router.post("/", response_model=Role, summary="创建角色")
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    创建新角色（需要超级管理员权限）
    """
    return RoleService.create(db, role_in)


@router.put("/{role_id}", response_model=Role, summary="更新角色")
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    更新角色信息（需要超级管理员权限）
    """
    return RoleService.update(db, role_id, role_in)


@router.delete("/{role_id}", summary="删除角色")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    删除角色（需要超级管理员权限）
    """
    RoleService.delete(db, role_id)
    return Response(message="删除成功")


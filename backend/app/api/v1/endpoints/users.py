from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, get_current_superuser
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.response import Response, PageResponse
from app.services.user_service import UserService
from app.models.user import User as UserModel

router = APIRouter()


@router.get("/", response_model=PageResponse[User], summary="获取用户列表")
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（姓名、手机号、邮箱、用户名）"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    获取用户列表（需要超级管理员权限）
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **keyword**: 搜索关键词，支持搜索姓名、手机号、邮箱、用户名
    - **is_active**: 是否激活（true/false）
    """
    skip = (page - 1) * page_size
    users, total = UserService.get_multi(
        db, 
        skip=skip, 
        limit=page_size,
        keyword=keyword,
        is_active=is_active
    )
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=users
    )


@router.get("/{user_id}", response_model=User, summary="获取用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    根据ID获取用户详情
    
    - **user_id**: 用户ID
    """
    # 普通用户只能查看自己的信息
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.post("/", response_model=User, summary="创建用户")
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    创建新用户（需要超级管理员权限）
    
    - **username**: 用户名
    - **password**: 密码
    - **email**: 邮箱（可选）
    - **full_name**: 全名（可选）
    - **phone**: 手机号（可选）
    - **role_ids**: 角色ID列表（可选）
    """
    return UserService.create(db, user_in)


@router.put("/{user_id}", response_model=User, summary="更新用户")
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    更新用户信息
    
    - **user_id**: 用户ID
    
    普通用户只能更新自己的信息（不能修改角色）
    超级管理员可以更新任何用户信息
    """
    # 普通用户只能修改自己的信息
    if not current_user.is_superuser:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        # 普通用户不能修改角色
        if user_in.role_ids is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改角色"
            )
    
    return UserService.update(db, user_id, user_in)


@router.delete("/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    删除用户（需要超级管理员权限）
    
    - **user_id**: 用户ID
    """
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    UserService.delete(db, user_id)
    return Response(message="删除成功")


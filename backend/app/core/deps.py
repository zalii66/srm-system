from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, selectinload
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.token import TokenPayload

# OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenPayload(sub=username)
    except JWTError:
        raise credentials_exception
    
    # 加载用户角色及其权限，以便前端能够正确显示菜单
    user = db.query(User).options(
        selectinload(User.roles).selectinload(Role.permissions)
    ).filter(User.username == token_data.sub).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前超级管理员"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user


def get_current_admin_or_project_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员或项目经理"""
    # 检查是否是超级管理员
    if current_user.is_superuser:
        return current_user
    
    # 检查是否是项目经理
    is_project_manager = any(role.code == "project_manager" for role in current_user.roles)
    if not is_project_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员或项目经理权限"
        )
    return current_user


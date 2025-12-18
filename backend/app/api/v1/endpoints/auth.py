from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token
from app.core.deps import get_db, get_current_user
from app.schemas.token import Token
from app.schemas.user import User, UserLogin
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=Token, summary="用户登录")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    用户登录接口（支持手机号或用户名登录）
    
    - **username**: 手机号或用户名
    - **password**: 密码
    """
    user = UserService.authenticate(
        db, 
        username=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=User, summary="获取当前用户信息")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    """
    return current_user


@router.post("/logout", summary="用户登出")
def logout():
    """
    用户登出接口（前端清除token即可）
    """
    return {"message": "登出成功"}


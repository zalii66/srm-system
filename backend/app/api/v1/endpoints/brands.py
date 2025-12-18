from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.brand import Brand, BrandCreate, BrandUpdate
from app.schemas.response import Response, PageResponse
from app.services.brand_service import BrandService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PageResponse[Brand], summary="获取品牌列表")
def get_brands(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取品牌列表
    
    - 管理员：可以查看所有品牌
    - 其他用户：可以查看启用的品牌（用于下拉选择）
    """
    # 如果不是管理员，只能查看启用的品牌
    if not current_user.is_superuser:
        is_active = True
    
    skip = (page - 1) * page_size
    brands, total = BrandService.get_multi(
        db, skip=skip, limit=page_size, is_active=is_active
    )
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=brands
    )


@router.get("/{brand_id}", response_model=Brand, summary="获取品牌详情")
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取品牌详情
    """
    brand = BrandService.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="品牌不存在"
        )
    return brand


@router.post("/", response_model=Brand, summary="创建品牌")
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新品牌（管理员）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建品牌"
        )
    return BrandService.create(db, brand_in)


@router.put("/{brand_id}", response_model=Brand, summary="更新品牌")
def update_brand(
    brand_id: int,
    brand_in: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新品牌信息（管理员）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新品牌"
        )
    return BrandService.update(db, brand_id, brand_in)


@router.delete("/{brand_id}", summary="删除品牌")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除品牌（管理员）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除品牌"
        )
    BrandService.delete(db, brand_id)
    return Response(message="删除成功")


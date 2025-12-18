from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.company import Company, CompanyCreate, CompanyUpdate
from app.schemas.response import Response, PageResponse
from app.services.company_service import CompanyService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PageResponse[Company], summary="获取公司列表")
def get_companies(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    brand_id: Optional[int] = Query(None, description="品牌ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取公司列表
    
    - 管理员：可以查看所有公司
    - 其他用户：可以查看启用的公司（用于下拉选择）
    """
    # 如果不是管理员，只能查看启用的公司
    if not current_user.is_superuser:
        is_active = True
    
    skip = (page - 1) * page_size
    companies, total = CompanyService.get_multi(
        db, skip=skip, limit=page_size, is_active=is_active, brand_id=brand_id
    )
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=companies
    )


@router.get("/{company_id}", response_model=Company, summary="获取公司详情")
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取公司详情
    """
    company = CompanyService.get_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="公司不存在"
        )
    return company


@router.post("/", response_model=Company, summary="创建公司")
def create_company(
    company_in: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新公司（管理员）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建公司"
        )
    return CompanyService.create(db, company_in)


@router.put("/{company_id}", response_model=Company, summary="更新公司")
def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新公司信息（管理员）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新公司"
        )
    return CompanyService.update(db, company_id, company_in)


@router.delete("/{company_id}", summary="删除公司")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除公司（管理员）
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除公司"
        )
    CompanyService.delete(db, company_id)
    return Response(message="删除成功")


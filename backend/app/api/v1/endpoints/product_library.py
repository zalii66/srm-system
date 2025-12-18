from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.product_library import ProductLibraryItem, ProductLibraryDetail, ProductLibraryStatistics
from app.schemas.response import Response, PageResponse
from app.services.product_library_service import ProductLibraryService
from app.services.supplier_service import SupplierService
from app.models.user import User

router = APIRouter()


def is_supplier(user: User) -> bool:
    """检查是否是供应商"""
    return any(role.code == "supplier" for role in user.roles)


@router.get("/", response_model=PageResponse[ProductLibraryItem], summary="获取产品库列表")
def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    supplier_id: Optional[int] = Query(None, description="供应商ID（管理员可筛选）"),
    project_id: Optional[int] = Query(None, description="项目ID"),
    keyword: Optional[str] = Query(None, description="产品关键词（同时搜索产品名称和规格型号）"),
    item_name: Optional[str] = Query(None, description="产品名称（模糊搜索，已废弃，使用keyword）"),
    specification: Optional[str] = Query(None, description="规格型号（模糊搜索，已废弃，使用keyword）"),
    project_name: Optional[str] = Query(None, description="项目名称（模糊搜索）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取产品库列表
    
    基于报价明细汇总产品信息
    - 供应商：只能看到自己的报价产品
    - 管理员：可以看到所有供应商的产品
    """
    skip = (page - 1) * page_size
    
    # 供应商只能看自己的产品
    if is_supplier(current_user) and not current_user.is_superuser:
        supplier = SupplierService.get_by_user_id(db, current_user.id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商信息不存在"
            )
        supplier_id = supplier.id
    
    # 如果提供了 keyword，则同时搜索产品名称和规格型号
    # 为了向后兼容，如果提供了 item_name 或 specification，也支持
    if keyword:
        item_name = keyword
        specification = keyword
    elif item_name and specification:
        # 如果同时提供了 item_name 和 specification，则分别搜索
        pass
    elif item_name:
        specification = None
    elif specification:
        item_name = None
    
    products, total = ProductLibraryService.get_products(
        db=db,
        supplier_id=supplier_id,
        project_id=project_id,
        item_name=item_name,
        specification=specification,
        project_name=project_name,
        skip=skip,
        limit=page_size
    )
    
    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get("/{product_id}", response_model=Response[ProductLibraryDetail], summary="获取产品详情")
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取产品详情
    """
    product = ProductLibraryService.get_product_detail(db, product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在"
        )
    
    # 供应商只能看自己的产品
    if is_supplier(current_user) and not current_user.is_superuser:
        supplier = SupplierService.get_by_user_id(db, current_user.id)
        if not supplier or product.supplier_id != supplier.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此产品"
            )
    
    return {"data": product}


@router.get("/statistics/summary", response_model=Response[ProductLibraryStatistics], summary="获取产品库统计")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取产品库统计信息
    """
    supplier_id = None
    
    # 供应商只能看自己的统计
    if is_supplier(current_user) and not current_user.is_superuser:
        supplier = SupplierService.get_by_user_id(db, current_user.id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商信息不存在"
            )
        supplier_id = supplier.id
    
    statistics = ProductLibraryService.get_product_statistics(db, supplier_id)
    
    return {"data": statistics}


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.quotation import Quotation, QuotationCreate, QuotationUpdate, QuotationEvaluate
from app.schemas.response import Response, PageResponse
from app.services.quotation_service import QuotationService
from app.services.supplier_service import SupplierService
from app.services.project_service import ProjectService
from app.models.user import User
from app.models.supplier import SupplierStatus
from app.utils.operation_log import log_operation

router = APIRouter()


def is_supplier(user: User) -> bool:
    """检查是否是供应商"""
    return any(role.code == "supplier" for role in user.roles)


def is_project_manager(user: User) -> bool:
    """检查是否是项目经理"""
    return any(role.code == "project_manager" for role in user.roles) or user.is_superuser


@router.post("/", response_model=Quotation, summary="创建报价")
def create_quotation(
    quotation_in: QuotationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建报价（供应商）
    
    供应商必须审核通过才能报价
    """
    if not is_supplier(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商可以报价"
        )
    
    # 获取供应商信息
    supplier = SupplierService.get_by_user_id(db, current_user.id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商信息不存在"
        )
    
    # 检查供应商审核状态
    if supplier.status != SupplierStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="供应商资质未审核通过，无法报价"
        )
    
    quotation = QuotationService.create(db, quotation_in, supplier.id)
    
    # 获取项目信息
    project = ProjectService.get_by_id(db, quotation.project_id)
    project_name = project.project_name if project else None
    
    # 记录操作日志
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="quotation",
        resource_id=quotation.id,
        resource_name=f"报价#{quotation.id}",
        description=f"创建报价：项目 {project_name}"
    )
    
    return Quotation.model_validate(quotation)


@router.get("/", response_model=PageResponse[Quotation], summary="获取报价列表")
def get_quotations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    project_id: Optional[int] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取报价列表
    
    - 供应商：看到自己的报价
    - 项目经理：看到自己项目的所有报价
    - 管理员：看到所有报价
    """
    skip = (page - 1) * page_size
    
    if is_supplier(current_user):
        # 供应商看自己的报价
        supplier = SupplierService.get_by_user_id(db, current_user.id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商信息不存在"
            )
        quotations, total = QuotationService.get_multi_by_supplier(
            db, supplier.id, skip=skip, limit=page_size
        )
    elif project_id:
        # 根据项目ID获取报价
        project = ProjectService.get_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 项目经理只能看自己项目的报价
        if is_project_manager(current_user) and not current_user.is_superuser:
            if project.creator_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权查看此项目的报价"
                )
        
        quotations, total = QuotationService.get_multi_by_project(
            db, project_id, skip=skip, limit=page_size
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请指定项目ID"
        )
    
    # 确保序列化时包含供应商信息
    quotations_data = [Quotation.model_validate(q) for q in quotations]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=quotations_data
    )


@router.get("/my", response_model=PageResponse[Quotation], summary="获取我的报价")
def get_my_quotations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前供应商的所有报价
    """
    if not is_supplier(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商可以查看自己的报价"
        )
    
    supplier = SupplierService.get_by_user_id(db, current_user.id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商信息不存在"
        )
    
    skip = (page - 1) * page_size
    quotations, total = QuotationService.get_multi_by_supplier(
        db, supplier.id, skip=skip, limit=page_size
    )
    
    # 确保序列化时包含供应商信息
    quotations_data = [Quotation.model_validate(q) for q in quotations]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=quotations_data
    )


@router.get("/{quotation_id}", response_model=Quotation, summary="获取报价详情")
def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取报价详情
    """
    quotation = QuotationService.get_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报价不存在"
        )
    
    # 权限检查
    if is_supplier(current_user):
        supplier = SupplierService.get_by_user_id(db, current_user.id)
        if not supplier or quotation.supplier_id != supplier.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此报价"
            )
    elif is_project_manager(current_user) and not current_user.is_superuser:
        project = ProjectService.get_by_id(db, quotation.project_id)
        if not project or project.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此报价"
            )
    
    # 确保序列化时包含供应商和明细信息
    return Quotation.model_validate(quotation)


@router.put("/{quotation_id}", response_model=Quotation, summary="更新报价")
def update_quotation(
    quotation_id: int,
    quotation_in: QuotationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新报价（供应商，仅草稿状态可修改）
    """
    if not is_supplier(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商可以更新报价"
        )
    
    supplier = SupplierService.get_by_user_id(db, current_user.id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商信息不存在"
        )
    
    # 检查供应商审核状态
    if supplier.status != SupplierStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="供应商资质未审核通过，无法更新报价"
        )
    
    quotation = QuotationService.update(db, quotation_id, quotation_in, supplier.id)
    
    # 获取项目信息
    project = ProjectService.get_by_id(db, quotation.project_id)
    project_name = project.project_name if project else None
    
    # 记录操作日志
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="quotation",
        resource_id=quotation.id,
        resource_name=f"报价#{quotation.id}",
        description=f"更新报价：项目 {project_name}"
    )
    
    return Quotation.model_validate(quotation)


@router.post("/{quotation_id}/submit", response_model=Quotation, summary="提交报价")
def submit_quotation(
    quotation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交报价（供应商）
    
    供应商必须审核通过才能提交报价
    """
    if not is_supplier(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有供应商可以提交报价"
        )
    
    supplier = SupplierService.get_by_user_id(db, current_user.id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商信息不存在"
        )
    
    # 检查供应商审核状态
    if supplier.status != SupplierStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="供应商资质未审核通过，无法提交报价。请先完善公司资料并等待审核通过。"
        )
    
    quotation = QuotationService.submit(db, quotation_id, supplier.id)
    
    # 获取项目信息
    project = ProjectService.get_by_id(db, quotation.project_id)
    project_name = project.project_name if project else None
    
    # 记录操作日志
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="submit",
        resource_type="quotation",
        resource_id=quotation.id,
        resource_name=f"报价#{quotation.id}",
        description=f"提交报价：项目 {project_name}"
    )
    
    return Quotation.model_validate(quotation)


@router.post("/{quotation_id}/evaluate", response_model=Quotation, summary="评审报价")
def evaluate_quotation(
    quotation_id: int,
    evaluate_in: QuotationEvaluate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    评审报价（项目经理或管理员）
    
    - **status**: selected（中标）/ rejected（未中标）
    - **evaluation_comment**: 评审意见
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理可以评审报价"
        )
    
    # 验证权限
    quotation = QuotationService.get_by_id(db, quotation_id)
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报价不存在"
        )
    
    if not current_user.is_superuser:
        project = ProjectService.get_by_id(db, quotation.project_id)
        if not project or project.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权评审此报价"
            )
    
    # 获取旧状态
    old_status = quotation.status
    
    quotation = QuotationService.evaluate(db, quotation_id, evaluate_in, current_user.id)
    
    # 获取项目信息
    project = ProjectService.get_by_id(db, quotation.project_id)
    project_name = project.project_name if project else None
    
    # 记录操作日志
    status_text = "中标" if evaluate_in.status == "selected" else "未中标"
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="evaluate",
        resource_type="quotation",
        resource_id=quotation.id,
        resource_name=f"报价#{quotation.id}",
        description=f"评审报价：{status_text}，项目 {project_name}",
        old_value={"status": old_status},
        new_value={"status": evaluate_in.status, "evaluation_comment": evaluate_in.evaluation_comment}
    )
    
    return Quotation.model_validate(quotation)


@router.post("/{quotation_id}/cancel", response_model=Quotation, summary="取消报价")
def cancel_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消报价
    
    - 供应商：只能取消自己的报价，且只能取消草稿或已提交状态的报价
    - 管理员：可以取消任何报价
    """
    is_admin = current_user.is_superuser
    
    # 如果是供应商，检查权限
    if not is_admin:
        if not is_supplier(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有供应商或管理员可以取消报价"
            )
    
    quotation = QuotationService.cancel(db, quotation_id, current_user.id, is_admin)
    return Quotation.model_validate(quotation)


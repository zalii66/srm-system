from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from fastapi.responses import FileResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from pathlib import Path
import uuid
from datetime import datetime
from app.core.deps import get_db, get_current_user, get_current_superuser
from app.core.config import settings
from app.schemas.supplier import (
    Supplier, SupplierRegister, SupplierUpdate, SupplierAudit, SupplierQualificationUpload
)
from app.schemas.response import Response, PageResponse
from app.services.supplier_service import SupplierService
from app.models.user import User
from app.models.quotation import Quotation, QuotationStatus
from app.models.project import Project
from app.models.company import Company
from app.models.supplier import Supplier as SupplierModel
from app.models.supplier_project_history import SupplierProjectHistory
from app.utils.operation_log import log_operation
from pydantic import BaseModel

router = APIRouter()


@router.post("/register", response_model=Supplier, summary="供应商注册")
def register_supplier(
    supplier_in: SupplierRegister,
    db: Session = Depends(get_db)
):
    """
    供应商自主注册
    
    - **username**: 用户名
    - **password**: 密码
    - **company_name**: 公司名称
    - **contact_person**: 联系人
    - **contact_phone**: 联系电话
    
    此接口无需认证，任何人都可以注册供应商账号
    """
    supplier = SupplierService.register(db, supplier_in)
    return Supplier.model_validate(supplier)


@router.get("/", response_model=PageResponse[Supplier], summary="获取供应商列表")
def get_suppliers(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="审核状态（-1待审核/0审核失败/1审核通过）"),
    keyword: Optional[str] = Query(None, description="搜索关键词（手机号、公司名称、联系人）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取供应商列表
    
    - 超级管理员可以查看所有供应商
    - 项目经理只能查看参与过自己发布项目的供应商
    
    - **keyword**: 模糊搜索关键词，支持搜索手机号、公司名称、联系人
    """
    # 检查权限：只有超级管理员和项目经理可以访问
    is_project_manager = any(role.code == "project_manager" for role in current_user.roles)
    if not current_user.is_superuser and not is_project_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员或项目经理权限"
        )
    
    skip = (page - 1) * page_size
    
    # 根据用户角色获取供应商列表
    if current_user.is_superuser:
        # 超级管理员查看所有供应商
        suppliers, total = SupplierService.get_multi(
            db, skip=skip, limit=page_size, status=status, keyword=keyword
        )
    else:
        # 项目经理只能查看参与过自己项目的供应商
        
        # 先查询当前项目经理创建的所有项目
        user_projects = db.query(Project.id).filter(Project.creator_id == current_user.id).subquery()
        
        # 查询条件：供应商参与了当前项目经理创建的项目（从报价表获取）
        query = db.query(SupplierModel).distinct()
        
        # 关联报价表和项目子查询
        query = query.join(
            Quotation, Quotation.supplier_id == SupplierModel.id
        ).join(
            user_projects, user_projects.c.id == Quotation.project_id
        )
        
        # 应用状态过滤
        if status is not None:
            query = query.filter(SupplierModel.status == status)
        
        # 应用关键词过滤
        if keyword and keyword.strip():
            keyword_pattern = f"%{keyword.strip()}%"
            query = query.filter(
                (SupplierModel.company_name.like(keyword_pattern)) | 
                (SupplierModel.contact_person.like(keyword_pattern)) |
                (SupplierModel.contact_phone.like(keyword_pattern))
            )
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        suppliers = query.options(
            joinedload(SupplierModel.user)
        ).order_by(SupplierModel.created_at.desc()).offset(skip).limit(page_size).all()
    
    # 确保正确序列化供应商对象
    supplier_items = [Supplier.model_validate(supplier) for supplier in suppliers]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=supplier_items
    )


@router.get("/me", response_model=Supplier, summary="获取当前供应商信息")
def get_current_supplier(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录供应商的信息
    
    只有供应商角色可以访问此接口
    """
    # 检查是否是供应商角色
    is_supplier = any(role.code == "supplier" for role in current_user.roles)
    if not is_supplier and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户不是供应商"
        )
    
    # 如果用户有供应商角色但没有supplier记录，自动创建一个初始记录
    supplier = SupplierService.get_by_user_id(db, current_user.id, auto_create=True)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法创建供应商记录，请联系管理员"
        )
    return Supplier.model_validate(supplier)


@router.put("/me", response_model=Supplier, summary="更新供应商信息")
def update_current_supplier(
    supplier_in: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前供应商信息
    
    只有供应商角色可以更新自己的信息
    """
    # 检查是否是供应商角色
    is_supplier = any(role.code == "supplier" for role in current_user.roles)
    if not is_supplier and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户不是供应商"
        )
    
    # 如果用户有供应商角色但没有supplier记录，自动创建一个初始记录
    supplier = SupplierService.get_by_user_id(db, current_user.id, auto_create=True)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法创建供应商记录，请联系管理员"
        )
    
    # 更新供应商信息（无论当前状态如何，都可以编辑）
    # 如果当前状态是已通过，编辑后状态会变为待审核（在service层处理）
    updated_supplier = SupplierService.update(db, supplier.id, supplier_in)
    return Supplier.model_validate(updated_supplier)


@router.post("/me/qualification", response_model=Supplier, summary="上传证件资质")
def upload_qualification(
    files: List[UploadFile] = File(..., description="证件资质文件（支持图片和文档）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传供应商证件资质文件（支持多个文件）
    
    支持格式：jpg, jpeg, png, pdf（仅支持图片和PDF文档，用于证明资质）
    最大文件大小：10MB/文件
    """
    # 检查是否是供应商角色
    is_supplier = any(role.code == "supplier" for role in current_user.roles)
    if not is_supplier and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户不是供应商"
        )
    
    # 如果用户有供应商角色但没有supplier记录，自动创建一个初始记录
    supplier = SupplierService.get_by_user_id(db, current_user.id, auto_create=True)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法创建供应商记录，请联系管理员"
        )
    
    # 创建按年月分类的上传目录
    now = datetime.now()
    year_month = now.strftime("%Y%m")  # 格式：202501
    upload_dir = Path(settings.UPLOAD_DIR) / "qualification" / year_month
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    saved_files = []
    
    try:
        # 处理每个文件（证件资质使用专门的配置）
        allowed_extensions = settings.ALLOWED_QUALIFICATION_FILE_EXTENSIONS
        for file in files:
            # 检查文件扩展名
            file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件 {file.filename} 格式不支持，仅支持：{', '.join(allowed_extensions)}"
                )
            
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            file_name = f"{file_id}.{file_ext}"
            file_path = upload_dir / file_name
            
            # 读取并保存文件
            content = file.file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件 {file.filename} 大小超过限制（最大{settings.MAX_FILE_SIZE // 1024 // 1024}MB）"
                )
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # 保存文件路径（新格式：/uploads/qualification/YYYYMM/filename.ext）
            file_url = f"/uploads/qualification/{year_month}/{file_name}"
            # 存储格式：{"url": 存储路径, "name": 原始文件名}
            uploaded_files.append({
                "url": file_url,
                "name": file.filename  # 保存原始文件名
            })
            saved_files.append(file_path)
        
        # 读取现有文件列表
        from app.utils.json_utils import parse_qualification_docs, serialize_qualification_docs
        existing_files = parse_qualification_docs(supplier.qualification_docs)
        # 兼容旧格式（纯字符串数组）
        if existing_files and isinstance(existing_files[0], str):
            existing_files = [{"url": url, "name": url.split("/")[-1]} for url in existing_files]
        
        # 合并新旧文件列表
        all_files = existing_files + uploaded_files
        supplier.qualification_docs = serialize_qualification_docs(all_files)
        
        # 如果当前状态是已通过，上传证件资质后需要重新审核
        from app.models.supplier import SupplierStatus
        if supplier.status == SupplierStatus.APPROVED:
            supplier.status = SupplierStatus.PENDING
            supplier.audit_user_id = None
            supplier.audit_time = None
            supplier.audit_comment = None
        
        try:
            db.commit()
            db.refresh(supplier)
            return Supplier.model_validate(supplier)
        except Exception as db_error:
            db.rollback()
            # 如果数据库提交失败，删除已创建的文件
            for file_path in saved_files:
                if file_path.exists():
                    file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败：{str(db_error)}"
            )
    except HTTPException:
        # 如果是HTTPException，直接抛出
        # 删除已保存的文件
        for file_path in saved_files:
            if file_path.exists():
                file_path.unlink()
        raise
    except Exception as e:
        # 如果保存失败，删除已创建的文件
        for file_path in saved_files:
            if file_path.exists():
                file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败：{str(e)}"
        )


@router.post("/me/business-license", response_model=Supplier, summary="上传营业执照（兼容旧接口）")
def upload_business_license(
    file: UploadFile = File(..., description="营业执照图片"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传供应商营业执照（图片）- 兼容旧接口
    
    支持格式：jpg, jpeg, png, gif, bmp, webp
    最大文件大小：10MB
    """
    # 兼容旧接口，将单个文件转为列表调用新接口
    return upload_qualification([file], db, current_user)


@router.delete("/me/qualification/{file_index}", response_model=Supplier, summary="删除证件资质文件")
def delete_qualification_file(
    file_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除指定的证件资质文件
    """
    # 检查是否是供应商角色
    is_supplier = any(role.code == "supplier" for role in current_user.roles)
    if not is_supplier and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户不是供应商"
        )
    
    supplier = SupplierService.get_by_user_id(db, current_user.id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    import json
    if not supplier.qualification_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有可删除的文件"
        )
    
    from app.utils.json_utils import parse_qualification_docs, serialize_qualification_docs
    files = parse_qualification_docs(supplier.qualification_docs)
    # 兼容旧格式（纯字符串数组）
    if files and isinstance(files[0], str):
        files = [{"url": url, "name": url.split("/")[-1]} for url in files]
    
    if file_index < 0 or file_index >= len(files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件索引无效"
        )
    
    # 获取要删除的文件信息
    file_info = files[file_index]
    file_url = file_info if isinstance(file_info, str) else file_info.get("url", "")
    
    # 删除物理文件
    try:
        if file_url and file_url.startswith('/uploads/'):
            # 构建完整文件路径
            file_path = Path(settings.UPLOAD_DIR) / file_url.lstrip('/uploads/')
            if file_path.exists():
                file_path.unlink()
    except Exception as e:
        # 记录错误但不影响删除流程
        import logging
        logging.error(f"删除物理文件失败: {file_path}, 错误: {str(e)}")
    
    # 从列表中移除
    files.pop(file_index)
    supplier.qualification_docs = serialize_qualification_docs(files)
    
    # 如果当前状态是已通过，删除证件资质后需要重新审核
    from app.models.supplier import SupplierStatus
    if supplier.status == SupplierStatus.APPROVED:
        supplier.status = SupplierStatus.PENDING
        supplier.audit_user_id = None
        supplier.audit_time = None
        supplier.audit_comment = None
    
    db.commit()
    db.refresh(supplier)
    return Supplier.model_validate(supplier)


@router.post("/{supplier_id}/audit", response_model=Supplier, summary="审核供应商")
def audit_supplier(
    supplier_id: int,
    audit_in: SupplierAudit,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    审核供应商资质（管理员）
    
    - **status**: 审核状态（approved/rejected）
    - **audit_comment**: 审核意见
    
    只有超级管理员可以审核供应商
    """
    # 获取旧状态
    old_supplier = SupplierService.get_by_id(db, supplier_id)
    old_status = old_supplier.status if old_supplier else None
    
    audited_supplier = SupplierService.audit(db, supplier_id, audit_in, current_user.id)
    
    # 记录操作日志
    status_text = "通过" if audit_in.status == "approved" else "拒绝"
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="audit",
        resource_type="supplier",
        resource_id=supplier_id,
        resource_name=audited_supplier.company_name,
        description=f"审核供应商：{status_text} - {audited_supplier.company_name}",
        old_value={"status": old_status},
        new_value={"status": audit_in.status, "audit_comment": audit_in.audit_comment}
    )
    
    return Supplier.model_validate(audited_supplier)


@router.get("/{supplier_id}", response_model=Supplier, summary="获取供应商详情")
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取供应商详情
    
    - 超级管理员：可以查看所有供应商
    - 供应商：只能查看自己的信息
    - 项目经理：可以查看参与其项目的供应商信息
    """
    supplier = SupplierService.get_by_id(db, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    # 超级管理员可以查看所有供应商
    if current_user.is_superuser:
        return Supplier.model_validate(supplier)
    
    # 供应商只能查看自己的信息
    if supplier.user_id == current_user.id:
        return Supplier.model_validate(supplier)
    
    # 项目经理可以查看参与其项目的供应商信息
    from sqlalchemy import exists
    has_access = db.query(exists().where(
        and_(
            Quotation.supplier_id == supplier_id,
            Quotation.project_id == Project.id,
            Project.creator_id == current_user.id
        )
    )).scalar()
    
    if has_access:
        return Supplier.model_validate(supplier)
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="权限不足，只能查看自己或参与您项目的供应商信息"
    )


class SupplierProjectItem(BaseModel):
    """供应商项目项"""
    id: int
    project_id: int
    project_no: Optional[str] = None
    project_name: Optional[str] = None
    company_name: Optional[str] = None
    participated_at: Optional[datetime] = None
    is_winner: int = 0
    contract_amount: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


@router.get("/{supplier_id}/projects", response_model=PageResponse[SupplierProjectItem], summary="获取供应商参与的项目列表")
def get_supplier_projects(
    supplier_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取供应商参与的项目列表
    
    从报价表中获取该供应商参与的所有项目
    
    - 超级管理员：可以查看所有供应商的项目列表
    - 供应商：只能查看自己的项目列表
    - 项目经理：可以查看参与其项目的供应商项目列表
    """
    # 检查供应商是否存在
    supplier = SupplierService.get_by_id(db, supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="供应商不存在"
        )
    
    # 检查权限：超级管理员可以查看所有，供应商只能查看自己的，项目经理可以查看参与其项目的供应商项目
    if current_user.is_superuser:
        pass  # 超级管理员可以查看所有
    elif supplier.user_id == current_user.id:
        pass  # 供应商可以查看自己的
    else:
        # 检查是否是项目经理，并且该供应商参与了其项目
        from sqlalchemy import exists
        has_access = db.query(exists().where(
            and_(
                Quotation.supplier_id == supplier_id,
                Quotation.project_id == Project.id,
                Project.creator_id == current_user.id
            )
        )).scalar()
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    skip = (page - 1) * page_size
    
    # 从报价表中获取该供应商参与的项目（去重）
    # 获取所有不重复的项目ID
    all_project_ids = db.query(Quotation.project_id).filter(
        Quotation.supplier_id == supplier_id
    ).distinct().all()
    
    unique_project_ids = [pid[0] for pid in all_project_ids]
    total = len(unique_project_ids)
    
    if total == 0:
        return PageResponse(
            total=0,
            page=page,
            page_size=page_size,
            items=[]
        )
    
    # 获取当前页的项目ID
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_project_ids = unique_project_ids[start_idx:end_idx]
    
    # 获取这些项目的最新报价信息
    items = []
    for project_id in page_project_ids:
        latest_quotation = db.query(Quotation).filter(
            Quotation.supplier_id == supplier_id,
            Quotation.project_id == project_id
        ).options(
            joinedload(Quotation.project).joinedload(Project.company)
        ).order_by(Quotation.created_at.desc()).first()
        
        if latest_quotation and latest_quotation.project:
            item_data = {
                "id": latest_quotation.id,  # 使用报价ID作为临时ID
                "project_id": project_id,
                "project_no": latest_quotation.project.project_no,
                "project_name": latest_quotation.project.project_name,
                "company_name": latest_quotation.project.company.company_name if latest_quotation.project.company else None,
                "participated_at": latest_quotation.submitted_at or latest_quotation.created_at,
                "is_winner": 1 if latest_quotation.status == QuotationStatus.SELECTED else 0,
                "contract_amount": float(latest_quotation.total_amount) if latest_quotation.total_amount else None,
                "created_at": latest_quotation.created_at
            }
            items.append(SupplierProjectItem(**item_data))
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.delete("/{supplier_id}", summary="删除供应商")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    删除供应商（需要超级管理员权限）
    
    - **supplier_id**: 供应商ID
    
    注意：如果供应商有报价记录，将无法删除
    """
    SupplierService.delete(db, supplier_id)
    return Response(message="删除成功")


# 注意：营业执照文件获取路由已移至 main.py，以便使用 /uploads 路径而不是 /api/v1/suppliers/uploads


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.project import Project, ProjectListItem, ProjectCreate, ProjectUpdate, ProjectItem, ProjectItemCreate, ProjectItemUpdate
from app.schemas.response import Response, PageResponse
from app.services.project_service import ProjectService
from app.services.supplier_service import SupplierService
from app.models.user import User
from app.models.project import ProjectStatus
from app.utils.operation_log import log_operation

router = APIRouter()


def is_project_manager(user: User) -> bool:
    """检查是否是项目经理"""
    return any(role.code == "project_manager" for role in user.roles) or user.is_superuser


def is_supplier(user: User) -> bool:
    """检查是否是供应商"""
    return any(role.code == "supplier" for role in user.roles)


@router.post("/", response_model=Project, summary="创建项目")
def create_project(
    project_in: ProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建招标项目（项目经理）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理可以创建项目"
        )
    
    project = ProjectService.create(db, project_in, current_user.id)
    
    # 记录操作日志（在项目创建之后，因为需要 project.id）
    # 使用独立会话，不影响主业务
    log_operation(
        db=db,  # 传递 db 参数以保持接口一致性，但内部会使用独立会话
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="create",
        resource_type="project",
        resource_id=project.id,
        resource_name=project.project_name,
        description=f"创建项目：{project.project_name}"
    )
    
    return project


@router.get("/", response_model=PageResponse[ProjectListItem], summary="获取项目列表")
def get_projects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, ge=0, le=5, description="项目状态（0已停止/1进行中/3竞标中/4已完成/5已取消）"),
    category_id: Optional[int] = Query(None, description="项目类别ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目列表
    
    - 项目经理：看到自己创建的项目
    - 供应商：只能看到已发布的项目（不需要审核通过也能查看，但只有审核通过才能报价）
    - 管理员：看到所有项目
    """
    skip = (page - 1) * page_size
    
    if is_supplier(current_user):
        # 供应商可以查看已发布的项目（不需要审核通过也能查看，但只有审核通过才能报价）
        # 只能看已发布的项目
        projects, total = ProjectService.get_published_projects(db, skip=skip, limit=page_size, category_id=category_id)
    elif is_project_manager(current_user) and not current_user.is_superuser:
        # 项目经理看自己的项目
        projects, total = ProjectService.get_multi(
            db, skip=skip, limit=page_size, creator_id=current_user.id, status=status, category_id=category_id
        )
    else:
        # 管理员看所有项目
        projects, total = ProjectService.get_multi(db, skip=skip, limit=page_size, status=status, category_id=category_id)
    
    # 确保正确序列化项目对象（列表接口使用 ProjectListItem，不包含items明细）
    project_items = [ProjectListItem.model_validate(project) for project in projects]
    
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=project_items
    )


@router.get("/{project_id}", response_model=Project, summary="获取项目详情")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目详情
    """
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 供应商只能看进行中(1)和竞标中(3)的项目（不需要审核通过也能查看，但只有审核通过才能报价）
    if is_supplier(current_user):
        if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="项目未发布或已结束"
            )
    
    # 项目经理只能看自己的项目
    elif is_project_manager(current_user) and not current_user.is_superuser:
        if project.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此项目"
            )
    
    return project


@router.get("/{project_id}/items", response_model=PageResponse[ProjectItem], summary="获取项目需求项列表")
def get_project_items(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目需求项列表
    
    - 管理员/项目经理：可以查看所有项目的需求项
    - 供应商：只能查看已发布项目的需求项（不需要审核通过也能查看，但只有审核通过才能报价）
    """
    from app.models.project import ProjectItem as ProjectItemModel
    
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 供应商只能看进行中(1)和竞标中(3)的项目（不需要审核通过也能查看需求项，但只有审核通过才能报价）
    if is_supplier(current_user):
        if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="项目未发布或已结束"
            )
    
    # 项目经理只能看自己项目的需求项
    elif is_project_manager(current_user) and not current_user.is_superuser:
        if project.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此项目的需求项"
            )
    
    # 获取所有需求项
    items = db.query(ProjectItemModel).filter(ProjectItemModel.project_id == project_id).order_by(ProjectItemModel.id).all()
    
    items_data = [ProjectItem.model_validate(item) for item in items]
    
    return PageResponse(
        total=len(items_data),
        page=1,
        page_size=len(items_data),
        items=items_data
    )


@router.put("/{project_id}", response_model=Project, summary="更新项目")
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新项目信息（项目经理或管理员）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以更新项目"
        )
    
    # 获取旧项目信息
    old_project = ProjectService.get_by_id(db, project_id)
    old_value = {
        "project_name": old_project.project_name if old_project else None,
        "status": old_project.status if old_project else None
    } if old_project else None
    
    project = ProjectService.update(db, project_id, project_in, current_user.id, current_user.is_superuser)
    
    # 记录操作日志
    new_value = {
        "project_name": project.project_name,
        "status": project.status
    }
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="project",
        resource_id=project.id,
        resource_name=project.project_name,
        description=f"更新项目：{project.project_name}",
        old_value=old_value,
        new_value=new_value
    )
    
    return project


@router.delete("/{project_id}", summary="删除项目")
def delete_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除项目（项目经理或管理员）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以删除项目"
        )
    
    # 获取项目信息
    project = ProjectService.get_by_id(db, project_id)
    project_name = project.project_name if project else None
    
    ProjectService.delete(db, project_id, current_user.id, current_user.is_superuser)
    
    # 记录操作日志
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="delete",
        resource_type="project",
        resource_id=project_id,
        resource_name=project_name,
        description=f"删除项目：{project_name}"
    )
    
    return Response(message="删除成功")


@router.post("/{project_id}/publish", response_model=Project, summary="发布项目")
def publish_project(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    发布项目（项目经理或管理员）
    
    将项目从"已停止"状态转为"进行中"状态，使项目对供应商可见
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以发布项目"
        )
    
    project = ProjectService.publish(db, project_id, current_user.id, current_user.is_superuser)
    
    # 记录操作日志
    log_operation(
        db=db,
        request=request,
        user_id=current_user.id,
        username=current_user.username,
        action="update",
        resource_type="project",
        resource_id=project.id,
        resource_name=project.project_name,
        description=f"发布项目：{project.project_name}"
    )
    
    return project


@router.post("/{project_id}/stop", response_model=Project, summary="停止项目")
def stop_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    停止项目（项目经理或管理员）
    
    将项目从"进行中"或"竞标中"状态转为"已停止"状态，使项目对供应商不可见
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以停止项目"
        )
    
    return ProjectService.stop(db, project_id, current_user.id, current_user.is_superuser)


@router.post("/{project_id}/cancel", response_model=Project, summary="取消项目")
def cancel_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消项目（项目经理或管理员）
    
    将项目状态转为"已取消"，项目将不能再进行任何操作
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以取消项目"
        )
    
    return ProjectService.cancel(db, project_id, current_user.id, current_user.is_superuser)


@router.post("/{project_id}/items", response_model=ProjectItem, summary="创建项目需求项")
def create_project_item(
    project_id: int,
    item_in: ProjectItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建项目需求项（管理员/项目经理）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理可以创建需求项"
        )
    
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 项目经理只能为自己的项目添加需求项
    if not current_user.is_superuser and project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此项目添加需求项"
        )
    
    from app.models.project import ProjectItem as ProjectItemModel
    
    # 自动生成需求编号：项目编号-序号（如：PRJ202511040007-01）
    # 获取该项目下已有的需求项数量
    existing_items_count = db.query(ProjectItemModel).filter(
        ProjectItemModel.project_id == project_id
    ).count()
    
    # 生成需求编号：项目编号-序号（从01开始）
    item_no = f"{project.project_no}-{str(existing_items_count + 1).zfill(2)}"
    
    item = ProjectItemModel(
        project_id=project_id,
        item_no=item_no,  # 自动生成，不使用item_in.item_no
        item_name=item_in.item_name,
        specification=item_in.specification,
        unit=item_in.unit,
        quantity=item_in.quantity,
        estimated_price=item_in.estimated_price,
        description=item_in.description
    )
    
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return ProjectItem.model_validate(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建需求项失败: {str(e)}"
        )


@router.put("/{project_id}/items/{item_id}", response_model=ProjectItem, summary="更新项目需求项")
def update_project_item(
    project_id: int,
    item_id: int,
    item_in: ProjectItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新项目需求项（管理员/项目经理）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理可以更新需求项"
        )
    
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 项目经理只能更新自己项目的需求项
    if not current_user.is_superuser and project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此项目的需求项"
        )
    
    from app.models.project import ProjectItem as ProjectItemModel
    
    item = db.query(ProjectItemModel).filter(
        ProjectItemModel.id == item_id,
        ProjectItemModel.project_id == project_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求项不存在"
        )
    
    update_data = item_in.model_dump(exclude_unset=True)
    # 不允许更新item_no（需求编号由系统自动生成）
    if 'item_no' in update_data:
        del update_data['item_no']
    
    try:
        for field, value in update_data.items():
            setattr(item, field, value)
        
        db.commit()
        db.refresh(item)
        return ProjectItem.model_validate(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新需求项失败: {str(e)}"
        )


@router.delete("/{project_id}/items/{item_id}", summary="删除项目需求项")
def delete_project_item(
    project_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除项目需求项（管理员/项目经理）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理可以删除需求项"
        )
    
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 项目经理只能删除自己项目的需求项
    if not current_user.is_superuser and project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此项目的需求项"
        )
    
    from app.models.project import ProjectItem as ProjectItemModel
    
    item = db.query(ProjectItemModel).filter(
        ProjectItemModel.id == item_id,
        ProjectItemModel.project_id == project_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求项不存在"
        )
    
    try:
        db.delete(item)
        db.commit()
        return Response(message="删除成功")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除需求项失败: {str(e)}"
        )


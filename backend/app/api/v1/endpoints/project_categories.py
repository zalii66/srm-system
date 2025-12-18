from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.project_category import ProjectCategory, ProjectCategoryCreate, ProjectCategoryUpdate
from app.schemas.response import Response, PageResponse
from app.services.project_category_service import ProjectCategoryService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=PageResponse[ProjectCategory], summary="获取项目类别列表")
def get_categories(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目类别列表（所有角色可查看）"""
    skip = (page - 1) * page_size
    categories, total = ProjectCategoryService.get_multi(
        db, skip=skip, limit=page_size, is_active=is_active
    )
    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=categories
    )


@router.get("/{category_id}", response_model=ProjectCategory, summary="获取项目类别详情")
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目类别详情（所有角色可查看）"""
    category = ProjectCategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目类别不存在"
        )
    return category


@router.post("/", response_model=ProjectCategory, summary="创建项目类别")
def create_category(
    category_in: ProjectCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建项目类别（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建项目类别"
        )
    return ProjectCategoryService.create(db, category_in)


@router.put("/{category_id}", response_model=ProjectCategory, summary="更新项目类别")
def update_category(
    category_id: int,
    category_in: ProjectCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目类别（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新项目类别"
        )
    return ProjectCategoryService.update(db, category_id, category_in)


@router.delete("/{category_id}", response_model=Response, summary="删除项目类别")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目类别（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除项目类别"
        )
    ProjectCategoryService.delete(db, category_id)
    return Response(message="删除成功")

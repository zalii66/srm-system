from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.schemas.milestone import (
    Milestone, MilestoneCreate, MilestoneUpdate,
    MilestoneComplete, MilestoneReorder, ProjectProgress
)
from app.schemas.response import Response
from app.services.milestone_service import MilestoneService
from app.services.project_service import ProjectService
from app.models.user import User
from datetime import datetime

router = APIRouter()


def is_project_manager(user: User) -> bool:
    """检查是否是项目经理"""
    return any(role.code == "project_manager" for role in user.roles) or user.is_superuser


@router.get("/projects/{project_id}/milestones", response_model=List[Milestone], summary="获取项目时间节点列表")
def get_milestones(
    project_id: int,
    include_invisible: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目的时间节点列表
    
    - **project_id**: 项目ID
    - **include_invisible**: 是否包含供应商不可见的节点（仅管理员可见）
    """
    # 检查项目是否存在
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 供应商只能查看可见的节点
    milestones = MilestoneService.get_by_project(db, project_id, include_invisible)
    
    # 如果不是管理员，过滤掉不可见的节点
    if not is_project_manager(current_user):
        milestones = [m for m in milestones if m.is_visible_to_supplier]
    
    return milestones


@router.get("/projects/{project_id}/milestones/{milestone_id}", response_model=Milestone, summary="获取时间节点详情")
def get_milestone(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个时间节点详情"""
    milestone = MilestoneService.get_by_id(db, milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间节点不存在"
        )
    
    if milestone.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="时间节点不属于该项目"
        )
    
    # 供应商只能查看可见的节点
    if not is_project_manager(current_user) and not milestone.is_visible_to_supplier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该节点"
        )
    
    return milestone


@router.post("/projects/{project_id}/milestones", response_model=Milestone, summary="创建时间节点")
def create_milestone(
    project_id: int,
    milestone_in: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建项目时间节点（项目经理或管理员）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以创建时间节点"
        )
    
    return MilestoneService.create(db, project_id, milestone_in, current_user.id)


@router.put("/projects/{project_id}/milestones/{milestone_id}", response_model=Milestone, summary="更新时间节点")
def update_milestone(
    project_id: int,
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新时间节点（项目经理或管理员）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以更新时间节点"
        )
    
    milestone = MilestoneService.get_by_id(db, milestone_id)
    if not milestone or milestone.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间节点不存在或不属于该项目"
        )
    
    return MilestoneService.update(db, milestone_id, milestone_in)


@router.delete("/projects/{project_id}/milestones/{milestone_id}", response_model=Response, summary="删除时间节点")
def delete_milestone(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除时间节点（项目经理或管理员）
    
    注意：只能删除待开始或已取消的节点
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以删除时间节点"
        )
    
    milestone = MilestoneService.get_by_id(db, milestone_id)
    if not milestone or milestone.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间节点不存在或不属于该项目"
        )
    
    MilestoneService.delete(db, milestone_id)
    return Response(message="删除成功")


@router.post("/projects/{project_id}/milestones/{milestone_id}/complete", response_model=Milestone, summary="标记节点完成")
def complete_milestone(
    project_id: int,
    milestone_id: int,
    complete_data: MilestoneComplete = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记时间节点完成（项目经理或管理员）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以标记节点完成"
        )
    
    milestone = MilestoneService.get_by_id(db, milestone_id)
    if not milestone or milestone.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="时间节点不存在或不属于该项目"
        )
    
    actual_date = complete_data.actual_date if complete_data else None
    return MilestoneService.complete(db, milestone_id, actual_date)


@router.put("/projects/{project_id}/milestones/reorder", response_model=List[Milestone], summary="批量更新节点顺序")
def reorder_milestones(
    project_id: int,
    reorder_data: MilestoneReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量更新节点顺序（项目经理或管理员）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以更新节点顺序"
        )
    
    return MilestoneService.reorder(db, project_id, reorder_data.milestone_ids)


@router.post("/projects/{project_id}/milestones/import-template", response_model=List[Milestone], summary="导入默认节点模板")
def import_milestone_template(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导入默认节点模板（项目经理或管理员）
    
    为项目创建默认的时间节点模板（需求发布、报价截止、报价评审等）
    """
    if not is_project_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有项目经理或管理员可以导入节点模板"
        )
    
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return MilestoneService.import_template(db, project_id, current_user.id, project)


@router.get("/projects/{project_id}/progress", response_model=ProjectProgress, summary="获取项目进度")
def get_project_progress(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目进度信息（基于时间节点计算）
    """
    # 检查项目是否存在
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 计算进度
    progress_data = MilestoneService.calculate_project_progress(db, project_id)
    
    # 获取所有节点
    milestones = MilestoneService.get_by_project(db, project_id)
    
    # 如果不是管理员，过滤掉不可见的节点
    if not is_project_manager(current_user):
        milestones = [m for m in milestones if m.is_visible_to_supplier]
    
    return ProjectProgress(
        project_id=project_id,
        total_progress=progress_data["total_progress"],
        completed_milestones=progress_data["completed_milestones"],
        total_milestones=progress_data["total_milestones"],
        critical_milestones=progress_data["critical_milestones"],
        milestones=milestones
    )


from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.supplier import Supplier, SupplierStatus
from app.models.project import Project, ProjectStatus
from app.models.quotation import Quotation, QuotationStatus
from app.models.operation_log import OperationLog
from app.models.project_category import ProjectCategory
from app.schemas.response import Response
from pydantic import BaseModel
from datetime import datetime, timedelta
from decimal import Decimal

router = APIRouter()


class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    # 通用统计
    suppliers_count: int = 0  # 供应商总数
    pending_suppliers_count: int = 0  # 待审核供应商数
    projects_count: int = 0  # 项目总数
    ongoing_projects_count: int = 0  # 进行中的项目数
    bidding_projects_count: int = 0  # 竞标中的项目数
    new_projects_this_month: int = 0  # 本月新增项目数
    new_projects_last_month: int = 0  # 上月新增项目数（用于对比）
    quotations_count: int = 0  # 报价总数
    total_quotation_amount: float = 0.0  # 总报价金额
    
    # 项目状态统计
    project_status_stats: dict = {}  # 项目状态统计 {status: count}
    
    # 报价状态统计
    quotation_status_stats: dict = {}  # 报价状态统计 {status: count}
    
    # 项目类别统计
    project_category_stats: list = []  # [{category_name: str, count: int, ongoing: int, completed: int}]
    
    # 供应商审核状态统计
    supplier_status_stats: dict = {}  # {status: count}
    
    # 项目创建趋势（最近6个月）
    project_trend: list = []  # [{month: str, count: int}]
    
    # 待办事项
    pending_tasks: dict = {}  # {pending_suppliers: [], upcoming_deadlines: [], pending_quotations: []}
    
    # 最近活动（操作日志）
    recent_activities: list = []  # 最近10条操作记录
    
    # 供应商角色专属
    participated_projects_count: int = 0  # 参与项目数
    pending_quotation_projects_count: int = 0  # 待报价项目数
    submitted_quotations_count: int = 0  # 已提交报价数
    winning_projects_count: int = 0  # 中标项目数
    participated_projects: list = []  # 参与的项目列表（包含进度信息）
    pending_quotation_projects: list = []  # 待报价项目列表
    draft_quotations: list = []  # 草稿报价列表


def _get_admin_stats(db: Session, stats: DashboardStats, current_user: User):
    """获取管理员/项目经理统计数据"""
    now = datetime.now()
    current_month_start = datetime(now.year, now.month, 1)
    if now.month == 1:
        last_month_start = datetime(now.year - 1, 12, 1)
        last_month_end = datetime(now.year, 1, 1) - timedelta(seconds=1)
    else:
        last_month_start = datetime(now.year, now.month - 1, 1)
        last_month_end = current_month_start - timedelta(seconds=1)
    
    # 根据用户角色决定是否只看自己的项目
    is_admin = current_user.is_superuser
    project_query = db.query(Project)
    if not is_admin:
        # 项目经理只能看自己创建的项目
        project_query = project_query.filter(Project.creator_id == current_user.id)
    
    # 供应商总数（只有管理员能看到）
    if is_admin:
        stats.suppliers_count = db.query(Supplier).filter(
            Supplier.user_id.isnot(None)
        ).count()
    else:
        stats.suppliers_count = 0
    
    # 待审核供应商数（只有管理员能看到）
    if is_admin:
        stats.pending_suppliers_count = db.query(Supplier).filter(
            Supplier.status == SupplierStatus.PENDING
        ).count()
    else:
        stats.pending_suppliers_count = 0
    
    # 供应商审核状态统计（只有管理员能看到）
    if is_admin:
        supplier_status_counts = db.query(
            Supplier.status,
            func.count(Supplier.id).label('count')
        ).group_by(Supplier.status).all()
        
        stats.supplier_status_stats = {str(status_val): count for status_val, count in supplier_status_counts}
    else:
        stats.supplier_status_stats = {}
    
    # 项目总数
    stats.projects_count = project_query.count()
    
    # 进行中的项目数（状态为1）
    stats.ongoing_projects_count = project_query.filter(
        Project.status == ProjectStatus.ONGOING
    ).count()
    
    # 竞标中的项目数（状态为3）
    stats.bidding_projects_count = project_query.filter(
        Project.status == ProjectStatus.BIDDING
    ).count()
    
    # 本月新增项目数
    stats.new_projects_this_month = project_query.filter(
        Project.created_at >= current_month_start
    ).count()
    
    # 上月新增项目数
    stats.new_projects_last_month = project_query.filter(
        and_(
            Project.created_at >= last_month_start,
            Project.created_at <= last_month_end
        )
    ).count()
    
    # 项目状态统计
    project_status_counts = project_query.with_entities(
        Project.status,
        func.count(Project.id).label('count')
    ).group_by(Project.status).all()
    
    stats.project_status_stats = {str(status_val): count for status_val, count in project_status_counts}
    
    # 项目类别统计
    try:
        if is_admin:
            # 管理员可以看到所有项目类别统计
            category_stats = db.query(
                ProjectCategory.category_name,
                func.count(Project.id).label('total_count'),
                func.sum(func.case((Project.status == ProjectStatus.ONGOING, 1), else_=0)).label('ongoing_count'),
                func.sum(func.case((Project.status == ProjectStatus.COMPLETED, 1), else_=0)).label('completed_count')
            ).outerjoin(Project, ProjectCategory.id == Project.category_id).group_by(ProjectCategory.id, ProjectCategory.category_name).all()
        else:
            # 项目经理只能看到自己项目的类别统计
            category_stats = db.query(
                ProjectCategory.category_name,
                func.count(Project.id).label('total_count'),
                func.sum(func.case((Project.status == ProjectStatus.ONGOING, 1), else_=0)).label('ongoing_count'),
                func.sum(func.case((Project.status == ProjectStatus.COMPLETED, 1), else_=0)).label('completed_count')
            ).join(Project, ProjectCategory.id == Project.category_id).filter(
                Project.creator_id == current_user.id
            ).group_by(ProjectCategory.id, ProjectCategory.category_name).all()
        
        stats.project_category_stats = [
            {
                "category_name": name or "未分类",
                "count": int(total_count or 0),
                "ongoing": int(ongoing_count or 0),
                "completed": int(completed_count or 0)
            }
            for name, total_count, ongoing_count, completed_count in category_stats
        ]
    except Exception as e:
        # 如果查询失败，返回空列表
        stats.project_category_stats = []
    
    # 项目创建趋势（最近6个月）
    six_months_ago = now - timedelta(days=180)
    trend_query = project_query.filter(
        Project.created_at >= six_months_ago
    ).with_entities(
        extract('year', Project.created_at).label('year'),
        extract('month', Project.created_at).label('month'),
        func.count(Project.id).label('count')
    ).group_by(
        extract('year', Project.created_at),
        extract('month', Project.created_at)
    ).order_by(
        extract('year', Project.created_at),
        extract('month', Project.created_at)
    )
    
    trend_data = trend_query.all()
    stats.project_trend = [
        {
            "month": f"{int(year)}-{int(month):02d}",
            "count": int(count)
        }
        for year, month, count in trend_data
    ]
    
    # 报价相关统计（基于当前用户的项目）
    if is_admin:
        # 管理员可以看到所有报价
        stats.quotations_count = db.query(Quotation).count()
        
        # 总报价金额
        total_amount_result = db.query(func.sum(Quotation.total_amount)).scalar()
        stats.total_quotation_amount = float(total_amount_result or 0)
        
        # 报价状态统计
        quotation_status_counts = db.query(
            Quotation.status,
            func.count(Quotation.id).label('count')
        ).group_by(Quotation.status).all()
    else:
        # 项目经理只能看到自己项目的报价
        user_project_ids = [p.id for p in project_query.all()]
        if user_project_ids:
            stats.quotations_count = db.query(Quotation).filter(
                Quotation.project_id.in_(user_project_ids)
            ).count()
            
            # 总报价金额
            total_amount_result = db.query(func.sum(Quotation.total_amount)).filter(
                Quotation.project_id.in_(user_project_ids)
            ).scalar()
            stats.total_quotation_amount = float(total_amount_result or 0)
            
            # 报价状态统计
            quotation_status_counts = db.query(
                Quotation.status,
                func.count(Quotation.id).label('count')
            ).filter(
                Quotation.project_id.in_(user_project_ids)
            ).group_by(Quotation.status).all()
        else:
            stats.quotations_count = 0
            stats.total_quotation_amount = 0
            quotation_status_counts = []
    
    stats.quotation_status_stats = {status.value: count for status, count in quotation_status_counts}
    
    # 中标率计算已移除（不再显示）
    
    # 待办事项：待审核供应商（只有管理员能看到）
    if is_admin:
        try:
            pending_suppliers = db.query(Supplier).filter(
                Supplier.status == SupplierStatus.PENDING
            ).order_by(Supplier.created_at.desc()).limit(5).all()
            
            stats.pending_tasks["pending_suppliers"] = [
                {
                    "id": s.id,
                    "company_name": s.company_name,
                    "contact_person": s.contact_person,
                    "contact_phone": s.contact_phone,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "status": s.status
                }
                for s in pending_suppliers
            ]
        except Exception:
            stats.pending_tasks["pending_suppliers"] = []
    else:
        stats.pending_tasks["pending_suppliers"] = []
    
    # 待办事项：即将截止的项目（投标截止时间在3天内）
    try:
        three_days_later = now + timedelta(days=3)
        upcoming_deadlines = project_query.filter(
            and_(
                Project.bidding_deadline.isnot(None),
                Project.bidding_deadline >= now,
                Project.bidding_deadline <= three_days_later,
                Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING])
            )
        ).order_by(Project.bidding_deadline.asc()).limit(5).all()
        
        stats.pending_tasks["upcoming_deadlines"] = [
            {
                "id": p.id,
                "project_no": p.project_no,
                "project_name": p.project_name,
                "bidding_deadline": p.bidding_deadline.isoformat() if p.bidding_deadline else None,
                "status": p.status,
                "remaining_hours": int((p.bidding_deadline - now).total_seconds() / 3600) if p.bidding_deadline else None
            }
            for p in upcoming_deadlines
        ]
    except Exception:
        stats.pending_tasks["upcoming_deadlines"] = []
    
    # 待办事项：待评审报价（已提交但未评审）
    try:
        if is_admin:
            # 管理员可以看到所有待评审报价
            pending_quotations_query = db.query(Quotation).filter(
                Quotation.status == QuotationStatus.SUBMITTED,
                Quotation.evaluated_at.is_(None)
            )
        else:
            # 项目经理只能看到自己项目的待评审报价
            user_project_ids = [p.id for p in project_query.all()]
            if user_project_ids:
                pending_quotations_query = db.query(Quotation).filter(
                    and_(
                        Quotation.status == QuotationStatus.SUBMITTED,
                        Quotation.evaluated_at.is_(None),
                        Quotation.project_id.in_(user_project_ids)
                    )
                )
            else:
                pending_quotations_query = db.query(Quotation).filter(
                    Quotation.id == -1  # 不存在的ID，返回空结果
                )
        
        pending_quotations = pending_quotations_query.order_by(Quotation.submitted_at.desc()).limit(5).all()
        
        stats.pending_tasks["pending_quotations"] = [
            {
                "id": q.id,
                "quotation_no": q.quotation_no,
                "project_id": q.project_id,
                "project_name": q.project.project_name if q.project else None,
                "supplier_id": q.supplier_id,
                "supplier_name": q.supplier.company_name if q.supplier else None,
                "total_amount": float(q.total_amount),
                "submitted_at": q.submitted_at.isoformat() if q.submitted_at else None
            }
            for q in pending_quotations
        ]
    except Exception:
        stats.pending_tasks["pending_quotations"] = []
    
    # 最近活动（操作日志，最近10条）
    try:
        if is_admin:
            # 管理员可以看到所有活动
            recent_logs = db.query(OperationLog).order_by(
                OperationLog.created_at.desc()
            ).limit(10).all()
        else:
            # 项目经理只能看到与自己项目相关的活动
            user_project_ids = [p.id for p in project_query.all()]
            if user_project_ids:
                # 先获取用户项目的所有报价ID
                user_quotation_ids = [q.id for q in db.query(Quotation.id).filter(Quotation.project_id.in_(user_project_ids)).all()]
                recent_logs = db.query(OperationLog).filter(
                    or_(
                        and_(
                            OperationLog.resource_type == "project",
                            OperationLog.resource_id.in_(user_project_ids)
                        ),
                        and_(
                            OperationLog.resource_type == "quotation",
                            OperationLog.resource_id.in_(user_quotation_ids)
                        )
                    )
                ).order_by(OperationLog.created_at.desc()).limit(10).all()
            else:
                recent_logs = []
        
        stats.recent_activities = [
            {
                "id": log.id,
                "username": log.username,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "resource_name": log.resource_name,
                "description": log.description,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in recent_logs
        ]
    except Exception:
        stats.recent_activities = []


def _get_supplier_stats(db: Session, stats: DashboardStats, supplier: Supplier):
    """获取供应商统计数据"""
    from app.services.milestone_service import MilestoneService
    
    # 获取供应商参与的项目ID（已报价的项目）
    project_ids_query = db.query(Quotation.project_id).filter(
        Quotation.supplier_id == supplier.id
    ).distinct()
    
    unique_project_ids = [pid[0] for pid in project_ids_query.all()]
    stats.participated_projects_count = len(unique_project_ids)
    
    # 获取可以报价但还未报价的项目（进行中或竞标中，且未报价）
    # 只有审核通过的供应商才能看到可报价的项目
    if supplier.status == SupplierStatus.APPROVED:
        if unique_project_ids:
            available_projects = db.query(Project).filter(
                and_(
                    Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING]),
                    ~Project.id.in_(unique_project_ids)
                )
            ).all()
        else:
            available_projects = db.query(Project).filter(
                Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING])
            ).all()
    else:
        available_projects = []
    
    stats.pending_quotation_projects_count = len(available_projects)
    
    # 待报价项目列表（最多5条，按投标截止时间排序）
    pending_quotation_projects = sorted(
        [p for p in available_projects if p.bidding_deadline],
        key=lambda x: x.bidding_deadline if x.bidding_deadline else datetime.max
    )[:5]
    
    now = datetime.now()
    stats.pending_quotation_projects = [
        {
            "id": p.id,
            "project_no": p.project_no,
            "project_name": p.project_name,
            "bidding_deadline": p.bidding_deadline.isoformat() if p.bidding_deadline else None,
            "status": p.status,
            "remaining_hours": int((p.bidding_deadline - now).total_seconds() / 3600) if p.bidding_deadline else None
        }
        for p in pending_quotation_projects
    ]
    
    # 已提交报价数
    stats.submitted_quotations_count = db.query(Quotation).filter(
        and_(
            Quotation.supplier_id == supplier.id,
            Quotation.status == QuotationStatus.SUBMITTED
        )
    ).count()
    
    # 中标项目数
    winning_quotations = db.query(Quotation).filter(
        and_(
            Quotation.supplier_id == supplier.id,
            Quotation.status == QuotationStatus.SELECTED
        )
    ).all()
    
    stats.winning_projects_count = len(set(q.project_id for q in winning_quotations))
    
    # 总报价金额
    total_amount_result = db.query(func.sum(Quotation.total_amount)).filter(
        Quotation.supplier_id == supplier.id
    ).scalar()
    stats.total_quotation_amount = float(total_amount_result or 0)
    
    # 报价状态统计
    quotation_status_counts = db.query(
        Quotation.status,
        func.count(Quotation.id).label('count')
    ).filter(
        Quotation.supplier_id == supplier.id
    ).group_by(Quotation.status).all()
    
    stats.quotation_status_stats = {status.value: count for status, count in quotation_status_counts}
    
    # 参与项目列表（最多10条，包含进度信息）
    if unique_project_ids:
        projects = db.query(Project).filter(
            Project.id.in_(unique_project_ids)
        ).order_by(Project.created_at.desc()).limit(10).all()
        
        participated_projects = []
        for project in projects:
            # 获取该供应商对此项目的报价
            quotation = db.query(Quotation).filter(
                Quotation.project_id == project.id,
                Quotation.supplier_id == supplier.id
            ).order_by(Quotation.created_at.desc()).first()
            
            # 计算项目进度（基于里程碑）
            progress_data = MilestoneService.calculate_project_progress(db, project.id)
            progress = progress_data.get("total_progress", 0)
            
            participated_projects.append({
                "id": project.id,
                "project_no": project.project_no,
                "project_name": project.project_name,
                "status": project.status,
                "progress": progress,
                "quotation_status": quotation.status.value if quotation else None,
                "quotation_amount": float(quotation.total_amount) if quotation else None,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
            })
        
        stats.participated_projects = participated_projects
    
    # 草稿报价列表（最多5条）
    draft_quotations = db.query(Quotation).filter(
        and_(
            Quotation.supplier_id == supplier.id,
            Quotation.status == QuotationStatus.DRAFT
        )
    ).order_by(Quotation.created_at.desc()).limit(5).all()
    
    stats.draft_quotations = [
        {
            "id": q.id,
            "quotation_no": q.quotation_no,
            "project_id": q.project_id,
            "project_name": q.project.project_name if q.project else None,
            "total_amount": float(q.total_amount),
            "created_at": q.created_at.isoformat() if q.created_at else None
        }
        for q in draft_quotations
    ]
    
    # 最近活动（供应商相关的操作日志）
    quotation_ids_result = db.query(Quotation.id).filter(Quotation.supplier_id == supplier.id).all()
    quotation_ids = [q[0] for q in quotation_ids_result]
    
    if quotation_ids or unique_project_ids:
        conditions = []
        if quotation_ids:
            conditions.append(
                and_(
                    OperationLog.resource_type == "quotation",
                    OperationLog.resource_id.in_(quotation_ids)
                )
            )
        if unique_project_ids:
            conditions.append(
                and_(
                    OperationLog.resource_type == "project",
                    OperationLog.resource_id.in_(unique_project_ids)
                )
            )
        recent_logs = db.query(OperationLog).filter(or_(*conditions)).order_by(OperationLog.created_at.desc()).limit(10).all()
    else:
        recent_logs = []
    
    stats.recent_activities = [
        {
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "resource_name": log.resource_name,
            "description": log.description,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in recent_logs
    ]


@router.get("/stats", response_model=DashboardStats, summary="获取仪表盘统计数据")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取仪表盘统计数据
    
    根据用户角色返回不同的统计数据：
    - 管理员/项目经理：显示系统整体统计
    - 供应商：显示参与的项目进度
    """
    from app.services.supplier_service import SupplierService
    
    stats = DashboardStats()
    
    # 检查是否是供应商角色
    is_supplier = any(role.code == "supplier" for role in current_user.roles) if current_user.roles else False
    
    if is_supplier and not current_user.is_superuser:
        # 供应商角色：显示参与的项目进度
        try:
            supplier = SupplierService.get_by_user_id(db, current_user.id)
            if supplier:
                _get_supplier_stats(db, stats, supplier)
        except Exception as e:
            # 如果获取供应商信息失败，返回空数据
            pass
    else:
        # 管理员/项目经理：显示系统整体统计
        _get_admin_stats(db, stats, current_user)
    
    return stats


@router.get("/gantt", summary="获取项目甘特图数据")
def get_gantt_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目甘特图数据
    
    返回所有项目的开始时间、结束时间、里程碑等信息，用于绘制甘特图
    """
    from app.services.milestone_service import MilestoneService
    
    # 检查是否是供应商角色
    is_supplier = any(role.code == "supplier" for role in current_user.roles) if current_user.roles else False
    
    if is_supplier and not current_user.is_superuser:
        # 供应商只能看到已参与的项目
        from app.services.supplier_service import SupplierService
        try:
            supplier = SupplierService.get_by_user_id(db, current_user.id)
            if supplier:
                project_ids_query = db.query(Quotation.project_id).filter(
                    Quotation.supplier_id == supplier.id
                ).distinct()
                unique_project_ids = [pid[0] for pid in project_ids_query.all()]
                
                if unique_project_ids:
                    projects = db.query(Project).filter(
                        Project.id.in_(unique_project_ids),
                        Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING, ProjectStatus.COMPLETED])
                    ).all()
                else:
                    projects = []
            else:
                projects = []
        except Exception:
            projects = []
    else:
        # 管理员/项目经理：根据角色显示项目（只显示最新5个）
        if current_user.is_superuser:
            # 超级管理员：显示所有进行中、竞标中、已完成的项目
            projects = db.query(Project).filter(
                Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING, ProjectStatus.COMPLETED])
            ).order_by(Project.created_at.desc()).limit(5).all()
        else:
            # 项目经理：只显示自己创建的项目
            projects = db.query(Project).filter(
                Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING, ProjectStatus.COMPLETED]),
                Project.creator_id == current_user.id
            ).order_by(Project.created_at.desc()).limit(5).all()
    
    gantt_data = []
    for project in projects:
        # 获取项目里程碑
        milestones = MilestoneService.get_by_project(db, project.id, include_invisible=True)
        
        # 如果没有开始时间，使用创建时间
        start_date = project.start_date or project.created_at
        end_date = project.end_date
        
        project_item = {
            "id": project.id,
            "project_no": project.project_no,
            "project_name": project.project_name,
            "status": project.status,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "bidding_deadline": project.bidding_deadline.isoformat() if project.bidding_deadline else None,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.milestone_name,
                    "planned_date": m.planned_date.isoformat() if m.planned_date else None,
                    "actual_date": m.actual_date.isoformat() if m.actual_date else None,
                    "status": m.status,
                    "progress": m.progress,
                    "is_critical": m.is_critical
                }
                for m in milestones
            ]
        }
        gantt_data.append(project_item)
    
    return {"projects": gantt_data}


from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from datetime import datetime
from app.models.milestone import ProjectMilestone, MilestoneStatus
from app.models.project import Project
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate


class MilestoneService:
    """项目时间节点服务"""
    
    # 默认节点模板
    DEFAULT_MILESTONES = [
        {
            "milestone_name": "需求发布",
            "description": "项目需求发布，供应商可见",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 1
        },
        {
            "milestone_name": "报价截止",
            "description": "供应商报价截止时间",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 2
        },
        {
            "milestone_name": "报价评审",
            "description": "评审供应商报价",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 3
        },
        {
            "milestone_name": "中标通知",
            "description": "通知中标供应商",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 4
        },
        {
            "milestone_name": "合同签署",
            "description": "与中标供应商签署合同",
            "is_critical": False,
            "is_visible_to_supplier": False,
            "sort_order": 5
        },
        {
            "milestone_name": "项目执行",
            "description": "项目开始执行",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 6
        },
        {
            "milestone_name": "项目验收",
            "description": "项目验收完成",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 7
        },
        {
            "milestone_name": "项目完成",
            "description": "项目正式完成",
            "is_critical": True,
            "is_visible_to_supplier": True,
            "sort_order": 8
        }
    ]
    
    @staticmethod
    def get_by_id(db: Session, milestone_id: int) -> Optional[ProjectMilestone]:
        """根据ID获取时间节点"""
        return db.query(ProjectMilestone).filter(ProjectMilestone.id == milestone_id).first()
    
    @staticmethod
    def get_by_project(
        db: Session,
        project_id: int,
        include_invisible: bool = False
    ) -> List[ProjectMilestone]:
        """获取项目的所有时间节点"""
        query = db.query(ProjectMilestone).filter(ProjectMilestone.project_id == project_id)
        
        if not include_invisible:
            # 如果不需要包含不可见节点，可以在这里过滤（但通常由调用方决定）
            pass
        
        return query.order_by(ProjectMilestone.sort_order, ProjectMilestone.id).all()
    
    @staticmethod
    def create(
        db: Session,
        project_id: int,
        milestone_in: MilestoneCreate,
        created_by: int
    ) -> ProjectMilestone:
        """创建时间节点"""
        # 检查项目是否存在
        from sqlalchemy.orm import joinedload
        project = db.query(Project).options(
            joinedload(Project.creator),
            joinedload(Project.category)
        ).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 生成节点编号
        existing_count = db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id
        ).count()
        milestone_code = f"MS-{str(existing_count + 1).zfill(3)}"
        
        # 自动计算状态
        status = MilestoneStatus.PENDING
        if milestone_in.planned_date:
            now = datetime.now()
            if milestone_in.planned_date <= now and milestone_in.status == MilestoneStatus.PENDING:
                status = MilestoneStatus.IN_PROGRESS
        
        milestone = ProjectMilestone(
            project_id=project_id,
            milestone_name=milestone_in.milestone_name,
            milestone_code=milestone_code,
            description=milestone_in.description,
            planned_date=milestone_in.planned_date,
            actual_date=milestone_in.actual_date,
            status=status if milestone_in.status == 0 else milestone_in.status,
            progress=milestone_in.progress or 0,
            sort_order=milestone_in.sort_order or 0,
            is_critical=milestone_in.is_critical or False,
            is_visible_to_supplier=milestone_in.is_visible_to_supplier if milestone_in.is_visible_to_supplier is not None else True,
            created_by=created_by
        )
        
        db.add(milestone)
        db.commit()
        db.refresh(milestone)
        return milestone
    
    @staticmethod
    def update(
        db: Session,
        milestone_id: int,
        milestone_in: MilestoneUpdate
    ) -> ProjectMilestone:
        """更新时间节点"""
        milestone = MilestoneService.get_by_id(db, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="时间节点不存在"
            )
        
        update_data = milestone_in.model_dump(exclude_unset=True)
        
        # 如果设置了实际完成时间，自动标记为已完成
        if "actual_date" in update_data and update_data["actual_date"]:
            update_data["status"] = MilestoneStatus.COMPLETED
            update_data["progress"] = 100
        
        # 如果设置了状态为已完成，但实际时间未设置，使用当前时间
        if update_data.get("status") == MilestoneStatus.COMPLETED and not milestone.actual_date:
            if "actual_date" not in update_data:
                update_data["actual_date"] = datetime.now()
            update_data["progress"] = 100
        
        # 自动更新状态（基于计划时间）
        if "planned_date" in update_data or "status" in update_data:
            now = datetime.now()
            planned_date = update_data.get("planned_date", milestone.planned_date)
            current_status = update_data.get("status", milestone.status)
            
            if planned_date and current_status == MilestoneStatus.PENDING:
                if planned_date <= now:
                    update_data["status"] = MilestoneStatus.IN_PROGRESS
                elif milestone.planned_date and milestone.planned_date < now and current_status == MilestoneStatus.PENDING:
                    update_data["status"] = MilestoneStatus.DELAYED
        
        for field, value in update_data.items():
            setattr(milestone, field, value)
        
        db.commit()
        db.refresh(milestone)
        return milestone
    
    @staticmethod
    def delete(db: Session, milestone_id: int) -> bool:
        """删除时间节点"""
        milestone = MilestoneService.get_by_id(db, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="时间节点不存在"
            )
        
        # 只允许删除未开始或已取消的节点
        if milestone.status not in [MilestoneStatus.PENDING, MilestoneStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能删除待开始或已取消的节点"
            )
        
        db.delete(milestone)
        db.commit()
        return True
    
    @staticmethod
    def complete(
        db: Session,
        milestone_id: int,
        actual_date: Optional[datetime] = None
    ) -> ProjectMilestone:
        """标记节点完成"""
        milestone = MilestoneService.get_by_id(db, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="时间节点不存在"
            )
        
        milestone.status = MilestoneStatus.COMPLETED
        milestone.progress = 100
        milestone.actual_date = actual_date or datetime.now()
        
        db.commit()
        db.refresh(milestone)
        return milestone
    
    @staticmethod
    def reorder(
        db: Session,
        project_id: int,
        milestone_ids: List[int]
    ) -> List[ProjectMilestone]:
        """批量更新节点顺序"""
        milestones = db.query(ProjectMilestone).filter(
            and_(
                ProjectMilestone.project_id == project_id,
                ProjectMilestone.id.in_(milestone_ids)
            )
        ).all()
        
        if len(milestones) != len(milestone_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部分节点不存在或不属于该项目"
            )
        
        # 创建ID到节点的映射
        milestone_map = {m.id: m for m in milestones}
        
        # 更新排序
        for index, milestone_id in enumerate(milestone_ids, start=1):
            milestone = milestone_map[milestone_id]
            milestone.sort_order = index
        
        db.commit()
        
        # 重新查询并返回
        return MilestoneService.get_by_project(db, project_id)
    
    @staticmethod
    def import_template(
        db: Session,
        project_id: int,
        created_by: int,
        project: Optional[Project] = None
    ) -> List[ProjectMilestone]:
        """导入默认节点模板"""
        # 检查项目是否存在
        if not project:
            from sqlalchemy.orm import joinedload
            project = db.query(Project).options(
                joinedload(Project.creator),
                joinedload(Project.category)
            ).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="项目不存在"
                )
        
        # 检查是否已有节点
        existing_count = db.query(ProjectMilestone).filter(
            ProjectMilestone.project_id == project_id
        ).count()
        if existing_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目已有时间节点，无法导入模板"
            )
        
        milestones = []
        for template in MilestoneService.DEFAULT_MILESTONES:
            milestone_code = f"MS-{str(template['sort_order']).zfill(3)}"
            
            # 根据节点名称设置计划时间
            planned_date = None
            if template['milestone_name'] == "需求发布":
                planned_date = project.created_at
            elif template['milestone_name'] == "报价截止":
                planned_date = project.bidding_deadline
            elif template['milestone_name'] == "项目完成":
                planned_date = project.end_date
            
            milestone = ProjectMilestone(
                project_id=project_id,
                milestone_name=template['milestone_name'],
                milestone_code=milestone_code,
                description=template['description'],
                planned_date=planned_date,
                status=MilestoneStatus.PENDING,
                progress=0,
                sort_order=template['sort_order'],
                is_critical=template['is_critical'],
                is_visible_to_supplier=template['is_visible_to_supplier'],
                created_by=created_by
            )
            db.add(milestone)
            milestones.append(milestone)
        
        db.commit()
        
        # 刷新所有节点
        for milestone in milestones:
            db.refresh(milestone)
        
        return milestones
    
    @staticmethod
    def calculate_project_progress(db: Session, project_id: int) -> dict:
        """计算项目进度"""
        milestones = MilestoneService.get_by_project(db, project_id)
        
        if not milestones:
            return {
                "total_progress": 0,
                "completed_milestones": 0,
                "total_milestones": 0,
                "critical_milestones": {
                    "completed": 0,
                    "total": 0
                }
            }
        
        # 只计算关键节点的进度
        critical_milestones = [m for m in milestones if m.is_critical]
        
        if not critical_milestones:
            # 如果没有关键节点，使用所有节点
            critical_milestones = milestones
        
        total_critical = len(critical_milestones)
        completed_critical = sum(1 for m in critical_milestones if m.status == MilestoneStatus.COMPLETED)
        
        # 计算总进度（基于关键节点）
        total_progress = int((completed_critical / total_critical) * 100) if total_critical > 0 else 0
        
        # 计算所有节点
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)
        
        return {
            "total_progress": total_progress,
            "completed_milestones": completed_milestones,
            "total_milestones": total_milestones,
            "critical_milestones": {
                "completed": completed_critical,
                "total": total_critical
            }
        }


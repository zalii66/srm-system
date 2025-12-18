from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.project import Project, ProjectItem, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectItemCreate
from datetime import datetime


class ProjectService:
    # 定义允许的状态转换规则
    ALLOWED_STATUS_TRANSITIONS = {
        ProjectStatus.ONGOING: [ProjectStatus.BIDDING, ProjectStatus.STOPPED, ProjectStatus.CANCELLED],
        ProjectStatus.BIDDING: [ProjectStatus.ONGOING, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED],
        ProjectStatus.STOPPED: [ProjectStatus.ONGOING, ProjectStatus.CANCELLED],
        ProjectStatus.COMPLETED: [],  # 已完成状态不能转换
        ProjectStatus.CANCELLED: []   # 已取消状态不能转换
    }
    
    @staticmethod
    def validate_status_transition(old_status: int, new_status: int) -> bool:
        """验证状态转换是否合法
        
        Args:
            old_status: 当前状态
            new_status: 目标状态
            
        Returns:
            bool: 如果转换合法返回True，否则返回False
        """
        # 如果状态相同，允许（实际不转换）
        if old_status == new_status:
            return True
        
        # 获取允许的转换目标状态列表
        allowed = ProjectService.ALLOWED_STATUS_TRANSITIONS.get(old_status, [])
        return new_status in allowed
    
    @staticmethod
    def generate_project_no() -> str:
        """生成项目编号
        
        格式：PRJ + 年月日时分
        例如：PRJ202511031950（PRJ + 20251103 + 1950）
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        return f"PRJ{timestamp}"
    
    @staticmethod
    def _parse_datetime(value):
        """解析日期时间字符串为datetime对象"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # 尝试多种日期格式
            formats = [
                "%Y-%m-%d %H:%M:%S",  # 前端发送的格式
                "%Y-%m-%dT%H:%M:%S",  # ISO格式（无时区）
                "%Y-%m-%dT%H:%M:%S.%f",  # ISO格式（带微秒）
                "%Y-%m-%dT%H:%M:%SZ",  # ISO格式（UTC）
                "%Y-%m-%dT%H:%M:%S%z",  # ISO格式（带时区）
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            # 如果所有格式都失败，尝试fromisoformat（Python 3.7+）
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                pass
        return None
    
    @staticmethod
    def create(db: Session, project_in: ProjectCreate, creator_id: int) -> Project:
        """创建项目"""
        try:
            project_no = ProjectService.generate_project_no()
            
            # 解析日期字段
            start_date = ProjectService._parse_datetime(project_in.start_date)
            end_date = ProjectService._parse_datetime(project_in.end_date)
            bidding_deadline = ProjectService._parse_datetime(project_in.bidding_deadline)
            
            project = Project(
                project_no=project_no,
                project_name=project_in.project_name,
                description=project_in.description,
                category_id=project_in.category_id,
                location=project_in.location,
                start_date=start_date,
                end_date=end_date,
                bidding_deadline=bidding_deadline,
                branch_office=project_in.branch_office,
                company_id=project_in.company_id,
                creator_id=creator_id,
                status=ProjectStatus.ONGOING,  # 新增项目默认状态为"进行中"（1）
                attachments=project_in.attachments
            )
            
            db.add(project)
            db.flush()
            
            # 创建项目明细
            for index, item_data in enumerate(project_in.items, start=1):
                # 自动生成需求编号：项目编号-序号（如：PRJ202511040007-01）
                item_no = f"{project_no}-{str(index).zfill(2)}"
                
                item = ProjectItem(
                    project_id=project.id,
                    item_no=item_no,  # 自动生成，不使用item_data.item_no
                    item_name=item_data.item_name,
                    specification=item_data.specification,
                    unit=item_data.unit,
                    quantity=item_data.quantity,
                    estimated_price=item_data.estimated_price,
                    description=item_data.description
                )
                db.add(item)
            
            db.commit()
            db.refresh(project)
            return project
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def update_status_by_dates(db: Session, project: Project) -> Project:
        """根据日期自动更新项目状态
        
        状态转换规则（int类型）：
        1. 进行中(1) -> 到达开始日期 -> 竞标中(3)
        2. 竞标中(3) -> 到达结束日期 -> 已完成(4)
        """
        now = datetime.now()
        
        # 如果项目已取消或已完成，不自动更新状态
        if project.status in [ProjectStatus.CANCELLED, ProjectStatus.COMPLETED]:
            return project
        
        # 如果项目进行中(1)，且有开始日期，检查是否应该变为"竞标中(3)"
        if project.status == ProjectStatus.ONGOING and project.start_date:
            # 直接比较datetime对象（SQLAlchemy返回的是datetime对象）
            if now >= project.start_date:
                project.status = ProjectStatus.BIDDING
        
        # 如果项目竞标中(3)，且有结束日期，检查是否应该变为"已完成(4)"
        if project.status == ProjectStatus.BIDDING and project.end_date:
            # 直接比较datetime对象（SQLAlchemy返回的是datetime对象）
            if now >= project.end_date:
                project.status = ProjectStatus.COMPLETED
        
        return project
    
    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        """根据ID获取项目（预加载所有关联数据）"""
        from sqlalchemy.orm import joinedload
        from app.models.company import Company
        project = db.query(Project).options(
            joinedload(Project.creator),
            joinedload(Project.company).joinedload(Company.brand),
            joinedload(Project.category)
        ).filter(Project.id == project_id).first()
        
        if project:
            try:
                # 自动更新状态
                ProjectService.update_status_by_dates(db, project)
                db.commit()
                db.refresh(project)
            except Exception as e:
                db.rollback()
                # 状态更新失败不影响查询，继续返回项目
        
        return project
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        creator_id: Optional[int] = None,
        status: Optional[int] = None,
        category_id: Optional[int] = None
    ) -> tuple[List[Project], int]:
        """获取项目列表（包含报价数量统计）"""
        from sqlalchemy.orm import joinedload
        from sqlalchemy import func
        from app.models.quotation import Quotation
        
        query = db.query(Project).options(joinedload(Project.creator), joinedload(Project.category))
        
        if creator_id:
            query = query.filter(Project.creator_id == creator_id)
        
        if status is not None:
            query = query.filter(Project.status == status)
        
        if category_id is not None:
            query = query.filter(Project.category_id == category_id)
        
        total = query.count()
        projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
        
        # 批量获取报价数量（优化N+1查询问题）
        if projects:
            project_ids = [p.id for p in projects]
            # 使用聚合查询一次性获取所有项目的报价数量
            quotation_counts = db.query(
                Quotation.project_id,
                func.count(Quotation.id).label('count')
            ).filter(
                Quotation.project_id.in_(project_ids)
            ).group_by(Quotation.project_id).all()
            
            # 创建项目ID到报价数量的映射
            count_map = {pid: count for pid, count in quotation_counts}
            # 为每个项目添加报价数量属性
            for project in projects:
                project.quotation_count = count_map.get(project.id, 0)
        
        # 自动更新所有项目的状态
        updated = False
        for project in projects:
            old_status = project.status
            ProjectService.update_status_by_dates(db, project)
            if project.status != old_status:
                updated = True
        
        if updated:
            try:
                db.commit()
                # 重新查询以获取更新后的状态
                from sqlalchemy.orm import joinedload
                from sqlalchemy import func
                from app.models.quotation import Quotation
                
                query = db.query(Project).options(joinedload(Project.creator), joinedload(Project.category))
                if creator_id:
                    query = query.filter(Project.creator_id == creator_id)
                if status is not None:
                    query = query.filter(Project.status == status)
                if category_id is not None:
                    query = query.filter(Project.category_id == category_id)
                projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
                
                # 重新获取报价数量
                if projects:
                    project_ids = [p.id for p in projects]
                    quotation_counts = db.query(
                        Quotation.project_id,
                        func.count(Quotation.id).label('count')
                    ).filter(
                        Quotation.project_id.in_(project_ids)
                    ).group_by(Quotation.project_id).all()
                    
                    count_map = {pid: count for pid, count in quotation_counts}
                    for project in projects:
                        project.quotation_count = count_map.get(project.id, 0)
            except Exception as e:
                db.rollback()
                # 状态更新失败不影响查询，使用原结果
        
        return projects, total
    
    @staticmethod
    def update(db: Session, project_id: int, project_in: ProjectUpdate, user_id: int, is_admin: bool = False) -> Project:
        """更新项目
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            project_in: 更新数据
            user_id: 用户ID
            is_admin: 是否是管理员（超级用户）
        """
        from sqlalchemy.orm import joinedload
        from app.models.company import Company
        # 直接查询，不使用get_by_id避免自动状态更新干扰
        project = db.query(Project).options(
            joinedload(Project.creator),
            joinedload(Project.company).joinedload(Company.brand),
            joinedload(Project.category)
        ).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查权限（创建者或管理员可以修改）
        if not is_admin and project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此项目"
            )
        
        update_data = project_in.model_dump(exclude_unset=True)
        
        # 如果尝试修改状态，验证状态转换是否合法
        if 'status' in update_data:
            new_status = update_data['status']
            if not ProjectService.validate_status_transition(project.status, new_status):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不允许从状态'{project.status}'转换到状态'{new_status}'。已完成的或已取消的项目不能修改状态。"
                )
        
        # 解析日期字段
        if 'start_date' in update_data:
            update_data['start_date'] = ProjectService._parse_datetime(update_data['start_date'])
        if 'end_date' in update_data:
            update_data['end_date'] = ProjectService._parse_datetime(update_data['end_date'])
        if 'bidding_deadline' in update_data:
            update_data['bidding_deadline'] = ProjectService._parse_datetime(update_data['bidding_deadline'])
        
        try:
            for field, value in update_data.items():
                setattr(project, field, value)
            
            # 更新后自动检查并更新状态（如果状态未被手动修改）
            if 'status' not in update_data:
                ProjectService.update_status_by_dates(db, project)
            
            db.commit()
            db.refresh(project)
            return project
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def delete(db: Session, project_id: int, user_id: int, is_admin: bool = False) -> bool:
        """删除项目
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            user_id: 用户ID
            is_admin: 是否是管理员（超级用户）
        """
        project = ProjectService.get_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查权限（创建者或管理员可以删除）
        if not is_admin and project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此项目"
            )
        
        try:
            db.delete(project)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def publish(db: Session, project_id: int, user_id: int, is_admin: bool = False) -> Project:
        """发布项目（从已停止状态转为进行中）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            user_id: 用户ID
            is_admin: 是否是管理员（超级用户）
        """
        from sqlalchemy.orm import joinedload
        from app.models.company import Company
        # 直接查询，不使用get_by_id避免自动状态更新干扰
        project = db.query(Project).options(
            joinedload(Project.creator),
            joinedload(Project.company).joinedload(Company.brand),
            joinedload(Project.category)
        ).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查权限（创建者或管理员可以发布）
        if not is_admin and project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权发布此项目"
            )
        
        # 检查当前状态是否可以发布（可以从已停止或已取消状态发布）
        if project.status not in [ProjectStatus.STOPPED, ProjectStatus.ONGOING, ProjectStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目当前状态为'{project.status}'，只能从'已停止'或'已取消'状态发布项目"
            )
        
        try:
            # 设置状态为进行中(1)
            project.status = ProjectStatus.ONGOING
            db.commit()
            db.refresh(project)
            
            # 发布后检查是否需要自动转换为竞标中状态
            ProjectService.update_status_by_dates(db, project)
            if project.status != ProjectStatus.ONGOING:
                db.commit()
                db.refresh(project)
            
            return project
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def stop(db: Session, project_id: int, user_id: int, is_admin: bool = False) -> Project:
        """停止项目（从进行中或竞标中转为已停止）
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            user_id: 用户ID
            is_admin: 是否是管理员（超级用户）
        """
        from sqlalchemy.orm import joinedload
        from app.models.company import Company
        project = db.query(Project).options(
            joinedload(Project.company).joinedload(Company.brand)
        ).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查权限（创建者或管理员可以停止）
        if not is_admin and project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权停止此项目"
            )
        
        # 检查当前状态是否可以停止（可以从进行中、竞标中或已取消状态停止）
        if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING, ProjectStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目当前状态为'{project.status}'，只能停止'进行中'、'竞标中'或'已取消'的项目"
            )
        
        try:
            project.status = ProjectStatus.STOPPED
            db.commit()
            db.refresh(project)
            return project
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def cancel(db: Session, project_id: int, user_id: int, is_admin: bool = False) -> Project:
        """取消项目
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            user_id: 用户ID
            is_admin: 是否是管理员（超级用户）
        """
        from sqlalchemy.orm import joinedload
        from app.models.company import Company
        project = db.query(Project).options(
            joinedload(Project.company).joinedload(Company.brand)
        ).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 检查权限（创建者或管理员可以取消）
        if not is_admin and project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权取消此项目"
            )
        
        # 检查当前状态是否可以取消
        if project.status in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目当前状态为'{project.status}'，已完成或已取消的项目不能再取消"
            )
        
        try:
            project.status = ProjectStatus.CANCELLED
            db.commit()
            db.refresh(project)
            return project
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def get_published_projects(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None
    ) -> tuple[List[Project], int]:
        """获取已发布的项目列表（供应商可见）
        
        注意：列表接口不加载items关系，避免序列化问题
        包含已发布和进行中的项目（供应商都可以查看）
        """
        from sqlalchemy.orm import joinedload
        # 供应商可以查看进行中(1)和竞标中(3)的项目
        query = db.query(Project).options(joinedload(Project.creator), joinedload(Project.category)).filter(
            Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING])
        )
        
        if category_id is not None:
            query = query.filter(Project.category_id == category_id)
        
        # 自动更新项目状态
        all_projects = query.all()
        updated = False
        for project in all_projects:
            old_status = project.status
            ProjectService.update_status_by_dates(db, project)
            if project.status != old_status:
                updated = True
        
        if updated:
            try:
                db.commit()
                # 重新查询
                from sqlalchemy.orm import joinedload
                query = db.query(Project).options(joinedload(Project.creator), joinedload(Project.category)).filter(
                    Project.status.in_([ProjectStatus.ONGOING, ProjectStatus.BIDDING])
                )
                if category_id is not None:
                    query = query.filter(Project.category_id == category_id)
            except Exception as e:
                db.rollback()
                # 状态更新失败不影响查询，使用原查询
        
        total = query.count()
        # 列表接口需要加载creator和category关系，但不加载items关系，避免数据过大和序列化问题
        from sqlalchemy import func
        from app.models.quotation import Quotation
        
        projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
        
        # 批量获取报价数量（优化N+1查询问题）
        if projects:
            project_ids = [p.id for p in projects]
            quotation_counts = db.query(
                Quotation.project_id,
                func.count(Quotation.id).label('count')
            ).filter(
                Quotation.project_id.in_(project_ids)
            ).group_by(Quotation.project_id).all()
            
            count_map = {pid: count for pid, count in quotation_counts}
            for project in projects:
                project.quotation_count = count_map.get(project.id, 0)
        
        return projects, total


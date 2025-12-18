from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.project_category import ProjectCategory
from app.schemas.project_category import ProjectCategoryCreate, ProjectCategoryUpdate


class ProjectCategoryService:
    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[ProjectCategory]:
        """根据ID获取项目类别"""
        return db.query(ProjectCategory).filter(ProjectCategory.id == category_id).first()
    
    @staticmethod
    def get_by_code(db: Session, category_code: str) -> Optional[ProjectCategory]:
        """根据编码获取项目类别"""
        return db.query(ProjectCategory).filter(ProjectCategory.category_code == category_code).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[List[ProjectCategory], int]:
        """获取项目类别列表"""
        query = db.query(ProjectCategory)
        
        if is_active is not None:
            query = query.filter(ProjectCategory.is_active == is_active)
        
        query = query.order_by(ProjectCategory.sort_order.asc(), ProjectCategory.created_at.desc())
        total = query.count()
        categories = query.offset(skip).limit(limit).all()
        return categories, total
    
    @staticmethod
    def create(db: Session, category_in: ProjectCategoryCreate) -> ProjectCategory:
        """创建项目类别"""
        # 检查编码是否已存在
        if ProjectCategoryService.get_by_code(db, category_in.category_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="类别编码已存在"
            )
        
        # 检查名称是否已存在
        existing = db.query(ProjectCategory).filter(ProjectCategory.category_name == category_in.category_name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="类别名称已存在"
            )
        
        try:
            category = ProjectCategory(**category_in.model_dump())
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def update(db: Session, category_id: int, category_in: ProjectCategoryUpdate) -> ProjectCategory:
        """更新项目类别"""
        category = ProjectCategoryService.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目类别不存在"
            )
        
        try:
            update_data = category_in.model_dump(exclude_unset=True)
            # 如果更新名称，检查是否与其他类别冲突
            if 'category_name' in update_data and update_data['category_name'] != category.category_name:
                existing = db.query(ProjectCategory).filter(
                    ProjectCategory.category_name == update_data['category_name'],
                    ProjectCategory.id != category_id
                ).first()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="类别名称已存在"
                    )
            
            for field, value in update_data.items():
                setattr(category, field, value)
            
            db.commit()
            db.refresh(category)
            return category
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def delete(db: Session, category_id: int) -> bool:
        """删除项目类别"""
        category = ProjectCategoryService.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目类别不存在"
            )
        
        # 检查是否有项目使用此类别
        from app.models.project import Project
        project_count = db.query(Project).filter(Project.category_id == category_id).count()
        if project_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除：有 {project_count} 个项目使用此类别"
            )
        
        try:
            db.delete(category)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise

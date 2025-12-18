from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    @staticmethod
    def get_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        """根据ID获取权限"""
        return db.query(Permission).filter(Permission.id == permission_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Permission]:
        """根据编码获取权限"""
        return db.query(Permission).filter(Permission.code == code).first()
    
    @staticmethod
    def get_multi(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[List[Permission], int]:
        """获取权限列表"""
        query = db.query(Permission)
        
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        
        total = query.count()
        permissions = query.offset(skip).limit(limit).all()
        return permissions, total
    
    @staticmethod
    def get_all(db: Session, is_active: Optional[bool] = None) -> List[Permission]:
        """获取所有权限（不分页）"""
        query = db.query(Permission)
        
        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)
        
        return query.all()
    
    @staticmethod
    def create(db: Session, permission_in: PermissionCreate) -> Permission:
        """创建权限"""
        # 检查编码是否已存在
        if PermissionService.get_by_code(db, permission_in.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限编码已存在"
            )
        
        # 检查名称是否已存在
        existing = db.query(Permission).filter(Permission.name == permission_in.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="权限名称已存在"
            )
        
        # 创建权限
        db_permission = Permission(
            name=permission_in.name,
            code=permission_in.code,
            resource=permission_in.resource,
            action=permission_in.action,
            description=permission_in.description,
            is_active=permission_in.is_active
        )
        
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def update(db: Session, permission_id: int, permission_in: PermissionUpdate) -> Permission:
        """更新权限"""
        db_permission = PermissionService.get_by_id(db, permission_id)
        if not db_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在"
            )
        
        # 更新字段
        update_data = permission_in.model_dump(exclude_unset=True)
        
        # 如果更新编码，检查是否与其他权限冲突
        if "code" in update_data and update_data["code"] != db_permission.code:
            existing = PermissionService.get_by_code(db, update_data["code"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="权限编码已存在"
                )
        
        # 如果更新名称，检查是否与其他权限冲突
        if "name" in update_data and update_data["name"] != db_permission.name:
            existing = db.query(Permission).filter(Permission.name == update_data["name"]).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="权限名称已存在"
                )
        
        # 更新字段
        for field, value in update_data.items():
            setattr(db_permission, field, value)
        
        db.commit()
        db.refresh(db_permission)
        return db_permission
    
    @staticmethod
    def delete(db: Session, permission_id: int) -> bool:
        """删除权限"""
        db_permission = PermissionService.get_by_id(db, permission_id)
        if not db_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="权限不存在"
            )
        
        db.delete(db_permission)
        db.commit()
        return True


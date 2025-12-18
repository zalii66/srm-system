from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    @staticmethod
    def get_by_id(db: Session, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return db.query(Role).options(
            joinedload(Role.permissions)
        ).filter(Role.id == role_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Role]:
        """根据编码获取角色（预加载权限）"""
        return db.query(Role).options(
            joinedload(Role.permissions)
        ).filter(Role.code == code).first()
    
    @staticmethod
    def get_multi(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Role], int]:
        """获取角色列表"""
        query = db.query(Role).options(
            joinedload(Role.permissions)
        )
        total = query.count()
        roles = query.offset(skip).limit(limit).all()
        return roles, total
    
    @staticmethod
    def create(db: Session, role_in: RoleCreate) -> Role:
        """创建角色"""
        # 检查编码是否已存在
        if RoleService.get_by_code(db, role_in.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色编码已存在"
            )
        
        # 创建角色
        db_role = Role(
            name=role_in.name,
            code=role_in.code,
            description=role_in.description,
            is_active=role_in.is_active
        )
        
        # 分配权限
        if role_in.permission_ids:
            permissions = db.query(Permission).filter(
                Permission.id.in_(role_in.permission_ids)
            ).all()
            db_role.permissions = permissions
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def update(db: Session, role_id: int, role_in: RoleUpdate) -> Role:
        """更新角色"""
        db_role = RoleService.get_by_id(db, role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        # 更新字段
        update_data = role_in.model_dump(exclude_unset=True)
        
        # 处理权限
        if "permission_ids" in update_data:
            permission_ids = update_data.pop("permission_ids")
            if permission_ids is not None:
                permissions = db.query(Permission).filter(
                    Permission.id.in_(permission_ids)
                ).all()
                db_role.permissions = permissions
        
        # 更新其他字段
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def delete(db: Session, role_id: int) -> bool:
        """删除角色"""
        db_role = RoleService.get_by_id(db, role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        db.delete(db_role)
        db.commit()
        return True


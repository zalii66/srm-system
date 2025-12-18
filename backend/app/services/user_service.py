from typing import Optional, List
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from datetime import datetime


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户（预加载角色及其权限）"""
        return db.query(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        ).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户（预加载角色及其权限）"""
        return db.query(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        ).filter(User.username == username).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户（预加载角色及其权限）"""
        return db.query(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        ).filter(User.email == email).first()
    
    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        """根据手机号获取用户（预加载角色及其权限）"""
        return db.query(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        ).filter(User.phone == phone).first()
    
    @staticmethod
    def get_multi(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """获取用户列表（预加载角色及其权限）"""
        from sqlalchemy import or_
        
        query = db.query(User).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        
        # 搜索关键词（支持搜索姓名、手机号、邮箱、用户名）
        if keyword:
            keyword = keyword.strip()
            if keyword:
                query = query.filter(
                    or_(
                        User.full_name.like(f"%{keyword}%"),
                        User.phone.like(f"%{keyword}%"),
                        User.email.like(f"%{keyword}%"),
                        User.username.like(f"%{keyword}%")
                    )
                )
        
        # 状态筛选
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total
    
    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if UserService.get_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if user_in.email and UserService.get_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 检查手机号是否已存在
        if user_in.phone and UserService.get_by_phone(db, user_in.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已存在"
            )
        
        # 创建用户
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            phone=user_in.phone,
            is_active=user_in.is_active
        )
        
        # 分配角色
        if user_in.role_ids:
            roles = db.query(Role).filter(Role.id.in_(user_in.role_ids)).all()
            db_user.roles = roles
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update(db: Session, user_id: int, user_in: UserUpdate) -> User:
        """更新用户"""
        db_user = UserService.get_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        update_data = user_in.model_dump(exclude_unset=True)
        
        # 如果更新密码
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # 处理角色
        if "role_ids" in update_data:
            role_ids = update_data.pop("role_ids")
            if role_ids is not None:
                roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
                db_user.roles = roles
        
        # 更新其他字段
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """删除用户"""
        from app.models.project import Project
        from app.models.quotation import Quotation
        from app.models.supplier import Supplier
        
        db_user = UserService.get_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查是否有创建的项目（需要先处理）
        projects_count = db.query(Project).filter(Project.creator_id == user_id).count()
        if projects_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该用户创建了 {projects_count} 个项目，无法删除。请先转移或删除相关项目。"
            )
        
        # 检查用户是否是供应商（user_id）
        supplier_as_owner = db.query(Supplier).filter(Supplier.user_id == user_id).first()
        if supplier_as_owner:
            # 如果用户是供应商，需要先检查该供应商是否有报价
            quotations_count = db.query(Quotation).filter(Quotation.supplier_id == supplier_as_owner.id).count()
            if quotations_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"该用户是供应商，且该供应商有 {quotations_count} 个报价记录，无法删除。请先处理相关报价。"
                )
        
        # 检查是否有作为审核人的供应商记录（需要先清空审核人信息）
        # 注意：需要排除用户自己拥有的供应商（因为会被CASCADE删除或被手动删除）
        if supplier_as_owner:
            # 如果用户是供应商的拥有者，只查询其他供应商的审核人记录
            suppliers_as_auditor = db.query(Supplier).filter(
                Supplier.audit_user_id == user_id,
                Supplier.id != supplier_as_owner.id
            ).all()
        else:
            # 如果用户不是供应商，查询所有供应商的审核人记录
            suppliers_as_auditor = db.query(Supplier).filter(
                Supplier.audit_user_id == user_id
            ).all()
        
        if suppliers_as_auditor:
            # 清空这些供应商的审核人信息
            for supplier in suppliers_as_auditor:
                supplier.audit_user_id = None
                supplier.audit_time = None
                supplier.audit_comment = None
        
        # 如果用户是供应商的拥有者，先手动删除供应商记录（避免CASCADE删除时的冲突）
        if supplier_as_owner:
            # 先清空该供应商作为其他供应商的审核人信息（如果存在）
            # 注意：这种情况理论上不应该存在，因为用户不能审核自己的供应商
            # 但为了安全，还是检查一下
            db.delete(supplier_as_owner)
        
        # 检查是否有作为评审人的报价记录（需要先清空评审人信息）
        quotations_as_evaluator = db.query(Quotation).filter(Quotation.evaluated_by == user_id).all()
        if quotations_as_evaluator:
            # 清空这些报价的评审人信息
            for quotation in quotations_as_evaluator:
                quotation.evaluated_by = None
                quotation.evaluated_at = None
                quotation.evaluation_comment = None
        
        # 检查是否有上传的文件记录（需要先处理）
        from app.models.upload import UploadFile
        uploads_count = db.query(UploadFile).filter(UploadFile.uploader_id == user_id).count()
        if uploads_count > 0:
            # uploader_id 是 NOT NULL，所以需要删除这些文件记录
            db.query(UploadFile).filter(UploadFile.uploader_id == user_id).delete()
        
        # 先提交清空的更改（不包括CASCADE删除的供应商）
        try:
            db.flush()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"清理关联数据失败: {str(e)}"
            )
        
        # 删除用户
        # Supplier 表有 CASCADE 删除，会自动删除关联的供应商记录（user_id外键）
        # 但需要确保在删除用户前，不会触发对供应商的更新操作
        try:
            db.delete(db_user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            # 获取详细的错误信息
            error_detail = str(e)
            if 'foreign key constraint' in error_detail.lower() or 'integrity constraint' in error_detail.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"删除用户失败：该用户有关联数据无法删除。错误详情: {error_detail}"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除用户失败: {error_detail}"
            )
    
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """认证用户（支持用户名或手机号登录）"""
        # 首先尝试通过用户名查找
        user = UserService.get_by_username(db, username)
        # 如果用户名未找到，尝试通过手机号查找
        if not user:
            user = UserService.get_by_phone(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        db.commit()
        
        return user


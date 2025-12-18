from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.supplier import Supplier, SupplierStatus
from app.models.user import User
from app.models.role import Role
from app.schemas.supplier import SupplierRegister, SupplierUpdate, SupplierAudit
from app.core.security import get_password_hash
from datetime import datetime


class SupplierService:
    @staticmethod
    def register(db: Session, supplier_in: SupplierRegister) -> Supplier:
        """供应商注册"""
        # 验证验证码（暂时使用简单验证：验证码为手机号后4位）
        # TODO: 后续可以接入真实的短信验证码服务
        expected_code = supplier_in.phone[-4:]
        if supplier_in.verification_code != expected_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误，请输入手机号后4位作为验证码"
            )
        
        # 检查手机号是否已存在
        from app.services.user_service import UserService
        existing_user = UserService.get_by_phone(db, supplier_in.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
        
        # 生成用户名（使用手机号）
        username = supplier_in.phone
        
        # 获取供应商角色
        supplier_role = db.query(Role).filter(Role.code == "supplier").first()
        if not supplier_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="供应商角色不存在，请联系管理员"
            )
        
        # 创建用户（使用手机号作为用户名）
        user = User(
            username=username,
            hashed_password=get_password_hash(supplier_in.password),
            full_name=None,  # 新用户注册时姓名为空，需要登录后完善
            phone=supplier_in.phone,
            email=None,  # 新用户注册时邮箱为空，需要登录后完善
            is_active=True,
            roles=[supplier_role]
        )
        db.add(user)
        db.flush()
        
        # 创建供应商信息（联系人暂时使用手机号，后续可以完善）
        supplier = Supplier(
            user_id=user.id,
            company_name=supplier_in.company_name,
            tax_number=None,
            contact_person=supplier_in.phone,  # 暂时使用手机号，后续需要完善
            contact_phone=supplier_in.phone,
            company_address=supplier_in.company_address,
            business_scope=supplier_in.business_scope,
            bank_account_name=None,
            bank_name=None,
            bank_account=None,
            status=SupplierStatus.PENDING  # 新注册用户状态为待审核
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        
        return supplier
    
    @staticmethod
    def get_by_id(db: Session, supplier_id: int) -> Optional[Supplier]:
        """根据ID获取供应商（预加载关联数据）"""
        from sqlalchemy.orm import joinedload
        return db.query(Supplier).options(
            joinedload(Supplier.user),
            joinedload(Supplier.audit_user)
        ).filter(Supplier.id == supplier_id).first()
    
    @staticmethod
    def get_by_user_id(db: Session, user_id: int, auto_create: bool = False) -> Optional[Supplier]:
        """根据用户ID获取供应商（预加载关联数据）"""
        from sqlalchemy.orm import joinedload
        supplier = db.query(Supplier).options(
            joinedload(Supplier.user),
            joinedload(Supplier.audit_user)
        ).filter(Supplier.user_id == user_id).first()
        
        # 如果不存在且允许自动创建，则创建初始供应商记录
        if not supplier and auto_create:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # 确保必填字段有值
                company_name = user.full_name or user.username or "未命名公司"
                contact_person = user.full_name or user.username or "未命名"
                contact_phone = user.phone or "00000000000"  # 提供默认值以满足非空约束
                
                supplier = Supplier(
                    user_id=user.id,
                    company_name=company_name,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    status=SupplierStatus.REJECTED
                )
                db.add(supplier)
                db.commit()
                db.refresh(supplier)
        
        return supplier
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None,
        keyword: Optional[str] = None
    ) -> tuple[List[Supplier], int]:
        """获取供应商列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            status: 审核状态筛选
            keyword: 模糊搜索关键词（手机号、公司名称、联系人）
        """
        from sqlalchemy import or_
        from sqlalchemy.orm import joinedload
        
        # 关联 User 表，并排除管理员用户
        query = db.query(Supplier).join(User, Supplier.user_id == User.id).filter(
            User.is_superuser == False
        )
        
        if status is not None:
            query = query.filter(Supplier.status == status)
        
        if keyword and keyword.strip():
            keyword_pattern = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    Supplier.contact_phone.like(keyword_pattern),
                    Supplier.company_name.like(keyword_pattern),
                    Supplier.contact_person.like(keyword_pattern)
                )
            )
        
        # 使用 joinedload 预加载关联的用户信息，先查询总数再查询数据
        total = query.count()
        
        # 优化：先应用 limit 和 offset，再加载关联数据
        suppliers = query.options(
            joinedload(Supplier.user)
        ).order_by(
            Supplier.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return suppliers, total
    
    @staticmethod
    def update(db: Session, supplier_id: int, supplier_in: SupplierUpdate) -> Supplier:
        """更新供应商信息
        
        如果当前状态是已通过审核，更新后状态会变为待审核（需要重新审核）
        """
        supplier = SupplierService.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # 如果当前状态是已通过，更新后需要重新审核
        was_approved = supplier.status == SupplierStatus.APPROVED
        
        update_data = supplier_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        
        # 如果之前是已通过状态，且有字段更新，则状态变为待审核（需要重新审核）
        if was_approved and update_data:
            supplier.status = SupplierStatus.PENDING
            # 清空审核信息，因为需要重新审核
            supplier.audit_user_id = None
            supplier.audit_time = None
            supplier.audit_comment = None
        
        # 如果供应商第一次提交资料（从初始状态变为有数据），设置为待审核
        if supplier.status == SupplierStatus.REJECTED and not was_approved and update_data:
            # 检查是否有必要字段更新（说明用户提交了资料）
            if any(field in update_data for field in ['company_name', 'contact_person', 'contact_phone', 'company_address']):
                supplier.status = SupplierStatus.PENDING
        
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def upload_qualification(db: Session, supplier_id: int, file_paths: List[str]) -> Supplier:
        """上传资质文件"""
        supplier = SupplierService.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        from app.utils.json_utils import serialize_qualification_docs
        supplier.qualification_docs = serialize_qualification_docs(file_paths)
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def audit(
        db: Session,
        supplier_id: int,
        audit_in: SupplierAudit,
        auditor_id: int
    ) -> Supplier:
        """审核供应商"""
        supplier = SupplierService.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        supplier.status = audit_in.status
        supplier.audit_user_id = auditor_id
        supplier.audit_time = datetime.now()
        supplier.audit_comment = audit_in.audit_comment
        
        db.commit()
        db.refresh(supplier)
        return supplier
    
    @staticmethod
    def delete(db: Session, supplier_id: int) -> bool:
        """删除供应商"""
        from app.models.quotation import Quotation
        
        supplier = SupplierService.get_by_id(db, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # 检查是否有报价记录
        quotations_count = db.query(Quotation).filter(Quotation.supplier_id == supplier_id).count()
        if quotations_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该供应商有 {quotations_count} 个报价记录，无法删除。请先处理相关报价。"
            )
        
        try:
            # 删除供应商记录（注意：这里不删除关联的用户，因为可能用户还有其他用途）
            # 如果需要删除用户，需要单独调用 UserService.delete
            db.delete(supplier)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除供应商失败: {str(e)}"
            )


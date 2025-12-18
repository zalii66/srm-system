from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.quotation import Quotation, QuotationItem, QuotationStatus
from app.models.project import Project, ProjectStatus
from app.schemas.quotation import QuotationCreate, QuotationUpdate, QuotationEvaluate
from app.services.supplier_service import SupplierService
from datetime import datetime
from decimal import Decimal
import uuid


class QuotationService:
    @staticmethod
    def generate_quotation_no() -> str:
        """生成报价单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = str(uuid.uuid4())[:6].upper()
        return f"QUO{timestamp}{random_str}"
    
    @staticmethod
    def create(db: Session, quotation_in: QuotationCreate, supplier_id: int) -> Quotation:
        """创建报价"""
        # 检查项目是否存在且已发布
        project = db.query(Project).filter(Project.id == quotation_in.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 只有进行中(1)和竞标中(3)的项目可以报价
        if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目未发布或已结束，无法报价"
            )
        
        # 检查是否已经报过价
        existing = db.query(Quotation).filter(
            Quotation.project_id == quotation_in.project_id,
            Quotation.supplier_id == supplier_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已对此项目报价，请修改现有报价"
            )
        
        # 计算总金额
        total_amount = Decimal(0)
        for item in quotation_in.items:
            total_amount += item.unit_price * item.quantity
        
        quotation_no = QuotationService.generate_quotation_no()
        
        quotation = Quotation(
            quotation_no=quotation_no,
            project_id=quotation_in.project_id,
            supplier_id=supplier_id,
            total_amount=total_amount,
            tax_rate=quotation_in.tax_rate,
            delivery_days=quotation_in.delivery_days,
            payment_terms=quotation_in.payment_terms,
            warranty_period=quotation_in.warranty_period,
            remarks=quotation_in.remarks,
            status=QuotationStatus.DRAFT
        )
        
        db.add(quotation)
        db.flush()
        
        # 创建报价明细
        for item_data in quotation_in.items:
            amount = item_data.unit_price * item_data.quantity
            item = QuotationItem(
                quotation_id=quotation.id,
                project_item_id=item_data.project_item_id,
                unit_price=item_data.unit_price,
                quantity=item_data.quantity,
                amount=amount,
                brand=item_data.brand,
                model=item_data.model,
                remarks=item_data.remarks
            )
            db.add(item)
        
        try:
            db.commit()
            # 重新加载关联关系
            quotation = db.query(Quotation).options(
                joinedload(Quotation.supplier),
                joinedload(Quotation.items).joinedload(QuotationItem.project_item)
            ).filter(Quotation.id == quotation.id).first()
            return quotation
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def get_by_id(db: Session, quotation_id: int) -> Optional[Quotation]:
        """根据ID获取报价（预加载所有关联数据）"""
        return db.query(Quotation).options(
            joinedload(Quotation.supplier),
            joinedload(Quotation.project),
            joinedload(Quotation.items).joinedload(QuotationItem.project_item)
        ).filter(Quotation.id == quotation_id).first()
    
    @staticmethod
    def get_multi_by_supplier(
        db: Session,
        supplier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Quotation], int]:
        """获取供应商的报价列表（预加载项目信息）"""
        query = db.query(Quotation).options(
            joinedload(Quotation.supplier),
            joinedload(Quotation.project)  # 添加项目信息预加载
        ).filter(Quotation.supplier_id == supplier_id)
        total = query.count()
        quotations = query.order_by(Quotation.created_at.desc()).offset(skip).limit(limit).all()
        return quotations, total
    
    @staticmethod
    def get_multi_by_project(
        db: Session,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Quotation], int]:
        """获取项目的所有报价（预加载供应商信息）"""
        query = db.query(Quotation).options(
            joinedload(Quotation.supplier),
            joinedload(Quotation.project)
        ).filter(Quotation.project_id == project_id)
        total = query.count()
        quotations = query.order_by(Quotation.created_at.desc()).offset(skip).limit(limit).all()
        return quotations, total
    
    @staticmethod
    def update(db: Session, quotation_id: int, quotation_in: QuotationUpdate, supplier_id: int) -> Quotation:
        """更新报价"""
        quotation = QuotationService.get_by_id(db, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )
        
        # 检查权限
        if quotation.supplier_id != supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此报价"
            )
        
        # 只有草稿和已取消状态的报价可以修改
        if quotation.status not in [QuotationStatus.DRAFT, QuotationStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前状态的报价不能修改"
            )
        
        try:
            # 先检查是否有明细项需要更新（直接从模型属性获取，不是从model_dump）
            items_data = None
            if quotation_in.items is not None:
                items_data = quotation_in.items
            
            # 获取更新数据（排除items字段，单独处理）
            update_data = quotation_in.model_dump(exclude_unset=True, exclude={'items'})
            
            # 更新基本字段
            for field, value in update_data.items():
                setattr(quotation, field, value)
            
            # 如果提供了明细项，更新明细（删除旧的，创建新的）
            if items_data is not None:
                # 删除旧的明细项
                db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation_id).delete()
                
                # 重新计算总金额
                total_amount = Decimal(0)
                for item_data in items_data:
                    total_amount += item_data.unit_price * item_data.quantity
                    amount = item_data.unit_price * item_data.quantity
                    item = QuotationItem(
                        quotation_id=quotation.id,
                        project_item_id=item_data.project_item_id,
                        unit_price=item_data.unit_price,
                        quantity=item_data.quantity,
                        amount=amount,
                        brand=item_data.brand,
                        model=item_data.model,
                        remarks=item_data.remarks
                    )
                    db.add(item)
                
                # 更新总金额
                quotation.total_amount = total_amount
            
            # 如果原来是已取消状态，修改后改为草稿状态，允许重新提交
            if quotation.status == QuotationStatus.CANCELLED:
                quotation.status = QuotationStatus.DRAFT
                quotation.submitted_at = None  # 清空提交时间
                quotation.evaluated_by = None  # 清空评审信息
                quotation.evaluated_at = None
                quotation.evaluation_comment = None
            
            db.commit()
            # 重新加载关联关系（包含明细项）
            quotation = db.query(Quotation).options(
                joinedload(Quotation.supplier),
                joinedload(Quotation.items).joinedload(QuotationItem.project_item)
            ).filter(Quotation.id == quotation_id).first()
            return quotation
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def submit(db: Session, quotation_id: int, supplier_id: int) -> Quotation:
        """提交报价"""
        quotation = QuotationService.get_by_id(db, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )
        
        if quotation.supplier_id != supplier_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权提交此报价"
            )
        
        try:
            quotation.status = QuotationStatus.SUBMITTED
            quotation.submitted_at = datetime.now()
            
            db.commit()
            # 重新加载关联关系
            quotation = db.query(Quotation).options(
                joinedload(Quotation.supplier)
            ).filter(Quotation.id == quotation_id).first()
            return quotation
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def evaluate(
        db: Session,
        quotation_id: int,
        evaluate_in: QuotationEvaluate,
        evaluator_id: int
    ) -> Quotation:
        """评审报价（支持重新评审）"""
        quotation = QuotationService.get_by_id(db, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )
        
        # 允许评审已提交、已中标、已拒绝的报价（支持重新评审）
        if quotation.status not in [QuotationStatus.SUBMITTED, QuotationStatus.SELECTED, QuotationStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能评审已提交、已中标或已拒绝的报价"
            )
        
        try:
            quotation.status = evaluate_in.status
            quotation.evaluated_by = evaluator_id
            quotation.evaluated_at = datetime.now()
            quotation.evaluation_comment = evaluate_in.evaluation_comment
            
            db.commit()
            # 重新加载关联关系
            quotation = db.query(Quotation).options(
                joinedload(Quotation.supplier)
            ).filter(Quotation.id == quotation_id).first()
            return quotation
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def cancel(db: Session, quotation_id: int, user_id: int, is_admin: bool = False) -> Quotation:
        """取消报价"""
        quotation = QuotationService.get_by_id(db, quotation_id)
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报价不存在"
            )
        
        # 权限检查：供应商只能取消自己的报价，管理员可以取消任何报价
        if not is_admin:
            supplier = SupplierService.get_by_user_id(db, user_id)
            if not supplier or quotation.supplier_id != supplier.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权取消此报价"
                )
        
        # 状态检查：只有 draft 和 submitted 可以取消
        if quotation.status not in [QuotationStatus.DRAFT, QuotationStatus.SUBMITTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前状态的报价不能取消"
            )
        
        try:
            quotation.status = QuotationStatus.CANCELLED
            db.commit()
            # 重新加载关联关系
            quotation = db.query(Quotation).options(
                joinedload(Quotation.supplier)
            ).filter(Quotation.id == quotation_id).first()
            return quotation
        except Exception as e:
            db.rollback()
            raise


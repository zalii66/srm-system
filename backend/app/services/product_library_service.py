from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, distinct
from app.models.quotation import QuotationItem
from app.models.quotation import Quotation
from app.models.project import ProjectItem
from app.models.project import Project
from app.models.supplier import Supplier


class ProductLibraryService:
    """产品库服务（基于报价明细）"""

    @staticmethod
    def get_products(
        db: Session,
        supplier_id: Optional[int] = None,
        project_id: Optional[int] = None,
        item_name: Optional[str] = None,
        specification: Optional[str] = None,
        project_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List, int]:
        """
        获取产品库列表
        
        基于报价明细（QuotationItem）汇总产品信息
        包含：产品名称、规格型号、品牌、报价、供应商、关联项目等
        """
        # 构建查询
        query = db.query(
            QuotationItem.id,
            ProjectItem.item_name.label('product_name'),
            ProjectItem.specification,
            ProjectItem.unit,
            QuotationItem.brand,
            QuotationItem.model,
            QuotationItem.origin,
            QuotationItem.unit_price,
            QuotationItem.quantity,
            QuotationItem.amount,
            Quotation.quotation_no,
            Quotation.status.label('quotation_status'),
            Quotation.created_at.label('quotation_date'),
            Supplier.id.label('supplier_id'),
            Supplier.company_name.label('supplier_name'),
            Project.id.label('project_id'),
            Project.project_no,
            Project.project_name,
            ProjectItem.id.label('project_item_id')
        ).join(
            Quotation, QuotationItem.quotation_id == Quotation.id
        ).join(
            ProjectItem, QuotationItem.project_item_id == ProjectItem.id
        ).join(
            Project, ProjectItem.project_id == Project.id
        ).join(
            Supplier, Quotation.supplier_id == Supplier.id
        )

        # 筛选条件
        if supplier_id:
            query = query.filter(Quotation.supplier_id == supplier_id)
        
        if project_id:
            query = query.filter(Project.id == project_id)
        
        # 如果 item_name 和 specification 相同（即使用 keyword 搜索），则使用 OR 条件
        if item_name and specification and item_name == specification:
            query = query.filter(
                or_(
                    ProjectItem.item_name.like(f'%{item_name}%'),
                    ProjectItem.specification.like(f'%{specification}%')
                )
            )
        else:
            if item_name:
                query = query.filter(ProjectItem.item_name.like(f'%{item_name}%'))
            
            if specification:
                query = query.filter(ProjectItem.specification.like(f'%{specification}%'))

        if project_name:
            query = query.filter(Project.project_name.like(f'%{project_name}%'))

        # 获取总数 - 使用 group_by 和 count 的组合
        # 先获取所有符合条件的 id，然后 count
        id_query = query.with_entities(QuotationItem.id)
        total = id_query.distinct().count()

        # 分页 - 使用 group_by 避免重复数据（更兼容的方式）
        # 需要确保 group_by 包含所有非聚合字段
        products = query.group_by(
            QuotationItem.id,
            ProjectItem.item_name,
            ProjectItem.specification,
            ProjectItem.unit,
            QuotationItem.brand,
            QuotationItem.model,
            QuotationItem.origin,
            QuotationItem.unit_price,
            QuotationItem.quantity,
            QuotationItem.amount,
            Quotation.quotation_no,
            Quotation.status,
            Quotation.created_at,
            Supplier.id,
            Supplier.company_name,
            Project.id,
            Project.project_no,
            Project.project_name,
            ProjectItem.id
        ).order_by(QuotationItem.created_at.desc()).offset(skip).limit(limit).all()

        return products, total

    @staticmethod
    def get_product_detail(db: Session, quotation_item_id: int):
        """
        获取产品详情
        """
        product = db.query(
            QuotationItem.id,
            ProjectItem.item_name.label('product_name'),
            ProjectItem.specification,
            ProjectItem.unit,
            ProjectItem.description.label('product_description'),
            QuotationItem.brand,
            QuotationItem.model,
            QuotationItem.origin,
            QuotationItem.unit_price,
            QuotationItem.quantity,
            QuotationItem.amount,
            QuotationItem.remarks,
            Quotation.quotation_no,
            Quotation.status.label('quotation_status'),
            Quotation.total_amount.label('quotation_total'),
            Quotation.created_at.label('quotation_date'),
            Quotation.submitted_at,
            Supplier.id.label('supplier_id'),
            Supplier.company_name.label('supplier_name'),
            Supplier.contact_person,
            Supplier.contact_phone,
            Project.id.label('project_id'),
            Project.project_no,
            Project.project_name,
            Project.description.label('project_description'),
            ProjectItem.id.label('project_item_id'),
            ProjectItem.item_no
        ).join(
            Quotation, QuotationItem.quotation_id == Quotation.id
        ).join(
            ProjectItem, QuotationItem.project_item_id == ProjectItem.id
        ).join(
            Project, ProjectItem.project_id == Project.id
        ).join(
            Supplier, Quotation.supplier_id == Supplier.id
        ).filter(
            QuotationItem.id == quotation_item_id
        ).first()

        return product

    @staticmethod
    def get_product_statistics(
        db: Session,
        supplier_id: Optional[int] = None
    ) -> dict:
        """
        获取产品库统计信息
        """
        query = db.query(QuotationItem).join(Quotation)

        if supplier_id:
            query = query.filter(Quotation.supplier_id == supplier_id)

        total_products = query.count()
        total_quotations = query.distinct(Quotation.id).count()
        total_projects = query.join(ProjectItem).join(Project).distinct(Project.id).count()

        # 统计品牌数量
        from sqlalchemy import distinct
        brand_count = db.query(distinct(QuotationItem.brand)).filter(
            QuotationItem.brand.isnot(None)
        ).join(Quotation)
        
        if supplier_id:
            brand_count = brand_count.filter(Quotation.supplier_id == supplier_id)
        
        brand_count = brand_count.count()

        return {
            'total_products': total_products,
            'total_quotations': total_quotations,
            'total_projects': total_projects,
            'brand_count': brand_count
        }


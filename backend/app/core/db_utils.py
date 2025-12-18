"""
数据库查询工具函数
统一管理常用查询模式，减少 N+1 查询问题
"""
from typing import Optional, Type, TypeVar
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.orm.query import Query

T = TypeVar('T')


def get_user_with_relations(db: Session, user_id: int):
    """获取用户及其关联数据（角色，权限按需加载）"""
    from app.models.user import User
    return db.query(User).options(
        selectinload(User.roles)
    ).filter(User.id == user_id).first()


def get_supplier_with_relations(db: Session, supplier_id: int):
    """获取供应商及其关联数据（用户、审核人）"""
    from app.models.supplier import Supplier
    return db.query(Supplier).options(
        joinedload(Supplier.user),
        joinedload(Supplier.audit_user)
    ).filter(Supplier.id == supplier_id).first()


def get_project_with_relations(db: Session, project_id: int):
    """获取项目及其关联数据（创建人、公司、品牌、类别）"""
    from app.models.project import Project
    from app.models.company import Company
    return db.query(Project).options(
        joinedload(Project.creator),
        joinedload(Project.company).joinedload(Company.brand),
        joinedload(Project.category)
    ).filter(Project.id == project_id).first()


def get_quotation_with_relations(db: Session, quotation_id: int):
    """获取报价及其关联数据（供应商、项目、明细、项目明细）"""
    from app.models.quotation import Quotation, QuotationItem
    return db.query(Quotation).options(
        joinedload(Quotation.supplier),
        joinedload(Quotation.project),
        joinedload(Quotation.items).joinedload(QuotationItem.project_item)
    ).filter(Quotation.id == quotation_id).first()


def get_projects_with_relations(db: Session, query: Optional[Query] = None):
    """获取项目列表及其关联数据"""
    from app.models.project import Project
    if query is None:
        query = db.query(Project)
    return query.options(
        joinedload(Project.creator),
        joinedload(Project.category)
    )


def get_quotations_with_relations(db: Session, query: Optional[Query] = None):
    """获取报价列表及其关联数据"""
    from app.models.quotation import Quotation
    if query is None:
        query = db.query(Quotation)
    return query.options(
        joinedload(Quotation.supplier)
    )


def get_suppliers_with_relations(db: Session, query: Optional[Query] = None):
    """获取供应商列表及其关联数据"""
    from app.models.supplier import Supplier
    if query is None:
        query = db.query(Supplier)
    return query.options(
        joinedload(Supplier.user)
    )


def get_users_with_relations(db: Session, query: Optional[Query] = None):
    """获取用户列表及其关联数据（仅角色，不加载权限以提高性能）"""
    from app.models.user import User
    from sqlalchemy.orm import selectinload
    if query is None:
        query = db.query(User)
    return query.options(
        selectinload(User.roles)
    )


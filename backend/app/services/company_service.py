from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    @staticmethod
    def get_by_id(db: Session, company_id: int) -> Optional[Company]:
        """根据ID获取公司（预加载品牌）"""
        from sqlalchemy.orm import joinedload
        return db.query(Company).options(
            joinedload(Company.brand)
        ).filter(Company.id == company_id).first()
    
    @staticmethod
    def get_by_code(db: Session, company_code: str) -> Optional[Company]:
        """根据编码获取公司"""
        return db.query(Company).filter(Company.company_code == company_code).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        brand_id: Optional[int] = None
    ) -> tuple[List[Company], int]:
        """获取公司列表"""
        from sqlalchemy.orm import joinedload
        query = db.query(Company).options(joinedload(Company.brand))
        
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)
        
        if brand_id is not None:
            query = query.filter(Company.brand_id == brand_id)
        
        query = query.order_by(Company.sort_order.asc(), Company.created_at.desc())
        total = query.count()
        companies = query.offset(skip).limit(limit).all()
        return companies, total
    
    @staticmethod
    def create(db: Session, company_in: CompanyCreate) -> Company:
        """创建公司"""
        # 检查编码是否已存在
        if CompanyService.get_by_code(db, company_in.company_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="公司编码已存在"
            )
        
        # 检查名称是否已存在
        existing = db.query(Company).filter(Company.company_name == company_in.company_name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="公司名称已存在"
            )
        
        try:
            company = Company(**company_in.model_dump())
            db.add(company)
            db.commit()
            db.refresh(company)
            return company
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def update(db: Session, company_id: int, company_in: CompanyUpdate) -> Company:
        """更新公司"""
        company = CompanyService.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="公司不存在"
            )
        
        try:
            update_data = company_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(company, field, value)
            
            db.commit()
            db.refresh(company)
            return company
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def delete(db: Session, company_id: int) -> bool:
        """删除公司"""
        company = CompanyService.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="公司不存在"
            )
        
        try:
            db.delete(company)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise


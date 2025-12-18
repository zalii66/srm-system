from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandService:
    @staticmethod
    def get_by_id(db: Session, brand_id: int) -> Optional[Brand]:
        """根据ID获取品牌"""
        return db.query(Brand).filter(Brand.id == brand_id).first()
    
    @staticmethod
    def get_by_code(db: Session, brand_code: str) -> Optional[Brand]:
        """根据编码获取品牌"""
        return db.query(Brand).filter(Brand.brand_code == brand_code).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> tuple[List[Brand], int]:
        """获取品牌列表"""
        query = db.query(Brand)
        
        if is_active is not None:
            query = query.filter(Brand.is_active == is_active)
        
        query = query.order_by(Brand.sort_order.asc(), Brand.created_at.desc())
        total = query.count()
        brands = query.offset(skip).limit(limit).all()
        return brands, total
    
    @staticmethod
    def create(db: Session, brand_in: BrandCreate) -> Brand:
        """创建品牌"""
        # 检查编码是否已存在
        if BrandService.get_by_code(db, brand_in.brand_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="品牌编码已存在"
            )
        
        # 检查名称是否已存在
        existing = db.query(Brand).filter(Brand.brand_name == brand_in.brand_name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="品牌名称已存在"
            )
        
        try:
            brand = Brand(**brand_in.model_dump())
            db.add(brand)
            db.commit()
            db.refresh(brand)
            return brand
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def update(db: Session, brand_id: int, brand_in: BrandUpdate) -> Brand:
        """更新品牌"""
        brand = BrandService.get_by_id(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        
        try:
            update_data = brand_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(brand, field, value)
            
            db.commit()
            db.refresh(brand)
            return brand
        except Exception as e:
            db.rollback()
            raise
    
    @staticmethod
    def delete(db: Session, brand_id: int) -> bool:
        """删除品牌"""
        brand = BrandService.get_by_id(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        
        try:
            db.delete(brand)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise


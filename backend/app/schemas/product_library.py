from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class ProductLibraryItem(BaseModel):
    """产品库列表项"""
    id: int
    product_name: str
    specification: Optional[str] = None
    unit: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    origin: Optional[str] = None
    unit_price: Decimal
    quantity: Decimal
    amount: Decimal
    quotation_no: str
    quotation_status: str
    quotation_date: datetime
    supplier_id: int
    supplier_name: str
    project_id: int
    project_no: str
    project_name: str
    project_item_id: int

    class Config:
        from_attributes = True


class ProductLibraryDetail(BaseModel):
    """产品库详情"""
    id: int
    product_name: str
    specification: Optional[str] = None
    unit: Optional[str] = None
    product_description: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    origin: Optional[str] = None
    unit_price: Decimal
    quantity: Decimal
    amount: Decimal
    remarks: Optional[str] = None
    quotation_no: str
    quotation_status: str
    quotation_total: Decimal
    quotation_date: datetime
    submitted_at: Optional[datetime] = None
    supplier_id: int
    supplier_name: str
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    project_id: int
    project_no: str
    project_name: str
    project_description: Optional[str] = None
    project_item_id: int
    item_no: str

    class Config:
        from_attributes = True


class ProductLibraryStatistics(BaseModel):
    """产品库统计"""
    total_products: int
    total_quotations: int
    total_projects: int
    brand_count: int

    class Config:
        from_attributes = True


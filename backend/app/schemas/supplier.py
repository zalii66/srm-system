from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SupplierRegister(BaseModel):
    """供应商注册"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    company_name: str = Field(..., min_length=2, max_length=200, description="公司名称")
    verification_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    company_address: Optional[str] = Field(None, max_length=500, description="公司地址")
    business_scope: Optional[str] = Field(None, description="经营范围")


class SupplierUpdate(BaseModel):
    """供应商信息更新"""
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    tax_number: Optional[str] = Field(None, max_length=50, description="公司税号")
    contact_person: Optional[str] = Field(None, min_length=2, max_length=100)
    contact_phone: Optional[str] = Field(None, min_length=11, max_length=20)
    company_address: Optional[str] = Field(None, max_length=500, description="注册地址")
    business_scope: Optional[str] = Field(None, description="主营产品")
    bank_account_name: Optional[str] = Field(None, max_length=100, description="账户名称")
    bank_name: Optional[str] = Field(None, max_length=200, description="开户行")
    bank_account: Optional[str] = Field(None, max_length=50, description="银行账号")
    qualification_docs: Optional[str] = Field(None, description="资质文件路径（JSON数组）")


class SupplierQualificationUpload(BaseModel):
    """资质文件上传"""
    file_ids: List[int] = Field(..., description="文件ID列表")


class SupplierAudit(BaseModel):
    """供应商审核"""
    status: int = Field(..., ge=0, le=1, description="审核状态（0审核失败/1审核通过）")
    audit_comment: Optional[str] = Field(None, description="审核意见")


class Supplier(BaseModel):
    """供应商信息"""
    id: int
    user_id: int
    company_name: str
    tax_number: Optional[str]
    contact_person: str
    contact_phone: str
    company_address: Optional[str]
    business_scope: Optional[str]
    bank_account_name: Optional[str]
    bank_name: Optional[str]
    bank_account: Optional[str]
    qualification_docs: Optional[str]
    status: int = Field(..., description="审核状态（0审核失败/1审核通过）")
    audit_user_id: Optional[int]
    audit_time: Optional[datetime]
    audit_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


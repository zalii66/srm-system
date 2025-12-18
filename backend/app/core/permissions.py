"""
权限检查工具
统一管理文件访问权限检查逻辑，避免代码重复
"""
from typing import Optional
from pathlib import Path
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.supplier_service import SupplierService


def check_file_permission(
    db: Session,
    current_user: User,
    file_path: str,
    file_type: str = "qualification",
    year_month: Optional[str] = None,
    filename: Optional[str] = None
) -> bool:
    """
    检查用户是否有权限访问文件
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        file_path: 文件路径（相对于 uploads 目录的路径，如 "qualification/202511/filename.jpg"）
        file_type: 文件类型 ("qualification" 或 "business_license")
        year_month: 年月目录（可选，用于新格式）
        filename: 文件名（可选）
    
    Returns:
        bool: 是否有权限访问
    
    Raises:
        HTTPException: 如果无权限访问，抛出 403 错误
    """
    # 超级管理员可以访问所有文件
    if current_user.is_superuser:
        return True
    
    # 非供应商用户且非管理员，拒绝访问
    supplier = SupplierService.get_by_user_id(db, current_user.id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此文件"
        )
    
    # 供应商用户需要检查文件是否属于自己
    from app.utils.json_utils import parse_qualification_docs
    
    # 获取供应商的资质文件列表
    qualification_docs = parse_qualification_docs(supplier.qualification_docs)
    
    # 构建文件 URL（支持新旧格式）
    # 如果提供了 year_month 和 filename，使用这些参数
    if year_month and filename:
        file_url = f"/uploads/{file_type}/{year_month}/{filename}"
        old_file_url = f"/api/v1/uploads/{file_type}/{year_month}/{filename}"
    elif filename:
        # 旧格式：无年月目录
        file_url = f"/uploads/{file_type}/{filename}"
        old_file_url = f"/api/v1/uploads/{file_type}/{filename}"
    else:
        # 从 file_path 中提取
        file_url = f"/uploads/{file_path}" if not file_path.startswith("/uploads/") else file_path
        old_file_url = f"/api/v1{file_url}" if not file_url.startswith("/api/v1") else file_url
    
    # 检查文件是否在供应商的资质文件列表中
    has_permission = False
    for doc in qualification_docs:
        # 支持新格式（对象）：{"url": "...", "name": "..."}
        if isinstance(doc, dict):
            doc_url = doc.get("url", "")
        # 支持旧格式（字符串）
        else:
            doc_url = doc if isinstance(doc, str) else ""
        
        if not doc_url:
            continue
        
        # 标准化 doc_url（移除 /api/v1 前缀）
        normalized_doc_url = doc_url.replace("/api/v1", "") if doc_url else ""
        
        # 检查完整 URL 匹配
        if normalized_doc_url in [file_url, old_file_url]:
            has_permission = True
            break
        
        # 检查文件名匹配（支持部分匹配，因为 URL 可能被截断）
        if filename and (normalized_doc_url.endswith(filename) or filename in normalized_doc_url):
            has_permission = True
            break
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此文件"
        )
    
    return True


def check_business_license_permission(
    db: Session,
    current_user: User,
    year_month: Optional[str] = None,
    filename: Optional[str] = None
) -> bool:
    """
    检查用户是否有权限访问营业执照文件
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        year_month: 年月目录（可选）
        filename: 文件名（可选）
    
    Returns:
        bool: 是否有权限访问
    """
    file_path = f"business_license/{year_month}/{filename}" if year_month else f"business_license/{filename}"
    return check_file_permission(db, current_user, file_path, "business_license", year_month, filename)


def check_qualification_permission(
    db: Session,
    current_user: User,
    year_month: Optional[str] = None,
    filename: Optional[str] = None
) -> bool:
    """
    检查用户是否有权限访问资质文件
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        year_month: 年月目录（可选）
        filename: 文件名（可选）
    
    Returns:
        bool: 是否有权限访问
    """
    file_path = f"qualification/{year_month}/{filename}" if year_month else f"qualification/{filename}"
    return check_file_permission(db, current_user, file_path, "qualification", year_month, filename)


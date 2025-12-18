"""
文件工具函数
统一管理文件路径验证、文件名清理等
"""
from pathlib import Path
from typing import Optional


def validate_file_path(upload_dir: Path, file_path: Path) -> bool:
    """
    验证文件路径安全性，防止路径遍历攻击
    
    Args:
        upload_dir: 上传文件的基础目录
        file_path: 要验证的文件路径
    
    Returns:
        bool: 如果路径安全返回 True，否则返回 False
    """
    try:
        # 解析路径并确保是绝对路径
        upload_dir_resolved = upload_dir.resolve()
        file_path_resolved = file_path.resolve()
        
        # 确保文件路径在允许的目录内
        file_path_resolved.relative_to(upload_dir_resolved)
        return True
    except ValueError:
        # 路径不在允许的目录内
        return False
    except Exception:
        # 其他错误（如路径不存在）
        return False


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
    if not filename:
        return ""
    
    # 移除路径分隔符和其他危险字符
    dangerous_chars = ['/', '\\', '..', '\x00', '\r', '\n']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    # 移除前后空格
    filename = filename.strip()
    
    # 移除 Windows 保留字符
    reserved_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in reserved_chars:
        filename = filename.replace(char, '_')
    
    return filename


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    验证文件扩展名
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表（小写，不含点号）
    
    Returns:
        bool: 如果扩展名允许返回 True，否则返回 False
    """
    if not filename:
        return False
    
    # 获取文件扩展名
    extension = Path(filename).suffix.lower().lstrip('.')
    
    return extension in allowed_extensions


def get_safe_file_path(upload_dir: Path, filename: str, subdirectory: Optional[str] = None) -> Path:
    """
    获取安全的文件路径
    
    Args:
        upload_dir: 上传文件的基础目录
        filename: 文件名
        subdirectory: 子目录（可选）
    
    Returns:
        Path: 安全的文件路径
    """
    # 清理文件名
    safe_filename = sanitize_filename(filename)
    
    # 构建路径
    if subdirectory:
        # 清理子目录名
        safe_subdir = sanitize_filename(subdirectory)
        file_path = upload_dir / safe_subdir / safe_filename
    else:
        file_path = upload_dir / safe_filename
    
    # 验证路径安全性
    if validate_file_path(upload_dir, file_path):
        return file_path
    else:
        raise ValueError(f"文件路径不安全: {file_path}")


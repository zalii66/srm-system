"""
JSON 工具函数
统一管理 JSON 序列化和反序列化，提供统一的错误处理
"""
import json
from typing import Any, Optional, List, Dict, Union


def safe_json_loads(json_str: Optional[str], default: Any = None) -> Any:
    """
    安全地解析 JSON 字符串
    
    Args:
        json_str: JSON 字符串
        default: 解析失败时的默认值
    
    Returns:
        解析后的对象，如果解析失败返回 default
    """
    if not json_str:
        return default if default is not None else []
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError, ValueError):
        return default if default is not None else []


def safe_json_dumps(obj: Any, ensure_ascii: bool = False, default: Any = None) -> Optional[str]:
    """
    安全地将对象序列化为 JSON 字符串
    
    Args:
        obj: 要序列化的对象
        ensure_ascii: 是否确保 ASCII 编码（False 表示使用 UTF-8）
        default: 序列化失败时的默认值
    
    Returns:
        JSON 字符串，如果序列化失败返回 default
    """
    if obj is None:
        return default
    
    try:
        return json.dumps(obj, ensure_ascii=ensure_ascii)
    except (TypeError, ValueError):
        return default


def parse_qualification_docs(json_str: Optional[str]) -> List[Union[str, Dict[str, Any]]]:
    """
    解析供应商资质文件列表
    
    Args:
        json_str: JSON 字符串
    
    Returns:
        资质文件列表（支持字符串和对象格式）
    """
    return safe_json_loads(json_str, default=[])


def serialize_qualification_docs(docs: List[Union[str, Dict[str, Any]]]) -> Optional[str]:
    """
    序列化供应商资质文件列表
    
    Args:
        docs: 资质文件列表
    
    Returns:
        JSON 字符串
    """
    if not docs:
        return None
    return safe_json_dumps(docs, ensure_ascii=False, default=None)


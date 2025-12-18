from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar, List

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    items: List[T]


"""
应用异常类
统一管理所有自定义异常
"""
from fastapi import status


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class BusinessLogicError(AppException):
    """业务逻辑错误异常"""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class PermissionDeniedError(AppException):
    """权限拒绝异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictError(AppException):
    """资源冲突异常"""
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)


class ValidationError(AppException):
    """验证错误异常"""
    def __init__(self, message: str = "验证失败"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


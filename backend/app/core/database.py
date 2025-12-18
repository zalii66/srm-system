"""数据库事务管理工具"""
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Callable, Any


def with_transaction(func: Callable) -> Callable:
    """数据库事务装饰器
    
    自动处理数据库事务的提交和回滚：
    - 函数执行成功时自动提交
    - 发生异常时自动回滚
    - SQLAlchemy错误转换为HTTP异常
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 从参数中获取 db session
        db: Session = None
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        if not db:
            db = kwargs.get('db')
        
        if not db:
            raise ValueError("数据库会话未找到，请确保传递 db 参数")
        
        try:
            result = func(*args, **kwargs)
            # 如果函数已经手动提交，不再重复提交
            if not db.in_transaction():
                db.commit()
            return result
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"数据库操作失败: {str(e)}"
            )
        except HTTPException:
            # HTTPException 直接抛出，但需要回滚
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            # 其他异常也记录并转换为HTTP异常
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"操作失败: {str(e)}"
            )
    
    return wrapper


def safe_commit(db: Session) -> bool:
    """安全提交事务
    
    如果已经在事务外或已提交，返回True
    发生错误时回滚并返回False
    """
    try:
        if db.in_transaction():
            db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        return False


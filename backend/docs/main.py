from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
import mimetypes
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.deps import get_db, get_current_user
from app.core.permissions import check_business_license_permission, check_qualification_permission
from app.core.exceptions import AppException, NotFoundError, PermissionDeniedError
from app.utils.file_utils import validate_file_path, sanitize_filename
from app.models.user import User

# 配置日志系统
setup_logging()
import logging
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="供应商关系管理系统 - 后端API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS中间件配置
# CORS_ORIGINS 已在 config.py 中处理，直接使用 settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)


# 全局异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """处理应用自定义异常"""
    logger.warning(f"应用异常: {exc.message} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    logger.warning(f"请求验证失败: {exc.errors()} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "请求参数验证失败",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未预期的异常"""
    logger.error(f"未预期的异常: {str(exc)} - 路径: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误" if not settings.DEBUG else str(exc)
        }
    )

# 静态文件服务（用于上传的文件）
# 注意：由于需要权限检查，营业执照文件通过路由提供服务，不使用直接挂载
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

# 营业执照文件获取路由（带权限检查）
@app.get("/uploads/business_license/{year_month}/{filename}", summary="获取营业执照图片（新格式）")
def get_business_license(
    year_month: str,
    filename: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取营业执照图片（新格式：按年月分类）"""
    # 清理文件名和年月目录，防止路径遍历攻击
    safe_filename = sanitize_filename(filename)
    safe_year_month = sanitize_filename(year_month)
    
    # 构建文件路径
    base_upload_dir = Path(settings.UPLOAD_DIR).resolve()
    file_path = base_upload_dir / "business_license" / safe_year_month / safe_filename
    
    # 验证文件路径安全性
    if not validate_file_path(base_upload_dir, file_path):
        logger.warning(f"文件路径不安全: {file_path} - 用户: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件路径无效"
        )
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限：使用统一的权限检查函数
    check_business_license_permission(db, current_user, safe_year_month, safe_filename)
    
    # 根据文件扩展名确定 media_type
    media_type, _ = mimetypes.guess_type(str(file_path))
    if not media_type:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_filename
    )


@app.get("/uploads/business_license/{filename}", summary="获取营业执照图片（兼容旧格式）")
def get_business_license_old(
    filename: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取营业执照图片（兼容旧格式：无年月目录）"""
    # 清理文件名，防止路径遍历攻击
    safe_filename = sanitize_filename(filename)
    
    # 构建文件路径
    base_upload_dir = Path(settings.UPLOAD_DIR).resolve()
    file_path = base_upload_dir / "business_license" / safe_filename
    
    # 验证文件路径安全性
    if not validate_file_path(base_upload_dir, file_path):
        logger.warning(f"文件路径不安全: {file_path} - 用户: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件路径无效"
        )
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限：使用统一的权限检查函数（旧格式，无年月目录）
    check_business_license_permission(db, current_user, None, safe_filename)
    
    # 根据文件扩展名确定 media_type
    media_type, _ = mimetypes.guess_type(str(file_path))
    if not media_type:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_filename
    )


@app.get("/uploads/qualification/{year_month}/{filename}", summary="获取证件资质文件（新格式）")
def get_qualification_file(
    year_month: str,
    filename: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取证件资质文件（新格式：按年月分类）"""
    # 清理文件名和年月目录，防止路径遍历攻击
    safe_filename = sanitize_filename(filename)
    safe_year_month = sanitize_filename(year_month)
    
    # 构建文件路径
    base_upload_dir = Path(settings.UPLOAD_DIR).resolve()
    file_path = base_upload_dir / "qualification" / safe_year_month / safe_filename
    
    # 验证文件路径安全性
    if not validate_file_path(base_upload_dir, file_path):
        logger.warning(f"文件路径不安全: {file_path} - 用户: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件路径无效"
        )
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限：使用统一的权限检查函数
    check_qualification_permission(db, current_user, safe_year_month, safe_filename)
    
    # 根据文件扩展名确定 media_type
    media_type, _ = mimetypes.guess_type(str(file_path))
    if not media_type:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_filename
    )



# 其他文件使用静态文件服务
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


@app.get("/", tags=["根路径"])
def root():
    """根路径"""
    return {
        "message": "欢迎使用SRM供应商管理系统API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG
    )


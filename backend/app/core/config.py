from pydantic_settings import BaseSettings
from pydantic import model_validator, field_validator
from typing import Optional, List
import os
import warnings


class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "SRM供应商管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # 数据库配置
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 默认8小时（480分钟），可通过环境变量覆盖
    
    # 默认管理员配置
    # 注意：生产环境必须通过环境变量设置管理员密码，禁止使用默认密码
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: Optional[str] = None  # 必须从环境变量读取，不允许硬编码
    
    # CORS配置（通过field_validator动态解析）
    CORS_ORIGINS: Optional[List[str]] = None
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"  # 上传文件目录
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 最大文件大小：10MB
    ALLOWED_IMAGE_EXTENSIONS: list = ["jpg", "jpeg","png"]  # 仅支持 JPG 图片
    
    # 项目附件支持的文件类型（更灵活，支持多种文档和图片格式）
    ALLOWED_PROJECT_FILE_EXTENSIONS: list = [
        "jpg", "jpeg", "png", "gif", "bmp", "webp",  # 图片格式
        "pdf",  # PDF文档
        "doc", "docx",  # Word文档
        "xls", "xlsx",  # Excel文档
        "ppt", "pptx"   # PowerPoint文档
    ]
    
    # 证件资质支持的文件类型（更严格，仅支持图片和PDF，用于证明资质）
    ALLOWED_QUALIFICATION_FILE_EXTENSIONS: list = [
        "jpg", "jpeg", "png",  # 图片格式
        "pdf"  # PDF文档
    ]
    
    # 兼容旧配置（保留，用于其他未分类的上传）
    ALLOWED_FILE_EXTENSIONS: list = ["jpg", "jpeg", "png","pdf","xlsx","xls","docx","doc"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS_ORIGINS环境变量"""
        if v is None:
            # 从环境变量读取
            env_value = os.getenv("CORS_ORIGINS", "")
            if env_value:
                # 按逗号分隔，过滤空字符串
                return [origin.strip() for origin in env_value.split(",") if origin.strip()]
            # 如果没有设置，开发环境返回空列表（由main.py中的FlexibleCORSMiddleware自动处理）
            if os.getenv("DEBUG", "True").lower() == "true":
                return []
            # 生产环境必须设置
            raise ValueError(
                "生产环境必须设置 CORS_ORIGINS 环境变量！\n"
                "格式：CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com"
            )
        # 如果已经是列表，直接返回
        if isinstance(v, list):
            return v
        # 如果是字符串，按逗号分隔
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @model_validator(mode='after')
    def validate_security_settings(self):
        """验证安全相关配置"""
        # 如果密码为空，在开发环境使用默认密码，生产环境报错
        if not self.DEFAULT_ADMIN_PASSWORD:
            if not self.DEBUG:
                # 生产环境必须设置密码
                raise ValueError(
                    "生产环境必须设置 DEFAULT_ADMIN_PASSWORD 环境变量！\n"
                    "请在 .env 文件中设置：DEFAULT_ADMIN_PASSWORD=你的强密码"
                )
            else:
                # 开发环境警告并使用默认密码
                warnings.warn(
                    "警告：未设置 DEFAULT_ADMIN_PASSWORD 环境变量，将使用默认密码 'admin123'。\n"
                    "生产环境部署前必须修改！",
                    UserWarning
                )
                self.DEFAULT_ADMIN_PASSWORD = "admin123"
        
        # 检查密码强度（如果是自定义密码）
        if self.DEFAULT_ADMIN_PASSWORD and self.DEFAULT_ADMIN_PASSWORD != "admin123":
            if len(self.DEFAULT_ADMIN_PASSWORD) < 8:
                raise ValueError("管理员密码长度至少为8位")
        
        return self
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()


from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UploadFileResponse(BaseModel):
    """文件上传响应"""
    id: int
    file_name: str
    file_path: str
    file_size: int
    file_type: Optional[str]
    mime_type: Optional[str]
    category: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class UploadFile(Base):
    """文件上传记录表"""
    __tablename__ = "upload_files"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小（字节）")
    file_type = Column(String(100), nullable=True, comment="文件类型")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    
    # 分类
    category = Column(String(50), nullable=True, comment="文件分类（qualification/project/quotation）")
    
    # 上传者
    uploader_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment="上传者ID")
    
    # 关联对象
    related_type = Column(String(50), nullable=True, comment="关联对象类型")
    related_id = Column(Integer, nullable=True, comment="关联对象ID")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系
    uploader = relationship("User", backref="uploaded_files")
    
    def __repr__(self):
        return f"<UploadFile {self.file_name}>"


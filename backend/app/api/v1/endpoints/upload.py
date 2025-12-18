from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.schemas.upload import UploadFileResponse
from app.schemas.response import Response
from app.models.upload import UploadFile as UploadFileModel
from app.models.user import User
from app.models.project import Project, ProjectStatus

router = APIRouter()


@router.post("/", response_model=List[UploadFileResponse], summary="上传文件")
async def upload_files(
    files: List[UploadFile] = File(None),
    file: UploadFile = File(None),
    category: str = Form("project"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传文件
    
    - **category**: 文件分类（project/quotation/qualification）
      - project: 项目附件，支持多种格式（jpg, jpeg, png, gif, bmp, webp, pdf, doc, docx, xls, xlsx, ppt, pptx）
      - qualification: 证件资质，仅支持图片和PDF（jpg, jpeg, png, pdf）
      - quotation: 报价附件，使用默认配置
    - 支持单个文件（file参数）或多个文件（files参数）
    """
    # 处理单个文件或文件列表
    file_list = []
    if files:
        file_list = files
    elif file:
        file_list = [file]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要上传的文件"
        )
    
    upload_dir = Path(settings.UPLOAD_DIR) / category
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 根据category选择允许的文件类型
    if category == "project":
        allowed_extensions = settings.ALLOWED_PROJECT_FILE_EXTENSIONS
    elif category == "qualification":
        allowed_extensions = settings.ALLOWED_QUALIFICATION_FILE_EXTENSIONS
    else:
        # 其他category使用默认配置
        allowed_extensions = settings.ALLOWED_FILE_EXTENSIONS
    
    uploaded_files = []
    
    for file in file_list:
        # 检查文件大小
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件 {file.filename} 超过最大大小限制（{settings.MAX_FILE_SIZE / 1024 / 1024}MB）"
            )
        
        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式：{file_ext}。支持的格式：{', '.join(allowed_extensions)}"
            )
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = upload_dir / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 保存到数据库
        upload_record = UploadFileModel(
            file_name=file.filename,
            file_path=f"{category}/{unique_filename}",
            file_size=len(file_content),
            file_type=file_ext,
            mime_type=file.content_type,
            category=category,
            uploader_id=current_user.id
        )
        
        db.add(upload_record)
        db.flush()
        db.refresh(upload_record)
        
        uploaded_files.append(upload_record)
    
    try:
        db.commit()
        return [UploadFileResponse.model_validate(f) for f in uploaded_files]
    except Exception as e:
        db.rollback()
        # 如果提交失败，尝试删除已保存的文件
        for file_record in uploaded_files:
            file_path = Path(settings.UPLOAD_DIR) / file_record.file_path
            if file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/", response_model=List[UploadFileResponse], summary="获取文件列表")
def get_files(
    file_ids: Optional[str] = Query(None, description="文件ID列表（逗号分隔）"),
    category: Optional[str] = Query(None, description="文件分类"),
    project_id: Optional[int] = Query(None, description="项目ID（用于验证项目附件权限）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取文件列表
    
    - **file_ids**: 文件ID列表，逗号分隔，如 "1,2,3"
    - **category**: 文件分类（project/quotation/qualification）
    - **project_id**: 项目ID（用于验证项目附件权限，供应商可以查看已发布项目的附件）
    """
    query = db.query(UploadFileModel)
    
    if file_ids:
        # 解析文件ID列表
        try:
            ids = [int(id.strip()) for id in file_ids.split(',') if id.strip()]
            if ids:
                query = query.filter(UploadFileModel.id.in_(ids))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件ID格式错误"
            )
    
    if category:
        query = query.filter(UploadFileModel.category == category)
    
    # 权限检查
    if not current_user.is_superuser:
        # 如果是项目附件且提供了项目ID，需要检查项目权限
        if category == 'project' and project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="项目不存在"
                )
            
            # 检查用户角色
            user_roles = [role.code for role in current_user.roles] if current_user.roles else []
            is_supplier = 'supplier' in user_roles
            is_project_manager = 'project_manager' in user_roles
            
            # 供应商只能查看已发布项目的附件
            if is_supplier:
                if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="项目未发布或已结束"
                    )
                # 供应商可以查看项目附件（不限制上传者）
                # 不添加 uploader_id 过滤条件
            # 项目经理只能查看自己项目的附件
            elif is_project_manager:
                if project.creator_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权查看此项目的附件"
                    )
                # 项目经理可以查看自己项目的附件（不限制上传者）
                # 不添加 uploader_id 过滤条件
            else:
                # 其他用户只能查看自己上传的文件
                query = query.filter(UploadFileModel.uploader_id == current_user.id)
        else:
            # 非项目附件，或者没有提供项目ID，只能查看自己上传的文件
            query = query.filter(UploadFileModel.uploader_id == current_user.id)
    
    files = query.order_by(UploadFileModel.created_at.desc()).all()
    
    return [UploadFileResponse.model_validate(f) for f in files]


@router.get("/{file_id}", response_model=UploadFileResponse, summary="获取文件详情")
def get_file(
    file_id: int,
    project_id: Optional[int] = Query(None, description="项目ID（用于验证项目附件权限）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取文件详情
    
    - **project_id**: 项目ID（用于验证项目附件权限，供应商可以查看已发布项目的附件）
    """
    upload_file = db.query(UploadFileModel).filter(UploadFileModel.id == file_id).first()
    
    if not upload_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 权限检查
    if not current_user.is_superuser:
        # 如果是项目附件且提供了项目ID，需要检查项目权限
        if upload_file.category == 'project' and project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="项目不存在"
                )
            
            # 检查用户角色
            user_roles = [role.code for role in current_user.roles] if current_user.roles else []
            is_supplier = 'supplier' in user_roles
            is_project_manager = 'project_manager' in user_roles
            
            # 供应商只能查看已发布项目的附件
            if is_supplier:
                if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="项目未发布或已结束"
                    )
                # 供应商可以查看项目附件
            # 项目经理只能查看自己项目的附件
            elif is_project_manager:
                if project.creator_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权查看此项目的附件"
                    )
                # 项目经理可以查看自己项目的附件
            else:
                # 其他用户只能查看自己上传的文件
                if upload_file.uploader_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权查看此文件"
                    )
        else:
            # 非项目附件，或者没有提供项目ID，只能查看自己上传的文件
            if upload_file.uploader_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权查看此文件"
                )
    
    return UploadFileResponse.model_validate(upload_file)


@router.get("/{file_id}/download", summary="下载文件")
def download_file(
    file_id: int,
    project_id: Optional[int] = Query(None, description="项目ID（用于验证项目附件权限）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载文件
    
    - **project_id**: 项目ID（用于验证项目附件权限，供应商可以下载已发布项目的附件）
    """
    upload_file = db.query(UploadFileModel).filter(UploadFileModel.id == file_id).first()
    
    if not upload_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 权限检查
    if not current_user.is_superuser:
        # 如果是项目附件且提供了项目ID，需要检查项目权限
        if upload_file.category == 'project' and project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="项目不存在"
                )
            
            # 检查用户角色
            user_roles = [role.code for role in current_user.roles] if current_user.roles else []
            is_supplier = 'supplier' in user_roles
            is_project_manager = 'project_manager' in user_roles
            
            # 供应商只能下载已发布项目的附件
            if is_supplier:
                if project.status not in [ProjectStatus.ONGOING, ProjectStatus.BIDDING]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="项目未发布或已结束"
                    )
                # 供应商可以下载项目附件
            # 项目经理只能下载自己项目的附件
            elif is_project_manager:
                if project.creator_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权下载此项目的附件"
                    )
                # 项目经理可以下载自己项目的附件
            else:
                # 其他用户只能下载自己上传的文件
                if upload_file.uploader_id != current_user.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权下载此文件"
                    )
        else:
            # 非项目附件，或者没有提供项目ID，只能下载自己上传的文件
            if upload_file.uploader_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权下载此文件"
                )
    
    # 构建文件路径
    file_path = Path(settings.UPLOAD_DIR) / upload_file.file_path
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 返回文件响应
    return FileResponse(
        path=str(file_path),
        filename=upload_file.file_name,
        media_type='application/octet-stream'
    )


@router.delete("/{file_id}", response_model=Response, summary="删除文件")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除文件
    """
    upload_file = db.query(UploadFileModel).filter(UploadFileModel.id == file_id).first()
    
    if not upload_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 检查权限（只能删除自己上传的文件，或管理员可以删除所有文件）
    if not current_user.is_superuser and upload_file.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文件"
        )
    
    # 删除物理文件
    file_path = Path(settings.UPLOAD_DIR) / upload_file.file_path
    if file_path.exists():
        file_path.unlink()
    
    try:
        # 删除数据库记录
        db.delete(upload_file)
        db.commit()
        return Response(message="删除成功")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, permissions, suppliers, projects, quotations, companies, brands, project_categories, upload, dashboard, milestones, product_library, operation_logs

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])

# 用户管理路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])

# 角色管理路由
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])

# 权限管理路由
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限管理"])

# 供应商管理路由
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["供应商管理"])

# 项目管理路由
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])

# 报价管理路由
api_router.include_router(quotations.router, prefix="/quotations", tags=["报价管理"])

# 公司管理路由
api_router.include_router(companies.router, prefix="/companies", tags=["公司管理"])

# 品牌管理路由
api_router.include_router(brands.router, prefix="/brands", tags=["品牌管理"])

# 项目类别管理路由
api_router.include_router(project_categories.router, prefix="/project-categories", tags=["项目类别管理"])

# 文件上传路由
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])

# 仪表盘路由
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])

# 项目时间节点路由（作为项目的子资源，不需要额外前缀）
api_router.include_router(milestones.router, tags=["项目时间节点管理"])

# 产品库路由
api_router.include_router(product_library.router, prefix="/product-library", tags=["产品库"])

# 操作日志路由
api_router.include_router(operation_logs.router, prefix="/operation-logs", tags=["操作日志"])


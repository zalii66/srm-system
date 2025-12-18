# SRM 项目结构说明

## 目录结构

```
backend/
│
├── app/                          # 应用主目录
│   ├── __init__.py
│   │
│   ├── api/                      # API接口层
│   │   ├── __init__.py
│   │   └── v1/                   # API版本1
│   │       ├── __init__.py
│   │       ├── api.py            # 路由聚合
│   │       └── endpoints/        # 各模块接口
│   │           ├── __init__.py
│   │           ├── auth.py       # 认证接口
│   │           ├── users.py      # 用户管理接口
│   │           └── roles.py      # 角色管理接口
│   │
│   ├── core/                     # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py             # 配置管理
│   │   ├── security.py           # 安全相关（JWT、密码加密）
│   │   └── deps.py               # 依赖注入
│   │
│   ├── db/                       # 数据库
│   │   ├── __init__.py
│   │   └── database.py           # 数据库连接和会话
│   │
│   ├── models/                   # SQLAlchemy 数据模型
│   │   ├── __init__.py
│   │   ├── user.py               # 用户模型
│   │   ├── role.py               # 角色模型
│   │   ├── permission.py         # 权限模型
│   │   └── role_permission.py    # 角色权限关联表
│   │
│   ├── schemas/                  # Pydantic 数据验证模型
│   │   ├── __init__.py
│   │   ├── user.py               # 用户Schema
│   │   ├── role.py               # 角色Schema
│   │   ├── permission.py         # 权限Schema
│   │   ├── token.py              # Token Schema
│   │   └── response.py           # 统一响应Schema
│   │
│   └── services/                 # 业务逻辑层
│       ├── __init__.py
│       ├── user_service.py       # 用户服务
│       └── role_service.py       # 角色服务
│
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略配置
├── requirements.txt              # Python依赖
├── alembic.ini                   # Alembic配置
│
├── main.py                       # 应用入口
├── init_db.py                    # 数据库初始化脚本
│
├── setup.bat                     # Windows安装脚本
├── init_db.bat                   # Windows数据库初始化脚本
├── run.bat                       # Windows启动脚本
│
├── README.md                     # 完整文档
├── QUICKSTART.md                 # 快速开始指南
└── PROJECT_STRUCTURE.md          # 本文件
```

## 核心组件说明

### 1. 数据模型层 (models/)

**用户模型 (User)**
- 字段: id, username, email, hashed_password, full_name, phone, is_active, is_superuser
- 关系: 多对多关联角色

**角色模型 (Role)**
- 字段: id, name, code, description, is_active
- 关系: 多对多关联用户和权限

**权限模型 (Permission)**
- 字段: id, name, code, resource, action, description, is_active
- 关系: 多对多关联角色

### 2. 数据验证层 (schemas/)

使用Pydantic进行数据验证，每个模型包含：
- `Base`: 基础字段
- `Create`: 创建时使用
- `Update`: 更新时使用
- `InDB`: 数据库返回（含所有字段）

### 3. 业务逻辑层 (services/)

封装业务逻辑，提供统一的服务接口：
- 数据查询
- 数据创建
- 数据更新
- 数据删除
- 业务验证

### 4. API接口层 (api/)

RESTful API接口，遵循以下规范：
- 使用路由前缀组织模块
- 统一的响应格式
- JWT认证保护
- OpenAPI文档自动生成

### 5. 核心功能 (core/)

**配置管理 (config.py)**
- 环境变量加载
- 数据库连接配置
- JWT配置

**安全功能 (security.py)**
- 密码加密/验证
- JWT生成/解析

**依赖注入 (deps.py)**
- 数据库会话管理
- 当前用户获取
- 权限验证

## 数据库设计

### ER关系

```
User (用户)
  ↓ N:M
user_role (用户角色关联表)
  ↓ N:M
Role (角色)
  ↓ N:M
role_permission (角色权限关联表)
  ↓ N:M
Permission (权限)
```

### 表结构

**users** - 用户表
- id (主键)
- username (唯一)
- email (唯一)
- hashed_password
- full_name
- phone
- is_active
- is_superuser
- created_at
- updated_at
- last_login

**roles** - 角色表
- id (主键)
- name (唯一)
- code (唯一)
- description
- is_active
- created_at
- updated_at

**permissions** - 权限表
- id (主键)
- name (唯一)
- code (唯一)
- resource
- action
- description
- is_active
- created_at
- updated_at

**user_role** - 用户角色关联表
- user_id (外键)
- role_id (外键)

**role_permission** - 角色权限关联表
- role_id (外键)
- permission_id (外键)

## API接口概览

### 认证接口 /api/v1/auth

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /login | 用户登录 | 否 |
| GET | /me | 获取当前用户 | 是 |
| POST | /logout | 用户登出 | 是 |

### 用户接口 /api/v1/users

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | / | 用户列表 | 超级管理员 |
| GET | /{id} | 用户详情 | 本人或管理员 |
| POST | / | 创建用户 | 超级管理员 |
| PUT | /{id} | 更新用户 | 本人或管理员 |
| DELETE | /{id} | 删除用户 | 超级管理员 |

### 角色接口 /api/v1/roles

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | / | 角色列表 | 超级管理员 |
| GET | /{id} | 角色详情 | 超级管理员 |
| POST | / | 创建角色 | 超级管理员 |
| PUT | /{id} | 更新角色 | 超级管理员 |
| DELETE | /{id} | 删除角色 | 超级管理员 |

## 认证流程

1. **登录**: POST /api/v1/auth/login
   - 提交用户名和密码
   - 验证成功返回JWT Token

2. **访问受保护资源**:
   - 在Header中添加: `Authorization: Bearer {token}`
   - 系统验证Token有效性
   - 提取用户信息并检查权限

3. **Token过期**:
   - Token默认30分钟过期
   - 过期后需要重新登录

## 权限控制

### RBAC模型

- **用户 (User)**: 系统使用者
- **角色 (Role)**: 权限的集合
- **权限 (Permission)**: 具体的操作权限

### 权限检查

1. **超级管理员**: `is_superuser=True`，拥有所有权限
2. **普通用户**: 通过角色获得权限
3. **依赖注入**: 使用 `Depends(get_current_superuser)` 等进行权限控制

## 扩展指南

### 添加新的API模块

1. **创建数据模型**: `app/models/your_model.py`
2. **创建Schema**: `app/schemas/your_schema.py`
3. **创建服务**: `app/services/your_service.py`
4. **创建接口**: `app/api/v1/endpoints/your_endpoint.py`
5. **注册路由**: 在 `app/api/v1/api.py` 中注册

### 添加新的权限

在 `init_db.py` 中添加权限定义，或通过API动态创建。

### 数据库迁移

使用Alembic进行版本控制：

```bash
# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 安全建议

1. **生产环境**:
   - 修改 `SECRET_KEY` 为强随机字符串
   - 设置 `DEBUG=False`
   - 配置具体的CORS来源
   - 使用HTTPS
   - 定期更新依赖包

2. **密码策略**:
   - 强制使用强密码
   - 定期修改密码
   - 修改默认管理员密码

3. **Token管理**:
   - 合理设置过期时间
   - 使用刷新令牌机制
   - 实现Token黑名单

## 性能优化

1. **数据库**:
   - 添加适当的索引
   - 使用连接池
   - 查询优化

2. **缓存**:
   - Redis缓存用户信息
   - 缓存权限数据

3. **异步**:
   - 使用FastAPI的异步特性
   - 异步数据库操作

## 监控和日志

建议添加：
- 请求日志
- 错误日志
- 性能监控
- 健康检查


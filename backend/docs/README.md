# SRM 供应商管理系统 - 后端API

基于FastAPI开发的供应商关系管理系统后端API，采用RBAC权限控制模型。

## 技术栈

- **FastAPI**: 现代化的Python Web框架
- **SQLAlchemy**: ORM框架
- **MySQL**: 数据库
- **PyMySQL**: MySQL数据库驱动
- **JWT**: 身份认证
- **Pydantic**: 数据验证

## 项目结构

```
backend/
├── app/
│   ├── api/              # API接口
│   │   └── v1/
│   │       ├── endpoints/  # 各模块接口
│   │       └── api.py      # 路由聚合
│   ├── core/             # 核心配置
│   │   ├── config.py       # 配置文件
│   │   ├── security.py     # 安全相关
│   │   └── deps.py         # 依赖注入
│   ├── db/               # 数据库
│   │   └── database.py     # 数据库连接
│   ├── models/           # 数据模型
│   │   ├── user.py
│   │   ├── role.py
│   │   └── permission.py
│   ├── schemas/          # Pydantic模型
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── token.py
│   │   └── response.py
│   └── services/         # 业务逻辑
│       ├── user_service.py
│       └── role_service.py
├── .env.example          # 环境变量示例
├── requirements.txt      # 依赖包
├── main.py              # 主程序
├── init_db.py           # 数据库初始化
└── README.md            # 说明文档
```

## 环境要求

- Python 3.8+
- MySQL 5.7+

## 安装步骤

### 1. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息。

### 4. 初始化数据库

确保MySQL服务已启动，然后运行：

```bash
python init_db.py
```

该脚本会自动：
- 创建数据库（如果不存在）
- 创建所有数据表
- 初始化默认角色和权限
- 创建默认管理员账号

**默认管理员账号：**
- 用户名: `admin`
- 密码: `admin`
- ⚠️ 首次登录后请立即修改密码！

### 5. 启动服务

```bash
# 开发模式（自动重载）
python main.py

# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API文档（Swagger）: http://localhost:8000/api/v1/docs
- API文档（ReDoc）: http://localhost:8000/api/v1/redoc

## API接口说明

### 认证管理 `/api/v1/auth`

- `POST /login` - 用户登录
- `GET /me` - 获取当前用户信息
- `POST /logout` - 用户登出

### 用户管理 `/api/v1/users`

- `GET /` - 获取用户列表（分页）
- `GET /{user_id}` - 获取用户详情
- `POST /` - 创建用户
- `PUT /{user_id}` - 更新用户
- `DELETE /{user_id}` - 删除用户

### 角色管理 `/api/v1/roles`

- `GET /` - 获取角色列表（分页）
- `GET /{role_id}` - 获取角色详情
- `POST /` - 创建角色
- `PUT /{role_id}` - 更新角色
- `DELETE /{role_id}` - 删除角色

## 权限说明

系统采用RBAC（基于角色的访问控制）模型：

- **User（用户）**: 系统用户
- **Role（角色）**: 用户角色
- **Permission（权限）**: 操作权限

关系：
- 用户 ↔ 角色：多对多
- 角色 ↔ 权限：多对多

## 数据库配置

默认配置：
- 主机: `127.0.0.1`
- 端口: `3306`
- 用户: `root`
- 密码: `root`
- 数据库: `srm`
- 字符集: `utf8mb4`
- 排序规则: `utf8mb4_general_ci`

## 身份认证

系统使用JWT（JSON Web Token）进行身份认证：

1. 用户通过 `/api/v1/auth/login` 登录，获取访问令牌
2. 后续请求在Header中携带令牌：`Authorization: Bearer <token>`
3. 令牌默认有效期：30分钟（可在.env中配置）

## 开发说明

### 添加新模块

1. 在 `app/models/` 创建数据模型
2. 在 `app/schemas/` 创建Pydantic模型
3. 在 `app/services/` 创建业务逻辑
4. 在 `app/api/v1/endpoints/` 创建API接口
5. 在 `app/api/v1/api.py` 注册路由

### 数据库迁移

使用Alembic进行数据库迁移：

```bash
# 初始化迁移
alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 检查 `.env` 中的数据库配置是否正确
- 确认数据库用户有足够的权限

### 2. 导入模块错误

确保已激活虚拟环境并安装了所有依赖：

```bash
pip install -r requirements.txt
```

### 3. 端口被占用

修改启动命令中的端口号：

```bash
uvicorn main:app --reload --port 8001
```

## 生产部署

1. 修改 `.env` 中的配置：
   - 设置强密码和密钥
   - 关闭DEBUG模式
   - 配置允许的CORS来源

2. 使用生产级WSGI服务器：

```bash
# 使用gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用uvicorn多进程
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

3. 配置反向代理（Nginx）

4. 配置HTTPS证书

## 许可证

MIT License


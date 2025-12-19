# SRM 供应商管理系统

## 项目概述

SRM（Supplier Relationship Management）供应商关系管理系统是一个基于前后端分离架构开发的企业级应用，旨在帮助企业高效管理供应商信息、采购流程和供应商关系，提升采购效率和供应商管理水平。

## 技术栈

### 后端

- **FastAPI**: 现代化的Python Web框架，提供高性能API开发体验
- **SQLAlchemy**: Python ORM框架，简化数据库操作
- **MySQL**: 关系型数据库，存储系统数据
- **JWT**: JSON Web Token，实现身份认证
- **Pydantic**: 数据验证库，确保数据完整性

### 前端

- **Vue 3**: 渐进式JavaScript框架，构建用户界面
- **Pinia**: Vue 3官方状态管理库
- **Vue Router**: 前端路由管理
- **Element Plus**: 基于Vue 3的UI组件库
- **Vite**: 现代化前端构建工具

## 核心功能模块

### 1. 供应商管理

- 供应商信息录入与维护
- 供应商资质审核流程
- 供应商等级评估
- 供应商分类管理
- 供应商参与项目历史记录

### 2. 项目管理

- 项目信息发布
- 项目需求管理
- 项目节点流程管理
- 项目评审功能
- 项目参与供应商管理

### 3. 报价管理

- 供应商参与报价功能
- 报价明细管理（包含品牌和型号）
- 报价提交、取消和重新报价
- 报价审核流程
- 中标管理

### 4. 权限管理

- RBAC（基于角色的访问控制）模型
- 用户、角色、权限三层权限体系
- 细粒度权限控制（资源+操作）
- 权限动态分配

### 5. 用户管理

- 用户信息维护
- 角色分配
- 密码策略管理
- 用户活动监控
- 自动退出机制（30分钟无操作）

### 6. 系统管理

- 仪表盘数据统计
- 操作日志记录
- 数据备份与恢复
- 系统参数配置

## 项目结构

```
SRM/
├── backend/                    # 后端代码
│   ├── app/                   # 应用核心
│   │   ├── api/               # API接口层
│   │   │   └── v1/            # API版本1
│   │   │       ├── endpoints/ # 各模块接口
│   │   │       └── api.py     # 路由聚合
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # 安全相关
│   │   │   └── deps.py        # 依赖注入
│   │   ├── db/                # 数据库
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模型
│   │   └── services/          # 业务逻辑
│   ├── alembic/               # 数据库迁移
│   ├── docs/                  # 后端文档
│   ├── main.py                # 应用入口
│   ├── requirements.txt       # 依赖包
│   └── init_db.py             # 数据库初始化
├── frontend/                  # 前端代码
│   ├── src/                   # 源代码
│   │   ├── api/               # API请求
│   │   ├── components/        # 组件
│   │   ├── composables/       # 组合式函数
│   │   ├── config/            # 配置
│   │   ├── constants/         # 常量
│   │   ├── layout/            # 布局
│   │   ├── router/            # 路由
│   │   ├── stores/            # 状态管理
│   │   ├── styles/            # 样式
│   │   ├── utils/             # 工具函数
│   │   ├── views/             # 页面
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── index.html             # HTML模板
│   ├── package.json           # 项目配置
│   └── vite.config.js         # Vite配置
└── .gitignore                 # Git忽略配置
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 后端安装与运行

1. **进入后端目录**

   ```bash
   cd backend
   ```

2. **创建虚拟环境**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

   编辑 `.env` 文件，配置数据库连接等信息。

5. **初始化数据库**

   ```bash
   python init_db.py
   ```

6. **启动后端服务**

   ```bash
   # 开发模式
   python main.py
   
   # 或使用uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### 前端安装与运行

1. **进入前端目录**

   ```bash
   cd frontend
   ```

2. **安装依赖**

   ```bash
   npm install
   ```

3. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   copy .env.example .env.development
   ```

   编辑 `.env.development` 文件，配置API地址等信息。

4. **启动前端服务**

   ```bash
   npm run dev
   ```

## API接口文档

后端提供完整的API文档，服务启动后可访问：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 主要API模块

| 模块       | 路径                 | 说明                             |
| ---------- | -------------------- | -------------------------------- |
| 认证管理   | `/api/v1/auth`       | 用户登录、登出、获取当前用户信息 |
| 用户管理   | `/api/v1/users`      | 用户列表、详情、创建、更新、删除 |
| 角色管理   | `/api/v1/roles`      | 角色列表、详情、创建、更新、删除 |
| 供应商管理 | `/api/v1/suppliers`  | 供应商信息管理                   |
| 项目管理   | `/api/v1/projects`   | 项目信息管理                     |
| 报价管理   | `/api/v1/quotations` | 报价信息管理                     |

## 权限管理

### RBAC模型

系统采用RBAC（基于角色的访问控制）模型，包含三层权限体系：

- **用户（User）**: 系统使用者
- **角色（Role）**: 权限的集合
- **权限（Permission）**: 具体的操作权限（资源+操作）

### 权限示例

| 资源      | 操作    | 权限代码          | 说明           |
| --------- | ------- | ----------------- | -------------- |
| supplier  | read    | supplier:read     | 查看供应商信息 |
| supplier  | create  | supplier:create   | 创建供应商     |
| project   | update  | project:update    | 更新项目信息   |
| quotation | approve | quotation:approve | 审核报价       |

## 开发指南

### 后端开发

1. **添加新模块**

   - 在 `app/models/` 创建数据模型
   - 在 `app/schemas/` 创建Pydantic模型
   - 在 `app/services/` 创建业务逻辑
   - 在 `app/api/v1/endpoints/` 创建API接口
   - 在 `app/api/v1/api.py` 注册路由

2. **数据库迁移**

   ```bash
   # 生成迁移脚本
   alembic revision --autogenerate -m "描述"
   
   # 执行迁移
   alembic upgrade head
   ```

### 前端开发

1. **添加新页面**
   - 在 `src/views/` 创建页面组件
   - 在 `src/router/` 配置路由
   - 在 `src/api/` 添加API请求
   - 在 `src/stores/` 添加状态管理（如需）

2. **组件开发**
   - 使用Composition API
   - 组件样式使用 `<style scoped>`
   - 可复用逻辑提取到 `composables/`

## 部署方案

### 环境准备

- 服务器：Ubuntu 22.04 LTS或24.04 LTS
- 数据库：MySQL 5.7+
- Web服务器：Nginx
- 应用服务器：Gunicorn + Uvicorn

### 后端部署

1. **安装依赖**

   ```bash
   apt-get update
   apt-get install -y python3-venv python3-pip mysql-server
   ```

2. **配置数据库**

   ```bash
   mysql -u root -p
   CREATE DATABASE srm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   CREATE USER 'srm_user'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON srm.* TO 'srm_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **部署应用**

   ```bash
   git clone <repository-url> /opt/srm
   cd /opt/srm/backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # 编辑.env配置
   alembic upgrade head
   ```

4. **启动应用（使用Gunicorn）**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

### 前端部署

1. **构建前端项目**

   ```bash
   cd /opt/srm/frontend
   npm install
   npm run build
   ```

2. **配置Nginx**

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /opt/srm/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

## 系统特性

### 安全性

- JWT身份认证
- 密码哈希存储
- 基于角色的权限控制
- 防止SQL注入
- 30分钟无操作自动退出

### 性能

- 数据库索引优化
- 异步API处理
- 前端懒加载
- 缓存机制

### 用户体验

- 响应式设计
- 直观的操作界面
- 实时数据更新
- 友好的错误提示

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 验证数据库配置是否正确
- 确认数据库用户权限

### 2. 前端无法访问后端API

- 检查CORS配置
- 确认后端服务是否运行
- 验证API地址配置

### 3. 登录后自动退出

- 系统实现了30分钟无操作自动退出机制
- 检查浏览器是否支持localStorage

### 4. 权限相关问题

- 确认用户角色配置
- 检查权限分配是否正确
- 超级管理员拥有所有权限

## 默认账号

### 管理员账号

- 用户名: `admin`
- 密码: `admin`
- ⚠️ 首次登录后请立即修改密码！

## 联系方式

如有问题或建议，请联系系统管理员。

---

**版本**: v1.0.0  
**最后更新**: 2025-11-07  
**版权所有**: SRM供应商管理系统开发团队# SRM 供应商管理系统

## 项目概述

SRM（Supplier Relationship Management）供应商关系管理系统是一个基于前后端分离架构开发的企业级应用，旨在帮助企业高效管理供应商信息、采购流程和供应商关系，提升采购效率和供应商管理水平。

## 技术栈

### 后端

- **FastAPI**: 现代化的Python Web框架，提供高性能API开发体验
- **SQLAlchemy**: Python ORM框架，简化数据库操作
- **MySQL**: 关系型数据库，存储系统数据
- **JWT**: JSON Web Token，实现身份认证
- **Pydantic**: 数据验证库，确保数据完整性

### 前端

- **Vue 3**: 渐进式JavaScript框架，构建用户界面
- **Pinia**: Vue 3官方状态管理库
- **Vue Router**: 前端路由管理
- **Element Plus**: 基于Vue 3的UI组件库
- **Vite**: 现代化前端构建工具

## 核心功能模块

### 1. 供应商管理

- 供应商信息录入与维护
- 供应商资质审核流程
- 供应商等级评估
- 供应商分类管理
- 供应商参与项目历史记录

### 2. 项目管理

- 项目信息发布
- 项目需求管理
- 项目节点流程管理
- 项目评审功能
- 项目参与供应商管理

### 3. 报价管理

- 供应商参与报价功能
- 报价明细管理（包含品牌和型号）
- 报价提交、取消和重新报价
- 报价审核流程
- 中标管理

### 4. 权限管理

- RBAC（基于角色的访问控制）模型
- 用户、角色、权限三层权限体系
- 细粒度权限控制（资源+操作）
- 权限动态分配

### 5. 用户管理

- 用户信息维护
- 角色分配
- 密码策略管理
- 用户活动监控
- 自动退出机制（30分钟无操作）

### 6. 系统管理

- 仪表盘数据统计
- 操作日志记录
- 数据备份与恢复
- 系统参数配置

## 项目结构

```
SRM/
├── backend/                    # 后端代码
│   ├── app/                   # 应用核心
│   │   ├── api/               # API接口层
│   │   │   └── v1/            # API版本1
│   │   │       ├── endpoints/ # 各模块接口
│   │   │       └── api.py     # 路由聚合
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # 安全相关
│   │   │   └── deps.py        # 依赖注入
│   │   ├── db/                # 数据库
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模型
│   │   └── services/          # 业务逻辑
│   ├── alembic/               # 数据库迁移
│   ├── docs/                  # 后端文档
│   ├── main.py                # 应用入口
│   ├── requirements.txt       # 依赖包
│   └── init_db.py             # 数据库初始化
├── frontend/                  # 前端代码
│   ├── src/                   # 源代码
│   │   ├── api/               # API请求
│   │   ├── components/        # 组件
│   │   ├── composables/       # 组合式函数
│   │   ├── config/            # 配置
│   │   ├── constants/         # 常量
│   │   ├── layout/            # 布局
│   │   ├── router/            # 路由
│   │   ├── stores/            # 状态管理
│   │   ├── styles/            # 样式
│   │   ├── utils/             # 工具函数
│   │   ├── views/             # 页面
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── index.html             # HTML模板
│   ├── package.json           # 项目配置
│   └── vite.config.js         # Vite配置
└── .gitignore                 # Git忽略配置
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 后端安装与运行

1. **进入后端目录**

   ```bash
   cd backend
   ```

2. **创建虚拟环境**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

   编辑 `.env` 文件，配置数据库连接等信息。

5. **初始化数据库**

   ```bash
   python init_db.py
   ```

6. **启动后端服务**

   ```bash
   # 开发模式
   python main.py
   
   # 或使用uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### 前端安装与运行

1. **进入前端目录**

   ```bash
   cd frontend
   ```

2. **安装依赖**

   ```bash
   npm install
   ```

3. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   copy .env.example .env.development
   ```

   编辑 `.env.development` 文件，配置API地址等信息。

4. **启动前端服务**

   ```bash
   npm run dev
   ```

## API接口文档

后端提供完整的API文档，服务启动后可访问：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 主要API模块

| 模块       | 路径                 | 说明                             |
| ---------- | -------------------- | -------------------------------- |
| 认证管理   | `/api/v1/auth`       | 用户登录、登出、获取当前用户信息 |
| 用户管理   | `/api/v1/users`      | 用户列表、详情、创建、更新、删除 |
| 角色管理   | `/api/v1/roles`      | 角色列表、详情、创建、更新、删除 |
| 供应商管理 | `/api/v1/suppliers`  | 供应商信息管理                   |
| 项目管理   | `/api/v1/projects`   | 项目信息管理                     |
| 报价管理   | `/api/v1/quotations` | 报价信息管理                     |

## 权限管理

### RBAC模型

系统采用RBAC（基于角色的访问控制）模型，包含三层权限体系：

- **用户（User）**: 系统使用者
- **角色（Role）**: 权限的集合
- **权限（Permission）**: 具体的操作权限（资源+操作）

### 权限示例

| 资源      | 操作    | 权限代码          | 说明           |
| --------- | ------- | ----------------- | -------------- |
| supplier  | read    | supplier:read     | 查看供应商信息 |
| supplier  | create  | supplier:create   | 创建供应商     |
| project   | update  | project:update    | 更新项目信息   |
| quotation | approve | quotation:approve | 审核报价       |

## 开发指南

### 后端开发

1. **添加新模块**

   - 在 `app/models/` 创建数据模型
   - 在 `app/schemas/` 创建Pydantic模型
   - 在 `app/services/` 创建业务逻辑
   - 在 `app/api/v1/endpoints/` 创建API接口
   - 在 `app/api/v1/api.py` 注册路由

2. **数据库迁移**

   ```bash
   # 生成迁移脚本
   alembic revision --autogenerate -m "描述"
   
   # 执行迁移
   alembic upgrade head
   ```

### 前端开发

1. **添加新页面**
   - 在 `src/views/` 创建页面组件
   - 在 `src/router/` 配置路由
   - 在 `src/api/` 添加API请求
   - 在 `src/stores/` 添加状态管理（如需）

2. **组件开发**
   - 使用Composition API
   - 组件样式使用 `<style scoped>`
   - 可复用逻辑提取到 `composables/`

## 部署方案

### 环境准备

- 服务器：Ubuntu 22.04 LTS或24.04 LTS
- 数据库：MySQL 5.7+
- Web服务器：Nginx
- 应用服务器：Gunicorn + Uvicorn

### 后端部署

1. **安装依赖**

   ```bash
   apt-get update
   apt-get install -y python3-venv python3-pip mysql-server
   ```

2. **配置数据库**

   ```bash
   mysql -u root -p
   CREATE DATABASE srm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   CREATE USER 'srm_user'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON srm.* TO 'srm_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **部署应用**

   ```bash
   git clone <repository-url> /opt/srm
   cd /opt/srm/backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # 编辑.env配置
   alembic upgrade head
   ```

4. **启动应用（使用Gunicorn）**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

### 前端部署

1. **构建前端项目**

   ```bash
   cd /opt/srm/frontend
   npm install
   npm run build
   ```

2. **配置Nginx**

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /opt/srm/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

## 系统特性

### 安全性

- JWT身份认证
- 密码哈希存储
- 基于角色的权限控制
- 防止SQL注入
- 30分钟无操作自动退出

### 性能

- 数据库索引优化
- 异步API处理
- 前端懒加载
- 缓存机制

### 用户体验

- 响应式设计
- 直观的操作界面
- 实时数据更新
- 友好的错误提示

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 验证数据库配置是否正确
- 确认数据库用户权限

### 2. 前端无法访问后端API

- 检查CORS配置
- 确认后端服务是否运行
- 验证API地址配置

### 3. 登录后自动退出

- 系统实现了30分钟无操作自动退出机制
- 检查浏览器是否支持localStorage

### 4. 权限相关问题

- 确认用户角色配置
- 检查权限分配是否正确
- 超级管理员拥有所有权限

## 默认账号

### 管理员账号

- 用户名: `admin`
- 密码: `admin`
- ⚠️ 首次登录后请立即修改密码！

## 联系方式

如有问题或建议，请联系系统管理员。

---

**版本**: v1.0.0  
**最后更新**: 2025-11-07  
**版权所有**: SRM供应商管理系统开发团队# SRM 供应商管理系统

## 项目概述

SRM（Supplier Relationship Management）供应商关系管理系统是一个基于前后端分离架构开发的企业级应用，旨在帮助企业高效管理供应商信息、采购流程和供应商关系，提升采购效率和供应商管理水平。

## 技术栈

### 后端

- **FastAPI**: 现代化的Python Web框架，提供高性能API开发体验
- **SQLAlchemy**: Python ORM框架，简化数据库操作
- **MySQL**: 关系型数据库，存储系统数据
- **JWT**: JSON Web Token，实现身份认证
- **Pydantic**: 数据验证库，确保数据完整性

### 前端

- **Vue 3**: 渐进式JavaScript框架，构建用户界面
- **Pinia**: Vue 3官方状态管理库
- **Vue Router**: 前端路由管理
- **Element Plus**: 基于Vue 3的UI组件库
- **Vite**: 现代化前端构建工具

## 核心功能模块

### 1. 供应商管理

- 供应商信息录入与维护
- 供应商资质审核流程
- 供应商等级评估
- 供应商分类管理
- 供应商参与项目历史记录

### 2. 项目管理

- 项目信息发布
- 项目需求管理
- 项目节点流程管理
- 项目评审功能
- 项目参与供应商管理

### 3. 报价管理

- 供应商参与报价功能
- 报价明细管理（包含品牌和型号）
- 报价提交、取消和重新报价
- 报价审核流程
- 中标管理

### 4. 权限管理

- RBAC（基于角色的访问控制）模型
- 用户、角色、权限三层权限体系
- 细粒度权限控制（资源+操作）
- 权限动态分配

### 5. 用户管理

- 用户信息维护
- 角色分配
- 密码策略管理
- 用户活动监控
- 自动退出机制（30分钟无操作）

### 6. 系统管理

- 仪表盘数据统计
- 操作日志记录
- 数据备份与恢复
- 系统参数配置

## 项目结构

```
SRM/
├── backend/                    # 后端代码
│   ├── app/                   # 应用核心
│   │   ├── api/               # API接口层
│   │   │   └── v1/            # API版本1
│   │   │       ├── endpoints/ # 各模块接口
│   │   │       └── api.py     # 路由聚合
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # 安全相关
│   │   │   └── deps.py        # 依赖注入
│   │   ├── db/                # 数据库
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模型
│   │   └── services/          # 业务逻辑
│   ├── alembic/               # 数据库迁移
│   ├── docs/                  # 后端文档
│   ├── main.py                # 应用入口
│   ├── requirements.txt       # 依赖包
│   └── init_db.py             # 数据库初始化
├── frontend/                  # 前端代码
│   ├── src/                   # 源代码
│   │   ├── api/               # API请求
│   │   ├── components/        # 组件
│   │   ├── composables/       # 组合式函数
│   │   ├── config/            # 配置
│   │   ├── constants/         # 常量
│   │   ├── layout/            # 布局
│   │   ├── router/            # 路由
│   │   ├── stores/            # 状态管理
│   │   ├── styles/            # 样式
│   │   ├── utils/             # 工具函数
│   │   ├── views/             # 页面
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── index.html             # HTML模板
│   ├── package.json           # 项目配置
│   └── vite.config.js         # Vite配置
└── .gitignore                 # Git忽略配置
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 后端安装与运行

1. **进入后端目录**

   ```bash
   cd backend
   ```

2. **创建虚拟环境**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

   编辑 `.env` 文件，配置数据库连接等信息。

5. **初始化数据库**

   ```bash
   python init_db.py
   ```

6. **启动后端服务**

   ```bash
   # 开发模式
   python main.py
   
   # 或使用uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### 前端安装与运行

1. **进入前端目录**

   ```bash
   cd frontend
   ```

2. **安装依赖**

   ```bash
   npm install
   ```

3. **配置环境变量**

   ```bash
   # 复制环境变量示例文件
   copy .env.example .env.development
   ```

   编辑 `.env.development` 文件，配置API地址等信息。

4. **启动前端服务**

   ```bash
   npm run dev
   ```

## API接口文档

后端提供完整的API文档，服务启动后可访问：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 主要API模块

| 模块       | 路径                 | 说明                             |
| ---------- | -------------------- | -------------------------------- |
| 认证管理   | `/api/v1/auth`       | 用户登录、登出、获取当前用户信息 |
| 用户管理   | `/api/v1/users`      | 用户列表、详情、创建、更新、删除 |
| 角色管理   | `/api/v1/roles`      | 角色列表、详情、创建、更新、删除 |
| 供应商管理 | `/api/v1/suppliers`  | 供应商信息管理                   |
| 项目管理   | `/api/v1/projects`   | 项目信息管理                     |
| 报价管理   | `/api/v1/quotations` | 报价信息管理                     |

## 权限管理

### RBAC模型

系统采用RBAC（基于角色的访问控制）模型，包含三层权限体系：

- **用户（User）**: 系统使用者
- **角色（Role）**: 权限的集合
- **权限（Permission）**: 具体的操作权限（资源+操作）

### 权限示例

| 资源      | 操作    | 权限代码          | 说明           |
| --------- | ------- | ----------------- | -------------- |
| supplier  | read    | supplier:read     | 查看供应商信息 |
| supplier  | create  | supplier:create   | 创建供应商     |
| project   | update  | project:update    | 更新项目信息   |
| quotation | approve | quotation:approve | 审核报价       |

## 开发指南

### 后端开发

1. **添加新模块**

   - 在 `app/models/` 创建数据模型
   - 在 `app/schemas/` 创建Pydantic模型
   - 在 `app/services/` 创建业务逻辑
   - 在 `app/api/v1/endpoints/` 创建API接口
   - 在 `app/api/v1/api.py` 注册路由

2. **数据库迁移**

   ```bash
   # 生成迁移脚本
   alembic revision --autogenerate -m "描述"
   
   # 执行迁移
   alembic upgrade head
   ```

### 前端开发

1. **添加新页面**
   - 在 `src/views/` 创建页面组件
   - 在 `src/router/` 配置路由
   - 在 `src/api/` 添加API请求
   - 在 `src/stores/` 添加状态管理（如需）

2. **组件开发**
   - 使用Composition API
   - 组件样式使用 `<style scoped>`
   - 可复用逻辑提取到 `composables/`

## 部署方案

### 环境准备

- 服务器：Ubuntu 22.04 LTS或24.04 LTS
- 数据库：MySQL 5.7+
- Web服务器：Nginx
- 应用服务器：Gunicorn + Uvicorn

### 后端部署

1. **安装依赖**

   ```bash
   apt-get update
   apt-get install -y python3-venv python3-pip mysql-server
   ```

2. **配置数据库**

   ```bash
   mysql -u root -p
   CREATE DATABASE srm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   CREATE USER 'srm_user'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON srm.* TO 'srm_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **部署应用**

   ```bash
   git clone <repository-url> /opt/srm
   cd /opt/srm/backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # 编辑.env配置
   alembic upgrade head
   ```

4. **启动应用（使用Gunicorn）**

   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
   ```

### 前端部署

1. **构建前端项目**

   ```bash
   cd /opt/srm/frontend
   npm install
   npm run build
   ```

2. **配置Nginx**

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /opt/srm/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

## 系统特性

### 安全性

- JWT身份认证
- 密码哈希存储
- 基于角色的权限控制
- 防止SQL注入
- 30分钟无操作自动退出

### 性能

- 数据库索引优化
- 异步API处理
- 前端懒加载
- 缓存机制

### 用户体验

- 响应式设计
- 直观的操作界面
- 实时数据更新
- 友好的错误提示

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 验证数据库配置是否正确
- 确认数据库用户权限

### 2. 前端无法访问后端API

- 检查CORS配置
- 确认后端服务是否运行
- 验证API地址配置

### 3. 登录后自动退出

- 系统实现了30分钟无操作自动退出机制
- 检查浏览器是否支持localStorage

### 4. 权限相关问题

- 确认用户角色配置
- 检查权限分配是否正确
- 超级管理员拥有所有权限

## 默认账号

### 管理员账号

- 用户名: `admin`
- 密码: `admin`
- ⚠️ 首次登录后请立即修改密码！

## 联系方式

如有问题或建议，请联系系统管理员。

---

**版本**: v1.0.0  
**最后更新**: 2025-11-07  
**版权所有**: SRM供应商管理系统开发团队

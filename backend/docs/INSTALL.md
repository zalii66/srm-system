# 详细安装说明

## 前置要求

### 1. Python 环境
- Python 3.8 或更高版本
- pip 包管理工具

**验证安装：**
```bash
python --version
pip --version
```

### 2. MySQL 数据库
- MySQL 5.7 或更高版本
- 确保MySQL服务正在运行

**验证安装：**
```bash
mysql --version
```

## 安装步骤

### 步骤 1: 下载项目

```bash
cd D:\Trae\SRM
```

### 步骤 2: 创建虚拟环境

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 步骤 3: 安装依赖包

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 步骤 4: 配置环境变量

在 `backend` 目录下创建 `.env` 文件：

**Windows (手动创建):**
1. 在backend目录右键 → 新建 → 文本文档
2. 重命名为 `.env` (注意开头的点)
3. 用记事本打开，粘贴以下内容：

```env
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=srm

# JWT配置
SECRET_KEY=your-secret-key-change-in-production-09876543210987654321
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
PROJECT_NAME=SRM供应商管理系统
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=True
```

**Linux/Mac:**
```bash
cat > .env << EOF
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=srm

# JWT配置
SECRET_KEY=your-secret-key-change-in-production-09876543210987654321
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
PROJECT_NAME=SRM供应商管理系统
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=True
EOF
```

⚠️ **重要提示：**
- 如果您的MySQL密码不是 `root`，请修改 `DB_PASSWORD`
- 生产环境请修改 `SECRET_KEY` 为强随机字符串

### 步骤 5: 确保MySQL服务运行

**Windows:**
```bash
# 检查服务状态
sc query MySQL80

# 如果未运行，启动服务
net start MySQL80
```

**Linux:**
```bash
# 检查服务状态
sudo systemctl status mysql

# 如果未运行，启动服务
sudo systemctl start mysql
```

**Mac:**
```bash
# 检查服务状态
brew services list

# 如果未运行，启动服务
brew services start mysql
```

### 步骤 6: 初始化数据库

```bash
python init_db.py
```

**预期输出：**
```
==================================================
SRM 数据库初始化工具
==================================================
正在创建数据库...
数据库 srm 创建成功！
正在创建数据表...
数据表创建成功！
正在初始化基础数据...
基础数据初始化成功！
默认管理员账号: admin
默认管理员密码: admin
请尽快修改默认密码！
==================================================
数据库初始化完成！
==================================================
```

### 步骤 7: 启动服务

```bash
python main.py
```

**预期输出：**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 步骤 8: 验证安装

1. **访问API文档：**
   - 打开浏览器访问: http://localhost:8000/api/v1/docs

2. **测试登录：**
   - 在API文档页面找到 `/api/v1/auth/login`
   - 点击 "Try it out"
   - 输入:
     ```
     username: admin
     password: admin123
     ```
   - 点击 "Execute"
   - 应该返回一个 `access_token`

3. **测试授权接口：**
   - 复制返回的 `access_token`
   - 点击页面右上角的 "Authorize" 按钮
   - 输入: `Bearer <your_token>`
   - 点击 "Authorize"
   - 现在可以测试其他需要认证的接口了

## 常见问题排查

### 问题 1: 无法创建数据库

**错误信息：**
```
Access denied for user 'root'@'localhost'
```

**解决方案：**
1. 检查MySQL是否正在运行
2. 验证用户名和密码是否正确
3. 确保root用户有创建数据库的权限

```sql
-- 登录MySQL
mysql -u root -p

-- 授予权限
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### 问题 2: 端口被占用

**错误信息：**
```
[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): 
通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

**解决方案：**
修改启动端口：
```bash
uvicorn main:app --reload --port 8001
```

### 问题 3: 模块导入错误

**错误信息：**
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案：**
1. 确认虚拟环境已激活
2. 重新安装依赖：
```bash
pip install -r requirements.txt
```

### 问题 4: 数据库连接超时

**错误信息：**
```
Can't connect to MySQL server on '127.0.0.1'
```

**解决方案：**
1. 检查MySQL服务是否运行
2. 检查防火墙设置
3. 验证端口3306是否可访问

### 问题 5: 字符编码问题

**错误信息：**
```
Incorrect string value: '\xE4\xB8\xAD\xE6\x96\x87'
```

**解决方案：**
确保数据库使用 utf8mb4 字符集：
```sql
ALTER DATABASE srm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

## Windows 快捷安装

如果您使用Windows系统，可以使用提供的批处理脚本：

### 1. 自动安装环境
双击运行 `setup.bat`

### 2. 手动创建.env文件
按照步骤4创建 `.env` 文件

### 3. 初始化数据库
双击运行 `init_db.bat`

### 4. 启动服务
双击运行 `run.bat`

## 生产环境部署

### 1. 修改配置

编辑 `.env` 文件：
```env
# 关闭调试模式
DEBUG=False

# 使用强密钥（至少32个随机字符）
SECRET_KEY=your-very-long-and-random-secret-key-here

# 增加token有效期（可选）
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 2. 使用生产级服务器

安装 Gunicorn：
```bash
pip install gunicorn
```

启动服务：
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

参数说明：
- `-w 4`: 4个工作进程
- `-k uvicorn.workers.UvicornWorker`: 使用Uvicorn worker
- `--bind 0.0.0.0:8000`: 绑定地址和端口

### 3. 配置Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. 配置HTTPS

使用Let's Encrypt免费证书：
```bash
sudo certbot --nginx -d your-domain.com
```

### 5. 配置系统服务

创建systemd服务文件 `/etc/systemd/system/srm.service`：

```ini
[Unit]
Description=SRM API Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start srm
sudo systemctl enable srm
```

## 下一步

安装完成后，您可以：

1. 📖 阅读 [README.md](README.md) 了解更多功能
2. 🚀 查看 [QUICKSTART.md](QUICKSTART.md) 快速开始使用
3. 🏗️ 参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 了解项目结构
4. 🔧 开始开发前端应用

**默认管理员账号：**
- 用户名: `admin`
- 密码: `admin`
- ⚠️ 登录后请立即修改密码！

祝您使用愉快！ 🎉


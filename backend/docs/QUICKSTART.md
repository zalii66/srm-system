# 快速开始指南

## Windows 用户

### 一键安装和启动

1. **安装环境**
```bash
setup.bat
```

2. **初始化数据库**
```bash
init_db.bat
```

3. **启动服务**
```bash
run.bat
```

### 默认管理员账号
- 用户名: `admin`
- 密码: `admin`

⚠️ **首次登录后请立即修改密码！**

### 访问地址
- API文档: http://localhost:8000/api/v1/docs
- 健康检查: http://localhost:8000/health

---

## Linux/Mac 用户

### 1. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接
```

### 4. 初始化数据库
```bash
python init_db.py
```

### 5. 启动服务
```bash
python main.py
# 或
uvicorn main:app --reload
```

---

## 测试API

### 1. 登录获取Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

返回:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. 获取当前用户信息

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 创建新用户

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com",
    "full_name": "测试用户",
    "role_ids": []
  }'
```

---

## 常见问题

### Q1: 数据库连接失败？
**A**: 检查MySQL服务是否启动，确认 `.env` 配置正确

### Q2: 端口8000被占用？
**A**: 修改启动命令，使用其他端口:
```bash
uvicorn main:app --reload --port 8001
```

### Q3: 导入模块错误？
**A**: 确保已激活虚拟环境并安装依赖:
```bash
pip install -r requirements.txt
```

---

## 下一步

- 查看完整文档: [README.md](README.md)
- 浏览API文档: http://localhost:8000/api/v1/docs
- 开始开发前端: 参考Vue3前端开发文档


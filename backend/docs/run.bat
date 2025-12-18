@echo off
chcp 65001
echo ===================================
echo SRM 供应商管理系统 - 后端服务启动
echo ===================================
echo.

REM 检查虚拟环境是否激活
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo [信息] 正在启动服务...
echo [信息] API文档地址: http://localhost:8001/api/v1/docs
echo.

REM 启动服务（两种方式都可以）
REM 方式1: 直接运行 main.py
REM python main.py

REM 方式2: 使用 uvicorn 命令（推荐，支持热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8001

pause


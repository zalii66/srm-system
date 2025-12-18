@echo off
chcp 65001
echo ===================================
echo SRM 供应商管理系统 - 环境安装
echo ===================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [2/5] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/5] 升级pip...
python -m pip install --upgrade pip

echo [4/5] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖包失败
    pause
    exit /b 1
)

echo [5/5] 配置环境变量...
if not exist ".env" (
    echo [警告] .env 文件不存在，需要手动创建
    echo [提示] 可以参考 .env.example 文件
)

echo.
echo ===================================
echo 环境安装完成！
echo ===================================
echo.
echo 下一步：
echo 1. 确保MySQL服务已启动
echo 2. 确认 .env 文件配置正确（如不存在请创建）
echo 3. 运行 init_db.bat 初始化数据库
echo 4. 运行 run.bat 启动服务
echo.
pause


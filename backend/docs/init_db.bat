@echo off
chcp 65001
echo ===================================
echo SRM 供应商管理系统 - 数据库初始化
echo ===================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查环境变量文件
if not exist ".env" (
    echo [错误] .env 文件不存在，请先创建配置文件
    echo [提示] 可以参考 .env.example 文件
    pause
    exit /b 1
)

echo [警告] 此操作将初始化数据库，如果数据库已存在将跳过创建
echo.
set /p confirm="确认继续？(y/n): "
if /i not "%confirm%"=="y" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo [信息] 正在初始化数据库...
python init_db.py

echo.
pause


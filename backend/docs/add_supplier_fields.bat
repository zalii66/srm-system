@echo off
chcp 65001 >nul
echo [信息] 开始执行数据库迁移...
echo.

cd /d %~dp0

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查pymysql是否安装
python -c "import pymysql" 2>nul
if errorlevel 1 (
    echo [信息] 正在安装 pymysql...
    pip install pymysql
)

REM 执行迁移脚本
python add_supplier_fields.py

echo.
echo [信息] 迁移完成！
pause

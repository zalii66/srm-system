@echo off
chcp 65001
echo ===================================
echo SRM - 重置数据库（删除并重新创建）
echo ===================================
echo.
echo [警告] 此操作将删除所有数据！
echo.

REM 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

set /p confirm="确认删除并重新创建数据库？(yes/no): "
if /i not "%confirm%"=="yes" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo [1/2] 删除旧数据库...
python -c "from sqlalchemy import create_engine, text; from app.core.config import settings; engine_url = f'mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}'; engine = create_engine(engine_url); conn = engine.connect(); conn.execute(text(f'DROP DATABASE IF EXISTS {settings.DB_NAME}')); conn.commit(); conn.close(); print('旧数据库已删除')"

echo.
echo [2/2] 重新初始化数据库...
python init_db.py

echo.
pause


@echo off
chcp 65001
echo ===================================
echo 修复 bcrypt 版本兼容性问题
echo ===================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo [1/3] 卸载旧版本...
pip uninstall -y bcrypt passlib

echo.
echo [2/3] 安装兼容版本...
pip install bcrypt==3.2.2
pip install passlib[bcrypt]==1.7.4

echo.
echo [3/3] 验证安装...
python -c "from passlib.hash import bcrypt; print('✓ bcrypt 工作正常')"

if errorlevel 0 (
    echo.
    echo ===================================
    echo ✓ 修复完成！
    echo ===================================
    echo.
    echo 下一步：运行 init_db.bat 重新初始化数据库
    echo.
) else (
    echo.
    echo [错误] 修复失败，请手动安装
    echo.
)

pause


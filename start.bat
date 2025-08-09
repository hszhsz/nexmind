@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 启动 NexMind 应用...
echo.

REM 检查是否存在 .env 文件
if not exist "backend\.env" (
    echo ⚠️  未找到 backend\.env 文件
    echo 📝 正在从模板创建 .env 文件...
    copy "backend\.env.example" "backend\.env" >nul
    echo ✅ 已创建 backend\.env 文件，请编辑该文件并配置您的API密钥
    echo 📖 配置说明：
    echo    - 需要配置 DeepSeek API密钥 ^(OPENAI_API_KEY^)
    echo    - 基础URL已设置为 https://api.deepseek.com
    echo    - 模型已设置为 deepseek-chat
    echo.
    echo ⏸️  请配置完成后重新运行此脚本
    pause
    exit /b 1
)

REM 检查 uv 是否安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 uv，请先安装 uv
    echo 💡 安装命令: powershell -c "irm https://astral.sh/uv/install.ps1 ^| iex"
    pause
    exit /b 1
)

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo 📦 安装前端依赖...
    cd frontend
    npm install
    cd ..
)

REM 检查后端依赖
echo 🐍 检查Python环境和后端依赖...
cd backend
if not exist ".venv" (
    echo 📦 安装后端依赖...
    uv sync
) else (
    echo ✅ 后端依赖已安装
)
cd ..

REM 创建日志目录
if not exist "backend\logs" mkdir "backend\logs"

echo ✅ 依赖检查完成
echo.
echo 🌟 启动服务...
echo    - 前端: http://localhost:3000
echo    - 后端API: http://localhost:8000
echo    - API文档: http://localhost:8000/docs
echo.
echo 📝 使用 Ctrl+C 停止所有服务
echo.

REM 启动后端服务
echo 🔧 启动后端服务...
cd backend
start /b "NexMind Backend" uv run python main.py
cd ..

REM 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端服务
echo 🎨 启动前端服务...
cd frontend
start /b "NexMind Frontend" npm run dev
cd ..

echo.
echo 🎉 NexMind 应用启动成功！
echo 📱 前端: http://localhost:3000
echo 🔧 后端: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo.
echo 💡 提示: 关闭此窗口将停止所有服务
echo.
echo 按任意键退出...
pause >nul

REM 清理进程
taskkill /f /im "node.exe" >nul 2>&1
taskkill /f /im "python.exe" >nul 2>&1
echo 👋 再见！
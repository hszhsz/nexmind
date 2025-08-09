#!/bin/bash

# NexMind 启动脚本

echo "🚀 启动 NexMind 应用..."

# 检查是否存在 .env 文件
if [ ! -f "backend/.env" ]; then
    echo "⚠️  未找到 backend/.env 文件"
    echo "📝 正在从模板创建 .env 文件..."
    cp backend/.env.example backend/.env
    echo "✅ 已创建 backend/.env 文件，请编辑该文件并配置您的API密钥"
    echo "📖 配置说明："
    echo "   - 至少需要配置一个AI模型API密钥 (OPENAI_API_KEY 或 ANTHROPIC_API_KEY)"
    echo "   - 可选配置搜索引擎API密钥 (TAVILY_API_KEY 或 BRAVE_API_KEY)"
    echo ""
    echo "⏸️  请配置完成后重新运行此脚本"
    exit 1
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 检查后端依赖
echo "🐍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.12+"
    exit 1
fi

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
pip install -r requirements.txt
cd ..

# 创建日志目录
mkdir -p backend/logs

echo "✅ 依赖安装完成"
echo ""
echo "🌟 启动服务..."
echo "   - 前端: http://localhost:3000"
echo "   - 后端API: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo ""

# 启动后端服务（后台运行）
echo "🔧 启动后端服务..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 NexMind 应用启动成功！"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap 'echo "\n🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
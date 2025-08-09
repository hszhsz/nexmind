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
    echo "   - 需要配置 DeepSeek API密钥 (OPENAI_API_KEY)"
    echo "   - 基础URL已设置为 https://api.deepseek.com"
    echo "   - 模型已设置为 deepseek-chat"
    echo ""
    echo "⏸️  请配置完成后重新运行此脚本"
    exit 1
fi

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ 未找到 uv，请先安装 uv"
    echo "💡 安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
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
echo "🐍 检查Python环境和后端依赖..."
cd backend
if [ ! -d ".venv" ]; then
    echo "📦 安装后端依赖..."
    uv sync
else
    echo "✅ 后端依赖已安装"
fi
cd ..

# 创建日志目录
mkdir -p backend/logs

echo "✅ 依赖检查完成"
echo ""
echo "🌟 启动服务..."
echo "   - 前端: http://localhost:3000"
echo "   - 后端API: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "📝 使用 Ctrl+C 停止所有服务"
echo ""
echo ""

# 信号处理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 后端服务已停止"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 前端服务已停止"
    fi
    echo "👋 再见！"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 启动后端服务（后台运行）
echo "🔧 启动后端服务..."
cd backend
uv run python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端是否成功启动
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 NexMind 应用启动成功！"
echo "📱 前端: http://localhost:3000"
echo "🔧 后端: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "💡 提示: 按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
while true; do
    sleep 1
    # 检查进程是否还在运行
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ 后端服务意外停止"
        cleanup
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ 前端服务意外停止"
        cleanup
    fi
done
# NexMind - AI-Powered Enterprise Analysis Platform

🚀 **NexMind** 是一个基于AI的企业分析平台，利用先进的大语言模型为用户提供智能的企业分析、市场研究和商业洞察服务。

## ✨ 主要功能

- 🤖 **智能对话**: 基于DeepSeek模型的自然语言交互
- 📊 **企业分析**: 深度企业信息分析和市场研究
- 📈 **报告生成**: 自动生成专业的分析报告
- 🔍 **信息检索**: 智能搜索和信息聚合
- 🎨 **现代UI**: 基于Next.js和Tailwind CSS的响应式界面

## 🛠️ 技术栈

### 前端
- **Next.js 14** - React框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **React Hooks** - 状态管理

### 后端
- **FastAPI** - 高性能Python Web框架
- **LangChain** - AI应用开发框架
- **DeepSeek API** - 大语言模型服务
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI服务器

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- npm 或 yarn
- uv (Python包管理器)

### 安装uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用pip
pip install uv
```

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/hszhsz/nexmind.git
   cd nexmind
   ```

2. **后端设置**
   ```bash
   cd backend
   uv sync
   cp .env.example .env
   ```

3. **配置环境变量**
   
   编辑 `backend/.env` 文件，设置以下配置：
   ```env
   # DeepSeek API配置
   OPENAI_API_KEY=your_deepseek_api_key
   OPENAI_BASE_URL=https://api.deepseek.com
   OPENAI_MODEL=deepseek-chat
   OPENAI_TEMPERATURE=0.1
   OPENAI_MAX_TOKENS=4000
   
   # CORS配置
   ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
   ```

4. **前端设置**
   ```bash
   cd ../frontend
   npm install
   ```

5. **启动服务**
   
   **启动后端** (在 `backend` 目录):
   ```bash
   mkdir -p logs
   uv run python main.py
   ```
   
   **启动前端** (在 `frontend` 目录):
   ```bash
   npm run dev
   ```

6. **访问应用**
   
   打开浏览器访问: http://localhost:3000

## 📁 项目结构

```
nexmind/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心模块
│   │   │   ├── agent.py    # AI Agent
│   │   │   └── config.py   # 配置管理
│   │   └── tools/          # AI工具
│   │       ├── analysis.py # 分析工具
│   │       └── report.py   # 报告生成
│   ├── main.py             # 应用入口
│   ├── pyproject.toml      # Python依赖和项目配置
│   └── .env.example        # 环境变量模板
├── frontend/               # 前端应用
│   ├── app/
│   │   ├── page.tsx        # 主页面
│   │   ├── layout.tsx      # 布局组件
│   │   └── globals.css     # 全局样式
│   ├── package.json        # Node.js依赖
│   └── next.config.js      # Next.js配置
└── docker-compose.yml      # Docker编排
```

## 🔧 API文档

### 主要端点

- `GET /api/health` - 健康检查
- `POST /api/chat` - 智能对话接口

### 请求示例

```bash
# 健康检查
curl http://localhost:8000/api/health

# 发送聊天消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "请分析一下腾讯公司的业务情况"}'
```

## 🐳 Docker部署

使用Docker Compose一键部署：

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的AI模型服务
- [LangChain](https://langchain.com/) - AI应用开发框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Next.js](https://nextjs.org/) - React生产框架

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [https://github.com/hszhsz/nexmind/issues](https://github.com/hszhsz/nexmind/issues)
- Email: [your-email@example.com](mailto:your-email@example.com)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
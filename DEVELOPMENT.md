# NexMind 开发指南

## 项目概述

NexMind是一个为金融投资者提供中国公司详细资料的AI驱动web应用。系统采用plan-and-execute范式的AI Agent，能够智能分析企业信息并生成comprehensive的分析报告。

## 技术架构

### 前端技术栈
- **React 18** - 用户界面框架
- **Next.js 14** - 全栈React框架
- **Tailwind CSS** - 样式框架
- **TypeScript** - 类型安全的JavaScript
- **Lucide React** - 图标库

### 后端技术栈
- **Python 3.12+** - 编程语言
- **FastAPI** - 现代Web框架
- **LangChain** - LLM应用开发框架
- **LangGraph** - 工作流编排
- **Pydantic** - 数据验证
- **SQLite** - 数据库（可扩展为PostgreSQL）

## 快速开始

### 1. 环境要求

- **Node.js**: 18.0+
- **Python**: 3.12+
- **npm**: 8.0+
- **pip**: 最新版本

### 2. 克隆项目

```bash
# 项目已在当前目录
cd nexmind
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑配置文件
vim backend/.env  # 或使用其他编辑器
```

**必需配置：**
- `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY` (至少配置一个)
- 其他配置可保持默认值

### 4. 一键启动

```bash
# 使用启动脚本（推荐）
./start.sh
```

### 5. 手动启动

**启动后端：**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**启动前端：**
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
nexmind/
├── frontend/                 # Next.js前端应用
│   ├── app/                 # App Router页面
│   │   ├── globals.css      # 全局样式
│   │   ├── layout.tsx       # 根布局
│   │   └── page.tsx         # 主页面
│   ├── components/          # React组件（待扩展）
│   ├── public/              # 静态资源
│   ├── package.json         # 前端依赖
│   ├── tailwind.config.js   # Tailwind配置
│   ├── next.config.js       # Next.js配置
│   └── Dockerfile           # 前端Docker配置
├── backend/                 # Python后端应用
│   ├── app/                 # 应用核心代码
│   │   ├── core/            # 核心模块
│   │   │   ├── config.py    # 配置管理
│   │   │   └── agent.py     # AI Agent核心
│   │   ├── tools/           # 工具模块
│   │   │   ├── search.py    # 搜索工具
│   │   │   ├── analysis.py  # 分析工具
│   │   │   └── report.py    # 报告生成
│   │   └── api/             # API路由
│   │       └── routes.py    # 路由定义
│   ├── main.py              # 应用入口
│   ├── requirements.txt     # Python依赖
│   ├── .env.example         # 环境变量模板
│   └── Dockerfile           # 后端Docker配置
├── docker-compose.yml       # Docker编排
├── start.sh                 # 启动脚本
├── README.md                # 项目说明
└── DEVELOPMENT.md           # 开发指南
```

## 核心功能

### AI Agent工作流

1. **规划阶段 (Planner)**
   - 分析用户查询
   - 制定分析计划
   - 确定执行步骤

2. **搜索阶段 (Searcher)**
   - 基于计划执行信息搜索
   - 支持多种搜索引擎
   - 收集相关企业信息

3. **分析阶段 (Analyzer)**
   - 财务数据分析
   - 行业地位评估
   - 竞争环境分析
   - 风险评估

4. **报告阶段 (Reporter)**
   - 生成综合分析报告
   - 提供投资建议
   - 格式化输出

### 支持的搜索引擎

- **DuckDuckGo** (默认，无需API密钥)
- **Tavily** (需要API密钥)
- **Brave Search** (需要API密钥)

### 支持的AI模型

- **OpenAI GPT-4** (推荐)
- **Anthropic Claude-3**

## API文档

启动后端服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

- `POST /api/chat` - 聊天对话
- `GET /api/health` - 健康检查
- `GET /api/conversations/{id}/history` - 获取对话历史
- `DELETE /api/conversations/{id}` - 清除对话
- `GET /api/system/info` - 系统信息
- `GET /api/suggestions` - 搜索建议
- `POST /api/export/report` - 导出报告

## 开发指南

### 前端开发

1. **组件开发**
   - 使用TypeScript
   - 遵循React Hooks模式
   - 使用Tailwind CSS样式

2. **状态管理**
   - 使用React内置状态管理
   - 可扩展为Redux Toolkit

3. **API调用**
   - 使用axios进行HTTP请求
   - 统一错误处理

### 后端开发

1. **添加新工具**
   ```python
   # 在 app/tools/ 目录下创建新工具
   class NewTool:
       async def process(self, data):
           # 实现工具逻辑
           pass
   ```

2. **扩展AI Agent**
   ```python
   # 在 agent.py 中添加新节点
   async def new_node(self, state: AgentState) -> AgentState:
       # 实现节点逻辑
       return state
   ```

3. **添加API端点**
   ```python
   # 在 routes.py 中添加新路由
   @chat_router.post("/new-endpoint")
   async def new_endpoint():
       return {"message": "success"}
   ```

## 部署指南

### Docker部署

```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 停止服务
docker-compose down
```

### 生产环境配置

1. **环境变量**
   - 设置 `DEBUG=False`
   - 配置生产数据库
   - 设置安全的API密钥

2. **性能优化**
   - 启用Redis缓存
   - 配置负载均衡
   - 优化数据库查询

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本 (需要3.12+)
   - 确认API密钥配置正确
   - 查看日志文件 `backend/logs/nexmind.log`

2. **前端无法连接后端**
   - 确认后端服务运行在8000端口
   - 检查CORS配置
   - 验证API代理设置

3. **AI响应异常**
   - 检查API密钥有效性
   - 确认网络连接正常
   - 查看后端日志

### 日志查看

```bash
# 查看后端日志
tail -f backend/logs/nexmind.log

# 查看Docker日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 贡献指南

1. **代码规范**
   - Python: 遵循PEP 8
   - TypeScript: 使用ESLint配置
   - 提交前运行测试

2. **提交流程**
   - 创建功能分支
   - 编写测试用例
   - 提交Pull Request

## 许可证

MIT License - 详见LICENSE文件

## 支持

如有问题，请提交Issue或联系开发团队。
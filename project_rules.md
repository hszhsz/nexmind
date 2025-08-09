# 项目规则

## 依赖管理
- 使用 `uv` 管理 Python 依赖
- 后端依赖配置在 `backend/pyproject.toml` 中
- 前端依赖使用 npm 管理，配置在 `frontend/package.json` 中

## 启动方式
- 使用 `start.sh` 脚本启动前端和后端服务
- 该脚本会同时启动前端开发服务器和后端 API 服务
- 确保在项目根目录下执行启动脚本

## 开发环境
- 前端：Next.js + TypeScript + Tailwind CSS
- 后端：FastAPI + Python
- 容器化：支持 Docker 和 docker-compose

## 注意事项
- 开发前请确保已安装 uv 和 Node.js
- 首次运行前需要安装依赖
- 遵循项目的代码规范和目录结构
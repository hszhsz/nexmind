import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os
import json
import asyncio

# 导入AI Agent
from app.core.agent import CompanyAnalysisAgent
from app.core.config import validate_api_keys

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 验证API密钥配置
try:
    validate_api_keys()
    logger.info("API密钥配置验证成功")
except ValueError as e:
    logger.error(f"API密钥配置错误: {e}")
    # 在开发环境中继续运行，但会在调用时报错

# 创建FastAPI应用
app = FastAPI(
    title="NexMind API",
    description="AI-powered Chinese company analysis platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 初始化AI Agent
agent = None
try:
    agent = CompanyAnalysisAgent()
    logger.info("AI Agent初始化成功")
except Exception as e:
    logger.error(f"AI Agent初始化失败: {e}")
    agent = None

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求和响应模型
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to NexMind API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": True
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """聊天API端点"""
    try:
        # 检查AI Agent是否可用
        if agent is None:
            return ChatResponse(
                response="抱歉，AI服务暂时不可用。请检查API密钥配置或稍后重试。",
                conversation_id=request.conversation_id or "default",
                timestamp=datetime.now().isoformat()
            )
        
        # 调用AI Agent处理查询
        logger.info(f"处理用户查询: {request.message}")
        
        # 添加超时控制
        try:
            result = await asyncio.wait_for(
                agent.process_query(
                    query=request.message,
                    conversation_id=request.conversation_id or "default"
                ),
                timeout=300  # 5分钟超时
            )
        except asyncio.TimeoutError:
            logger.warning(f"查询处理超时: {request.message}")
            return ChatResponse(
                response="抱歉，您的查询处理时间过长，请尝试简化查询或稍后重试。",
                conversation_id=request.conversation_id or "default",
                timestamp=datetime.now().isoformat()
            )
        
        return ChatResponse(
            response=result["content"],
            conversation_id=request.conversation_id or "default",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"处理聊天请求时发生错误: {e}")
        return ChatResponse(
            response=f"抱歉，处理您的请求时发生了错误：{str(e)}。请稍后重试或联系技术支持。",
            conversation_id=request.conversation_id or "default",
            timestamp=datetime.now().isoformat()
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
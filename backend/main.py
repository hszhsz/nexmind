import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os
import json
import asyncio
import re

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 输入验证函数
def is_company_related_query(message: str) -> bool:
    """
    判断用户输入是否与公司分析相关
    """
    # 转换为小写进行匹配
    message_lower = message.lower().strip()
    
    # 简单的问候语和无关内容
    greetings = [
        "你好", "hello", "hi", "嗨", "您好", "早上好", "下午好", "晚上好",
        "谢谢", "thank you", "thanks", "再见", "bye", "goodbye"
    ]
    
    # 如果是简单问候语，返回False
    if message_lower in greetings:
        return False
    
    # 公司相关关键词
    company_keywords = [
        "公司", "企业", "集团", "股份", "有限公司", "corporation", "company", "inc",
        "分析", "财务", "营收", "利润", "股价", "市值", "业务", "产品", "服务",
        "竞争", "市场", "行业", "投资", "风险", "发展", "战略", "管理",
        "腾讯", "阿里巴巴", "百度", "字节跳动", "美团", "京东", "小米", "华为",
        "苹果", "微软", "谷歌", "亚马逊", "特斯拉", "meta", "netflix"
    ]
    
    # 检查是否包含公司相关关键词
    for keyword in company_keywords:
        if keyword in message_lower:
            return True
    
    # 检查是否包含公司名称模式（如：XX公司、XX集团等）
    company_patterns = [
        r'\w+公司',
        r'\w+集团', 
        r'\w+企业',
        r'\w+股份',
        r'\w+科技',
        r'\w+控股'
    ]
    
    for pattern in company_patterns:
        if re.search(pattern, message):
            return True
    
    return False

# 请求和响应模型
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

class AgentStepResponse(BaseModel):
    type: str  # 'step' or 'final'
    step_name: str
    description: str
    status: str  # 'running', 'completed', 'error'
    timestamp: str
    data: Optional[Dict[str, Any]] = None

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
        
        # 验证用户输入是否与公司分析相关
        if not is_company_related_query(request.message):
            return ChatResponse(
                response="您好！我是NexMind企业分析助手，专门为您提供公司和企业相关的分析服务。\n\n请您输入想要分析的公司名称或相关问题，例如：\n• 帮我分析一下腾讯公司\n• 阿里巴巴的财务状况如何\n• 比较苹果和微软的竞争优势\n\n如果您确实需要进行企业分析，请重新输入您的问题。",
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

@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """流式聊天API端点"""
    async def generate_response():
        try:
            # 检查AI Agent是否可用
            if agent is None:
                yield f"data: {json.dumps({'type': 'error', 'message': 'AI服务暂时不可用'}, ensure_ascii=False)}\n\n"
                return
            
            # 验证用户输入
            if not is_company_related_query(request.message):
                yield f"data: {json.dumps({'type': 'final', 'response': '您好！我是NexMind企业分析助手，专门为您提供公司和企业相关的分析服务。请输入想要分析的公司名称或相关问题。'}, ensure_ascii=False)}\n\n"
                return
            
            # 发送开始信号
            description = f'正在分析"{request.message}"...'
            yield f"data: {json.dumps({'type': 'step', 'step_name': '开始分析', 'description': description, 'status': 'running', 'timestamp': datetime.now().isoformat()}, ensure_ascii=False)}\n\n"
            
            # 调用Agent处理查询并流式返回步骤
            async for step_data in agent.process_query_stream(
                query=request.message,
                conversation_id=request.conversation_id or "default"
            ):
                yield f"data: {json.dumps(step_data, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            logger.error(f"流式处理聊天请求时发生错误: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'处理请求时发生错误: {str(e)}'}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
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
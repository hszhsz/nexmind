from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

# 创建路由器
chat_router = APIRouter(prefix="/api", tags=["chat"])

# 请求和响应模型
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    status: str = "success"
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

# 健康检查路由
@chat_router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services={
            "api": "running",
            "ai_agent": "ready",
            "search": "available"
        }
    )

# 聊天历史存储（简单内存存储，生产环境应使用数据库）
conversation_history: Dict[str, List[Dict[str, Any]]] = {}

def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """获取对话历史"""
    return conversation_history.get(conversation_id, [])

def add_to_conversation_history(conversation_id: str, message: Dict[str, Any]):
    """添加消息到对话历史"""
    if conversation_id not in conversation_history:
        conversation_history[conversation_id] = []
    
    conversation_history[conversation_id].append(message)
    
    # 限制历史记录长度
    if len(conversation_history[conversation_id]) > 50:
        conversation_history[conversation_id] = conversation_history[conversation_id][-50:]

# 对话管理路由
@chat_router.get("/conversations/{conversation_id}/history")
async def get_conversation(
    conversation_id: str,
    limit: Optional[int] = 20
):
    """获取对话历史"""
    try:
        history = get_conversation_history(conversation_id)
        
        # 限制返回数量
        if limit:
            history = history[-limit:]
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "total_messages": len(conversation_history.get(conversation_id, [])),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取对话历史时发生错误: {e}")
        raise HTTPException(status_code=500, detail="获取对话历史失败")

@chat_router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """清除对话历史"""
    try:
        if conversation_id in conversation_history:
            del conversation_history[conversation_id]
        
        return {
            "message": f"对话 {conversation_id} 已清除",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"清除对话历史时发生错误: {e}")
        raise HTTPException(status_code=500, detail="清除对话历史失败")

# 系统信息路由
@chat_router.get("/system/info")
async def get_system_info():
    """获取系统信息"""
    try:
        from ..core.config import settings
        
        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "search_engine": settings.search_engine,
            "ai_model": settings.openai_model if settings.openai_api_key else settings.anthropic_model,
            "features": [
                "企业基本信息分析",
                "财务数据分析",
                "行业地位评估",
                "竞争环境分析",
                "风险评估",
                "投资建议生成"
            ],
            "supported_queries": [
                "公司基本信息查询",
                "财务状况分析",
                "行业地位评估",
                "投资价值分析",
                "风险评估报告"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取系统信息时发生错误: {e}")
        raise HTTPException(status_code=500, detail="获取系统信息失败")

# 搜索建议路由
@chat_router.get("/suggestions")
async def get_search_suggestions(query: Optional[str] = None):
    """获取搜索建议"""
    try:
        # 基础建议
        base_suggestions = [
            "腾讯控股有限公司分析",
            "阿里巴巴集团财务状况",
            "比亚迪股份投资价值",
            "中国平安保险分析",
            "贵州茅台行业地位",
            "美团点评竞争优势",
            "小米集团风险评估",
            "京东集团发展前景"
        ]
        
        # 如果有查询词，生成相关建议
        suggestions = base_suggestions
        if query and len(query.strip()) > 0:
            query_suggestions = [
                f"{query}基本信息",
                f"{query}财务分析",
                f"{query}投资价值",
                f"{query}行业地位",
                f"{query}风险评估"
            ]
            suggestions = query_suggestions + base_suggestions
        
        return {
            "suggestions": suggestions[:8],
            "categories": [
                "基本信息",
                "财务分析",
                "行业地位",
                "竞争分析",
                "风险评估",
                "投资建议"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取搜索建议时发生错误: {e}")
        raise HTTPException(status_code=500, detail="获取搜索建议失败")

# 导出功能路由
@chat_router.post("/export/report")
async def export_report(
    conversation_id: str,
    format: str = "markdown",
    include_metadata: bool = True
):
    """导出分析报告"""
    try:
        # 获取对话历史
        history = get_conversation_history(conversation_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="未找到对话记录")
        
        # 查找最后一个AI响应（通常包含完整报告）
        last_ai_response = None
        for message in reversed(history):
            if message.get("type") == "ai" and len(message.get("content", "")) > 500:
                last_ai_response = message
                break
        
        if not last_ai_response:
            raise HTTPException(status_code=404, detail="未找到可导出的报告")
        
        # 准备导出内容
        export_content = last_ai_response["content"]
        
        if include_metadata:
            metadata = f"""
---
**导出信息**
- 对话ID: {conversation_id}
- 导出时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- 格式: {format}
- 来源: NexMind AI 企业分析平台
---

"""
            export_content = metadata + export_content
        
        return {
            "content": export_content,
            "format": format,
            "filename": f"nexmind_report_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出报告时发生错误: {e}")
        raise HTTPException(status_code=500, detail="导出报告失败")
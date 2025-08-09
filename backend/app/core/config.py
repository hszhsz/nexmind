from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 基本配置
    app_name: str = "NexMind"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"
    
    # CORS配置
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # AI模型配置
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_model: str = "deepseek-chat"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 4000
    
    # Anthropic配置
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # 搜索引擎配置
    search_engine: str = "tavily"  # duckduckgo, tavily, brave
    tavily_api_key: Optional[str] = None
    brave_api_key: Optional[str] = None
    
    # 数据库配置
    database_url: str = "sqlite:///./nexmind.db"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/nexmind.log"
    
    # Agent配置
    max_iterations: int = 10
    max_execution_time: int = 300  # 秒
    
    # 缓存配置
    cache_ttl: int = 3600  # 秒
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# 创建全局设置实例
settings = Settings()

# 验证必要的API密钥
def validate_api_keys():
    """验证必要的API密钥是否已配置"""
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise ValueError(
            "至少需要配置一个AI模型的API密钥 (OPENAI_API_KEY 或 ANTHROPIC_API_KEY)"
        )
    
    if settings.search_engine == "tavily" and not settings.tavily_api_key:
        raise ValueError("使用Tavily搜索引擎需要配置 TAVILY_API_KEY")
    
    if settings.search_engine == "brave" and not settings.brave_api_key:
        raise ValueError("使用Brave搜索引擎需要配置 BRAVE_API_KEY")
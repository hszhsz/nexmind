from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from loguru import logger
import json
from urllib.parse import quote

from ..core.config import settings

class SearchTool:
    """搜索工具类"""
    
    def __init__(self):
        self.search_engine = settings.search_engine
        self.session = None
    
    async def _get_session(self):
        """获取HTTP会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """执行搜索"""
        logger.info(f"搜索查询: {query}")
        
        try:
            if self.search_engine == "duckduckgo":
                return await self._search_duckduckgo(query, max_results)
            elif self.search_engine == "tavily":
                return await self._search_tavily(query, max_results)
            elif self.search_engine == "brave":
                return await self._search_brave(query, max_results)
            else:
                logger.warning(f"未知的搜索引擎: {self.search_engine}，使用DuckDuckGo")
                return await self._search_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"搜索时发生错误: {e}")
            return []
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用DuckDuckGo搜索"""
        session = await self._get_session()
        
        try:
            # DuckDuckGo即时答案API
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    # 处理即时答案
                    if data.get('Abstract'):
                        results.append({
                            'title': data.get('Heading', ''),
                            'content': data.get('Abstract', ''),
                            'url': data.get('AbstractURL', ''),
                            'source': 'DuckDuckGo Abstract'
                        })
                    
                    # 处理相关主题
                    for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
                        if isinstance(topic, dict) and 'Text' in topic:
                            results.append({
                                'title': topic.get('Text', '')[:100],
                                'content': topic.get('Text', ''),
                                'url': topic.get('FirstURL', ''),
                                'source': 'DuckDuckGo Related'
                            })
                    
                    # 如果结果不足，添加一些通用信息
                    if len(results) < max_results:
                        results.append({
                            'title': f'关于 "{query}" 的搜索结果',
                            'content': f'正在为您搜索关于 "{query}" 的相关信息。建议您查看官方网站、财经新闻和行业报告获取最新信息。',
                            'url': '',
                            'source': 'System Generated'
                        })
                    
                    return results[:max_results]
                else:
                    logger.warning(f"DuckDuckGo API返回状态码: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"DuckDuckGo搜索错误: {e}")
            return []
    
    async def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Tavily搜索"""
        if not settings.tavily_api_key:
            logger.error("Tavily API密钥未配置")
            return []
        
        session = await self._get_session()
        
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": settings.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "include_images": False,
                "include_raw_content": False,
                "max_results": max_results
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get('results', []):
                        results.append({
                            'title': item.get('title', ''),
                            'content': item.get('content', ''),
                            'url': item.get('url', ''),
                            'source': 'Tavily'
                        })
                    
                    return results
                else:
                    logger.error(f"Tavily API错误: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Tavily搜索错误: {e}")
            return []
    
    async def _search_brave(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Brave搜索"""
        if not settings.brave_api_key:
            logger.error("Brave API密钥未配置")
            return []
        
        session = await self._get_session()
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": settings.brave_api_key
            }
            params = {
                "q": query,
                "count": max_results,
                "search_lang": "zh",
                "country": "CN"
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get('web', {}).get('results', []):
                        results.append({
                            'title': item.get('title', ''),
                            'content': item.get('description', ''),
                            'url': item.get('url', ''),
                            'source': 'Brave Search'
                        })
                    
                    return results
                else:
                    logger.error(f"Brave API错误: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Brave搜索错误: {e}")
            return []
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """获取网页内容"""
        if not url:
            return None
        
        session = await self._get_session()
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # 移除脚本和样式标签
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # 提取文本内容
                    text = soup.get_text()
                    
                    # 清理文本
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return text[:5000]  # 限制长度
                else:
                    logger.warning(f"无法获取网页内容，状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"获取网页内容时发生错误: {e}")
            return None
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def __del__(self):
        """析构函数"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.close())
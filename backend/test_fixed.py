#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的搜索功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.search import SearchTool
from app.core.config import settings

async def test_search_with_timeout():
    """测试带超时的搜索功能"""
    tool = SearchTool()
    print(f"当前搜索引擎: {tool.search_engine}")
    print(f"Tavily API密钥已配置: {bool(settings.tavily_api_key)}")
    
    try:
        # 测试基本搜索
        print("\n=== 测试基本搜索 ===")
        results = await asyncio.wait_for(
            tool.search('腾讯控股', 2),
            timeout=30
        )
        print(f"搜索结果数量: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. 标题: {result.get('title', '无标题')[:50]}...")
            print(f"   来源: {result.get('source', '未知来源')}")
            print(f"   URL: {result.get('url', '无URL')[:80]}...")
            print()
            
        # 测试多个查询
        print("\n=== 测试多个查询 ===")
        queries = ['腾讯控股 财务', '腾讯控股 竞争对手']
        
        for query in queries:
            try:
                results = await asyncio.wait_for(
                    tool.search(query, 1),
                    timeout=15
                )
                print(f"查询 '{query}': {len(results)} 个结果")
            except asyncio.TimeoutError:
                print(f"查询 '{query}': 超时")
            except Exception as e:
                print(f"查询 '{query}': 错误 - {e}")
                
    except asyncio.TimeoutError:
        print("搜索超时")
    except Exception as e:
        print(f"搜索时发生错误: {e}")
    finally:
        await tool.close()
        print("\n搜索工具已关闭")

if __name__ == "__main__":
    print("开始测试修复后的搜索功能...")
    asyncio.run(test_search_with_timeout())
    print("测试完成")
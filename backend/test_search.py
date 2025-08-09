import asyncio
from app.tools.search import SearchTool

async def test_search():
    tool = SearchTool()
    print(f"当前搜索引擎: {tool.search_engine}")
    
    try:
        results = await tool.search('腾讯控股', 2)
        print(f"搜索结果数量: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. 标题: {result.get('title', '无标题')}")
            print(f"   来源: {result.get('source', '未知来源')}")
            print(f"   内容: {result.get('content', '无内容')[:100]}...")
            print()
    except Exception as e:
        print(f"搜索时发生错误: {e}")
    finally:
        await tool.close()

if __name__ == "__main__":
    asyncio.run(test_search())
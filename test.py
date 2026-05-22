#!/usr/bin/env python3
"""测试 MCP 服务"""

import asyncio
from fastmcp import Client

async def test_mcp_service():
    """测试 MCP 服务功能"""
    
    # 创建客户端（直接传入脚本路径）
    client = Client("main.py")
    
    async with client:
        # 获取可用工具列表
        tools = await client.list_tools()
        print("📦 可用工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        print("\n" + "="*50 + "\n")
        
        # 测试搜索
        print("🔍 测试搜索功能...")
        result = await client.call_tool(
            "search_web",
            {"query": "Python 最新动态", "num_results": 3}
        )
        print(result)
        
        print("\n" + "="*50 + "\n")
        
        # 测试时间
        print("🕐 测试时间功能...")
        result = await client.call_tool(
            "get_current_time",
            {"tz_name": "Asia/Shanghai"}
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(test_mcp_service())
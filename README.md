# SearXNG MCP Server

为 LLM（如 Claude、Chatbox）提供网络搜索能力的 MCP 服务器，基于 SearXNG 搜索引擎。

## 功能特性

- 🔍 网络搜索 - 支持多引擎搜索（Google、Bing、DuckDuckGo 等）
- 📰 新闻搜索 - 专门获取最新资讯
- 📄 网页抓取 - 获取指定 URL 的完整内容
- 🕐 时间查询 - 支持多时区时间获取
- 🌍 国际化 - 支持中文和全球内容搜索

## 快速开始

### 1. 部署 SearXNG 搜索引擎

使用 Docker 部署 SearXNG 实例：

[bash]
# 创建配置文件目录
mkdir -p ~/searxng-data
cd ~/searxng-data

# 下载默认配置
wget -O searxng-settings.yml https://raw.githubusercontent.com/searxng/searxng/master/searx/settings.yml

# 启动 SearXNG 容器
docker run -d \
  --name searxng \
  -p 8888:8080 \
  -v $(pwd)/searxng-settings.yml:/etc/searxng/settings.yml:ro \
  --restart unless-stopped \
  searxng/searxng
[/bash]

国内用户配置镜像加速器（如遇拉取失败）：

[bash]
# 配置 Docker 镜像加速器后重试
# 详见：https://docker.mirrors.ustc.edu.cn
[/bash]

验证 SearXNG 是否运行：

[bash]
curl http://localhost:8888/search?q=test&format=json
[/bash]

### 2. 安装 MCP Server

[bash]
# 创建项目目录
mkdir -p ~/Documents/searxng-mcp
cd ~/Documents/searxng-mcp

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install fastmcp httpx
[/bash]

### 3. 创建 main.py

[python]
#!/usr/bin/env python3
"""SearXNG MCP Server - 为 LLM 提供网络搜索能力"""

import httpx
from fastmcp import FastMCP

mcp = FastMCP("SearXNG Search")

# 替换为你的 SearXNG 实例地址
SEARXNG_URL = "http://localhost:8888"

@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> str:
    """搜索网络获取实时信息
    
    Args:
        query: 搜索关键词
        max_results: 返回的最大结果数（1-20）
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{SEARXNG_URL}/search",
            params={"q": query, "format": "json"}
        )
        results = response.json().get("results", [])[:max_results]
        
        if not results:
            return f"未找到关于 '{query}' 的结果"
        
        output = [f"## 搜索: {query}\n"]
        for item in results:
            output.append(f"### {item.get('title')}")
            output.append(f"链接: {item.get('url')}")
            output.append(f"内容: {item.get('content', '')[:200]}...\n")
        
        return "\n".join(output)

if __name__ == "__main__":
    mcp.run()
[/python]

### 4. 配置 Chatbox

在 Chatbox 中添加 MCP 服务器配置（JSON 格式）：

[json]
{
  "mcpServers": {
    "searxng-search": {
      "command": "/Users/你的用户名/Documents/searxng-mcp/venv/bin/python3",
      "args": [
        "/Users/你的用户名/Documents/searxng-mcp/main.py"
      ],
      "transport": "stdio"
    }
  }
}
[/json]

注意：路径必须使用绝对路径，将"你的用户名"替换为实际的用户名。

### 5. 验证配置

[bash]
# 测试 MCP Server
cd ~/Documents/searxng-mcp
source venv/bin/activate
python main.py
# 应该显示 "Starting MCP server..."
# 按 Ctrl+C 停止
[/bash]

## 使用示例

配置完成后，在 Chatbox 中输入：

[text]
帮我搜索 "Python fastmcp 教程"
[/text]

LLM 将自动调用 search_web 工具并返回搜索结果。

## 目录结构

[text]
~/Documents/searxng-mcp/
├── venv/                 # Python 虚拟环境
├── main.py               # MCP Server 主程序
└── requirements.txt      # 依赖列表（可选）
[/text]

## 常见问题

### Q1: Docker 拉取镜像失败？

配置国内镜像加速器（Docker Desktop -> Settings -> Docker Engine）：

[json]
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
[/json]

### Q2: Chatbox 显示连接失败？

- 检查路径是否使用绝对路径
- 确认虚拟环境已安装 fastmcp
- 运行 python main.py 测试是否有语法错误

### Q3: 搜索无结果？

- 确认 SearXNG 容器正在运行：docker ps | grep searxng
- 测试 API：curl http://localhost:8888/search?q=test&format=json
- 检查防火墙是否允许 8888 端口

### Q4: 如何启用更多搜索引擎？

编辑 searxng-settings.yml，在 engines 列表中添加：

[yaml]
engines:
  - name: google
    use: true
  - name: bing
    use: true
  - name: duckduckgo
    use: true
[/yaml]

重启容器：docker restart searxng

## 许可证

MIT

## 相关链接

- FastMCP 文档: https://github.com/jlowin/fastmcp
- SearXNG 文档: https://docs.searxng.org
- MCP 协议规范: https://modelcontextprotocol.io
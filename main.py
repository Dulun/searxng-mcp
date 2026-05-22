# 1. 安装依赖
# pip install fastmcp httpx

from fastmcp import FastMCP
import httpx

# 创建 MCP 服务器
mcp = FastMCP("LocalWebSearch")

# 公共 SearXNG 实例列表（按优先级排列）
SEARXNG_INSTANCES = [
    "http://127.0.0.1:8888",         # 本地 Docker 实例（兜底）
    "https://searx.be",              # 比利时（首选）
    "https://search.bus-hit.me",     # 美国（备用1）
    "https://searx.tiekoetter.com",  # 德国（备用2）
    "https://searx.info",            # 加拿大（备用3）
]

# 默认搜索引擎配置
DEFAULT_ENGINES = "google,bing,duckduckgo"

# 超时设置
TIMEOUT_SECONDS = 15


async def try_search(instance: str, query: str, num_results: int, client: httpx.AsyncClient) -> dict | None:
    """尝试在单个 SearXNG 实例上执行搜索，失败返回 None"""
    try:
        resp = await client.get(
            f"{instance}/search",
            params={
                "q": query,
                "format": "json",
                "number_of_results": num_results,
                "engines": DEFAULT_ENGINES,
                "language": "zh-CN",
            },
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; LocalWebSearch/1.0)",
                "X-Forwarded-For": "127.0.0.1",
                "Accept": "application/json",
            },
            timeout=TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        return resp.json()
    except (httpx.HTTPError, httpx.TimeoutException, ValueError):
        return None


@mcp.tool()
async def search_web(query: str, num_results: int = 5) -> str:
    """使用公共 SearXNG 实例搜索网络并返回结果摘要

    自动遍历多个实例，按优先级依次尝试，直到成功获取结果。
    """
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        for instance in SEARXNG_INSTANCES:
            data = await try_search(instance, query, num_results, client)
            if data is None:
                continue

            results = data.get("results", [])
            if not results:
                continue

            snippets = []
            for r in results[:num_results]:
                title = r.get("title", "").strip()
                url = r.get("url", "").strip()
                snippet = r.get("content", "").strip()
                if not title and not snippet:
                    continue
                parts = []
                if title:
                    parts.append(f"标题: {title}")
                if url:
                    parts.append(f"链接: {url}")
                if snippet:
                    parts.append(f"摘要: {snippet}")
                snippets.append("\n".join(parts))

            if snippets:
                return f"来源: {instance}\n\n" + "\n---\n".join(snippets)

        return "未搜索到结果。请启动本地 SearXNG 实例：\ndocker run -d --name searxng -p 8888:8080 searxng/searxng"


@mcp.tool()
async def list_instances() -> str:
    """列出可用的公共 SearXNG 搜索实例"""
    lines = ["可用的 SearXNG 实例："]
    for i, url in enumerate(SEARXNG_INSTANCES, 1):
        lines.append(f"{i}. {url}")
    return "\n".join(lines)


@mcp.tool()
async def get_current_time(tz_name: str = "Asia/Shanghai") -> str:
    """获取指定时区的当前时间"""
    from datetime import datetime, timezone, timedelta

    tz_map = {
        "Asia/Shanghai": 8,
        "Asia/Tokyo": 9,
        "America/New_York": -5,
        "America/Los_Angeles": -8,
        "Europe/London": 0,
        "Europe/Berlin": 1,
        "UTC": 0,
    }
    offset = tz_map.get(tz_name)
    if offset is None:
        return f"不支持的时区: {tz_name}，支持的时区: {', '.join(tz_map.keys())}"

    tz = timezone(timedelta(hours=offset))
    now = datetime.now(tz)
    return now.strftime(f"%Y-%m-%d %H:%M:%S (UTC{'+-'[offset<0]}{abs(offset)})")


if __name__ == "__main__":
    mcp.run()

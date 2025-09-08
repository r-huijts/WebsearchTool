from typing import List, Optional
import asyncio
import httpx
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.routing import Mount

from mcp.server.fastmcp import FastMCP

# MCP server (official SDK)
mcp = FastMCP(name="tavily-websearch")

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    score: Optional[float] = None
    favicon: Optional[str] = None

@mcp.tool()
async def web_search(
    query: str,
    count: int = 5,
    search_depth: str = "basic",            # "basic" (1 credit) or "advanced" (2 credits)
    time_range: Optional[str] = None,       # "day" | "week" | "month" | "year"
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_images: bool = False,
) -> List[SearchResult]:
    """
    Tavily-backed search that returns normalized results.
    """
    import os
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")

    # Per Tavily docs, set these explicitly because they change response size/cost.
    payload = {
        "query": query,
        "max_results": max(1, min(count, 10)),
        "search_depth": search_depth,
        "include_answer": False,
        "include_raw_content": False,
    }
    if time_range:
        payload["time_range"] = time_range
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains
    if include_images:
        payload["include_images"] = True

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = "https://api.tavily.com/search"

    # Simple retries with backoff
    last_err = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post(url, json=payload, headers=headers)
            if r.status_code == 401:
                raise RuntimeError("Tavily unauthorized (check TAVILY_API_KEY)")
            if r.status_code == 429:
                raise RuntimeError("Tavily rate limited (429)")
            r.raise_for_status()
            data = r.json()
            out: List[SearchResult] = []
            for item in (data.get("results") or [])[: payload["max_results"]]:
                out.append(
                    SearchResult(
                        title=str(item.get("title") or ""),
                        url=str(item.get("url") or ""),
                        snippet=(item.get("content") or "")[:1000],
                        score=float(item.get("score") or 0),
                        favicon=item.get("favicon"),
                    )
                )
            return out
        except (httpx.HTTPError, httpx.TransportError) as e:
            last_err = e
            if attempt < 2:
                await asyncio.sleep(0.5 * (2 ** attempt))
            else:
                raise RuntimeError(f"Tavily request failed: {e}") from e

# Create the Starlette app for both direct and uvicorn usage
app = Starlette(routes=[Mount("/mcp", app=mcp.streamable_http_app())])

# When run directly as a module, start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
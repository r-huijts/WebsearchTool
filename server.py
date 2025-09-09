# server.py
import os
from typing import List, Optional, Union, Literal

from starlette.applications import Starlette
from starlette.routing import Mount

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

from tavily import TavilyClient

# --- Configuration via environment variables ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY env var is required")

# Host/port for the ASGI server (inside the container use 0.0.0.0:8000)
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

# --- MCP Server ---
mcp = FastMCP("Tavily MCP (Streamable HTTP)", stateless_http=True)

# We construct the Tavily client once and keep it in the MCP lifespan context.
# Tools can fetch it via ctx.request_context.lifespan_context.
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@mcp.tool()
def tavily_search(
    query: str,
    search_depth: Literal["basic", "advanced"] = "basic",
    topic: Literal["general", "news", "finance"] = "general",
    days: Optional[int] = None,
    time_range: Optional[Literal["day","week","month","year","d","w","m","y"]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    max_results: int = 5,
    chunks_per_source: Optional[int] = None,
    include_images: bool = False,
    include_image_descriptions: bool = False,
    include_answer: Union[bool, Literal["basic","advanced"]] = False,
    include_raw_content: Union[bool, Literal["markdown","text"]] = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    country: Optional[str] = None,
    timeout: Optional[int] = None,
    include_favicon: bool = False,
) -> dict:
    """
    Wraps Tavily Search.
    See Tavily's docs for semantics of each parameter.
    """
    # Handle date parameters - if start_date and end_date are the same, use days=1 instead
    if start_date and end_date and start_date == end_date:
        start_date = None
        end_date = None
        days = 1
    
    try:
        # Build the search parameters, excluding None values
        search_params = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "max_results": max_results,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_domains": include_domains or [],
            "exclude_domains": exclude_domains or [],
            "timeout": timeout or 60,
            "include_favicon": include_favicon,
        }
        
        # Only add optional parameters if they have values
        if days is not None:
            search_params["days"] = days
        if time_range is not None:
            search_params["time_range"] = time_range
        if start_date is not None:
            search_params["start_date"] = start_date
        if end_date is not None:
            search_params["end_date"] = end_date
        if chunks_per_source is not None:
            search_params["chunks_per_source"] = chunks_per_source
        if country is not None:
            search_params["country"] = country
            
        return tavily_client.search(**search_params)
    except Exception as e:
        # Return detailed error information for debugging
        return {
            "error": f"Tavily API error: {str(e)}",
            "error_type": type(e).__name__,
            "search_params": search_params
        }

@mcp.tool()
def tavily_extract(
    urls: Union[str, List[str]],
    include_images: bool = False,
    extract_depth: Literal["basic","advanced"] = "basic",
    format: Literal["markdown","text"] = "markdown",
    timeout: Optional[float] = None,
    include_favicon: bool = False,
) -> dict:
    """Wraps Tavily Extract."""
    return tavily_client.extract(
        urls=urls,
        include_images=include_images,
        extract_depth=extract_depth,
        format=format,
        timeout=timeout,
        include_favicon=include_favicon,
    )

@mcp.tool()
def tavily_crawl(
    url: str,
    max_depth: int = 1,
    max_breadth: int = 20,
    limit: int = 50,
    instructions: Optional[str] = None,
    select_paths: Optional[List[str]] = None,
    select_domains: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    allow_external: bool = True,
    include_images: bool = False,
    categories: Optional[List[str]] = None,
    extract_depth: Literal["basic","advanced"] = "basic",
) -> dict:
    """Wraps Tavily Crawl (beta)."""
    return tavily_client.crawl(
        url=url,
        max_depth=max_depth,
        max_breadth=max_breadth,
        limit=limit,
        instructions=instructions,
        select_paths=select_paths,
        select_domains=select_domains,
        exclude_paths=exclude_paths,
        exclude_domains=exclude_domains,
        allow_external=allow_external,
        include_images=include_images,
        categories=categories,
        extract_depth=extract_depth,
    )

@mcp.tool()
def tavily_map(
    url: str,
    max_depth: int = 2,
    limit: int = 30,
    instructions: Optional[str] = None,
) -> dict:
    """Wraps Tavily Map (beta)."""
    return tavily_client.map(
        url=url,
        max_depth=max_depth,
        limit=limit,
        instructions=instructions,
    )

# Build Streamable HTTP ASGI app
app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    # Start the ASGI app via Uvicorn.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
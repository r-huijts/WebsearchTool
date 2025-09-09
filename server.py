# server.py
import os
from datetime import datetime, date
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
def get_current_date() -> dict:
    """
    Get the current date and time information.
    Useful for understanding what 'today', 'recent', 'current' means in context.
    """
    now = datetime.now()
    today = date.today()
    
    return {
        "current_date": today.isoformat(),
        "current_datetime": now.isoformat(),
        "day_of_week": today.strftime("%A"),
        "formatted_date": today.strftime("%B %d, %Y"),
        "year": today.year,
        "month": today.month,
        "day": today.day
    }

@mcp.tool()
def tavily_search(
    query: str,
    search_depth: Literal["basic", "advanced"] = "basic",
    topic: Literal["general", "news", "finance", "health", "scientific", "travel"] = "general",
    auto_parameters: bool = False,
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
    Search the web using Tavily API with comprehensive parameter support.
    
    IMPORTANT DATE CONTEXT: Today's date is {today}
    
    🤖 SMART FEATURES:
    - Use auto_parameters=True for AI-optimized search parameters (BETA)
    - Tavily's AI will automatically set optimal search_depth, topic, time_range
    
    📊 DETAILED CONTENT:
    - include_answer="advanced" for comprehensive AI summaries
    - include_raw_content="markdown" for full article content
    - search_depth="advanced" for deeper analysis (costs 2 credits vs 1)
    - max_results=10-20 for thorough research
    
    🎯 TOPIC SPECIALIZATION:
    - "general": Default for most searches
    - "news": Current events, recent developments
    - "finance": Market data, economic news
    - "health": Medical, wellness content
    - "scientific": Research, academic content  
    - "travel": Tourism, destination information
    
    ⏰ TIME FILTERING:
    - days=N for recent content (works with news topic)
    - time_range="week" for broader time windows
    - start_date/end_date for specific date ranges (YYYY-MM-DD)
    
    🖼️ VISUAL CONTENT:
    - include_images=True for related images
    - include_image_descriptions=True for AI-generated image descriptions
    - include_favicon=True for site favicons
    """.format(today=date.today().isoformat())
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
            "auto_parameters": auto_parameters,
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
def qna_search(query: str) -> str:
    """
    Get a direct, concise answer to a question without full search results.
    
    Perfect for:
    - Quick facts and simple questions
    - When you need just the answer, not sources
    - Fast responses without detailed analysis
    
    Returns a string answer directly instead of full search results.
    Uses less API credits and provides faster responses.
    """
    try:
        answer = tavily_client.qna_search(query=query)
        return answer
    except Exception as e:
        return f"QNA search error: {str(e)}. Try using regular tavily_search for this query."

@mcp.tool()
def get_search_context(
    query: str, 
    max_tokens: int = 4000,
    search_depth: Literal["basic", "advanced"] = "basic"
) -> str:
    """
    Generate context string optimized for RAG (Retrieval-Augmented Generation) applications.
    
    Returns clean, formatted text perfect for feeding into LLMs or AI applications.
    Automatically optimizes content for:
    - Context windows
    - Token limits  
    - Relevant information extraction
    
    This is ideal for building AI applications that need web context.
    """
    try:
        # Note: max_tokens parameter might not be available in all Tavily versions
        # Falls back to get_search_context without max_tokens if needed
        try:
            context = tavily_client.get_search_context(query=query, max_tokens=max_tokens)
        except TypeError:
            # Fallback for older Tavily versions without max_tokens
            context = tavily_client.get_search_context(query=query)
        
        return context
    except Exception as e:
        # Fallback to regular search with context extraction
        try:
            search_result = tavily_client.search(
                query=query,
                search_depth=search_depth,
                include_answer="advanced",
                include_raw_content="text",
                max_results=5
            )
            
            # Extract and combine content for context
            context_parts = []
            if search_result.get("answer"):
                context_parts.append(f"Summary: {search_result['answer']}")
            
            for result in search_result.get("results", []):
                if result.get("content"):
                    context_parts.append(f"Source ({result.get('title', 'Unknown')}): {result['content']}")
            
            return "\n\n".join(context_parts)
            
        except Exception as fallback_error:
            return f"Context generation error: {str(e)}. Fallback error: {str(fallback_error)}"

@mcp.tool()
def detailed_news_search(
    query: str,
    days: int = 7,
    max_results: int = 10,
    country: Optional[str] = None,
    include_international_sources: bool = True,
) -> dict:
    """
    Specialized tool for getting detailed, comprehensive news coverage.
    
    This tool automatically uses optimal parameters for rich content:
    - Advanced search depth for thorough analysis
    - Full article content extraction
    - Comprehensive AI-generated summaries
    - Multiple sources for complete coverage
    
    Perfect for when you want detailed analysis rather than just headlines.
    
    TIP: For country-specific news, try both with and without country filter.
    International sources often have better coverage of specific countries.
    """
    # If looking for specific country news, try without country filter first
    # as international sources often have better coverage
    search_country = None if include_international_sources else country
    
    return tavily_search(
        query=query,
        search_depth="advanced",
        topic="news", 
        auto_parameters=True,  # Let Tavily's AI optimize parameters
        days=days,
        max_results=max_results,
        include_answer="advanced",
        include_raw_content="markdown",
        include_image_descriptions=True,  # Enhanced visual content
        include_favicon=True,             # Better source identification
        country=search_country,
        timeout=120  # Longer timeout for advanced searches
    )

@mcp.tool()
def smart_search(
    query: str,
    max_results: int = 10,
    include_answer: Union[bool, Literal["basic","advanced"]] = "advanced",
    include_raw_content: Union[bool, Literal["markdown","text"]] = "markdown"
) -> dict:
    """
    Intelligent search that automatically optimizes all parameters based on query intent.
    
    🤖 FEATURES:
    - Uses Tavily's AI to automatically determine optimal search_depth, topic, time_range
    - Smart parameter selection based on query content and context
    - Enhanced content extraction with images and metadata
    - Perfect for when you want the best results without manual parameter tuning
    
    ⚠️ NOTE: May use advanced search (2 credits) if Tavily's AI determines it will improve results.
    Explicitly set search_depth="basic" in regular tavily_search to avoid extra cost.
    """
    return tavily_search(
        query=query,
        auto_parameters=True,           # 🎯 Let Tavily's AI optimize everything
        max_results=max_results,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
        include_images=True,            # 🖼️ Include visual content
        include_image_descriptions=True, # 📝 AI descriptions of images
        include_favicon=True,           # 🔗 Better source identification
        timeout=120                     # ⏱️ Allow time for complex searches
    )

@mcp.tool()
def tavily_extract(
    urls: Union[str, List[str]],
    include_images: bool = False,
    extract_depth: Literal["basic","advanced"] = "basic",
    format: Literal["markdown","text"] = "markdown",
    timeout: Optional[float] = None,
    include_favicon: bool = False,
) -> dict:
    """
    Extract content from specific URLs using Tavily.
    
    IMPORTANT: This tool requires actual URLs (starting with http:// or https://).
    Do NOT pass text summaries or search results as URLs.
    
    Use tavily_search first to get URLs, then use this tool to extract content from those URLs.
    """
    
    # Validate that urls parameter contains actual URLs
    if isinstance(urls, str):
        url_list = [urls]
    else:
        url_list = urls
    
    # Check if any of the URLs are actually URLs
    valid_urls = []
    for url in url_list:
        if isinstance(url, str) and (url.startswith('http://') or url.startswith('https://')):
            valid_urls.append(url)
    
    if not valid_urls:
        return {
            "error": "No valid URLs provided. tavily_extract requires actual URLs (starting with http:// or https://)",
            "provided_input": urls,
            "help": "Use tavily_search first to get URLs, then extract content from those URLs"
        }
    
    try:
        result = tavily_client.extract(
            urls=valid_urls,
            include_images=include_images,
            extract_depth=extract_depth,
            format=format,
            timeout=timeout or 60,
            include_favicon=include_favicon,
        )
        
        # Check if extraction was successful
        if result.get("results") or result.get("failed_results"):
            if result.get("failed_results"):
                result["extraction_note"] = "Some URLs failed to extract. This is common with news sites that block crawlers or have paywalls."
            return result
        else:
            return result
            
    except Exception as e:
        return {
            "error": f"Tavily extract error: {str(e)}",
            "error_type": type(e).__name__,
            "valid_urls": valid_urls,
            "suggestion": "Try using tavily_search with include_raw_content=True for better content access"
        }

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
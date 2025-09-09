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

# --- Parameter Validation & Error Handling ---
class TavilyValidationError(Exception):
    """Custom exception for parameter validation errors"""
    pass

def validate_search_params(
    search_depth: str, 
    chunks_per_source: Optional[int], 
    max_results: int,
    topic: str,
    country: Optional[str]
) -> None:
    """
    Validate search parameters and raise descriptive errors.
    """
    # Validate max_results range
    if max_results < 0 or max_results > 20:
        raise TavilyValidationError(
            f"max_results must be between 0 and 20, got {max_results}. "
            "Use 5-10 for most searches, 15-20 for comprehensive research."
        )
    
    # Validate chunks_per_source constraints
    if chunks_per_source is not None:
        if search_depth != "advanced":
            raise TavilyValidationError(
                f"chunks_per_source only available with search_depth='advanced', got search_depth='{search_depth}'. "
                "Either set search_depth='advanced' or remove chunks_per_source parameter."
            )
        if chunks_per_source < 1 or chunks_per_source > 3:
            raise TavilyValidationError(
                f"chunks_per_source must be between 1 and 3, got {chunks_per_source}. "
                "Use 1 for brief snippets, 3 for detailed content extraction."
            )
    
    # Validate topic and country combination
    if country is not None and topic != "general":
        raise TavilyValidationError(
            f"country parameter only available with topic='general', got topic='{topic}'. "
            "Use topic='general' for country-specific searches, or remove country parameter."
        )

def calculate_optimal_timeout(
    search_depth: str, 
    include_raw_content: Union[bool, str], 
    max_results: int,
    auto_parameters: bool
) -> int:
    """
    Calculate optimal timeout based on search complexity.
    """
    base_timeout = 60
    
    # Advanced search takes longer
    if search_depth == "advanced":
        base_timeout += 30
    
    # Auto parameters may trigger advanced search
    if auto_parameters:
        base_timeout += 20
    
    # Raw content extraction adds time
    if include_raw_content:
        base_timeout += 20
    
    # More results = more processing time
    if max_results > 10:
        base_timeout += 15
    elif max_results > 15:
        base_timeout += 25
    
    # Cap at 3 minutes for reasonable response times
    return min(base_timeout, 180)

def create_fallback_search_params(original_params: dict) -> dict:
    """
    Create fallback parameters for when advanced search fails.
    """
    fallback_params = original_params.copy()
    
    # Fallback to basic search
    fallback_params["search_depth"] = "basic"
    fallback_params["auto_parameters"] = False
    
    # Reduce result count to speed up search
    fallback_params["max_results"] = min(fallback_params.get("max_results", 5), 5)
    
    # Remove advanced-only parameters
    if "chunks_per_source" in fallback_params:
        del fallback_params["chunks_per_source"]
    
    # Reduce content complexity
    if fallback_params.get("include_raw_content"):
        fallback_params["include_raw_content"] = False
    
    if fallback_params.get("include_answer") == "advanced":
        fallback_params["include_answer"] = "basic"
    
    return fallback_params

def robust_tavily_search_with_fallback(search_params: dict, max_retries: int = 2) -> dict:
    """
    Execute Tavily search with smart fallback strategies and retry logic.
    """
    import time
    
    # Calculate optimal timeout
    optimal_timeout = calculate_optimal_timeout(
        search_params.get("search_depth", "basic"),
        search_params.get("include_raw_content", False),
        search_params.get("max_results", 5),
        search_params.get("auto_parameters", False)
    )
    
    # Use calculated timeout if none provided
    if "timeout" not in search_params or search_params["timeout"] is None:
        search_params["timeout"] = optimal_timeout
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            # First attempt: Use original parameters
            if attempt == 0:
                return tavily_client.search(**search_params)
            
            # Subsequent attempts: Use fallback strategies
            elif attempt == 1:
                # Fallback 1: Reduce complexity but keep core functionality
                fallback_params = create_fallback_search_params(search_params)
                result = tavily_client.search(**fallback_params)
                result["_fallback_used"] = "reduced_complexity"
                result["_original_error"] = str(last_error)
                return result
            
            else:
                # Fallback 2: Minimal search for basic results
                minimal_params = {
                    "query": search_params["query"],
                    "search_depth": "basic",
                    "max_results": 3,
                    "timeout": 30
                }
                result = tavily_client.search(**minimal_params)
                result["_fallback_used"] = "minimal_search"
                result["_original_error"] = str(last_error)
                return result
                
        except Exception as e:
            last_error = e
            
            # Check if it's a credit/quota error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["credit", "quota", "limit", "billing"]):
                return {
                    "error": f"API quota/credit limit reached: {str(e)}",
                    "error_type": "QuotaExceeded",
                    "suggestion": "Check your Tavily API usage limits and billing status. Try using search_depth='basic' to reduce credit consumption.",
                    "fallback_action": "Use qna_search for simple questions to save credits"
                }
            
            # Check if it's a timeout error
            if any(keyword in error_str for keyword in ["timeout", "time out", "took too long"]):
                # For timeout, wait briefly before retry
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
            
            # For other errors, retry immediately
            if attempt < max_retries:
                time.sleep(1)  # Brief pause between retries
                continue
    
    # If all retries failed, return structured error
    return {
        "error": f"All search attempts failed: {str(last_error)}",
        "error_type": type(last_error).__name__,
        "attempts": max_retries + 1,
        "suggestion": "Try simplifying your query or using qna_search for basic questions",
        "troubleshooting": {
            "check_api_key": "Verify TAVILY_API_KEY is valid",
            "check_network": "Ensure internet connectivity to api.tavily.com",
            "reduce_complexity": "Try search_depth='basic' and fewer max_results"
        }
    }

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
    # Validate parameters before processing
    try:
        validate_search_params(search_depth, chunks_per_source, max_results, topic, country)
    except TavilyValidationError as e:
        return {
            "error": f"Parameter validation error: {str(e)}",
            "error_type": "ValidationError",
            "fix_suggestion": "Check the parameter requirements in the error message above"
        }
    
    # Handle date parameters - if start_date and end_date are the same, use days=1 instead
    if start_date and end_date and start_date == end_date:
        start_date = None
        end_date = None
        days = 1
    
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
        "timeout": timeout,  # Will be calculated automatically if None
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
    
    # Use robust search with fallback strategies
    return robust_tavily_search_with_fallback(search_params)

@mcp.tool()
def tavily_health_check() -> dict:
    """
    Check the health and status of the Tavily API connection.
    
    Performs a minimal search to verify:
    - API key validity
    - Network connectivity
    - Service availability
    - Response time
    
    Useful for troubleshooting connection issues.
    """
    import time
    
    try:
        start_time = time.time()
        
        # Perform minimal test search
        test_result = tavily_client.search(
            query="test",
            max_results=1,
            search_depth="basic",
            timeout=10
        )
        
        response_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "api_accessible": True,
            "response_time_seconds": round(response_time, 2),
            "test_query_successful": True,
            "results_count": len(test_result.get("results", [])),
            "timestamp": date.today().isoformat()
        }
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Diagnose specific error types
        if "api" in error_str and ("key" in error_str or "auth" in error_str):
            diagnosis = "Invalid or missing API key"
            fix_suggestion = "Check TAVILY_API_KEY environment variable"
        elif any(keyword in error_str for keyword in ["network", "connection", "timeout"]):
            diagnosis = "Network connectivity issue"
            fix_suggestion = "Check internet connection and firewall settings"
        elif any(keyword in error_str for keyword in ["quota", "limit", "billing"]):
            diagnosis = "API quota or billing issue"
            fix_suggestion = "Check Tavily account usage and billing status"
        else:
            diagnosis = "Unknown API issue"
            fix_suggestion = "Check Tavily service status"
        
        return {
            "status": "unhealthy",
            "api_accessible": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "diagnosis": diagnosis,
            "fix_suggestion": fix_suggestion,
            "timestamp": date.today().isoformat()
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
        
        # Validate that we got a meaningful response
        if not answer or answer.strip() == "":
            return "No answer found for this query. Try using tavily_search for more comprehensive results."
        
        return answer
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Provide specific guidance based on error type
        if any(keyword in error_str for keyword in ["quota", "credit", "limit"]):
            return f"QNA search quota exceeded: {str(e)}. This uses fewer credits than regular search - check your Tavily account."
        elif "timeout" in error_str:
            return f"QNA search timed out: {str(e)}. Try a simpler question or use tavily_search instead."
        else:
            return f"QNA search error: {str(e)}. Try using tavily_search for this query, which may have better error handling."

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
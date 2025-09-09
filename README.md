# 🔍 MCP Tavily Search Server

> **Enterprise-grade MCP server designed to replace OpenWebUI's default search with intelligent, robust web search capabilities through Tavily API integration**

[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Tavily API](https://img.shields.io/badge/Tavily-Integrated-green)](https://tavily.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com/)
[![OpenWebUI](https://img.shields.io/badge/OpenWebUI-Enhanced-orange)](https://openwebui.com/)

## 🎯 Purpose & Overview

**Primary Goal**: Replace OpenWebUI's basic search functionality with a sophisticated, AI-optimized search system that provides:

- 🧠 **Intelligent tool selection** based on query intent
- 🖼️ **Rich visual content** with images and diagrams  
- 📰 **Specialized news search** for current events
- ⚡ **Cost-optimized searches** from quick facts to deep research
- 🛡️ **Enterprise reliability** with fallback strategies and error handling

This MCP server transforms web search from a basic utility into a powerful AI assistant capability, enabling OpenWebUI to provide research-grade search results with visual content, specialized tools, and intelligent query routing.

### 🌟 Key Features

- **🧠 Intelligent Tool Selection** - AI automatically chooses the best search tool for each query type
- **🖼️ Advanced Visual Search** - Specialized image, diagram, and visual content discovery
- **📰 Enhanced News Search** - Real-time news with comprehensive analysis and visual content
- **⚡ Performance Optimized** - From instant QNA to deep research, credit-aware tool selection
- **🛡️ Enterprise Reliability** - 3-tier fallback system with smart retry logic and health monitoring
- **🎯 Context-Aware Search** - Temporal awareness, domain specialization, and RAG optimization
- **🔧 OpenWebUI Integration** - Drop-in replacement for default search with superior capabilities

## 🏗️ Architecture

```
OpenWebUI → Port 18000 → MCPO (port 8001) → MCP-Tavily (port 8000/mcp)
```

### Container Services
- **`mcp-tavily`** - Main MCP server with Tavily integration
- **`mcpo`** - MCP OpenAPI Proxy (converts MCP protocol to REST)
- **`nginx-auth`** - Optional authentication layer (currently disabled)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Tavily API Key ([Get one here](https://tavily.com/))
- Portainer (recommended for deployment)

### 1. Environment Setup
```bash
# Set your Tavily API key
export TAVILY_API_KEY="tvly-YOUR_API_KEY"
```

### 2. Deploy with Docker Compose
```bash
# Clone the repository
git clone <repository-url>
cd WebsearchTool

# Deploy the stack
docker-compose up -d
```

### 3. Deploy with Portainer
1. Add stack in Portainer
2. Upload `docker-compose.yml`
3. Set environment variable: `TAVILY_API_KEY=tvly-YOUR_API_KEY`
4. Deploy stack
5. Access via `http://your-server:18000`

## 🛠️ Enhanced Tool Arsenal

### 🧠 AI-Guided Tool Selection
**The LLM automatically selects the optimal tool based on query intent:**

| Tool | Purpose | LLM Triggers | Credits |
|------|---------|--------------|---------|
| **`qna_search`** 🔥 | Quick factual answers | "What is...", "Who is...", "When did..." | <1 |
| **`smart_search`** 🎯 | Comprehensive research | "analyze", "compare", "research", complex topics | 1-2 |
| **`detailed_news_search`** 📰 | Current events analysis | "latest news", "recent developments", "current events" | 2 |
| **`visual_search`** 🖼️ | Image-focused search | "image", "photo", "picture", visual content | 2 |
| **`diagram_search`** 📊 | Educational diagrams | "diagram", "flowchart", "chart", "illustration" | 2 |

### 🔍 Core Search Tools

### 🧠 Context & Utility Tools

| Tool | Purpose | Auto-Selected For |
|------|---------|-------------------|
| **`get_current_date`** 📅 | Temporal awareness | "today", "recent", "current", "this week" |
| **`get_search_context`** 🧠 | RAG-optimized context | "research for me to analyze", AI processing |
| **`tavily_health_check`** 🏥 | API diagnostics | Search failures, troubleshooting |

### 📄 Content Extraction Tools

| Tool | Purpose | Features |
|------|---------|----------|
| **`tavily_extract`** | URL content extraction | Batch processing (20 URLs) |
| **`tavily_crawl`** | Website crawling | Depth control, filtering |
| **`tavily_map`** | Site structure analysis | Architecture discovery |

## 💡 OpenWebUI Integration Examples

### 🧠 Intelligent Query Routing
**The LLM automatically selects the best tool - no manual tool specification needed!**

```
User: "What is machine learning?"
→ LLM selects: qna_search (quick facts)
→ Result: Direct answer, <1 credit

User: "Find diagrams explaining neural networks"  
→ LLM selects: diagram_search (visual educational content)
→ Result: Diagrams with AI descriptions, 2 credits

User: "Research renewable energy innovations and trends"
→ LLM selects: smart_search (comprehensive research)  
→ Result: Rich analysis with images, 1-2 credits

User: "Latest news on climate summit"
→ LLM selects: detailed_news_search (current events)
→ Result: News analysis with sources, 2 credits
```

### 🖼️ Enhanced Visual Content
```
User: "Show me a diagram of how LLMs work"
→ Automatic tool: diagram_search 
→ Enhanced query: "how LLMs work diagram flowchart illustration"
→ Result: Educational diagrams with AI descriptions

User: "Images of solar panel installations"
→ Automatic tool: visual_search
→ Result: Photos with descriptions and technical details
```

### 📰 Intelligent News Analysis
```
User: "What happened this week in politics?"
→ Auto sequence: get_current_date → detailed_news_search
→ Result: Comprehensive news with temporal context

User: "Recent developments in AI technology"
→ Automatic tool: detailed_news_search with auto-optimization
→ Result: Latest AI news with analysis and sources
```

### 🎯 Cost-Optimized Search Strategy
```
Simple Facts → qna_search (cheapest)
Complex Research → smart_search (optimized)
Current Events → detailed_news_search (specialized)
Visual Content → visual_search/diagram_search (rich media)
```

## 🛡️ Robustness Features

### 3-Tier Fallback System
1. **Tier 1 (Original)** - Full functionality with requested parameters
2. **Tier 2 (Reduced)** - Basic search with fewer results, maintained quality
3. **Tier 3 (Minimal)** - Emergency fallback for basic results

### Intelligent Error Handling
- **Parameter Validation** - Comprehensive validation with clear error messages
- **Smart Retry Logic** - Exponential backoff for timeouts, immediate retry for transient errors
- **Error Classification** - Specific handling for quota, network, timeout, and authentication errors
- **Dynamic Timeouts** - Automatically calculated based on search complexity

### Performance Optimization
- **Credit Management** - Automatic fallback to lower-cost searches
- **Timeout Optimization** - Dynamic calculation based on search parameters
- **Response Caching** - Efficient resource utilization
- **Health Monitoring** - Real-time API status and performance metrics

## 📊 Advanced OpenWebUI Capabilities

### 🤖 Automatic AI Optimization
**Tavily's AI automatically optimizes search parameters based on query analysis:**
- **Topic Detection**: Automatically selects general/news/finance/health/scientific/travel
- **Search Depth**: AI decides between basic (1 credit) vs advanced (2 credits)  
- **Time Range**: Smart temporal filtering for time-sensitive queries
- **Content Type**: Optimizes for text, visual, or mixed content needs

### 🖼️ Superior Visual Content Discovery
**Far beyond basic web search - intelligent visual content extraction:**
- **Diagram Recognition**: Specialized educational diagram discovery
- **Image Descriptions**: AI-generated descriptions of visual content
- **Visual Context**: Images integrated with comprehensive text explanations
- **Rich Media**: Favicons, thumbnails, and visual metadata

### 📈 Performance vs. Default OpenWebUI Search

| Feature | Default OpenWebUI | Enhanced MCP Server |
|---------|-------------------|---------------------|
| Search Intelligence | Basic web search | AI-guided tool selection |
| Visual Content | Limited | Specialized image/diagram tools |
| News Analysis | Generic results | Dedicated news search with analysis |
| Cost Optimization | No awareness | Credit-optimized tool routing |
| Error Handling | Basic | 3-tier fallback with diagnostics |
| Temporal Awareness | None | Date context and time-based routing |
| Content Quality | Variable | Advanced search with AI summaries |

## 🔧 Configuration

### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TAVILY_API_KEY` | ✅ Yes | - | Your Tavily API key |
| `MCP_HOST` | No | `0.0.0.0` | Server bind address |
| `MCP_PORT` | No | `8000` | Server port |
| `AUTH_TOKEN` | No | - | Optional authentication token |

### Docker Compose Override
```yaml
# docker-compose.override.yml
version: "3.8"
services:
  mcp-tavily:
    environment:
      - TAVILY_API_KEY=your-key-here
      - MCP_PORT=8000
  mcpo:
    ports:
      - "8001:8001"  # Expose MCPO directly for testing
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Connection Errors
```bash
# Check health status
curl http://localhost:18000/tool/tavily_health_check
```

#### 2. Container Communication
```bash
# Verify network connectivity
docker network inspect websearchtool_mcpnet
```

#### 3. Port Conflicts
```bash
# Check port usage
netstat -tlnp | grep 18000
```

### Error Codes & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `QuotaExceeded` | API credit limit | Check Tavily billing, use basic search |
| `ValidationError` | Invalid parameters | Review parameter constraints |
| `NetworkError` | Connectivity issue | Check internet, firewall settings |
| `TimeoutError` | Request timeout | Reduce complexity, check network |

## 📈 Performance Tuning

### Credit Optimization
- Use `qna_search` for simple questions (lowest cost)
- Set `search_depth="basic"` to use 1 credit instead of 2
- Disable `auto_parameters` to prevent automatic advanced search
- Monitor usage with `tavily_health_check`

### Response Time Optimization
- Set appropriate `max_results` (5-10 for speed, 15-20 for research)
- Use `timeout` parameter to prevent hanging requests
- Enable fallback strategies for automatic optimization
- Monitor response times via health check

## 🔄 Development & Architecture

### Project Structure
```
WebsearchTool/
├── server.py              # Main MCP server (10 intelligent tools)
├── docker-compose.yml     # Container orchestration  
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── nginx.conf             # Optional auth configuration
├── .cursor/rules/         # Comprehensive development rules
│   ├── mcp-server-structure.mdc     # Project overview
│   ├── tavily-api-patterns.mdc      # Implementation patterns
│   ├── robustness-patterns.mdc      # Error handling
│   ├── performance-optimization.mdc # Performance guidelines
│   └── tool-arsenal.mdc             # Complete tool reference
└── README.md              # This comprehensive guide
```

### 🎯 OpenWebUI Integration Architecture
```
OpenWebUI Chat Interface
    ↓ (User Query)
OpenWebUI LLM Processing  
    ↓ (Intelligent Tool Selection)
MCP Tools via MCPO Proxy
    ↓ (Optimized Search)
Tavily API with Enhanced Parameters
    ↓ (Rich Results)
OpenWebUI Enhanced Response
```

### Adding New Tools
1. Follow patterns in `.cursor/rules/tavily-api-patterns.mdc`
2. Implement parameter validation with `validate_search_params()`
3. Use `robust_tavily_search_with_fallback()` for reliability
4. Add LLM guidance with clear "USE WHEN" and "DON'T USE FOR" sections
5. Include emoji indicators and credit cost information
6. Test tool selection logic with OpenWebUI integration

### Testing
```bash
# Health check
curl http://localhost:18000/tool/tavily_health_check

# Basic search test
curl -X POST http://localhost:18000/tool/qna_search \
  -H "Content-Type: application/json" \
  -d '{"query": "test question"}'
```

## 📚 OpenWebUI Integration Reference

### 🔌 Connection Setup
1. **Deploy MCP Server**: Use docker-compose or Portainer 
2. **OpenWebUI Discovery**: Tools auto-discovered via MCPO proxy
3. **Immediate Enhancement**: OpenWebUI search is instantly upgraded

### 🧠 Tool Selection Intelligence
The LLM automatically routes queries to optimal tools:

```
Fact Questions → qna_search (fast, cheap)
"What is X?" → Direct answer, <1 credit

Research Queries → smart_search (comprehensive)  
"Research X" → AI-optimized with visuals, 1-2 credits

News Queries → detailed_news_search (specialized)
"Latest news on X" → Rich news analysis, 2 credits

Visual Queries → visual_search or diagram_search
"Diagram of X" → Educational diagrams, 2 credits

Temporal Queries → get_current_date → specialized tool
"Recent X" → Date context + appropriate search
```

### 🎯 Superior Search Results
**Compared to default OpenWebUI search:**
- ✅ **10x more intelligent** tool routing
- ✅ **Rich visual content** with AI descriptions  
- ✅ **Specialized news analysis** with multiple sources
- ✅ **Cost optimization** from instant facts to deep research
- ✅ **Enterprise reliability** with fallback strategies
- ✅ **Temporal awareness** for time-sensitive queries

### 📊 API Documentation
- **OpenAPI Spec**: `http://your-server:18000/openapi.json`
- **MCP Protocol**: Latest standard with HTTP/SSE streaming
- **Tool Discovery**: Automatic via OpenWebUI integration

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run locally: `python server.py`

### Code Standards
- Follow patterns defined in `.cursor/rules/`
- Implement robust error handling
- Add comprehensive parameter validation
- Include fallback strategies for reliability

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **[Tavily](https://tavily.com/)** - Powerful web search API
- **[FastMCP](https://github.com/jlowin/fastmcp)** - MCP server framework
- **[OpenWebUI](https://openwebui.com/)** - AI interface integration
- **[MCPO](https://github.com/open-webui/mcpo)** - MCP to OpenAPI proxy

---

**Built with ❤️ to enhance OpenWebUI's search capabilities**

*Ready to replace basic web search with AI-powered intelligence? Deploy now and transform your OpenWebUI experience with enterprise-grade search capabilities!* 🚀

### 🎯 Why This MCP Server?

**Default OpenWebUI Search Limitations:**
- ❌ Basic web search with limited intelligence
- ❌ No visual content discovery  
- ❌ No cost optimization or tool selection
- ❌ Limited error handling and reliability
- ❌ No specialized search types (news, diagrams, etc.)

**Enhanced MCP Search Capabilities:**
- ✅ **AI-guided tool selection** for optimal results
- ✅ **Rich visual content** with diagrams and images
- ✅ **Cost-optimized routing** from facts to research  
- ✅ **Enterprise reliability** with robust error handling
- ✅ **Specialized tools** for news, visuals, and context
- ✅ **Seamless integration** as drop-in OpenWebUI enhancement

**Transform your OpenWebUI from basic search to AI-powered research assistant!** 🧠✨

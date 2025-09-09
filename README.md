# 🔍 MCP Tavily Search Server

> **Enterprise-grade MCP (Model Context Protocol) server providing intelligent web search capabilities through Tavily API integration**

[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Tavily API](https://img.shields.io/badge/Tavily-Integrated-green)](https://tavily.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com/)
[![OpenWebUI](https://img.shields.io/badge/OpenWebUI-Compatible-orange)](https://openwebui.com/)

## 🎯 Overview

This MCP server transforms web search into a powerful, AI-friendly service with robust error handling, intelligent fallback strategies, and comprehensive search capabilities. Built with FastMCP and containerized for easy deployment.

### 🌟 Key Features

- **🤖 AI-Optimized Search** - Auto-parameters for intelligent search optimization
- **🛡️ Bulletproof Reliability** - 3-tier fallback system with smart retry logic
- **⚡ Multiple Search Types** - From quick answers to comprehensive research
- **🔧 Enterprise-Ready** - Health monitoring, error diagnostics, and performance optimization
- **📊 Rich Content** - Visual content extraction with image descriptions
- **🎯 Specialized Tools** - News, finance, health, scientific, and travel-focused searches

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

## 🛠️ Tool Arsenal

### 🔍 Core Search Tools

| Tool | Purpose | Best For | Credits |
|------|---------|----------|---------|
| **`tavily_search`** | Universal search with full control | Custom parameter tuning | 1-2 |
| **`smart_search`** | AI-optimized comprehensive search | Best results without tuning | 1-2 |
| **`qna_search`** | Direct answers to questions | Quick facts, credit conservation | <1 |
| **`detailed_news_search`** | News-specific research | Current events, politics | 2 |

### 🧠 Context & Utility Tools

| Tool | Purpose | Best For |
|------|---------|----------|
| **`get_search_context`** | RAG-optimized text context | AI applications, LLM feeding |
| **`get_current_date`** | Temporal awareness | Date-sensitive queries |
| **`tavily_health_check`** | API diagnostics | Troubleshooting, monitoring |

### 📄 Content Extraction Tools

| Tool | Purpose | Features |
|------|---------|----------|
| **`tavily_extract`** | URL content extraction | Batch processing (20 URLs) |
| **`tavily_crawl`** | Website crawling | Depth control, filtering |
| **`tavily_map`** | Site structure analysis | Architecture discovery |

## 💡 Usage Examples

### Basic Search
```python
# Quick fact lookup
answer = qna_search("What is the capital of France?")

# Comprehensive research
results = smart_search("climate change renewable energy", max_results=15)
```

### News Research
```python
# Current political news
news = detailed_news_search("political developments Netherlands", days=7)

# International coverage
global_news = detailed_news_search("climate summit", include_international_sources=True)
```

### AI Application Context
```python
# Get RAG-ready context
context = get_search_context("artificial intelligence trends 2024", max_tokens=4000)

# Check current date for temporal queries
date_info = get_current_date()
```

### Health Check & Diagnostics
```python
# Verify API status
health = tavily_health_check()
# Returns: status, response_time, diagnostics, fix_suggestions
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

## 📊 Advanced Features

### AI-Optimized Search
```python
# Let Tavily's AI optimize everything
results = smart_search("renewable energy storage solutions")
# Automatically selects optimal: topic, search_depth, time_range
```

### Visual Content Extraction
```python
# Enhanced content with images
results = tavily_search(
    query="solar panel technology",
    include_images=True,
    include_image_descriptions=True,
    include_favicon=True
)
```

### Domain-Specific Research
```python
# Topic specialization (6 types available)
finance_news = tavily_search("market trends", topic="finance")
health_info = tavily_search("nutrition guidelines", topic="health")
travel_tips = tavily_search("Japan travel guide", topic="travel")
```

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

## 🔄 Development

### Project Structure
```
WebsearchTool/
├── server.py              # Main MCP server implementation
├── docker-compose.yml     # Container orchestration
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── nginx.conf             # Optional auth configuration
├── .cursor/rules/         # Cursor IDE rules for development
└── README.md              # This file
```

### Adding New Tools
1. Follow patterns in `.cursor/rules/tavily-api-patterns.mdc`
2. Implement parameter validation with `validate_search_params()`
3. Use `robust_tavily_search_with_fallback()` for reliability
4. Add comprehensive error handling and documentation

### Testing
```bash
# Health check
curl http://localhost:18000/tool/tavily_health_check

# Basic search test
curl -X POST http://localhost:18000/tool/qna_search \
  -H "Content-Type: application/json" \
  -d '{"query": "test question"}'
```

## 📚 API Reference

### OpenAPI Documentation
When deployed, API documentation is available at:
- **OpenAPI Spec**: `http://your-server:18000/openapi.json`
- **Interactive Docs**: Available through OpenWebUI integration

### MCP Protocol Compliance
This server implements the Model Context Protocol specification:
- **Protocol Version**: Latest MCP standard
- **Transport**: HTTP/SSE streaming
- **Tool Discovery**: Automatic via MCP protocol
- **Error Handling**: MCP-compliant error responses

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

**Built with ❤️ for the AI community**

*Ready to transform your web search capabilities? Deploy now and experience intelligent, reliable search at scale!* 🚀

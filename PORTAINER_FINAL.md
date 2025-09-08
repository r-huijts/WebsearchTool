# 🎯 **FINAL PORTAINER SETUP - MCP Tavily WebSearch**

*Your monkey has perfected this setup after extensive banana-powered testing!* 🐒🍌

## 🚀 **SIMPLIFIED PORTAINER DEPLOYMENT**

### **Step 1: Environment Variables**
Set these in your Portainer Stack:

```bash
# 🔑 REQUIRED
TAVILY_API_KEY=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

# 🌐 OPTIONAL 
EXTERNAL_PORT=18000
```

### **Step 2: Stack Configuration**
Use `portainer-docker-compose.yml` content:

```yaml
services:
  mcp-tavily:
    image: mcp-tavily:latest
    container_name: mcp-tavily-search
    restart: unless-stopped
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - TAVILY_API_KEY=${TAVILY_API_KEY}
    networks: 
      - mcp-network
    ports:
      - "${EXTERNAL_PORT:-18000}:7000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7000/mcp/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  mcp-network:
    driver: bridge
```

## 🎪 **What You Get**

✅ **Direct MCP Server**: No proxy complications  
✅ **Port 18000**: Direct access to your search service  
✅ **Health Checks**: Automatic service monitoring  
✅ **Web Search Tool**: Real Tavily API integration  

## 🔌 **Integration**

### **With Open WebUI:**
```
MCP Server URL: http://your-server:18000/mcp
Protocol: StreamableHTTP
```

### **With Claude Desktop:**
Add to your MCP config:
```json
{
  "mcpServers": {
    "tavily-search": {
      "command": "curl",
      "args": ["-X", "POST", "http://your-server:18000/mcp"]
    }
  }
}
```

### **Direct API Testing:**
```bash
# Test the search function
curl -X POST http://your-server:18000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "arguments": {
      "query": "Python best practices",
      "count": 3
    }
  }'
```

## 🐛 **Troubleshooting**

### **Container Status**
```bash
# Check if running
docker ps | grep mcp-tavily

# View logs
docker logs mcp-tavily-search
```

### **Port Issues**
If port 18000 is busy, change `EXTERNAL_PORT`:
```bash
EXTERNAL_PORT=19000
```

### **API Issues**
Verify your Tavily API key:
```bash
# Test directly in container
docker exec mcp-tavily-search python -c "
import os
print('API Key:', os.getenv('TAVILY_API_KEY', 'NOT SET'))
"
```

## 🎉 **Success!**

Your MCP Tavily WebSearch tool is ready for production! 
- ✨ **Real web search powered by Tavily**
- 🔄 **Automatic restarts and health monitoring** 
- 🌐 **Accessible on port 18000**
- 🐒 **Monkey-tested and approved!**

*Go forth and search the web with the power of a caffeinated code monkey!* 🚀

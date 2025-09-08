# 🐒 MCP Tavily WebSearch - Portainer Stack Setup

## 🚀 Quick Deploy to Portainer

### Step 1: Environment Variables
Set these in your Portainer Stack environment variables:

```bash
# 🔑 REQUIRED - Your Tavily API Key
TAVILY_API_KEY=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

# 🌐 OPTIONAL - External port (default: 18000)
EXTERNAL_PORT=18000

# 🔐 OPTIONAL - MCPO API Key for security (default: supersecret)
MCPO_API_KEY=your-secure-api-key-here

# 📝 OPTIONAL - Stack naming (default: mcp-tavily)
STACK_NAME=mcp-tavily
```

### Step 2: Deploy Methods

#### Option A: Use the optimized Portainer stack file
1. Copy `portainer-stack.yml` content
2. Create new stack in Portainer
3. Set environment variables above
4. Deploy!

#### Option B: Use docker-compose.yml
1. Copy `docker-compose.yml` content  
2. Set the environment variables
3. Deploy via Portainer stacks

## 🎯 Access Your Service

Once deployed, access your MCP WebSearch at:
- **Main Service**: `http://your-server:18000`
- **API Documentation**: `http://your-server:18000/docs`
- **Health Check**: `http://your-server:18000/health`

## 🔧 Environment Variables Explained

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TAVILY_API_KEY` | ✅ Yes | - | Your Tavily API key for web search |
| `EXTERNAL_PORT` | ❌ No | `18000` | Port to expose the service on |
| `MCPO_API_KEY` | ❌ No | `supersecret` | API key for MCPO proxy authentication |
| `STACK_NAME` | ❌ No | `mcp-tavily` | Prefix for container and network names |

## 🐛 Troubleshooting

### Health Checks
Both services include health checks:
- **mcp-tavily**: Checks if the FastMCP server responds
- **mcpo**: Checks if the proxy is running

### Common Issues
1. **Port 18000 already in use**: Change `EXTERNAL_PORT` to another port
2. **Tavily API errors**: Verify your `TAVILY_API_KEY` is correct
3. **Container communication**: Ensure both containers are on the same network

### Logs
Check container logs in Portainer:
- `mcp-tavily-server`: FastMCP server logs
- `mcp-tavily-proxy`: MCPO proxy logs

## 🎪 Integration with Open WebUI

To use with Open WebUI, add this MCP server:
```
URL: http://your-server:18000
API Key: [your MCPO_API_KEY]
```

The web search tool will then be available in your Open WebUI instance!

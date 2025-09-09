# 🔐 Secure MCP Server Deployment Guide

## 🎯 Option 1: Nginx Bearer Token Authentication

### **Pre-Deployment Checklist**
- [ ] Set `TAVILY_API_KEY` in Portainer environment variables
- [ ] Set `AUTH_TOKEN` in Portainer environment variables (your secret bearer token)
- [ ] Ensure `nginx.conf` is in the same directory as `docker-compose.yml`
- [ ] Verify OpenWebUI has external tool/connection configuration options

### **Environment Variables Required**
```bash
# In Portainer Stack Environment Variables:
TAVILY_API_KEY=tvly-your-actual-api-key-here
AUTH_TOKEN=your-super-secret-bearer-token-12345-change-this
```

### **Architecture Flow**
```
OpenWebUI → http://your-server:18000 → Nginx Auth → MCPO → MCP-Tavily → Tavily API
```

### **Testing Steps**

#### 1. Health Check (No Auth Required)
```bash
curl http://your-server:18000/health
# Expected: {"status":"healthy","service":"mcp-tavily-auth"}
```

#### 2. Unauthorized Request (Should Fail)
```bash
curl http://your-server:18000/openapi.json
# Expected: {"error":"Unauthorized","message":"Valid Bearer token required"}
```

#### 3. Authorized Request (Should Work)
```bash
curl -H "Authorization: Bearer your-super-secret-bearer-token-12345-change-this" \
     http://your-server:18000/openapi.json
# Expected: OpenAPI specification JSON
```

#### 4. Tool Call Test
```bash
curl -X POST \
  -H "Authorization: Bearer your-super-secret-bearer-token-12345-change-this" \
  -H "Content-Type: application/json" \
  -d '{"query": "test search"}' \
  http://your-server:18000/tool/qna_search
# Expected: Search results or tool response
```

### **OpenWebUI Configuration**

1. **Go to OpenWebUI Settings** → **Connections** or **External Tools**
2. **Add New Connection:**
   - **Name**: `MCP Tavily Search`
   - **Base URL**: `http://your-server:18000`
   - **Authentication Type**: `Bearer Token`
   - **Bearer Token**: `your-super-secret-bearer-token-12345-change-this`
3. **Test Connection** and **Save**

### **Troubleshooting**

#### Container Logs
```bash
# Check Nginx auth logs
docker logs nginx-auth-container-name

# Check MCPO logs  
docker logs mcpo-container-name

# Check MCP server logs
docker logs mcp-tavily-container-name
```

#### Common Issues
- **401 Unauthorized**: Check AUTH_TOKEN matches between Portainer and OpenWebUI
- **Connection Refused**: Verify containers are running and port 18000 is accessible
- **CORS Errors**: The nginx.conf includes CORS headers for browser compatibility
- **Timeout Errors**: Long searches use 5-minute timeouts, normal for complex queries

### **Security Notes**
- ✅ **Bearer token validation** on all API endpoints
- ✅ **CORS headers** for web browser compatibility  
- ✅ **Health check endpoint** without authentication for monitoring
- ✅ **Proper error responses** with JSON formatting
- ✅ **Extended timeouts** for AI search operations (5 minutes)

### **Production Recommendations**
1. **Use a strong AUTH_TOKEN** (32+ characters, random)
2. **Enable HTTPS** if exposing to internet (add SSL termination)
3. **Monitor health endpoint** for service availability
4. **Rotate AUTH_TOKEN** periodically for security
5. **Check container logs** for any authentication failures

---

**🚀 Deploy with confidence! This configuration provides enterprise-grade security for your OpenWebUI integration.**

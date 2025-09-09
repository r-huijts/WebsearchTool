FROM python:3.11-slim
WORKDIR /app

# system deps (optional)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# 1) copy only requirements first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) then copy the rest
COPY . .

ENV MCP_HOST=0.0.0.0 MCP_PORT=8000
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
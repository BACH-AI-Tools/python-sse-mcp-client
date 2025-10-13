# SSE MCP 客户端使用指南

[![GitHub](https://img.shields.io/badge/GitHub-BACH--AI--Tools-blue?logo=github)](https://github.com/BACH-AI-Tools/python-sse-mcp-client)

## 🎯 什么是 SSE MCP？

通过 HTTP/SSE 协议连接**远程** MCP 服务器（而不是本地进程）。

## 🚀 基础用法

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client(
    url="http://example.com/sse",
    headers={"Authorization": "Bearer TOKEN"},
    timeout=10.0,           # HTTP 超时
    sse_read_timeout=300.0  # SSE 读取超时
) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 列出工具
        tools = await session.list_tools()

        # 调用工具
        result = await session.call_tool("tool_name", arguments={})
        print(result.content[0].text)
```

## 📋 OpenFDA 示例配置

```python
server_url = "http://openfda.mcp.kaleido.guru/sse"
headers = {
    "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
    "emcp-usercode": "2DebiJQI"
}
```

### Cursor/Claude Desktop 配置

```json
{
  "mcpServers": {
    "openfda": {
      "url": "http://openfda.mcp.kaleido.guru/sse",
      "headers": {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
      },
      "type": "sse"
    }
  }
}
```

## 🔧 OpenFDA 可用工具

### 1. search_drug_labels - 搜索药品标签

```python
result = await session.call_tool("search_drug_labels", {
    "search": "ibuprofen",  # 药品名、成分、制造商等
    "limit": 10             # 返回数量（1-1000）
})
```

### 2. get_drug_adverse_reactions - 查询不良反应

```python
result = await session.call_tool("get_drug_adverse_reactions", {
    "drug_name": "aspirin",  # 必填
    "limit": 5
})
```

### 3. get_drug_warnings - 查询警告信息

```python
result = await session.call_tool("get_drug_warnings", {
    "drug_name": "acetaminophen",  # 必填
    "limit": 3
})
```

### 4. ae_pipeline_rag - RAG 安全分析

```python
result = await session.call_tool("ae_pipeline_rag", {
    "query": "cardiovascular side effects",
    "drug": "ibuprofen",
    "top_k": 5
})
```

### 5. get_drug_indications - 查询适应症

```python
result = await session.call_tool("get_drug_indications", {
    "drug_name": "naproxen",  # 必填
    "limit": 5
})
```

## 💡 实用示例

### 查询单个药品

```python
import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def search_drug(drug_name: str):
    server_url = "http://openfda.mcp.kaleido.guru/sse"
    headers = {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
    }

    async with sse_client(url=server_url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("search_drug_labels", {
                "search": drug_name,
                "limit": 1
            })

            data = json.loads(result.content[0].text)
            return data

# 运行
asyncio.run(search_drug("aspirin"))
```

### 批量查询多个药品

```python
async def batch_query(drugs: list):
    server_url = "http://openfda.mcp.kaleido.guru/sse"
    headers = {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
    }

    async with sse_client(url=server_url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            results = {}
            for drug in drugs:
                result = await session.call_tool("search_drug_labels", {
                    "search": drug,
                    "limit": 1
                })
                results[drug] = json.loads(result.content[0].text)

            return results

# 运行
drugs = ["aspirin", "ibuprofen", "naproxen"]
asyncio.run(batch_query(drugs))
```

### 药品安全分析

```python
async def analyze_drug_safety(drug_name: str, concern: str):
    server_url = "http://openfda.mcp.kaleido.guru/sse"
    headers = {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
    }

    async with sse_client(url=server_url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("ae_pipeline_rag", {
                "query": concern,
                "drug": drug_name,
                "top_k": 5
            })

            return result.content[0].text

# 运行
analysis = asyncio.run(analyze_drug_safety(
    "ibuprofen",
    "cardiovascular risks"
))
print(analysis)
```

## ❓ 常见问题

### 如何处理超时？

```python
async with sse_client(
    url=server_url,
    headers=headers,
    timeout=10.0,          # HTTP 请求超时（秒）
    sse_read_timeout=300.0 # SSE 读取超时（秒）
) as (read, write):
    # ...
```

### 如何添加自定义 Headers？

```python
headers = {
    "Authorization": "Bearer TOKEN",
    "Custom-Header": "value",
    "emcp-key": "your-key"
}
```

### 如何分页查询大量数据？

```python
# 分页获取数据
for page in range(0, 100, 10):
    result = await session.call_tool("search_drug_labels", {
        "search": "aspirin",
        "skip": page,   # 跳过前 N 条
        "limit": 10     # 每页 10 条
    })
    # 处理结果...
```

### 如何处理错误？

```python
try:
    result = await session.call_tool("unknown_tool", arguments={})
except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
```

## 📚 完整示例文件

- **src/sse_client_example.py** - 基础连接和测试
- **src/openfda_demo.py** - 实用查询示例

```bash
# 运行示例
python src/sse_client_example.py
python src/openfda_demo.py
```

## 🔗 相关链接

- [本项目 GitHub 仓库](https://github.com/BACH-AI-Tools/python-sse-mcp-client)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [BACH AI Tools 组织](https://github.com/BACH-AI-Tools)

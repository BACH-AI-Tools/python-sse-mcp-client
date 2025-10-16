# StreamableHTTP MCP 协议指南

## 📌 概述

StreamableHTTP 是 MCP（Model Context Protocol）的一种传输协议，专为支持 HTTP POST 请求和可选的 SSE（Server-Sent Events）流式响应设计。它提供了会话管理、断点续传等高级功能。

## 🌟 协议特点

### 与 SSE 协议的区别

| 特性             | SSE 协议                | StreamableHTTP 协议           |
| ---------------- | ----------------------- | ----------------------------- |
| **请求方式**     | GET                     | POST                          |
| **会话管理**     | 无                      | 支持（通过 session-id）       |
| **断点续传**     | 不支持                  | 支持（通过 resumption token） |
| **双向通信**     | 单向（服务器 → 客户端） | 双向（支持请求-响应模式）     |
| **协议版本协商** | 不支持                  | 支持                          |
| **适用场景**     | 简单的事件推送          | 复杂的交互式应用              |

## 🔧 使用方法

### 1. 基本连接

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def connect_streamable_http():
    # 服务器配置
    server_url = "http://your-server.com/mcp"
    headers = {
        "Authorization": "Bearer YOUR_TOKEN",
        "Custom-Header": "value"
    }

    # 连接服务器
    async with streamablehttp_client(
        url=server_url,
        headers=headers,
        timeout=30.0,  # HTTP 超时
        sse_read_timeout=300.0  # SSE 读取超时
    ) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()

            # 获取当前会话 ID
            session_id = get_session_id()
            print(f"Session ID: {session_id}")

            # 使用服务器功能
            tools = await session.list_tools()
            # ...
```

### 2. 会话管理

StreamableHTTP 支持会话管理，服务器会为每个客户端分配唯一的会话 ID：

```python
async with streamablehttp_client(...) as (read, write, get_session_id):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 获取会话 ID
        session_id = get_session_id()
        if session_id:
            print(f"已建立会话: {session_id}")
            # 会话 ID 会自动包含在后续请求的头部
```

### 3. 调用工具

```python
# 调用工具示例
result = await session.call_tool(
    "tool_name",
    arguments={
        "param1": "value1",
        "param2": 123
    }
)

# 处理结果
for content in result.content:
    if hasattr(content, 'text'):
        print(content.text)
```

### 4. 流式响应处理

StreamableHTTP 支持流式响应，适合处理大量数据或长时间运行的操作：

```python
# 服务器可以选择返回 JSON 或 SSE 流
# 客户端会自动处理两种响应类型

# 对于流式响应，数据会逐块到达
result = await session.call_tool("long_running_task", {
    "input": "large_data"
})

# 结果会在所有数据接收完成后返回
```

## 📝 配置示例

### 在 Cursor/Claude Desktop 中使用

```json
{
  "mcpServers": {
    "my-streamable-server": {
      "url": "http://api.example.com/mcp",
      "headers": {
        "api-key": "YOUR_API_KEY",
        "user-id": "YOUR_USER_ID"
      },
      "type": "streamableHttp"
    }
  }
}
```

### Python 客户端配置

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    # 完整配置示例
    config = {
        "url": "http://fda.sitmcp.kaleido.guru/mcp",
        "headers": {
            "emcp-key": "YOUR_KEY",
            "emcp-usercode": "YOUR_CODE"
        },
        "timeout": 30.0,  # 普通 HTTP 操作超时
        "sse_read_timeout": 300.0,  # SSE 流读取超时
        "terminate_on_close": True  # 关闭时终止会话
    }

    async with streamablehttp_client(**config) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            # 初始化
            init_result = await session.initialize()
            print(f"协议版本: {init_result.protocolVersion}")

            # 列出工具
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # 调用工具
            if tools.tools:
                result = await session.call_tool(
                    tools.tools[0].name,
                    arguments={"search": "test", "limit": 5}
                )
                print(result.content[0].text if result.content else "无结果")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚀 高级功能

### 1. 断点续传

StreamableHTTP 支持断点续传，适用于不稳定网络环境：

```python
from mcp.client.session import ClientMessageMetadata

# 使用 resumption token 恢复中断的请求
metadata = ClientMessageMetadata(
    resumption_token="last-event-id-123"
)

# 发送带有元数据的请求
# 服务器会从断点处继续发送数据
```

### 2. 协议版本协商

客户端和服务器会自动协商使用的协议版本：

```python
init_result = await session.initialize()
protocol_version = init_result.protocolVersion
print(f"使用协议版本: {protocol_version}")
```

### 3. 错误处理

```python
try:
    async with streamablehttp_client(...) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # ... 使用服务器功能

except ConnectionError as e:
    print(f"连接错误: {e}")
    # 处理网络连接问题

except TimeoutError as e:
    print(f"超时错误: {e}")
    # 处理超时情况

except Exception as e:
    print(f"其他错误: {e}")
    # 处理其他异常
```

## 📊 性能优化建议

1. **合理设置超时时间**

   - `timeout`: 用于普通 HTTP 操作，建议 10-30 秒
   - `sse_read_timeout`: 用于 SSE 流读取，建议 300-600 秒

2. **会话复用**

   - 保持会话活跃，避免频繁重连
   - 使用会话 ID 进行状态管理

3. **流式处理**
   - 对于大数据量的响应，服务器应使用 SSE 流式返回
   - 客户端自动处理流式数据，无需特殊配置

## 🔍 调试技巧

### 启用详细日志

```python
import logging

# 启用 MCP 客户端日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('mcp.client.streamable_http')
logger.setLevel(logging.DEBUG)
```

### 监控会话状态

```python
# 检查会话 ID 变化
old_session_id = None
async with streamablehttp_client(...) as (read, write, get_session_id):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 定期检查会话状态
        current_session_id = get_session_id()
        if current_session_id != old_session_id:
            print(f"会话变更: {old_session_id} -> {current_session_id}")
            old_session_id = current_session_id
```

## 📋 常见问题

### Q: 何时使用 StreamableHTTP 而非 SSE？

**A:** 当你需要以下功能时使用 StreamableHTTP：

- 双向通信（请求-响应模式）
- 会话管理和状态保持
- 断点续传支持
- POST 请求支持（携带复杂数据）

### Q: 如何处理 405 Method Not Allowed 错误？

**A:** 这通常表示：

1. 服务器不支持 StreamableHTTP，尝试使用 SSE 协议
2. URL 路径错误，检查服务器文档确认正确的端点
3. 缺少必要的请求头，确认认证信息是否正确

### Q: 会话 ID 有什么用？

**A:** 会话 ID 用于：

- 在服务器端保持客户端状态
- 实现断点续传功能
- 管理并发请求
- 提供会话级别的安全控制

## 🔗 相关资源

- [MCP 官方文档 - StreamableHTTP](https://modelcontextprotocol.io/docs/transports/streamable-http)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [示例代码](./src/streamable_http_demo.py)

## 📄 许可证

MIT License

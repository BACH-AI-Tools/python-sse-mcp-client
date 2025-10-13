# Python SSE MCP 客户端示例

[![GitHub](https://img.shields.io/badge/GitHub-BACH--AI--Tools-blue?logo=github)](https://github.com/BACH-AI-Tools/python-sse-mcp-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

在 Python 代码中连接 **SSE（Server-Sent Events）类型**的远程 MCP 服务器。

## ⭐ 特点

✅ **远程连接**：通过 HTTP/SSE 连接云端 MCP 服务器  
✅ **开箱即用**：完整示例代码，可直接运行  
✅ **实用演示**：包含 OpenFDA 药品数据库查询示例  
✅ **详细文档**：完整的使用指南和 API 说明

## 📦 项目结构

```
.
├── src/
│   ├── sse_client_example.py  # SSE MCP 基础连接示例
│   └── openfda_demo.py        # OpenFDA 实用查询示例
├── SSE_MCP_GUIDE.md           # 详细使用指南
├── README.md                  # 本文件
├── requirements.txt           # 依赖列表
└── pyproject.toml            # 项目配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install mcp
```

### 2. 运行示例

```bash
# 测试基础连接（查看所有可用工具）
python src/sse_client_example.py

# 运行实用查询示例（药品信息查询）
python src/openfda_demo.py
```

## 💡 核心代码

### 连接 SSE MCP 服务器

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

# 服务器配置
server_url = "http://openfda.mcp.kaleido.guru/sse"
headers = {
    "emcp-key": "YOUR_KEY",
    "emcp-usercode": "YOUR_CODE"
}

# 连接并调用
async with sse_client(url=server_url, headers=headers) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # 列出可用工具
        tools = await session.list_tools()

        # 调用工具
        result = await session.call_tool("tool_name", arguments={
            "param": "value"
        })

        print(result.content[0].text)
```

## 🌟 OpenFDA 示例

项目包含完整的 OpenFDA（美国 FDA 药品数据库）查询示例：

### 可用工具

1. **search_drug_labels** - 搜索 FDA 药品标签信息
2. **get_drug_adverse_reactions** - 查询药品不良反应
3. **get_drug_warnings** - 获取药品警告信息
4. **ae_pipeline_rag** - RAG 药品安全分析
5. **get_drug_indications** - 获取药品适应症

### 示例代码

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def query_drug(drug_name: str):
    server_url = "http://openfda.mcp.kaleido.guru/sse"
    headers = {
        "emcp-key": "DGBBWP0neHpDf8MH5l6QIVeRpmBOkZB1",
        "emcp-usercode": "2DebiJQI"
    }

    async with sse_client(url=server_url, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 搜索药品
            result = await session.call_tool("search_drug_labels", {
                "search": drug_name,
                "limit": 5
            })

            print(result.content[0].text)

# 运行
asyncio.run(query_drug("aspirin"))
```

## 📚 详细文档

查看 [SSE_MCP_GUIDE.md](SSE_MCP_GUIDE.md) 了解：

- 完整的 API 文档
- 所有工具的参数说明
- 更多实用示例
- 常见问题解答

## 🎯 使用场景

- **云服务集成**：连接远程 MCP API 服务
- **数据查询**：查询 OpenFDA、天气、股票等公共 API
- **AI 助手增强**：为 Claude/Cursor 等提供外部工具
- **企业应用**：连接企业内部 MCP 服务器

## 📋 MCP 配置示例

如果要在 Cursor/Claude Desktop 中使用：

```json
{
  "mcpServers": {
    "openfda": {
      "url": "http://openfda.mcp.kaleido.guru/sse",
      "headers": {
        "emcp-key": "YOUR_KEY",
        "emcp-usercode": "YOUR_CODE"
      },
      "type": "sse"
    }
  }
}
```

## 🔗 相关资源

- [本项目 GitHub 仓库](https://github.com/BACH-AI-Tools/python-sse-mcp-client)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [BACH AI Tools 组织](https://github.com/BACH-AI-Tools)

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 👤 作者

**Feng Rongquan**

- GitHub: [@BACH-AI-Tools](https://github.com/BACH-AI-Tools)

# Python MCP 客户端示例（Streamable HTTP + SSE）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | **简体中文**

用官方 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) 连接**远程** MCP 服务器的小型示例程序，可以直接运行。两种 HTTP 传输都覆盖：
- **Streamable HTTP**：当前的标准传输方式；
- **HTTP+SSE**：旧版传输方式，不少服务器仍在提供。

每个程序都会初始化会话，列出服务器的工具、资源和提示词，再调用一个工具。示例服务器用的是 [jieba-mcp](https://github.com/BACH-AI-Tools/jieba-mcp)（中文分词服务），本地一条命令就能启动，不需要任何账号或 API Key。

## 文件说明

| 文件 | 演示内容 |
|---|---|
| `src/streamable_http_demo.py` | Streamable HTTP：用 `httpx.AsyncClient` 设置请求头和超时、会话 ID、列出全部能力、调用工具 |
| `src/sse_client_example.py` | 同样的流程，走旧版 SSE 传输 |
| `src/jieba_demo.py` | 实用客户端：依次调用 jieba 的 5 个工具，`--transport streamable-http\|sse` |
| `src/common.py` | 公共命令行参数（`--url`、`--header`、`--timeout`）和输出格式 |
| `scripts/smoke.py` | 启动 jieba-mcp，用两种传输跑完所有示例并检查输出 |

## 快速开始

**1. 启动示例服务器**（两种传输各开一个终端）：

```bash
uvx jieba-mcp --transport streamable-http --port 8000   # http://127.0.0.1:8000/mcp
uvx jieba-mcp --transport sse --port 8001               # http://127.0.0.1:8001/sse
```

- jieba-mcp 发布到 PyPI 之前，把 `uvx jieba-mcp` 换成 `uvx --from git+https://github.com/BACH-AI-Tools/jieba-mcp jieba-mcp`。
- 如果 8000 端口已被占用，换一个端口，并在下面运行示例时用 `--url` 指过去。

**2. 安装客户端依赖**（Python 3.10+）：

```bash
pip install -r requirements.txt
```

**3. 运行示例：**

```bash
python src/streamable_http_demo.py
python src/sse_client_example.py --url http://127.0.0.1:8001/sse
python src/jieba_demo.py
python src/jieba_demo.py --transport sse --url http://127.0.0.1:8001/sse
```

下面是真实输出（有删减；会话 ID 每次运行都不同）：

```text
$ python src/streamable_http_demo.py --header 'Authorization: Bearer demo-token'
Connecting to http://127.0.0.1:8000/mcp (Streamable HTTP)
Headers: {'Authorization': '***oken'}
Session id: b4b27575b92042ba9e26b5ef2799f028
Server: jieba 1.0.0
Protocol version: 2025-11-25

Tools (5):
  - segment: Split Chinese text into words with jieba.
      text (string, required)
      mode (string, optional)
      hmm (boolean, optional)
  - extract_keywords: Extract the most important keywords from Chinese text.
  ...
Calling extract_keywords {"text": "我来到北京清华大学，清华大学是一所综合性大学", "top_k": 3}:
{"method": "tfidf", "keywords": [{"word": "清华大学", "weight": 2.308741}, {"word": "一所", "weight": 1.115948}, {"word": "综合性", "weight": 1.044143}]}
```

```text
$ python src/sse_client_example.py --url http://127.0.0.1:8001/sse
Connecting to http://127.0.0.1:8001/sse (SSE)
Server: jieba 1.0.0
...
Calling segment {"text": "我来到北京清华大学"}:
{"mode": "precise", "tokens": ["我", "来到", "北京", "清华大学"], "count": 4}
```

```text
$ python src/jieba_demo.py

>>> segment
{"mode": "search", "tokens": ["小明", "硕士", "毕业", "于", "中国", "科学", "学院", "科学院", "中国科学院", "计算", "计算所"], "count": 11}

>>> extract_keywords
{"method": "textrank", "keywords": [{"word": "线程", "weight": 1.0}, {"word": "进程", "weight": 0.7957}, {"word": "共享", "weight": 0.504354}]}

>>> pos_tag
{"tokens": [{"word": "我", "flag": "r"}, {"word": "爱", "flag": "v"}, {"word": "北京", "flag": "ns"}, {"word": "天安门", "flag": "ns"}], "count": 4}

>>> add_user_words
{"added": ["大语言模型"], "count": 1}

>>> segment
{"mode": "precise", "tokens": ["大语言模型", "正在", "改变", "软件开发"], "count": 4}

>>> convert_chinese
{"config": "s2twp", "text": "軟體和滑鼠"}
```

`jieba_demo.py` 走 SSE 时输出完全相同。

## 连接你自己的服务器

```bash
python src/streamable_http_demo.py --url https://example.com/mcp \
    --header 'Authorization: Bearer <your-token>'
```

也可以设置环境变量 `MCP_SERVER_URL` 来代替 `--url`。打印请求头时会自动打码。真实的 token 请放在环境变量或本地被 git 忽略的 `.env` 里，不要写进代码。

## 核心代码

**Streamable HTTP**（需要 `mcp>=1.24`）：

```python
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

http = httpx.AsyncClient(headers={"Authorization": "Bearer <token>"},
                         timeout=httpx.Timeout(30, read=300))
async with http, streamable_http_client("http://127.0.0.1:8000/mcp", http_client=http) as (read, write, get_session_id), \
        ClientSession(read, write) as session:
    await session.initialize()
    result = await session.call_tool("segment", {"text": "我来到北京清华大学"})
    print(result.structuredContent)
```

**SSE：**

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://127.0.0.1:8001/sse", headers={...}, timeout=30, sse_read_timeout=300) as (read, write), \
        ClientSession(read, write) as session:
    await session.initialize()
    tools = await session.list_tools()
```

## 选 Streamable HTTP 还是 SSE？

| | Streamable HTTP | HTTP+SSE（旧版） |
|---|---|---|
| 端点 | 一个 URL，通常是 `/mcp`（POST，外加可选的 GET 流） | `GET /sse` 事件流 + `POST /messages/?session_id=…` |
| 规范中的地位 | 当前标准（自 2025-03-26 起） | 已废弃，仅为兼容保留 |
| 会话 | 可选的 `Mcp-Session-Id` 头；服务器也可以无状态 | 每条 SSE 连接对应一个会话 |
| 断线续传 | 支持（`Last-Event-ID`） | 不支持 |
| 代理 / Serverless | 普通请求-响应就能工作 | 需要长连接 |

服务器支持 Streamable HTTP 时优先用它；SSE 只留给只提供 SSE 的服务器。

## 在 MCP 应用里使用远程服务器

很多客户端可以直接填 URL，具体字段名各家略有不同。以 Cursor 的 `mcp.json` 为例：

```json
{
  "mcpServers": {
    "jieba": { "url": "http://127.0.0.1:8000/mcp" }
  }
}
```

## 常见问题

- **`405 Method Not Allowed` / `404`**：URL 和传输方式对不上。Streamable HTTP 一般在 `/mcp`，SSE 一般在 `/sse`。
- **`Redirect to … not followed`**：SDK 只跟随同源、同方法的重定向。出现这个错误，说明 URL 指向了别的服务，比如同一端口上另一个应用的登录页。
- **工具调用时间长导致超时**：调大 `--timeout`（请求超时），或调大读取超时（`sse_read_timeout` / `httpx.Timeout(read=…)`）。
- **`ImportError: streamable_http_client`**：升级到 `mcp>=1.24`。旧版 SDK 只有已废弃的 `streamablehttp_client(url, headers=…)`。

## 冒烟测试

```bash
python scripts/smoke.py                           # 默认使用 `uvx jieba-mcp`
JIEBA_MCP_CMD=jieba-mcp python scripts/smoke.py   # 已经装好 jieba-mcp 时
```

## 许可证

MIT，见 [LICENSE](LICENSE)。作者：**Feng Rongquan**，[BACH-AI-Tools](https://github.com/BACH-AI-Tools)。

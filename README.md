# Python MCP client examples (Streamable HTTP + SSE)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**English** | [简体中文](README.zh-CN.md)

Small, runnable Python programs that connect to a **remote** MCP server with the official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). They cover both HTTP transports:
- **Streamable HTTP**, the current transport;
- **HTTP+SSE**, the legacy transport that many servers still offer.

Each program initializes a session, lists the server's tools, resources and prompts, and calls a tool. The examples use [jieba-mcp](https://github.com/BACH-AI-Tools/jieba-mcp), a Chinese text-processing server you can start locally in one command, so everything below runs without any account or API key.

## Files

| File | What it shows |
|---|---|
| `src/streamable_http_demo.py` | Streamable HTTP: custom headers and timeouts via `httpx.AsyncClient`, session id, list everything, call a tool |
| `src/sse_client_example.py` | The same over the legacy SSE transport |
| `src/jieba_demo.py` | A practical client calling five jieba tools; `--transport streamable-http\|sse` |
| `src/common.py` | Shared CLI options (`--url`, `--header`, `--timeout`) and printing |
| `scripts/smoke.py` | Starts jieba-mcp, runs every example over both transports, checks the output |

## Quick start

**1. Start the demo server.** Run each transport in its own terminal:

```bash
uvx jieba-mcp --transport streamable-http --port 8000   # http://127.0.0.1:8000/mcp
uvx jieba-mcp --transport sse --port 8001               # http://127.0.0.1:8001/sse
```

- Until jieba-mcp is on PyPI, use `uvx --from git+https://github.com/BACH-AI-Tools/jieba-mcp jieba-mcp` in place of `uvx jieba-mcp`.
- If port 8000 is taken, pick another port and pass a matching `--url` below.

**2. Install the client dependencies** (Python 3.10+):

```bash
pip install -r requirements.txt
```

**3. Run the examples:**

```bash
python src/streamable_http_demo.py
python src/sse_client_example.py --url http://127.0.0.1:8001/sse
python src/jieba_demo.py
python src/jieba_demo.py --transport sse --url http://127.0.0.1:8001/sse
```

Real output, trimmed. The session id differs on every run.

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

The SSE run of `jieba_demo.py` prints the same output.

## Connect to your own server

```bash
python src/streamable_http_demo.py --url https://example.com/mcp \
    --header 'Authorization: Bearer <your-token>'
```

You can also set `MCP_SERVER_URL` instead of passing `--url`. Header values are masked when printed. Keep real tokens in environment variables or a local, git-ignored `.env`, never in code.

## The core code

**Streamable HTTP** (`mcp>=1.24`):

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

**SSE:**

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async with sse_client("http://127.0.0.1:8001/sse", headers={...}, timeout=30, sse_read_timeout=300) as (read, write), \
        ClientSession(read, write) as session:
    await session.initialize()
    tools = await session.list_tools()
```

## Streamable HTTP or SSE?

| | Streamable HTTP | HTTP+SSE (legacy) |
|---|---|---|
| Endpoint | one URL, usually `/mcp` (POST, plus an optional GET stream) | `GET /sse` for the event stream + `POST /messages/?session_id=…` |
| Status in the spec | current (since 2025-03-26) | deprecated, kept for compatibility |
| Sessions | optional `Mcp-Session-Id` header; servers may be stateless | one session per open SSE connection |
| Resuming a dropped stream | supported with `Last-Event-ID` | not supported |
| Proxies / serverless | plain request/response works | needs a long-lived connection |

Use Streamable HTTP when the server offers it, and SSE only for servers that have nothing else.

## Using a remote server from an MCP app

Many clients accept a URL directly. The exact keys vary by app. For example, Cursor's `mcp.json`:

```json
{
  "mcpServers": {
    "jieba": { "url": "http://127.0.0.1:8000/mcp" }
  }
}
```

## Troubleshooting

- **`405 Method Not Allowed` / `404`:** the URL and transport don't match. Streamable HTTP servers usually listen on `/mcp`, SSE servers on `/sse`.
- **`Redirect to … not followed`:** the SDK only follows redirects that stay on the same origin and method. The URL probably points at something else, such as a login page served by another web app on the same port.
- **Timeouts on long tool calls:** raise `--timeout` (request timeout) or the read timeout (`sse_read_timeout` / `httpx.Timeout(read=…)`).
- **`ImportError: streamable_http_client`:** upgrade to `mcp>=1.24`. Older SDKs only have the deprecated `streamablehttp_client(url, headers=…)`.

## Smoke test

```bash
python scripts/smoke.py                    # uses `uvx jieba-mcp`
JIEBA_MCP_CMD=jieba-mcp python scripts/smoke.py   # if it is already installed
```

## License

MIT, see [LICENSE](LICENSE). Author: **Feng Rongquan**, [BACH-AI-Tools](https://github.com/BACH-AI-Tools).

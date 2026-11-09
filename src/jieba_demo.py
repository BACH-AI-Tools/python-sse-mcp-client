#!/usr/bin/env python3
"""A practical client: Chinese text processing through the jieba-mcp server.

python src/jieba_demo.py                                  # Streamable HTTP
python src/jieba_demo.py --transport sse --url http://127.0.0.1:8000/sse
"""

import argparse
import asyncio
import os
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client

from common import print_result

CALLS = [
    ("segment", {"text": "小明硕士毕业于中国科学院计算所", "mode": "search"}),
    ("extract_keywords", {"text": "线程是程序执行中一个单一的顺序控制流程，进程内有一个或多个线程，线程共享进程的资源", "top_k": 3, "method": "textrank"}),
    ("pos_tag", {"text": "我爱北京天安门"}),
    ("add_user_words", {"words": [{"word": "大语言模型", "tag": "nz"}]}),
    ("segment", {"text": "大语言模型正在改变软件开发"}),
    ("convert_chinese", {"text": "软件和鼠标", "config": "s2twp"}),
]  # fmt: skip


@asynccontextmanager
async def connect(transport: str, url: str):
    if transport == "sse":
        async with sse_client(url) as (read, write):
            yield read, write
    else:
        async with streamable_http_client(url) as (read, write, _):
            yield read, write


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--transport", choices=["streamable-http", "sse"], default="streamable-http"
    )
    parser.add_argument("--url", default=os.environ.get("MCP_SERVER_URL"))
    args = parser.parse_args()
    path = "/sse" if args.transport == "sse" else "/mcp"
    url = args.url or f"http://127.0.0.1:8000{path}"

    async with (
        connect(args.transport, url) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        for name, arguments in CALLS:
            print(f"\n>>> {name}")
            print_result(await session.call_tool(name, arguments))


if __name__ == "__main__":
    asyncio.run(main())

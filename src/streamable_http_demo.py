#!/usr/bin/env python3
"""Connect to an MCP server over the Streamable HTTP transport.

python src/streamable_http_demo.py --url http://127.0.0.1:8000/mcp
"""

import asyncio

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from common import (
    describe_server,
    mask_headers,
    parse_args,
    parse_headers,
    print_result,
)


async def main() -> None:
    args = parse_args(__doc__.splitlines()[0], "http://127.0.0.1:8000/mcp")
    headers = parse_headers(args.header)
    print(f"Connecting to {args.url} (Streamable HTTP)")
    if headers:
        print(f"Headers: {mask_headers(headers)}")

    # Headers, auth and timeouts live on the httpx client you pass in.
    http_client = httpx.AsyncClient(
        headers=headers,
        timeout=httpx.Timeout(args.timeout, read=300),
        follow_redirects=True,
    )
    async with (
        http_client,
        streamable_http_client(args.url, http_client=http_client) as (
            read,
            write,
            get_session_id,
        ),
        ClientSession(read, write) as session,
    ):
        init = await session.initialize()
        # Stateful servers assign a session id (Mcp-Session-Id header).
        print(f"Session id: {get_session_id() or '(stateless server)'}")
        tools = await describe_server(session, init)

        if "extract_keywords" in tools:  # the jieba-mcp demo server
            text = "我来到北京清华大学，清华大学是一所综合性大学"
            print(f'\nCalling extract_keywords {{"text": "{text}", "top_k": 3}}:')
            print_result(
                await session.call_tool("extract_keywords", {"text": text, "top_k": 3})
            )


if __name__ == "__main__":
    asyncio.run(main())

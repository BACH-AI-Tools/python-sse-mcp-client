#!/usr/bin/env python3
"""Connect to an MCP server over the (legacy) HTTP+SSE transport.

python src/sse_client_example.py --url http://127.0.0.1:8000/sse
"""

import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client

from common import (
    describe_server,
    mask_headers,
    parse_args,
    parse_headers,
    print_result,
)


async def main() -> None:
    args = parse_args(__doc__.splitlines()[0], "http://127.0.0.1:8000/sse")
    headers = parse_headers(args.header)
    print(f"Connecting to {args.url} (SSE)")
    if headers:
        print(f"Headers: {mask_headers(headers)}")

    async with (
        sse_client(
            url=args.url,
            headers=headers,
            timeout=args.timeout,  # timeout for the HTTP requests
            sse_read_timeout=300,  # how long to wait for the next SSE event
        ) as (read, write),
        ClientSession(read, write) as session,
    ):
        init = await session.initialize()
        tools = await describe_server(session, init)

        if "segment" in tools:  # the jieba-mcp demo server
            print('\nCalling segment {"text": "我来到北京清华大学"}:')
            print_result(
                await session.call_tool("segment", {"text": "我来到北京清华大学"})
            )


if __name__ == "__main__":
    asyncio.run(main())

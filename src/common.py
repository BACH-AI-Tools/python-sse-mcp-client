"""Shared helpers for the example clients: CLI options and pretty printing."""

from __future__ import annotations

import argparse
import json
import os

from mcp import ClientSession
from mcp.types import CallToolResult, InitializeResult


def parse_args(description: str, default_url: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--url",
        default=os.environ.get("MCP_SERVER_URL", default_url),
        help=f"MCP server endpoint (default: $MCP_SERVER_URL or {default_url})",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="'Name: value'",
        help="Extra HTTP header, e.g. 'Authorization: Bearer <token>'. Repeatable.",
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="HTTP timeout in seconds."
    )
    return parser.parse_args()


def parse_headers(values: list[str]) -> dict[str, str]:
    headers = {}
    for value in values:
        name, sep, content = value.partition(":")
        if not sep or not name.strip():
            raise SystemExit(f"--header must look like 'Name: value', got {value!r}")
        headers[name.strip()] = content.strip()
    return headers


def mask_headers(headers: dict[str, str]) -> dict[str, str]:
    """Never print credentials: keep only the last 4 characters."""
    return {k: "***" + v[-4:] if len(v) > 4 else "***" for k, v in headers.items()}


async def describe_server(session: ClientSession, init: InitializeResult) -> list[str]:
    """Print server info and everything it offers. Returns the tool names."""
    print(f"Server: {init.serverInfo.name} {init.serverInfo.version}")
    print(f"Protocol version: {init.protocolVersion}")
    caps = init.capabilities

    tools = (await session.list_tools()).tools
    print(f"\nTools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool.name}: {(tool.description or '').splitlines()[0]}")
        schema = tool.inputSchema or {}
        required = set(schema.get("required", []))
        for name, info in schema.get("properties", {}).items():
            kind = info.get("type") or "/".join(
                str(x.get("type")) for x in info.get("anyOf", [])
            )
            flag = "required" if name in required else "optional"
            print(f"      {name} ({kind or 'any'}, {flag})")

    if caps.resources:
        resources = (await session.list_resources()).resources
        print(f"\nResources ({len(resources)}):")
        for res in resources:
            print(f"  - {res.uri} {res.name or ''}")
    if caps.prompts:
        prompts = (await session.list_prompts()).prompts
        print(f"\nPrompts ({len(prompts)}):")
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description or ''}")
    return [t.name for t in tools]


def print_result(result: CallToolResult) -> None:
    if result.isError:
        text = " ".join(getattr(c, "text", "") for c in result.content)
        raise RuntimeError(f"tool returned an error: {text}")
    if result.structuredContent is not None:
        print(json.dumps(result.structuredContent, ensure_ascii=False))
    else:
        for content in result.content:
            print(getattr(content, "text", content))

#!/usr/bin/env python3
"""End-to-end smoke test: start jieba-mcp, run every example against it.

    python scripts/smoke.py

The server command defaults to `uvx jieba-mcp`; override it with
JIEBA_MCP_CMD, e.g. JIEBA_MCP_CMD="jieba-mcp" if it is already installed.
"""

import os
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER_CMD = shlex.split(os.environ.get("JIEBA_MCP_CMD", "uvx jieba-mcp"))

# (transport, script, expected substrings in stdout)
CASES = [
    ("sse", "src/sse_client_example.py", ["Server: jieba", "清华大学"]),
    ("streamable-http", "src/streamable_http_demo.py", ["Session id:", "清华大学"]),
    (
        "streamable-http",
        "src/jieba_demo.py",
        ["中国科学院", "大语言模型", "軟體和滑鼠"],
    ),
    ("sse", "src/jieba_demo.py", ["中国科学院", "大语言模型", "軟體和滑鼠"]),
]


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_port(port: int, proc: subprocess.Popen, timeout: float = 180) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early with code {proc.returncode}")
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.3)
    raise TimeoutError(f"server did not listen on port {port} in {timeout}s")


def run_case(transport: str, script: str, expected: list[str]) -> None:
    port = free_port()
    path = "/sse" if transport == "sse" else "/mcp"
    server = subprocess.Popen(
        [*SERVER_CMD, "--transport", transport, "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_port(port, server)
        args = [sys.executable, script, "--url", f"http://127.0.0.1:{port}{path}"]
        if script.endswith("jieba_demo.py"):
            args += ["--transport", transport]
        out = subprocess.run(
            args, check=False, cwd=ROOT, capture_output=True, text=True, timeout=120
        )
        missing = [e for e in expected if e not in out.stdout]
        if out.returncode != 0 or missing:
            print(out.stdout, out.stderr, sep="\n")
            raise AssertionError(
                f"{script} ({transport}): rc={out.returncode}, missing={missing}"
            )
        print(f"ok  {script:32} {transport}")
    finally:
        server.terminate()
        server.wait(timeout=10)


def main() -> None:
    for case in CASES:
        run_case(*case)
    print("all examples passed")


if __name__ == "__main__":
    main()

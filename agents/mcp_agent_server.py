#!/usr/bin/env python3
"""
mcp_agent_server.py — MCP stdio server wrapping TrueAgenticAgent.

Register once with:
    claude mcp add ig-agent -- python3 /home/mrnob0dy666/imsgct/imscribing_grammar/agents/mcp_agent_server.py

Exposes one tool: run_agent(task, model?)
"""

import asyncio
import sys
from pathlib import Path

# Ensure the agents package and its parent are importable
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
for _p in [str(_HERE), str(_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult

server = Server("ig-agent")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="run_agent",
            description=(
                "Run a task through TrueAgenticAgent — the grammar-optimal "
                "THINK→ACT→OBSERVE→UPDATE loop (O∞, Frobenius-closed). "
                "Runs on OpenRouter via OPENROUTER_API_KEY."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task to execute",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model alias or full ID (default: grok-4)",
                        "default": "grok-4",
                    },
                },
                "required": ["task"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    if name != "run_agent":
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True,
        )

    task = arguments.get("task", "")
    model = arguments.get("model", "grok-4")

    try:
        from true_agentic_agent import TrueAgenticAgent
        agent = TrueAgenticAgent(model=model)
        result = await agent.run(task)
        text = result if isinstance(result, str) else str(result)
    except Exception as exc:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Agent error: {exc}")],
            isError=True,
        )

    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        isError=False,
    )


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

"""
Tool System for Claude API Agents (Async)
Provides common tool definitions, a dynamic tool registry, and an asynchronous executor.
"""
import asyncio
import os
import json
import httpx
import logging
from typing import Dict, List, Any, Callable, Awaitable, Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Dynamic registry for tool definitions and handlers.
    Allows runtime registration via register() or the @tool_handler decorator.
    """

    def __init__(self):
        self._definitions: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Any]]] = {}

    def register(
        self,
        name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Any]],
        description: str,
        input_schema: Dict[str, Any],
    ) -> None:
        """Register a tool with its handler and schema definition."""
        self._definitions[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
        }
        self._handlers[name] = handler
        logger.debug(f"Registered tool: {name}")

    def tool_handler(self, name: str, description: str, input_schema: Dict[str, Any]):
        """Decorator to register an async function as a tool handler."""
        def decorator(fn: Callable[[Dict[str, Any]], Awaitable[Any]]):
            self.register(name, fn, description, input_schema)
            return fn
        return decorator

    def get_definition(self, name: str) -> Optional[Dict[str, Any]]:
        return self._definitions.get(name)

    def get_handler(self, name: str) -> Optional[Callable]:
        return self._handlers.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self._definitions.values())

    def has_tool(self, name: str) -> bool:
        return name in self._handlers


# Global shared registry — adapted projects can register their domain-specific tools here
global_registry = ToolRegistry()


class ToolDefinitions:
    """
    Common tool definitions in Claude API format.
    """

    @staticmethod
    def file_read() -> Dict[str, Any]:
        return {
            "name": "file_read",
            "description": "Read the contents of a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"}
                },
                "required": ["path"]
            }
        }

    @staticmethod
    def file_write() -> Dict[str, Any]:
        return {
            "name": "file_write",
            "description": "Write content to a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }

    @staticmethod
    def run_command() -> Dict[str, Any]:
        return {
            "name": "run_command",
            "description": "Execute a shell command",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds"}
                },
                "required": ["command"]
            }
        }

    @staticmethod
    def web_fetch() -> Dict[str, Any]:
        return {
            "name": "web_fetch",
            "description": "Fetch content from a URL",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"]
            }
        }

    @staticmethod
    def json_load() -> Dict[str, Any]:
        return {
            "name": "json_load",
            "description": "Load and parse a JSON file, returning its contents as a structured object",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the JSON file to load"}
                },
                "required": ["path"]
            }
        }

    @staticmethod
    def json_save() -> Dict[str, Any]:
        return {
            "name": "json_save",
            "description": "Serialize data to JSON and write it to a file",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Destination file path"},
                    "data": {"description": "Data to serialize as JSON"},
                    "indent": {"type": "integer", "description": "JSON indentation level (default: 2)"}
                },
                "required": ["path", "data"]
            }
        }

    @staticmethod
    def list_directory() -> Dict[str, Any]:
        return {
            "name": "list_directory",
            "description": "List files and directories at a given path",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list"},
                    "recursive": {"type": "boolean", "description": "Whether to list recursively"}
                },
                "required": ["path"]
            }
        }

    @staticmethod
    def get_all_basic_tools() -> List[Dict[str, Any]]:
        return [
            ToolDefinitions.file_read(),
            ToolDefinitions.file_write(),
            ToolDefinitions.run_command(),
            ToolDefinitions.web_fetch(),
            ToolDefinitions.json_load(),
            ToolDefinitions.json_save(),
            ToolDefinitions.list_directory(),
        ]


class ToolExecutor:
    """
    Asynchronously executes tool calls.
    Checks the global ToolRegistry first, then falls back to built-in handlers.
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or global_registry
        self.handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Any]]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        self.handlers["file_read"] = self._handle_file_read
        self.handlers["file_write"] = self._handle_file_write
        self.handlers["run_command"] = self._handle_run_command
        self.handlers["web_fetch"] = self._handle_web_fetch
        self.handlers["json_load"] = self._handle_json_load
        self.handlers["json_save"] = self._handle_json_save
        self.handlers["list_directory"] = self._handle_list_directory

    def register_handler(self, tool_name: str, handler_func: Callable[[Dict[str, Any]], Awaitable[Any]]):
        """Register a handler directly on this executor instance."""
        self.handlers[tool_name] = handler_func

    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        # Check global registry first (allows runtime-registered custom tools)
        if self.registry.has_tool(tool_name):
            handler = self.registry.get_handler(tool_name)
        elif tool_name in self.handlers:
            handler = self.handlers[tool_name]
        else:
            return f"Error: No handler registered for tool: {tool_name}"

        try:
            return await handler(tool_input)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"

    async def _handle_file_read(self, tool_input: Dict[str, Any]) -> str:
        path = tool_input["path"]
        def sync_read():
            with open(path, 'r') as f:
                return f.read()
        return await asyncio.to_thread(sync_read)

    async def _handle_file_write(self, tool_input: Dict[str, Any]) -> str:
        path = tool_input["path"]
        content = tool_input["content"]
        def sync_write():
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        return await asyncio.to_thread(sync_write)

    async def _handle_run_command(self, tool_input: Dict[str, Any]) -> str:
        command = tool_input["command"]
        timeout = tool_input.get("timeout", 30)

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            result = stdout.decode().strip()
            error = stderr.decode().strip()
            return f"STDOUT: {result}\nSTDERR: {error}" if error else result
        except asyncio.TimeoutError:
            process.kill()
            return "Error: Command timed out"

    async def _handle_web_fetch(self, tool_input: Dict[str, Any]) -> str:
        url = tool_input["url"]
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text

    async def _handle_json_load(self, tool_input: Dict[str, Any]) -> Any:
        path = tool_input["path"]
        def sync_load():
            with open(path, 'r') as f:
                return json.load(f)
        data = await asyncio.to_thread(sync_load)
        return json.dumps(data, indent=2)

    async def _handle_json_save(self, tool_input: Dict[str, Any]) -> str:
        path = tool_input["path"]
        data = tool_input["data"]
        indent = tool_input.get("indent", 2)
        def sync_save():
            with open(path, 'w') as f:
                json.dump(data, f, indent=indent)
            return f"Successfully saved JSON to {path}"
        return await asyncio.to_thread(sync_save)

    async def _handle_list_directory(self, tool_input: Dict[str, Any]) -> str:
        path = tool_input["path"]
        recursive = tool_input.get("recursive", False)

        def sync_list():
            entries = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    for name in dirs:
                        rel = os.path.relpath(os.path.join(root, name), path)
                        entries.append(f"[dir]  {rel}/")
                    for name in files:
                        rel = os.path.relpath(os.path.join(root, name), path)
                        entries.append(f"[file] {rel}")
            else:
                for name in sorted(os.listdir(path)):
                    full = os.path.join(path, name)
                    tag = "[dir] " if os.path.isdir(full) else "[file]"
                    entries.append(f"{tag} {name}")
            return "\n".join(entries)

        return await asyncio.to_thread(sync_list)

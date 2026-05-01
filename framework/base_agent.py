"""
Base Agent Framework with Multi-Provider LLM Support (Async)
"""
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import os
import asyncio
import logging
import json
from datetime import datetime
from .enhanced_llm_provider import get_llm_provider
from .tools import ToolExecutor

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseAgent(ABC):
    """
    Abstract base class for LLM agents with multi-provider support and autonomous tool use.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        capabilities: List[str],
        config: Dict[str, Any],
        persona: Optional[str] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.config = config
        # Optional named persona shapes the system prompt identity.
        # Inspired by the role-specialization pattern from downstream projects.
        self.persona = persona or name

        self.status = AgentStatus.IDLE
        self.artifacts = []
        self.results = {}
        self.start_time = None
        self.end_time = None

        # Tools
        self.tool_executor = ToolExecutor()
        self.provider = self._setup_llm_provider()

    def _setup_llm_provider(self):
        provider_name = self.config.get("provider", "anthropic")
        model = self.config.get("model", "claude-3-5-sonnet-20241022")

        try:
            return get_llm_provider(provider_name, model=model)
        except ValueError as e:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                return get_llm_provider('anthropic', model=model)
            else:
                raise e

    # ------------------------------------------------------------------
    # Response post-processing
    # ------------------------------------------------------------------

    @staticmethod
    def clean_response(text: str) -> str:
        """
        Strip LLM formatting artifacts from a response string.

        Removes:
        - Fenced code blocks (```lang ... ```)
        - XML-style reasoning / thinking tags (<think>…</think>, <reasoning>…</reasoning>)
        - Leading "FINAL ANSWER:" prefix
        - Excess leading/trailing whitespace
        """
        # Strip XML reasoning tags (DeepSeek-R1 / Qwen reasoning models emit these)
        text = re.sub(r"<(think|thinking|reasoning)>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Strip fenced code blocks but keep their content
        text = re.sub(r"```[a-zA-Z]*\n?", "", text)
        text = text.replace("```", "")
        # Strip "FINAL ANSWER:" prefix if present
        if "FINAL ANSWER:" in text:
            text = text.split("FINAL ANSWER:", 1)[1]
        return text.strip()

    @staticmethod
    def extract_json_blocks(text: str) -> List[Dict[str, Any]]:
        """
        Extract all JSON objects from a text that may contain multiple ```json blocks
        or bare JSON objects. Returns a list of parsed dicts.

        Handles nested objects correctly via JSONDecoder.raw_decode — the old
        regex approach ({[^{}]*}) silently dropped any response with nested keys.
        """
        results = []

        # 1. Try fenced ```json ... ``` blocks first (pre-cleaning pass)
        fenced = re.findall(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        for raw in fenced:
            raw = raw.strip()
            if raw.startswith("{"):
                try:
                    results.append(json.loads(raw))
                except json.JSONDecodeError:
                    pass

        if results:
            return results

        # 2. Walk the string and decode every top-level { ... } (handles nesting)
        decoder = json.JSONDecoder()
        i = 0
        while i < len(text):
            if text[i] == "{":
                try:
                    obj, end_idx = decoder.raw_decode(text, i)
                    if isinstance(obj, dict):
                        results.append(obj)
                    i += end_idx - i
                    continue
                except json.JSONDecodeError:
                    pass
            i += 1

        return results

    # ------------------------------------------------------------------
    # LLM interaction
    # ------------------------------------------------------------------

    async def call_llm(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system: str = "You are a helpful assistant."
    ) -> str:
        """
        Call LLM with support for both raw string prompts and message lists.
        """
        if isinstance(prompt, str):
            final_prompt = prompt
        else:
            prompt_parts = []
            for m in prompt:
                role = m.get('role', 'user').upper()
                content = m.get('content', '')
                prompt_parts.append(f"{role}: {content}")
            final_prompt = f"SYSTEM: {system}\n" + "\n".join(prompt_parts)

        return await self.provider.query(
            final_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

    async def execute_with_tools(
        self,
        task: str,
        max_iterations: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Thinking/Acting loop:
        1. Prompt LLM with task and available tools
        2. LLM identifies tool call (JSON block)
        3. Agent executes tool and feeds result back
        4. Repeat until final answer or max iterations
        """
        messages = [{"role": "user", "content": task}]
        tools = self.get_tools()

        system_prompt = f"""You are {self.persona}. {self.description}
Capabilities: {', '.join(self.capabilities)}

Available Tools: {json.dumps(tools, indent=2)}

To use a tool, output a JSON block like this:
```json
{{
  "tool": "tool_name",
  "input": {{"param": "value"}}
}}
```
When you have the final answer, prefix it with 'FINAL ANSWER:'.
"""

        for i in range(max_iterations):
            response = await self.call_llm(messages, system=system_prompt)

            # Extract all JSON blocks; try first valid tool call
            json_blocks = self.extract_json_blocks(response)
            tool_call = next(
                (b for b in json_blocks if "tool" in b),
                None
            )

            if tool_call:
                tool_name = tool_call.get("tool")
                tool_input = tool_call.get("input", {})

                print(f"[{self.name}] Executing tool: {tool_name}")
                result = await self.tool_executor.execute_tool(tool_name, tool_input)

                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Tool Result: {result}"})
                continue

            if "FINAL ANSWER:" in response:
                return self.clean_response(response)

            # No tool call and no FINAL ANSWER — return cleaned response
            return self.clean_response(response)

        return "Error: Max iterations reached without final answer."

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    def get_tools(self) -> List[Dict[str, Any]]:
        return []

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.status = AgentStatus.RUNNING
        self.start_time = datetime.now()
        self.artifacts = []
        self.results = {}

    def complete(self, results: Dict[str, Any]) -> None:
        self.status = AgentStatus.COMPLETED
        self.end_time = datetime.now()
        self.results = results

    def fail(self, error: str) -> None:
        self.status = AgentStatus.FAILED
        self.end_time = datetime.now()
        self.results = {"error": error}

    def save_artifact(self, artifact_data: Any, artifact_type: str) -> None:
        artifact = {
            "type": artifact_type,
            "data": artifact_data,
            "timestamp": datetime.now().isoformat()
        }
        self.artifacts.append(artifact)

    def get_execution_time(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, status={self.status.value})>"

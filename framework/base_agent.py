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

# ── provider self-heal ────────────────────────────────────────────────────────
# A 402/401/403 is FATAL for one provider and harmless for the others, so it must
# not be retried and must not kill the call. Treating it as transient is what made
# `imscribe` grind: four exponential backoffs against a payment failure that will
# never clear, then a hard raise, so every mint died and the agent looped asking
# for a reagent that could not be created. ask_native already self-heals this way
# on the Rust side; the generator it shells out to never got the fix.
_FATAL_PROVIDER_CODES = ("402", "401", "403", "payment required", "insufficient", "quota")

# Preference order among providers that actually have a key on this host.
_PROVIDER_FALLBACK = [
    ("openrouter", "OPENROUTER_API_KEY"),
    ("deepseek",   "DEEPSEEK_API_KEY"),
]


def _is_fatal_provider_error(err: str) -> bool:
    e = err.lower()
    return any(c in e for c in _FATAL_PROVIDER_CODES)


def _funded_providers(exclude: set) -> list:
    """Providers with a key present, minus the ones already known broke."""
    import os
    return [n for n, k in _PROVIDER_FALLBACK if n not in exclude and os.environ.get(k)]



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
        """
        Setup LLM provider from config with prefix-syntax model resolution.

        Supports:
          - provider/model from config
          - base_url / api_key from config (for local servers and custom endpoints)
          - MODEL_ALIASES resolution (grok-4 → x-ai/grok-4.3, etc.)
          - Prefix syntax: ollama:, lm-studio:, local:, deepseek:, qwen:
          - Fallback to ANTHROPIC_API_KEY env var
        """
        provider_name = self.config.get("provider", "anthropic")
        model = self.config.get("model", "claude-3-5-sonnet-20241022")
        base_url = self.config.get("base_url", "")
        api_key = self.config.get("api_key", "")

        # Model alias resolution (from true_agentic_agent harness)
        MODEL_ALIASES = {
            "claude-opus-4":    "anthropic/claude-opus-4",
            "claude-sonnet-4":  "anthropic/claude-sonnet-4-5",
            "grok-4":           "x-ai/grok-4.3",
            "grok-4.3":         "x-ai/grok-4.3",
            "gpt-4o":           "openai/gpt-4o",
            "o3":               "openai/o3",
            "gemini-2-5-pro":   "google/gemini-2.5-pro-preview-05-06",
            "deepseek-r1":      "deepseek/deepseek-r1",
        }
        model = MODEL_ALIASES.get(model, model)

        try:
            # If base_url is provided, use it for a custom endpoint
            if base_url:
                provider = get_llm_provider(provider_name, model=model)
                # Override the provider's base URL if set
                if hasattr(provider, 'base_url'):
                    provider.base_url = base_url
                if api_key and hasattr(provider, 'api_key'):
                    provider.api_key = api_key
                return provider
            return get_llm_provider(provider_name, model=model)
        except ValueError as e:
            # Fallback: try Anthropic with env key
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
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
        system: str = "You are a helpful assistant.",
        max_retries: int = 3,
        reasoning_off: bool = False,
    ) -> str:
        """
        Call LLM with support for both raw string prompts and message lists.

        Includes exponential backoff retry for transient errors (429, 5xx, timeouts).
        Retry config inherited from true_agentic_agent harness.
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

        last_error = ""
        for attempt in range(max_retries + 1):
            try:
                return await self.provider.query(
                    final_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    reasoning_off=reasoning_off,
                )
            except Exception as exc:
                err = str(exc)
                last_error = err
                code = getattr(exc, "status_code", None)

                # 429 rate limit
                if code == 429 and attempt < max_retries:
                    delay = min(60, 2 ** (attempt + 2))
                    logger.warning(
                        f"[{self.name}] rate limited (429) — retrying in {delay}s "
                        f"(attempt {attempt+1}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                    continue

                # 5xx server errors
                if code is not None and code >= 500 and attempt < max_retries:
                    delay = 3 ** (attempt + 1)
                    logger.warning(
                        f"[{self.name}] server error {code} — retrying in {delay}s "
                        f"(attempt {attempt+1}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                    continue

                # Connection timeouts
                if "timeout" in err.lower() and attempt < max_retries:
                    delay = 10.0 * (2 ** attempt)
                    logger.warning(
                        f"[{self.name}] timeout — retrying in {delay:.0f}s "
                        f"(attempt {attempt+1}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                    continue

                # A fatal provider error is not transient: no amount of backoff buys
                # credit. Demote to the next FUNDED provider and carry on, unless the
                # caller pinned one explicitly.
                if _is_fatal_provider_error(err):
                    self._dead_providers = getattr(self, "_dead_providers", set())
                    cur = self.config.get("provider", "")
                    self._dead_providers.add(cur)
                    if self.config.get("_provider_pinned"):
                        raise RuntimeError(
                            f"[{self.name}] provider '{cur}' returned a fatal error and was "
                            f"pinned, so it was not demoted: {err}"
                        ) from exc
                    nxt = _funded_providers(self._dead_providers)
                    if nxt:
                        # The MODEL must travel with the provider. A slug is
                        # provider-scoped: carrying openrouter's
                        # `deepseek/deepseek-v4-pro` over to google turns a 402 into a
                        # 404, which is a demotion that fixes nothing. Take the new
                        # provider's own default.
                        from .enhanced_llm_provider import _get_default_model
                        self.config["provider"] = nxt[0]
                        self.config["model"] = _get_default_model(nxt[0])
                        # base_url/api_key are the OLD provider's. Left in place they
                        # are sticky and the rebuilt provider keeps posting to the dead
                        # endpoint, turning a 402 into a 401 against the same host.
                        self.config.pop("base_url", None)
                        self.config.pop("api_key", None)
                        logger.warning(
                            f"[{self.name}] provider '{cur}' fatal ({err.strip()[:60]}) — "
                            f"demoting to '{nxt[0]}' model '{self.config['model']}'"
                        )
                        self.provider = self._setup_llm_provider()
                        continue
                    raise RuntimeError(
                        f"[{self.name}] every funded provider returned a fatal error; "
                        f"last was '{cur}': {err}"
                    ) from exc

                # Other transient errors
                if attempt < max_retries:
                    delay = 2 ** (attempt + 1)
                    logger.warning(
                        f"[{self.name}] {type(exc).__name__} — retrying in {delay}s "
                        f"(attempt {attempt+1}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                    continue

                raise RuntimeError(
                    f"[{self.name}] LLM call failed after {attempt+1} attempts: {err}"
                ) from exc

        raise RuntimeError(
            f"[{self.name}] LLM call failed after all retries: {last_error}"
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

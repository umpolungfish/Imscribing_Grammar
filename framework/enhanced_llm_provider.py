"""
Enhanced LLM Provider Factory with Multi-Provider Support for AjintK (Async Version)

Provider defaults are loaded from provider_defaults.yaml configuration file.
"""
import os
import re
import json
import logging
import httpx
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .llm_provider_abc import LLMProvider

logger = logging.getLogger(__name__)

# Common retry configuration for all providers
llm_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=(
        retry_if_exception_type(httpx.HTTPStatusError) |
        retry_if_exception_type(httpx.RequestError) |
        retry_if_exception_type(asyncio.TimeoutError)
    ),
    reraise=True
)

# Provider defaults cache (loaded lazily from config)
_provider_defaults: Optional[Dict[str, Any]] = None


def _load_provider_defaults() -> Dict[str, Any]:
    """Load provider defaults from YAML config file."""
    global _provider_defaults
    
    if _provider_defaults is not None:
        return _provider_defaults
    
    # Try to load from provider_defaults.yaml
    config_paths = [
        Path(__file__).parent.parent / "provider_defaults.yaml",
        Path(__file__).parent / "provider_defaults.yaml",
        Path.cwd() / "provider_defaults.yaml",
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                import yaml
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
                    _provider_defaults = config.get("providers", {})
                    logger.info(f"Loaded provider defaults from {config_path}")
                    return _provider_defaults
            except Exception as e:
                logger.warning(f"Error loading provider config from {config_path}: {e}")
    
    # Fallback to built-in defaults
    _provider_defaults = {
        "anthropic": {
            "default_model": "claude-sonnet-4-5-20250929",
            "base_url": "https://api.anthropic.com",
        },
        "deepseek": {
            "default_model": "deepseek-chat",
            "base_url": "https://api.deepseek.com/chat/completions",
        },
        "qwen": {
            "default_model": "qwen3-max",
            "base_url": "https://api.mulerouter.ai/vendors/openai/v1/chat/completions",
        },
        "mistral": {
            "default_model": "codestral-2508",
            "base_url": "https://api.mistral.ai",
        },
        "google": {
            "default_model": "gemini-2.0-flash-exp",
            "base_url": "https://generativelanguage.googleapis.com",
        },
    }
    logger.info("Using built-in provider defaults")
    return _provider_defaults


def _get_default_model(provider: str) -> str:
    """Get default model for a provider from config."""
    defaults = _load_provider_defaults()
    provider_config = defaults.get(provider, {})
    return provider_config.get("default_model", "claude-sonnet-4-5-20250929")

class AnthropicProvider(LLMProvider):
    """LLM Provider for Anthropic's Claude models (Async)."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        # Use config-driven default if model not specified
        self.model = model or _get_default_model("anthropic")
        self.client = None

        if not self.api_key or self.api_key == "YOUR_ANTHROPIC_API_KEY_HERE":
            raise ValueError("Anthropic API key is not configured properly.")

    @llm_retry
    async def query(self, prompt: str, **kwargs) -> str:
        temp = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 4096)
        system = kwargs.get("system", "You are a helpful assistant.")

        cached_response = await self.get_cached_response(prompt, model=self.model, temperature=temp, max_tokens=max_tokens)
        if cached_response:
            return cached_response

        from anthropic import AsyncAnthropic

        if self.client is None:
            self.client = AsyncAnthropic(api_key=self.api_key)

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temp,
                system=system,
                messages=[{"role": "user", "content": prompt}]
            )

            content = message.content[0].text if message.content else ""
            await self.cache_response(prompt, content, model=self.model, temperature=temp, max_tokens=max_tokens)
            return content
        except Exception as e:
            logger.error(f"Error during Anthropic API call: {e}")
            raise


class GoogleProvider(LLMProvider):
    """LLM Provider for Google's Gemini models (Async)."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        # Use config-driven default if model not specified
        self.model_name = model or _get_default_model("google")
        self.client = None

        if not self.api_key or self.api_key == "YOUR_GOOGLE_API_KEY_HERE":
            raise ValueError("Google API key is not configured properly.")

    @llm_retry
    async def query(self, prompt: str, **kwargs) -> str:
        cached_response = await self.get_cached_response(prompt, model=self.model_name)
        if cached_response:
            return cached_response

        # Use new google.genai package (google.generativeai is deprecated)
        from google.genai import Client

        if self.client is None:
            self.client = Client(api_key=self.api_key)

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            content = response.text if response.text else ""

            await self.cache_response(prompt, content, model=self.model_name)
            return content
        except Exception as e:
            logger.error(f"Error during Google API call: {e}")
            raise


class HttpProvider(LLMProvider):
    """Base class for HTTP-based providers like DeepSeek and Qwen (Async)."""

    def __init__(self, api_key: str, model: Optional[str], base_url: str, provider_name: str):
        super().__init__()
        self.api_key = api_key
        self.provider_name = provider_name
        # Use config-driven default if model not specified
        self.model = model or _get_default_model(provider_name)
        self.base_url = base_url

    @llm_retry
    async def query(self, prompt: str, **kwargs) -> str:
        temp = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 4096)
        system = kwargs.get("system")

        cached_response = await self.get_cached_response(prompt, model=self.model, temperature=temp, max_tokens=max_tokens)
        if cached_response:
            return cached_response

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()

                full_response = response.json()
                content = full_response["choices"][0]["message"]["content"]

                if content is None:
                    # API returned null content — surface a clear error rather than
                    # crashing inside re.sub (content filter, rate limit, empty response).
                    finish_reason = full_response["choices"][0].get("finish_reason", "unknown")
                    raise ValueError(
                        f"API returned null content (finish_reason={finish_reason!r}). "
                        f"Check rate limits, content filters, or model availability."
                    )

                # Strip <think>...</think> reasoning blocks (Grok, DeepSeek-R1, etc.)
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

                await self.cache_response(prompt, content, model=self.model, temperature=temp, max_tokens=max_tokens)
                return content
        except Exception as e:
            logger.error(f"Error during API call to {self.base_url}: {e}")
            raise


class DeepSeekProvider(HttpProvider):
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, "https://api.deepseek.com/chat/completions", "deepseek")


class QwenProvider(HttpProvider):
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, "https://api.mulerouter.ai/vendors/openai/v1/chat/completions", "qwen")


class OpenRouterProvider(HttpProvider):
    """OpenRouter — OpenAI-compatible gateway to 200+ models. API key: OPENROUTER_API_KEY."""
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, "https://openrouter.ai/api/v1/chat/completions", "openrouter")


class LocalProvider(LLMProvider):
    """Direct tensor inference — no API key.

    Loads a merged Qwen3 model once (class-level singleton) and keeps it
    in GPU memory for the lifetime of the process.  Suitable for guided
    generation where 12 sequential calls would otherwise each hit a remote
    API with a thinking-token overhead.

    Model path resolution order:
      1. `model_path` constructor arg
      2. LOCAL_MODEL_PATH env var
      3. Default INFERRED merged-model path
    """

    DEFAULT_MODEL_PATH = (
        "/home/mrnob0dy666/synthomniconP/INFERRED/output"
        "/synthonicon_qlora/merged2/merged_model"
    )

    # Class-level singleton state
    _model = None
    _tokenizer = None
    _loaded_path: Optional[str] = None
    _load_lock = None  # threading.Lock, created on first use

    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        raw = model_path or os.getenv("LOCAL_MODEL_PATH") or self.DEFAULT_MODEL_PATH
        self.model_path = str(Path(raw).expanduser())

    def _ensure_loaded(self) -> None:
        import threading
        if LocalProvider._load_lock is None:
            LocalProvider._load_lock = threading.Lock()
        if LocalProvider._loaded_path == self.model_path:
            return
        with LocalProvider._load_lock:
            if LocalProvider._loaded_path == self.model_path:
                return
            import os, torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
            logger.info(f"Loading local model from {self.model_path} ...")
            tok = AutoTokenizer.from_pretrained(
                self.model_path, trust_remote_code=True
            )
            # Merged QLoRA models often lose chat_template from tokenizer_config.json.
            # Try to recover it from the base model recorded in config.json /
            # adapter_config.json.
            if tok.chat_template is None:
                import json as _j
                _base_name: Optional[str] = None
                for _cfg_name in ("config.json", "adapter_config.json"):
                    _cfg_p = Path(self.model_path) / _cfg_name
                    if _cfg_p.exists():
                        with open(_cfg_p) as _f:
                            _d = _j.load(_f)
                        _base_name = _d.get("_name_or_path") or _d.get("base_model_name_or_path")
                        if _base_name:
                            break
                if _base_name:
                    try:
                        _btok = AutoTokenizer.from_pretrained(
                            _base_name, trust_remote_code=True, local_files_only=True
                        )
                        if _btok.chat_template:
                            tok.chat_template = _btok.chat_template
                            logger.info(f"Recovered chat_template from base model: {_base_name}")
                    except Exception as _e:
                        logger.warning(
                            f"Could not recover chat_template from '{_base_name}' ({_e}). "
                            f"Fix: from the base tokenizer run "
                            f"tok.save_pretrained('{self.model_path}')."
                        )
                else:
                    logger.warning(
                        "tokenizer.chat_template is None and no base model name found in "
                        "config.json / adapter_config.json. apply_chat_template will fail."
                    )
            # Pick the GPU with the most free memory; fall back to CPU if none available
            # or if the chosen GPU is in a bad post-crash state.
            device_map: Any = "cpu"
            if torch.cuda.is_available():
                best_gpu = max(
                    range(torch.cuda.device_count()),
                    key=lambda i: torch.cuda.mem_get_info(i)[0],
                )
                free_bytes = torch.cuda.mem_get_info(best_gpu)[0]
                if free_bytes > 2 * 1024 ** 3:  # require at least 2 GB free
                    device_map = {"": best_gpu}
                    logger.info(f"Selected GPU {best_gpu} ({free_bytes // 1024**3} GB free).")
                else:
                    logger.warning("No GPU has >2 GB free; loading on CPU.")
            try:
                mdl = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map=device_map,
                    trust_remote_code=True,
                    attn_implementation="eager",
                )
                logger.info(f"Local model loaded (device_map={device_map}).")
            except Exception as e:
                logger.warning(f"Load failed ({e}); retrying on CPU.")
                mdl = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map="cpu",
                    trust_remote_code=True,
                    attn_implementation="eager",
                    torch_dtype=torch.float32,
                )
                logger.info("Local model loaded on CPU.")
            mdl.eval()
            LocalProvider._tokenizer = tok
            LocalProvider._model = mdl
            LocalProvider._loaded_path = self.model_path
            logger.info("Local model ready.")

    def _sync_generate(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_new_tokens: int,
    ) -> str:
        import torch

        self._ensure_loaded()
        tok = LocalProvider._tokenizer
        mdl = LocalProvider._model

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # enable_thinking=False: no CoT overhead for single-answer guided calls
        text = tok.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = tok(text, return_tensors="pt").to(mdl.device)

        with torch.no_grad():
            # Clear max_length from generation config so max_new_tokens is unambiguous
            if hasattr(mdl, "generation_config") and hasattr(mdl.generation_config, "max_length"):
                mdl.generation_config.max_length = None
            outputs = mdl.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature if temperature > 0 else None,
                do_sample=temperature > 0,
                pad_token_id=tok.eos_token_id,
            )

        new_tokens = outputs[0][inputs.input_ids.shape[1]:]
        response = tok.decode(new_tokens, skip_special_tokens=True).strip()
        # Strip any stray thinking blocks
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        return response

    async def query(self, prompt: str, **kwargs) -> str:
        system = kwargs.get("system")
        temperature = float(kwargs.get("temperature", 0.3))
        max_tokens = int(kwargs.get("max_tokens", 512))

        cached = await self.get_cached_response(
            prompt, model=self.model_path, temperature=temperature, max_tokens=max_tokens
        )
        if cached:
            return cached

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._sync_generate, prompt, system, temperature, max_tokens
        )

        await self.cache_response(
            prompt, result, model=self.model_path, temperature=temperature, max_tokens=max_tokens
        )
        return result


class MistralProvider(LLMProvider):
    """LLM Provider for Mistral (Async)."""
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        # Use config-driven default if model not specified
        self.model = model or _get_default_model("mistral")
        self.client = None

    @llm_retry
    async def query(self, prompt: str, **kwargs) -> str:
        system = kwargs.get("system")
        cached_response = await self.get_cached_response(prompt, model=self.model)
        if cached_response:
            return cached_response

        from mistralai import Mistral

        if self.client is None:
            self.client = Mistral(api_key=self.api_key)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            chat_response = await self.client.chat.complete_async(
                model=self.model,
                messages=messages,
            )

            if chat_response.choices:
                content = chat_response.choices[0].message.content
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                await self.cache_response(prompt, content, model=self.model)
                return content
            return "Error: No response choices from API."
        except Exception as e:
            logger.error(f"Error during Mistral API call: {e}")
            raise


class ModelRouter:
    """
    Intelligent router that selects the best provider for a given task type.

    get_provider_chain() returns an ordered preference list; get_adaptive_provider()
    walks that list and falls back to the next candidate on failure.
    """

    def __init__(self):
        self.task_model_mapping: Dict[str, List[str]] = {
            'coding':    ['aider', 'qwen', 'mistral', 'deepseek', 'anthropic'],
            'refactor':  ['aider', 'anthropic', 'qwen', 'deepseek'],
            'reasoning': ['anthropic', 'qwen', 'deepseek', 'mistral'],
            'creative':  ['anthropic', 'qwen', 'deepseek', 'mistral'],
            'analysis':  ['anthropic', 'qwen', 'deepseek', 'mistral'],
            'general':   ['qwen', 'anthropic', 'mistral', 'deepseek'],
            'synthon_generation': ['anthropic', 'qwen', 'deepseek'],
        }
        # Track which providers have failed during this session
        self._failed_providers: set = set()

    def get_provider_chain(self, task_type: str) -> List[str]:
        """Return the ordered list of provider names for a task type."""
        return self.task_model_mapping.get(task_type, ['qwen', 'anthropic', 'mistral', 'deepseek'])

    def select_best_provider(self, task_type: str) -> str:
        """Return the top-priority available provider for a task type."""
        for name in self.get_provider_chain(task_type):
            if name not in self._failed_providers:
                return name
        # All known providers have failed — reset and try first in chain
        self._failed_providers.clear()
        return self.get_provider_chain(task_type)[0]

    def mark_failed(self, provider_name: str) -> None:
        """Mark a provider as unavailable for this session."""
        self._failed_providers.add(provider_name)
        logger.warning(f"Provider '{provider_name}' marked as failed; will fall back to next in chain.")


def get_llm_provider(provider_name: str, **kwargs) -> LLMProvider:
    """
    Get LLM provider instance by name.
    
    Args:
        provider_name: Provider name (anthropic, deepseek, qwen, mistral, google, aider)
        **kwargs: Provider-specific configuration
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider not supported or API key missing
    """
    provider_name = provider_name.lower()

    # Local provider — no API key required
    if provider_name == 'local':
        return LocalProvider(model_path=kwargs.get("model_path"))

    # Special case: aider doesn't require API key (uses underlying LLM's keys)
    if provider_name == 'aider':
        from .aider_provider import AiderLLMProvider
        return AiderLLMProvider(**kwargs)

    # Canonical API key env var overrides (providers that don't follow {NAME}_API_KEY)
    _api_key_env_overrides = {
        "google": "GOOGLE_API_KEY",
        "gemini": "GOOGLE_API_KEY",
    }
    api_key_env = _api_key_env_overrides.get(provider_name, f"{provider_name.upper()}_API_KEY")
    api_key = os.getenv(api_key_env)

    if not api_key and provider_name not in ('google', 'gemini'):
        raise ValueError(f"{api_key_env} environment variable not set.")

    if provider_name == 'qwen':
        return QwenProvider(api_key=api_key, **kwargs)
    elif provider_name == 'mistral':
        return MistralProvider(api_key=api_key, **kwargs)
    elif provider_name == 'anthropic':
        return AnthropicProvider(api_key=api_key, **kwargs)
    elif provider_name in ('google', 'gemini'):
        api_key = os.getenv("GOOGLE_API_KEY")
        return GoogleProvider(api_key=api_key, **kwargs)
    elif provider_name == 'deepseek':
        return DeepSeekProvider(api_key=api_key, **kwargs)
    elif provider_name == 'openrouter':
        return OpenRouterProvider(api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")


async def get_adaptive_provider(task_type: str = "general", **kwargs) -> Tuple[LLMProvider, str]:
    """
    Return the best available provider for task_type, falling back through the
    priority chain if a provider is misconfigured or unavailable.
    """
    router = ModelRouter()
    chain = router.get_provider_chain(task_type)

    last_error: Optional[Exception] = None
    for provider_name in chain:
        try:
            provider = get_llm_provider(provider_name, **kwargs)
            logger.info(f"Adaptive provider selected: {provider_name} for task_type='{task_type}'")
            return provider, provider_name
        except (ValueError, Exception) as e:
            logger.warning(f"Provider '{provider_name}' unavailable ({e}), trying next in chain.")
            last_error = e

    raise RuntimeError(
        f"No available LLM provider for task_type='{task_type}'. "
        f"Chain tried: {chain}. Last error: {last_error}"
    )
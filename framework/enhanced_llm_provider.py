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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_exception

from .llm_provider_abc import LLMProvider

logger = logging.getLogger(__name__)

# Reasoning-token toggle. IG_THINK is the name across the repos (MODOT_THINK
# still reads); auto.py --thinking sets this module global directly. Default ON:
# the agent loop has a THINK phase, and with reasoning disabled the template
# emits a closed <think></think> before the model writes a token, so that phase
# produces nothing — which is exactly how every winding came to log an empty
# THINK line.
def _thinking_default() -> bool:
    """OFF unless asked. This global governs the ob3ect design call, whose --thinking
    flag is documented as default off and which sets this to True only when the flag
    is given. Defaulting it ON sent the local kernel's whole output into a think
    block, so `--raw` returned the empty text after `</think>`, the design call
    parsed nothing, and with --retries at its default of infinity it re-asked
    forever. The agent loop does NOT read this — it has its own IG_THINK reader and
    is on by default there, where a THINK phase is the point.

    An explicit IG_THINK=1 still turns it on here.
    """
    import os as _os
    raw = (_os.environ.get("IG_THINK") or _os.environ.get("MODOT_THINK") or "").strip().lower()
    return raw in ("1", "true", "on", "yes")


enable_thinking: bool = _thinking_default()

# Common retry configuration for all providers
def _is_retryable_http_error(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        # 4xx client errors (except 429 rate-limit) are permanent — don't retry
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False

llm_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=(
        retry_if_exception_type(httpx.RequestError) |
        retry_if_exception_type(asyncio.TimeoutError) |
        retry_if_exception(_is_retryable_http_error)
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
            "default_model": "deepseek-v4-pro",
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
            "default_model": "gemini-flash-latest",  # -latest: an exp/dated slug retires and 404s
            "base_url": "https://generativelanguage.googleapis.com",
        },
        "openrouter": {
            "default_model": "deepseek/deepseek-chat",
            "base_url": "https://openrouter.ai/api/v1/chat/completions",
        },
        "groq": {
            "default_model": "llama-3.3-70b-versatile",
            "base_url": "https://api.groq.com/openai/v1/chat/completions",
        },
    }
    logger.info("Using built-in provider defaults")
    return _provider_defaults


def _sampling_card(model_path: str) -> dict:
    """The sampling a local model's own card asks for, keyed off its path.

    Qwen3 and Qwen3.5 differ and the difference is not cosmetic: 3.5 thinks at
    temperature 1.0 and asks for a presence penalty of 1.5 where 3 asked for
    none. An unrecognized checkpoint gets Qwen3's numbers, the conservative pair.
    """
    name = (model_path or "").lower()
    if "qwen3.5" in name or "qwen3_5" in name or "qwen35" in name:
        return {"think_temp": 1.0, "instruct_temp": 0.7, "top_p": 0.8, "top_k": 20,
                "presence_penalty": 1.5}
    return {"think_temp": 0.6, "instruct_temp": 0.7, "top_p": 0.8, "top_k": 20,
            "presence_penalty": 0.0}


# Device selection lives in one place, ig_devices, so `ask --provider local`,
# this loader and the training scripts all answer to the same IG_DEVICES.
from .ig_devices import cpu_forced as _cpu_forced, devices as ig_devices, device_plan as ig_device_plan  # noqa: F401


def _get_default_model(provider: str) -> str:
    """Get default model for a provider from config."""
    defaults = _load_provider_defaults()
    provider_config = defaults.get(provider, {})
    model = provider_config.get("default_model")
    if model:
        return model
    # No silent cross-provider default. A model slug is provider-scoped, so
    # handing back some other vendor's slug turns a missing entry into a 404
    # against a healthy endpoint and hides the real fault, which is that this
    # provider has no default configured.
    raise ValueError(
        f"provider '{provider}' has no default_model configured; add one to the "
        f"provider defaults rather than inheriting another provider's slug"
    )

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
        # Clamp temperature to valid range (max 2.0 for most providers including Gemini)
        MAX_TEMP = 2.0
        if temp > MAX_TEMP:
            logger.warning(
                f"Temperature {temp} exceeds max {MAX_TEMP} for {self.provider_name}/{self.model}. "
                f"Clamping to {MAX_TEMP}."
            )
            temp = MAX_TEMP

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
        # NOTE: no reasoning switch here. `reasoning`/`reasoning_effort` is OpenRouter's
        # unified field and DeepSeek's own API 400s on it, so it is NOT vendor-neutral and
        # cannot live in the shared payload. OpenRouterProvider sends it; see there.
        # Streaming: the caller passes on_token and gets each delta as it lands.
        # The full text is still returned, so every caller downstream — the JSON
        # extractor, the cache — is unchanged; streaming is a view of the same
        # answer, not a different path through it.
        on_token = kwargs.get("on_token")
        if on_token is not None:
            data["stream"] = True
            chunks: List[str] = []
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", self.base_url, headers=headers, json=data) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        payload = line[5:].strip()
                        if payload == "[DONE]":
                            break
                        try:
                            evt = json.loads(payload)
                        except Exception:
                            continue
                        for choice in evt.get("choices") or []:
                            piece = (choice.get("delta") or {}).get("content")
                            if piece:
                                chunks.append(piece)
                                on_token(piece)
            content = "".join(chunks)
            if not content:
                raise ValueError("stream produced no content")
            await self.cache_response(prompt, content, model=self.model,
                                      temperature=temp, max_tokens=max_tokens)
            return content

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
        # Use the official OpenAI-compatible endpoint. DeepSeek accepts both
        # https://api.deepseek.com/chat/completions and /v1 variant.
        model = model or "deepseek-v4-pro"
        super().__init__(api_key, model, "https://api.deepseek.com/chat/completions", "deepseek")


class QwenProvider(HttpProvider):
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, "https://api.mulerouter.ai/vendors/openai/v1/chat/completions", "qwen")


class GroqProvider(HttpProvider):
    """Groq — OpenAI-compatible, LPU inference (very low latency). API key: GROQ_API_KEY.
    Model slugs may carry a vendor prefix (moonshotai/kimi-k2-instruct,
    openai/gpt-oss-120b); the slash is part of the id and is not stripped."""
    def __init__(self, api_key: str, model: Optional[str] = None):
        model = model or "llama-3.3-70b-versatile"
        super().__init__(api_key, model, "https://api.groq.com/openai/v1/chat/completions", "groq")


class KiloProvider(HttpProvider):
    """Kilo Code / Kilo AI Gateway — OpenAI-compatible gateway. API key: KILO_API_KEY."""
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, "https://api.kilo.ai/api/gateway/chat/completions", "kilo")


class OpenRouterProvider(HttpProvider):
    """OpenRouter — OpenAI-compatible gateway to 200+ models. API key: OPENROUTER_API_KEY."""
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model, "https://openrouter.ai/api/v1/chat/completions", "openrouter")

    @llm_retry
    async def query(self, prompt: str, **kwargs) -> str:
        temp = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 4096)
        system = kwargs.get("system")
        # Clamp temperature to valid range (max 2.0 for most models on OpenRouter)
        MAX_TEMP = 2.0
        if temp > MAX_TEMP:
            logger.warning(
                f"Temperature {temp} exceeds max {MAX_TEMP} for openrouter/{self.model}. "
                f"Clamping to {MAX_TEMP}."
            )
            temp = MAX_TEMP

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://github.com/umpolungfish/imscrbgrmr"),
            "X-Title": "Imscribing Grammar",
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
        # A trivial call (e.g. the guided imscribe pick: reply with a number) does not need a
        # reasoning model to think — that just burns the budget and stalls. Turn reasoning off
        # for it via OpenRouter's unified switch; models that always reason ignore it harmlessly.
        if kwargs.get("reasoning_off"):
            data["reasoning"] = {"enabled": False}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.base_url, headers=headers, json=data)
                response.raise_for_status()
                full_response = response.json()
                content = full_response["choices"][0]["message"]["content"]
                if content is None:
                    finish_reason = full_response["choices"][0].get("finish_reason", "unknown")
                    raise ValueError(f"API returned null content (finish_reason={finish_reason!r})")
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                return content
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.text[:800] if e.response else "no body"
            except Exception:
                body = "unreadable"
            # The comment above assumed "models that always reason ignore [reasoning:off]
            # harmlessly" — false for endpoints that make reasoning mandatory: they 400
            # instead of ignoring the switch. That's not a transient failure the @llm_retry
            # wrapper should burn attempts re-sending identically; it's a fixed request-shape
            # mismatch, so drop the switch once and resend rather than failing the call.
            if (
                e.response is not None
                and e.response.status_code == 400
                and "reasoning" in data
                and "reasoning is mandatory" in body.lower()
            ):
                logger.warning(
                    f"openrouter/{self.model} makes reasoning mandatory — retrying "
                    "without the reasoning:off switch instead of failing the call."
                )
                data.pop("reasoning", None)
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(self.base_url, headers=headers, json=data)
                    response.raise_for_status()
                    full_response = response.json()
                    content = full_response["choices"][0]["message"]["content"]
                    if content is None:
                        finish_reason = full_response["choices"][0].get("finish_reason", "unknown")
                        raise ValueError(f"API returned null content (finish_reason={finish_reason!r})")
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                    return content
            logger.error(f"HTTP {e.response.status_code} from {self.base_url}: {body}")
            raise


class LocalProvider(LLMProvider):
    """Local inference served by the Rust kernel — no API key, no second model.

    The kernel lives in Rust. Its local inference is candle running IN-PROCESS
    inside `ask_native` (ask_native/src/local.rs). To route the local model the
    SAME way MoDoT does, ob3ect does not load its own copy in Python/transformers
    — it shells out to the `ask` binary in raw mode:

        ask --provider local --raw --system <sys> --ask <prompt>

    so every `--provider local` completion is produced by the identical candle
    engine the organism uses. One brain, owned by the kernel; Python only calls
    it. (The former in-process transformers path is retained below, renamed and
    unused, in case a pure-Python fallback is ever wanted.)

    Binary resolution:
      1. MODOT_ASK_BIN env var
      2. ~/imsgct/MoDoT/ask   (the wrapper that builds/execs the native binary)

    The model the kernel loads is selected on the Rust side via
    IG_LOCAL_MODEL_DIR (default ~/models/Qwen3-1.7B, ask_native/src/local.rs), and
    the cards it runs on via IG_DEVICES — with two cards open the model is SPLIT
    across them layer by layer;
    ob3ect does not second-guess it, which is exactly what "routed the same"
    means. NOTE: the native binary must be built WITH the local provider —
    `cargo build --release --features local,cuda` (a plain build strips it).
    """

    # Retained only as the identity string for the response cache key and for the
    # renamed pure-Python fallback below. The kernel resolves the real model dir.
    DEFAULT_MODEL_PATH = "~/models/Qwen3-1.7B"

    DEFAULT_ASK_BIN = "~/imsgct/MoDoT/ask"

    # Class-level singleton state (used only by the renamed transformers fallback)
    _model = None
    _tokenizer = None
    _loaded_path: Optional[str] = None
    _load_lock = None  # threading.Lock, created on first use

    def __init__(self, model_path: Optional[str] = None, use_nested_tensor: bool = False):
        super().__init__()
        self.ask_bin = str(
            Path(os.getenv("MODOT_ASK_BIN") or self.DEFAULT_ASK_BIN).expanduser()
        )
        raw = (
            model_path
            or os.getenv("IG_LOCAL_MODEL_DIR") or os.getenv("LOCAL_MODEL_PATH")
            or os.getenv("MODOT_LOCAL_MODEL_DIR")
            or self.DEFAULT_MODEL_PATH
        )
        self.model_path = str(Path(raw).expanduser())
        self.use_nested_tensor = use_nested_tensor

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

            # Set env vars before any CUDA init (must precede torch.cuda calls).
            os.environ.setdefault("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
            os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:512")
            os.environ.setdefault("OMP_NUM_THREADS", "8")
            os.environ.setdefault("TORCH_CUDNN_V8_API_ENABLED", "1")
            os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")

            if not Path(self.model_path).exists():
                raise FileNotFoundError(
                    f"Local model path not found: {self.model_path}. "
                    f"Set IG_LOCAL_MODEL_DIR env var or pass model_path= to LocalProvider."
                )

            logger.info(f"Loading local model from {self.model_path} ...")

            tok = AutoTokenizer.from_pretrained(
                self.model_path, trust_remote_code=True, local_files_only=True,
                use_fast=False,
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
                            _base_name, trust_remote_code=True, local_files_only=True,
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
            device_map, max_memory = ig_device_plan(logger)

            # 4-bit BitsAndBytes quantization — off by default; set LOAD_IN_4BIT=1 to enable.
            load_kwargs: dict = {
                "device_map": device_map,
                "max_memory": max_memory,
                "trust_remote_code": True,
                "attn_implementation": "sdpa",  # native PyTorch SDPA; 3-5x faster than eager on long contexts
                "dtype": torch.float16,
                "low_cpu_mem_usage": True,
            }
            if max_memory is None:
                load_kwargs.pop("max_memory", None)
            if os.getenv("LOAD_IN_4BIT", "").strip() not in ("", "0"):
                from transformers import BitsAndBytesConfig
                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
                load_kwargs.pop("torch_dtype", None)
                logger.info("4-bit BitsAndBytes quantization enabled.")

            load_kwargs["local_files_only"] = True
            # ── GrammaFormer detection ──────────────────────────────────
            _cfg_p = Path(self.model_path) / "config.json"
            _is_grammaformer = False
            if _cfg_p.exists():
                try:
                    import json as _j2
                    _cfg = _j2.loads(_cfg_p.read_text())
                    _is_grammaformer = _cfg.get("_grammaformer_marker") == "grammaformer_v1"
                except Exception:
                    pass

            if _is_grammaformer:
                print("[GF] detected grammaformer; loading ...", flush=True)
                _gf_root = str(Path(__file__).resolve().parent.parent)
                import sys as _sys2
                if _gf_root not in _sys2.path:
                    _sys2.path.insert(0, _gf_root)
                from framework.grammaformer import GrammaFormerForCausalLM
                print("[GF] reading pytorch_model.bin ...", flush=True)
                mdl = GrammaFormerForCausalLM.from_pretrained(self.model_path)
                print("[GF] weights loaded to CPU.", flush=True)
                mdl = mdl.to(torch.bfloat16)
                # Pick CUDA device — wrap entirely so any cuDNN/CUDA init failure
                # falls back gracefully to CPU without crashing the agent.
                _dev_target: Any = "cpu"
                try:
                    if torch.cuda.is_available() and not _cpu_forced():
                        _cands = ig_devices() or list(range(torch.cuda.device_count()))
                        _best = max(_cands, key=lambda i: torch.cuda.mem_get_info(i)[0])
                        _free_gb = torch.cuda.mem_get_info(_best)[0] / 1024 ** 3
                        _model_gb = sum(p.numel() * p.element_size()
                                       for p in mdl.parameters()) / 1024 ** 3
                        print(f"[GF] GPU {_best}: {_free_gb:.1f} GB free, model {_model_gb:.1f} GB (bf16)", flush=True)
                        if _free_gb > _model_gb + 1.5:
                            _dev_target = _best
                        else:
                            print(f"[GF] not enough VRAM; staying on CPU.", flush=True)
                    if _dev_target != "cpu":
                        print(f"[GF] moving to cuda:{_dev_target} ...", flush=True)
                        mdl = mdl.to(_dev_target)
                except Exception as _cuda_err:
                    print(f"[GF] CUDA unavailable ({type(_cuda_err).__name__}: {_cuda_err}); using CPU.", flush=True)
                    mdl = mdl.to("cpu").to(torch.float32)
                    _dev_target = "cpu"
                mdl.eval()
                print(f"[GF] ready on {mdl.device}.", flush=True)
            else:
                try:
                    mdl = AutoModelForCausalLM.from_pretrained(self.model_path, **load_kwargs)
                    logger.info(f"Local model loaded (device_map={device_map}).")
                except Exception as e:
                    logger.warning(f"Load failed ({e}); retrying on CPU.")
                    load_kwargs["device_map"] = "cpu"
                    load_kwargs.pop("max_memory", None)
                    load_kwargs["dtype"] = torch.float32
                    load_kwargs.pop("quantization_config", None)
                    mdl = AutoModelForCausalLM.from_pretrained(self.model_path, **load_kwargs)
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
        stream: bool = False,
        on_token=None,
    ) -> str:
        """Route local inference through the Rust kernel (candle in-process)."""
        if on_token is not None:
            return self._stream_generate(prompt, system, temperature, max_new_tokens, on_token)
        return self._kernel_generate(prompt, system, temperature, max_new_tokens, stream)

    def _stream_generate(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_new_tokens: int,
        on_token,
    ) -> str:
        """Generate in-process, handing back each token as the model produces it.

        The weights are already resident here, so generation can be watched
        directly rather than inferred from a subprocess's stderr: transformers'
        TextIteratorStreamer puts decoded text on a queue as it is generated,
        `generate` runs on a worker thread, and this loop drains the queue,
        calling `on_token` per piece and accumulating the whole answer to return.

        Sampling follows the model's card, the same table the non-streaming path
        uses. The full text is still the return value, so a streaming call and a
        silent one produce the same answer by the same route.
        """
        import threading
        import torch
        from transformers import TextIteratorStreamer

        self._ensure_loaded()
        tok = LocalProvider._tokenizer
        mdl = LocalProvider._model

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        text = tok.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=enable_thinking,
        )
        inputs = tok(text, return_tensors="pt").to(mdl.device)

        card = _sampling_card(self.model_path)
        streamer = TextIteratorStreamer(tok, skip_prompt=True, skip_special_tokens=True)
        gen_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=int(max_new_tokens),
            do_sample=temperature > 0,
            pad_token_id=tok.eos_token_id,
            eos_token_id=tok.eos_token_id,
        )
        if temperature > 0:
            gen_kwargs.update(temperature=temperature, top_p=card["top_p"], top_k=card["top_k"])

        error: List[BaseException] = []

        def _run():
            try:
                with torch.no_grad():
                    mdl.generate(**gen_kwargs)
            except BaseException as exc:            # surfaced after the drain
                error.append(exc)

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()

        pieces: List[str] = []
        for piece in streamer:
            if piece:
                pieces.append(piece)
                on_token(piece)
        worker.join()
        if error:
            raise error[0]

        response = "".join(pieces).strip()
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        return response

    def _kernel_generate(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_new_tokens: int,
        stream: bool = False,
    ) -> str:
        import subprocess

        if not Path(self.ask_bin).exists():
            raise RuntimeError(
                f"ask binary not found: {self.ask_bin}. Set MODOT_ASK_BIN, and build "
                f"it with `cargo build --release --features local,cuda` (a plain "
                f"build strips the local provider)."
            )
        cmd = [
            self.ask_bin,
            "--provider", "local",
            "--raw",
            "--temperature", str(temperature),
            "--max-tokens", str(int(max_new_tokens)),
        ]
        if system:
            cmd += ["--system", system]
        cmd += ["--ask", prompt]
        # enable_thinking mirrors MoDoT's --think toggle; keep it explicit so the
        # kernel's reasoning state matches ob3ect's, not the binary's own default.
        env = dict(os.environ)
        env["IG_THINK"] = env["MODOT_THINK"] = "1" if enable_thinking else "0"
        # The kernel writes its live token stream to STDERR (IG_LOCAL_STREAM, on
        # by default) and the finished answer to stdout. Capturing stderr is what
        # swallows the stream, so under `stream` it is left attached to the
        # terminal and the tokens appear as they are generated. stdout is still
        # captured — the answer is a return value, not a display.
        if stream:
            env.setdefault("IG_LOCAL_STREAM", "1")
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, env=env)
        else:
            proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            raise RuntimeError(
                f"kernel ask (local/raw) failed [{proc.returncode}]: "
                f"{(proc.stderr or '').strip() or proc.stdout.strip()}"
            )
        response = proc.stdout.strip()
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        return response

    def _transformers_generate(
        self,
        prompt: str,
        system: Optional[str],
        temperature: float,
        max_new_tokens: int,
    ) -> str:
        # Retained, unused: the former pure-Python in-process path. Kept so a
        # non-kernel fallback exists, but `_sync_generate` no longer calls it —
        # local inference is owned by the Rust kernel (see _kernel_generate).
        import torch

        self._ensure_loaded()
        tok = LocalProvider._tokenizer
        mdl = LocalProvider._model

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        text = tok.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking,
        )
        _dev = mdl.device

        # ── Nested-tensor path when sequences have variable length ──────
        # Tokenize → if multiple sequences with different lengths detected,
        # wrap with torch.nested.as_nested_tensor (jagged layout).
        # For single-sequence generation (standard generate), fall back to
        # the padded tensor path since transformers' generate() expects dense.
        inputs = tok(text, return_tensors="pt")
        input_ids = inputs.input_ids

        # Detect variable-length sequences in a batch context
        if hasattr(self, "use_nested_tensor") and self.use_nested_tensor and input_ids.dim() == 2:
            seq_lengths = (input_ids != tok.pad_token_id).sum(dim=1)
            if len(set(seq_lengths.tolist())) > 1:
                # Variable-length batch → wrap as jagged nested tensor
                tensors = [input_ids[i, :seq_lengths[i]] for i in range(input_ids.size(0))]
                nested_ids = torch.nested.nested_tensor(tensors, layout=torch.jagged)
                logger.info(f"Wrapped {input_ids.size(0)} variable-length sequences as nested tensor "
                            f"(lengths: {seq_lengths.tolist()})")
                # For autoregressive generation with transformers, we still need
                # the last element as a dense tensor; the nested path improves
                # encoding fidelity (⋈^ì → ⋈^ż) but we fall back to padded for generate
                input_ids = inputs.input_ids
            else:
                input_ids = inputs.input_ids
        else:
            input_ids = inputs.input_ids

        input_ids = input_ids.to(_dev)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(_dev)

        # GrammaFormer has no KV cache: truncate context and cap output to keep latency sane.
        _is_gf = type(mdl).__name__ == "GrammaFormerForCausalLM"
        if _is_gf:
            _GF_MAX_CTX = 2048
            _GF_MAX_NEW = 128
            if input_ids.shape[1] > _GF_MAX_CTX:
                print(f"[GF] truncating context {input_ids.shape[1]} → {_GF_MAX_CTX}", flush=True)
                input_ids = input_ids[:, -_GF_MAX_CTX:]
                if attention_mask is not None:
                    attention_mask = attention_mask[:, -_GF_MAX_CTX:]
            if max_new_tokens > _GF_MAX_NEW:
                print(f"[GF] capping max_new_tokens {max_new_tokens} → {_GF_MAX_NEW}", flush=True)
                max_new_tokens = _GF_MAX_NEW

        if _dev.type == "cuda":
            try:
                _w = torch.zeros(1, device=_dev)
                torch.cuda.synchronize(_dev)
                del _w
            except Exception:
                pass

        with torch.no_grad():
            # Clear max_length from generation config so max_new_tokens is unambiguous
            if hasattr(mdl, "generation_config") and hasattr(mdl.generation_config, "max_length"):
                mdl.generation_config.max_length = None
            # Sampling from the model's own card. Qwen3 non-thinking: temp=0.7,
            # top_p=0.8, top_k=20. Qwen3.5 keeps top_k=20 and adds a PRESENCE
            # penalty of 1.5 in both modes — additive, once per distinct token,
            # which is not what a repetition penalty does and cannot be spelled
            # as one. A caller temperature of 0 still means greedy.
            _is_gf = type(mdl).__name__ == "GrammaFormerForCausalLM"
            _card = _sampling_card(self.model_path)
            gen_kwargs = {
                "input_ids": input_ids,
                "max_new_tokens": max_new_tokens,
                "temperature": temperature if temperature > 0 else None,
                "do_sample": temperature > 0,
                "pad_token_id": tok.eos_token_id,
                "eos_token_id": tok.eos_token_id,
            }
            if temperature > 0:
                gen_kwargs["top_k"] = _card["top_k"]
                gen_kwargs["top_p"] = _card["top_p"]
                if _card["presence_penalty"]:
                    # transformers spells this encoder_repetition_penalty-free:
                    # the additive form is exposed as `presence_penalty` only on
                    # newer versions, so pass it when the installed generate()
                    # accepts it and say so plainly when it does not.
                    import inspect as _inspect
                    if "presence_penalty" in _inspect.signature(mdl.generate).parameters or hasattr(
                        mdl.generation_config, "presence_penalty"
                    ):
                        gen_kwargs["presence_penalty"] = _card["presence_penalty"]
                    else:
                        logger.info(
                            "transformers here has no presence_penalty; the card asks for "
                            f"{_card['presence_penalty']} and it is being left off rather than "
                            "substituted with a repetition penalty, which is a different thing."
                        )
            elif _is_gf:
                gen_kwargs["top_k"] = 20
                gen_kwargs["top_p"] = 0.8
            if attention_mask is not None:
                gen_kwargs["attention_mask"] = attention_mask
            try:
                outputs = mdl.generate(**gen_kwargs)
            except RuntimeError as _cuda_err:
                if _dev.type != "cuda" or not (
                    "cuda" in str(_cuda_err).lower() or "device" in str(_cuda_err).lower()
                ):
                    raise
                logger.warning(f"GPU generate failed ({_cuda_err}); reloading on CPU.")
                # A CUDA fault leaves the context sticky: every later CUDA call in
                # this process raises again, so the whole process stays on the host
                # from here. FORCE_CPU is how _ensure_loaded is already told that,
                # which is why the reload goes back through it rather than
                # duplicating the GrammaFormer/AutoModel branch.
                os.environ["FORCE_CPU"] = "1"
                LocalProvider._model = None
                LocalProvider._loaded_path = None
                del mdl
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass
                self._ensure_loaded()
                mdl = LocalProvider._model
                _dev = mdl.device
                gen_kwargs["input_ids"] = input_ids = input_ids.to(_dev)
                if attention_mask is not None:
                    gen_kwargs["attention_mask"] = attention_mask.to(_dev)
                outputs = mdl.generate(**gen_kwargs)

        new_tokens = outputs[0][input_ids.shape[1]:]
        response = tok.decode(new_tokens, skip_special_tokens=True).strip()
        # Strip any stray thinking blocks
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()
        return response

    async def query(self, prompt: str, **kwargs) -> str:
        system = kwargs.get("system")
        temperature = float(kwargs.get("temperature", 0.7))
        max_tokens = int(kwargs.get("max_tokens", 512))

        cached = await self.get_cached_response(
            prompt, model=self.model_path, temperature=temperature, max_tokens=max_tokens
        )
        if cached:
            return cached

        # `on_token` is the streaming request, and it is served in-process: the
        # weights are already here, so the tokens are handed over as the model
        # produces them rather than read off a subprocess's stderr.
        on_token = kwargs.get("on_token")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._sync_generate, prompt, system, temperature, max_tokens,
            on_token is not None, on_token,
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
            'coding':    ['aider', 'qwen', 'mistral', 'deepseek'],
            'refactor':  ['aider', 'qwen', 'deepseek', 'mistral'],
            'reasoning': ['qwen', 'deepseek', 'mistral'],
            'creative':  ['qwen', 'deepseek', 'mistral'],
            'analysis':  ['qwen', 'deepseek', 'mistral'],
            'general':   ['qwen', 'mistral', 'deepseek'],
            'imscription_generation': ['qwen', 'deepseek'],
        }
        # Track which providers have failed during this session
        self._failed_providers: set = set()

    def get_provider_chain(self, task_type: str) -> List[str]:
        """Return the ordered list of provider names for a task type."""
        return self.task_model_mapping.get(task_type, ['qwen', 'mistral', 'deepseek'])

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

    # IG_MODEL env var → default model when not explicitly passed
    if "model" not in kwargs or kwargs.get("model") is None:
        ig_model = os.environ.get("IG_MODEL", "").strip()
        if ig_model:
            kwargs["model"] = ig_model

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
    elif provider_name == 'groq':
        return GroqProvider(api_key=api_key, **kwargs)
    elif provider_name in ('kilo', 'kilocode'):
        return KiloProvider(api_key=api_key, **kwargs)
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
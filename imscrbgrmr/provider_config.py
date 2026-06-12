"""
Provider Configuration Utilities for Imscribing Grammar.

Loads provider-specific defaults from YAML configuration files,
eliminating hardcoded values and centralizing provider settings.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

# Default provider defaults file location
DEFAULT_PROVIDER_CONFIG = Path(__file__).parent.parent / "provider_defaults.yaml"


class ProviderConfig:
    """
    Configuration manager for LLM provider settings.
    
    Loads provider-specific defaults from YAML configuration,
    providing a centralized source of truth for provider settings.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize provider configuration.
        
        Args:
            config_path: Path to provider defaults YAML file.
                        Defaults to provider_defaults.yaml in project root.
        """
        self.config_path = config_path or DEFAULT_PROVIDER_CONFIG
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load provider configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Provider config file not found: {self.config_path}")
            self._config = self._get_builtin_defaults()
            return
        
        try:
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
            logger.info(f"Loaded provider config from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading provider config: {e}")
            self._config = self._get_builtin_defaults()
    
    def _get_builtin_defaults(self) -> Dict[str, Any]:
        """Return built-in defaults if config file is unavailable."""
        return {
            "providers": {
                "deepseek": {
                    "default_model": "deepseek-v4-pro",
                    "max_tokens_default": 4000,
                    "temperature_default": 0.7,
                },
                "anthropic": {
                    "default_model": "claude-sonnet-4-5-20250929",
                    "max_tokens_default": 4000,
                    "temperature_default": 0.7,
                },
                "qwen": {
                    "default_model": "qwen3-max",
                    "max_tokens_default": 4000,
                    "temperature_default": 0.7,
                },
                "mistral": {
                    "default_model": "codestral-2508",
                    "max_tokens_default": 4000,
                    "temperature_default": 0.7,
                },
                "google": {
                    "default_model": "gemini-2.0-flash-exp",
                    "max_tokens_default": 4000,
                    "temperature_default": 0.7,
                },
                "local": {
                    "default_model": "Imscriptiveon_qlora_merged2",
                    "max_tokens_default": 512,
                    "temperature_default": 0.3,
                },
            },
            "cli": {
                "default_provider": "deepseek",
                "max_tokens": 4000,
                "temperature": 0.3,
            },
        }
    
    def get_provider_default_model(self, provider: str) -> str:
        """
        Get the default model for a specific provider.
        
        Args:
            provider: Provider name (e.g., 'anthropic', 'deepseek', 'qwen')
            
        Returns:
            Default model name for the provider
        """
        providers = self._config.get("providers", {})
        provider_config = providers.get(provider, {})
        return provider_config.get("default_model", self._get_fallback_model(provider))
    
    def _get_fallback_model(self, provider: str) -> str:
        """Return a fallback model if provider is unknown."""
        fallbacks = {
            "deepseek": "deepseek-v4-pro",
            "anthropic": "claude-sonnet-4-5-20250929",
            "qwen": "qwen3-max",
            "mistral": "codestral-2508",
            "google": "gemini-2.0-flash-exp",
        }
        return fallbacks.get(provider.lower(), "deepseek-v4-pro")
    
    def get_provider_defaults(self, provider: str) -> Dict[str, Any]:
        """
        Get all default settings for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Dictionary of provider settings
        """
        providers = self._config.get("providers", {})
        return providers.get(provider, {})
    
    def get_cli_defaults(self) -> Dict[str, Any]:
        """Get CLI-level default settings, with env-var overrides."""
        defaults = dict(self._config.get("cli", {}))
        env_provider = os.environ.get("IG_PROVIDER") or os.environ.get("IG_DEFAULT_PROVIDER")
        if env_provider:
            defaults["default_provider"] = env_provider
        return defaults
    
    def get_task_routing(self, task_type: str) -> Dict[str, Any]:
        """
        Get task-based routing configuration.
        
        Args:
            task_type: Task type (e.g., 'coding', 'reasoning', 'imscription_generation')
            
        Returns:
            Routing configuration for the task type
        """
        routing = self._config.get("task_routing", {})
        return routing.get(task_type, {})
    
    def get_all_providers(self) -> list[str]:
        """Get list of all configured providers."""
        return list(self._config.get("providers", {}).keys())
    
    def get_provider_models(self, provider: str) -> list[Dict[str, Any]]:
        """
        Get all available models for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            List of model configurations
        """
        providers = self._config.get("providers", {})
        provider_config = providers.get(provider, {})
        return provider_config.get("models", [])


# Global provider config instance (lazy-loaded)
_provider_config: Optional[ProviderConfig] = None


def get_provider_config(config_path: Optional[Path] = None) -> ProviderConfig:
    """
    Get the global provider configuration instance.
    
    Args:
        config_path: Optional custom config path
        
    Returns:
        ProviderConfig instance
    """
    global _provider_config
    if _provider_config is None:
        _provider_config = ProviderConfig(config_path)
    return _provider_config


def get_default_model_for_provider(provider: str) -> str:
    """
    Convenience function to get default model for a provider.
    
    Args:
        provider: Provider name
        
    Returns:
        Default model name
    """
    config = get_provider_config()
    return config.get_provider_default_model(provider)


def build_agent_config(
    provider: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build a complete agent configuration with provider-aware defaults.
    
    Args:
        provider: LLM provider name
        model: Optional model name (uses provider default if not specified)
        max_tokens: Optional max tokens (uses provider default if not specified)
        temperature: Optional temperature (uses provider default if not specified)
        
    Returns:
        Complete agent configuration dictionary
    """
    config = get_provider_config()
    provider_defaults = config.get_provider_defaults(provider)
    
    # Build config with cascading defaults
    resolved_model = model or provider_defaults.get("default_model", config.get_provider_default_model(provider))
    # Sanitize model for direct providers (e.g. deepseek) to prevent sending
    # "deepseek:xxx" or "deepseek/deepseek-xxx" style names (which cause 400 Bad Request
    # on the native DeepSeek /chat/completions endpoint).
    if provider.lower() == "deepseek":
        if resolved_model:
            # Strip common provider prefixes: deepseek:deepseek-v4-pro, deepseek/deepseek-v4-pro, etc.
            if ":" in resolved_model:
                resolved_model = resolved_model.split(":", 1)[-1]
            if "/" in resolved_model:
                resolved_model = resolved_model.split("/")[-1]
        if not resolved_model or not (resolved_model.startswith("deepseek-") or resolved_model.startswith("deepseek")):
            resolved_model = "deepseek-v4-pro"

    result = {
        "provider": provider,
        "model": resolved_model,
        "max_tokens": max_tokens or provider_defaults.get("max_tokens_default", 4000),
        "temperature": temperature if temperature is not None else provider_defaults.get("temperature_default", 0.7),
    }
    
    # Include base URL if available
    if "base_url" in provider_defaults:
        result["base_url"] = provider_defaults["base_url"]
    
    return result

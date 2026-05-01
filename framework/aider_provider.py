"""
Aider Provider — Git-native AI pair programming integration.

This module provides two integration modes:
1. AiderLLMProvider — Direct LLM access via aider's model configuration
2. AiderCodeAgent — Full Git-aware code operations (see agents/aider_code_agent.py)

Aider uses LiteLLM under the hood with additional model configuration and Git-native workflows.
See: https://aider.chat/
"""
import asyncio
import logging
from typing import Optional, Dict, Any

from .llm_provider_abc import LLMProvider

logger = logging.getLogger(__name__)


class AiderLLMProvider(LLMProvider):
    """
    Aider LLM Provider — Direct LLM access via aider's model configuration.
    
    Uses aider's model settings but provides simple query/response interface.
    This is useful for users who want aider's model configuration without
    the Git overhead.
    
    Example:
        provider = AiderLLMProvider(model="claude-sonnet-4-5-20250929")
        response = await provider.query("Write a function...")
    """
    
    def __init__(self, model: Optional[str] = None, **kwargs):
        """
        Initialize Aider LLM provider.
        
        Args:
            model: Model name (uses aider's default if not specified)
            **kwargs: Additional provider configuration
        """
        super().__init__()
        
        # Import aider's Model class lazily
        try:
            from aider.models import Model
            self._aider_available = True
        except ImportError:
            self._aider_available = False
            logger.warning(
                "aider-chat not installed. AiderLLMProvider will fall back to LiteLLM directly. "
                "Install with: pip install aider-chat"
            )
        
        # Initialize model
        if self._aider_available:
            from aider.models import Model
            model_name = model or "nvidia/nemotron-3-nano-30b-a3b:free"
            self.main_model = Model(model_name, verbose=kwargs.get("verbose", False))
            self.model_name = model_name
        else:
            # Fallback: use model name directly with openrouter prefix
            model_name = model or "nvidia/nemotron-3-nano-30b-a3b:free"
            self.model_name = model_name
            self.main_model = type('obj', (object,), {
                'name': model_name,
                'use_temperature': True,
                'max_tokens': None,
                'info': {'max_input_tokens': 256000},
            })()
        
        self.config = kwargs
    
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Query the LLM via aider's model configuration.
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional query parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLM response text
        """
        # Check cache first
        cached = await self.get_cached_response(prompt, **kwargs)
        if cached:
            return cached
        
        if self._aider_available:
            response = await self._query_via_aider(prompt, **kwargs)
        else:
            response = await self._query_via_litellm_direct(prompt, **kwargs)
        
        # Cache the response
        await self.cache_response(prompt, response, **kwargs)
        
        return response
    
    async def _query_via_aider(self, prompt: str, **kwargs) -> str:
        """Query using aider's model configuration."""
        from aider.llm import litellm
        
        # Build messages
        messages = [{"role": "user", "content": prompt}]
        
        # For OpenRouter free models, need to use openrouter/ prefix with LiteLLM
        model_name = self.model_name
        if ':free' in model_name or model_name.startswith('nvidia/') or model_name.startswith('openrouter/'):
            if not model_name.startswith('openrouter/'):
                model_name = f"openrouter/{model_name}"
        
        # Build completion kwargs from model settings
        completion_kwargs = {
            "model": model_name,
            "messages": messages,
        }
        
        # Add model-specific settings
        if self.main_model.use_temperature:
            completion_kwargs["temperature"] = kwargs.get("temperature", 0.7)
        
        # Aider uses info dict for max_input_tokens, not direct attribute
        if hasattr(self.main_model, 'info') and self.main_model.info:
            max_tokens = self.main_model.info.get('max_input_tokens')
            if max_tokens:
                completion_kwargs["max_tokens"] = min(max_tokens, kwargs.get("max_tokens", 4000))
        elif kwargs.get("max_tokens"):
            completion_kwargs["max_tokens"] = kwargs["max_tokens"]
        
        # Add any extra params from model config
        if hasattr(self.main_model, 'extra_params') and self.main_model.extra_params:
            completion_kwargs.update(self.main_model.extra_params)
        
        # Call litellm via aider's wrapper
        try:
            response = litellm.completion(**completion_kwargs)
            
            if response.choices:
                content = response.choices[0].message.content
                
                # Log token usage if available
                if hasattr(response, 'usage') and response.usage:
                    logger.info(
                        f"AiderLLM: {response.usage.prompt_tokens} sent, "
                        f"{response.usage.completion_tokens} received"
                    )
                
                if content is None:
                    logger.warning("LLM returned None content - possible API key issue")
                    return "Error: LLM returned empty response. Check API key configuration."
                
                return content
            
            return "Error: No response choices from API."
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during Aider LLM API call: {error_msg}")
            
            # Check for common API key errors
            if "API" in error_msg or "key" in error_msg.lower() or "401" in error_msg:
                logger.error(
                    "API key error detected. For OpenRouter free models, "
                    "you may still need a free API key from https://openrouter.ai/keys"
                )
            
            raise
    
    async def _query_via_litellm_direct(self, prompt: str, **kwargs) -> str:
        """Fallback: Query using LiteLLM directly."""
        import litellm
        
        messages = [{"role": "user", "content": prompt}]
        
        # For OpenRouter free models, need to use openrouter/ prefix
        model_name = self.model_name
        if ':free' in model_name or model_name.startswith('nvidia/') or model_name.startswith('openrouter/'):
            if not model_name.startswith('openrouter/'):
                model_name = f"openrouter/{model_name}"
        
        completion_kwargs = {
            "model": model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        if kwargs.get("max_tokens"):
            completion_kwargs["max_tokens"] = kwargs["max_tokens"]
        
        try:
            response = litellm.completion(**completion_kwargs)
            
            if response.choices:
                return response.choices[0].message.content
            
            return "Error: No response choices from API."
            
        except Exception as e:
            logger.error(f"Error during LiteLLM API call: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the configured model."""
        if self._aider_available:
            return {
                "name": self.main_model.name,
                "edit_format": getattr(self.main_model, 'edit_format', None),
                "max_input_tokens": getattr(self.main_model, 'max_input_tokens', None),
                "use_temperature": getattr(self.main_model, 'use_temperature', True),
                "missing_keys": getattr(self.main_model, 'missing_keys', None),
                "keys_in_environment": getattr(self.main_model, 'keys_in_environment', False),
            }
        else:
            return {
                "name": self.main_model.name,
                "aider_available": False,
                "note": "Install aider-chat for full model configuration",
            }

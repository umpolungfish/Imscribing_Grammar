"""
Claude Agent Framework with Multi-Provider LLM Support
A reusable framework for building multi-agent systems with multiple LLM providers.
"""

import os
import sys

from .base_agent import BaseAgent, AgentStatus
from .orchestrator import AgentOrchestrator, PipelineContext
from .tools import ToolDefinitions, ToolExecutor, ToolRegistry, global_registry
from .memory import AgentMemory
from .communication import AgentCommunication, Message, MessageType
from .config_loader import (
    load_config,
    agent_config_from,
    orchestrator_config_from,
    register_presets_from_config,
)
from .enhanced_llm_provider import (
    get_llm_provider,
    get_adaptive_provider,
    AnthropicProvider,
    GoogleProvider,
    DeepSeekProvider,
    QwenProvider,
    MistralProvider,
    ModelRouter
)

__version__ = "2.1.0"

__all__ = [
    # Core agent
    "BaseAgent",
    "AgentStatus",
    # Orchestration
    "AgentOrchestrator",
    "PipelineContext",
    # Tools
    "ToolDefinitions",
    "ToolExecutor",
    "ToolRegistry",
    "global_registry",
    # Memory & communication
    "AgentMemory",
    "AgentCommunication",
    "Message",
    "MessageType",
    # Config
    "load_config",
    "agent_config_from",
    "orchestrator_config_from",
    "register_presets_from_config",
    # LLM providers
    "get_llm_provider",
    "get_adaptive_provider",
    "AnthropicProvider",
    "GoogleProvider",
    "DeepSeekProvider",
    "QwenProvider",
    "MistralProvider",
    "ModelRouter",
    # Utilities
    "clear_cache",
]


def clear_cache():
    """
    Clear all framework caches.
    
    Useful when:
    - Switching API keys
    - Changing provider configurations
    - Debugging module import issues
    
    Usage:
        from framework import clear_cache
        clear_cache()
    """
    # Clear LLM cache file
    cache_file = ".llm_cache.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f"✓ Cleared LLM cache file: {cache_file}")
    
    # Clear module cache for framework and imscrbgrmr
    modules_to_clear = [k for k in list(sys.modules.keys()) if 'framework' in k or 'imscrbgrmr' in k or 'agents' in k]
    for module in modules_to_clear:
        sys.modules.pop(module, None)
    
    print(f"✓ Cleared {len(modules_to_clear)} cached modules")
    print("⚠ Note: For complete refresh, restart your Python/shell session")

"""
YAML-Based Configuration Loader for AjintK Orchestration

Inspired by the build.yaml / config.yaml pattern used across adapted projects.
Allows entire orchestration setups — providers, agents, presets — to be declared
in a single YAML file rather than scattered across imperative Python.

Minimal example config.yaml
----------------------------
provider: anthropic
model: claude-3-5-sonnet-20241022
max_tokens: 4000
temperature: 0.7
max_concurrent_agents: 5

presets:
  full:    [hunter, triage, reporter]
  quick:   [hunter, reporter]
  redteam: [hunter, exploit]
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


def load_config(path: str | Path) -> Dict[str, Any]:
    """
    Load a YAML config file and return it as a plain dict.

    Raises FileNotFoundError if the file doesn't exist.
    Raises yaml.YAMLError on parse errors.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        raise ValueError(f"Config file must contain a YAML mapping at the top level: {path}")

    logger.info(f"Loaded config from {path}")
    return cfg


def agent_config_from(cfg: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract the agent-level config dict (provider, model, max_tokens, temperature)
    from a top-level config, with optional overrides.

    This is the dict passed to BaseAgent.__init__(config=...).
    """
    base = {
        "provider":    cfg.get("provider", "anthropic"),
        "model":       cfg.get("model", "claude-3-5-sonnet-20241022"),
        "max_tokens":  cfg.get("max_tokens", 4000),
        "temperature": cfg.get("temperature", 0.7),
    }
    if overrides:
        base.update(overrides)
    return base


def orchestrator_config_from(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the orchestrator-level config dict from a top-level config."""
    return {
        "max_concurrent_agents": cfg.get("max_concurrent_agents", 10),
        "timeout":               cfg.get("timeout", 300),
    }


def register_presets_from_config(
    orchestrator,
    cfg: Dict[str, Any],
) -> List[str]:
    """
    Read the `presets` block from a config dict and register each preset on
    the given AgentOrchestrator instance.

    Returns the list of preset names registered.

    Config format:
        presets:
          full:    [stage1, stage2, stage3]
          quick:   [stage1, stage3]
    """
    presets_cfg = cfg.get("presets", {})
    registered = []
    for name, agent_ids in presets_cfg.items():
        if not isinstance(agent_ids, list):
            logger.warning(f"Preset '{name}' must be a list of agent IDs; skipping.")
            continue
        orchestrator.register_preset(name, agent_ids)
        registered.append(name)
    return registered

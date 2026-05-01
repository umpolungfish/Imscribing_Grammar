"""
Example Agents
Pre-built agent implementations demonstrating the framework.
"""
import sys as _sys
import os as _os

# Ensure the project root is on sys.path so `framework` is importable,
# regardless of how this package is loaded.
_agents_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_agents_dir)
# Ensure project root appears BEFORE any sibling directory (e.g. INFERRED)
# that may contain a stub `agents` package shadowing this one.
try:
    _sys.path.remove(_project_root)
except ValueError:
    pass
_sys.path.insert(0, _project_root)

from .example_agent import ResearchAgent, AnalysisAgent
from .synthon_generator_agent import SynthonGeneratorAgent, SynthonGenerationResult
from .axiom_guided_generator import AxiomGuidedGeneratorAgent, AxiomGuidedResult

try:
    from .aider_code_agent import AiderCodeAgent
except ImportError:
    AiderCodeAgent = None  # optional: requires `aider` package

from .perturbation_design_agent import PerturbationDesignAgent, PerturbationDesignResult
from .ensemble_design_agent import EnsembleDesignAgent, EnsembleDesignResult
from .retrodesign_agent import RetrodesignAgent, RetrodesignAnalysisResult
from .criticality_hunting_agent import CriticalityHuntingAgent, CriticalityHuntReport
from .true_agentic_agent import TrueAgenticAgent, LoopCycle, DualToolResult

__all__ = [
    # Example agents
    "ResearchAgent",
    "AnalysisAgent",
    # Synthon generator
    "SynthonGeneratorAgent",
    "SynthonGenerationResult",
    # Axiom-guided generator
    "AxiomGuidedGeneratorAgent",
    "AxiomGuidedResult",
    # Aider code agent (optional)
    "AiderCodeAgent",
    # Protocol-layer agents (v0.3.0+)
    "PerturbationDesignAgent",
    "PerturbationDesignResult",
    "EnsembleDesignAgent",
    "EnsembleDesignResult",
    "RetrodesignAgent",
    "RetrodesignAnalysisResult",
    "CriticalityHuntingAgent",
    "CriticalityHuntReport",
    # Grammar-optimal agent (O_inf)
    "TrueAgenticAgent",
    "LoopCycle",
    "DualToolResult",
]

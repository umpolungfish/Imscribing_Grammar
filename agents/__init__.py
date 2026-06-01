"""
Agents — Pre-built agent implementations for the Imscribing Grammar.

Architecture:
  - true_agentic_agent.py     → Grammar-optimal O_inf agent (full harness)
  - paraconsistent.py         → B4 dialetheic engine (ParaVM, Belnap FOUR)
  - example_agent.py          → Framework BaseAgent examples
  - imscribe_generator_agent.py   → Universal imscription from descriptions
  - axiom_guided_generator.py     → Axiom-validated imscription generation
  - retrodesign_agent.py          → Retrosynthetic decomposition analysis
  - perturbation_design_agent.py  → Primitive Jacobian interpretation
  - criticality_hunting_agent.py  → Automated ⊙_ÿ hunting
  - ensemble_design_agent.py      → Goal-directed multi-imscription composition
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

# Example agents
from .example_agent import ResearchAgent, AnalysisAgent

# Imscription generators
from .imscribe_generator_agent import ImscriptionGeneratorAgent, ImscriptionGenerationResult
from .axiom_guided_generator import AxiomGuidedGeneratorAgent, AxiomGuidedResult

# Optional: Aider code agent
try:
    from .aider_code_agent import AiderCodeAgent
except ImportError:
    AiderCodeAgent = None  # optional: requires `aider` package

# Protocol-layer agents (v0.3.0+)
from .perturbation_design_agent import PerturbationDesignAgent, PerturbationDesignResult
from .ensemble_design_agent import EnsembleDesignAgent, EnsembleDesignResult
from .retrodesign_agent import RetrodesignAgent, RetrodesignAnalysisResult
from .criticality_hunting_agent import CriticalityHuntingAgent, CriticalityHuntReport

# Grammar-optimal agent — O_inf harness
from .true_agentic_agent import TrueAgenticAgent, LoopCycle, DualToolResult

# Paraconsistent engine — B4 dialetheic (ParaVM, Belnap FOUR)
from .paraconsistent import (
    B4,
    ParaKernel,
    ParaVM,
    BelnapCircuit,
    B4Frobenius,
    dialetheic_alignment_tri,
    self_test as para_self_test,
)

__all__ = [
    # Example agents
    "ResearchAgent",
    "AnalysisAgent",
    # Imscription generator
    "ImscriptionGeneratorAgent",
    "ImscriptionGenerationResult",
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
    # Paraconsistent B4 engine
    "B4",
    "ParaKernel",
    "ParaVM",
    "BelnapCircuit",
    "B4Frobenius",
    "dialetheic_alignment_tri",
    "para_self_test",
]

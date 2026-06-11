"""
genetic_engine — Frobenius-Guided Gene Editing Engine.

The genetic code is a stratified Frobenius algebra on B₄³ codon space.
  ⟨Ð_ω; Þ_ò; Ř_=; Φ_υ; ƒ_ð; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩
  Ouroboricity: O_∞  |  C-score: both gates open

Core modules:
  lattice    — B₄ nucleotide type system with covering relations
  codon      — Codon table with Frobenius stratum classification
  primitives — Amino acid → IG primitive mapping & risk
  editor     — B₄ lattice edit cost analysis
  stratum    — Frobenius stratum classifier
  guide      — Frobenius-aware guide RNA design
  prime      — Prime editing optimization (Frobenius template rule)
  chimera    — Tensor product risk for multi-primitive edits
  verifier   — μ∘δ=id Frobenius closure verification
  compiler   — Full editing compiler pipeline
  cli        — Command-line interface
  demo       — Demonstration and visualization functions
"""

__version__ = "1.0.0"
__author__ = "Lando \u2297 \u2299perator"

from genetic_engine.lattice import B4Element
from genetic_engine.codon import Codon, FrobeniusStratum, CODON_TABLE, ALL_CODONS
from genetic_engine.primitives import IGPrimitive, AA_PRIMITIVE_MAP, PRIMITIVE_RISK, get_primitive_delta
from genetic_engine.editor import B4EditAnalyzer, EditCostReport
from genetic_engine.stratum import FrobeniusStratumClassifier, StratumReport
from genetic_engine.guide import FrobeniusGuideDesigner, GuideDesign
from genetic_engine.prime import PrimeEditOptimizer, PrimeEditDesign
from genetic_engine.chimera import ChimeraDetector, ChimeraReport
from genetic_engine.verifier import FrobeniusVerifier, FrobeniusVerification
from genetic_engine.compiler import EditingCompiler, CompiledEdit

__all__ = [
    "B4Element",
    "Codon",
    "FrobeniusStratum",
    "CODON_TABLE",
    "ALL_CODONS",
    "IGPrimitive",
    "AA_PRIMITIVE_MAP",
    "PRIMITIVE_RISK",
    "get_primitive_delta",
    "B4EditAnalyzer",
    "EditCostReport",
    "FrobeniusStratumClassifier",
    "StratumReport",
    "FrobeniusGuideDesigner",
    "GuideDesign",
    "PrimeEditOptimizer",
    "PrimeEditDesign",
    "ChimeraDetector",
    "ChimeraReport",
    "FrobeniusVerifier",
    "FrobeniusVerification",
    "EditingCompiler",
    "CompiledEdit",
]

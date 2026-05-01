"""
Imscribing Grammar — A Unified Framework for Synthonic Systems

This package implements the theoretical framework from QUANTIG.md,
providing computational tools for analyzing self-organizing synthonic systems
across molecular, supramolecular, temporal, and cross-domain scales
using twelve formal primitives.

Validation anchor: the molecular and supramolecular domains are the primary
validation tier, grounded in experimental ΔG, crystallographic, and spectroscopic
data. Cross-domain encodings (ecological, techno-social, robotic) constitute the
extended tier — same formalism, analogue grounding.

The Seven Primitives (EXTENDED to nine):
    - Dimensionality (D): Coordinate set of operation
    - Topology (T): Internal connectivity pattern
    - Recognition Mode (R): Physical interaction mechanism
    - Polarity (P): Directional character (with symmetric/pseudosymmetric distinction)
    - Fidelity (F): Thermodynamic reliability
    - Kinetic Character (K): Kinetic accessibility — NEW
    - Granularity (G): Scale of control
    - Interaction Grammar (Γ): Partner selection logic (with Boolean algebra) — EXTENDED
    - Criticality Phase (Φ): Phase condition at G-D degeneracy — NEW

    - Stoichiometry (S): Valency ratio primitive — NEW (v2.2)

Extended Notation: ⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩  (H/Ω optional, default H0/None)
"""

from .models import (
    # Enumerations (canonical names)
    Dimensionality,
    Topology,
    Recognition,
    Polarity,
    Grammar,
    Fidelity,
    KineticChar,
    Granularity,
    Criticality,
    Protection,
    Stoichiometry,
    Chirality,
    # Backward-compat aliases
    RecognitionMode,
    KineticCharacter,
    CriticalityPhase,
    TopoIndex,
    # Backward-compat aliases for compound types
    InteractionGrammar,
    GrammarOperator,
    # Core class
    Synthon,
    CONFLICT,
    # Notation parser
    parse_notation,
)
from .registry import SynthonCatalog, global_catalog, get_validation_tier
from .constraints import (
    ConstraintEngine,
    CompatibilityMatrix,
    FidelityPropagator,
    AxiomValidator,  # NEW
)
from .thermodynamics import (
    compute_eta_CP,
    compute_xi_CP,
    compute_kinetic_fidelity,  # NEW
    compute_effective_fidelity,  # NEW
    ConstraintPropagationEfficiency,
    LANDAUER_COST_PER_BIT,
)
from .criticality import (  # NEW
    analyze_criticality,
    check_axiom5_criticality,
    find_criticality_candidates,
    CriticalityAnalysis,
)
from .transformation8 import (  # NEW - Transformation #8 probe
    analyze_dethreading_profile,
    create_rotaxane_synthon,
    compute_rotaxane_efficiency,
    check_transformation8_validation,
    DethreadingProfile,
)
from .symbolic import (  # NEW - Symbolic reasoning engine
    SymbolicReasoningEngine,
    SymbolicExpression,
    AxiomTheoremProver,
    CrossDomainAnalogyDetector,
    PredictiveRuleGenerator,
    GrammarAlgebra,
    GDTensor,
    AnalogyResult,
    PredictiveRule,
    TheoremProof,
)
from .grounding import (  # NEW - Grounding validation layer
    GroundingValidator,
    GroundingStatus,
    GroundingResult,
    PrimitiveGrounding,
    validate_synthon_with_grounding,
)
from .rdkit_utils import (  # RDKit-based ΔG estimation and structural flag extraction
    estimate_delta_g_from_smiles,
    validate_synthon_structure,
    generate_rdkit_grounding,
    DeltaGEstimationResult,
    RDKit_AVAILABLE,
    StructuralFlags,
    smiles_to_structural_flags,
    smiles_to_measurements,
)
from .llm_grounding import (  # NEW - LLM-grounded justification extraction
    extract_grounding_from_description,
    extract_and_validate,
    LLMGroundingResult,
    LLM_GROUNDING_AVAILABLE,
)
from .perturbation import (  # IG_PERTURBATION
    PerturbationEngine,
    PerturbationResult,
    PrimitiveJacobian,
    PRIMITIVE_WEIGHTS as PERTURBATION_PRIMITIVE_WEIGHTS,
)
from .trajectory import (  # IG_TRAJECTORY
    TemporalSynthonAgent,
    TrajectoryStep,
    TrajectoryValidationResult,
    StepCriticalityResult,
    ContinuityCheckResult,
)
from .ensembler import (  # IG_ENSEMBLER
    EnsembleCatalog,
    EnsembleReport,
    EnsembleCompatibilityEntry,
    EmergentPropertyResult,
)
from .retrodesign import (  # IG_RETRODESIGN
    RetrodesignEngine,
    DecompositionTree,
    DecompositionNode,
    PruningViolation,
    parse_notation_from_string,
)
from .hotswap import (  # IG_HOTSWAP
    HotSwapEngine,
    HotSwapReport,
    HotSwapDecision,
    PrimitiveCheckResult,
    validate_hotswap,
    XI_CP_TOLERANCE,
    K_MULTIPLICITY_PENALTY,
)
from .cross_domain import register_cross_domain_synthons  # Phase 1 cross-domain entries
from .domains.quantum import register_quantum_synthons      # v0.4.0 quantum/topological entries
from .domains.molecular import register_molecular_synthons  # v0.4.0 molecular catalog (.syn design files)
from .psychedelic_catalog import register_psychedelic_synthons  # v0.4.9 psychedelic synthons
from .stellar_catalog import register_stellar_synthons          # v0.4.10 stellar/compact-object catalog
from .ice_catalog import register_ice_synthons                  # v0.4.13 ice phase ladder catalog
from .particle_catalog import register_particle_synthons        # v0.4.21 fundamental particle catalog
from .millennium_catalog import register_millennium_synthons, millennium_distance_report  # v0.5.0
from .translate import (  # Translation Protocol v0.4 — structural→classical cost layer
    TranslationCost,
    TranslationStep,
    FHBAR_THRESHOLD_NATS,
    FHBAR_THRESHOLD_BITS,
    FEIGENBAUM_LAMBDA,
    LOGISTIC_BIFURCATION_1,
    CRITICALITY_LIFT_NATS,
    fhbar_satisfied,
    fhbar_deficit,
    logistic_fixed_point,
    logistic_jacobian_at_fp,
    phic_bifurcation,
    phic_from_jacobian,
    translate_fidelity,
    translate_criticality,
    translate_grammar,
    kleisli_compose,
    full_translation,
    translation_cost_summary,
)
from .monad import (  # Phase 3a — SynthonM monad transformer stack
    SynthonM,
    Context,
    StepRecord,
    DesignStrategy,
    join_m,
    meet_m,
    tensor_m,
    lift_m,
    path_m,
    assert_m,
    strategy_then,
    strategy_or,
    optimize,
)
from .syn_runner import (  # Phase 3a — .syn DSL evaluator
    SynScript,
    SynParseError,
    UnknownAssertion,
    run_syn_file,
)
from .decompose import (  # Decomposition algebra — inverse of build-up operations
    project,
    primitive_peel,
    factor,
    principal_decomp,
    cofactor,
    complement_rel,
    kernel,
    retrosynthetic_path,
    project_m,
    peel_m,
    factor_m,
    cofactor_m,
    phi_c_probe,
    topo_protection_probe,
    ProjectResult,
    PeelResult,
    FactorResult,
    PrincipalDecompResult,
    CofactorResult,
    CofactorDimension,
    ComplementResult,
    KernelResult,
    RetrosynthResult,
    RetrosynthCandidate,
)

# Auto-register cross-domain synthons on import
try:
    register_cross_domain_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register quantum/topological synthons on import
try:
    register_quantum_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register canonical molecular/supramolecular synthons on import
try:
    register_molecular_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register psychedelic synthons on import
try:
    register_psychedelic_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register stellar/compact-object synthons on import
try:
    register_stellar_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register ice phase / water synthons on import
try:
    register_ice_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register fundamental particle synthons on import
try:
    register_particle_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

# Auto-register Millennium Prize Problem synthons on import
try:
    register_millennium_synthons()
except Exception:
    pass  # Non-fatal; catalog may be read-only or already populated

__version__ = "0.5.0"  # Quantum primitives: T_braid · K_MBL · Γ(QUANTUM) · Ω · Factor 8
__author__ = "Imscribing Grammar Contributors"

__all__ = [
    # Enumerations
    "Dimensionality",
    "Topology",
    "RecognitionMode",
    "Polarity",
    "Fidelity",
    "KineticCharacter",  # NEW
    "Granularity",
    "InteractionGrammar",
    "GrammarOperator",  # NEW
    "CriticalityPhase",  # NEW
    "TopoIndex",         # NEW — Ω
    # Core classes
    "Synthon",
    "SynthonNotation",
    "parse_notation",
    # Registry
    "SynthonCatalog",
    "global_catalog",
    "get_validation_tier",
    # Constraints
    "ConstraintEngine",
    "CompatibilityMatrix",
    "FidelityPropagator",
    "AxiomValidator",  # NEW
    # Thermodynamics
    "compute_eta_CP",
    "compute_xi_CP",
    "compute_kinetic_fidelity",  # NEW
    "compute_effective_fidelity",  # NEW
    "ConstraintPropagationEfficiency",
    "LANDAUER_COST_PER_BIT",
    # Criticality (NEW)
    "analyze_criticality",
    "check_axiom5_criticality",
    "find_criticality_candidates",
    "CriticalityAnalysis",
    # Transformation #8 (NEW)
    "analyze_dethreading_profile",
    "create_rotaxane_synthon",
    "compute_rotaxane_efficiency",
    "check_transformation8_validation",
    "DethreadingProfile",
    # Symbolic Reasoning (NEW)
    "SymbolicReasoningEngine",
    "SymbolicExpression",
    "AxiomTheoremProver",
    "CrossDomainAnalogyDetector",
    "PredictiveRuleGenerator",
    "GrammarAlgebra",
    "GDTensor",
    "AnalogyResult",
    "PredictiveRule",
    "TheoremProof",
    # Grounding Validation (NEW)
    "GroundingValidator",
    "GroundingStatus",
    "GroundingResult",
    "PrimitiveGrounding",
    "validate_synthon_with_grounding",
    # RDKit Utilities (NEW)
    "estimate_delta_g_from_smiles",
    "validate_synthon_structure",
    "generate_rdkit_grounding",
    "DeltaGEstimationResult",
    "RDKit_AVAILABLE",
    # LLM Grounding (NEW)
    "extract_grounding_from_description",
    "extract_and_validate",
    "LLMGroundingResult",
    "LLM_GROUNDING_AVAILABLE",
    # Perturbation (NEW)
    "PerturbationEngine",
    "PerturbationResult",
    "PrimitiveJacobian",
    "PERTURBATION_PRIMITIVE_WEIGHTS",
    # Trajectory (NEW)
    "TemporalSynthonAgent",
    "TrajectoryStep",
    "TrajectoryValidationResult",
    "StepCriticalityResult",
    "ContinuityCheckResult",
    # Ensembler (NEW)
    "EnsembleCatalog",
    "EnsembleReport",
    "EnsembleCompatibilityEntry",
    "EmergentPropertyResult",
    # Retrodesign (NEW)
    "RetrodesignEngine",
    "DecompositionTree",
    "DecompositionNode",
    "PruningViolation",
    "parse_notation_from_string",
    # HotSwap (NEW)
    "HotSwapEngine",
    "HotSwapReport",
    "HotSwapDecision",
    "PrimitiveCheckResult",
    "validate_hotswap",
    "XI_CP_TOLERANCE",
    "K_MULTIPLICITY_PENALTY",
    # Translation Protocol v0.4 (NEW)
    "TranslationCost",
    "TranslationStep",
    "FHBAR_THRESHOLD_NATS",
    "FHBAR_THRESHOLD_BITS",
    "FEIGENBAUM_LAMBDA",
    "LOGISTIC_BIFURCATION_1",
    "CRITICALITY_LIFT_NATS",
    "fhbar_satisfied",
    "fhbar_deficit",
    "logistic_fixed_point",
    "logistic_jacobian_at_fp",
    "phic_bifurcation",
    "phic_from_jacobian",
    "translate_fidelity",
    "translate_criticality",
    "translate_grammar",
    "kleisli_compose",
    "full_translation",
    "translation_cost_summary",
    # Phase 3a — SynthonM monad (NEW)
    "SynthonM",
    "Context",
    "StepRecord",
    "DesignStrategy",
    "join_m",
    "meet_m",
    "tensor_m",
    "lift_m",
    "path_m",
    "assert_m",
    "strategy_then",
    "strategy_or",
    "optimize",
    # Phase 3a — .syn DSL runner (NEW)
    "SynScript",
    "SynParseError",
    "UnknownAssertion",
    "run_syn_file",
    # Decomposition algebra (NEW)
    "project",
    "primitive_peel",
    "factor",
    "principal_decomp",
    "cofactor",
    "complement_rel",
    "kernel",
    "retrosynthetic_path",
    "project_m",
    "peel_m",
    "factor_m",
    "cofactor_m",
    "phi_c_probe",
    "topo_protection_probe",
    "ProjectResult",
    "PeelResult",
    "FactorResult",
    "PrincipalDecompResult",
    "CofactorResult",
    "CofactorDimension",
    "ComplementResult",
    "KernelResult",
    "RetrosynthResult",
    "RetrosynthCandidate",
]

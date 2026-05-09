"""
GroundingValidator — mechanistic justification layer for synthon primitive assignments.

This module implements a pre-axiom validation step that enforces:
    "Each primitive value must be justified by reference to a specific physical 
    phenomenon, not a description keyword."

The validator catches three failure modes invisible to axiom checking:
1. Tuple collision — different chemistries assigned identical tuples
2. Semantic drift — primitives redefined silently to accommodate out-of-scope concepts
3. Keyword clustering — speculative prompts converging to attractor tuples

Usage:
    validator = GroundingValidator()
    result = validator.validate(synthon, justifications)
    if not result.is_valid:
        print(f"Ungrounded assignments: {result.ungrounded_primitives}")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum, auto

from .models import (
    Synthon,
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    Granularity,
    InteractionGrammar,
)


class GroundingStatus(Enum):
    """Status of grounding validation for a primitive."""
    GROUNDED = auto()      # Valid mechanistic justification provided
    UNGROUNDED = auto()    # No justification or keyword-only justification
    AMBIGUOUS = auto()     # Justification references multiple phenomena
    INVALID = auto()       # Justification contradicts primitive value


@dataclass
class PrimitiveGrounding:
    """Grounding result for a single primitive.

    Fix 4 (IG_FIXES.md): Added confidence and is_grounded fields
    to support per-primitive confidence scoring.
    """
    primitive: str
    value: str
    status: GroundingStatus
    justification: str
    matched_phenomena: List[str] = field(default_factory=list)
    warning: Optional[str] = None
    # Fix 4: Per-primitive confidence scoring
    confidence: float = 0.0          # 0.0–1.0 grounding confidence
    is_grounded: bool = True         # False if UNGROUNDED or INVALID
    failure_reason: Optional[str] = None          # Why grounding failed
    suggested_alternative: Optional[str] = None   # Suggested correct value

    def __post_init__(self):
        # Derive is_grounded from status if not explicitly set
        if self.status in {GroundingStatus.UNGROUNDED, GroundingStatus.INVALID}:
            self.is_grounded = False
        # Derive confidence from status if not explicitly set
        if self.confidence == 0.0:
            self.confidence = {
                GroundingStatus.GROUNDED: 0.9,
                GroundingStatus.AMBIGUOUS: 0.5,
                GroundingStatus.UNGROUNDED: 0.1,
                GroundingStatus.INVALID: 0.0,
            }.get(self.status, 0.5)


@dataclass
class GroundingResult:
    """Overall grounding validation result.

    Fix 4 (IG_FIXES.md): Added get_failed_primitives() and
    get_confidence() methods for per-primitive confidence access by
    Axioms 6 & 7 checkers.
    """
    is_valid: bool
    primitive_results: Dict[str, PrimitiveGrounding]
    ungrounded_primitives: List[str]
    warnings: List[str]
    delta_g_grounding: Optional[PrimitiveGrounding] = None  # ΔG justification

    # Fix 4: overall grounding status string
    overall_status: str = "unverified"  # "full", "partial", "failed"

    def get_failed_primitives(self) -> List[str]:
        """Return list of primitive names that failed grounding (Fix 4)."""
        return [k for k, v in self.primitive_results.items() if not v.is_grounded]

    def get_confidence(self, primitive: str) -> float:
        """Return per-primitive confidence score (Fix 4)."""
        result = self.primitive_results.get(primitive)
        return result.confidence if result else 0.0

    def justifications(self) -> Dict[str, str]:
        """Return dict of primitive -> justification_text (Fix 4)."""
        return {k: v.justification for k, v in self.primitive_results.items()}

    def __str__(self) -> str:
        if self.is_valid:
            return "✓ All primitives mechanistically grounded"
        return f"✗ {len(self.ungrounded_primitives)} ungrounded: {', '.join(self.ungrounded_primitives)}"


class GroundingValidator:
    """
    Validates that primitive assignments are mechanistically grounded.
    
    The validator maintains a vocabulary of valid physical phenomena for each
    primitive value. Justifications must reference phenomena from this vocabulary
    rather than description keywords.
    """
    
    # Grounding vocabulary: valid physical phenomena for each primitive value
    # These are extracted from QUANTIG.md transformations and examples
    GROUNDING_VOCABULARY: Dict[str, Dict[str, List[str]]] = {
        # Dimensionality (D) — coordinate set along which synthon operates
        "dimensionality": {
            "MOLECULAR": [
                "covalent bond formation",
                "intramolecular constraint",
                "single-molecule geometry",
                "bond rotation restriction",
                "conformational locking",
            ],
            "SUPRAMOLECULAR": [
                "crystal packing",
                "intermolecular recognition",
                "host-guest complexation",
                "self-assembly",
                "network formation",
                "coordination geometry",
                "metal-ligand binding",
                "π-stacking",
                "van der Waals contact",
            ],
            "TEMPORAL": [
                "closed catalytic cycle",
                "error-correction mechanism",
                "temporal periodicity",
                "oscillatory dynamics",
                "hydrolysis/re-condensation",
                "dissipative structure",
                "non-equilibrium steady state",
                "time-crystalline order",
                "Floquet driving",
                "reaction-diffusion pattern",
                "autocatalytic feedback",
            ],
        },
        
        # Topology (T) — internal connectivity pattern
        "topology": {
            "CYCLIC_BOWTIE": [
                "cyclic hydrogen bonding",
                "ring closure",
                "R₂²(8) motif",
                "base pairing",
                "dimerization interface",
                "cooperative ring current",
                "geometric constraint preventing partial dissociation",
                "cyclic closure",
                "catalytic cycle",
            ],
            "CHAIN": [
                "linear propagation",
                "polymer chain",
                "oligomer extension",
                "sequential addition",
                "end-to-end linkage",
            ],
            "HUB_NODE": [
                "coordination sphere",
                "metal node",
                "secondary building unit",
                "branch point",
                "cross-linking junction",
                "MOF node",
                "chelate geometry",
                "bite-angle constraint",
            ],
            "CAGE": [
                "self-assemble",
                "self-assembly",
                "cage-close",
                "cage close",
                "cage formation",
                "panelling",
                "face-capped",
                "face-cap",
                "encapsulate",
                "encapsulation",
                "enclose",
                "enclosure",
                "sequester",
                "portal",
                "aperture",
                "cryptand",
                "carcerand",
                "cucurbit",
                "metal-organic polyhedr",
                "covalent organic cage",
                "Fujita",
            ],
        },
        
        # Recognition Mode (R) — physical mechanism for constraint propagation
        "recognition_mode": {
            "COVALENT": [
                "covalent bond formation",
                "electron sharing",
                "orbital overlap",
                "σ-bond",
                "π-bond",
                "dynamic covalent chemistry",
            ],
            "NON_COVALENT": [
                "hydrogen bonding",
                "electrostatic interaction",
                "dispersion",
                "induction",
                "σ-hole interaction",
                "halogen bonding",
                "chalcogen bonding",
                "ion pairing",
                "dipole-dipole",
            ],
            "DYNAMIC_CATALYTIC": [
                "transition state stabilization",
                "barrier reduction",
                "enamine catalysis",
                "iminium catalysis",
                "organocatalysis",
                "metal catalysis",
                "acid/base catalysis",
                "proofreading",
                "kinetic selectivity",
            ],
            "CATALYTIC": [
                "transition state stabilization",
                "barrier reduction",
                "enamine catalysis",
                "iminium catalysis",
                "organocatalysis",
                "metal catalysis",
                "acid/base catalysis",
                "proofreading",
                "kinetic selectivity",
            ],
            "MECHANICAL": [
                "mechanical bond",
                "steric clipping",
                "rotaxane dethreading",
                "catenane interlocking",
                "topological entanglement",
                "steric cliff barrier",
                "supramolecular threading",
            ],
        },
        
        # Polarity (P) — directional character
        "polarity": {
            "DONOR": [
                "electron donor",
                "hydrogen bond donor",
                "Lewis base",
                "nucleophilic site",
                "DAD pattern donor",
            ],
            "ACCEPTOR": [
                "electron acceptor",
                "hydrogen bond acceptor",
                "Lewis acid",
                "electrophilic site",
                "ADA pattern acceptor",
            ],
            "SELF_COMPLEMENTARY_SYM": [
                "homodimerization",
                "self-assembly",
                "symmetric recognition",
                "pseudosymmetric interface",
                "identical donor and acceptor faces",
                "cyclic self-complementarity",
                "symmetric self-complementary",
            ],
            "SELF_COMPLEMENTARY_PSEUDO": [
                "homodimerization",
                "self-assembly",
                "symmetric recognition",
                "pseudosymmetric interface",
                "identical donor and acceptor faces",
                "cyclic self-complementarity",
                "pseudosymmetric self-complementary",
            ],
            "DONOR_ACCEPTOR": [
                "directional donor-acceptor pair",
                "D-A interaction",
                "complementary donor and acceptor",
            ],
        },
        
        # Fidelity (F) — reliability and persistence
        "fidelity": {
            "HIGH": [
                "proofreading",
                "kinetic selectivity",
                "thermodynamic stability",
                "high barrier to dissociation",
                "error rate < 0.1%",
                "ξ_CP < 8.5 nats",
                "cooperative fidelity amplification",
                "triple H-bond array",
                "chelate effect",
            ],
            "MEDIUM": [
                "moderate selectivity",
                "reversible binding",
                "dynamic equilibrium",
                "error rate 0.1-1%",
                "ξ_CP 8.5-10.5 nats",
                "context-dependent fidelity",
                "acid-amide heterodimer",
            ],
            "LOW": [
                "promiscuous binding",
                "weak interaction",
                "high error rate",
                "error rate > 1%",
                "ξ_CP > 10.5 nats",
                "formamide homodimer",
                "shallow σ-hole",
            ],
        },
        
        # Granularity (G) — scale of control
        "granularity": {
            "LOCAL": [
                "single binding event",
                "pairwise interaction",
                "local constraint",
                "immediate recognition pair",
                "no network propagation",
            ],
            "MESOSCALE": [
                "cooperative array",
                "superlinear induction",
                "emergent constraint",
                "multiple binding sites",
                "intermediate range order",
                "induction ratio > 2",
            ],
            "GLOBAL": [
                "network-scale assembly",
                "percolation",
                "long-range order",
                "crystal growth",
                "polymer propagation",
                "MOF framework",
                "chelate amplification",
                "nucleation event",
            ],
        },
        
        # Interaction Grammar (Γ) — partner selection logic
        "interaction_grammar": {
            # SPECIFIC tier
            "SPECIFIC_AND": [
                "one specific partner",
                "lock-and-key recognition",
                "highly selective binding",
                "single partner tolerance",
                "binary complex",
                "all partners required simultaneously",
            ],
            "SPECIFIC_OR": [
                "one specific partner",
                "lock-and-key recognition",
                "highly selective binding",
                "single partner tolerance",
                "binary complex",
                "any one partner suffices",
            ],
            "SPECIFIC_SEQ": [
                "one specific partner",
                "lock-and-key recognition",
                "highly selective binding",
                "single partner tolerance",
                "binary complex",
                "ordered sequential recognition",
            ],
            # SELECTIVE tier
            "SELECTIVE_AND": [
                "few partners",
                "moderate selectivity",
                "small partner set",
                "degenerate recognition site",
                "promiscuous but constrained",
                "all partners required simultaneously",
                "ordered sequential recognition",
            ],
            "SELECTIVE_OR": [
                "few partners",
                "moderate selectivity",
                "small partner set",
                "degenerate recognition site",
                "promiscuous but constrained",
                "any one partner suffices",
            ],
            "SELECTIVE_SEQ": [
                "few partners",
                "moderate selectivity",
                "small partner set",
                "degenerate recognition site",
                "promiscuous but constrained",
                "ordered sequential recognition",
                "template-directed assembly",
            ],
            # BROAD tier
            "BROAD_AND": [
                "many partners",
                "low selectivity",
                "broad partner tolerance",
                "shallow energy landscape",
                "multiple viable partners",
                "all partners required simultaneously",
            ],
            "BROAD_OR": [
                "many partners",
                "low selectivity",
                "broad partner tolerance",
                "shallow energy landscape",
                "multiple viable partners",
                "any one partner suffices",
            ],
            "BROAD_SEQ": [
                "many partners",
                "low selectivity",
                "broad partner tolerance",
                "shallow energy landscape",
                "multiple viable partners",
                "ordered sequential recognition",
            ],
        },
        
        # ΔG Justification — thermodynamic grounding (NEW)
        # Free energy must be justified by experimental or computational evidence
        "delta_g": {
            "EXPERIMENTAL": [
                "experimental measurement",
                "calorimetry",
                "ITC",
                "isothermal titration calorimetry",
                "DSC",
                "differential scanning calorimetry",
                "binding constant",
                "Ç_d",
                "Ç_a",
                "equilibrium constant",
                "van't Hoff analysis",
            ],
            "COMPUTATIONAL": [
                "DFT calculation",
                "density functional theory",
                "ab initio",
                "CCSD(T)",
                "MP2",
                "geometry optimization",
                "frequency calculation",
                "thermal correction",
                "solvation model",
                "SMD",
                "CPCM",
                "counterpoise correction",
                "BSSE",
                "single-point energy",
                "interaction energy",
                "binding energy",
            ],
            "LITERATURE": [
                "literature value",
                "literature benchmark",
                "experimental benchmark",
                "reference data",
                "CSD propensity",
                "S66 dataset",
                "HBC6 dataset",
            ],
            "ESTIMATED": [
                "group additivity",
                "fragment contribution",
                "linear free energy relationship",
                "Hammett equation",
                "Taft equation",
                "analogous system",
            ],
        },
        
        # Kinetic Primitive (K) — kinetic character (extension primitive)
        "kinetic": {
            "FAST": [
                "barrier < 60 kJ/mol",
                "spontaneous on experimental timescales",
                "rapid equilibration",
                "diffusion-limited",
                "carboxylic acid dimer",
            ],
            "MODERATE": [
                "barrier 60-100 kJ/mol",
                "accessible with mild activation",
                "requires heat or catalyst",
                "proline aldol cycle",
                "imine condensation aqueous",
            ],
            "SLOW": [
                "barrier > 100 kJ/mol",
                "requires significant activation",
                "effectively irreversible",
                "gas-phase imine condensation",
                "high transition state",
            ],
            "TRAP": [
                "pathway multiplicity high",
                "kinetic product diverges from thermodynamic",
                "multiple local minima",
                "glassy dynamics",
                "many-body localization",
                "frustrated landscape",
            ],
        },
        
        # Criticality Phase (Φ) — phase primitive (extension primitive)
        "criticality": {
            "SUBCRITICAL": [
                "normal phase",
                "G and D independent",
                "finite correlation length",
                "characteristic scale present",
            ],
            "CRITICAL": [
                "scale-free behavior",
                "correlation length diverges",
                "self-similar across scales",
                "percolation threshold",
                "phase transition",
                "universality class",
                "fractal self-encoding",
                "primitive basis contraction",
            ],
            "SUPERCritical": [
                "passed through assembly",
                "merged into assembled material",
                "synthon identity lost",
                "post-critical phase",
            ],
        },
    }
    
    # Keywords that indicate shallow/ungrounded justifications
    KEYWORD_FLAGS = [
        "quantum",
        "speculative",
        "theoretical",
        "hypothetical",
        "analogous to",
        "similar to",
        "like",
        "suggests",
        "appears to",
        "may exhibit",
        "could display",
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the grounding validator.
        
        Args:
            strict_mode: If True, reject any justification containing keyword flags.
                        If False, flag but allow keyword-heavy justifications.
        """
        self.strict_mode = strict_mode
        self._compiled_vocab: Dict[str, Dict[str, Set[str]]] = {}
        self._compile_vocabulary()
    
    def _compile_vocabulary(self) -> None:
        """Pre-process vocabulary for efficient matching."""
        for primitive, values in self.GROUNDING_VOCABULARY.items():
            self._compiled_vocab[primitive] = {}
            for value, phenomena in values.items():
                # Normalize phenomena to lowercase for matching
                self._compiled_vocab[primitive][value] = {
                    p.lower() for p in phenomena
                }
    
    def validate(
        self,
        synthon: Synthon,
        justifications: Dict[str, str],
        delta_g_value: Optional[float] = None,
        delta_g_justification: Optional[str] = None,
    ) -> GroundingResult:
        """
        Validate that all primitive assignments are mechanistically grounded.

        Args:
            synthon: The synthon to validate
            justifications: Dict mapping primitive names to justification strings
                           e.g., {"dimensionality": "closed catalytic cycle with...",
                                  "fidelity": "proofreading via hydrolysis..."}
            delta_g_value: Optional ΔG value (kJ/mol) for thermodynamic grounding
            delta_g_justification: Optional justification for ΔG value/source

        Returns:
            GroundingResult with validation status and details
        """
        primitive_results: Dict[str, PrimitiveGrounding] = {}
        ungrounded_primitives: List[str] = []
        warnings: List[str] = []
        
        # Map synthon fields to primitive names
        field_mapping = {
            "dimensionality": synthon.dimensionality.name,
            "topology": synthon.topology.name,
            "recognition_mode": synthon.recognition_mode.name,
            "polarity": synthon.polarity.name,
            "fidelity": synthon.fidelity.name,
            "granularity": synthon.granularity.name,
            "interaction_grammar": synthon.interaction_grammar.name,
        }
        
        # Add extension primitives if present
        if hasattr(synthon, 'kinetic_character') and synthon.kinetic_character is not None:
            field_mapping["kinetic"] = synthon.kinetic_character.name
        if hasattr(synthon, 'criticality_phase') and synthon.criticality_phase is not None:
            field_mapping["criticality"] = synthon.criticality_phase.name
        
        for prim_name, prim_value in field_mapping.items():
            justification = justifications.get(prim_name, "")
            result = self._validate_primitive(
                prim_name, prim_value, justification
            )
            primitive_results[prim_name] = result
            
            if result.status != GroundingStatus.GROUNDED:
                ungrounded_primitives.append(prim_name)
            
            if result.warning:
                warnings.append(result.warning)
        
        # Validate ΔG justification if provided
        delta_g_grounding = None
        if delta_g_value is not None or delta_g_justification:
            delta_g_grounding = self._validate_delta_g(
                delta_g_value, delta_g_justification or ""
            )
            if delta_g_grounding.status != GroundingStatus.GROUNDED:
                warnings.append(delta_g_grounding.warning or "ΔG justification missing")
        
        is_valid = len(ungrounded_primitives) == 0 and (
            delta_g_grounding is None or delta_g_grounding.status == GroundingStatus.GROUNDED
        )
        
        return GroundingResult(
            is_valid=is_valid,
            primitive_results=primitive_results,
            ungrounded_primitives=ungrounded_primitives,
            warnings=warnings,
            delta_g_grounding=delta_g_grounding,
        )
    
    def _validate_primitive(
        self,
        prim_name: str,
        prim_value: str,
        justification: str,
    ) -> PrimitiveGrounding:
        """Validate grounding for a single primitive."""
        
        # Check for empty justification
        if not justification or not justification.strip():
            return PrimitiveGrounding(
                primitive=prim_name,
                value=prim_value,
                status=GroundingStatus.UNGROUNDED,
                justification=justification,
                matched_phenomena=[],
                warning=f"No justification provided for {prim_name}",
            )
        
        # Get valid phenomena for this primitive value
        vocab = self._compiled_vocab.get(prim_name, {})
        valid_phenomena = vocab.get(prim_value, set())
        
        # Normalize justification for matching
        justification_lower = justification.lower()
        
        # Find matched phenomena
        matched = []
        for phenomenon in valid_phenomena:
            if phenomenon in justification_lower:
                matched.append(phenomenon)
        
        # Check for keyword flags (shallow justifications)
        keyword_matches = [
            kw for kw in self.KEYWORD_FLAGS
            if kw in justification_lower
        ]
        
        # Determine status
        if matched:
            status = GroundingStatus.GROUNDED
            warning = None
            
            # Warn if also contains keyword flags
            if keyword_matches and not self.strict_mode:
                warning = (
                    f"Justification for {prim_name} contains keyword flags "
                    f"({', '.join(keyword_matches)}) but is mechanically grounded"
                )
            elif keyword_matches and self.strict_mode:
                status = GroundingStatus.UNGROUNDED
                warning = (
                    f"Justification relies on keyword matching "
                    f"({', '.join(keyword_matches)}) without mechanistic grounding"
                )
        else:
            status = GroundingStatus.UNGROUNDED
            warning = (
                f"No valid physical phenomena found for {prim_name}={prim_value}. "
                f"Expected one of: {', '.join(list(valid_phenomena)[:5])}..."
            )
        
        return PrimitiveGrounding(
            primitive=prim_name,
            value=prim_value,
            status=status,
            justification=justification,
            matched_phenomena=matched,
            warning=warning,
        )
    
    def _validate_delta_g(
        self,
        delta_g_value: Optional[float],
        justification: str,
    ) -> PrimitiveGrounding:
        """
        Validate ΔG justification.
        
        Args:
            delta_g_value: ΔG value in kJ/mol
            justification: Justification for the value/source
        
        Returns:
            PrimitiveGrounding for ΔG
        """
        # Check for missing value
        if delta_g_value is None:
            return PrimitiveGrounding(
                primitive="delta_g",
                value="N/A",
                status=GroundingStatus.UNGROUNDED,
                justification=justification,
                matched_phenomena=[],
                warning="ΔG value not provided",
            )
        
        # Check for empty justification
        if not justification or not justification.strip():
            return PrimitiveGrounding(
                primitive="delta_g",
                value=f"{delta_g_value} kJ/mol",
                status=GroundingStatus.UNGROUNDED,
                justification=justification,
                matched_phenomena=[],
                warning=f"ΔG = {delta_g_value} kJ/mol provided without source/method justification",
            )
        
        # Get valid phenomena for ΔG
        vocab = self._compiled_vocab.get("delta_g", {})
        all_phenomena = set()
        for phenomena in vocab.values():
            all_phenomena.update(phenomena)
        
        # Normalize justification for matching
        justification_lower = justification.lower()
        
        # Find matched phenomena
        matched = []
        for phenomenon in all_phenomena:
            if phenomenon in justification_lower:
                matched.append(phenomenon)
        
        # Check for keyword flags
        keyword_matches = [
            kw for kw in self.KEYWORD_FLAGS
            if kw in justification_lower
        ]
        
        # Determine status
        if matched:
            status = GroundingStatus.GROUNDED
            warning = None
            
            if keyword_matches and not self.strict_mode:
                warning = (
                    f"ΔG justification contains keyword flags "
                    f"({', '.join(keyword_matches)}) but is grounded"
                )
            elif keyword_matches and self.strict_mode:
                status = GroundingStatus.UNGROUNDED
                warning = (
                    f"ΔG justification relies on keyword matching "
                    f"({', '.join(keyword_matches)})"
                )
        else:
            status = GroundingStatus.UNGROUNDED
            warning = (
                f"ΔG justification '{justification[:50]}...' does not reference "
                f"experimental, computational, or literature source. "
                f"Expected: experimental measurement, DFT calculation, literature value, etc."
            )
        
        return PrimitiveGrounding(
            primitive="delta_g",
            value=f"{delta_g_value} kJ/mol",
            status=status,
            justification=justification,
            matched_phenomena=matched,
            warning=warning,
        )
    
    def validate_batch(
        self,
        synthons: List[Tuple[Synthon, Dict[str, str]]],
    ) -> List[GroundingResult]:
        """
        Validate grounding for multiple synthons.
        
        Args:
            synthons: List of (synthon, justifications) tuples
        
        Returns:
            List of GroundingResult objects
        """
        return [self.validate(syn, just) for syn, just in synthons]
    
    def get_grounding_report(
        self,
        result: GroundingResult,
    ) -> str:
        """
        Generate a human-readable grounding report.
        
        Args:
            result: GroundingResult to report on
        
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("GROUNDING VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append("")

        if result.is_valid:
            lines.append("✓ ALL PRIMITIVES GROUNDED")
        else:
            lines.append(f"✗ {len(result.ungrounded_primitives)} UNGROUNDED PRIMITIVES")
            lines.append(f"  Ungrounded: {', '.join(result.ungrounded_primitives)}")

        lines.append("")
        lines.append("-" * 60)
        lines.append("DETAILED BREAKDOWN")
        lines.append("-" * 60)

        for prim_name, prim_result in result.primitive_results.items():
            status_icon = {
                GroundingStatus.GROUNDED: "✓",
                GroundingStatus.UNGROUNDED: "✗",
                GroundingStatus.AMBIGUOUS: "?",
                GroundingStatus.INVALID: "!",
            }[prim_result.status]

            lines.append("")
            lines.append(f"{status_icon} {prim_name.upper()}: {prim_result.value}")
            lines.append(f"  Justification: {prim_result.justification[:100]}...")

            if prim_result.matched_phenomena:
                lines.append(
                    f"  Matched phenomena: {', '.join(prim_result.matched_phenomena)}"
                )

            if prim_result.warning:
                lines.append(f"  ⚠ {prim_result.warning}")
        
        # Include ΔG grounding if present
        if result.delta_g_grounding:
            status_icon = {
                GroundingStatus.GROUNDED: "✓",
                GroundingStatus.UNGROUNDED: "✗",
                GroundingStatus.AMBIGUOUS: "?",
                GroundingStatus.INVALID: "!",
            }[result.delta_g_grounding.status]
            lines.append("")
            lines.append(f"{status_icon} ΔG: {result.delta_g_grounding.value}")
            lines.append(f"  Justification: {result.delta_g_grounding.justification[:100]}...")
            
            if result.delta_g_grounding.matched_phenomena:
                lines.append(
                    f"  Matched phenomena: {', '.join(result.delta_g_grounding.matched_phenomena)}"
                )
            
            if result.delta_g_grounding.warning:
                lines.append(f"  ⚠ {result.delta_g_grounding.warning}")

        if result.warnings:
            lines.append("")
            lines.append("-" * 60)
            lines.append("WARNINGS")
            lines.append("-" * 60)
            for warning in result.warnings:
                lines.append(f"  • {warning}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


def validate_synthon_with_grounding(
    synthon: Synthon,
    justifications: Dict[str, str],
    delta_g_value: Optional[float] = None,
    delta_g_justification: Optional[str] = None,
    require_grounding: bool = True,
) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to validate synthon grounding.
    
    Args:
        synthon: Synthon to validate
        justifications: Dict of primitive -> justification
        delta_g_value: Optional ΔG value (kJ/mol)
        delta_g_justification: Optional ΔG source/method justification
        require_grounding: If True, raise ValueError on ungrounded primitives
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Raises:
        ValueError: If require_grounding and validation fails
    """
    validator = GroundingValidator()
    result = validator.validate(
        synthon, justifications, delta_g_value, delta_g_justification
    )
    
    if require_grounding and not result.is_valid:
        report = validator.get_grounding_report(result)
        raise ValueError(
            f"Synthon has ungrounded primitive assignments:\n{report}"
        )
    
    return result.is_valid, None

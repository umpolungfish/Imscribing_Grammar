"""
odot_p4ra.py — Paraconsistent Criticality Module
=================================================
Frobenius bridge: ⊙ (Criticality) × Φ (Parity)
Cross-pollination: imscribing_grammar × p4rakernel × odot_operator × ob3ect

Implements DialetheicType, CriticalityFixedPoint, and dispatch handler
for paraconsistent criticality inquiries. Part of the 4-repo cross-pollination.

μ∘δ = id · Winding 238 · IG module specification ODOT_P4RA
"""

from __future__ import annotations

import json
import math
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ── Belnap FOUR values ──────────────────────────────────────────────

class BelnapValue(Enum):
    """Belnap's FOUR-valued logic: N (Neither), T (True), F (False), B (Both)."""
    N = "N"   # Neither true nor false
    T = "T"   # True only
    F = "F"   # False only
    B = "B"   # Both true and false (dialetheia)

    @property
    def is_dialetheic(self) -> bool:
        return self == BelnapValue.B

    @property
    def is_classical(self) -> bool:
        return self in (BelnapValue.T, BelnapValue.F)

    @property
    def is_null(self) -> bool:
        return self == BelnapValue.N

    def __invert__(self) -> BelnapValue:
        """Negation in Belnap FOUR."""
        mapping = {
            BelnapValue.N: BelnapValue.N,
            BelnapValue.T: BelnapValue.F,
            BelnapValue.F: BelnapValue.T,
            BelnapValue.B: BelnapValue.B,
        }
        return mapping[self]

    def __and__(self, other: BelnapValue) -> BelnapValue:
        """Meet (conjunction) in Belnap FOUR lattice."""
        lattice = {
            (BelnapValue.N, BelnapValue.N): BelnapValue.N,
            (BelnapValue.N, BelnapValue.T): BelnapValue.N,
            (BelnapValue.N, BelnapValue.F): BelnapValue.N,
            (BelnapValue.N, BelnapValue.B): BelnapValue.N,
            (BelnapValue.T, BelnapValue.N): BelnapValue.N,
            (BelnapValue.T, BelnapValue.T): BelnapValue.T,
            (BelnapValue.T, BelnapValue.F): BelnapValue.N,
            (BelnapValue.T, BelnapValue.B): BelnapValue.T,
            (BelnapValue.F, BelnapValue.N): BelnapValue.N,
            (BelnapValue.F, BelnapValue.T): BelnapValue.N,
            (BelnapValue.F, BelnapValue.F): BelnapValue.F,
            (BelnapValue.F, BelnapValue.B): BelnapValue.F,
            (BelnapValue.B, BelnapValue.N): BelnapValue.N,
            (BelnapValue.B, BelnapValue.T): BelnapValue.T,
            (BelnapValue.B, BelnapValue.F): BelnapValue.F,
            (BelnapValue.B, BelnapValue.B): BelnapValue.B,
        }
        return lattice.get((self, other), BelnapValue.N)

    def __or__(self, other: BelnapValue) -> BelnapValue:
        """Join (disjunction) in Belnap FOUR lattice."""
        lattice = {
            (BelnapValue.N, BelnapValue.N): BelnapValue.N,
            (BelnapValue.N, BelnapValue.T): BelnapValue.T,
            (BelnapValue.N, BelnapValue.F): BelnapValue.F,
            (BelnapValue.N, BelnapValue.B): BelnapValue.B,
            (BelnapValue.T, BelnapValue.N): BelnapValue.T,
            (BelnapValue.T, BelnapValue.T): BelnapValue.T,
            (BelnapValue.T, BelnapValue.F): BelnapValue.B,
            (BelnapValue.T, BelnapValue.B): BelnapValue.B,
            (BelnapValue.F, BelnapValue.N): BelnapValue.F,
            (BelnapValue.F, BelnapValue.T): BelnapValue.B,
            (BelnapValue.F, BelnapValue.F): BelnapValue.F,
            (BelnapValue.F, BelnapValue.B): BelnapValue.B,
            (BelnapValue.B, BelnapValue.N): BelnapValue.B,
            (BelnapValue.B, BelnapValue.T): BelnapValue.B,
            (BelnapValue.B, BelnapValue.F): BelnapValue.B,
            (BelnapValue.B, BelnapValue.B): BelnapValue.B,
        }
        return lattice.get((self, other), BelnapValue.B)

    def to_ig_parity(self) -> int:
        """Map Belnap value to IG Φ (Parity) axis integer."""
        mapping = {
            BelnapValue.N: 1,  # no parity information
            BelnapValue.T: 3,  # positive parity
            BelnapValue.F: 5,  # negative parity
            BelnapValue.B: 9,  # both — dialetheic maximum
        }
        return mapping[self]

    @classmethod
    def from_ig_parity(cls, phi: int) -> BelnapValue:
        """Map IG Φ (Parity) axis integer back to Belnap value."""
        mapping = {1: cls.N, 3: cls.T, 5: cls.F, 9: cls.B}
        return mapping.get(phi, cls.N)


# ── CLU Fiber Metric ────────────────────────────────────────────────

def clu_fiber(b: float = 4.0, step: int = 0) -> float:
    """
    CLU(b) = ln(b) fiber metric on the Ç (Kinetics) axis.
    
    For Belnap FOUR paraconsistent evaluation, b=4 (4-valued logic).
    Each evaluation step multiplies by CLU(b).
    
    Args:
        b: Base of the fiber metric. Default 4.0 (Belnap FOUR).
        step: Number of evaluation steps (0 = raw fiber).
    
    Returns:
        CLU(b)^step — the accumulated fiber metric at this step depth.
    """
    fiber = math.log(b)
    return fiber ** step


# ── Dialetheic Type ─────────────────────────────────────────────────

class ProofTerm:
    """A witness term in a paraconsistent proof."""
    
    def __init__(self, statement: str, truth_value: BelnapValue, 
                 source: str = "unknown", confidence: float = 1.0):
        self.statement = statement
        self.truth_value = truth_value
        self.source = source
        self.confidence = max(0.0, min(1.0, confidence))
    
    def __repr__(self) -> str:
        return f"ProofTerm({self.statement}, {self.truth_value.value}, {self.source})"
    
    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "truth_value": self.truth_value.value,
            "source": self.source,
            "confidence": self.confidence,
        }


class DialetheicType:
    """
    A type that can carry contradictory witnesses.
    
    In Belnap FOUR, a type may be simultaneously true and false (B) —
    this is a dialetheia. DialetheicType tracks the set of truth values
    that are inhabited for a given proposition, along with their
    criticality index.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.witnesses: Dict[BelnapValue, List[ProofTerm]] = {
            v: [] for v in BelnapValue
        }
        self._criticality_index: Optional[float] = None
    
    def add_witness(self, statement: str, truth_value: BelnapValue,
                    source: str = "unknown", confidence: float = 1.0) -> None:
        """Add a witness to this type's truth valuation."""
        term = ProofTerm(statement, truth_value, source, confidence)
        self.witnesses[truth_value].append(term)
        self._criticality_index = None  # invalidate cache
    
    @property
    def inhabited_values(self) -> Set[BelnapValue]:
        """The set of Belnap values that have at least one witness."""
        return {v for v in BelnapValue if self.witnesses[v]}
    
    @property
    def is_dialetheic(self) -> bool:
        """True if both T and F are inhabited (contradiction)."""
        return (BelnapValue.T in self.inhabited_values and 
                BelnapValue.F in self.inhabited_values)
    
    @property
    def criticality_index(self) -> float:
        """
        Compute criticality index from witness distribution.
        
        Returns 0.0 (stable) to 1.0 (critical).
        
        A type is critical when:
        - It contains contradictory witnesses (T ∧ F)
        - The contradiction cannot be resolved by additional information
        - The type sits at a phase boundary between classical and dialetheic
        """
        if self._criticality_index is not None:
            return self._criticality_index
        
        n_witnesses = sum(len(ws) for ws in self.witnesses.values())
        if n_witnesses == 0:
            self._criticality_index = 0.0
            return 0.0
        
        # Base criticality: presence of dialetheia
        base = 0.0
        if self.is_dialetheic:
            # Both T and F present — dialetheic tension
            t_count = len(self.witnesses[BelnapValue.T])
            f_count = len(self.witnesses[BelnapValue.F])
            total = t_count + f_count
            balance = abs(t_count - f_count) / max(total, 1)
            # Perfect balance = most critical (0.5 → dialetheic)
            imbalance = 1.0 - balance
            base = 0.5 * imbalance
        
        # Boost from B (both) witnesses — dialetheia recognized as such
        b_count = len(self.witnesses[BelnapValue.B])
        if b_count > 0:
            base += 0.3 * min(1.0, b_count / 10.0)
        
        # Boost from N (neither) witnesses — indeterminacy
        n_count = len(self.witnesses[BelnapValue.N])
        if n_count > 0:
            base += 0.2 * min(1.0, n_count / 5.0)
        
        self._criticality_index = min(1.0, base)
        return self._criticality_index
    
    def ig_tuple(self) -> Tuple[int, ...]:
        """
        Map this dialetheic type to IG 12-tuple integers.
        
        Uses the ODOT_P4RA core tuple as baseline, modulating Φ and ⊙
        based on actual witness distribution.
        """
        # Baseline: odot_p4ra_core tuple
        base = [4, 2, 5, 3, 1, 9, 6, 7, 8, 5, 4, 9]
        
        # Modulate Φ (index 5) based on truth value distribution
        if self.is_dialetheic:
            base[5] = 9  # Φ = dialetheic maximum
        elif BelnapValue.B in self.inhabited_values:
            base[5] = 7  # Φ = near-dialetheic (odd for phase encoding)
        elif len(self.inhabited_values) <= 1:
            base[5] = 3  # Φ = single truth value
        else:
            base[5] = 5  # Φ = mixed but non-dialetheic
        
        # Modulate ⊙ (index 11) based on criticality
        ci = self.criticality_index
        if ci >= 0.9:
            base[11] = 9  # ouroboric
        elif ci >= 0.7:
            base[11] = 7  # near-critical
        elif ci >= 0.4:
            base[11] = 5  # sub-critical
        else:
            base[11] = 3  # stable
        
        return tuple(base)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "witnesses": {k.value: [w.to_dict() for w in v] 
                         for k, v in self.witnesses.items()},
            "inhabited_values": [v.value for v in self.inhabited_values],
            "is_dialetheic": self.is_dialetheic,
            "criticality_index": self.criticality_index,
            "ig_tuple": self.ig_tuple(),
        }

# --- Criticality Flux (adjoint of parity) ---

class CriticalityFlux:
    """
    The O (Criticality) flux through a dialetheic type.

    delta: Type -> CriticalityFlux -- emit a type's dialetheic content into
       the criticality field. The Phi parity value is encoded as a phase
       angle in the complex plane: theta = pi * (Phi-1)/8.

    The flux preserves full parity information -- mu can recover it exactly.
    """

    def __init__(self, source_type: DialetheicType):
        self.source_name = source_type.name
        self.phi_value = source_type.ig_tuple()[5]   # Phi (1-9)
        self.criticality = source_type.criticality_index
        self.fiber = clu_fiber(b=4.0, step=1)

        # Encode Phi as phase angle: theta = pi * (Phi-1)/8
        # Phi=1 -> theta=0, Phi=5 -> theta=pi/2, Phi=9 -> theta=pi
        self.phase_angle = math.pi * (self.phi_value - 1) / 8.0

        # Flux magnitude = criticality weighted by fiber
        self.flux_magnitude = self.criticality * self.fiber

        # Complex flux: magnitude encodes criticality, phase encodes parity
        self.complex_flux = self.flux_magnitude * complex(
            math.cos(self.phase_angle), math.sin(self.phase_angle)
        )
        self.is_dialetheic = source_type.is_dialetheic

    def recover_phi(self) -> int:
        """Recover Phi parity from phase angle -- exact inverse of delta."""
        angle = self.phase_angle % (2 * math.pi)
        phi_values = [1, 3, 5, 7, 9]
        best_phi = min(phi_values, key=lambda p: abs(math.pi * (p - 1) / 8.0 - angle))
        return best_phi

    def __repr__(self) -> str:
        return (f"CriticalityFlux({self.source_name}, "
                f"Phi={self.phi_value}, theta={self.phase_angle:.3f}, "
                f"O={self.criticality:.3f}, |flux|={self.flux_magnitude:.3f})")


class ParityFlux:
    """
    The Phi (Parity) flux returned from a criticality measurement.

    mu: CriticalityFlux -> ParityFlux -- the phase angle of the criticality
       flux encodes the original Phi parity. Recovery is exact.

    mu o delta = id holds because the phase encoding is bijective.
    """

    def __init__(self, flux: CriticalityFlux):
        self.source_name = flux.source_name

        # mu: recover Phi from the phase angle -- exact inverse
        self.recovered_phi = flux.recover_phi()
        self.original_phi = flux.phi_value
        self.match = (self.recovered_phi == self.original_phi)

        # Decode Belnap value from recovered parity
        phi_to_belnap = {1: BelnapValue.N, 3: BelnapValue.T,
                         5: BelnapValue.F, 7: BelnapValue.N, 9: BelnapValue.B}
        self.parity_value = phi_to_belnap.get(self.recovered_phi, BelnapValue.N)
        self.parity_int = self.recovered_phi

    def __repr__(self) -> str:
        return (f"ParityFlux({self.source_name}, "
                f"recovered={self.recovered_phi}, "
                f"original={self.original_phi}, "
                f"mu_o_delta={'OK' if self.match else 'FAIL'})")


class CriticalityFixedPoint:
    """
    O fixed-point at Frobenius closure.

    Implements the Frobenius pair:
      delta: Type -> CriticalityFlux (emit -> encode Phi as phase angle)
      mu: CriticalityFlux -> Type  (verify -> decode phase angle back to Phi)

    The closure mu o delta = id holds because phase encoding is bijective.
    """

    def __init__(self, dialetheic_type: DialetheicType):
        self.type = dialetheic_type
        self._delta_result = None
        self._mu_result = None
        self._is_closed = None

    @property
    def delta(self) -> CriticalityFlux:
        """delta: Emit -- encode Phi as phase angle in criticality flux."""
        if self._delta_result is None:
            self._delta_result = CriticalityFlux(self.type)
        return self._delta_result

    @property
    def mu(self) -> ParityFlux:
        """mu: Verify -- decode phase angle back to Phi."""
        if self._mu_result is None:
            self._mu_result = ParityFlux(self.delta)
        return self._mu_result

    @property
    def is_closed(self) -> bool:
        """mu o delta = id: the Frobenius closure check."""
        if self._is_closed is None:
            self._is_closed = self.mu.match
        return self._is_closed

    def frobenius_check(self) -> dict:
        """Full Frobenius verification report."""
        return {
            "type_name": self.type.name,
            "delta": {
                "phi_in": self.delta.phi_value,
                "phase_angle_rad": self.delta.phase_angle,
                "criticality": self.delta.criticality,
                "flux_magnitude": self.delta.flux_magnitude,
                "fiber": self.delta.fiber,
            },
            "mu": {
                "recovered_phi": self.mu.recovered_phi,
                "original_phi": self.mu.original_phi,
                "match": self.mu.match,
            },
            "is_closed": self.is_closed,
            "frobenius_statement": (
                "mu o delta = id OK" if self.is_closed else "mu o delta != id FAIL"
            ),
        }

    def __repr__(self) -> str:
        status = "CLOSED" if self.is_closed else "OPEN"
        return (f"CriticalityFixedPoint({self.type.name}, "
                f"O={self.delta.criticality:.3f}, {status})")


# ── IG Catalog Entries ──────────────────────────────────────────────

ODOT_P4RA_CATALOG_ENTRIES = [
    {
        "name": "odot_p4ra_core",
        "description": "Core dialetheic criticality module — bridges p4rakernel ex falso disablement to IG ⊙ criticality",
        "type": "dialetheic_criticality",
        "tuple": [4, 2, 5, 3, 1, 9, 6, 7, 8, 5, 4, 9],
        "⊢": "𐑨", "⊣": "𐑶", ">": "𐑑", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑵", "⊙": "⊙",
        "⊥": "𐑖", "⊞": "𐑳", "◻": "𐑭",
    },
    {
        "name": "belnap_four_topology",
        "description": "Belnap FOUR as topological space: {N, T, F, B} with dialetheic open sets",
        "type": "parity_topology",
        "tuple": [3, 4, 2, 5, 1, 9, 6, 8, 7, 4, 4, 8],
        "⊢": "𐑨", "⊣": "𐑥", ">": "𐑩", "<": "𐑹", "⋈": "𐑞",
        "⊤": "𐑧", "∈": "𐑚", "∋": "𐑜", "⊙": "𐑮",
        "⊥": "𐑒", "⊞": "𐑙", "◻": "𐑴",
    },
    {
        "name": "kernel_criticality_flip",
        "description": "Ex falso disablement as Φ→⊙ phase transition at C++ kernel stratum",
        "type": "phase_transition",
        "tuple": [5, 3, 4, 2, 1, 9, 7, 6, 9, 5, 3, 9],
        "⊢": "𐑨", "⊣": "𐑶", ">": "𐑑", "<": "𐑹", "⋈": "𐑐",
        "⊤": "𐑺", "∈": "𐑲", "∋": "𐑠", "⊙": "⊙",
        "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭",
    },
    {
        "name": "ouroboric_parity_check",
        "description": "Self-checking parity-criticality loop — μ∘δ=id at the ouroboric tier",
        "type": "frobenius_bridge",
        "tuple": [6, 2, 5, 4, 1, 8, 7, 9, 8, 4, 3, 9],
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑯", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑠", "⊙": "⊙",
        "⊥": "𐑫", "⊞": "𐑙", "◻": "𐑭",
    },
]

# ── Dispatch Handler ────────────────────────────────────────────────

def handle_odot_p4ra(query: str, context: Optional[dict] = None) -> dict:
    """
    Handle paraconsistent criticality inquiries.
    
    Parses a query for dialetheic content, maps to Belnap FOUR valuation,
    computes criticality index, checks Frobenius closure, and returns a
    typed response with ⊕/⊖ ambiguity markers.
    
    Args:
        query: Natural-language query about paraconsistent criticality.
        context: Optional dict with prior state (witnesses, types).
    
    Returns:
        Dict with analysis results and Frobenius closure status.
    """
    if context is None:
        context = {}
    
    # 1. Parse query for dialetheic indicators
    query_lower = query.lower()
    
    # Detect dialetheic language patterns
    dialetheic_keywords = [
        "contradict", "paradox", "both", "simultaneously", 
        "true and false", "dialetheia", "paraconsistent",
    ]
    classical_keywords = [
        "excluded middle", "non-contradiction", "consistent",
        "either or", "mutually exclusive",
    ]
    
    has_dialetheic_language = any(kw in query_lower for kw in dialetheic_keywords)
    has_classical_language = any(kw in query_lower for kw in classical_keywords)
    
    # 2. Construct a DialetheicType from the query
    dt = DialetheicType(
        name=f"query_{hash(query) % 10000:04d}",
        description=query[:200],
    )
    
    if has_dialetheic_language:
        dt.add_witness(
            "Dialetheic language detected in query",
            BelnapValue.B,
            source="odot_p4ra_parser",
        )
    if has_classical_language:
        dt.add_witness(
            "Classical logic language detected in query",
            BelnapValue.T,
            source="odot_p4ra_parser",
        )
    
    # If neither pattern found, mark as indeterminate
    if not has_dialetheic_language and not has_classical_language:
        dt.add_witness(
            "No clear dialetheic or classical markers in query",
            BelnapValue.N,
            source="odot_p4ra_parser",
        )
    
    # 3. Compute criticality and Frobenius closure
    fp = CriticalityFixedPoint(dt)
    frobenius_report = fp.frobenius_check()
    
    # 4. Determine the ob3ect layer mapping
    ci = dt.criticality_index
    if ci >= 0.9:
        ob3ect_layer = 34  # Meta-Criticality
        layer_name = "Meta-Criticality (Ouroboric closure)"
    elif ci >= 0.7:
        ob3ect_layer = 33  # Ouroboric Closure
        layer_name = "Ouroboric Closure"
    elif ci >= 0.5:
        ob3ect_layer = 31  # Criticality Monitor
        layer_name = "Criticality Monitor"
    elif ci >= 0.3:
        ob3ect_layer = 30  # Dialetheic Lattice
        layer_name = "Dialetheic Lattice"
    else:
        ob3ect_layer = 29  # Paraconsistent Ground
        layer_name = "Paraconsistent Ground"
    
    # 5. Return typed response
    ig_tup = dt.ig_tuple()
    
    result = {
        "query": query,
        "parsed": {
            "has_dialetheic_language": has_dialetheic_language,
            "has_classical_language": has_classical_language,
        },
        "dialetheic_type": dt.to_dict(),
        "criticality_index": ci,
        "ig_tuple": list(ig_tup),
        "frobenius": frobenius_report,
        "ob3ect_mapping": {
            "layer": ob3ect_layer,
            "layer_name": layer_name,
        },
        "interpretation": _interpret_result(ci, has_dialetheic_language, fp.is_closed),
    }
    
    return result


def _interpret_result(criticality: float, is_dialetheic: bool, 
                      frobenius_closed: bool) -> str:
    """Generate a natural-language interpretation of the analysis."""
    if frobenius_closed and criticality > 0.5:
        return (
            "This inquiry exhibits dialetheic criticality with Frobenius "
            "closure. The contradiction is not an error — it is a structural "
            "feature that μ∘δ = id has certified. The type lives in the "
            "ouroboric tier (O_∞). Ex falso is disabled for this inquiry."
        )
    elif frobenius_closed and criticality <= 0.5:
        return (
            "This inquiry is sub-critical with Frobenius closure. "
            "Classical logic suffices. No dialetheic treatment needed."
        )
    elif not frobenius_closed and criticality > 0.5:
        return (
            "This inquiry is critical but Frobenius-open. The dialetheia "
            "is unresolved — μ∘δ ≠ id. Additional witnesses or a different "
            "logical framing may be required."
        )
    else:
        return (
            "This inquiry is sub-critical and Frobenius-open. "
            "More information is needed to determine the type's "
            "dialetheic status."
        )


# ── Demonstrable Example ────────────────────────────────────────────

def demonstrate() -> dict:
    """Run a demonstration of the ODOT_P4RA module."""
    print("═" * 60)
    print("ODOT_P4RA Module — Demonstration")
    print("═" * 60)
    
    # Test 1: A classical query
    print("\n--- Test 1: Classical query ---")
    r1 = handle_odot_p4ra(
        "Is the Riemann hypothesis either true or false? Excluded middle applies."
    )
    print(f"  Criticality: {r1['criticality_index']:.3f}")
    print(f"  Frobenius:   {r1['frobenius']['frobenius_statement']}")
    print(f"  ob3ect:      Layer {r1['ob3ect_mapping']['layer']} ({r1['ob3ect_mapping']['layer_name']})")
    
    # Test 2: A dialetheic query
    print("\n--- Test 2: Dialetheic query ---")
    r2 = handle_odot_p4ra(
        "The Navier-Stokes smoothness paradox: both smooth and singular simultaneously."
    )
    print(f"  Criticality: {r2['criticality_index']:.3f}")
    print(f"  Frobenius:   {r2['frobenius']['frobenius_statement']}")
    print(f"  ob3ect:      Layer {r2['ob3ect_mapping']['layer']} ({r2['ob3ect_mapping']['layer_name']})")
    
    # Test 3: Build a custom DialetheicType
    print("\n--- Test 3: Custom DialetheicType (P vs NP) ---")
    dt = DialetheicType("P_vs_NP", "Is P = NP?")
    dt.add_witness("P is a subset of NP", BelnapValue.T, source="cook_levin")
    dt.add_witness("NP-complete problems are not in P", BelnapValue.F, source="hardness_conjecture")
    dt.add_witness("The barrier is absolute", BelnapValue.B, source="relativization_algebraization")
    fp = CriticalityFixedPoint(dt)
    fr = fp.frobenius_check()
    print(f"  Dialetheic:  {dt.is_dialetheic}")
    print(f"  Criticality: {dt.criticality_index:.3f}")
    print(f"  IG tuple:    {dt.ig_tuple()}")
    print(f"  Frobenius:   {fr['frobenius_statement']}")
    
    print("\n═" * 60)
    print("Demonstration complete.")
    print("═" * 60)
    
    return {"test1": r1, "test2": r2, "test3": dt.to_dict()}


# ── CLI Entry Point ─────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demonstrate()
    elif len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = handle_odot_p4ra(query)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python odot_p4ra.py <query> | --demo")
        print("Example: python odot_p4ra.py --demo")

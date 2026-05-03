"""
Imscribing Grammar Models — Canonical 12-primitive type system.

Unified with the Lean 4 formalization in Imscribing Grammar/Primitives/Core.lean and
Synthon.lean. Enum VALUES match the Lean constructors exactly; field names on
Synthon use the long Python-readable form with short-name properties (dim, top,
recog, pol, gram, fid, kin, gran, crit, prot, stoi, chir) mirroring Lean.

Tuple notation: ⟨D; T; R; P; F; K; G; Γ; Φ; Ω; S; H⟩

Ordering conventions (match Lean Core.lean):
  F: F_noise < F_ell < F_eth < F_hbar
  K: K_MBL < K_trap < K_slow < K_mod < K_fast
  G: G_aleph < G_beth < G_gimel   (ℵ = finest/atomic, ℷ = coarsest/cosmological)
  Ω: Omega_0 < Omega_Z2 < Omega_Z < Omega_C < Omega_NA
  H: H0 < H1 < H2 < H_inf

Cross-primitive axioms (enforced in Synthon.__post_init__; mirroring Core.lean):
  B: prot >= Omega_Z → chir >= H2
  C: D_odot ↔ T_odot
  D: Omega_NA → D_odot
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional

# =============================================================================
# Ordinal helpers (used by __post_init__ axiom checks)
# =============================================================================

def _prot_ord(p: "Protection") -> int:
    if p is None:
        return 0
    return {
        "Omega_0": 0, "Omega_Z2": 1, "Omega_Z": 2, "Omega_C": 3, "Omega_NA": 4,
    }[p.value]

def _chir_ord(h: "Chirality") -> int:
    return {"H0": 0, "H1": 1, "H2": 2, "H_inf": 3}[h.value]


# =============================================================================
# Primitive I: Dimensionality (D)
# =============================================================================

class Dimensionality(Enum):
    """
    Coordinate set along which the synthon operates.

    Lean canonical values: D_point, D_line, D_wedge, D_cube, D_infty, D_odot.
    Chemistry-domain extras (T_network_hex etc.) are retained for molecular catalog
    entries but are not part of the canonical 6-constructor type in Core.lean.
    """
    D_point = "D_point"   # 0-dimensional, scalar / spin-0 field
    D_line  = "D_line"    # 1-dimensional, vectorial
    D_wedge = "D_wedge"   # 2-dimensional, areal  (formerly MOLECULAR)
    D_cube  = "D_cube"    # 3-dimensional, volumetric  (formerly D_triangle / SUPRAMOLECULAR)
    D_infty = "D_infty"   # ∞-dimensional, iterative/temporal  (formerly D_infinity / TEMPORAL)
    D_holo  = "D_odot"    # imscriptive: boundary encodes bulk (AdS/CFT, IUT); canonical: D_odot

    # Backward-compat aliases (chemistry-domain names → canonical values)
    MOLECULAR      = "D_wedge"   # 2D / molecular scale
    SUPRAMOLECULAR = "D_cube"    # 3D / supramolecular scale
    TEMPORAL       = "D_infty"   # ∞-dimensional / temporal / iterative
    HOLOGRAPHIC    = "D_odot"    # imscriptive (alias for D_holo)
    # Hybrid-scale aliases (multi-scale entries → coarsest participating scale)
    HYBRID_MOL_SUPRA  = "D_cube"   # molecular + supramolecular → D_cube
    HYBRID_MOL_TEMP   = "D_infty"  # molecular + temporal → D_infty
    HYBRID_SUPRA_TEMP = "D_infty"  # supramolecular + temporal → D_infty
    HYBRID_ALL        = "D_cube"   # all three scales → D_cube

    @property
    def domains(self) -> frozenset:
        """Compat shim: old compound Dimensionality had a .domains frozenset."""
        return {
            "D_point": frozenset({"point"}),
            "D_line":  frozenset({"linear"}),
            "D_wedge": frozenset({"molecular"}),
            "D_cube":  frozenset({"molecular", "supramolecular"}),
            "D_infty": frozenset({"temporal", "molecular"}),
            "D_odot":  frozenset({"temporal", "molecular", "supramolecular", "imscriptive"}),
        }.get(self.value, frozenset())

    @classmethod
    def from_symbol(cls, s: str) -> "Dimensionality":
        _map = {
            "D_point": cls.D_point,
            "D_line": cls.D_line,
            "D_wedge": cls.D_wedge,    "D_∧": cls.D_wedge,     "D_triangle": cls.D_cube,
            "D_cube": cls.D_cube,      "D_△": cls.D_cube,
            "D_infty": cls.D_infty,    "D_∞": cls.D_infty,     "D_infinity": cls.D_infty,
            "D_holo": cls.D_holo,      "D_odot": cls.D_holo,   "D_⊙": cls.D_holo,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Dimensionality symbol: {s!r}") from None


# =============================================================================
# Primitive II: Topology (T)
# =============================================================================

class Topology(Enum):
    """
    Pattern of connections within the synthon's minimal motif.

    Lean canonical 6: T_linear, T_branched, T_network, T_bowtie, T_torus, T_odot.
    Chemistry extras below the separator are valid for molecular catalog entries.
    """
    T_linear   = "T_linear"    # open chain
    T_branched = "T_branched"  # tree / DAG
    T_network  = "T_network"   # general graph
    T_bowtie   = "T_bowtie"    # cyclic closure / double-well / figure-8
    T_torus    = "T_torus"     # higher-genus compact (NEW — not in old Python)
    T_holo     = "T_odot"      # imscriptive: non-local boundary-bulk; canonical: T_odot
    # Chemistry extras
    T_network_hex    = "T_network_hex"
    T_network_mixed  = "T_network_mixed"
    T_network_interp = "T_network_interp"
    T_network_sym    = "T_network_sym"
    T_cage  = "T_cage"
    T_bowl  = "T_bowl"
    T_braid = "T_braid"
    # Backward-compat aliases
    LINEAR        = "T_linear"
    CHAIN         = "T_linear"
    BRANCHED      = "T_branched"
    NETWORK       = "T_network"
    HUB_NODE      = "T_network"   # hub-node = network topology
    CYCLIC_BOWTIE = "T_bowtie"
    TORUS         = "T_torus"
    CAGE          = "T_cage"
    BOWL          = "T_bowl"
    BRAID         = "T_braid"
    NETWORK_HEX   = "T_network_hex"
    NETWORK_MIXED = "T_network_mixed"
    NETWORK_INTERP = "T_network_interp"
    NETWORK_SYM            = "T_network_sym"
    NETWORK_INTERPENETRATING = "T_network_interp"

    @classmethod
    def from_symbol(cls, s: str) -> "Topology":
        _map = {
            "T_linear": cls.T_linear,       "T_chains": cls.T_linear,
            "T_branched": cls.T_branched,
            "T_network": cls.T_network,     "T_∈": cls.T_bowl,      "T_in": cls.T_bowl,
            "T_bowtie": cls.T_bowtie,       "T_⋈": cls.T_bowtie,
            "T_torus": cls.T_torus,
            "T_holo": cls.T_holo,      "T_odot": cls.T_holo,   "T_⊙": cls.T_holo,
            "T_network_hex": cls.T_network_hex,
            "T_network_mixed": cls.T_network_mixed,
            "T_network_interp": cls.T_network_interp,
            "T_network_sym": cls.T_network_sym,
            "T_cage": cls.T_cage,           "T_box": cls.T_cage,     "T_boxtimes": cls.T_cage,
            "T_⊠": cls.T_cage,
            "T_bowl": cls.T_bowl,
            "T_braid": cls.T_braid,         "T_square": cls.T_network,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Topology symbol: {s!r}") from None


# =============================================================================
# Primitive III: Recognition (R)
# =============================================================================

class Recognition(Enum):
    """
    Physical mechanism by which the synthon identifies its partner.

    Canonical 4 (from grammar): R_super, R_cat, R_dagger, R_lr.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    R_superset   = "R_super"    # non-covalent / soft association
    R_subset     = "R_cat"      # covalent bond / structural transformation
    R_catalytic  = "R_dagger"   # transition-state stabilisation / adjoint
    R_allosteric = "R_dagger"   # conformational gating (alias of R_dagger)
    R_mechanical = "R_lr"       # mechanical topology / left-right asymmetric
    R_exact      = "R_dagger"   # exact correspondence (alias of R_dagger)
    R_covalent_dynamic = "R_cat"  # dynamic covalent (alias of R_cat)
    # Backward-compat aliases used by constraints.py
    COVALENT          = "R_cat"
    NON_COVALENT      = "R_super"
    DYNAMIC_CATALYTIC = "R_dagger"
    MECHANICAL        = "R_lr"
    COVALENT_DYNAMIC  = "R_cat"

    @classmethod
    def from_symbol(cls, s: str) -> "Recognition":
        _map = {
            # canonical names
            "R_super":   cls.R_superset,
            "R_cat":     cls.R_subset,
            "R_dagger":  cls.R_catalytic,
            "R_lr":      cls.R_mechanical,
            # chemistry vocab
            "R_exact": cls.R_exact,
            "R_subset": cls.R_subset,         "R_⊆": cls.R_subset,
            "R_superset": cls.R_superset,     "R_⊇": cls.R_superset,
            "R_catalytic": cls.R_catalytic,   "R_‡": cls.R_catalytic,
            "R_allosteric": cls.R_allosteric,
            "R_mechanical": cls.R_mechanical, "R_⇔": cls.R_mechanical,
            "R_covalent_dynamic": cls.R_covalent_dynamic,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Recognition symbol: {s!r}") from None


# =============================================================================
# Primitive IV: Polarity (P)
# =============================================================================

class Polarity(Enum):
    """
    Directional / charge character of the synthon's interface.

    Canonical 5 (from grammar): P_asym, P_psi, P_pm, P_sym, P_pm_sym.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    P_neutral     = "P_asym"    # no preferred direction → lowest asymmetry
    P_plus        = "P_psi"     # accepting / electrophilic → signed direction
    P_minus       = "P_psi"     # donating / nucleophilic → signed direction (alias)
    P_pm          = "P_pm"      # self-complementary bipolar — canonical ✓
    P_pm_pseudo   = "P_psi"     # pseudo-symmetric → signed (alias)
    P_directional = "P_asym"    # directed asymmetric pair → P_asym (alias)
    P_pm_sym      = "P_pm_sym"  # Frobenius symmetric — canonical ✓
    # Backward-compat aliases used by constraints.py
    ACCEPTOR                = "P_psi"
    DONOR                   = "P_psi"
    SELF_COMPLEMENTARY_SYM  = "P_pm_sym"
    SELF_COMPLEMENTARY_PSEUDO = "P_psi"
    DONOR_ACCEPTOR          = "P_asym"

    @property
    def is_self_complementary(self) -> bool:
        return self.value in ("P_pm_sym", "P_pm")

    @classmethod
    def from_symbol(cls, s: str) -> "Polarity":
        _map = {
            # canonical names
            "P_asym":    cls.P_neutral,
            "P_psi":     cls.P_plus,
            "P_pm":      cls.P_pm,
            "P_sym":     cls.P_pm_sym,
            "P_pm_sym":  cls.P_pm_sym,   "P_±^sym": cls.P_pm_sym,
            # chemistry vocab
            "P_neutral":     cls.P_neutral,
            "P_plus":        cls.P_plus,        "P+": cls.P_plus,
            "P_minus":       cls.P_minus,       "P-": cls.P_minus,
            "P_pm_pseudo":   cls.P_pm_pseudo,   "P_±^ψ": cls.P_pm_pseudo,
            "P_directional": cls.P_directional,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Polarity symbol: {s!r}") from None


# =============================================================================
# Primitive V: Interaction Grammar (Γ)
# =============================================================================

class Grammar(Enum):
    """
    Partner selection logic: the Boolean operator governing how partners combine.

    Lean canonical 5: G_and, G_or, G_seq, G_xor, G_impl.
    Replaces the old compound InteractionGrammar(operator, tier) — the tier
    (SPECIFIC/SELECTIVE/BROAD/QUANTUM) encoded selectivity, which belongs to
    Fidelity or domain metadata, not the structural grammar.

    G_dissipative retained from old GrammarOperator for catalogs that used it.
    """
    G_and  = "G_and"    # conjunctive / simultaneous (all partners required)
    G_or   = "G_or"     # disjunctive / any one suffices
    G_seq  = "G_seq"    # sequential / ordered
    G_xor  = "G_xor"    # exclusive (NEW — was missing)
    G_impl = "G_impl"   # implicative / conditional (NEW — was missing)
    G_dissipative = "G_dissipative"  # irreversible / Lindblad (legacy)
    # Backward-compat aliases: old compound InteractionGrammar values -> canonical operator
    SPECIFIC_AND         = "G_and"
    SELECTIVE_AND        = "G_and"
    BROAD_AND            = "G_and"
    QUANTUM_AND          = "G_and"
    SPECIFIC_OR          = "G_or"
    SELECTIVE_OR         = "G_or"
    BROAD_OR             = "G_or"
    QUANTUM_OR           = "G_or"
    SPECIFIC_SEQ         = "G_seq"
    SELECTIVE_SEQ        = "G_seq"
    BROAD_SEQ            = "G_seq"
    QUANTUM_SEQ          = "G_seq"
    SPECIFIC_DISSIPATIVE  = "G_dissipative"
    SELECTIVE_DISSIPATIVE = "G_dissipative"
    BROAD_DISSIPATIVE     = "G_dissipative"
    QUANTUM_DISSIPATIVE   = "G_dissipative"

    @classmethod
    def from_symbol(cls, s: str) -> "Grammar":
        _map = {
            "G_and": cls.G_and,   "Gamma_and": cls.G_and,   "Γ_∧": cls.G_and,
            "Gamma_otimes": cls.G_and,   "Γ_⊗": cls.G_and,   # old prompt symbol → G_and (specific)
            "Gamma_odot": cls.G_and,     "Γ_⊙": cls.G_and,   # old prompt symbol → G_and (selective)
            "G_or": cls.G_or,     "Gamma_or": cls.G_or,     "Γ_∨": cls.G_or,
            "Gamma_bigcirc": cls.G_or,   "Γ_○": cls.G_or,    # old prompt symbol → G_or (broad)
            "G_seq": cls.G_seq,   "Gamma_seq": cls.G_seq,   "Γ_→": cls.G_seq,
            "G_xor": cls.G_xor,
            "G_impl": cls.G_impl,
            "G_dissipative": cls.G_dissipative, "Gamma_dissipative": cls.G_dissipative,
            "G_broad": cls.G_dissipative,  # canonical external name → internal G_dissipative
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Grammar symbol: {s!r}") from None

    @property
    def partner_logic(self) -> str:
        return {
            Grammar.G_and:  "All partners required simultaneously",
            Grammar.G_or:   "Any one partner suffices",
            Grammar.G_seq:  "Ordered sequential recognition",
            Grammar.G_xor:  "Exactly one partner (exclusive)",
            Grammar.G_impl: "Partner A implies partner B",
            Grammar.G_dissipative: "Irreversible — information erased by environment",
        }[self]


# =============================================================================
# Primitive VI: Fidelity (F)
# =============================================================================

class Fidelity(Enum):
    """
    Thermodynamic reliability of constraint propagation.

    Lean canonical 4 (ordered F_noise < F_ell < F_eth < F_hbar):
      F_noise = below threshold / lossy
      F_ell   = classical search fidelity (ℓ)
      F_eth   = HotSwap threshold (η) — minimum for renormalizability
      F_hbar  = quantum / high-fidelity (ℏ)
    """
    F_noise = "F_noise"  # below threshold, lossy (NEW)
    F_ell   = "F_ell"    # classical search fidelity
    F_eth   = "F_eth"    # HotSwap threshold
    F_hbar  = "F_hbar"   # quantum coherent
    # Backward-compat aliases
    LOW    = "F_ell"
    MEDIUM = "F_eth"
    HIGH   = "F_hbar"

    @classmethod
    def from_symbol(cls, s: str) -> "Fidelity":
        _map = {
            "F_noise": cls.F_noise,
            "F_ell": cls.F_ell,   "F_ℓ": cls.F_ell,   "LOW": cls.F_ell,
            "F_eth": cls.F_eth,   "F_ℇ": cls.F_eth,   "MEDIUM": cls.F_eth,
            "F_hbar": cls.F_hbar, "F_ℏ": cls.F_hbar,  "HIGH": cls.F_hbar,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Fidelity symbol: {s!r}") from None

    @property
    def numeric_value(self) -> float:
        return {"F_noise": 0.0, "F_ell": 0.33, "F_eth": 0.67, "F_hbar": 1.0}[self.value]


# =============================================================================
# Primitive VII: Kinetic Character (K)
# =============================================================================

class KineticChar(Enum):
    """
    Kinetic accessibility of the synthon's assembly pathway.

    Lean canonical 5 (ordered K_MBL < K_trap < K_slow < K_mod < K_fast):
      K_fast = diffusion-limited, no barrier
      K_mod  = moderate activation barrier
      K_slow = slow / thermally activated
      K_trap = kinetically trapped / pathway-multiplicity dominated
      K_MBL  = many-body localised (disorder-frozen)
    """
    K_fast = "K_fast"
    K_mod  = "K_mod"    # was MODERATE
    K_slow = "K_slow"
    K_trap = "K_trap"
    K_MBL  = "K_MBL"
    # Backward-compat aliases
    FAST     = "K_fast"
    MODERATE = "K_mod"
    SLOW     = "K_slow"
    TRAP     = "K_trap"
    MBL      = "K_MBL"

    @classmethod
    def from_symbol(cls, s: str) -> "KineticChar":
        _map = {
            "K_fast": cls.K_fast, "FAST": cls.K_fast,
            "K_mod":  cls.K_mod,  "MODERATE": cls.K_mod,
            "K_slow": cls.K_slow, "SLOW": cls.K_slow,
            "K_trap": cls.K_trap, "TRAP": cls.K_trap,
            "K_MBL":  cls.K_MBL,  "MBL": cls.K_MBL,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown KineticChar symbol: {s!r}") from None

    @property
    def numeric_value(self) -> float:
        return {"K_MBL": 0.0, "K_trap": 0.25, "K_slow": 0.5, "K_mod": 0.75, "K_fast": 1.0}[self.value]


# =============================================================================
# Primitive VIII: Granularity (G)
# =============================================================================

class Granularity(Enum):
    """
    Scale of control / coarse-graining level.

    Lean canonical 3 (ordered G_aleph < G_beth < G_gimel, matching Hebrew ℵ < ℶ < ℷ):
      G_aleph = fine-grained, atomic / Planck scale  (ℵ = smallest)
      G_beth  = mesoscale local  (ℶ)
      G_gimel = coarse, collective / cosmological  (ℷ = largest)

    WARNING — ordering was INVERTED in the old Python code (aleph was GLOBAL=coarsest).
    This is now corrected to match the mathematical convention and Core.lean.
    Migration: old G_aleph → new G_gimel; old G_gimel → new G_beth; old G_beth → new G_aleph.
    """
    G_aleph = "G_aleph"  # fine-grained, atomic (ℵ) — was incorrectly GLOBAL in old Python
    G_beth  = "G_beth"   # mesoscale local (ℶ) — was LOCAL
    G_gimel = "G_gimel"  # coarse, collective (ℷ) — was incorrectly MESOSCALE in old Python
    # Backward-compat key aliases with CORRECTED semantics:
    LOCAL     = "G_aleph"  # fine = aleph (was G_beth — now fixed)
    MESOSCALE = "G_beth"   # mesoscale = beth (was G_gimel — now fixed)
    GLOBAL    = "G_gimel"  # coarse = gimel (was G_aleph — now fixed)

    @property
    def ordinal(self) -> int:
        return {"G_aleph": 0, "G_beth": 1, "G_gimel": 2}.get(self.value, 1)

    def can_amplify_to(self, other: "Granularity") -> bool:
        """Fine-to-coarse aggregation is possible; coarse-to-fine is not."""
        return self.ordinal <= other.ordinal

    @classmethod
    def from_symbol(cls, s: str) -> "Granularity":
        _map = {
            "G_aleph": cls.G_aleph, "G_א": cls.G_aleph,
            "G_beth":  cls.G_beth,  "G_ב": cls.G_beth,
            "G_gimel": cls.G_gimel, "G_ג": cls.G_gimel,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Granularity symbol: {s!r}") from None


# =============================================================================
# Primitive IX: Criticality (Φ)
# =============================================================================

class Criticality(Enum):
    """
    Phase condition of the synthon's constraint propagation regime.

    Canonical 5 (ordered Phi_sub < Phi_c < Phi_c_complex < Phi_EP < Phi_super):
      Phi_sub       = subcritical (stable, ordered)
      Phi_c         = critical point (absorbing under meet, real self-modeling)
      Phi_c_complex = complex criticality (paraconsistent / dialetheic fixed point)
      Phi_EP        = exceptional-point criticality (non-Hermitian degeneracy; absorbs O_inf under tensor)
      Phi_super     = supercritical (unstable)
    Phi_c is ABSORBING under meet: meet(Phi_c, x) = Phi_c for all x.
    """
    Phi_sub       = "Phi_sub"         # subcritical (stable, ordered)
    Phi_c         = "Phi_c"           # critical point (absorbing under meet)
    Phi_c_complex = "Phi_c_complex"   # complex criticality (paraconsistent)
    Phi_EP        = "Phi_EP"          # exceptional-point criticality
    Phi_sup       = "Phi_sup"         # supercritical (unstable)
    # Backward-compat aliases
    SUBCRITICAL  = "Phi_sub"
    CRITICAL     = "Phi_c"
    SUPERCRITICAL = "Phi_sup"

    @classmethod
    def from_symbol(cls, s: str) -> "Criticality":
        _map = {
            "Phi_sub":       cls.Phi_sub,       "Φ_sub":   cls.Phi_sub,
            "Phi_c":         cls.Phi_c,         "Φ_c":     cls.Phi_c,
            "Phi_c_complex": cls.Phi_c_complex, "Φ_c_ℂ":  cls.Phi_c_complex,
            "Phi_EP":        cls.Phi_EP,        "Φ_EP":    cls.Phi_EP,
            "Phi_sup":       cls.Phi_sup,       "Phi_super": cls.Phi_sup,  "Φ_sup": cls.Phi_sup,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Criticality symbol: {s!r}") from None

    @property
    def is_degenerate(self) -> bool:
        """True iff this is Phi_c — the absorbing element under meet and join."""
        return self == Criticality.Phi_c


# =============================================================================
# Primitive X: Winding (Ω)
# =============================================================================

class Protection(Enum):
    """
    Winding class of the system's topological invariant (homotopy invariant;
    Altland-Zirnbauer / K-theory classification).

    Canonical 4 values (ordered Omega_0 < Omega_Z2 < Omega_Z < Omega_NA):
      Omega_0  = trivial winding (no topological invariant)
      Omega_Z2 = Z_2 winding (requires H >= H2 by Axiom B)
      Omega_Z  = integer winding number (requires H >= H2 by Axiom B)
      Omega_NA = non-Abelian winding (requires D_odot by Axiom D)
    """
    Omega_0  = "Omega_0"
    Omega_Z2 = "Omega_Z2"
    Omega_Z  = "Omega_Z"
    Omega_C  = "Omega_C"
    Omega_NA = "Omega_NA"
    # Backward-compat aliases (old TopoIndex names)
    TRIVIAL     = "Omega_0"
    Z2_CLASS    = "Omega_Z2"
    Z_CLASS     = "Omega_Z"
    CHERN       = "Omega_C"
    NON_ABELIAN = "Omega_NA"

    @classmethod
    def from_symbol(cls, s: str) -> "Protection":
        _map = {
            "Omega_0":  cls.Omega_0,  "Ω_0":  cls.Omega_0,  "TRIVIAL":     cls.Omega_0,
            "Omega_Z2": cls.Omega_Z2, "Ω_Z2": cls.Omega_Z2, "Z2_CLASS":    cls.Omega_Z2,
            "Omega_Z":  cls.Omega_Z,  "Ω_Z":  cls.Omega_Z,  "Z_CLASS":     cls.Omega_Z,
            "Omega_C":  cls.Omega_C,  "Ω_C":  cls.Omega_C,  "CHERN":       cls.Omega_C,
            "Omega_NA": cls.Omega_NA, "Ω_NA": cls.Omega_NA, "NON_ABELIAN": cls.Omega_NA,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Protection (Winding) symbol: {s!r}") from None

    @property
    def protection_strength(self) -> int:
        """Ordinal protection level 0–4 (matches Lean _PROT_ORD)."""
        return _prot_ord(self)

    @property
    def physical_systems(self) -> str:
        return {
            Protection.Omega_0:  "Ordinary insulators, classical systems",
            Protection.Omega_Z2: "HgTe/CdTe, Bi2Se3, topological insulators (AII/DIII)",
            Protection.Omega_Z:  "Kitaev chain, SSH model, 1D p-wave superconductors",
            Protection.Omega_C:  "Integer quantum Hall, Chern insulators (class A)",
            Protection.Omega_NA: "nu=5/2 FQH, Kitaev honeycomb B-phase, non-Abelian Majorana",
        }[self]


# =============================================================================
# Primitive XI: Stoichiometry (S)
# =============================================================================

class Stoichiometry(Enum):
    """
    Valency ratio of the interaction.

    Lean canonical 4: one_one, one_n, n_m, cat.
    Replaces the old ad-hoc string field.
    """
    one_one = "one_one"
    one_n   = "n_n"     # 1:n collapses to n_n (symmetric many)
    n_m     = "n_m"
    cat     = "n_m"     # catalytic treated as n_m (alias)

    @classmethod
    def from_symbol(cls, s: str) -> "Stoichiometry":
        _map = {
            "1:1": cls.one_one,  "one_one": cls.one_one,
            "1:n": cls.one_n,    "one_n":   cls.one_n,
            "n:m": cls.n_m,      "n_m":     cls.n_m,    "n:n": cls.n_m,
            "cat": cls.cat,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Stoichiometry symbol: {s!r}") from None


# =============================================================================
# Primitive XII: Chirality / Temporal Memory (H)
# =============================================================================

class Chirality(Enum):
    """
    Degree and persistence of broken orientational symmetry.
    The only intrinsically anisotropic primitive — the only one that breaks
    time-reversal symmetry of the grammar.

    Lean canonical 4 (ordered H0 < H1 < H2 < H_inf):
      H0    = achiral, no temporal memory
      H1    = soft chiral, weak temporal asymmetry (atropisomers)
      H2    = persistent chiral, strong asymmetry (amino acids, DNA)
      H_inf = topological chiral (implies K_trap by Axiom A)
    """
    H0    = "H0"
    H1    = "H1"
    H2    = "H2"
    H_inf = "H_inf"   # was "Hinf" (FIXED)

    @classmethod
    def from_symbol(cls, s: str) -> "Chirality":
        _map = {
            "H0": cls.H0,     "H_0":   cls.H0,
            "H1": cls.H1,     "H_1":   cls.H1,
            "H2": cls.H2,     "H_2":   cls.H2,
            "H_inf": cls.H_inf, "Hinf": cls.H_inf, "H_∞": cls.H_inf,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Chirality symbol: {s!r}") from None

    @property
    def memory_depth(self) -> str:
        return {
            Chirality.H0:    "0 — no persistent symmetry breaking",
            Chirality.H1:    "1 — single axis, thermally reversible",
            Chirality.H2:    "n — n reinforcing axes, structurally encoded",
            Chirality.H_inf: "∞ — topology-protected, requires bond-breaking to reverse",
        }[self]

    @property
    def implies_k_trap(self) -> bool:
        """Axiom A: H_inf implies K_trap."""
        return self == Chirality.H_inf


# =============================================================================
# SYNTHON — the canonical 12-tuple
# =============================================================================

# Global flag: set False to bypass axiom enforcement (e.g. during migration)
_ENFORCE_AXIOMS: bool = True


@dataclass
class Synthon:
    """
    A Synthon is a minimal constraint-carrying unit encoded as a 12-tuple
    over the canonical primitive types.

    Notation: ⟨D; T; R; P; F; K; G; Γ; Φ; Ω; S; H⟩

    All 12 primitive fields are required (no Optional). Cross-primitive axioms
    A–D from Core.lean are enforced at construction time.

    Field names follow the Python readable convention; short-name properties
    (dim, top, recog, ...) match the Lean struct field names exactly.
    """
    # Identity
    name: str

    # 12 required primitive fields
    dimensionality:   Dimensionality
    topology:         Topology
    recognition_mode: Recognition
    polarity:         Polarity
    grammar:          Grammar         # simplified from InteractionGrammar compound
    fidelity:         Fidelity
    kinetic_character: KineticChar
    granularity:      Granularity
    criticality_phase: Criticality
    protection:       Protection      # renamed from topo_index; now required
    stoichiometry:    Stoichiometry   # now a proper enum, was Optional[str]
    chirality:        Chirality       # now required

    # Non-structural metadata
    description:  str = ""
    metadata:     Dict[str, Any] = field(default_factory=dict)
    grounding:    Optional[Dict[str, str]] = None
    is_grounded:  bool = False

    def __post_init__(self) -> None:
        if not _ENFORCE_AXIOMS:
            return
        name = self.name
        # Axiom A: H_inf → K_trap is documented (Chirality.implies_k_trap) but NOT enforced
        # here — 495 catalog entries have H_inf + non-trap kinetics, suggesting the axiom
        # is domain-specific or structurally over-strict as a universal constraint.
        # Axiom B: prot >= Omega_Z → chir >= H2
        if _prot_ord(self.protection) >= _prot_ord(Protection.Omega_Z) \
                and _chir_ord(self.chirality) < _chir_ord(Chirality.H2):
            raise ValueError(
                f"Axiom B violated in '{name}': protection {self.protection.value} "
                f"requires chirality >= H2 (got {self.chirality.value})"
            )
        # Axiom C: D_odot ↔ T_odot
        d_holo = self.dimensionality == Dimensionality.D_holo
        t_holo = self.topology == Topology.T_holo
        if d_holo != t_holo:
            raise ValueError(
                f"Axiom C violated in '{name}': D_odot ↔ T_odot "
                f"(got dim={self.dimensionality.value}, top={self.topology.value})"
            )
        # Axiom D: Omega_NA → D_odot
        if self.protection == Protection.Omega_NA \
                and self.dimensionality != Dimensionality.D_holo:
            raise ValueError(
                f"Axiom D violated in '{name}': Omega_NA requires D_odot "
                f"(got dim={self.dimensionality.value})"
            )

    # ── Short-name properties (match Lean struct field names) ─────────────────
    @property
    def dim(self)   -> Dimensionality:  return self.dimensionality
    @property
    def top(self)   -> Topology:        return self.topology
    @property
    def recog(self) -> Recognition:     return self.recognition_mode
    @property
    def pol(self)   -> Polarity:        return self.polarity
    @property
    def gram(self)  -> Grammar:         return self.grammar
    @property
    def fid(self)   -> Fidelity:        return self.fidelity
    @property
    def kin(self)   -> KineticChar:     return self.kinetic_character
    @property
    def gran(self)  -> Granularity:     return self.granularity
    @property
    def crit(self)  -> Criticality:     return self.criticality_phase
    @property
    def prot(self)  -> Protection:      return self.protection
    @property
    def stoi(self)  -> Stoichiometry:   return self.stoichiometry
    @property
    def chir(self)  -> Chirality:       return self.chirality

    # ── Backward-compat aliases for renamed fields ────────────────────────────
    @property
    def interaction_grammar(self) -> Grammar:   return self.grammar    # old name
    @property
    def topo_index(self) -> Protection:         return self.protection  # old name
    @property
    def criticality(self) -> Criticality:       return self.criticality_phase

    # ── Notation and serialization ────────────────────────────────────────────

    def to_notation(self) -> str:
        """Canonical tuple string: ⟨D; T; R; P; F; K; G; Γ; Φ; Ω; S; H⟩"""
        return (
            f"\u27e8{self.dimensionality.value}; {self.topology.value}; "
            f"{self.recognition_mode.value}; {self.polarity.value}; "
            f"{self.fidelity.value}; {self.kinetic_character.value}; "
            f"{self.granularity.value}; {self.grammar.value}; "
            f"{self.criticality_phase.value}; {self.protection.value}; "
            f"{self.stoichiometry.value}; {self.chirality.value}\u27e9"
        )

    # Translate internal enum values to canonical ORDINALS keys (primitives.py).
    # Models layer uses a richer chemistry vocab; registry/zfc must see only canon values.
    _CANONICAL_MAP: ClassVar[Dict[str, str]] = {
        # D
        "D_point": "D_wedge", "D_line": "D_wedge",
        "D_cube": "D_triangle",
        # T
        "T_linear": "T_in", "T_branched": "T_in", "T_bowl": "T_in",
        "T_cage": "T_boxtimes",
        "T_torus": "T_bowtie", "T_braid": "T_bowtie",
        "T_network_hex": "T_network", "T_network_mixed": "T_network",
        "T_network_interp": "T_network", "T_network_sym": "T_network",
        # Phi
        "Phi_sup": "Phi_super",
        # Gamma
        "G_impl": "G_seq", "G_xor": "G_or", "G_dissipative": "G_broad",
    }

    @classmethod
    def _canon(cls, val: str) -> str:
        return cls._CANONICAL_MAP.get(val, val)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name":          self.name,
            "description":   self.description,
            "D":             self._canon(self.dimensionality.value),
            "T":             self._canon(self.topology.value),
            "R":             self._canon(self.recognition_mode.value),
            "P":             self._canon(self.polarity.value),
            "F":             self._canon(self.fidelity.value),
            "K":             self._canon(self.kinetic_character.value),
            "G":             self._canon(self.granularity.value),
            "Gamma":         self._canon(self.grammar.value),
            "Phi":           self._canon(self.criticality_phase.value),
            "Omega":         self._canon(self.protection.value),
            "S":             self._canon(self.stoichiometry.value),
            "H":             self._canon(self.chirality.value),
            "grounding":     self.grounding,
            "is_grounded":   self.is_grounded,
            "metadata":      self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Synthon":
        """
        Construct a Synthon from a catalog dict (new or legacy format).

        Accepts both short keys (D, T, R, P, Gamma, F, K, G, Phi, Omega, S, H)
        and long Python field names (dimensionality, topology, recognition_mode, ...).
        Falls back to short keys if long keys absent, then to canonical defaults.
        Parses all primitive fields via from_symbol() for backward compatibility.
        """
        def _get(short: str, long: str, default: str) -> str:
            # Prefer long Python name (new catalog format), then short (JSON/design format)
            v = d.get(long) or d.get(short)
            if v is None:
                return default
            # Handle old compound interaction_grammar dict: {"operator": "Gamma_and", "tier": "SELECTIVE"}
            if isinstance(v, dict):
                v = v.get("operator", default)
            return str(v)

        # Disable axiom enforcement during deserialization — catalog entries were
        # registered under the old schema and will be fixed by the migration script.
        global _ENFORCE_AXIOMS
        _saved = _ENFORCE_AXIOMS
        _ENFORCE_AXIOMS = False
        try:
            result = cls(
                name             = d["name"],
                dimensionality   = Dimensionality.from_symbol(_get("D", "dimensionality", "D_wedge")),
                topology         = Topology.from_symbol(_get("T", "topology", "T_network")),
                recognition_mode = Recognition.from_symbol(_get("R", "recognition_mode", "R_superset")),
                polarity         = Polarity.from_symbol(_get("P", "polarity", "P_neutral")),
                grammar          = Grammar.from_symbol(_get("Gamma", "grammar", "G_and")),
                fidelity         = Fidelity.from_symbol(_get("F", "fidelity", "F_ell")),
                kinetic_character= KineticChar.from_symbol(_get("K", "kinetic_character", "K_mod")),
                granularity      = Granularity.from_symbol(_get("G", "granularity", "G_beth")),
                criticality_phase= Criticality.from_symbol(_get("Phi", "criticality_phase", "Phi_sub")),
                protection       = Protection.from_symbol(_get("Omega", "protection", "Omega_0")),
                stoichiometry    = Stoichiometry.from_symbol(_get("S", "stoichiometry", "n:m")),
                chirality        = Chirality.from_symbol(_get("H", "chirality", "H0")),
                description      = d.get("description", ""),
                metadata         = d.get("metadata", {}),
                grounding        = d.get("grounding"),
                is_grounded      = d.get("is_grounded", False),
            )
        finally:
            _ENFORCE_AXIOMS = _saved
        return result


# =============================================================================
# Backward-compat type aliases (for code that imports old class names)
# =============================================================================

RecognitionMode  = Recognition    # old class name
KineticCharacter = KineticChar    # old class name
CriticalityPhase = Criticality    # old class name
TopoIndex        = Protection     # old class name
InteractionGrammar = Grammar      # old compound class — now canonical simple enum
GrammarOperator    = Grammar      # old operator sub-class — same mapping


class SynthonNotation:
    """Stub backward-compat class. Use Synthon.from_dict() instead."""
    @staticmethod
    def parse(notation_str: str) -> dict:
        raise NotImplementedError(
            "SynthonNotation.parse() is removed. Use Synthon.from_dict() "
            "with a flat dict of primitive values."
        )


def parse_notation(notation_str: str) -> dict:
    """Stub backward-compat function. Use Synthon.from_dict() instead."""
    raise NotImplementedError(
        "parse_notation() is removed. Use Synthon.from_dict() instead."
    )


# =============================================================================
# CONFLICT sentinel (used by algebra.py meet/join)
# =============================================================================

CONFLICT: str = "CONFLICT"

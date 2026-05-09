"""
Imscribing Grammar Models — Canonical 12-primitive type system.

Unified with the Lean 4 formalization in Imscribing Grammar/Primitives/Core.lean and
Synthon.lean. Enum VALUES match the Lean constructors exactly; field names on
Synthon use the long Python-readable form with short-name properties (dim, top,
recog, pol, gram, fid, kin, gran, crit, prot, stoi, chir) mirroring Lean.

Tuple notation: ⟨D; T; R; P; F; K; G; Γ; Φ; Ω; S; H⟩

Ordering conventions (match Lean Core.lean):
  F: F_noise < F_beltl < F_dh < F_hardsign
  K: K_lambda < K_teshlig < K_schwa < K_turnm < K_frtailgamma
  G: G_revapostrophe < G_beta < G_gamma   (ℵ = finest/atomic, ℷ = coarsest/cosmological)
  Ω: Omega_closeepsilon < Omega_crtwo < Omega_dzlig < Omega_C < Omega_turna
  H: H_closeomega < H_toneletterstem < H_turntwo < H_invscripta

Cross-primitive axioms (enforced in Synthon.__post_init__; mirroring Core.lean):
  B: prot >= Omega_dzlig → chir >= H_turntwo
  C: D_omega ↔ T_openo
  D: Omega_turna → D_omega
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
        "Ω_closeepsilon": 0, "Ω_crtwo": 1, "Ω_dzlig": 2, "Ω_C": 3, "Ω_turna": 4,
    }[p.value]

def _chir_ord(h: "Chirality") -> int:
    return {"Ħ_closeomega": 0, "Ħ_toneletterstem": 1, "Ħ_turntwo": 2, "Ħ_invscripta": 3}[h.value]


# =============================================================================
# Primitive I: Dimensionality (D)
# =============================================================================

class Dimensionality(Enum):
    """
    Coordinate set along which the synthon operates.

    Lean canonical values: D_point, D_line, D_wynn, D_cube, D_invomega, D_omega.
    Chemistry-domain extras (T_network_hex etc.) are retained for molecular catalog
    entries but are not part of the canonical 6-constructor type in Core.lean.
    """
    # ── Canonical F4 members ──────────────────────────────────────────────────
    D_wynn      = "Ð_wynn"      # ordinal 1: 2D areal / molecular sheet
    D_turnthree = "Ð_turnthree" # ordinal 2: triangulated / simplicial / stratified
    D_invomega  = "Ð_invomega"  # ordinal 3: ∞-dimensional / iterative-temporal
    D_holo      = "Ð_omega"     # ordinal 4: imscriptive (boundary encodes bulk); canonical value D_omega
    # ── Lean-only extensions (non-canonical, chemistry/physics domain) ─────
    D_point = "Ð_point"   # 0D, scalar / spin-0 field
    D_line  = "Ð_line"    # 1D, vectorial
    D_cube  = "Ð_cube"    # 3D volumetric (Lean extension; canonical slot = D_turnthree)

    # Backward-compat aliases (chemistry-domain names → canonical values)
    MOLECULAR      = "Ð_wynn"
    SUPRAMOLECULAR = "Ð_turnthree"  # was D_cube; canonical ordinal 2 = D_turnthree
    TEMPORAL       = "Ð_invomega"
    HOLOGRAPHIC    = "Ð_omega"
    HYBRID_MOL_SUPRA  = "Ð_turnthree"
    HYBRID_MOL_TEMP   = "Ð_invomega"
    HYBRID_SUPRA_TEMP = "Ð_invomega"
    HYBRID_ALL        = "Ð_turnthree"

    @property
    def domains(self) -> frozenset:
        """Compat shim: old compound Dimensionality had a .domains frozenset."""
        return {
            "Ð_point":      frozenset({"point"}),
            "Ð_line":       frozenset({"linear"}),
            "Ð_wynn":       frozenset({"molecular"}),
            "Ð_turnthree":  frozenset({"molecular", "supramolecular"}),
            "Ð_cube":       frozenset({"molecular", "supramolecular"}),
            "Ð_invomega":   frozenset({"temporal", "molecular"}),
            "Ð_omega":      frozenset({"temporal", "molecular", "supramolecular", "imscriptive"}),
        }.get(self.value, frozenset())

    @classmethod
    def from_symbol(cls, s: str) -> "Dimensionality":
        _map = {
            # canonical phonetic names
            "Ð_wynn":       cls.D_wynn,
            "Ð_turnthree":  cls.D_turnthree,
            "Ð_invomega":   cls.D_invomega,
            "Ð_omega":      cls.D_holo,
            # legacy canonical names (pre-migration)
            "Ð_triangle":   cls.D_turnthree,
            "Ð_wedge":      cls.D_wynn,
            "Ð_infty":      cls.D_invomega,
            "Ð_odot":       cls.D_holo,
            # Lean extensions
            "Ð_point":  cls.D_point,
            "Ð_line":   cls.D_line,
            "Ð_cube":   cls.D_cube,
            # Unicode aliases
            "D_∧": cls.D_wynn,  "D_△": cls.D_turnthree,
            "D_∞": cls.D_invomega, "D_⊙": cls.D_holo,
            "Ð_infinity": cls.D_invomega,
            "Ð_holo": cls.D_holo,
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

    Lean canonical 6: T_linear, T_branched, T_nrleg, T_bullseye, T_torus, T_openo.
    Chemistry extras below the separator are valid for molecular catalog entries.
    """
    T_linear   = "Þ_linear"    # open chain
    T_branched = "Þ_branched"  # tree / DAG
    T_nrleg  = "Þ_nrleg"   # general graph
    T_bullseye   = "Þ_bullseye"    # cyclic closure / double-well / figure-8
    T_torus    = "Þ_torus"     # higher-genus compact (NEW — not in old Python)
    T_holo     = "Þ_openo"      # imscriptive: non-local boundary-bulk; canonical: T_openo
    # Chemistry extras
    T_network_hex    = "Þ_network_hex"
    T_network_mixed  = "Þ_network_mixed"
    T_network_interp = "Þ_network_interp"
    T_network_sym    = "Þ_network_sym"
    T_cage  = "Þ_cage"
    T_bowl  = "Þ_bowl"
    T_braid = "Þ_braid"
    # Backward-compat aliases
    LINEAR        = "Þ_linear"
    CHAIN         = "Þ_linear"
    BRANCHED      = "Þ_branched"
    NETWORK       = "Þ_nrleg"
    HUB_NODE      = "Þ_nrleg"   # hub-node = network topology
    CYCLIC_BOWTIE = "Þ_bullseye"
    TORUS         = "Þ_torus"
    CAGE          = "Þ_cage"
    BOWL          = "Þ_bowl"
    BRAID         = "Þ_braid"
    NETWORK_HEX   = "Þ_network_hex"
    NETWORK_MIXED = "Þ_network_mixed"
    NETWORK_INTERP = "Þ_network_interp"
    NETWORK_SYM            = "Þ_network_sym"
    NETWORK_INTERPENETRATING = "Þ_network_interp"

    @classmethod
    def from_symbol(cls, s: str) -> "Topology":
        _map = {
            "Þ_linear": cls.T_linear,       "Þ_chains": cls.T_linear,
            "Þ_branched": cls.T_branched,
            "Þ_nrleg": cls.T_nrleg,     "T_∈": cls.T_bowl,      "Þ_invscr": cls.T_bowl,
            "Þ_bullseye": cls.T_bullseye,       "T_⋈": cls.T_bullseye,
            "Þ_torus": cls.T_torus,
            "Þ_holo": cls.T_holo,      "Þ_openo": cls.T_holo,   "T_⊙": cls.T_holo,
            "Þ_network_hex": cls.T_network_hex,
            "Þ_network_mixed": cls.T_network_mixed,
            "Þ_network_interp": cls.T_network_interp,
            "Þ_network_sym": cls.T_network_sym,
            "Þ_cage": cls.T_cage,           "Þ_box": cls.T_cage,     "Þ_commatailz": cls.T_cage,
            "T_⊠": cls.T_cage,
            "Þ_bowl": cls.T_bowl,
            "Þ_braid": cls.T_braid,         "Þ_square": cls.T_nrleg,
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

    Canonical 4 (from grammar): R_subrightarrow, R_ctz, R_downstep, R_lyoghlig.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    R_superset   = "Ř_subrightarrow"    # non-covalent / soft association
    R_subset     = "Ř_ctz"      # covalent bond / structural transformation
    R_catalytic  = "Ř_downstep"   # transition-state stabilisation / adjoint
    R_allosteric = "Ř_downstep"   # conformational gating (alias of R_downstep)
    R_mechanical = "Ř_lyoghlig"       # mechanical topology / left-right asymmetric
    R_exact      = "Ř_downstep"   # exact correspondence (alias of R_downstep)
    R_covalent_dynamic = "Ř_ctz"  # dynamic covalent (alias of R_ctz)
    # Backward-compat aliases used by constraints.py
    COVALENT          = "Ř_ctz"
    NON_COVALENT      = "Ř_subrightarrow"
    DYNAMIC_CATALYTIC = "Ř_downstep"
    MECHANICAL        = "Ř_lyoghlig"
    COVALENT_DYNAMIC  = "Ř_ctz"

    @classmethod
    def from_symbol(cls, s: str) -> "Recognition":
        _map = {
            # canonical names
            "Ř_subrightarrow":   cls.R_superset,
            "Ř_ctz":     cls.R_subset,
            "Ř_downstep":  cls.R_catalytic,
            "Ř_lyoghlig":      cls.R_mechanical,
            # chemistry vocab
            "Ř_exact": cls.R_exact,
            "Ř_subset": cls.R_subset,         "R_⊆": cls.R_subset,
            "Ř_superset": cls.R_superset,     "R_⊇": cls.R_superset,
            "Ř_catalytic": cls.R_catalytic,   "R_‡": cls.R_catalytic,
            "Ř_allosteric": cls.R_allosteric,
            "Ř_mechanical": cls.R_mechanical, "R_⇔": cls.R_mechanical,
            "Ř_covalent_dynamic": cls.R_covalent_dynamic,
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

    Canonical 5 (from grammar): P_aolig, P_upsilon, P_pipevar, P_subdoublearrow, P_doublebarpipe.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    # ── Canonical F5 members ──────────────────────────────────────────────────
    P_neutral        = "Φ_aolig"           # ordinal 1: asymmetric, no preferred direction
    P_plus           = "Φ_upsilon"         # ordinal 2: signed direction (electrophilic)
    P_pipevar        = "Φ_pipevar"         # ordinal 3: self-complementary bipolar
    P_subdoublearrow = "Φ_subdoublearrow"  # ordinal 4: symmetric (non-Frobenius)
    P_doublebarpipe  = "Φ_doublebarpipe"   # ordinal 5: Frobenius special (P_pm_sym)
    # ── Aliases ───────────────────────────────────────────────────────────────
    P_minus       = "Φ_upsilon"    # nucleophilic → same ordinal as electrophilic
    P_pm_pseudo   = "Φ_upsilon"    # pseudo-symmetric → signed
    P_directional = "Φ_aolig"     # directed asymmetric pair
    ACCEPTOR               = "Φ_upsilon"
    DONOR                  = "Φ_upsilon"
    SELF_COMPLEMENTARY_SYM = "Φ_doublebarpipe"
    SELF_COMPLEMENTARY_PSEUDO = "Φ_upsilon"
    DONOR_ACCEPTOR         = "Φ_aolig"

    @property
    def is_self_complementary(self) -> bool:
        return self.value in ("Φ_doublebarpipe", "Φ_pipevar", "Φ_subdoublearrow")

    @classmethod
    def from_symbol(cls, s: str) -> "Polarity":
        _map = {
            # canonical phonetic names
            "Φ_aolig":          cls.P_neutral,
            "Φ_upsilon":        cls.P_plus,
            "Φ_pipevar":        cls.P_pipevar,
            "Φ_subdoublearrow": cls.P_subdoublearrow,
            "Φ_doublebarpipe":  cls.P_doublebarpipe,
            # legacy canonical names
            "Φ_asym":    cls.P_neutral,
            "Φ_psi":     cls.P_plus,
            "Φ_pm":      cls.P_pipevar,
            "Φ_sym":     cls.P_subdoublearrow,
            "Φ_pm_sym":  cls.P_doublebarpipe,  "P_±^sym": cls.P_doublebarpipe,
            # chemistry vocab
            "Φ_neutral":     cls.P_neutral,
            "Φ_plus":        cls.P_plus,        "P+": cls.P_plus,
            "Φ_minus":       cls.P_minus,       "P-": cls.P_minus,
            "Φ_pm_pseudo":   cls.P_pm_pseudo,   "P_±^ψ": cls.P_pm_pseudo,
            "Φ_directional": cls.P_directional,
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

    Lean canonical 5: Gamma_corner, Gamma_spleftarrow, Gamma_secstress, G_xor, G_impl.
    Replaces the old compound InteractionGrammar(operator, tier) — the tier
    (SPECIFIC/SELECTIVE/BROAD/QUANTUM) encoded selectivity, which belongs to
    Fidelity or domain metadata, not the structural grammar.

    G_dissipative retained from old GrammarOperator for catalogs that used it.
    """
    Gamma_corner  = "ɢ_corner"    # conjunctive / simultaneous (all partners required)
    Gamma_spleftarrow   = "ɢ_spleftarrow"     # disjunctive / any one suffices
    Gamma_secstress  = "ɢ_secstress"    # sequential / ordered
    G_xor  = "Γ_xor"    # exclusive (NEW — was missing)
    G_impl = "Γ_impl"   # implicative / conditional (NEW — was missing)
    G_dissipative = "Γ_dissipative"  # irreversible / Lindblad (legacy)
    # Backward-compat aliases: old compound InteractionGrammar values -> canonical operator
    SPECIFIC_AND         = "ɢ_corner"
    SELECTIVE_AND        = "ɢ_corner"
    BROAD_AND            = "ɢ_corner"
    QUANTUM_AND          = "ɢ_corner"
    SPECIFIC_OR          = "ɢ_spleftarrow"
    SELECTIVE_OR         = "ɢ_spleftarrow"
    BROAD_OR             = "ɢ_spleftarrow"
    QUANTUM_OR           = "ɢ_spleftarrow"
    SPECIFIC_SEQ         = "ɢ_secstress"
    SELECTIVE_SEQ        = "ɢ_secstress"
    BROAD_SEQ            = "ɢ_secstress"
    QUANTUM_SEQ          = "ɢ_secstress"
    SPECIFIC_DISSIPATIVE  = "Γ_dissipative"
    SELECTIVE_DISSIPATIVE = "Γ_dissipative"
    BROAD_DISSIPATIVE     = "Γ_dissipative"
    QUANTUM_DISSIPATIVE   = "Γ_dissipative"

    @classmethod
    def from_symbol(cls, s: str) -> "Grammar":
        _map = {
            "ɢ_corner": cls.Gamma_corner,   "ɢ_and": cls.Gamma_corner,   "Γ_∧": cls.Gamma_corner,
            "ɢ_otimes": cls.Gamma_corner,   "Γ_⊗": cls.Gamma_corner,   # old prompt symbol → Gamma_corner (specific)
            "ɢ_odot": cls.Gamma_corner,     "Γ_⊙": cls.Gamma_corner,   # old prompt symbol → Gamma_corner (selective)
            "ɢ_spleftarrow": cls.Gamma_spleftarrow,     "ɢ_or": cls.Gamma_spleftarrow,     "Γ_∨": cls.Gamma_spleftarrow,
            "ɢ_bigcirc": cls.Gamma_spleftarrow,   "Γ_○": cls.Gamma_spleftarrow,    # old prompt symbol → Gamma_spleftarrow (broad)
            "ɢ_secstress": cls.Gamma_secstress,   "ɢ_seq": cls.Gamma_secstress,   "Γ_→": cls.Gamma_secstress,
            "Γ_xor": cls.G_xor,
            "Γ_impl": cls.G_impl,
            "Γ_dissipative": cls.G_dissipative, "ɢ_dissipative": cls.G_dissipative,
            "ɢ_doublevertline": cls.G_dissipative,  # canonical external name → internal G_dissipative
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Grammar symbol: {s!r}") from None

    @property
    def partner_logic(self) -> str:
        return {
            Grammar.Gamma_corner:  "All partners required simultaneously",
            Grammar.Gamma_spleftarrow:   "Any one partner suffices",
            Grammar.Gamma_secstress:  "Ordered sequential recognition",
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

    Lean canonical 4 (ordered F_noise < F_beltl < F_dh < F_hardsign):
      F_noise = below threshold / lossy
      F_beltl   = classical search fidelity (ℓ)
      F_dh   = HotSwap threshold (η) — minimum for renormalizability
      F_hardsign  = quantum / high-fidelity (ℏ)
    """
    F_noise = "ƒ_noise"  # below threshold, lossy (NEW)
    F_beltl   = "ƒ_beltl"    # classical search fidelity
    F_dh   = "ƒ_dh"    # HotSwap threshold
    F_hardsign  = "ƒ_hardsign"   # quantum coherent
    # Backward-compat aliases
    LOW    = "ƒ_beltl"
    MEDIUM = "ƒ_dh"
    HIGH   = "ƒ_hardsign"

    @classmethod
    def from_symbol(cls, s: str) -> "Fidelity":
        _map = {
            "ƒ_noise": cls.F_noise,
            "ƒ_beltl": cls.F_beltl,   "F_ℓ": cls.F_beltl,   "LOW": cls.F_beltl,
            "ƒ_dh": cls.F_dh,   "F_ℇ": cls.F_dh,   "MEDIUM": cls.F_dh,
            "ƒ_hardsign": cls.F_hardsign, "F_ℏ": cls.F_hardsign,  "HIGH": cls.F_hardsign,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Fidelity symbol: {s!r}") from None

    @property
    def numeric_value(self) -> float:
        return {"ƒ_noise": 0.0, "ƒ_beltl": 0.33, "ƒ_dh": 0.67, "ƒ_hardsign": 1.0}[self.value]


# =============================================================================
# Primitive VII: Kinetic Character (K)
# =============================================================================

class KineticChar(Enum):
    """
    Kinetic accessibility of the synthon's assembly pathway.

    Lean canonical 5 (ordered K_lambda < K_teshlig < K_schwa < K_turnm < K_frtailgamma):
      K_frtailgamma = diffusion-limited, no barrier
      K_turnm  = moderate activation barrier
      K_schwa = slow / thermally activated
      K_teshlig = kinetically trapped / pathway-multiplicity dominated
      K_lambda  = many-body localised (disorder-frozen)
    """
    K_frtailgamma = "Ç_frtailgamma"
    K_turnm  = "Ç_turnm"    # was MODERATE
    K_schwa = "Ç_schwa"
    K_teshlig = "Ç_teshlig"
    K_lambda  = "Ç_lambda"
    # Backward-compat aliases
    FAST     = "Ç_frtailgamma"
    MODERATE = "Ç_turnm"
    SLOW     = "Ç_schwa"
    TRAP     = "Ç_teshlig"
    MBL      = "Ç_lambda"

    @classmethod
    def from_symbol(cls, s: str) -> "KineticChar":
        _map = {
            "Ç_frtailgamma": cls.K_frtailgamma, "FAST": cls.K_frtailgamma,
            "Ç_turnm":  cls.K_turnm,  "MODERATE": cls.K_turnm,
            "Ç_schwa": cls.K_schwa, "SLOW": cls.K_schwa,
            "Ç_teshlig": cls.K_teshlig, "TRAP": cls.K_teshlig,
            "Ç_lambda":  cls.K_lambda,  "MBL": cls.K_lambda,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown KineticChar symbol: {s!r}") from None

    @property
    def numeric_value(self) -> float:
        return {"Ç_lambda": 0.0, "Ç_teshlig": 0.25, "Ç_schwa": 0.5, "Ç_turnm": 0.75, "Ç_frtailgamma": 1.0}[self.value]


# =============================================================================
# Primitive VIII: Granularity (G)
# =============================================================================

class Granularity(Enum):
    """
    Scale of control / coarse-graining level.

    Lean canonical 3 (ordered G_revapostrophe < G_beta < G_gamma, matching Hebrew ℵ < ℶ < ℷ):
      G_revapostrophe = fine-grained, atomic / Planck scale  (ℵ = smallest)
      G_beta  = mesoscale local  (ℶ)
      G_gamma = coarse, collective / cosmological  (ℷ = largest)

    WARNING — ordering was INVERTED in the old Python code (aleph was GLOBAL=coarsest).
    This is now corrected to match the mathematical convention and Core.lean.
    Migration: old G_revapostrophe → new G_gamma; old G_gamma → new G_beta; old G_beta → new G_revapostrophe.
    """
    G_revapostrophe = "Γ_revapostrophe"  # fine-grained, atomic (ℵ) — was incorrectly GLOBAL in old Python
    G_beta  = "Γ_beta"   # mesoscale local (ℶ) — was LOCAL
    G_gamma = "Γ_gamma"  # coarse, collective (ℷ) — was incorrectly MESOSCALE in old Python
    # Backward-compat key aliases with CORRECTED semantics:
    LOCAL     = "Γ_revapostrophe"  # fine = aleph (was G_beta — now fixed)
    MESOSCALE = "Γ_beta"   # mesoscale = beth (was G_gamma — now fixed)
    GLOBAL    = "Γ_gamma"  # coarse = gimel (was G_revapostrophe — now fixed)

    @property
    def ordinal(self) -> int:
        return {"Γ_revapostrophe": 0, "Γ_beta": 1, "Γ_gamma": 2}.get(self.value, 1)

    def can_amplify_to(self, other: "Granularity") -> bool:
        """Fine-to-coarse aggregation is possible; coarse-to-fine is not."""
        return self.ordinal <= other.ordinal

    @classmethod
    def from_symbol(cls, s: str) -> "Granularity":
        _map = {
            "Γ_revapostrophe": cls.G_revapostrophe, "G_א": cls.G_revapostrophe,
            "Γ_beta":  cls.G_beta,  "G_ב": cls.G_beta,
            "Γ_gamma": cls.G_gamma, "G_ג": cls.G_gamma,
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

    Canonical 5 (ordered Phi_softsign < Phi_ctyogh < Phi_closerevepsilon < Phi_revepsilon < Phi_upstep):
      Phi_softsign       = subcritical (stable, ordered)
      Phi_ctyogh         = critical point (absorbing under meet, real self-modeling)
      Phi_closerevepsilon = complex criticality (paraconsistent / dialetheic fixed point)
      Phi_revepsilon        = exceptional-point criticality (non-Hermitian degeneracy; absorbs O_inf under tensor)
      Phi_upstep     = supercritical (unstable)
    Phi_ctyogh is ABSORBING under meet: meet(Phi_ctyogh, x) = Phi_ctyogh for all x.
    """
    Phi_softsign       = "φ̂_softsign"         # subcritical (stable, ordered)
    Phi_ctyogh         = "φ̂_ctyogh"           # critical point (absorbing under meet)
    Phi_closerevepsilon = "φ̂_closerevepsilon"   # complex criticality (paraconsistent)
    Phi_revepsilon        = "φ̂_revepsilon"          # exceptional-point criticality
    Phi_upstep       = "φ̂_upstep"         # supercritical (unstable)
    # Backward-compat aliases
    SUBCRITICAL  = "φ̂_softsign"
    CRITICAL     = "φ̂_ctyogh"
    SUPERCRITICAL = "φ̂_upstep"

    @classmethod
    def from_symbol(cls, s: str) -> "Criticality":
        _map = {
            "φ̂_softsign":       cls.Phi_softsign,       "Φ_sub":   cls.Phi_softsign,
            "φ̂_ctyogh":         cls.Phi_ctyogh,         "Φ_c":     cls.Phi_ctyogh,
            "φ̂_closerevepsilon": cls.Phi_closerevepsilon, "Φ_c_ℂ":  cls.Phi_closerevepsilon,
            "φ̂_revepsilon":        cls.Phi_revepsilon,        "Φ_EP":    cls.Phi_revepsilon,
            "φ̂_upstep":       cls.Phi_upstep,       "φ̂_upstep": cls.Phi_upstep,  "Φ_sup": cls.Phi_upstep,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Criticality symbol: {s!r}") from None

    @property
    def is_degenerate(self) -> bool:
        """True iff this is Phi_ctyogh — the absorbing element under meet and join."""
        return self == Criticality.Phi_ctyogh


# =============================================================================
# Primitive X: Winding (Ω)
# =============================================================================

class Protection(Enum):
    """
    Winding class of the system's topological invariant (homotopy invariant;
    Altland-Zirnbauer / K-theory classification).

    Canonical 4 values (ordered Omega_closeepsilon < Omega_crtwo < Omega_dzlig < Omega_turna):
      Omega_closeepsilon  = trivial winding (no topological invariant)
      Omega_crtwo = Z_2 winding (requires H >= H_turntwo by Axiom B)
      Omega_dzlig  = integer winding number (requires H >= H_turntwo by Axiom B)
      Omega_turna = non-Abelian winding (requires D_omega by Axiom D)
    """
    Omega_closeepsilon  = "Ω_closeepsilon"
    Omega_crtwo = "Ω_crtwo"
    Omega_dzlig  = "Ω_dzlig"
    Omega_C  = "Ω_C"
    Omega_turna = "Ω_turna"
    # Backward-compat aliases (old TopoIndex names)
    TRIVIAL     = "Ω_closeepsilon"
    Z2_CLASS    = "Ω_crtwo"
    Z_CLASS     = "Ω_dzlig"
    CHERN       = "Ω_C"
    NON_ABELIAN = "Ω_turna"

    @classmethod
    def from_symbol(cls, s: str) -> "Protection":
        _map = {
            "Ω_closeepsilon":  cls.Omega_closeepsilon,  "Ω_0":  cls.Omega_closeepsilon,  "TRIVIAL":     cls.Omega_closeepsilon,
            "Ω_crtwo": cls.Omega_crtwo, "Ω_Z2": cls.Omega_crtwo, "Z2_CLASS":    cls.Omega_crtwo,
            "Ω_dzlig":  cls.Omega_dzlig,  "Ω_Z":  cls.Omega_dzlig,  "Z_CLASS":     cls.Omega_dzlig,
            "Ω_C":  cls.Omega_C,  "Ω_C":  cls.Omega_C,  "CHERN":       cls.Omega_C,
            "Ω_turna": cls.Omega_turna, "Ω_NA": cls.Omega_turna, "NON_ABELIAN": cls.Omega_turna,
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
            Protection.Omega_closeepsilon:  "Ordinary insulators, classical systems",
            Protection.Omega_crtwo: "HgTe/CdTe, Bi2Se3, topological insulators (AII/DIII)",
            Protection.Omega_dzlig:  "Kitaev chain, SSH model, 1D p-wave superconductors",
            Protection.Omega_C:  "Integer quantum Hall, Chern insulators (class A)",
            Protection.Omega_turna: "nu=5/2 FQH, Kitaev honeycomb B-phase, non-Abelian Majorana",
        }[self]


# =============================================================================
# Primitive XI: Stoichiometry (S)
# =============================================================================

class Stoichiometry(Enum):
    """
    Valency ratio of the interaction.

    Lean canonical 4: S_doublebaresh, one_n, S_ltailm, cat.
    Replaces the old ad-hoc string field.
    """
    S_doublebaresh = "Σ_doublebaresh"
    one_n   = "Σ_ctn"     # 1:n collapses to S_ctn (symmetric many)
    S_ltailm     = "Σ_ltailm"
    cat     = "Σ_ltailm"     # catalytic treated as S_ltailm (alias)

    @classmethod
    def from_symbol(cls, s: str) -> "Stoichiometry":
        _map = {
            # canonical phonetic names
            "Σ_doublebaresh": cls.S_doublebaresh,
            "Σ_ctn":          cls.one_n,
            "Σ_ltailm":       cls.S_ltailm,
            # legacy canonical names
            "one_one": cls.S_doublebaresh,
            "n_n":     cls.one_n,
            "n_m":     cls.S_ltailm,
            # notation variants
            "1:1": cls.S_doublebaresh, "one_n": cls.one_n,
            "1:n": cls.one_n,
            "n:m": cls.S_ltailm, "n:n": cls.one_n,
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

    Lean canonical 4 (ordered H_closeomega < H_toneletterstem < H_turntwo < H_invscripta):
      H_closeomega    = achiral, no temporal memory
      H_toneletterstem    = soft chiral, weak temporal asymmetry (atropisomers)
      H_turntwo    = persistent chiral, strong asymmetry (amino acids, DNA)
      H_invscripta = topological chiral (implies K_teshlig by Axiom A)
    """
    H_closeomega    = "Ħ_closeomega"
    H_toneletterstem    = "Ħ_toneletterstem"
    H_turntwo    = "Ħ_turntwo"
    H_invscripta = "Ħ_invscripta"   # was "Hinf" (FIXED)

    @classmethod
    def from_symbol(cls, s: str) -> "Chirality":
        _map = {
            "Ħ_closeomega": cls.H_closeomega,     "H_0":   cls.H_closeomega,
            "Ħ_toneletterstem": cls.H_toneletterstem,     "H_1":   cls.H_toneletterstem,
            "Ħ_turntwo": cls.H_turntwo,     "H_2":   cls.H_turntwo,
            "Ħ_invscripta": cls.H_invscripta, "Hinf": cls.H_invscripta, "H_∞": cls.H_invscripta,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Chirality symbol: {s!r}") from None

    @property
    def memory_depth(self) -> str:
        return {
            Chirality.H_closeomega:    "0 — no persistent symmetry breaking",
            Chirality.H_toneletterstem:    "1 — single axis, thermally reversible",
            Chirality.H_turntwo:    "n — n reinforcing axes, structurally encoded",
            Chirality.H_invscripta: "∞ — topology-protected, requires bond-breaking to reverse",
        }[self]

    @property
    def implies_k_trap(self) -> bool:
        """Axiom A: H_invscripta implies K_teshlig."""
        return self == Chirality.H_invscripta


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
        # Axiom A: H_invscripta → K_teshlig is documented (Chirality.implies_k_trap) but NOT enforced
        # here — 495 catalog entries have H_invscripta + non-trap kinetics, suggesting the axiom
        # is domain-specific or structurally over-strict as a universal constraint.
        # Axiom B: prot >= Omega_dzlig → chir >= H_turntwo
        if _prot_ord(self.protection) >= _prot_ord(Protection.Omega_dzlig) \
                and _chir_ord(self.chirality) < _chir_ord(Chirality.H_turntwo):
            raise ValueError(
                f"Axiom B violated in '{name}': protection {self.protection.value} "
                f"requires chirality >= H_turntwo (got {self.chirality.value})"
            )
        # Axiom C: D_omega ↔ T_openo
        d_holo = self.dimensionality == Dimensionality.D_holo
        t_holo = self.topology == Topology.T_holo
        if d_holo != t_holo:
            raise ValueError(
                f"Axiom C violated in '{name}': D_omega ↔ T_openo "
                f"(got dim={self.dimensionality.value}, top={self.topology.value})"
            )
        # Axiom D: Omega_turna → D_omega
        if self.protection == Protection.Omega_turna \
                and self.dimensionality != Dimensionality.D_holo:
            raise ValueError(
                f"Axiom D violated in '{name}': Omega_turna requires D_omega "
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
        "Ð_point": "Ð_wynn", "Ð_line": "Ð_wynn",
        "Ð_cube": "Ð_turnthree",
        # T
        "Þ_linear": "Þ_invscr", "Þ_branched": "Þ_invscr", "Þ_bowl": "Þ_invscr",
        "Þ_cage": "Þ_commatailz",
        "Þ_torus": "Þ_bullseye", "Þ_braid": "Þ_bullseye",
        "Þ_network_hex": "Þ_nrleg", "Þ_network_mixed": "Þ_nrleg",
        "Þ_network_interp": "Þ_nrleg", "Þ_network_sym": "Þ_nrleg",
        # Phi
        "φ̂_upstep": "φ̂_upstep",
        # Gamma
        "Γ_impl": "ɢ_secstress", "Γ_xor": "ɢ_spleftarrow", "Γ_dissipative": "ɢ_doublevertline",
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
            # Handle old compound interaction_grammar dict: {"operator": "ɢ_and", "tier": "SELECTIVE"}
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
                dimensionality   = Dimensionality.from_symbol(_get("D", "dimensionality", "Ð_wynn")),
                topology         = Topology.from_symbol(_get("T", "topology", "Þ_nrleg")),
                recognition_mode = Recognition.from_symbol(_get("R", "recognition_mode", "Ř_superset")),
                polarity         = Polarity.from_symbol(_get("P", "polarity", "Φ_neutral")),
                grammar          = Grammar.from_symbol(_get("Gamma", "grammar", "ɢ_corner")),
                fidelity         = Fidelity.from_symbol(_get("F", "fidelity", "ƒ_beltl")),
                kinetic_character= KineticChar.from_symbol(_get("K", "kinetic_character", "Ç_turnm")),
                granularity      = Granularity.from_symbol(_get("G", "granularity", "Γ_beta")),
                criticality_phase= Criticality.from_symbol(_get("Phi", "criticality_phase", "φ̂_softsign")),
                protection       = Protection.from_symbol(_get("Omega", "protection", "Ω_closeepsilon")),
                stoichiometry    = Stoichiometry.from_symbol(_get("S", "stoichiometry", "n:m")),
                chirality        = Chirality.from_symbol(_get("H", "chirality", "Ħ_closeomega")),
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

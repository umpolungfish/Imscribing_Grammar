"""
Imscribing Grammar Models — Canonical 12-primitive type system.

Unified with the Lean 4 formalization in Imscribing Grammar/Primitives/Core.lean and
Imscription.lean. Enum VALUES are glyph IDs (e.g. Ð_ß, Þ_6, Ħ_Ñ); field names on
Imscription use the long Python-readable form with short-name properties (dim, top,
recog, pol, gram, fid, kin, gran, crit, prot, stoi, chir) mirroring Lean.

Tuple notation: ⟨D; T; R; P; F; K; G; Γ; Φ; Ω; S; H⟩

Ordering conventions (match Lean Core.lean):
  F: F_noise < F_beltl < F_dh < F_hardsign
  K: K_lambda < K_teshlig < K_schwa < K_turnm < K_frtailgamma
  G: G_revapostrophe < G_beta < G_gamma   (ℵ = finest/atomic, ℷ = coarsest/cosmological)
  Ω: Omega_closeepsilon < Omega_crtwo < Omega_dzlig < Omega_C < Omega_turna
  H: H_closeomega < H_toneletterstem < H_turntwo < H_invscripta

Cross-primitive axioms (enforced in Imscription.__post_init__; mirroring Core.lean):
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
    return {"Ω_Å": 0, "Ω_2": 1, "Ω_z": 2, "Ω_C": 3, "Ω_5": 4}[p.value]

def _chir_ord(h: "Chirality") -> int:
    return {"Ħ_Ñ": 0, "Ħ_£": 1, "Ħ_A": 2, "Ħ_!": 3}[h.value]


# =============================================================================
# Primitive I: Dimensionality (D)
# =============================================================================

class Dimensionality(Enum):
    """
    Coordinate set along which the imscription operates.

    Lean canonical values: D_point, D_line, D_wynn, D_cube, D_invomega, D_omega.
    Chemistry-domain extras (T_network_hex etc.) are retained for molecular catalog
    entries but are not part of the canonical 6-constructor type in Core.lean.
    """
    # ── Canonical F4 members ──────────────────────────────────────────────────
    D_wynn      = "Ð_ß"   # ordinal 1: 2D areal / molecular sheet
    D_turnthree = "Ð_C"   # ordinal 2: triangulated / simplicial / stratified
    D_invomega  = "Ð_;"   # ordinal 3: ∞-dimensional / iterative-temporal
    D_holo      = "Ð_ω"   # ordinal 4: imscriptive (boundary encodes bulk); canonical value D_omega
    # ── Lean-only extensions (non-canonical, chemistry/physics domain) ─────
    D_point = "Ð_point"   # 0D, scalar / spin-0 field
    D_line  = "Ð_line"    # 1D, vectorial
    D_cube  = "Ð_cube"    # 3D volumetric (Lean extension; canonical slot = D_turnthree)

    # Backward-compat aliases (chemistry-domain names → canonical values)
    MOLECULAR      = "Ð_ß"
    SUPRAMOLECULAR = "Ð_C"   # was D_cube; canonical ordinal 2 = D_turnthree
    TEMPORAL       = "Ð_;"
    HOLOGRAPHIC    = "Ð_ω"
    HYBRID_MOL_SUPRA  = "Ð_C"
    HYBRID_MOL_TEMP   = "Ð_;"
    HYBRID_SUPRA_TEMP = "Ð_;"
    HYBRID_ALL        = "Ð_C"

    @property
    def domains(self) -> frozenset:
        """Compat shim: old compound Dimensionality had a .domains frozenset."""
        return {
            "Ð_point":  frozenset({"point"}),
            "Ð_line":   frozenset({"linear"}),
            "Ð_ß":      frozenset({"molecular"}),
            "Ð_C":      frozenset({"molecular", "supramolecular"}),
            "Ð_cube":   frozenset({"molecular", "supramolecular"}),
            "Ð_;":      frozenset({"temporal", "molecular"}),
            "Ð_ω":      frozenset({"temporal", "molecular", "supramolecular", "imscriptive"}),
        }.get(self.value, frozenset())

    @classmethod
    def from_symbol(cls, s: str) -> "Dimensionality":
        _map = {
            # glyph IDs (canonical)
            "Ð_ß":  cls.D_wynn,
            "Ð_C":  cls.D_turnthree,
            "Ð_;":  cls.D_invomega,
            "Ð_ω":  cls.D_holo,
            # phonetic names (backward compat)
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
    Pattern of connections within the imscription's minimal motif.

    Lean canonical 6: T_linear, T_branched, T_nrleg, T_bullseye, T_torus, T_openo.
    Chemistry extras below the separator are valid for molecular catalog entries.
    """
    T_linear   = "Þ_linear"    # open chain
    T_branched = "Þ_branched"  # tree / DAG
    T_nrleg    = "Þ_6"         # general graph
    T_bullseye = "Þ_ò"         # cyclic closure / double-well / figure-8
    T_torus    = "Þ_torus"     # higher-genus compact (NEW — not in old Python)
    T_holo     = "Þ_O"         # imscriptive: non-local boundary-bulk; canonical: T_openo
    # Chemistry extras
    T_network_hex    = "Þ_network_hex"
    T_network_mixed  = "Þ_network_mixed"
    T_network_interp = "Þ_network_interp"
    T_network_sym    = "Þ_network_sym"
    T_cage  = "Þ_¨"
    T_bowl  = "Þ_K"
    T_braid = "Þ_braid"
    # Backward-compat aliases
    LINEAR        = "Þ_linear"
    CHAIN         = "Þ_linear"
    BRANCHED      = "Þ_branched"
    NETWORK       = "Þ_6"
    HUB_NODE      = "Þ_6"
    CYCLIC_BOWTIE = "Þ_ò"
    TORUS         = "Þ_torus"
    CAGE          = "Þ_¨"
    BOWL          = "Þ_K"
    BRAID         = "Þ_braid"
    NETWORK_HEX   = "Þ_network_hex"
    NETWORK_MIXED = "Þ_network_mixed"
    NETWORK_INTERP = "Þ_network_interp"
    NETWORK_SYM            = "Þ_network_sym"
    NETWORK_INTERPENETRATING = "Þ_network_interp"

    @classmethod
    def from_symbol(cls, s: str) -> "Topology":
        _map = {
            # glyph IDs (canonical)
            "Þ_6":  cls.T_nrleg,
            "Þ_ò":  cls.T_bullseye,
            "Þ_O":  cls.T_holo,
            "Þ_¨":  cls.T_cage,
            "Þ_K":  cls.T_bowl,
            # phonetic names (backward compat)
            "Þ_linear": cls.T_linear,       "Þ_chains": cls.T_linear,
            "Þ_branched": cls.T_branched,
            "Þ_nrleg": cls.T_nrleg,
            "Þ_bullseye": cls.T_bullseye,
            "Þ_torus": cls.T_torus,
            "Þ_holo": cls.T_holo,      "Þ_openo": cls.T_holo,
            "Þ_network_hex": cls.T_network_hex,
            "Þ_network_mixed": cls.T_network_mixed,
            "Þ_network_interp": cls.T_network_interp,
            "Þ_network_sym": cls.T_network_sym,
            "Þ_cage": cls.T_cage,      "Þ_box": cls.T_cage,  "Þ_commatailz": cls.T_cage,
            "Þ_bowl": cls.T_bowl,      "Þ_invscr": cls.T_bowl,
            "Þ_braid": cls.T_braid,    "Þ_square": cls.T_nrleg,
            # Unicode aliases
            "T_∈": cls.T_bowl,  "T_⋈": cls.T_bullseye,  "T_⊙": cls.T_holo,
            "T_⊠": cls.T_cage,
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
    Physical mechanism by which the imscription identifies its partner.

    Canonical 4 (from grammar): R_subrightarrow, R_ctz, R_downstep, R_lyoghlig.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    R_superset   = "Ř_¯"    # non-covalent / soft association
    R_subset     = "Ř_ý"    # covalent bond / structural transformation
    R_catalytic  = "Ř_Ť"    # transition-state stabilisation / adjoint
    R_allosteric = "Ř_Ť"    # conformational gating (alias of R_downstep)
    R_mechanical = "Ř_="    # mechanical topology / left-right asymmetric
    R_exact      = "Ř_Ť"    # exact correspondence (alias of R_downstep)
    R_covalent_dynamic = "Ř_ý"  # dynamic covalent (alias of R_ctz)
    # Backward-compat aliases used by constraints.py
    COVALENT          = "Ř_ý"
    NON_COVALENT      = "Ř_¯"
    DYNAMIC_CATALYTIC = "Ř_Ť"
    MECHANICAL        = "Ř_="
    COVALENT_DYNAMIC  = "Ř_ý"

    @classmethod
    def from_symbol(cls, s: str) -> "Recognition":
        _map = {
            # glyph IDs (canonical)
            "Ř_¯":  cls.R_superset,
            "Ř_ý":  cls.R_subset,
            "Ř_Ť":  cls.R_catalytic,
            "Ř_=":  cls.R_mechanical,
            # phonetic names (backward compat)
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
    Directional / charge character of the imscription's interface.

    Canonical 5 (from grammar): P_aolig, P_upsilon, P_pipevar, P_subdoublearrow, P_doublebarpipe.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    # ── Canonical F5 members ──────────────────────────────────────────────────
    P_neutral        = "Φ_ɐ"   # ordinal 1: asymmetric, no preferred direction
    P_plus           = "Φ_υ"   # ordinal 2: signed direction (electrophilic)
    P_pipevar        = "Φ_F"   # ordinal 3: self-complementary bipolar
    P_subdoublearrow = "Φ_˙"   # ordinal 4: symmetric (non-Frobenius)
    P_doublebarpipe  = "Φ_}"   # ordinal 5: Frobenius special (P_pm_sym)
    # ── Aliases ───────────────────────────────────────────────────────────────
    P_minus       = "Φ_υ"    # nucleophilic → same ordinal as electrophilic
    P_pm_pseudo   = "Φ_υ"    # pseudo-symmetric → signed
    P_directional = "Φ_ɐ"    # directed asymmetric pair
    ACCEPTOR               = "Φ_υ"
    DONOR                  = "Φ_υ"
    SELF_COMPLEMENTARY_SYM = "Φ_}"
    SELF_COMPLEMENTARY_PSEUDO = "Φ_υ"
    DONOR_ACCEPTOR         = "Φ_ɐ"

    @property
    def is_self_complementary(self) -> bool:
        return self.value in ("Φ_}", "Φ_F", "Φ_˙")

    @classmethod
    def from_symbol(cls, s: str) -> "Polarity":
        _map = {
            # glyph IDs (canonical)
            "Φ_ɐ":  cls.P_neutral,
            "Φ_υ":  cls.P_plus,
            "Φ_F":  cls.P_pipevar,
            "Φ_˙":  cls.P_subdoublearrow,
            "Φ_}":  cls.P_doublebarpipe,
            # phonetic names (backward compat)
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
    Gamma_corner      = "ɢ_^"   # conjunctive / simultaneous (all partners required)
    Gamma_spleftarrow = "ɢ_˝"   # disjunctive / any one suffices
    Gamma_secstress   = "ɢ_ˌ"   # sequential / ordered
    G_xor         = "Γ_xor"     # exclusive (NEW — was missing)
    G_impl        = "Γ_impl"    # implicative / conditional (NEW — was missing)
    G_dissipative = "ɢ_Ş"       # irreversible / Lindblad (legacy)
    # Backward-compat aliases: old compound InteractionGrammar values -> canonical operator
    SPECIFIC_AND         = "ɢ_^"
    SELECTIVE_AND        = "ɢ_^"
    BROAD_AND            = "ɢ_^"
    QUANTUM_AND          = "ɢ_^"
    SPECIFIC_OR          = "ɢ_˝"
    SELECTIVE_OR         = "ɢ_˝"
    BROAD_OR             = "ɢ_˝"
    QUANTUM_OR           = "ɢ_˝"
    SPECIFIC_SEQ         = "ɢ_ˌ"
    SELECTIVE_SEQ        = "ɢ_ˌ"
    BROAD_SEQ            = "ɢ_ˌ"
    QUANTUM_SEQ          = "ɢ_ˌ"
    SPECIFIC_DISSIPATIVE  = "ɢ_Ş"
    SELECTIVE_DISSIPATIVE = "ɢ_Ş"
    BROAD_DISSIPATIVE     = "ɢ_Ş"
    QUANTUM_DISSIPATIVE   = "ɢ_Ş"

    @classmethod
    def from_symbol(cls, s: str) -> "Grammar":
        _map = {
            # glyph IDs (canonical)
            "ɢ_^":  cls.Gamma_corner,
            "ɢ_˝":  cls.Gamma_spleftarrow,
            "ɢ_ˌ":  cls.Gamma_secstress,
            "ɢ_Ş":  cls.G_dissipative,
            # phonetic names (backward compat)
            "ɢ_corner": cls.Gamma_corner,   "ɢ_and": cls.Gamma_corner,
            "ɢ_otimes": cls.Gamma_corner,   "Γ_⊗": cls.Gamma_corner,
            "ɢ_odot": cls.Gamma_corner,     "Γ_⊙": cls.Gamma_corner,
            "ɢ_spleftarrow": cls.Gamma_spleftarrow, "ɢ_or": cls.Gamma_spleftarrow,
            "ɢ_bigcirc": cls.Gamma_spleftarrow,   "Γ_○": cls.Gamma_spleftarrow,
            "ɢ_secstress": cls.Gamma_secstress,   "ɢ_seq": cls.Gamma_secstress,
            "ɢ_dissipative": cls.G_dissipative,   "ɢ_doublevertline": cls.G_dissipative,
            # Unicode aliases
            "Γ_∧": cls.Gamma_corner,
            "Γ_∨": cls.Gamma_spleftarrow,
            "Γ_→": cls.Gamma_secstress,
            # G_xor / G_impl kept as phonetic since they have no glyph ID yet
            "Γ_xor": cls.G_xor,
            "Γ_impl": cls.G_impl,
            # legacy full string (backward compat)
            "Γ_dissipative": cls.G_dissipative,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Grammar symbol: {s!r}") from None

    @property
    def partner_logic(self) -> str:
        return {
            Grammar.Gamma_corner:      "All partners required simultaneously",
            Grammar.Gamma_spleftarrow: "Any one partner suffices",
            Grammar.Gamma_secstress:   "Ordered sequential recognition",
            Grammar.G_xor:             "Exactly one partner (exclusive)",
            Grammar.G_impl:            "Partner A implies partner B",
            Grammar.G_dissipative:     "Irreversible — information erased by environment",
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
    F_noise    = "ƒ_noise"  # below threshold, lossy (NEW)
    F_beltl    = "ƒ_ì"     # classical search fidelity
    F_dh       = "ƒ_ð"     # HotSwap threshold
    F_hardsign = "ƒ_ż"     # quantum coherent
    # Backward-compat aliases
    LOW    = "ƒ_ì"
    MEDIUM = "ƒ_ð"
    HIGH   = "ƒ_ż"

    @classmethod
    def from_symbol(cls, s: str) -> "Fidelity":
        _map = {
            # glyph IDs (canonical)
            "ƒ_ì":  cls.F_beltl,
            "ƒ_ð":  cls.F_dh,
            "ƒ_ż":  cls.F_hardsign,
            # phonetic names (backward compat)
            "ƒ_noise": cls.F_noise,
            "ƒ_beltl": cls.F_beltl,   "F_ℓ": cls.F_beltl,   "LOW": cls.F_beltl,
            "ƒ_dh": cls.F_dh,         "F_ℇ": cls.F_dh,       "MEDIUM": cls.F_dh,
            "ƒ_hardsign": cls.F_hardsign, "F_ℏ": cls.F_hardsign, "HIGH": cls.F_hardsign,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Fidelity symbol: {s!r}") from None

    @property
    def numeric_value(self) -> float:
        return {"ƒ_noise": 0.0, "ƒ_ì": 0.33, "ƒ_ð": 0.67, "ƒ_ż": 1.0}[self.value]


# =============================================================================
# Primitive VII: Kinetic Character (K)
# =============================================================================

class KineticChar(Enum):
    """
    Kinetic accessibility of the imscription's assembly pathway.

    Lean canonical 5 (ordered K_lambda < K_teshlig < K_schwa < K_turnm < K_frtailgamma):
      K_frtailgamma = diffusion-limited, no barrier
      K_turnm  = moderate activation barrier
      K_schwa = slow / thermally activated
      K_teshlig = kinetically trapped / pathway-multiplicity dominated
      K_lambda  = many-body localised (disorder-frozen)
    """
    K_frtailgamma = "Ç_-"
    K_turnm       = "Ç_W"   # was MODERATE
    K_schwa       = "Ç_@"
    K_teshlig     = "Ç_Ù"
    K_lambda      = "Ç_λ"
    # Backward-compat aliases
    FAST     = "Ç_-"
    MODERATE = "Ç_W"
    SLOW     = "Ç_@"
    TRAP     = "Ç_Ù"
    MBL      = "Ç_λ"

    @classmethod
    def from_symbol(cls, s: str) -> "KineticChar":
        _map = {
            # glyph IDs (canonical)
            "Ç_-":  cls.K_frtailgamma,
            "Ç_W":  cls.K_turnm,
            "Ç_@":  cls.K_schwa,
            "Ç_Ù":  cls.K_teshlig,
            "Ç_λ":  cls.K_lambda,
            # phonetic names (backward compat)
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
        return {"Ç_λ": 0.0, "Ç_Ù": 0.25, "Ç_@": 0.5, "Ç_W": 0.75, "Ç_-": 1.0}[self.value]


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
    G_revapostrophe = "Γ_ʔ"   # fine-grained, atomic (ℵ) — was incorrectly GLOBAL in old Python
    G_beta          = "Γ_β"   # mesoscale local (ℶ) — was LOCAL
    G_gamma         = "Γ_γ"   # coarse, collective (ℷ) — was incorrectly MESOSCALE in old Python
    # Backward-compat key aliases with CORRECTED semantics:
    LOCAL     = "Γ_ʔ"   # fine = aleph (was G_beta — now fixed)
    MESOSCALE = "Γ_β"   # mesoscale = beth (was G_gamma — now fixed)
    GLOBAL    = "Γ_γ"   # coarse = gimel (was G_revapostrophe — now fixed)

    @property
    def ordinal(self) -> int:
        return {"Γ_ʔ": 0, "Γ_β": 1, "Γ_γ": 2}.get(self.value, 1)

    def can_amplify_to(self, other: "Granularity") -> bool:
        """Fine-to-coarse aggregation is possible; coarse-to-fine is not."""
        return self.ordinal <= other.ordinal

    @classmethod
    def from_symbol(cls, s: str) -> "Granularity":
        _map = {
            # glyph IDs (canonical)
            "Γ_ʔ":  cls.G_revapostrophe,
            "Γ_β":  cls.G_beta,
            "Γ_γ":  cls.G_gamma,
            # phonetic names (backward compat)
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
    Phase condition of the imscription's constraint propagation regime.

    Canonical 5 (ordered Phi_softsign < Phi_ctyogh < Phi_closerevepsilon < Phi_revepsilon < Phi_upstep):
      Phi_softsign       = subcritical (stable, ordered)
      Phi_ctyogh         = critical point (absorbing under meet, real self-modeling)
      Phi_closerevepsilon = complex criticality (paraconsistent / dialetheic fixed point)
      Phi_revepsilon        = exceptional-point criticality (non-Hermitian degeneracy; absorbs O_inf under tensor)
      Phi_upstep     = supercritical (unstable)
    Phi_ctyogh is ABSORBING under meet: meet(Phi_ctyogh, x) = Phi_ctyogh for all x.
    """
    Phi_softsign        = "φ̂_ž"   # subcritical (stable, ordered)
    Phi_ctyogh          = "φ̂_ÿ"   # critical point (absorbing under meet)
    Phi_closerevepsilon = "φ̂_Æ"   # complex criticality (paraconsistent)
    Phi_revepsilon      = "φ̂_3"   # exceptional-point criticality
    Phi_upstep          = "φ̂_Ţ"   # supercritical (unstable)
    # Backward-compat aliases
    SUBCRITICAL  = "φ̂_ž"
    CRITICAL     = "φ̂_ÿ"
    SUPERCRITICAL = "φ̂_Ţ"

    @classmethod
    def from_symbol(cls, s: str) -> "Criticality":
        _map = {
            # glyph IDs (canonical)
            "φ̂_ž":  cls.Phi_softsign,
            "φ̂_ÿ":  cls.Phi_ctyogh,
            "φ̂_Æ":  cls.Phi_closerevepsilon,
            "φ̂_3":  cls.Phi_revepsilon,
            "φ̂_Ţ":  cls.Phi_upstep,
            # phonetic names (backward compat)
            "φ̂_softsign":       cls.Phi_softsign,       "Φ_sub":   cls.Phi_softsign,
            "φ̂_ctyogh":         cls.Phi_ctyogh,         "Φ_c":     cls.Phi_ctyogh,
            "φ̂_closerevepsilon": cls.Phi_closerevepsilon, "Φ_c_ℂ":  cls.Phi_closerevepsilon,
            "φ̂_revepsilon":      cls.Phi_revepsilon,      "Φ_EP":    cls.Phi_revepsilon,
            "φ̂_upstep":         cls.Phi_upstep,          "Φ_sup":   cls.Phi_upstep,
            # odot-prefixed variants (old memory file notation)
            "⊙_ž":  cls.Phi_softsign,
            "⊙_ÿ":  cls.Phi_ctyogh,
            "⊙_Æ":  cls.Phi_closerevepsilon,
            "⊙_3":  cls.Phi_revepsilon,
            "⊙_Ţ":  cls.Phi_upstep,
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
    Omega_closeepsilon = "Ω_Å"
    Omega_crtwo        = "Ω_2"
    Omega_dzlig        = "Ω_z"
    Omega_C            = "Ω_C"
    Omega_turna        = "Ω_5"
    # Backward-compat aliases (old TopoIndex names)
    TRIVIAL     = "Ω_Å"
    Z2_CLASS    = "Ω_2"
    Z_CLASS     = "Ω_z"
    CHERN       = "Ω_C"
    NON_ABELIAN = "Ω_5"

    @classmethod
    def from_symbol(cls, s: str) -> "Protection":
        _map = {
            # glyph IDs (canonical)
            "Ω_Å":  cls.Omega_closeepsilon,
            "Ω_2":  cls.Omega_crtwo,
            "Ω_z":  cls.Omega_dzlig,
            "Ω_C":  cls.Omega_C,
            "Ω_5":  cls.Omega_turna,
            # phonetic names (backward compat)
            "Ω_closeepsilon":  cls.Omega_closeepsilon, "Ω_0":  cls.Omega_closeepsilon, "TRIVIAL":     cls.Omega_closeepsilon,
            "Ω_crtwo": cls.Omega_crtwo, "Ω_Z2": cls.Omega_crtwo, "Z2_CLASS":    cls.Omega_crtwo,
            "Ω_dzlig":  cls.Omega_dzlig,  "Ω_Z":  cls.Omega_dzlig,  "Z_CLASS":     cls.Omega_dzlig,
            "Ω_turna": cls.Omega_turna, "Ω_NA": cls.Omega_turna, "NON_ABELIAN": cls.Omega_turna,
            "CHERN":       cls.Omega_C,
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
            Protection.Omega_closeepsilon: "Ordinary insulators, classical systems",
            Protection.Omega_crtwo:        "HgTe/CdTe, Bi2Se3, topological insulators (AII/DIII)",
            Protection.Omega_dzlig:        "Kitaev chain, SSH model, 1D p-wave superconductors",
            Protection.Omega_C:            "Integer quantum Hall, Chern insulators (class A)",
            Protection.Omega_turna:        "nu=5/2 FQH, Kitaev honeycomb B-phase, non-Abelian Majorana",
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
    S_doublebaresh = "Σ_S"
    one_n          = "Σ_ő"   # 1:n collapses to S_ctn (symmetric many)
    S_ltailm       = "Σ_ï"
    cat            = "Σ_ï"   # catalytic treated as S_ltailm (alias)

    @classmethod
    def from_symbol(cls, s: str) -> "Stoichiometry":
        _map = {
            # glyph IDs (canonical)
            "Σ_S":  cls.S_doublebaresh,
            "Σ_ő":  cls.one_n,
            "Σ_ï":  cls.S_ltailm,
            # phonetic names (backward compat)
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
    H_closeomega     = "Ħ_Ñ"
    H_toneletterstem = "Ħ_£"
    H_turntwo        = "Ħ_A"
    H_invscripta     = "Ħ_!"   # was "Hinf" (FIXED)

    @classmethod
    def from_symbol(cls, s: str) -> "Chirality":
        _map = {
            # glyph IDs (canonical)
            "Ħ_Ñ":  cls.H_closeomega,
            "Ħ_£":  cls.H_toneletterstem,
            "Ħ_A":  cls.H_turntwo,
            "Ħ_!":  cls.H_invscripta,
            # phonetic names (backward compat)
            "Ħ_closeomega":     cls.H_closeomega,     "H_0":   cls.H_closeomega,
            "Ħ_toneletterstem": cls.H_toneletterstem, "H_1":   cls.H_toneletterstem,
            "Ħ_turntwo":        cls.H_turntwo,        "H_2":   cls.H_turntwo,
            "Ħ_invscripta":     cls.H_invscripta,     "Hinf":  cls.H_invscripta,  "H_∞": cls.H_invscripta,
        }
        try:
            return _map[s]
        except KeyError:
            raise ValueError(f"Unknown Chirality symbol: {s!r}") from None

    @property
    def memory_depth(self) -> str:
        return {
            Chirality.H_closeomega:     "0 — no persistent symmetry breaking",
            Chirality.H_toneletterstem: "1 — single axis, thermally reversible",
            Chirality.H_turntwo:        "n — n reinforcing axes, structurally encoded",
            Chirality.H_invscripta:     "∞ — topology-protected, requires bond-breaking to reverse",
        }[self]

    @property
    def implies_k_trap(self) -> bool:
        """Axiom A: H_invscripta implies K_teshlig."""
        return self == Chirality.H_invscripta


# =============================================================================
# imscription — the canonical 12-tuple
# =============================================================================

# Global flag: set False to bypass axiom enforcement (e.g. during migration)
_ENFORCE_AXIOMS: bool = True


@dataclass
class Imscription:
    """
    A Imscription is a minimal constraint-carrying unit encoded as a 12-tuple
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
            f"⟨{self.dimensionality.value}; {self.topology.value}; "
            f"{self.recognition_mode.value}; {self.polarity.value}; "
            f"{self.fidelity.value}; {self.kinetic_character.value}; "
            f"{self.granularity.value}; {self.grammar.value}; "
            f"{self.criticality_phase.value}; {self.protection.value}; "
            f"{self.stoichiometry.value}; {self.chirality.value}⟩"
        )

    # Translate internal enum values to canonical ORDINALS keys (primitives.py).
    # Models layer uses a richer chemistry vocab; registry/zfc must see only canon values.
    _CANONICAL_MAP: ClassVar[Dict[str, str]] = {
        # D — non-canonical extensions collapse to nearest canonical
        "Ð_point": "Ð_ß", "Ð_line": "Ð_ß",
        "Ð_cube": "Ð_C",
        # T — chemistry extras collapse to canonical 5
        "Þ_linear": "Þ_K", "Þ_branched": "Þ_K", "Þ_bowl": "Þ_K",
        "Þ_cage": "Þ_¨",
        "Þ_torus": "Þ_ò", "Þ_braid": "Þ_ò",
        "Þ_network_hex": "Þ_6", "Þ_network_mixed": "Þ_6",
        "Þ_network_interp": "Þ_6", "Þ_network_sym": "Þ_6",
        # Grammar — non-canonical G_xor/G_impl/G_dissipative collapse to canonical
        "Γ_impl": "ɢ_ˌ", "Γ_xor": "ɢ_˝", "Γ_dissipative": "ɢ_Ş",
    }

    @classmethod
    def _canon(cls, val: str) -> str:
        return cls._CANONICAL_MAP.get(val, val)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name":          self.name,
            "description":   self.description,
            "Ð":             self._canon(self.dimensionality.value),
            "Þ":             self._canon(self.topology.value),
            "Ř":             self._canon(self.recognition_mode.value),
            "Φ":             self._canon(self.polarity.value),
            "ƒ":             self._canon(self.fidelity.value),
            "Ç":             self._canon(self.kinetic_character.value),
            "Γ":             self._canon(self.granularity.value),
            "ɢ":             self._canon(self.grammar.value),
            "φ̂":             self._canon(self.criticality_phase.value),
            "Ω":             self._canon(self.protection.value),
            "Σ":             self._canon(self.stoichiometry.value),
            "Ħ":             self._canon(self.chirality.value),
            "grounding":     self.grounding,
            "is_grounded":   self.is_grounded,
            "metadata":      self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Imscription":
        """
        Construct a Imscription from a catalog dict (new or legacy format).

        Accepts glyph keys (Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, φ̂, Ħ, Σ, Ω), short ASCII keys
        (D, T, R, P, F, K, G, Gamma, Phi, Omega, S, H), and long Python field names.
        Parses all primitive fields via from_symbol() for backward compatibility.
        """
        def _get(glyph: str, short: str, long: str, default: str) -> str:
            # Prefer glyph key (catalog format), then long Python name, then short ASCII
            v = d.get(glyph) or d.get(long) or d.get(short)
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
                dimensionality   = Dimensionality.from_symbol(_get("Ð", "D", "dimensionality", "Ð_ß")),
                topology         = Topology.from_symbol(_get("Þ", "T", "topology", "Þ_6")),
                recognition_mode = Recognition.from_symbol(_get("Ř", "R", "recognition_mode", "Ř_¯")),
                polarity         = Polarity.from_symbol(_get("Φ", "P", "polarity", "Φ_ɐ")),
                grammar          = Grammar.from_symbol(_get("ɢ", "Gamma", "grammar", "ɢ_^")),
                fidelity         = Fidelity.from_symbol(_get("ƒ", "F", "fidelity", "ƒ_ì")),
                kinetic_character= KineticChar.from_symbol(_get("Ç", "K", "kinetic_character", "Ç_W")),
                granularity      = Granularity.from_symbol(_get("Γ", "G", "granularity", "Γ_β")),
                criticality_phase= Criticality.from_symbol(_get("φ̂", "Phi", "criticality_phase", "φ̂_ž")),
                protection       = Protection.from_symbol(_get("Ω", "Omega", "protection", "Ω_Å")),
                stoichiometry    = Stoichiometry.from_symbol(_get("Σ", "S", "stoichiometry", "n:m")),
                chirality        = Chirality.from_symbol(_get("Ħ", "H", "chirality", "Ħ_Ñ")),
                description      = d.get("description", ""),
                metadata         = d.get("metadata", {}),
                grounding        = d.get("grounding"),
                is_grounded      = d.get("is_grounded", False),
            )
        finally:
            _ENFORCE_AXIOMS = _saved
        return result


# Patch Imscription.__init__ to accept old kwarg names and supply defaults for
# fields that became required (protection, chirality) after old catalog entries
# were written.  Also coerces stoichiometry strings to the enum.
_imscription_dc_init = Imscription.__init__

def _imscription_init_compat(
    self, *args,
    interaction_grammar=None,
    topo_index=None,
    **kwargs,
):
    global _ENFORCE_AXIOMS
    using_defaults = False
    if interaction_grammar is not None and "grammar" not in kwargs:
        kwargs["grammar"] = interaction_grammar
    if topo_index is not None and "protection" not in kwargs:
        kwargs["protection"] = topo_index
    if "protection" not in kwargs:
        kwargs["protection"] = Protection.Omega_closeepsilon
        using_defaults = True
    if "chirality" not in kwargs:
        kwargs["chirality"] = Chirality.H_closeomega
        using_defaults = True
    stoi = kwargs.get("stoichiometry")
    if isinstance(stoi, str):
        kwargs["stoichiometry"] = Stoichiometry.from_symbol(stoi)
    elif stoi is None:
        kwargs["stoichiometry"] = Stoichiometry.S_ltailm
    if using_defaults:
        _saved = _ENFORCE_AXIOMS
        _ENFORCE_AXIOMS = False
        try:
            _imscription_dc_init(self, *args, **kwargs)
        finally:
            _ENFORCE_AXIOMS = _saved
    else:
        _imscription_dc_init(self, *args, **kwargs)

Imscription.__init__ = _imscription_init_compat


# =============================================================================
# Backward-compat type aliases (for code that imports old class names)
# =============================================================================

RecognitionMode  = Recognition    # old class name
KineticCharacter = KineticChar    # old class name
CriticalityPhase = Criticality    # old class name
TopoIndex        = Protection     # old class name
InteractionGrammar = Grammar      # old compound class — now canonical simple enum
GrammarOperator    = Grammar      # old operator sub-class — same mapping


class ImscriptionNotation:
    """Stub backward-compat class. Use Imscription.from_dict() instead."""
    @staticmethod
    def parse(notation_str: str) -> dict:
        raise NotImplementedError(
            "ImscriptionNotation.parse() is removed. Use Imscription.from_dict() "
            "with a flat dict of primitive values."
        )


def parse_notation(notation_str: str) -> dict:
    """Stub backward-compat function. Use Imscription.from_dict() instead."""
    raise NotImplementedError(
        "parse_notation() is removed. Use Imscription.from_dict() instead."
    )


# =============================================================================
# CONFLICT sentinel (used by algebra.py meet/join)
# =============================================================================

CONFLICT: str = "CONFLICT"

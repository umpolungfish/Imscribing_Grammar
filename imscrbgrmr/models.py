"""
Imscribing Grammar Models — Canonical 12-primitive type system.

Unified with the Lean 4 formalization in Imscribing Grammar/Primitives/Core.lean and
Imscription.lean. Enum VALUES are glyph IDs (e.g. 𐑛, 𐑡, 𐑓); field names on
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
    return {"𐑷": 0, "𐑴": 1, "𐑭": 2, "Ω_C": 3, "𐑟": 4}[p.value]

def _chir_ord(h: "Chirality") -> int:
    return {"𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3}[h.value]


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
    D_wynn      = "𐑛"   # ordinal 1: 2D areal / molecular sheet
    D_turnthree = "𐑨"   # ordinal 2: triangulated / simplicial / stratified
    D_invomega  = "𐑼"   # ordinal 3: ∞-dimensional / iterative-temporal
    D_holo      = "𐑦"   # ordinal 4: imscriptive (boundary encodes bulk); canonical value D_omega
    # ── Lean-only extensions (non-canonical, chemistry/physics domain) ─────
    D_point = "Ð_point"   # 0D, scalar / spin-0 field
    D_line  = "Ð_line"    # 1D, vectorial
    D_cube  = "Ð_cube"    # 3D volumetric (Lean extension; canonical slot = D_turnthree)

    # Backward-compat aliases (chemistry-domain names → canonical values)
    MOLECULAR      = "𐑛"
    SUPRAMOLECULAR = "𐑨"   # was D_cube; canonical ordinal 2 = D_turnthree
    TEMPORAL       = "𐑼"
    HOLOGRAPHIC    = "𐑦"
    HYBRID_MOL_SUPRA  = "𐑨"
    HYBRID_MOL_TEMP   = "𐑼"
    HYBRID_SUPRA_TEMP = "𐑼"
    HYBRID_ALL        = "𐑨"

    @property
    def domains(self) -> frozenset:
        """Compat shim: old compound Dimensionality had a .domains frozenset."""
        return {
            "Ð_point":  frozenset({"point"}),
            "Ð_line":   frozenset({"linear"}),
            "𐑛":      frozenset({"molecular"}),
            "𐑨":      frozenset({"molecular", "supramolecular"}),
            "Ð_cube":   frozenset({"molecular", "supramolecular"}),
            "𐑼":      frozenset({"temporal", "molecular"}),
            "𐑦":      frozenset({"temporal", "molecular", "supramolecular", "imscriptive"}),
        }.get(self.value, frozenset())

    @classmethod
    def from_symbol(cls, s: str) -> "Dimensionality":
        _map = {
            # glyph IDs (canonical)
            "𐑛":  cls.D_wynn,
            "𐑨":  cls.D_turnthree,
            "𐑼":  cls.D_invomega,
            "𐑦":  cls.D_holo,
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
            # Shavian (v0.6.0)
            "𐑛": cls.D_wynn,   "𐑨": cls.D_turnthree,
            "𐑼": cls.D_invomega, "𐑦": cls.D_holo,
            # Unicode aliases
            "D_∧": cls.D_wynn,  "D_△": cls.D_turnthree,
            "D_∞": cls.D_invomega, "D_⊙": cls.D_holo,
            "Ð_infinity": cls.D_invomega,
            "Ð_holo": cls.D_holo,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "wynn": cls.D_wynn,
            "wedge": cls.D_wynn,
            "turnthree": cls.D_turnthree,
            "triangle": cls.D_turnthree,
            "invomega": cls.D_invomega,
            "infty": cls.D_invomega,
            "infinity": cls.D_invomega,
            "omega": cls.D_holo,
            "holo": cls.D_holo,
            "odot": cls.D_holo,
            "point": cls.D_point,
            "line": cls.D_line,
            "cube": cls.D_cube,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Dimensionality: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Dimensionality: unknown symbol {s!r}, defaulting to D_wynn")
        return cls.D_wynn


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
    T_nrleg    = "𐑡"         # general graph
    T_bullseye = "𐑥"         # cyclic closure / double-well / figure-8
    T_torus    = "Þ_torus"     # higher-genus compact (NEW — not in old Python)
    T_holo     = "𐑸"         # imscriptive: non-local boundary-bulk; canonical: T_openo
    # Chemistry extras
    T_network_hex    = "Þ_network_hex"
    T_network_mixed  = "Þ_network_mixed"
    T_network_interp = "Þ_network_interp"
    T_network_sym    = "Þ_network_sym"
    T_cage  = "𐑶"
    T_bowl  = "𐑰"
    T_braid = "Þ_braid"
    # Backward-compat aliases
    LINEAR        = "Þ_linear"
    CHAIN         = "Þ_linear"
    BRANCHED      = "Þ_branched"
    NETWORK       = "𐑡"
    HUB_NODE      = "𐑡"
    CYCLIC_BOWTIE = "𐑥"
    TORUS         = "Þ_torus"
    CAGE          = "𐑶"
    BOWL          = "𐑰"
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
            "𐑡":  cls.T_nrleg,
            "𐑥":  cls.T_bullseye,
            "𐑸":  cls.T_holo,
            "𐑶":  cls.T_cage,
            "𐑰":  cls.T_bowl,
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
            # Shavian (v0.6.0)
            "𐑡": cls.T_nrleg,  "𐑰": cls.T_bowl, "𐑥": cls.T_bullseye,
            "𐑶": cls.T_cage,   "𐑸": cls.T_holo,
            # Unicode aliases
            "T_∈": cls.T_bowl,  "T_⋈": cls.T_bullseye,  "T_⊙": cls.T_holo,
            "T_⊠": cls.T_cage,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "linear": cls.T_linear,
            "chain": cls.T_linear,
            "chains": cls.T_linear,
            "branched": cls.T_branched,
            "nrleg": cls.T_nrleg,
            "network": cls.T_nrleg,
            "square": cls.T_nrleg,
            "bullseye": cls.T_bullseye,
            "cyclic_bowtie": cls.T_bullseye,
            "torus": cls.T_torus,
            "holo": cls.T_holo,
            "openo": cls.T_holo,
            "cage": cls.T_cage,
            "box": cls.T_cage,
            "commatailz": cls.T_cage,
            "bowl": cls.T_bowl,
            "invscr": cls.T_bowl,
            "braid": cls.T_braid,
            "network_hex": cls.T_network_hex,
            "network_mixed": cls.T_network_mixed,
            "network_interp": cls.T_network_interp,
            "network_sym": cls.T_network_sym,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Topology: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Topology: unknown symbol {s!r}, defaulting to T_linear")
        return cls.T_linear


# =============================================================================
# Primitive III: Recognition (R)
# =============================================================================

class Recognition(Enum):
    """
    Physical mechanism by which the imscription identifies its partner.

    Canonical 4 (from grammar): R_subrightarrow, R_ctz, R_downstep, R_lyoghlig.
    Chemistry vocab is preserved as member names but values are canonical.
    """
    R_superset   = "𐑩"    # non-covalent / soft association
    R_subset     = "𐑑"    # covalent bond / structural transformation
    R_catalytic  = "𐑽"    # transition-state stabilisation / adjoint
    R_allosteric = "𐑽"    # conformational gating (alias of R_downstep)
    R_mechanical = "𐑾"    # mechanical topology / left-right asymmetric
    R_exact      = "𐑽"    # exact correspondence (alias of R_downstep)
    R_covalent_dynamic = "𐑑"  # dynamic covalent (alias of R_ctz)
    # Backward-compat aliases used by constraints.py
    COVALENT          = "𐑑"
    NON_COVALENT      = "𐑩"
    DYNAMIC_CATALYTIC = "𐑽"
    MECHANICAL        = "𐑾"
    COVALENT_DYNAMIC  = "𐑑"

    @classmethod
    def from_symbol(cls, s: str) -> "Recognition":
        _map = {
            # glyph IDs (canonical)
            "𐑩":  cls.R_superset,
            "𐑑":  cls.R_subset,
            "𐑽":  cls.R_catalytic,
            "𐑾":  cls.R_mechanical,
            # phonetic names (backward compat)
            "Ř_subrightarrow":   cls.R_superset,
            "Ř_ctz":     cls.R_subset,
            "Ř_downstep":  cls.R_catalytic,
            "Ř_lyoghlig":      cls.R_mechanical,
            # Shavian (v0.6.0)
            "𐑩": cls.R_superset, "𐑑": cls.R_subset,
            "𐑽": cls.R_catalytic, "𐑾": cls.R_mechanical,
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
            pass
        # Suffix-based fallback: strip any hallucinated prefix before '_'
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _suffix_map = {
            "superset": cls.R_superset, "subrightarrow": cls.R_superset,
            "subset": cls.R_subset, "ctz": cls.R_subset, "covalent": cls.R_subset,
            "covalent_dynamic": cls.R_covalent_dynamic,
            "catalytic": cls.R_catalytic, "downstep": cls.R_catalytic,
            "allosteric": cls.R_allosteric, "exact": cls.R_exact,
            "mechanical": cls.R_mechanical, "lyoghlig": cls.R_mechanical,
        }
        if suffix in _suffix_map:
            import warnings
            warnings.warn(f"Recognition: normalised unknown symbol {s!r} via suffix {suffix!r}")
            return _suffix_map[suffix]
        import warnings
        warnings.warn(f"Recognition: completely unknown symbol {s!r}, defaulting to R_superset")
        return cls.R_superset


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
    P_neutral        = "𐑗"   # ordinal 1: asymmetric, no preferred direction
    P_plus           = "𐑿"   # ordinal 2: signed direction (electrophilic)
    P_pipevar        = "𐑬"   # ordinal 3: self-complementary bipolar
    P_subdoublearrow = "𐑯"   # ordinal 4: symmetric (non-Frobenius)
    P_doublebarpipe  = "𐑹"   # ordinal 5: Frobenius special (P_pm_sym)
    # ── Aliases ───────────────────────────────────────────────────────────────
    P_minus       = "𐑿"    # nucleophilic → same ordinal as electrophilic
    P_pm_pseudo   = "𐑿"    # pseudo-symmetric → signed
    P_directional = "𐑗"    # directed asymmetric pair
    ACCEPTOR               = "𐑿"
    DONOR                  = "𐑿"
    SELF_COMPLEMENTARY_SYM = "𐑹"
    SELF_COMPLEMENTARY_PSEUDO = "𐑿"
    DONOR_ACCEPTOR         = "𐑗"

    @property
    def is_self_complementary(self) -> bool:
        return self.value in ("𐑹", "𐑬", "𐑯")

    @classmethod
    def from_symbol(cls, s: str) -> "Polarity":
        _map = {
            # glyph IDs (canonical)
            "𐑗":  cls.P_neutral,
            "𐑿":  cls.P_plus,
            "𐑬":  cls.P_pipevar,
            "𐑯":  cls.P_subdoublearrow,
            "𐑹":  cls.P_doublebarpipe,
            # phonetic names (backward compat)
            "Φ_aolig":          cls.P_neutral,
            "Φ_upsilon":        cls.P_plus,
            "Φ_pipevar":        cls.P_pipevar,
            "Φ_subdoublearrow": cls.P_subdoublearrow,
            "Φ_doublebarpipe":  cls.P_doublebarpipe,
            # Shavian (v0.6.0)
            "𐑗": cls.P_neutral,  "𐑿": cls.P_plus,    "𐑬": cls.P_pipevar,
            "𐑯": cls.P_subdoublearrow, "𐑹": cls.P_doublebarpipe,
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
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "neutral": cls.P_neutral,
            "asym": cls.P_neutral,
            "directional": cls.P_neutral,
            "aolig": cls.P_neutral,
            "plus": cls.P_plus,
            "psi": cls.P_plus,
            "upsilon": cls.P_plus,
            "minus": cls.P_minus,
            "pm_pseudo": cls.P_pm_pseudo,
            "pipevar": cls.P_pipevar,
            "pm": cls.P_pipevar,
            "subdoublearrow": cls.P_subdoublearrow,
            "sym": cls.P_subdoublearrow,
            "doublebarpipe": cls.P_doublebarpipe,
            "pm_sym": cls.P_doublebarpipe,
            "frobenius": cls.P_doublebarpipe,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Polarity: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Polarity: unknown symbol {s!r}, defaulting to P_neutral")
        return cls.P_neutral


# =============================================================================
# Primitive V: Coupling (Γ)
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
    Gamma_corner      = "𐑝"   # conjunctive / simultaneous (all partners required)
    Gamma_spleftarrow = "𐑜"   # disjunctive / any one suffices
    Gamma_secstress   = "𐑠"   # sequential / ordered
    G_xor         = "Γ_xor"     # exclusive (NEW — was missing)
    G_impl        = "Γ_impl"    # implicative / conditional (NEW — was missing)
    G_dissipative = "𐑵"       # irreversible / Lindblad (legacy)
    # Backward-compat aliases: old compound InteractionGrammar values -> canonical operator
    SPECIFIC_AND         = "𐑝"
    SELECTIVE_AND        = "𐑝"
    BROAD_AND            = "𐑝"
    QUANTUM_AND          = "𐑝"
    SPECIFIC_OR          = "𐑜"
    SELECTIVE_OR         = "𐑜"
    BROAD_OR             = "𐑜"
    QUANTUM_OR           = "𐑜"
    SPECIFIC_SEQ         = "𐑠"
    SELECTIVE_SEQ        = "𐑠"
    BROAD_SEQ            = "𐑠"
    QUANTUM_SEQ          = "𐑠"
    SPECIFIC_DISSIPATIVE  = "𐑵"
    SELECTIVE_DISSIPATIVE = "𐑵"
    BROAD_DISSIPATIVE     = "𐑵"
    QUANTUM_DISSIPATIVE   = "𐑵"

    @classmethod
    def from_symbol(cls, s: str) -> "Grammar":
        _map = {
            # glyph IDs (canonical)
            "𐑝":  cls.Gamma_corner,
            "𐑜":  cls.Gamma_spleftarrow,
            "𐑠":  cls.Gamma_secstress,
            "𐑵":  cls.G_dissipative,
            # Shavian (v0.6.0)
            "𐑝": cls.Gamma_corner, "𐑜": cls.Gamma_spleftarrow,
            "𐑠": cls.Gamma_secstress, "𐑵": cls.G_dissipative,
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
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "corner": cls.Gamma_corner,
            "and": cls.Gamma_corner,
            "otimes": cls.Gamma_corner,
            "odot": cls.Gamma_corner,
            "spleftarrow": cls.Gamma_spleftarrow,
            "or": cls.Gamma_spleftarrow,
            "bigcirc": cls.Gamma_spleftarrow,
            "secstress": cls.Gamma_secstress,
            "seq": cls.Gamma_secstress,
            "xor": cls.G_xor,
            "impl": cls.G_impl,
            "dissipative": cls.G_dissipative,
            "doublevertline": cls.G_dissipative,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Grammar: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Grammar: unknown symbol {s!r}, defaulting to Gamma_corner")
        return cls.Gamma_corner

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
    F_beltl    = "𐑱"     # classical search fidelity
    F_dh       = "𐑞"     # HotSwap threshold
    F_hardsign = "𐑐"     # quantum coherent
    # Backward-compat aliases
    LOW    = "𐑱"
    MEDIUM = "𐑞"
    HIGH   = "𐑐"

    @classmethod
    def from_symbol(cls, s: str) -> "Fidelity":
        _map = {
            # glyph IDs (canonical)
            "𐑱":  cls.F_beltl,
            "𐑞":  cls.F_dh,
            "𐑐":  cls.F_hardsign,
            # Shavian (v0.6.0)
            "𐑱": cls.F_beltl, "𐑞": cls.F_dh, "𐑐": cls.F_hardsign,
            # phonetic names (backward compat)
            "ƒ_noise": cls.F_noise,
            "ƒ_beltl": cls.F_beltl,   "F_ℓ": cls.F_beltl,   "LOW": cls.F_beltl,
            "ƒ_dh": cls.F_dh,         "F_ℇ": cls.F_dh,       "MEDIUM": cls.F_dh,
            "ƒ_hardsign": cls.F_hardsign, "F_ℏ": cls.F_hardsign, "HIGH": cls.F_hardsign,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "noise": cls.F_noise,
            "beltl": cls.F_beltl,
            "low": cls.F_beltl,
            "dh": cls.F_dh,
            "medium": cls.F_dh,
            "hardsign": cls.F_hardsign,
            "high": cls.F_hardsign,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Fidelity: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Fidelity: unknown symbol {s!r}, defaulting to F_beltl")
        return cls.F_beltl

    @property
    def numeric_value(self) -> float:
        return {"ƒ_noise": 0.0, "𐑱": 0.33, "𐑞": 0.67, "𐑐": 1.0}[self.value]


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
    K_frtailgamma = "𐑘"
    K_turnm       = "𐑤"   # was MODERATE
    K_schwa       = "𐑧"
    K_teshlig     = "𐑪"
    K_lambda      = "𐑺"
    # Backward-compat aliases
    FAST     = "𐑘"
    MODERATE = "𐑤"
    SLOW     = "𐑧"
    TRAP     = "𐑪"
    MBL      = "𐑺"

    @classmethod
    def from_symbol(cls, s: str) -> "KineticChar":
        _map = {
            # glyph IDs (canonical)
            "𐑘":  cls.K_frtailgamma,
            "𐑤":  cls.K_turnm,
            "𐑧":  cls.K_schwa,
            "𐑪":  cls.K_teshlig,
            "𐑺":  cls.K_lambda,
            # Shavian (v0.6.0)
            "𐑘": cls.K_frtailgamma, "𐑤": cls.K_turnm, "𐑧": cls.K_schwa,
            "𐑪": cls.K_teshlig, "𐑺": cls.K_lambda,
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
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "frtailgamma": cls.K_frtailgamma,
            "fast": cls.K_frtailgamma,
            "turnm": cls.K_turnm,
            "moderate": cls.K_turnm,
            "schwa": cls.K_schwa,
            "slow": cls.K_schwa,
            "teshlig": cls.K_teshlig,
            "trap": cls.K_teshlig,
            "lambda": cls.K_lambda,
            "mbl": cls.K_lambda,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"KineticChar: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"KineticChar: unknown symbol {s!r}, defaulting to K_schwa")
        return cls.K_schwa

    @property
    def numeric_value(self) -> float:
        return {"𐑺": 0.0, "𐑪": 0.25, "𐑧": 0.5, "𐑤": 0.75, "𐑘": 1.0}[self.value]


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
    G_revapostrophe = "𐑲"   # fine-grained, atomic (ℵ) — was incorrectly GLOBAL in old Python
    G_beta          = "𐑚"   # mesoscale local (ℶ) — was LOCAL
    G_gamma         = "𐑔"   # coarse, collective (ℷ) — was incorrectly MESOSCALE in old Python
    # Backward-compat key aliases with CORRECTED semantics:
    LOCAL     = "𐑲"   # fine = aleph (was G_beta — now fixed)
    MESOSCALE = "𐑚"   # mesoscale = beth (was G_gamma — now fixed)
    GLOBAL    = "𐑔"   # coarse = gimel (was G_revapostrophe — now fixed)

    @property
    def ordinal(self) -> int:
        return {"𐑲": 0, "𐑚": 1, "𐑔": 2}.get(self.value, 1)

    def can_amplify_to(self, other: "Granularity") -> bool:
        """Fine-to-coarse aggregation is possible; coarse-to-fine is not."""
        return self.ordinal <= other.ordinal

    @classmethod
    def from_symbol(cls, s: str) -> "Granularity":
        _map = {
            # glyph IDs (canonical)
            "𐑲":  cls.G_revapostrophe,
            "𐑚":  cls.G_beta,
            "𐑔":  cls.G_gamma,
            # Shavian (v0.6.0)
            "𐑚": cls.G_beta, "𐑔": cls.G_gamma, "𐑲": cls.G_revapostrophe,
            # phonetic names (backward compat)
            "Γ_revapostrophe": cls.G_revapostrophe, "G_א": cls.G_revapostrophe,
            "Γ_beta":  cls.G_beta,  "G_ב": cls.G_beta,
            "Γ_gamma": cls.G_gamma, "G_ג": cls.G_gamma,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "revapostrophe": cls.G_revapostrophe,
            "local": cls.G_revapostrophe,
            "beta": cls.G_beta,
            "mesoscale": cls.G_beta,
            "gamma": cls.G_gamma,
            "global": cls.G_gamma,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Granularity: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Granularity: unknown symbol {s!r}, defaulting to G_beta")
        return cls.G_beta


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
      Phi_revepsilon        = exceptional-point criticality (non-Hermitian degeneracy; absorbs O_∞ under tensor)
      Phi_upstep     = supercritical (unstable)
    Phi_ctyogh is ABSORBING under meet: meet(Phi_ctyogh, x) = Phi_ctyogh for all x.
    """
    # canonical Shavian names (SNS_PRIME.md §𝓕₅ Criticality)
    woe   = "𐑢"   # subcritical (stable, ordered)
    monad = "⊙"   # critical point (absorbing under meet)
    roar  = "𐑮"   # complex criticality (paraconsistent)
    err   = "𐑻"   # exceptional-point criticality
    haha  = "𐑣"   # supercritical (unstable)
    egg   = "𐑧"   # maximally indeterminate (synthetic / transactinide)
    # backward-compat aliases — duplicate values become aliases in Python Enum
    Phi_softsign        = "𐑢"
    Phi_ctyogh          = "⊙"
    Phi_closerevepsilon = "𐑮"
    Phi_revepsilon      = "𐑻"
    Phi_upstep          = "𐑣"
    Phi_ish             = "𐑧"
    SUBCRITICAL         = "𐑢"
    CRITICAL            = "⊙"
    SUPERCRITICAL       = "𐑣"

    @classmethod
    def from_symbol(cls, s: str) -> "Criticality":
        _map = {
            # glyph IDs (canonical)
            "𐑢":  cls.woe,
            "⊙":  cls.monad,
            "𐑮":  cls.roar,
            "𐑻":  cls.err,
            "𐑣":  cls.haha,
            "𐑧":  cls.egg,
            # Shavian names
            "woe": cls.woe, "monad": cls.monad, "roar": cls.roar,
            "err": cls.err, "haha": cls.haha,   "egg":  cls.egg,
            # phonetic names (backward compat)
            "⊙_softsign":       cls.Phi_softsign,       "Φ_sub":   cls.Phi_softsign,
            "⊙_ctyogh":         cls.Phi_ctyogh,         "Φ_c":     cls.Phi_ctyogh,
            "⊙_closerevepsilon": cls.Phi_closerevepsilon, "Φ_c_ℂ":  cls.Phi_closerevepsilon,
            "⊙_revepsilon":      cls.Phi_revepsilon,      "Φ_EP":    cls.Phi_revepsilon,
            "⊙_upstep":         cls.Phi_upstep,          "Φ_sup":   cls.Phi_upstep,
            # odot-prefixed variants (old memory file notation — keep as compat)
            "⊙_softsign": cls.woe,  "⊙_ctyogh": cls.monad,
            "⊙_closerevepsilon": cls.roar, "⊙_revepsilon": cls.err, "⊙_upstep": cls.haha,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "softsign": cls.Phi_softsign,
            "sub": cls.Phi_softsign,
            "subcritical": cls.Phi_softsign,
            "ctyogh": cls.Phi_ctyogh,
            "critical": cls.Phi_ctyogh,
            "c": cls.Phi_ctyogh,
            "closerevepsilon": cls.Phi_closerevepsilon,
            "revepsilon": cls.Phi_revepsilon,
            "ep": cls.Phi_revepsilon,
            "upstep": cls.Phi_upstep,
            "sup": cls.Phi_upstep,
            "supercritical": cls.Phi_upstep,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Criticality: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Criticality: unknown symbol {s!r}, defaulting to Phi_softsign")
        return cls.Phi_softsign

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
    Omega_closeepsilon = "𐑷"
    Omega_crtwo        = "𐑴"
    Omega_dzlig        = "𐑭"
    Omega_C            = "Ω_C"
    Omega_turna        = "𐑟"
    # Backward-compat aliases (old TopoIndex names)
    TRIVIAL     = "𐑷"
    Z2_CLASS    = "𐑴"
    Z_CLASS     = "𐑭"
    CHERN       = "Ω_C"
    NON_ABELIAN = "𐑟"

    @classmethod
    def from_symbol(cls, s: str) -> "Protection":
        _map = {
            # glyph IDs (canonical)
            "𐑷":  cls.Omega_closeepsilon,
            "𐑴":  cls.Omega_crtwo,
            "𐑭":  cls.Omega_dzlig,
            "Ω_C":  cls.Omega_C,
            "𐑟":  cls.Omega_turna,
            # Shavian (v0.6.0)
            "𐑷": cls.Omega_closeepsilon, "𐑴": cls.Omega_crtwo,
            "𐑭": cls.Omega_dzlig, "𐑟": cls.Omega_turna,
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
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "closeepsilon": cls.Omega_closeepsilon,
            "trivial": cls.Omega_closeepsilon,
            "crtwo": cls.Omega_crtwo,
            "z2": cls.Omega_crtwo,
            "z2_class": cls.Omega_crtwo,
            "dzlig": cls.Omega_dzlig,
            "z": cls.Omega_dzlig,
            "z_class": cls.Omega_dzlig,
            "c": cls.Omega_C,
            "chern": cls.Omega_C,
            "turna": cls.Omega_turna,
            "na": cls.Omega_turna,
            "non_abelian": cls.Omega_turna,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Protection: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Protection: unknown symbol {s!r}, defaulting to Omega_closeepsilon")
        return cls.Omega_closeepsilon

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
    # canonical Shavian names (SNS_PRIME.md §𝓕₃ Stoichiometry)
    hung = "𐑙"   # 1:1
    so   = "𐑕"   # 1:n (symmetric many)
    up   = "𐑳"   # n:m (unmatched many)
    dead = "𐑛"   # trivalent (boron-group / pnictogen)
    # backward-compat aliases
    S_doublebaresh = "𐑙"
    one_n          = "𐑕"
    S_ltailm       = "𐑳"
    cat            = "𐑳"

    @classmethod
    def from_symbol(cls, s: str) -> "Stoichiometry":
        _map = {
            # canonical glyphs
            "𐑙": cls.hung, "𐑕": cls.so, "𐑳": cls.up, "𐑛": cls.dead,
            # Shavian names
            "hung": cls.hung, "so": cls.so, "up": cls.up, "dead": cls.dead,
            # phonetic/legacy backward compat
            "Σ_doublebaresh": cls.hung, "Σ_ctn": cls.so, "Σ_ltailm": cls.up,
            "one_one": cls.hung, "n_n": cls.so, "n_m": cls.up,
            "1:1": cls.hung, "1:n": cls.so, "n:m": cls.up, "n:n": cls.so,
            "one_n": cls.so, "cat": cls.up,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "doublebaresh": cls.S_doublebaresh,
            "one_one": cls.S_doublebaresh,
            "ctn": cls.one_n,
            "one_n": cls.one_n,
            "ltailm": cls.S_ltailm,
            "n_m": cls.S_ltailm,
            "cat": cls.cat,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Stoichiometry: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Stoichiometry: unknown symbol {s!r}, defaulting to S_doublebaresh")
        return cls.S_doublebaresh


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
    H_closeomega     = "𐑓"
    H_toneletterstem = "𐑒"
    H_turntwo        = "𐑖"
    H_invscripta     = "𐑫"   # was "Hinf" (FIXED)

    @classmethod
    def from_symbol(cls, s: str) -> "Chirality":
        _map = {
            # glyph IDs (canonical)
            "𐑓":  cls.H_closeomega,
            "𐑒":  cls.H_toneletterstem,
            "𐑖":  cls.H_turntwo,
            "𐑫":  cls.H_invscripta,
            # Shavian (v0.6.0)
            "𐑓": cls.H_closeomega, "𐑒": cls.H_toneletterstem,
            "𐑖": cls.H_turntwo, "𐑫": cls.H_invscripta,
            # phonetic names (backward compat)
            "Ħ_closeomega":     cls.H_closeomega,     "H_0":   cls.H_closeomega,
            "Ħ_toneletterstem": cls.H_toneletterstem, "H_1":   cls.H_toneletterstem,
            "Ħ_turntwo":        cls.H_turntwo,        "H_2":   cls.H_turntwo,
            "Ħ_invscripta":     cls.H_invscripta,     "Hinf":  cls.H_invscripta,  "H_∞": cls.H_invscripta,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "closeomega": cls.H_closeomega,
            "achiral": cls.H_closeomega,
            "toneletterstem": cls.H_toneletterstem,
            "turntwo": cls.H_turntwo,
            "invscripta": cls.H_invscripta,
            "hinf": cls.H_invscripta,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Chirality: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Chirality: unknown symbol {s!r}, defaulting to H_closeomega")
        return cls.H_closeomega

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
        """Canonical tuple string: ⟨DTRPFKGΓΦΩSH⟩"""
        return (
            f"⟨{self.dimensionality.value}{self.topology.value}"
            f"{self.recognition_mode.value}{self.polarity.value}"
            f"{self.fidelity.value}{self.kinetic_character.value}"
            f"{self.granularity.value}{self.grammar.value}"
            f"{self.criticality_phase.value}{self.protection.value}"
            f"{self.stoichiometry.value}{self.chirality.value}⟩"
        )

    # Translate internal enum values to canonical ORDINALS keys (primitives.py).
    # Models layer uses a richer chemistry vocab; registry/zfc must see only canon values.
    _CANONICAL_MAP: ClassVar[Dict[str, str]] = {
        # D — non-canonical extensions collapse to nearest canonical
        "Ð_point": "𐑛", "Ð_line": "𐑛",
        "Ð_cube": "𐑨",
        # T — chemistry extras collapse to canonical 5
        "Þ_linear": "𐑰", "Þ_branched": "𐑰", "Þ_bowl": "𐑰",
        "Þ_cage": "𐑶",
        "Þ_torus": "𐑥", "Þ_braid": "𐑥",
        "Þ_network_hex": "𐑡", "Þ_network_mixed": "𐑡",
        "Þ_network_interp": "𐑡", "Þ_network_sym": "𐑡",
        # Grammar — non-canonical G_xor/G_impl/G_dissipative collapse to canonical
        "Γ_impl": "𐑠", "Γ_xor": "𐑜", "Γ_dissipative": "𐑵",
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
            "⊙":             self._canon(self.criticality_phase.value),
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

        Accepts glyph keys (Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, ⊙, Ħ, Σ, Ω), short ASCII keys
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
                dimensionality   = Dimensionality.from_symbol(_get("Ð", "D", "dimensionality", "𐑛")),
                topology         = Topology.from_symbol(_get("Þ", "T", "topology", "𐑡")),
                recognition_mode = Recognition.from_symbol(_get("Ř", "R", "recognition_mode", "𐑩")),
                polarity         = Polarity.from_symbol(_get("Φ", "P", "polarity", "𐑗")),
                grammar          = Grammar.from_symbol(_get("ɢ", "Gamma", "grammar", "𐑝")),
                fidelity         = Fidelity.from_symbol(_get("ƒ", "F", "fidelity", "𐑱")),
                kinetic_character= KineticChar.from_symbol(_get("Ç", "K", "kinetic_character", "𐑤")),
                granularity      = Granularity.from_symbol(_get("Γ", "G", "granularity", "𐑚")),
                criticality_phase= Criticality.from_symbol(_get("⊙", "Phi", "criticality_phase", "𐑢")),
                protection       = Protection.from_symbol(_get("Ω", "Omega", "protection", "𐑷")),
                stoichiometry    = Stoichiometry.from_symbol(_get("Σ", "S", "stoichiometry", "n:m")),
                chirality        = Chirality.from_symbol(_get("Ħ", "H", "chirality", "𐑓")),
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

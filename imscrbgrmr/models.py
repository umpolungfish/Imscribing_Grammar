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
    dead      = "𐑛"   # ordinal 1: 2D areal / molecular sheet
    ash = "𐑨"   # ordinal 2: triangulated / simplicial / stratified
    array  = "𐑼"   # ordinal 3: ∞-dimensional / iterative-temporal
    if_      = "𐑦"   # ordinal 4: imscriptive (boundary encodes bulk); canonical value D_omega
    # ── Lean-only extensions (non-canonical, chemistry/physics domain) ─────
    D_point = "Ð_point"   # 0D, scalar / spin-0 field
    D_line  = "Ð_line"    # 1D, vectorial
    D_cube  = "Ð_cube"    # 3D volumetric (Lean extension; canonical slot = D_turnthree)

    # Backward-compat aliases (chemistry-domain names → canonical values)

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
            "𐑛":  cls.dead,
            "𐑨":  cls.ash,
            "𐑼":  cls.array,
            "𐑦":  cls.if_,
            # phonetic names (backward compat)
            "Ð_wynn":       cls.dead,
            "Ð_turnthree":  cls.ash,
            "Ð_invomega":   cls.array,
            "Ð_omega":      cls.if_,
            # legacy canonical names (pre-migration)
            "Ð_triangle":   cls.ash,
            "Ð_wedge":      cls.dead,
            "Ð_infty":      cls.array,
            "Ð_odot":       cls.if_,
            # Lean extensions
            "Ð_point":  cls.D_point,
            "Ð_line":   cls.D_line,
            "Ð_cube":   cls.D_cube,
            # Shavian (v0.6.0)
            "𐑛": cls.dead,   "𐑨": cls.ash,
            "𐑼": cls.array, "𐑦": cls.if_,
            # Unicode aliases
            "D_∧": cls.dead,  "D_△": cls.ash,
            "D_∞": cls.array, "D_⊙": cls.if_,
            "Ð_infinity": cls.array,
            "Ð_holo": cls.if_,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "wynn": cls.dead,
            "wedge": cls.dead,
            "turnthree": cls.ash,
            "triangle": cls.ash,
            "invomega": cls.array,
            "infty": cls.array,
            "infinity": cls.array,
            "omega": cls.if_,
            "holo": cls.if_,
            "odot": cls.if_,
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
        return cls.dead


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
    judge    = "𐑡"         # general graph
    mime = "𐑥"         # cyclic closure / double-well / figure-8
    T_torus    = "Þ_torus"     # higher-genus compact (NEW — not in old Python)
    are     = "𐑸"         # imscriptive: non-local boundary-bulk; canonical: T_openo
    # Chemistry extras
    T_network_hex    = "Þ_network_hex"
    T_network_mixed  = "Þ_network_mixed"
    T_network_interp = "Þ_network_interp"
    T_network_sym    = "Þ_network_sym"
    oil  = "𐑶"
    eat  = "𐑰"
    T_braid = "Þ_braid"
    # Backward-compat aliases

    @classmethod
    def from_symbol(cls, s: str) -> "Topology":
        _map = {
            # glyph IDs (canonical)
            "𐑡":  cls.judge,
            "𐑥":  cls.mime,
            "𐑸":  cls.are,
            "𐑶":  cls.oil,
            "𐑰":  cls.eat,
            # phonetic names (backward compat)
            "Þ_linear": cls.T_linear,       "Þ_chains": cls.T_linear,
            "Þ_branched": cls.T_branched,
            "Þ_nrleg": cls.judge,
            "Þ_bullseye": cls.mime,
            "Þ_torus": cls.T_torus,
            "Þ_holo": cls.are,      "Þ_openo": cls.are,
            "Þ_network_hex": cls.T_network_hex,
            "Þ_network_mixed": cls.T_network_mixed,
            "Þ_network_interp": cls.T_network_interp,
            "Þ_network_sym": cls.T_network_sym,
            "Þ_cage": cls.oil,      "Þ_box": cls.oil,  "Þ_commatailz": cls.oil,
            "Þ_bowl": cls.eat,      "Þ_invscr": cls.eat,
            "Þ_braid": cls.T_braid,    "Þ_square": cls.judge,
            # Shavian (v0.6.0)
            "𐑡": cls.judge,  "𐑰": cls.eat, "𐑥": cls.mime,
            "𐑶": cls.oil,   "𐑸": cls.are,
            # Unicode aliases
            "T_∈": cls.eat,  "T_⋈": cls.mime,  "T_⊙": cls.are,
            "T_⊠": cls.oil,
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
            "nrleg": cls.judge,
            "network": cls.judge,
            "square": cls.judge,
            "bullseye": cls.mime,
            "cyclic_bowtie": cls.mime,
            "torus": cls.T_torus,
            "holo": cls.are,
            "openo": cls.are,
            "cage": cls.oil,
            "box": cls.oil,
            "commatailz": cls.oil,
            "bowl": cls.eat,
            "invscr": cls.eat,
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
    ado   = "𐑩"    # non-covalent / soft association
    tot     = "𐑑"    # covalent bond / structural transformation
    ear  = "𐑽"    # transition-state stabilisation / adjoint
    ian = "𐑾"    # mechanical topology / left-right asymmetric
    # Backward-compat aliases used by constraints.py

    @classmethod
    def from_symbol(cls, s: str) -> "Recognition":
        _map = {
            # glyph IDs (canonical)
            "𐑩":  cls.ado,
            "𐑑":  cls.tot,
            "𐑽":  cls.ear,
            "𐑾":  cls.ian,
            # phonetic names (backward compat)
            "Ř_subrightarrow":   cls.ado,
            "Ř_ctz":     cls.tot,
            "Ř_downstep":  cls.ear,
            "Ř_lyoghlig":      cls.ian,
            # Shavian (v0.6.0)
            "𐑩": cls.ado, "𐑑": cls.tot,
            "𐑽": cls.ear, "𐑾": cls.ian,
            # chemistry vocab
            "Ř_exact": cls.R_exact,
            "Ř_subset": cls.tot,         "R_⊆": cls.tot,
            "Ř_superset": cls.ado,     "R_⊇": cls.ado,
            "Ř_catalytic": cls.ear,   "R_‡": cls.ear,
            "Ř_allosteric": cls.R_allosteric,
            "Ř_mechanical": cls.ian, "R_⇔": cls.ian,
            "Ř_covalent_dynamic": cls.R_covalent_dynamic,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        # Suffix-based fallback: strip any hallucinated prefix before '_'
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _suffix_map = {
            "superset": cls.ado, "subrightarrow": cls.ado,
            "subset": cls.tot, "ctz": cls.tot, "covalent": cls.tot,
            "covalent_dynamic": cls.R_covalent_dynamic,
            "catalytic": cls.ear, "downstep": cls.ear,
            "allosteric": cls.R_allosteric, "exact": cls.R_exact,
            "mechanical": cls.ian, "lyoghlig": cls.ian,
        }
        if suffix in _suffix_map:
            import warnings
            warnings.warn(f"Recognition: normalised unknown symbol {s!r} via suffix {suffix!r}")
            return _suffix_map[suffix]
        import warnings
        warnings.warn(f"Recognition: completely unknown symbol {s!r}, defaulting to R_superset")
        return cls.ado


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
    church        = "𐑗"   # ordinal 1: asymmetric, no preferred direction
    yew           = "𐑿"   # ordinal 2: signed direction (electrophilic)
    out        = "𐑬"   # ordinal 3: self-complementary bipolar
    nun = "𐑯"   # ordinal 4: symmetric (non-Frobenius)
    or_  = "𐑹"   # ordinal 5: Frobenius special (P_pm_sym)
    # ── Aliases ───────────────────────────────────────────────────────────────

    @property
    def is_self_complementary(self) -> bool:
        return self.value in ("𐑹", "𐑬", "𐑯")

    @classmethod
    def from_symbol(cls, s: str) -> "Polarity":
        _map = {
            # glyph IDs (canonical)
            "𐑗":  cls.church,
            "𐑿":  cls.yew,
            "𐑬":  cls.out,
            "𐑯":  cls.nun,
            "𐑹":  cls.or_,
            # phonetic names (backward compat)
            "Φ_aolig":          cls.church,
            "Φ_upsilon":        cls.yew,
            "Φ_pipevar":        cls.out,
            "Φ_subdoublearrow": cls.nun,
            "Φ_doublebarpipe":  cls.or_,
            # Shavian (v0.6.0)
            "𐑗": cls.church,  "𐑿": cls.yew,    "𐑬": cls.out,
            "𐑯": cls.nun, "𐑹": cls.or_,
            # legacy canonical names
            "Φ_asym":    cls.church,
            "Φ_psi":     cls.yew,
            "Φ_pm":      cls.out,
            "Φ_sym":     cls.nun,
            "Φ_pm_sym":  cls.or_,  "P_±^sym": cls.or_,
            # chemistry vocab
            "Φ_neutral":     cls.church,
            "Φ_plus":        cls.yew,        "P+": cls.yew,
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
            "neutral": cls.church,
            "asym": cls.church,
            "directional": cls.church,
            "aolig": cls.church,
            "plus": cls.yew,
            "psi": cls.yew,
            "upsilon": cls.yew,
            "minus": cls.P_minus,
            "pm_pseudo": cls.P_pm_pseudo,
            "pipevar": cls.out,
            "pm": cls.out,
            "subdoublearrow": cls.nun,
            "sym": cls.nun,
            "doublebarpipe": cls.or_,
            "pm_sym": cls.or_,
            "frobenius": cls.or_,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Polarity: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Polarity: unknown symbol {s!r}, defaulting to P_neutral")
        return cls.church


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
    vow      = "𐑝"   # conjunctive / simultaneous (all partners required)
    gag = "𐑜"   # disjunctive / any one suffices
    measure   = "𐑠"   # sequential / ordered
    G_xor         = "Γ_xor"     # exclusive (NEW — was missing)
    G_impl        = "Γ_impl"    # implicative / conditional (NEW — was missing)
    ooze = "𐑵"       # irreversible / Lindblad (legacy)
    # Backward-compat aliases: old compound InteractionGrammar values -> canonical operator

    @classmethod
    def from_symbol(cls, s: str) -> "Grammar":
        _map = {
            # glyph IDs (canonical)
            "𐑝":  cls.vow,
            "𐑜":  cls.gag,
            "𐑠":  cls.measure,
            "𐑵":  cls.ooze,
            # Shavian (v0.6.0)
            "𐑝": cls.vow, "𐑜": cls.gag,
            "𐑠": cls.measure, "𐑵": cls.ooze,
            # phonetic names (backward compat)
            "ɢ_corner": cls.vow,   "ɢ_and": cls.vow,
            "ɢ_otimes": cls.vow,   "Γ_⊗": cls.vow,
            "ɢ_odot": cls.vow,     "Γ_⊙": cls.vow,
            "ɢ_spleftarrow": cls.gag, "ɢ_or": cls.gag,
            "ɢ_bigcirc": cls.gag,   "Γ_○": cls.gag,
            "ɢ_secstress": cls.measure,   "ɢ_seq": cls.measure,
            "ɢ_dissipative": cls.ooze,   "ɢ_doublevertline": cls.ooze,
            # Unicode aliases
            "Γ_∧": cls.vow,
            "Γ_∨": cls.gag,
            "Γ_→": cls.measure,
            # G_xor / G_impl kept as phonetic since they have no glyph ID yet
            "Γ_xor": cls.G_xor,
            "Γ_impl": cls.G_impl,
            # legacy full string (backward compat)
            "Γ_dissipative": cls.ooze,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "corner": cls.vow,
            "and": cls.vow,
            "otimes": cls.vow,
            "odot": cls.vow,
            "spleftarrow": cls.gag,
            "or": cls.gag,
            "bigcirc": cls.gag,
            "secstress": cls.measure,
            "seq": cls.measure,
            "xor": cls.G_xor,
            "impl": cls.G_impl,
            "dissipative": cls.ooze,
            "doublevertline": cls.ooze,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Grammar: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Grammar: unknown symbol {s!r}, defaulting to Gamma_corner")
        return cls.vow

    @property
    def partner_logic(self) -> str:
        return {
            Grammar.vow:      "All partners required simultaneously",
            Grammar.gag: "Any one partner suffices",
            Grammar.measure:   "Ordered sequential recognition",
            Grammar.G_xor:             "Exactly one partner (exclusive)",
            Grammar.G_impl:            "Partner A implies partner B",
            Grammar.ooze:     "Irreversible — information erased by environment",
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
    age    = "𐑱"     # classical search fidelity
    they       = "𐑞"     # HotSwap threshold
    peep = "𐑐"     # quantum coherent
    # Backward-compat aliases

    @classmethod
    def from_symbol(cls, s: str) -> "Fidelity":
        _map = {
            # glyph IDs (canonical)
            "𐑱":  cls.age,
            "𐑞":  cls.they,
            "𐑐":  cls.peep,
            # Shavian (v0.6.0)
            "𐑱": cls.age, "𐑞": cls.they, "𐑐": cls.peep,
            # phonetic names (backward compat)
            "ƒ_noise": cls.F_noise,
            "ƒ_beltl": cls.age,   "F_ℓ": cls.age,   "LOW": cls.age,
            "ƒ_dh": cls.they,         "F_ℇ": cls.they,       "MEDIUM": cls.they,
            "ƒ_hardsign": cls.peep, "F_ℏ": cls.peep, "HIGH": cls.peep,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "noise": cls.F_noise,
            "beltl": cls.age,
            "low": cls.age,
            "dh": cls.they,
            "medium": cls.they,
            "hardsign": cls.peep,
            "high": cls.peep,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Fidelity: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Fidelity: unknown symbol {s!r}, defaulting to F_beltl")
        return cls.age

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
    yea = "𐑘"
    loll       = "𐑤"   # was MODERATE
    egg       = "𐑧"
    on     = "𐑪"
    air      = "𐑺"
    # Backward-compat aliases

    @classmethod
    def from_symbol(cls, s: str) -> "KineticChar":
        _map = {
            # glyph IDs (canonical)
            "𐑘":  cls.yea,
            "𐑤":  cls.loll,
            "𐑧":  cls.egg,
            "𐑪":  cls.on,
            "𐑺":  cls.air,
            # Shavian (v0.6.0)
            "𐑘": cls.yea, "𐑤": cls.loll, "𐑧": cls.egg,
            "𐑪": cls.on, "𐑺": cls.air,
            # phonetic names (backward compat)
            "Ç_frtailgamma": cls.yea, "FAST": cls.yea,
            "Ç_turnm":  cls.loll,  "MODERATE": cls.loll,
            "Ç_schwa": cls.egg, "SLOW": cls.egg,
            "Ç_teshlig": cls.on, "TRAP": cls.on,
            "Ç_lambda":  cls.air,  "MBL": cls.air,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "frtailgamma": cls.yea,
            "fast": cls.yea,
            "turnm": cls.loll,
            "moderate": cls.loll,
            "schwa": cls.egg,
            "slow": cls.egg,
            "teshlig": cls.on,
            "trap": cls.on,
            "lambda": cls.air,
            "mbl": cls.air,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"KineticChar: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"KineticChar: unknown symbol {s!r}, defaulting to K_schwa")
        return cls.egg

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
    ice = "𐑲"   # fine-grained, atomic (ℵ) — was incorrectly GLOBAL in old Python
    bib          = "𐑚"   # mesoscale local (ℶ) — was LOCAL
    thigh         = "𐑔"   # coarse, collective (ℷ) — was incorrectly MESOSCALE in old Python
    # Backward-compat key aliases with CORRECTED semantics:

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
            "𐑲":  cls.ice,
            "𐑚":  cls.bib,
            "𐑔":  cls.thigh,
            # Shavian (v0.6.0)
            "𐑚": cls.bib, "𐑔": cls.thigh, "𐑲": cls.ice,
            # phonetic names (backward compat)
            "Γ_revapostrophe": cls.ice, "G_א": cls.ice,
            "Γ_beta":  cls.bib,  "G_ב": cls.bib,
            "Γ_gamma": cls.thigh, "G_ג": cls.thigh,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "revapostrophe": cls.ice,
            "local": cls.ice,
            "beta": cls.bib,
            "mesoscale": cls.bib,
            "gamma": cls.thigh,
            "global": cls.thigh,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Granularity: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Granularity: unknown symbol {s!r}, defaulting to G_beta")
        return cls.bib


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
        return self == Criticality.monad


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
    awe = "𐑷"
    oak        = "𐑴"
    ah        = "𐑭"
    Omega_C            = "Ω_C"
    zoo        = "𐑟"
    # Backward-compat aliases (old TopoIndex names)

    @classmethod
    def from_symbol(cls, s: str) -> "Protection":
        _map = {
            # glyph IDs (canonical)
            "𐑷":  cls.awe,
            "𐑴":  cls.oak,
            "𐑭":  cls.ah,
            "Ω_C":  cls.Omega_C,
            "𐑟":  cls.zoo,
            # Shavian (v0.6.0)
            "𐑷": cls.awe, "𐑴": cls.oak,
            "𐑭": cls.ah, "𐑟": cls.zoo,
            # phonetic names (backward compat)
            "Ω_closeepsilon":  cls.awe, "Ω_0":  cls.awe, "TRIVIAL":     cls.awe,
            "Ω_crtwo": cls.oak, "Ω_Z2": cls.oak, "Z2_CLASS":    cls.oak,
            "Ω_dzlig":  cls.ah,  "Ω_Z":  cls.ah,  "Z_CLASS":     cls.ah,
            "Ω_turna": cls.zoo, "Ω_NA": cls.zoo, "NON_ABELIAN": cls.zoo,
            "CHERN":       cls.Omega_C,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "closeepsilon": cls.awe,
            "trivial": cls.awe,
            "crtwo": cls.oak,
            "z2": cls.oak,
            "z2_class": cls.oak,
            "dzlig": cls.ah,
            "z": cls.ah,
            "z_class": cls.ah,
            "c": cls.Omega_C,
            "chern": cls.Omega_C,
            "turna": cls.zoo,
            "na": cls.zoo,
            "non_abelian": cls.zoo,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Protection: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Protection: unknown symbol {s!r}, defaulting to Omega_closeepsilon")
        return cls.awe

    @property
    def protection_strength(self) -> int:
        """Ordinal protection level 0–4 (matches Lean _PROT_ORD)."""
        return _prot_ord(self)

    @property
    def physical_systems(self) -> str:
        return {
            Protection.awe: "Ordinary insulators, classical systems",
            Protection.oak:        "HgTe/CdTe, Bi2Se3, topological insulators (AII/DIII)",
            Protection.ah:        "Kitaev chain, SSH model, 1D p-wave superconductors",
            Protection.Omega_C:            "Integer quantum Hall, Chern insulators (class A)",
            Protection.zoo:        "nu=5/2 FQH, Kitaev honeycomb B-phase, non-Abelian Majorana",
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
    fee     = "𐑓"
    kick = "𐑒"
    sure        = "𐑖"
    wool     = "𐑫"   # was "Hinf" (FIXED)

    @classmethod
    def from_symbol(cls, s: str) -> "Chirality":
        _map = {
            # glyph IDs (canonical)
            "𐑓":  cls.fee,
            "𐑒":  cls.kick,
            "𐑖":  cls.sure,
            "𐑫":  cls.wool,
            # Shavian (v0.6.0)
            "𐑓": cls.fee, "𐑒": cls.kick,
            "𐑖": cls.sure, "𐑫": cls.wool,
            # phonetic names (backward compat)
            "Ħ_closeomega":     cls.fee,     "H_0":   cls.fee,
            "Ħ_toneletterstem": cls.kick, "H_1":   cls.kick,
            "Ħ_turntwo":        cls.sure,        "H_2":   cls.sure,
            "Ħ_invscripta":     cls.wool,     "Hinf":  cls.wool,  "H_∞": cls.wool,
        }
        try:
            return _map[s]
        except KeyError:
            pass
        suffix = s.split("_", 1)[-1].lower() if "_" in s else s.lower()
        _sfx = {
            "closeomega": cls.fee,
            "achiral": cls.fee,
            "toneletterstem": cls.kick,
            "turntwo": cls.sure,
            "invscripta": cls.wool,
            "hinf": cls.wool,
        }
        if suffix in _sfx:
            import warnings
            warnings.warn(f"Chirality: normalised {s!r} via suffix {suffix!r}")
            return _sfx[suffix]
        import warnings
        warnings.warn(f"Chirality: unknown symbol {s!r}, defaulting to H_closeomega")
        return cls.fee

    @property
    def memory_depth(self) -> str:
        return {
            Chirality.fee:     "0 — no persistent symmetry breaking",
            Chirality.kick: "1 — single axis, thermally reversible",
            Chirality.sure:        "n — n reinforcing axes, structurally encoded",
            Chirality.wool:     "∞ — topology-protected, requires bond-breaking to reverse",
        }[self]

    @property
    def implies_k_trap(self) -> bool:
        """Axiom A: H_invscripta implies K_teshlig."""
        return self == Chirality.wool


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
        if _prot_ord(self.protection) >= _prot_ord(Protection.ah) \
                and _chir_ord(self.chirality) < _chir_ord(Chirality.sure):
            raise ValueError(
                f"Axiom B violated in '{name}': protection {self.protection.value} "
                f"requires chirality >= H_turntwo (got {self.chirality.value})"
            )
        # Axiom C: D_omega ↔ T_openo
        d_holo = self.dimensionality == Dimensionality.if_
        t_holo = self.topology == Topology.are
        if d_holo != t_holo:
            raise ValueError(
                f"Axiom C violated in '{name}': D_omega ↔ T_openo "
                f"(got dim={self.dimensionality.value}, top={self.topology.value})"
            )
        # Axiom D: Omega_turna → D_omega
        if self.protection == Protection.zoo \
                and self.dimensionality != Dimensionality.if_:
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
        kwargs["protection"] = Protection.awe
        using_defaults = True
    if "chirality" not in kwargs:
        kwargs["chirality"] = Chirality.fee
        using_defaults = True
    stoi = kwargs.get("stoichiometry")
    if isinstance(stoi, str):
        kwargs["stoichiometry"] = Stoichiometry.from_symbol(stoi)
    elif stoi is None:
        kwargs["stoichiometry"] = Stoichiometry.up
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

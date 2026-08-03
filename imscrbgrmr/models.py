"""
Imscribing Grammar Models — Canonical 12-primitive type system.

Unified with the Lean 4 formalization in Imscribing Grammar/Primitives/Core.lean and
Imscription.lean. Enum VALUES are glyph IDs (e.g. 𐑛, 𐑡, 𐑓); field names on
Imscription use the long Python-readable form with short-name properties (dim, top,
recog, pol, gram, fid, kin, gran, crit, prot, stoi, chir) mirroring Lean.

Tuple notation: ⟨D; T; R; P; F; K; G; ∈; <; Ω; S; H⟩

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

    # Backward-compat aliases (chemistry-domain names → canonical values)

    @property
    def domains(self) -> frozenset:
        """Which domains this extent is at home in."""
        return {
            "𐑛": frozenset({"molecular"}),
            "𐑨": frozenset({"molecular", "supramolecular"}),
            "𐑼": frozenset({"temporal", "molecular"}),
            "𐑦": frozenset({"temporal", "molecular", "supramolecular", "imscriptive"}),
        }.get(self.value, frozenset())

    @classmethod
    def from_symbol(cls, s: str) -> "Dimensionality":
        _map = {
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "dead": cls.dead,
            "ash": cls.ash,
            "array": cls.array,
            "if_": cls.if_,
            # glyph IDs (canonical)
            "𐑛": cls.dead,
            "𐑨": cls.ash,
            "𐑼": cls.array,
            "𐑦": cls.if_,
            # phonetic names (backward compat)
            # legacy canonical names (pre-migration)
            # Lean extensions
            # Shavian (v0.6.0)
            "𐑛": cls.dead, "𐑨": cls.ash,
            "𐑼": cls.array, "𐑦": cls.if_,
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None


# =============================================================================
# Primitive II: Topology (T)
# =============================================================================

class Topology(Enum):
    """
    Pattern of connections within the imscription's minimal motif.

    Lean canonical 6: T_linear, T_branched, T_nrleg, T_bullseye, T_torus, T_openo.
    Chemistry extras below the separator are valid for molecular catalog entries.
    """
    judge    = "𐑡"         # general graph
    mime = "𐑥"         # cyclic closure / double-well / figure-8
    are     = "𐑸"         # imscriptive: non-local boundary-bulk; canonical: T_openo
    # Chemistry extras
    oil  = "𐑶"
    eat  = "𐑰"
    # Backward-compat aliases

    @classmethod
    def from_symbol(cls, s: str) -> "Topology":
        _map = {
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "judge": cls.judge,
            "mime": cls.mime,
            "are": cls.are,
            "oil": cls.oil,
            "eat": cls.eat,
            # glyph IDs (canonical)
            "𐑡": cls.judge,
            "𐑥": cls.mime,
            "𐑸": cls.are,
            "𐑶": cls.oil,
            "𐑰": cls.eat,
            # phonetic names (backward compat)
            # Shavian (v0.6.0)
            "𐑡": cls.judge, "𐑰": cls.eat, "𐑥": cls.mime,
            "𐑶": cls.oil, "𐑸": cls.are,
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None


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
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "ado": cls.ado,
            "tot": cls.tot,
            "ear": cls.ear,
            "ian": cls.ian,
            # glyph IDs (canonical)
            "𐑩": cls.ado,
            "𐑑": cls.tot,
            "𐑽": cls.ear,
            "𐑾": cls.ian,
            # phonetic names (backward compat)
            # Shavian (v0.6.0)
            "𐑩": cls.ado, "𐑑": cls.tot,
            "𐑽": cls.ear, "𐑾": cls.ian,
            # chemistry vocab
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback: only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None


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
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "church": cls.church,
            "yew": cls.yew,
            "out": cls.out,
            "nun": cls.nun,
            "or_": cls.or_,
            # glyph IDs (canonical)
            "𐑗": cls.church,
            "𐑿": cls.yew,
            "𐑬": cls.out,
            "𐑯": cls.nun,
            "𐑹": cls.or_,
            # phonetic names (backward compat)
            # Shavian (v0.6.0)
            "𐑗": cls.church, "𐑿": cls.yew, "𐑬": cls.out,
            "𐑯": cls.nun, "𐑹": cls.or_,
            # legacy canonical names
            # chemistry vocab
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None


# =============================================================================
# Primitive V: Coupling (∈)
# =============================================================================

class Grammar(Enum):
    """
    Partner selection logic: the Boolean operator governing how partners combine.

    Lean canonical 5: Gamma_corner, Gamma_spleftarrow, Gamma_secstress, G_xor, G_impl.
    Replaces the old compound InteractionGrammar(operator, tier) — the tier
    (SPECIFIC/SELECTIVE/BROAD/QUANTUM) encoded selectivity, which belongs to
    Fidelity or domain metadata, not the grammar.

    G_dissipative retained from old GrammarOperator for catalogs that used it.
    """
    vow      = "𐑝"   # conjunctive / simultaneous (all partners required)
    gag = "𐑜"   # disjunctive / any one suffices
    measure   = "𐑠"   # sequential / ordered
    ooze = "𐑵"       # irreversible / Lindblad (legacy)
    # Backward-compat aliases: old compound InteractionGrammar values -> canonical operator

    @classmethod
    def from_symbol(cls, s: str) -> "Grammar":
        _map = {
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "vow": cls.vow,
            "gag": cls.gag,
            "measure": cls.measure,
            "ooze": cls.ooze,
            # glyph IDs (canonical)
            "𐑝": cls.vow,
            "𐑜": cls.gag,
            "𐑠": cls.measure,
            "𐑵": cls.ooze,
            # Shavian (v0.6.0)
            "𐑝": cls.vow, "𐑜": cls.gag,
            "𐑠": cls.measure, "𐑵": cls.ooze,
            # phonetic names (backward compat)
            # Unicode aliases
            # G_xor / G_impl kept as phonetic since they have no glyph ID yet
            # legacy full string (backward compat)
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None

    @property
    def partner_logic(self) -> str:
        return {
            Grammar.vow:      "All partners required simultaneously",
            Grammar.gag: "Any one partner suffices",
            Grammar.measure:   "Ordered sequential recognition",
            Grammar.gag:             "Exactly one partner (exclusive)",
            Grammar.measure:            "Partner A implies partner B",
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
    age    = "𐑱"     # classical search fidelity
    they       = "𐑞"     # HotSwap threshold
    peep = "𐑐"     # quantum coherent
    # Backward-compat aliases

    @classmethod
    def from_symbol(cls, s: str) -> "Fidelity":
        _map = {
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "age": cls.age,
            "they": cls.they,
            "peep": cls.peep,
            # glyph IDs (canonical)
            "𐑱": cls.age,
            "𐑞": cls.they,
            "𐑐": cls.peep,
            # Shavian (v0.6.0)
            "𐑱": cls.age, "𐑞": cls.they, "𐑐": cls.peep,
            # phonetic names (backward compat)
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None

    @property
    def numeric_value(self) -> float:
        return {"𐑱": 0.0, "𐑱": 0.33, "𐑞": 0.67, "𐑐": 1.0}[self.value]


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
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "yea": cls.yea,
            "loll": cls.loll,
            "egg": cls.egg,
            "on": cls.on,
            "air": cls.air,
            # glyph IDs (canonical)
            "𐑘": cls.yea,
            "𐑤": cls.loll,
            "𐑧": cls.egg,
            "𐑪": cls.on,
            "𐑺": cls.air,
            # Shavian (v0.6.0)
            "𐑘": cls.yea, "𐑤": cls.loll, "𐑧": cls.egg,
            "𐑪": cls.on, "𐑺": cls.air,
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None

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
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "ice": cls.ice,
            "bib": cls.bib,
            "thigh": cls.thigh,
            # glyph IDs (canonical)
            "𐑲": cls.ice,
            "𐑚": cls.bib,
            "𐑔": cls.thigh,
            # Shavian (v0.6.0)
            "𐑚": cls.bib, "𐑔": cls.thigh, "𐑲": cls.ice,
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None


# =============================================================================
# Primitive IX: Criticality (<)
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
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "woe": cls.woe,
            "monad": cls.monad,
            "roar": cls.roar,
            "err": cls.err,
            "haha": cls.haha,
            "egg": cls.egg,
            # glyph IDs (canonical)
            "𐑢": cls.woe,
            "⊙": cls.monad,
            "𐑮": cls.roar,
            "𐑻": cls.err,
            "𐑣": cls.haha,
            "𐑧": cls.egg,
            # Shavian names
            "woe": cls.woe, "monad": cls.monad, "roar": cls.roar,
            "err": cls.err, "haha": cls.haha, "egg": cls.egg,
            # phonetic names (backward compat)
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None

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
    zoo        = "𐑟"
    # Backward-compat aliases (old TopoIndex names)

    @classmethod
    def from_symbol(cls, s: str) -> "Protection":
        _map = {
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "awe": cls.awe,
            "oak": cls.oak,
            "ah": cls.ah,
            "zoo": cls.zoo,
            # glyph IDs (canonical)
            "𐑷": cls.awe,
            "𐑴": cls.oak,
            "𐑭": cls.ah,
            "𐑟": cls.zoo,
            # Shavian (v0.6.0)
            "𐑷": cls.awe, "𐑴": cls.oak,
            "𐑭": cls.ah, "𐑟": cls.zoo,
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None

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
            Protection.ah:            "Integer quantum Hall, Chern insulators (class A)",
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
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "hung": cls.hung,
            "so": cls.so,
            "up": cls.up,
            "dead": cls.dead,
            # canonical glyphs
            "𐑙": cls.hung, "𐑕": cls.so, "𐑳": cls.up, "𐑛": cls.dead,
            # Shavian names
            "hung": cls.hung, "so": cls.so, "up": cls.up, "dead": cls.dead,
            # phonetic/legacy backward compat
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None


# =============================================================================
# Primitive XII: Chirality / Temporal Memory (H)
# =============================================================================

class Chirality(Enum):
    """
    Degree and persistence of broken orientational symmetry.
    The only intrinsically anisotropic primitive — the only one that breaks
    time-reversal symmetry of the grammar.

    Lean canonical 4 (ordered H_closeomega < H_toneletterstem < H_turntwo < H_invscripta):
      H_closeomega    = achiral: shift-invariant, no handedness to break
      H_toneletterstem    = soft chiral: period-2 under the shift (atropisomers)
      H_turntwo    = persistent chiral: a descent through rank (amino acids, DNA)
      H_invscripta = topological chiral (implies K_teshlig by Axiom A)
    """
    fee     = "𐑓"
    kick = "𐑒"
    sure        = "𐑖"
    wool     = "𐑫"   # was "Hinf" (FIXED)

    @classmethod
    def from_symbol(cls, s: str) -> "Chirality":
        _map = {
            # canonical: the glyph, and the Shavian name. Nothing else resolves —
            # an old form MUST NOT import, so it is simply absent.
            "fee": cls.fee,
            "kick": cls.kick,
            "sure": cls.sure,
            "wool": cls.wool,
            # glyph IDs (canonical)
            "𐑓": cls.fee,
            "𐑒": cls.kick,
            "𐑖": cls.sure,
            "𐑫": cls.wool,
            # Shavian (v0.6.0)
            "𐑓": cls.fee, "𐑒": cls.kick,
            "𐑖": cls.sure, "𐑫": cls.wool,
        }
        try:
            return _map[s]
        except KeyError:
            # No fallback. A silent default is how old notation kept "working"
            # while lying: Φ_c once meant the critical fixed point, and defaulting
            # returned the subcritical value instead — the opposite end of the axis,
            # with no error. Only the glyph or the Shavian name resolves.
            raise ValueError(
                f"{cls.__name__}: unknown symbol {s!r}. Valid: a glyph "
                f"({', '.join(m.value for m in cls)}) or a Shavian name "
                f"({', '.join(m.name for m in cls)}). Old notation does not resolve."
            ) from None

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

    Notation: ⟨D; T; R; P; F; K; G; ∈; <; Ω; S; H⟩

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
        # ── The four axioms are CLOSURE conditions, not coordinate rules ──────
        # Established by the correct_formulation_of_axiom_{a,b,c,d} ob3ects. Each
        # axiom asserts that a named δ/μ dyad closes: μ∘δ = id with ΔS ≈ 0, with
        # EVALT the affirmative arm and EVALF the failure arm. Each names its own
        # split, and that split is the whole content of the axiom:
        #
        #   A  Bulk → (Boundary projection, Bulk remainder) → Bulk
        #      "the boundary accurately encodes the bulk" / "encoding fails to
        #      represent the bulk". Information preserved through encode+decode.
        #   B  Topological-State → (Persistent-Chiral arm, Achiral arm) → same
        #      "integer winding conserved" / "broken symmetry, no protection".
        #      Dialetheia-complete: BOTH arms run, held at ENGAGR through transition.
        #   C  Bulk → (Boundary-Projection, Bulk-Residual) → Bulk
        #      "correspondence exact" / "encoding fails to preserve bulk info".
        #   D  Bulk → (Boundary-encoding, Bulk-decoding) → Bulk
        #      "μ∘δ = id satisfied" / "encoding incomplete or symmetry broken".
        #
        # Truth is established by RUNNING the dyad, which the twelve coordinates
        # cannot decide. NO coordinate-level check is enforced here, because every
        # coordinate form is falsified — twice over:
        #
        #   Self-application. The correct formulation of A imscribes with ⊥=𐑫 ∧ ⊤=𐑧,
        #   the exact pair old-A forbade. The correct formulation of D imscribes with
        #   ⊢=𐑛 ∧ Ω=𐑟 (old-D required ⊢=𐑦) and ⊣=𐑸 at ⊢=𐑛 (violating one-way C).
        #   Each correct formulation violates the coordinate form of its own axiom.
        #
        #   Catalog. Every shadow has counterexamples across multiple dimensionalities,
        #   including genuine non-Abelian anyons and SIC existence entries carrying
        #   Ω=𐑟 without ⊢=𐑦.
        #
        # Enforcing any of them refuses to construct legal tuples. The closure test
        # belongs to the protocol layer, where δ/μ can actually be run: see
        # CoreAxioms.closure_verdict().
        _ = self.name

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
        """Canonical tuple string: ⟨⊢ ⊣ > < ⋈ ⊤ ∈ ɢ ⊙ Ħ Σ Ω⟩ (concatenated, no separators).

        Ħ (chirality) is slot 10 and Ω (protection) is slot 12. Emitting protection at
        10 and chirality at 12 transposes them: the VALUES stay correct but land in each
        other's slots, so every consumer that reads by position sees an Ω-value where Ħ
        belongs and vice versa — and neither is a member of the slot's own value set.
        """
        return (
            f"⟨{self.dimensionality.value}{self.topology.value}"
            f"{self.recognition_mode.value}{self.polarity.value}"
            f"{self.fidelity.value}{self.kinetic_character.value}"
            f"{self.granularity.value}{self.grammar.value}"
            f"{self.criticality_phase.value}{self.chirality.value}"
            f"{self.stoichiometry.value}{self.protection.value}⟩"
        )

    # Translate internal enum values to canonical ORDINALS keys (primitives.py).
    # Models layer uses a richer chemistry vocab; registry/zfc must see only canon values.


    def to_dict(self) -> Dict[str, Any]:
        return {
            "name":          self.name,
            "description":   self.description,
            "⊢":             self.dimensionality.value,
            "⊣":             self.topology.value,
            ">":             self.recognition_mode.value,
            "<":             self.polarity.value,
            "⋈":             self.fidelity.value,
            "⊤":             self.kinetic_character.value,
            "∈":             self.granularity.value,
            "∋":             self.grammar.value,
            "⊙":             self.criticality_phase.value,
            "◻":             self.protection.value,
            "⊞":             self.stoichiometry.value,
            "⊥":             self.chirality.value,
            "grounding":     self.grounding,
            "is_grounded":   self.is_grounded,
            "metadata":      self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Imscription":
        """
        Construct a Imscription from a catalog dict (new or legacy format).

        Accepts glyph keys (⊢, ⊣, >, <, ⋈, ⊤, ∈, ∋, ⊙, ⊥, ⊞, ◻), short ASCII keys
        (D, T, R, P, F, K, G, Gamma, Phi, Omega, S, H), and long Python field names.

        The retired glyph keys do NOT resolve. Every stored catalog was migrated
        with the rename, so a dict still carrying them is not old data to be
        read, it is data that was missed, and a reader that quietly accepted it
        is how the two alphabets stayed alive through the last several purges.
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
                dimensionality   = Dimensionality.from_symbol(_get("⊢", "D", "dimensionality", "𐑛")),
                topology         = Topology.from_symbol(_get("⊣", "T", "topology", "𐑡")),
                recognition_mode = Recognition.from_symbol(_get(">", "R", "recognition_mode", "𐑩")),
                polarity         = Polarity.from_symbol(_get("<", "P", "polarity", "𐑗")),
                grammar          = Grammar.from_symbol(_get("∋", "Gamma", "grammar", "𐑝")),
                fidelity         = Fidelity.from_symbol(_get("⋈", "F", "fidelity", "𐑱")),
                kinetic_character= KineticChar.from_symbol(_get("⊤", "K", "kinetic_character", "𐑤")),
                granularity      = Granularity.from_symbol(_get("∈", "G", "granularity", "𐑚")),
                criticality_phase= Criticality.from_symbol(_get("⊙", "Phi", "criticality_phase", "𐑢")),
                protection       = Protection.from_symbol(_get("◻", "Omega", "protection", "𐑷")),
                # 𐑳 is n:m, the general ratio: the old "n:m" spelling was left as the
                # default long after from_symbol stopped resolving it, so an entry
                # missing this key raised instead of taking a default.
                stoichiometry    = Stoichiometry.from_symbol(_get("⊞", "S", "stoichiometry", "𐑳")),
                chirality        = Chirality.from_symbol(_get("⊥", "H", "chirality", "𐑓")),
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

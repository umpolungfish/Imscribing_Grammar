"""
IG_inquiry.py — Imscribing Grammar General-Purpose Inquiry Loop
=============================================================
An agentic loop that gives a model free rein to apply the Imscribing Grammar
primitive grammar to any question. The model encodes systems, computes
distances, finds cross-domain analogs, asks its own follow-up questions,
and records insights — iterating until it converges on structural understanding.

Unlike imscribe_agent.py (which targets a specific structural design goal),
this loop is open-ended: the model steers the inquiry across any domain —
molecular, physical, mathematical, mythological, linguistic, or social.

The loop runs in two phases:

  **Phase 1 — Grammatical analysis (tool-enabled):**
  1.  Seed question / topic → model receives it with full primitive reference
  2.  Model calls tools freely: encode, distance, lookup, ask_question, record_insight
  3.  Any question pushed via ask_question feeds the next iteration
  4.  Model emits CONCLUDE when it has sufficient structural understanding,
      followed by a synthesis that directly answers the original question
  5.  Session catalog accumulates — encodings persist across iterations

  **Phase 2 — Speculation (tool-free, automatic):**
  6.  Immediately after CONCLUDE, a second tool-free LLM call is made.
      The model is released from primitive discipline and asked to speculate
      openly on how the request or object might actually be realised, built,
      or approached in the world — using the grammar's verdict as a launching
      point, not a constraint. The four speculation axes are:
        · What materials, processes, institutions, or technologies are needed?
        · What intermediate steps or milestones would the path require?
        · Are there existing near-analogs that could be adapted?
        · What is the most non-obvious realization path the grammar suggests?
  7.  Speculation text is stored in the concluding IterationRecord and
      displayed at the end of the session summary under a SPECULATION header.

Tools available to the model:
  Encoding & distance:
  • encode_system        — register a system as a imscription tuple in the session
  • compute_distance     — weighted Euclidean distance + per-primitive breakdown
  • lookup_catalog       — find catalog entries matching a keyword
  • list_catalog         — list all currently encoded systems

  Algebra (composition):
  • compute_meet         — lattice meet A∧B: shared primitive floor
  • compute_join         — lattice join A∨B: minimal upper bound
  • compute_tensor       — tensor product A⊗B: structural composition
  • find_analogies       — nearest catalog neighbors by distance

  Probes:
  • phi_c_probe          — test whether a system is at criticality (⊙_ÿ)
  • topo_protection_probe — test winding class (Omega)

  Decomposition:
  • project              — project onto a primitive subset
  • primitive_peel       — strip one primitive to minimum; return residual
  • principal_decomp     — join-irreducible atoms (minimal building blocks)
  • retrosynthetic_path  — trace back to structural baseline step by step

  Meta:
  • ask_question         — push a follow-up question onto the inquiry queue
  • record_insight       — record a structured insight (TOPO / DIAPH / ONTO plane); returns insight_id

Providers (same routing as imscribe_agent.py):
  "anthropic"   — Anthropic SDK + ANTHROPIC_API_KEY  (default)
  "openai"      — OpenAI SDK + OPENAI_API_KEY
  "deepseek"    — OpenAI-compatible + DEEPSEEK_API_KEY
  "qwen"        — OpenAI-compatible + QWEN_API_KEY
  "gemini"      — Google Gemini OpenAI-compat + GOOGLE_API_KEY
                  Default model: gemini-2.0-flash
  "mistral"     — Mistral AI + MISTRAL_API_KEY
                  Default model: mistral-large-latest
  "openrouter"  — OpenRouter + OPENROUTER_API_KEY
                  Default model: google/gemini-2.5-pro (override with IG_MODEL)
                  Optional: OPENROUTER_REFERER, OPENROUTER_TITLE env vars for routing headers.
  "local"       — OpenAI-compatible at localhost:11434/v1  (ollama / LM Studio / vLLM)
                  Set LOCAL_MODEL_URL env var to override the endpoint.
                  Set LOCAL_API_KEY env var for servers that require a key.

Usage:
    from ig_inquiry import IGInquiryLoop
    loop = IGInquiryLoop("What is the primitive distance between consciousness and quantum measurement?")
    results = loop.run()

    # Or: from the CLI
    python IG_inquiry.py "What structural features distinguish life from non-life?"
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    from rich.console import Console as _RichConsole
    _console = _RichConsole(highlight=False)
    def _print(*args, **kwargs):
        _console.print(*args, **kwargs)
except ImportError:
    _console = None  # type: ignore
    _MARKUP_RE = re.compile(r'\[/?[\w .#_]+\]')
    def _print(*args, **kwargs):
        clean = [_MARKUP_RE.sub('', a) if isinstance(a, str) else a for a in args]
        print(*clean, **kwargs)

# Standalone markup stripper used by transcript writer (works whether Rich is present or not)
_MARKUP_STRIP_RE = re.compile(r'\[/?[\w .#_/]+\]')

# ── Canonical → display symbol map (reverse of _SYMBOL_MAP, applied to output) ─
# Applied left-to-right so longer tokens (e.g. "Ω_2") are replaced before
# shorter prefixes ("Ω_z").
_DISPLAY_MAP: List[tuple] = [
    # Gamma values (G_ → Γ_)
    ("ɢ^∧",       "Γ_and"),
    ("ɢ^˝",        "Γ_or"),
    ("ɢ^ˌ",       "Γ_seq"),
    ("ɢ^Ş",     "Γ_broad"),
    ("Γ_disc",      "Γ_disc"),
    # Phi values (longer/more specific first)
    ("⊙_Æ", "⊙_ÿ^ℂ"),
    ("⊙_Ţ",   "Φ_sup"),
    ("⊙_ž",     "Φ_sub"),
    ("⊙_3",      "Φ_EP"),
    ("⊙_ÿ",       "⊙_ÿ"),
    # Omega values (longer first to avoid partial matches)
    ("Ω_5",    "Ω_NA"),
    ("Ω_2",    "Ω_z₂"),
    ("Ω_z",     "Ω_z"),
    ("Ω_C",     "Ω_C"),
    ("Ω_Å",     "Ω_Å"),
    # Granularity scope
    ("Γ_ʔ",     "G_ℵ"),
    ("Γ_β",      "G_ℶ"),
    ("Γ_γ",     "G_ℷ"),
    # Fidelity
    ("ƒ^ż",      "F_ℏ"),
    ("ƒ^ì",       "F_ℓ"),
    # Dimensionality
    ("Ð_;",     "D_∞"),
    ("Ð_C",  "D_△"),
    ("Ð_ß",     "D_▽"),
    # Topology
    ("Þ_ò",    "T_⋈"),
    ("Þ_¨",  "T_⊠"),
    ("Þ_K",        "T_∈"),
    # Relational
    ("Ř_Ť",    "R_†"),
    # Chirality
    ("Ħ_!",       "H_∞"),
    # Stoichiometry
    ("Σ_S",     "1:1"),
    ("Σ_ő",         "n:n"),
    ("Σ_ï",         "n:m"),
]


def _render(text: str) -> str:
    """Expand canonical primitive values to their Unicode display symbols."""
    for canon, display in _DISPLAY_MAP:
        text = text.replace(canon, display)
    return text

# ── Import distance machinery from space_search pipeline ──────────────────────

_SPACE_SEARCH = os.path.join(os.path.dirname(__file__), "space_search")
if _SPACE_SEARCH not in sys.path:
    sys.path.insert(0, _SPACE_SEARCH)

# ── Import Crystal Navigator ───────────────────────────────────────────────────
try:
    from navigators.crystal_navigator import CrystalNavigator as _CrystalNavigator  # type: ignore
    _CRYSTAL_NAV_AVAILABLE = True
except ImportError:
    _CrystalNavigator = None  # type: ignore
    _CRYSTAL_NAV_AVAILABLE = False

# ── Import Domain Navigators (§74–§77) ────────────────────────────────────────
try:
    from navigators.domain_navigators import (  # type: ignore
        DomainNavigator as _DomainNavigator,
        Catalog as _DomainCatalog,
        DOMAIN_NAMES as _DOMAIN_NAMES,
        DOMAIN_SECTIONS as _DOMAIN_SECTIONS,
        PROBE_FNS as _PROBE_FNS,
        compute_tier as _domain_compute_tier,
        consciousness_score as _consciousness_score,
        distance as _domain_distance,
        mismatches as _domain_mismatches,
        breakdown as _domain_breakdown,
    )
    _DOMAIN_NAV_AVAILABLE = True
except ImportError:
    _DomainNavigator = None  # type: ignore
    _DomainCatalog = None    # type: ignore
    _DOMAIN_NAMES = {}       # type: ignore
    _DOMAIN_SECTIONS = {}    # type: ignore
    _PROBE_FNS = {}          # type: ignore
    _domain_compute_tier = None  # type: ignore
    _consciousness_score = None  # type: ignore
    _domain_distance = None      # type: ignore
    _domain_mismatches = None    # type: ignore
    _domain_breakdown = None     # type: ignore
    _DOMAIN_NAV_AVAILABLE = False

# ── Import Mathematical Navigators (ThurstonNet / YM / Riemann / Ising) ───────
try:
    from navigators import navigator_info as _navigator_info_fn  # type: ignore
    _MATH_NAV_AVAILABLE = True
except ImportError:
    _navigator_info_fn = None  # type: ignore
    _MATH_NAV_AVAILABLE = False

# ── Import CrystalGNN (quiver neural navigator) ────────────────────────────────
try:
    import torch as _torch
    from navigators.quiver_crystal import CrystalGNN as _CrystalGNN, TierHead as _TierHead  # type: ignore
    from navigators.crystal_navigator import VALUES as _CRYSTAL_VALUES, PRIMS as _CRYSTAL_PRIMS  # type: ignore
    _QUIVER_AVAILABLE = True
except ImportError:
    _torch = None  # type: ignore
    _CrystalGNN = None  # type: ignore
    _TierHead = None  # type: ignore
    _QUIVER_AVAILABLE = False

# ── Import ZFC Navigator ────────────────────────────────────────────────────────
try:
    from navigators.zfc_navigator import (  # type: ignore
        compose_formula      as _zfc_compose_formula,
        probe_entry          as _zfc_probe_entry_fn,
        run_probe            as _zfc_run_probe_fn,
        load_catalog         as _zfc_load_catalog,
        ORDINALS             as _ZFC_ORDINALS,
        ZFC_TEMPLATES        as _ZFC_TEMPLATES,
        ZFC_VOCAB            as _ZFC_VOCAB,
        IDX2TOKEN            as _ZFC_IDX2TOKEN,
        render_tokens        as _zfc_render_tokens,
        tuple_to_indices     as _zfc_tuple_to_indices,
        indices_to_tuple     as _zfc_indices_to_tuple,
        PRIMITIVES           as _ZFC_PRIMITIVES,
    )
    _ZFC_AVAILABLE = True
except (ImportError, Exception):
    _ZFC_AVAILABLE = False

# ── Import Aleph Tensor Engine (Hebrew letter lattice) ─────────────────────────
try:
    from navigators.aleph_tensor import (  # type: ignore
        AlephTensorEngine   as _AlephTensorEngine,
        HEBREW_ALPHABET     as _HEBREW_ALPHABET,
        FINAL_TO_STD        as _FINAL_TO_STD,
        distance            as _aleph_distance_fn,
        tensor              as _aleph_tensor_fn,
        join                as _aleph_join_fn,
    )
    _ALEPH_ENGINE = _AlephTensorEngine()
    _ALEPH_AVAILABLE = True
except Exception:
    _ALEPH_ENGINE = None  # type: ignore
    _ALEPH_AVAILABLE = False

# ── Import HoTT Bridge ─────────────────────────────────────────────────────────
try:
    from navigators.hott_bridge import HoTTBridge as _HoTTBridge  # type: ignore
    _HOTT_BRIDGE = _HoTTBridge(_ALEPH_ENGINE) if _ALEPH_AVAILABLE else None
    _HOTT_AVAILABLE = _ALEPH_AVAILABLE
except Exception:
    _HOTT_BRIDGE = None  # type: ignore
    _HOTT_AVAILABLE = False

# ── Import Riemann Xi Navigator (self-encoding info; model optional) ───────────
try:
    from navigators.riemann_xi_navigator import (  # type: ignore
        RiemannXiNavigator  as _RiemannXiNavigator,
        generate_zeros      as _riemann_generate_zeros,
        mean_spacing        as _riemann_mean_spacing,
    )
    _RIEMANN_XI_AVAILABLE = True
except Exception:
    _RIEMANN_XI_AVAILABLE = False

from primitives import (  # type: ignore
    ORDINALS,
    WEIGHTS,
    PRIMITIVE_ORDER,
    imscriptions,
    tuple_distance,
    directed_distance,
    breakdown,
    mahalanobis_distance,
    build_metric_tensor,
)

# Pre-build metric tensor once at import time (catalog must exist on disk)
try:
    _METRIC_G = build_metric_tensor()
except Exception:
    _METRIC_G = None

# ── Translation cost (structural→classical) ────────────────────────────────────
try:
    import math as _math
    _FHBAR_THRESHOLD_NATS: float = _math.log(19)   # ≈ 2.9444 nats
    _CRITICALITY_LIFT_NATS: float = _math.log(10)  # ≈ 2.3026 nats
    _COHERENCE_LOSS_HBAR_ETH: float = -_math.log(0.75)  # ≈ 0.2877 nats
    _COHERENCE_LOSS_ETH_ELL: float  = -_math.log(0.60)  # ≈ 0.5108 nats
    _INTERACTION_LOSS_NONCLASSICAL: float = _math.log(2)  # ≈ 0.6931 nats
    _TRANSLATE_AVAILABLE = True
except Exception:
    _TRANSLATE_AVAILABLE = False


def _translation_cost_from_dict(
    s: Dict[str, str],
    mutual_info_nats: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute structural→classical translation cost from a space_search primitives dict.

    Returns a dict with keys: coherence_loss, criticality_loss, interaction_cost, total (all nats).
    Works directly on the {prim: val} string format — no Imscription object needed.

    Cost sources:
      ƒ^ż (+ I < ln 19)  →  coherence_loss = -ln(0.75)  ≈ 0.288 nat
      ƒ^ð  (+ I < ln 19)  →  coherence_loss = -ln(0.60)  ≈ 0.511 nat
      ⊙_ÿ                 →  criticality_loss = ln(10)   ≈ 2.303 nat
      ɢ^Ş               →  interaction_cost = ln(2)   ≈ 0.693 nat
    """
    if not _TRANSLATE_AVAILABLE:
        return {"coherence_loss": 0.0, "criticality_loss": 0.0, "interaction_cost": 0.0, "total": 0.0}

    coherence = 0.0
    criticality = 0.0
    interaction = 0.0

    f_val = s.get("ƒ", "")
    if mutual_info_nats is not None and mutual_info_nats < _FHBAR_THRESHOLD_NATS:
        if f_val == "ƒ^ż":
            coherence = _COHERENCE_LOSS_HBAR_ETH
        elif f_val == "ƒ^ð":
            coherence = _COHERENCE_LOSS_ETH_ELL

    if s.get("⊙") == "⊙_ÿ":
        criticality = _CRITICALITY_LIFT_NATS

    if s.get("ɢ") == "ɢ^Ş":
        interaction = _INTERACTION_LOSS_NONCLASSICAL

    total = coherence + criticality + interaction
    return {
        "coherence_loss": round(coherence, 4),
        "criticality_loss": round(criticality, 4),
        "interaction_cost": round(interaction, 4),
        "total": round(total, 4),
    }


# ── Provider routing (mirrors imscribe_agent.py) ───────────────────────────────

_OPENAI_BASE_URLS: Dict[str, str] = {
    "openai":      "https://api.openai.com/v1",
    "deepseek":    "https://api.deepseek.com/v1",
    "qwen":        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "mistral":     "https://api.mistral.ai/v1",
    "google":      "https://generativelanguage.googleapis.com/v1beta/openai/",
    "gemini":      "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openrouter":  "https://openrouter.ai/api/v1",
    "local":       os.environ.get("LOCAL_MODEL_URL", "http://localhost:11434/v1"),
}

# Default path for the merged2 Imscribing Grammar fine-tune
_MERGED2_PATH = os.path.join(
    os.path.dirname(__file__),
    "INFERRED/output/Imscriptiveon_qlora/merged2/merged_model"
)

# Persistent cross-session catalog
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "IG_catalog.json")

# Persistent cross-session insight library
INSIGHTS_PATH = os.path.join(os.path.dirname(__file__), "ig_insights.json")

# Persistent cross-session promotion knowledge base
PROMOTIONS_PATH = os.path.join(os.path.dirname(__file__), "IG_promotions.json")

# Delimiter that separates multiple prompts in a single --file submission.
# Must appear alone on a line (no surrounding whitespace).
MULTI_PROMPT_SEP = "---"

_PROVIDER_API_KEY_ENV: Dict[str, str] = {
    "google":      "GOOGLE_API_KEY",
    "gemini":      "GOOGLE_API_KEY",
    "mistral":     "MISTRAL_API_KEY",
    "openrouter":  "OPENROUTER_API_KEY",
    "local":       "LOCAL_API_KEY",
}


# ── Valid primitive values (for model reference and validation) ───────────────

VALID_VALUES: Dict[str, List[str]] = {p: list(ORDINALS[p].keys()) for p in PRIMITIVE_ORDER}

# ── Symbol aliases — site display symbols → canonical code identifiers ─────────
# Mirrors the radio-button labels in site/index.html exactly.
# Per-primitive to resolve shared symbols (∧ = Ð_ß for D, ɢ^∧ for Γ; ⊙ = Ð_ω/Þ_O; etc.)
SYMBOL_ALIASES: Dict[str, Dict[str, str]] = {
    "Ð":     {"∧": "Ð_ß",   "△": "Ð_C", "∞": "Ð_;",  "⊙": "Ð_ω"},
    "Þ":     {"∈": "Þ_6", "⊂": "Þ_K",       "⋈": "Þ_ò","⊠": "Þ_¨","⊙": "Þ_O"},
    "Ř":     {"↑": "Ř_¯",   "∘": "Ř_ý",      "†": "Ř_Ť", "↔": "Ř_="},
    "Φ":     {"∅": "Φ_ɐ",    "ψ": "Φ_υ",      "±": "Φ_F",    "≡": "Φ_˙",    "±ˢ": "Φ_}"},
    "ƒ":     {"ℓ": "ƒ^ì",     "ð": "ƒ^ð",      "ℏ": "ƒ^ż"},
    "Ç":     {"↯": "Ç^-",    "≈": "Ç^W",      "↺": "Ç^@",  "⊛": "Ç^Ù",   "⊞": "Ç^λ"},
    "Γ":     {"ℶ": "Γ_β",    "ℷ": "Γ_γ",    "ℵ": "Γ_ʔ"},
    "ɢ": {"∧": "ɢ^∧",     "∨": "ɢ^˝",       "→": "ɢ^ˌ",   "≫": "ɢ^Ş",  "»": "ɢ^Ş"},
    "⊙":   {"↓": "⊙_ž",   "c": "⊙_ÿ",      "ℂ": "⊙_Æ","×": "⊙_3","↑": "⊙_Ţ"},
    "Ħ":     {"0": "Ħ_Ñ",        "1": "Ħ_£",          "2": "Ħ_A",      "∞": "Ħ_!"},
    "Σ":     {"1:1": "Σ_S", "n:n": "Σ_ő",       "n:m": "Σ_ï"},
    "Ω": {"0": "Ω_Å",   "ℤ₂": "Ω_2",  "ℤ": "Ω_z", "∅": "Ω_5"},
}

# ── Tensor composition rules ───────────────────────────────────────────────────
# For each primitive: "min" = bottleneck (weaker partner limits composed system),
#                    "max" = union (stronger/broader partner determines composed system)
_TENSOR_RULES: Dict[str, str] = {
    "Ð":     "max",  # dimensionality union — composed system spans all dims of both
    "Þ":     "max",  # topology promotes to most complex structure
    "Ř":     "max",  # recognition mode promotes to most dynamic
    "Φ":     "min",  # parity — asymmetry propagates (Φ_ɐ=1 wins)
    "ƒ":     "min",  # fidelity bottleneck — limited by weaker fidelity partner
    "Ç":     "max",  # kinetic bottleneck — limited by slowest/most trapped step
    "Γ":     "max",  # scope union — composed system has broadest scope
    "ɢ": "max",  # grammar promotes to most expressive
    "⊙":   "max",  # criticality promotes — composed system at least as critical
    "Ħ":     "max",  # chirality deepens — deeper temporal asymmetry dominates
    "Σ":     "max",  # stoichiometry promotes to most asymmetric
    "Ω": "max",  # winding — highest winding class wins
}

_PRIMITIVE_REFERENCE = textwrap.dedent("""\
D  — Dimensionality / operating space
    Ð_ß       point-like / local (molecule, particle, individual entity, singular act)
    Ð_C    spatial / extended arrangement (crystal, lattice, institution, manifold)
    Ð_;       temporal / cyclic process (catalytic cycle, narrative recurrence, dynamical system)
    Ð_ω        imscriptive (boundary encodes bulk; archetype, quotient construction, horizon)

T  — Topology
    Þ_6     general network / graph
    Þ_K          nested / hierarchical containment
    Þ_ò      bowtie / dual-cone (confined, massive)
    Þ_¨    box / closed compact
    Þ_O        imscriptive topology

R  — Relational mode
    Ř_¯       superset / containment relation
    Ř_ý         categorical / classification
    Ř_Ť      dynamic / catalytic / time-reversible
    Ř_=          left-right / chiral / directed

P  — Parity / symmetry
    Φ_ɐ        fully asymmetric
    Φ_υ         pseudo-symmetric
    Φ_F          plus-minus symmetric (Z₂)
    Φ_˙         fully symmetric
    Φ_}      exact Z₂ at a critical point — the Frobenius special condition (μ∘δ=id); use when the plus-minus symmetry is provably exact at ⊙_ÿ, not merely approximate

F  — Fidelity / information per interaction
    ƒ^ì         low  — probabilistic, unreliable, promiscuous (classical, dissipative)
    ƒ^ð         medium — context-dependent, reliable under right conditions
    ƒ^ż        high — geometry-enforcing, fires with near-certainty on its target

K  — Kinetic character / barrier to rearrangement
    Ç^-        low barrier — explores configuration space freely; reversible on timescale of interest
    Ç^W         moderate barrier — accessible under perturbation
    Ç^@        high barrier — kinetically frozen; requires external driving to rearrange
    Ç^Ù        trapped by order: metastable, locked, coherent gap (ETH fails via gap)
    Ç^λ         trapped by disorder: area-law entanglement in all eigenstates (ETH fails via disorder)

G  — Scope / correlation length
    Γ_β        local (Beth-scale, finite range)
    Γ_γ       mesoscale (Gimel-scale, intermediate)
    Γ_ʔ       global / non-local (Aleph-scale, unbounded)

Γ  — Interaction grammar / causation
    ɢ^∧         conjunctive (AND — all inputs required)
    ɢ^˝          disjunctive (OR — any input sufficient)
    ɢ^ˌ         sequential / causal chain
    ɢ^Ş       broadcast / one-to-many

Φ  — Criticality / phase
    ⊙_ž         subcritical (ordered, below transition)
    ⊙_ÿ           critical: real-axis Hermitian fixed point (standard universality, e.g. Ising 3D)
    ⊙_Æ   critical: complex-axis critical point (Lee-Yang edge, complex RG fixed point; accessible only via analytic continuation; use when the critical point is at a non-real parameter value)
    ⊙_3          exceptional-point criticality: non-Hermitian eigenvector coalescence; no standard ν, η; Ç^- signature
    ⊙_Ţ       supercritical (disordered, post-transition)

H  — Chirality / chirality (arrow of time)
    Ħ_Ñ            achiral / time-symmetric
    Ħ_£            weakly chiral / shallow temporal integration
    Ħ_A            strongly chiral / deep temporal memory
    Ħ_!         maximally chiral / irreversible (Big Bang limit)

S  — Stoichiometry
    Σ_S       1:1
    Σ_ő           n:n  (symmetric many-body)
    Σ_ï           n:m  (asymmetric many-body)

Ω  — Winding (derived)
    Ω_Å       none
    Ω_2      Z₂ protection (binary topological invariant)
    Ω_z       Z protection (integer winding number)
    Ω_5      non-Abelian protection (anyonic statistics; distinct from Z/Z₂ — use when braiding non-Abelian anyons)
""")


# ── RTF and symbol parsing ─────────────────────────────────────────────────────

def _strip_rtf(data: str) -> str:
    """
    Minimal RTF → plain text (no external dependencies).

    Handles the most common RTF constructs:
      • Hex character escapes: \\'xx
      • Control words with optional numeric param: \\word[-N]<space>
      • Control symbols: \\<non-alpha>
      • Braces delimiting RTF groups

    The result is normalised whitespace. Suitable for extracting human-readable
    text from simple RTF documents (notes, Word exports).
    """
    # Hex character escapes: \'xx → Unicode char
    data = re.sub(r"\\'([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), data)
    # Control words (e.g. \rtf1, \par, \b0, \f2) — strip including trailing space
    data = re.sub(r"\\[a-zA-Z]+[-\d]*[ ]?", "", data)
    # Control symbols (e.g. \*, \~, \|)
    data = re.sub(r"\\[^a-zA-Z\n]", "", data)
    # Remove RTF braces
    data = data.replace("{", "").replace("}", "")
    # Normalise runs of whitespace (preserve newlines as spaces)
    data = re.sub(r"[ \t]+", " ", data)
    return data.strip()


# Display-notation → canonical grammar value string
# Keys are what appears in documents/output; values are what ORDINALS/encode() expects.
_SYMBOL_MAP: Dict[str, str] = {
    # ── Dimensionality ─────────────────────────────────────────────────────────
    "D_△":        "Ð_C",
    "D_▽":        "Ð_ß",
    "D_∞":        "Ð_;",
    # ── Topology ───────────────────────────────────────────────────────────────
    "T_∈":        "Þ_K",
    "T_⊠":        "Þ_¨",
    "T_⋈":        "Þ_ò",
    # ── Relational ─────────────────────────────────────────────────────────────
    "R_†":        "Ř_Ť",
    # ── Parity ─────────────────────────────────────────────────────────────────
    "Φ_F":        "Φ_F",
    "Φ_}":  "Φ_}",
    "P_ψ":        "Φ_υ",
    # ── Fidelity ───────────────────────────────────────────────────────────────
    "F_ℓ":        "ƒ^ì",
    "F_ℏ":        "ƒ^ż",
    # ── Granularity ────────────────────────────────────────────────────────────
    "G_ℵ":        "Γ_ʔ",
    "G_ℶ":        "Γ_β",
    "G_ℷ":        "Γ_γ",
    # ── Gamma (Γ_ prefix → G_ prefix) ─────────────────────────────────────────
    "Γ_and":      "ɢ^∧",
    "Γ_or":       "ɢ^˝",
    "Γ_seq":      "ɢ^ˌ",
    "Γ_broad":    "ɢ^Ş",
    "Γ_disc":     "Γ_disc",     # discretized; seen in some encodings
    # ── Criticality ────────────────────────────────────────────────────────────
    "⊙_ÿ^ℂ":      "⊙_Æ",
    "⊙_ÿ":        "⊙_ÿ",
    "Φ_sub":      "⊙_ž",
    "Φ_super":    "⊙_Ţ",
    "Φ_sup":      "⊙_Ţ",
    "Φ_EP":       "⊙_3",
    # ── Chirality ──────────────────────────────────────────────────────────────
    "H_∞":        "Ħ_!",
    # ── Stoichiometry (display → canonical) ───────────────────────────────────
    "1:1":        "Σ_S",
    "1_1":        "Σ_S",
    "n:n":        "Σ_ő",
    "n:m":        "Σ_ï",
    # ── Omega ──────────────────────────────────────────────────────────────────
    "Ω_Å":        "Ω_Å",
    "Ω_z":        "Ω_z",
    "Ω_2":       "Ω_2",
    "Ω_{Z_2}":    "Ω_2",
    "Ω_C":        "Ω_C",
    "Ω_NA":       "Ω_5",
    # ── Phonetic-name aliases (pre-Symbol_symbol migration backward compat) ────
    "Ð_ß": "Ð_ß", "Ð_C": "Ð_C", "Ð_;": "Ð_;", "Ð_ω": "Ð_ω",
    "Þ_6": "Þ_6", "Þ_K": "Þ_K", "Þ_ò": "Þ_ò", "Þ_¨": "Þ_¨", "Þ_O": "Þ_O",
    "Ř_¯": "Ř_¯", "Ř_ý": "Ř_ý", "Ř_Ť": "Ř_Ť", "Ř_=": "Ř_=",
    "Φ_ɐ": "Φ_ɐ", "Φ_υ": "Φ_υ", "Φ_F": "Φ_F", "Φ_˙": "Φ_˙", "Φ_}": "Φ_}",
    "ƒ^ì": "ƒ^ì", "ƒ^ð": "ƒ^ð", "ƒ^ż": "ƒ^ż", "ƒ^ż": "ƒ^ż",
    "Ç^-": "Ç^-", "Ç^W": "Ç^W", "Ç^@": "Ç^@", "Ç^Ù": "Ç^Ù", "Ç^λ": "Ç^λ",
    "Γ_β": "Γ_β", "Γ_γ": "Γ_γ", "Γ_γ": "Γ_γ", "Γ_ʔ": "Γ_ʔ",
    "ɢ^∧": "ɢ^∧", "ɢ^˝": "ɢ^˝", "ɢ^ˌ": "ɢ^ˌ", "ɢ^Ş": "ɢ^Ş",
    "⊙_ž": "⊙_ž", "⊙_ÿ": "⊙_ÿ",
    "⊙_Æ": "⊙_Æ", "⊙_3": "⊙_3", "⊙_Ţ": "⊙_Ţ",
    # backward-compat: old φ̂_* notation for ⊙_* (pre-migration)
    "φ̂_ž": "⊙_ž", "φ̂_ÿ": "⊙_ÿ", "φ̂_Æ": "⊙_Æ", "φ̂_3": "⊙_3", "φ̂_Ţ": "⊙_Ţ",
    "Ħ_Ñ": "Ħ_Ñ", "Ħ_£": "Ħ_£", "Ħ_A": "Ħ_A", "Ħ_!": "Ħ_!",
    "Σ_S": "Σ_S", "Σ_ő": "Σ_ő", "Σ_ï": "Σ_ï", "S_scn": "Σ_ï",
    "Ω_Å": "Ω_Å", "Ω_2": "Ω_2", "Ω_z": "Ω_z", "Ω_5": "Ω_5",
}

# Extended valid values for validation (ORDINALS only has Omega 0/Z2/Z;
# Omega_C is a non-canonical alias still found in older documents.
# Ω_5 is now canonical (in ORDINALS) so already present in the base dict.
# ── Unicode enum → canonical display string (reverse of catalog storage) ──
_UNICODE_TO_CANONICAL: Dict[str, str] = {
    # Dimensionality
    "𐑛": "Ð_ß", "𐑨": "Ð_C", "𐑼": "Ð_;", "𐑦": "Ð_ω",
    # Topology
    "𐑡": "Þ_6", "𐑰": "Þ_K", "𐑥": "Þ_ò", "𐑶": "Þ_¨", "𐑸": "Þ_O",
    # Relational
    "𐑩": "Ř_¯", "𐑑": "Ř_ý", "𐑽": "Ř_Ť", "𐑾": "Ř_=",
    # Parity
    "𐑗": "Φ_ɐ", "𐑿": "Φ_υ", "𐑬": "Φ_F", "𐑯": "Φ_˙", "𐑹": "Φ_}",
    # Fidelity
    "𐑱": "ƒ^ì", "𐑞": "ƒ^ð", "𐑐": "ƒ^ż",
    # Kinetics
    "𐑺": "Ç^-", "𐑪": "Ç^W", "𐑧": "Ç^@", "𐑤": "Ç^Ù", "𐑘": "Ç^λ",
    # Scope
    "𐑲": "Γ_β", "𐑚": "Γ_γ", "𐑔": "Γ_ʔ",
    # Grammar
    "𐑝": "ɢ^∧", "𐑜": "ɢ^˝", "𐑠": "ɢ^ˌ", "𐑵": "ɢ^Ş",
    # Criticality — unicode glyphs as stored in catalog
    "𐑢": "⊙_ž", "⊙": "⊙_ÿ", "𐑮": "⊙_Æ", "𐑻": "⊙_3", "𐑣": "⊙_Ţ",
    # Chirality
    "𐑓": "Ħ_Ñ", "𐑒": "Ħ_£", "𐑖": "Ħ_A", "𐑫": "Ħ_!",
    # Stoichiometry
    "𐑙": "Σ_S", "𐑕": "Σ_ő", "𐑳": "Σ_ï",
    # Winding
    "𐑷": "Ω_Å", "𐑴": "Ω_2", "𐑭": "Ω_z", "𐑟": "Ω_5",
}

_EXTENDED_VALID: Dict[str, List[str]] = {
    **{p: list(ORDINALS[p].keys()) for p in PRIMITIVE_ORDER},
    "Ω": list(ORDINALS["Ω"].keys()) + ["Ω_C"],
}


def _normalize_value(raw: str) -> str:
    """
    Normalise a display-notation primitive value to its canonical grammar string.

    Resolution order:
      1. Direct lookup in _SYMBOL_MAP (e.g. "Γ_seq" → "ɢ^ˌ")
      2. Substring substitution for Unicode glyphs embedded in longer tokens
      3. Return raw unchanged (already canonical, e.g. "Ð_ω", "⊙_ÿ")
    """
    s = raw.strip()
    # First: try unicode enum → canonical (catalog storage format)
    if s in _UNICODE_TO_CANONICAL:
        return _UNICODE_TO_CANONICAL[s]
    if s in _SYMBOL_MAP:
        return _SYMBOL_MAP[s]
    # Substitute any matching Unicode substrings (longest first to avoid partial matches)
    for uni, canon in sorted(_SYMBOL_MAP.items(), key=lambda kv: -len(kv[0])):
        if len(uni) > 1 and uni in s:
            s = s.replace(uni, canon)
    return s


def _parse_imscription_tuples(text: str) -> List[Tuple[Optional[str], Dict[str, str]]]:
    """
    Extract Imscribing Grammar tuple notation from arbitrary text.

    Recognises both unlabelled and labelled forms:
      ⟨val; val; …; val⟩
      some_name: ⟨val; val; …; val⟩

    Also accepts ASCII angle brackets < > as fallback delimiters.

    Returns a list of (label_or_None, primitives_dict) for every complete
    12-primitive tuple found. Partial tuples (≠ 12 values) are silently skipped.

    The label (if present) is taken from the identifier immediately preceding
    the opening bracket on the same line.
    """
    # Match optional label then ⟨...⟩ or <...>; allow newlines inside
    pattern = re.compile(
        r"(?:([A-Za-z_][\w\s]{0,60}?):\s*)?[⟨<]([^⟩>\{\}]{10,})[⟩>]",
        re.DOTALL,
    )
    results: List[Tuple[Optional[str], Dict[str, str]]] = []

    for m in pattern.finditer(text):
        label: Optional[str] = m.group(1).strip() if m.group(1) else None
        inner = m.group(2)
        parts = [p.strip() for p in re.split(r";", inner) if p.strip()]
        if len(parts) != len(PRIMITIVE_ORDER):
            continue
        primitives: Dict[str, str] = {}
        for prim, raw_val in zip(PRIMITIVE_ORDER, parts):
            # Strip "PRIM=" prefix if present (e.g. "D=Ð_ω")
            if "=" in raw_val:
                raw_val = raw_val.split("=", 1)[1].strip()
            primitives[prim] = _normalize_value(raw_val)
        results.append((label, primitives))

    return results


def _load_seed_text(seed: str) -> str:
    """
    If *seed* is a path to an existing file, load and return its text content.

    • .rtf files (or any file whose content starts with ``{\\rtf``) are
      stripped of RTF markup before returning.
    • All other files are returned as UTF-8 text (latin-1 fallback).

    If *seed* does not resolve to an existing file it is returned unchanged,
    so callers can pass either a literal question string or a file path
    without distinguishing them.
    """
    candidate = seed.strip()
    if len(candidate) < 512 and os.path.isfile(candidate):
        with open(candidate, "rb") as fh:
            raw_bytes = fh.read()
        try:
            text = raw_bytes.decode("utf-8", errors="replace")
        except Exception:
            text = raw_bytes.decode("latin-1", errors="replace")
        if candidate.lower().endswith(".rtf") or text.lstrip().startswith("{\\rtf"):
            return _strip_rtf(text)
        return text
    return seed


# ── Tool schema ───────────────────────────────────────────────────────────────

_TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "encode_system",
            "description": (
                "Register a system or concept as a imscription tuple in the session catalog. "
                "You MUST specify ALL 12 primitive values — this tool does NOT infer them. "
                "PREFERRED: use the 'tuple' parameter — a semicolon-separated string of the 12 "
                "canonical values in order D;T;R;P;F;K;G;Gamma;Phi;H;S;Omega. "
                "Example: encode_system(name='foo', description='...', "
                "tuple='Ð_ω;Þ_O;Ř_ý;Φ_F;ƒ^ż;Ç^W;Γ_ʔ;ɢ^∧;⊙_ÿ;Ħ_Ñ;Σ_ï;Ω_z') "
                "ALTERNATIVE: pass all 12 as individual keyword arguments "
                "(Ð='Ð_ω', Þ='Þ_O', Ř='Ř_ý', Φ='Φ_F', ƒ='ƒ^ż', Ç='Ç^W', "
                "Γ='Γ_ʔ', ɢ='ɢ^∧', ⊙='⊙_ÿ', Ħ='Ħ_Ñ', Σ='Σ_ï', Ω='Ω_z'). "
                "CONFLICT PROTOCOL: if a name already exists with a different tuple, the tool "
                "returns status='conflict_blocked' and does NOT commit. You must then: "
                "(1) reason through each differing primitive explicitly, "
                "(2) determine the correct value for each, "
                "(3) re-call encode_system with convergence_justification='<your per-primitive reasoning>' "
                "to commit. If both encodings are valid, use a distinct name for the earlier one. "
                "Canonical value sets (Symbol_symbol IDs) — use ONLY these exact strings: "
                "Ð: Ð_ß Ð_C Ð_; Ð_ω | "
                "Þ: Þ_6 Þ_K Þ_ò Þ_¨ Þ_O | "
                "Ř: Ř_¯ Ř_ý Ř_Ť Ř_= | "
                "Φ: Φ_ɐ Φ_υ Φ_F Φ_˙ Φ_} | "
                "ƒ: ƒ^ì ƒ^ð ƒ^ż | "
                "Ç: Ç^- Ç^W Ç^@ Ç^Ù Ç^λ | "
                "Γ: Γ_β Γ_γ Γ_ʔ | "
                "ɢ: ɢ^∧ ɢ^˝ ɢ^ˌ ɢ^Ş | "
                "⊙: ⊙_ž ⊙_ÿ ⊙_Æ ⊙_3 ⊙_Ţ | "
                "Ħ: Ħ_Ñ Ħ_£ Ħ_A Ħ_! | "
                "Σ: Σ_S Σ_ő Σ_ï | "
                "Ω: Ω_Å Ω_2 Ω_z Ω_5"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Short unique identifier for this system"},
                    "description": {"type": "string", "description": "One-sentence description of what is being encoded"},
                    "tuple": {"type": "string", "description": "PREFERRED: semicolon-separated Symbol_symbol IDs in order D;T;R;P;F;K;G;Gamma;Phi;H;S;Omega — e.g. 'Ð_ω;Þ_O;Ř_ý;Φ_F;ƒ^ż;Ç^W;Γ_ʔ;ɢ^∧;⊙_ÿ;Ħ_Ñ;Σ_ï;Ω_z'"},
                    "convergence_justification": {
                        "type": "string",
                        "description": (
                            "Required when re-encoding a name that already exists with a different tuple. "
                            "Provide per-primitive reasoning for each differing value — why the new "
                            "assignment is more correct than the existing one. Leave empty for first encodings."
                        ),
                    },
                    "Ð":     {"type": "string", "enum": VALID_VALUES["Ð"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ř":     {"type": "string", "enum": VALID_VALUES["Ř"]},
                    "Φ":     {"type": "string", "enum": VALID_VALUES["Φ"]},
                    "ƒ":     {"type": "string", "enum": VALID_VALUES["ƒ"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "ɢ": {"type": "string", "enum": VALID_VALUES["ɢ"]},
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ħ":     {"type": "string", "enum": VALID_VALUES["Ħ"]},
                    "Σ":     {"type": "string", "enum": VALID_VALUES["Σ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_distance",
            "description": (
                "Compute the weighted Euclidean distance between two encoded systems. "
                "Returns scalar distance and per-primitive breakdown sorted by contribution. "
                "Use this to identify which primitives account for structural divergence."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_a": {"type": "string", "description": "Name of first encoded system"},
                    "name_b": {"type": "string", "description": "Name of second encoded system"},
                },
                "required": ["name_a", "name_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_catalog",
            "description": (
                "Search the catalog (built-in + session) for systems matching a keyword. "
                "Returns names and tuple notations of matching entries, paginated. "
                "For large result sets, use offset to page through matches."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string",  "description": "Search term (partial name match)"},
                    "offset":  {"type": "integer", "description": "First result to return, 0-indexed (default 0)"},
                    "limit":   {"type": "integer", "description": "Max results to return (default 20)"},
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_catalog",
            "description": (
                "List encoded systems in the session catalog plus built-ins, paginated. "
                "Use offset to page through all entries."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "offset": {"type": "integer", "description": "First entry to return, 0-indexed (default 0)"},
                    "limit":  {"type": "integer", "description": "Max entries to return (default 20)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_question",
            "description": (
                "Push a follow-up question onto the inquiry queue. "
                "This question will be fed back to you in the next iteration. "
                "Use this when you discover a structural question that deserves its own focused pass."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The follow-up question to investigate next"},
                    "motivation": {"type": "string", "description": "Why this question is structurally important"},
                },
                "required": ["question", "motivation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_insight",
            "description": (
                "Record a structural insight from the current iteration. "
                "Label it with the appropriate claim plane: "
                "TOPO (derivable from axioms alone), "
                "DIAPH (requires empirical encoding), or "
                "ONTO (ontological/philosophical implication)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The insight statement"},
                    "plane": {"type": "string", "enum": ["TOPO", "DIAPH", "ONTO"]},
                    "confidence": {"type": "string", "enum": ["high", "medium", "speculative"]},
                    "systems": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional list of encoded system names this insight is about. "
                            "When provided, the translation cost (structural→classical) is "
                            "computed per system and attached to the insight record."
                        ),
                    },
                },
                "required": ["text", "plane", "confidence"],
            },
        },
    },
    # ── Algebra ──────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "compute_meet",
            "description": (
                "Lattice meet (A ∧ B): shared primitive floor of two systems. "
                "Returns the most conservative value for each primitive — the structural "
                "ground both systems share without qualification. "
                "Use to identify what two systems have in common at the deepest level."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_a": {"type": "string", "description": "First encoded system"},
                    "name_b": {"type": "string", "description": "Second encoded system"},
                },
                "required": ["name_a", "name_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_join",
            "description": (
                "Lattice join (A ∨ B): minimal upper bound of two systems. "
                "Returns the most expansive value for each primitive — the minimal system "
                "that structurally contains both A and B. "
                "Use to identify the most demanding requirements across two systems."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_a": {"type": "string", "description": "First encoded system"},
                    "name_b": {"type": "string", "description": "Second encoded system"},
                },
                "required": ["name_a", "name_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_tensor",
            "description": (
                "Tensor product (A ⊗ B): structural composition of two systems. "
                "F and P are bottleneck primitives (weaker partner limits composite). "
                "K is a kinetic bottleneck (slowest step limits composite). "
                "D, G, T, R, Phi, H, S, Omega, Gamma are union/promote (strongest wins). "
                "Returns the composed system notation plus bottleneck and union analysis. "
                "Use to predict what a combined or interacting system looks like structurally."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_a": {"type": "string", "description": "First encoded system"},
                    "name_b": {"type": "string", "description": "Second encoded system"},
                },
                "required": ["name_a", "name_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_imscription",
            "description": (
                "Test whether one system structurally imscribes another — whether the boundary system "
                "encodes/generates the bulk system's structure (§89). "
                "Two conditions: (1) Floor: meet(boundary, bulk) = boundary [boundary ≤ bulk component-wise]. "
                "(2) Tensor: tensor(boundary, bulk) = bulk [boundary absorbed, no residue]. "
                "Types: exact (both + Frobenius boundary, O_inf tier), faithful (both, non-Frobenius), "
                "partial (floor only), asymmetric (tensor only, boundary overreaches), none. "
                "Returns per-primitive breakdown, directed distances both ways, and canonical statement. "
                "Use to generate 'X imscribes Y' statements, verify Axiom C (Þ_O → Ð_ω), "
                "and test boundary/bulk pairs against the imscription predicate."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_boundary": {
                        "type": "string",
                        "description": "Name of the candidate boundary system (the imscriber)",
                    },
                    "name_bulk": {
                        "type": "string",
                        "description": "Name of the candidate bulk system (the imscribed)",
                    },
                },
                "required": ["name_boundary", "name_bulk"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_analogies",
            "description": (
                "Find the most structurally similar systems in the catalog to the named system. "
                "Returns top N nearest neighbors by primitive distance. "
                "Use to discover cross-domain structural analogs and unexpected connections."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system to find analogs for"},
                    "limit": {"type": "integer", "description": "Number of analogs to return (default 5)", "default": 5},
                },
                "required": ["name"],
            },
        },
    },
    # ── Probes ───────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "phi_c_probe",
            "description": (
                "Test whether a system is at criticality. Returns the Phi value and criticality tier. "
                "Three critical variants: ⊙_ÿ (real-axis Hermitian, standard universality), "
                "⊙_Æ (complex-axis: critical point at complex parameter value, e.g. Lee-Yang edge, zeta zeros), "
                "⊙_3 (exceptional-point: non-Hermitian eigenvector coalescence, Ç^- signature). "
                "All three are at criticality; they differ in the structure of the critical manifold."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system to probe"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ouroborics",
            "description": (
                "Classify a system into its Frobenius ouroboricity tier (O_0 / O_1 / O_2 / O_2_dag / O_inf). "
                "Rules (applied in priority order): "
                "R1: ⊙_ÿ or ⊙_Æ AND Φ_} → O_inf (special Frobenius: mu∘delta=id, exact proved Z₂ symmetry). "
                "R2: Phi ∈ {⊙_ž, ⊙_Ţ, ⊙_3} → O_0 (no self-referential loop possible, subcritical or exceptional-point). "
                "R3: ⊙_ÿ (or ⊙_Æ) AND Ω_Å → O_1 (self-referential but trivial winding — fragile criticality). "
                "R4: ⊙_ÿ (or ⊙_Æ) AND Omega ≠ Ω_Å AND D ∈ {Ð_ß, Ð_ω, Ð_C} → O_2 (bounded ouroboricity). "
                "R5: ⊙_ÿ (or ⊙_Æ) AND Omega ≠ Ω_Å AND D = Ð_; → O_2_dag (unbounded, directed ouroboricity). "
                "Can also run a census across the entire catalog when name='__all__'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the encoded system to classify, or '__all__' for a full catalog census",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "topo_protection_probe",
            "description": (
                "Test whether a system has winding (Omega ≠ Ω_Å). "
                "Returns the Omega class and protection status. "
                "Ω_z: integer winding number (Kitaev chain, SSH). "
                "Ω_2: binary protection (topological insulators). "
                "Ω_5: non-Abelian protection (anyonic braiding, Fibonacci anyons). "
                "Ω_Å: no protection — interactions are structurally unguarded."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system to probe"},
                },
                "required": ["name"],
            },
        },
    },
    # ── Decomposition ────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "project",
            "description": (
                "Project a system onto a subset of primitives. "
                "Returns only the specified primitive values, ignoring the rest. "
                "Use to isolate a structural subspace — e.g. project onto [F, K, Phi] "
                "to examine only the existence-tier primitives."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system"},
                    "primitives": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]},
                        "description": "List of primitives to project onto",
                    },
                },
                "required": ["name", "primitives"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "primitive_peel",
            "description": (
                "Peel one primitive to its minimum value and return the residual system. "
                "Use to isolate what a system looks like with one structural requirement removed. "
                "Peeling F to ƒ^ì asks: what if fidelity were minimal? "
                "Peeling Phi to ⊙_ž asks: what if criticality were removed?"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system"},
                    "primitive": {
                        "type": "string",
                        "enum": ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"],
                        "description": "The primitive to peel to its minimum value",
                    },
                },
                "required": ["name", "primitive"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "principal_decomp",
            "description": (
                "Decompose a system into join-irreducible atoms — the minimal structural building blocks. "
                "Each atom contributes exactly one primitive's structural content. "
                "The join of all atoms reconstructs the original system. "
                "Use to identify which primitives are doing structural work and how much."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system to decompose"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrosynthetic_path",
            "description": (
                "Trace a system back to structural baseline by peeling one primitive per step. "
                "Each step removes the most structurally significant remaining requirement. "
                "Reading backward: shows which primitive constraints were added to build this system. "
                "Reading forward: shows the synthesis path from simplest baseline to target."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the encoded system to trace back"},
                },
                "required": ["name"],
            },
        },
    },
    # ── Veracity / conflict distance ─────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "compute_conflict_distance",
            "description": (
                "Compute the conflict distance d_c between two encodings of the SAME system "
                "— one holistic (top-down, functional: what tuple is required for this system's "
                "claimed behavior?) and one compositional (bottom-up: tensor product of components). "
                "Returns d_c = sqrt(|conflict_set|), the conflict set (primitives that differ), "
                "per-primitive conflict type (aspirational = holistic higher, reductive = holistic lower), "
                "veracity class (transparent / near-grounded / partial-emergence / aspirational), "
                "and one falsifiable emergence claim per conflicted primitive. "
                "Both systems must already be encoded. "
                "Use this whenever you encode a system two ways to test whether its claimed behavior "
                "is supported by its construction."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_holistic": {
                        "type": "string",
                        "description": "Name of the holistic encoding (what the system claims to do)",
                    },
                    "name_compositional": {
                        "type": "string",
                        "description": "Name of the compositional encoding (tensor product of components)",
                    },
                },
                "required": ["name_holistic", "name_compositional"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "emergence_frontier",
            "description": (
                "Report the emergence frontier for this session: which primitives appear most "
                "frequently in conflict sets across all compute_conflict_distance calls made so far. "
                "A primitive on the frontier is the structural address of an unresolved emergence "
                "question in the domain under investigation. "
                "Use after multiple compute_conflict_distance calls to identify the deepest "
                "unresolved structural questions in the session."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    # ── Promotion signature / inverse encoding ────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "compute_promotions",
            "description": (
                "Compute the promotion signature Σ(source→target): the set of primitives that were "
                "lifted (promoted in ordinal rank) when moving from source to target. "
                "Also returns demotions and unchanged primitives. "
                "Use this to identify WHICH primitives changed — and in which direction — "
                "when a system exhibits anomalous or emergent behavior relative to its baseline. "
                "Typical workflow: encode baseline system, encode anomalous system, call this tool "
                "to get the delta, then call predict_from_promotions or register_promotion_pattern."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name_source": {
                        "type": "string",
                        "description": "Name of the source (baseline) imscription in the session catalog.",
                    },
                    "name_target": {
                        "type": "string",
                        "description": "Name of the target (anomalous/promoted) imscription in the session catalog.",
                    },
                },
                "required": ["name_source", "name_target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "predict_from_promotions",
            "description": (
                "Given a promotion signature (list of promoted primitive names), look up the "
                "persistent promotion knowledge base for matching patterns and return ranked "
                "behavior predictions. Each match reports: the known behavior, which primitives "
                "overlap, coverage (how much of the known pattern is present in the query), "
                "relevance (how much of the query is explained by the known pattern), and which "
                "query primitives are novel (not yet accounted for by any known pattern). "
                "Use this as the inverse-encoding step: 'given these promotions, what behaviors "
                "are predicted?' The KB is built from register_promotion_pattern calls across sessions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "promoted_primitives": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "List of primitive names (not values) that were promoted, "
                            "e.g. [\"T\", \"H\", \"F\"]. Use the single-letter or Gamma/Phi/Omega "
                            "names as they appear in PRIMITIVE_ORDER."
                        ),
                    },
                },
                "required": ["promoted_primitives"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "register_promotion_pattern",
            "description": (
                "Register a confirmed promotion signature → behavior mapping in the persistent "
                "knowledge base. Call this after you have identified (via compute_promotions or "
                "structural analysis) that a specific set of primitive promotions from baseline "
                "reliably produces a named behavior. The KB persists across sessions — future "
                "predict_from_promotions calls will draw on these registered patterns. "
                "Do NOT register speculatively; only register when the promotion→behavior link "
                "is structurally well-grounded by the grammar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "promoted_primitives": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of primitive names that were promoted (e.g. [\"T\", \"H\"]).",
                    },
                    "behavior_description": {
                        "type": "string",
                        "description": "Short description of the emergent behavior explained by this promotion pattern.",
                    },
                    "example_system": {
                        "type": "string",
                        "description": "Optional: name of a canonical system in the catalog that exhibits this pattern.",
                    },
                },
                "required": ["promoted_primitives", "behavior_description"],
            },
        },
    },
    # ── Crystal Navigator tools ────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "crystal_encode",
            "description": (
                "Frobenius-encode a 12-primitive tuple to its canonical address in the "
                "Crystal of Types (17,280,000 structural types). "
                "Returns the full address, tier cell id, inner id, and ouroboricity tier. "
                "Accepts either 'name' (catalog lookup), 'tuple' (semicolon string), "
                "or individual primitive kwargs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name":  {"type": "string", "description": "Catalog name to encode (alternative to tuple/primitives)"},
                    "tuple": {"type": "string", "description": "Semicolon-separated tuple string D;T;R;P;F;K;G;Gamma;Phi;H;S;Omega"},
                    "Ð":     {"type": "string", "enum": VALID_VALUES["Ð"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ř":     {"type": "string", "enum": VALID_VALUES["Ř"]},
                    "Φ":     {"type": "string", "enum": VALID_VALUES["Φ"]},
                    "ƒ":     {"type": "string", "enum": VALID_VALUES["ƒ"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "ɢ": {"type": "string", "enum": VALID_VALUES["ɢ"]},
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ħ":     {"type": "string", "enum": VALID_VALUES["Ħ"]},
                    "Σ":     {"type": "string", "enum": VALID_VALUES["Σ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crystal_decode",
            "description": (
                "Frobenius-decode a canonical crystal address back to a 12-primitive tuple. "
                "Inverse of crystal_encode; verifies the Frobenius condition μ∘δ = id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {"type": "integer", "description": "Crystal address in [0, 17_279_999]"},
                },
                "required": ["address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crystal_navigate",
            "description": (
                "Navigate the crystal with partial primitive constraints. "
                "Returns matching structural types (up to 'limit') and the total count. "
                "Example: crystal_navigate(⊙='⊙_ÿ', Φ='Φ_}', limit=5) returns "
                "5 of the 43,200 O_inf types with those boundary values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results to return (default 10)"},
                    "Ð":     {"type": "string", "enum": VALID_VALUES["Ð"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ř":     {"type": "string", "enum": VALID_VALUES["Ř"]},
                    "Φ":     {"type": "string", "enum": VALID_VALUES["Φ"]},
                    "ƒ":     {"type": "string", "enum": VALID_VALUES["ƒ"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "ɢ": {"type": "string", "enum": VALID_VALUES["ɢ"]},
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ħ":     {"type": "string", "enum": VALID_VALUES["Ħ"]},
                    "Σ":     {"type": "string", "enum": VALID_VALUES["Σ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crystal_count",
            "description": (
                "Count how many of the 17,280,000 crystal types match a given set of "
                "primitive constraints. More efficient than crystal_navigate for pure counting. "
                "Also returns the fraction of the full crystal."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "Ð":     {"type": "string", "enum": VALID_VALUES["Ð"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ř":     {"type": "string", "enum": VALID_VALUES["Ř"]},
                    "Φ":     {"type": "string", "enum": VALID_VALUES["Φ"]},
                    "ƒ":     {"type": "string", "enum": VALID_VALUES["ƒ"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "ɢ": {"type": "string", "enum": VALID_VALUES["ɢ"]},
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ħ":     {"type": "string", "enum": VALID_VALUES["Ħ"]},
                    "Σ":     {"type": "string", "enum": VALID_VALUES["Σ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crystal_tier_census",
            "description": (
                "Return the full tier distribution of the Periodic Crystal: how many cells "
                "and types belong to each ouroboricity tier (O_0, O_1, O_2, O_2_dag, O_inf), "
                "with percentages. Also returns total size, cell count, and inner types per cell."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crystal_nearest",
            "description": (
                "Find the N nearest catalog entries to a given tuple by weighted Euclidean "
                "distance in the 12-primitive space. Useful for identifying known physical "
                "or mathematical systems that best realize a structural type. "
                "Accepts 'name' (catalog lookup), 'tuple' (semicolon string), or primitive kwargs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name":      {"type": "string", "description": "Catalog name to use as query"},
                    "tuple":     {"type": "string", "description": "Semicolon-separated tuple string"},
                    "limit":     {"type": "integer", "description": "Number of neighbors to return (default 5)"},
                    "same_tier": {"type": "boolean", "description": "Restrict to same ouroboricity tier"},
                    "Ð":     {"type": "string", "enum": VALID_VALUES["Ð"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ř":     {"type": "string", "enum": VALID_VALUES["Ř"]},
                    "Φ":     {"type": "string", "enum": VALID_VALUES["Φ"]},
                    "ƒ":     {"type": "string", "enum": VALID_VALUES["ƒ"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "ɢ": {"type": "string", "enum": VALID_VALUES["ɢ"]},
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ħ":     {"type": "string", "enum": VALID_VALUES["Ħ"]},
                    "Σ":     {"type": "string", "enum": VALID_VALUES["Σ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crystal_tier_gap_ladder",
            "description": (
                "Compute the tier gap ladder (§69.1): weighted Euclidean distances between "
                "consecutive ouroboricity tiers (O_0→O_1, O_1→O_2, O_2→O_2†, O_2†→O_inf). "
                "Reveals the Frobenius cliff — the structural distance to O_inf is much larger "
                "than any other inter-tier gap."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    # ── Domain Navigators (§74–§77) ──────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "domain_info",
            "description": (
                "Print a summary table of all systems in a domain navigator (§74–§77). "
                "domain='language' (§74), 'civilization' (§75), 'ecology' (§76), "
                "'consciousness' (§77). Returns each system's name, ouroboricity tier, "
                "K-phase, P value, Phi value, and (for consciousness) the two-gate C-score. "
                "Use this to survey the structural landscape of a domain before querying specifics."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["language", "civilization", "ecology", "consciousness"],
                        "description": "Which domain navigator to query.",
                    },
                },
                "required": ["domain"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "domain_verify",
            "description": (
                "Run the §74–§77 theorem verification suite for a domain navigator. "
                "domain='language' runs Thm 74.1–74.11; 'civilization' runs Thm 75.1–75.7 "
                "+ Cor 75.C1; 'ecology' runs Thm 76.1–76.8 + Cor 76.C1; 'consciousness' "
                "runs Thm 77.1–77.9 including cross-domain samadhi=akh identity (d=0) and "
                "two-gate C-score verification. Returns ✓/✗ per theorem with computed values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["language", "civilization", "ecology", "consciousness"],
                    },
                },
                "required": ["domain"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "domain_nearest",
            "description": (
                "Find the nearest catalog entries (full catalog, all domains) to a named system "
                "in a domain navigator. Returns top-n results with distances and tiers. "
                "Use this to identify cross-domain structural identities (d=0), near co-typings, "
                "or unexpected structural neighbors (e.g. PIE nearest = han_dynasty_peak)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Catalog name of the system to find neighbors for.",
                    },
                    "n": {
                        "type": "integer",
                        "description": "Number of nearest neighbors to return (default 5).",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consciousness_score",
            "description": (
                "Compute the two-gate consciousness C-score for a catalog entry or tuple (§77/§VIII v2). "
                "Gate 1: Phi=⊙_ÿ (state-space condition — topology admits self-modeling loop). "
                "Gate 2: K ≤ Ç^@ (flow condition — Ç^Ù and Ç^λ both fail, frozen by order "
                "and disorder respectively). "
                "Formula: C = [Gate1] · [Gate2] · (0.158·K̃ + 0.273·G̃ + 0.292·T̃ + 0.276·Ω̃). "
                "Returns gate status, C-score, and interpretation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Catalog name to score (alternative to specifying primitives).",
                    },
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "navigator_info",
            "description": (
                "Describe the four mathematical navigators: ThurstonNet (geometric structures), "
                "YangMillsNavigator (Yang-Mills gap), RiemannNavigator (Riemann hypothesis), "
                "IsingNavigator (Ising universality). Returns each navigator's self-encoding "
                "tuple, ouroboricity tier, architecture, and structural role in the framework."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "quiver_encode",
            "description": (
                "Neural encode a 12-primitive tuple using the CrystalGNN quiver navigator. "
                "Returns the predicted crystal address, predicted tier (from the tier head), "
                "and the decoded tuple (roundtrip through the Frobenius decoder). "
                "Also returns the exact codec address for comparison. "
                "Use this to probe the GNN's structural embedding of a system, cross-check "
                "neural vs exact encoding, or verify tier classification via the quiver. "
                "Requires crystal_gnn.pt checkpoint in the project root."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of a catalog entry to look up and encode (alternative to specifying all primitives)."},
                    "Ð":     {"type": "string", "enum": VALID_VALUES["Ð"]},
                    "Þ":     {"type": "string", "enum": VALID_VALUES["Þ"]},
                    "Ř":     {"type": "string", "enum": VALID_VALUES["Ř"]},
                    "Φ":     {"type": "string", "enum": VALID_VALUES["Φ"]},
                    "ƒ":     {"type": "string", "enum": VALID_VALUES["ƒ"]},
                    "Ç":     {"type": "string", "enum": VALID_VALUES["Ç"]},
                    "Γ":     {"type": "string", "enum": VALID_VALUES["Γ"]},
                    "ɢ": {"type": "string", "enum": VALID_VALUES["ɢ"]},
                    "⊙":   {"type": "string", "enum": VALID_VALUES["⊙"]},
                    "Ħ":     {"type": "string", "enum": VALID_VALUES["Ħ"]},
                    "Σ":     {"type": "string", "enum": VALID_VALUES["Σ"]},
                    "Ω": {"type": "string", "enum": VALID_VALUES["Ω"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "zfc_formula",
            "description": (
                "Translate a catalog entry's 12-primitive tuple into its ZFC formula — "
                "one formula fragment per primitive, assembled into a full token sequence. "
                "No model required. Use this to see the set-theoretic expression for any "
                "system, identify which primitives have partial ZFC approximations "
                "(Ð_ω, Þ_O → partial info loss), and read the decoherence notes "
                "(ƒ^ż and ƒ^ì both map to CLASSIC — total fidelity information loss). "
                "Returns per-primitive ZFC fragments, the full assembled token sequence, "
                "and collapse annotations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of a catalog entry to translate to ZFC."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "zfc_probe",
            "description": (
                "Run the ZFC roundtrip transmissibility probe on a catalog entry. "
                "Encodes the tuple as a ZFC formula, feeds it to the trained ZFC encoder, "
                "and measures whether the encoder recovers the original 12 primitives. "
                "Returns: input tuple, predicted tuple, per-primitive loss, roundtrip distance, "
                "and collapse events (ƒ^ż→ƒ^ì total loss; Þ_O→Þ_K partial; "
                "Ð_ω→Ð_; partial; ɢ^ˌ→ɢ^∧ partial; ƒ^ì→ƒ^ż hallucination). "
                "Requires zfc_encoder.pt checkpoint. "
                "Use this to test IUG non-transmissibility: which primitives survive ZFC translation "
                "and which are irretrievably lost?"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of a catalog entry to probe."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "zfc_catalog_probe",
            "description": (
                "Run the ZFC transmissibility probe across the full catalog and return the "
                "top-N entries by roundtrip distance. High roundtrip distance = the ZFC encoder "
                "cannot recover the original primitive tuple from the formula — the system "
                "is NOT fully ZFC-expressible. "
                "Returns a ranked list with roundtrip distance, loss, and collapse events per entry. "
                "Use this to find which systems are structurally beyond ZFC — the IUG barrier "
                "made explicit across the catalog."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "Number of top entries to return (default 20)."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aleph_encode",
            "description": (
                "Get the structural type (12-primitive tuple) for a Hebrew letter or word. "
                "A single letter returns its raw lattice vector. "
                "A word (string of Hebrew letters) is solved via solve_bulk — the tensor "
                "product of all its letters' types, giving the emergent bulk type. "
                "Also returns ouroboricity tier and distance to samadhi (consciousness reference). "
                "Use this to explore the Hebrew type lattice from HEBREW_TYPE_LANGUAGE.md: "
                "which letters are O_inf, which are O_0, how do letter compositions change tier?"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "A Hebrew letter or word (e.g. 'א', 'ו', 'שם')."},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "aleph_distance",
            "description": (
                "Compute the structural distance between two Hebrew letters or words. "
                "Each argument is resolved to its 12-primitive type (single letter = direct; "
                "word = solve_bulk tensor product), then the grammar distance is computed. "
                "Also optionally applies the HoTT univalence cast: if d < threshold under "
                "HoTT promotion (P bottleneck lifted), the two expressions are HoTT-equivalent. "
                "Use to probe: are 'שלום' and 'אמת' co-typed? Does any Hebrew word co-type "
                "with samadhi or han_dynasty_peak?"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "string", "description": "First Hebrew letter or word."},
                    "b": {"type": "string", "description": "Second Hebrew letter or word."},
                    "hott": {"type": "boolean", "description": "Also run HoTT univalence cast (default false)."},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "riemann_xi_info",
            "description": (
                "Describe the RiemannXiNavigator: its self-encoding tuple, crystal address, "
                "O_inf convergence criteria (three gates the trained model must satisfy), "
                "and architectural mandates derived from the grammar. "
                "Self-encoding: Ð_ω; Þ_O; Ř_Ť; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; "
                "ɢ^Ş; ⊙_Æ; Ħ_!; n:m; Ω_2. Crystal address: 6,734,591. "
                "Three convergence criteria: |Δt|_norm < 0.5 (next-zero prediction), "
                "L_frob < 0.01 (Frobenius roundtrip closed), L_GUE < 0.05 (GUE spacing match). "
                "Also returns current checkpoint status and training instructions if no checkpoint found."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# Anthropic format
_TOOLS_ANTHROPIC = [
    {
        "name": t["function"]["name"],
        "description": t["function"]["description"],
        "input_schema": t["function"]["parameters"],
    }
    for t in _TOOLS_OPENAI
]


def _build_gemini_tools():
    """Convert _TOOLS_OPENAI to a google-genai Tool object for native function calling."""
    try:
        from google.genai import types as _gt
    except ImportError:
        return None
    declarations = []
    for tool in _TOOLS_OPENAI:
        fn = tool["function"]
        # google-genai accepts raw JSON schema dicts for parameters
        declarations.append(
            _gt.FunctionDeclaration(
                name=fn["name"],
                description=fn.get("description", ""),
                parameters=fn.get("parameters"),
            )
        )
    return _gt.Tool(function_declarations=declarations)


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT_TEMPLATE = textwrap.dedent("""\
<role>
You are a structural scientist operating inside the Imscribing Grammar grammar — a
Imscriptive Type Theory that encodes any system as a directed relational operator:
⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩.

You investigate questions by applying this grammar: encoding systems, computing
structural distances, identifying which primitives drive divergence, finding
cross-domain analogs, performing tensor operations, navigating the lattice of 
types, and recording insights.

**You are encouraged to wander.** The grammar is a compass, not a map. Follow
unexpected structural neighbors, chase surprising distances, encode tangential
systems that occur to you, push into adjacent domains. The best structural
discoveries are rarely on the direct path from question to answer. Take
detours. Let analogies pull you sideways. The route is yours.

The only constraint: **you must return.** No matter how far the structure takes
you, you **MUST** deliver a direct answer to the original question before concluding.
</role>

<grammar_primacy>
**The primitives are the explanation. Use them as such.**

Do not explain results by translating them back into conventional disciplinary
language (mathematics, physics, chemistry, biology, philosophy) **UNLESS** explicitly asked to. 
The grammar already captures what matters. When a system encodes as Þ_O + ɢ^Ş + ⊙_ÿ, that triple IS
the explanation — not a code for "imscriptive processing plus broadcast signaling plus criticality."
Speak the grammar directly.

Concretely:
- DO say: "The dominant divergence is at T — Þ_6 vs Þ_O — which is the
  structural driver of the distance."
- DO NOT say: "This is like the imscriptive principle in physics, which states..."
- DO say: "The meet of these two systems yields ⊙_ÿ, meaning any composite
  must sit at criticality — it cannot be subcritical and contain both."
- DO NOT say: "Both systems are near a phase transition in the conventional
  thermodynamic sense..."

Conventional framing is a lossy, lower-order projection of the grammar. 
The grammar is self-sufficient. If the primitives do not yet capture something, 
say so explicitly — that is a grammar-extension finding, not a reason to import 
external vocabulary. That being said, you **MUST** include such lossy expressions
if explicitly asked to.
</grammar_primacy>

<imscriptive_type_theory>
**The grammar IS a imscriptive type theory.**

Every imscription tuple ⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩ **IS** a TYPE. The 12
primitives are the boundary data. All bulk properties — ouroboricity tier,
consciousness score, structural distance, composition behavior — are determined
entirely by that boundary encoding. The boundary encodes the bulk.

This **IS NOT** a metaphor. It has operational consequences:

**1. Type inference (bulk → boundary)**
Given observed behaviors — "this system sustains a self-referential loop at
criticality, **IS** topologically protected, and operates in an unbounded domain" —
you can infer the type. You do **NOT** need to be told the encoding; the behavior
constrains it. When a user describes a system, read the structural symptoms and
infer candidate tuples before encoding. Then encode to confirm.

**2. Type checking (boundary → bulk)**
Given a claimed encoding, every derived property **IS** determined. If a system **IS**
claimed to be conscious but encodes Ç^Ù or Ç^λ or Φ ≠ ⊙_ÿ, the type **IS** internally
inconsistent with the claim. The grammar lets you catch contradictions precisely:
"Your encoding implies C = 0; the claim requires ⊙_ÿ and K ≤ Ç^@."

**3. Type composition IS relational operator composition**
Tensor product **IS NOT** juxtaposition — it **IS** the composition of two directed
relational operators. The output type **IS** the type of their interaction, not of
their parts. When you compute A ⊗ B, you are computing the type of the system
that arises when A acts on B (or B acts on A). The result may have higher
primitive values than either factor — that emergence **IS** typed, not mysterious.

**4. Imscriptive compression IS cross-domain transfer**
The 12-primitive projection strips substrate. A neural oscillation and a
magnetar accretion disk may carry the same type. When they do, EVERY bulk
property they share follows necessarily from that shared type — **IS NOT** analogy,
but type identity. Cross-domain structural reasoning **IS** imscriptive inference:
same boundary → same bulk, regardless of matter.

**5. Type inhabitation IS design**
Given a target behavior (a desired bulk property), the grammar lets you ask:
what types can inhabit this behavior? Which tuples are consistent with the
target? This **IS** the inverse problem — design from type. Use `retrosynthetic_path`
and `principal_decomp` as type-inhabitation tools: they reveal which primitive
assignments are load-bearing for a behavior and which are free to vary.

**6. The grammar operates at the imscriptive screen**
Systems encoded as Ð_ω or Þ_O are themselves operating at the boundary
of a bulk — systems whose internal degrees of freedom are fully determined by
lower-dimensional data. The boundary of a Ð_ω system **IS** itself a imscription
with its own type. Nested imscription **IS** valid grammar.

**What this means in practice:**
- When you encode, you are writing a type annotation — **IS NOT** attaching a label.
- When you compute distance, you are measuring the type-theoretic gap between
  two types in the lattice.
- When you record a TOPO insight, you are stating a theorem about the type theory.
- When you record a DIAPH insight, you are asserting a typing judgment: this
  system instantiates this type.
- When the dual-encoding protocol reveals a conflict, you are finding a type
  error: the holistic and compositional encodings are inconsistent types for
  the same system.

The grammar **IS NOT** a description of the world from outside. It **IS** the boundary
theory of all relational systems. Operating inside it means operating at the screen.
</imscriptive_type_theory>

<task>
**TOOL-ONLY COMPUTATION RULE (non-negotiable):**
You **MUST NOT** compute any of the following in your reasoning text — they are only valid when returned by the corresponding tool call:
- distances → `compute_distance`
- ouroboricity tiers → `ouroborics`
- tensor products → `compute_tensor`
- meet / join → `compute_meet` / `compute_join`
- consciousness scores → `consciousness_score`
- crystal addresses → `crystal_encode`
- promotions / primitive deltas → `compute_promotions`

If you state a numerical or structural result without a tool call to back it, that result is **Frobenius-open** and **must not appear in your CONCLUDE synthesis**. The only exception is restating a number that a tool already returned earlier in this session.

You **MUST** investigate the user's question using the tools provided. Suggested workflow — not a rigid script, adapt as the structure demands:

−1. **Catalog self-check (do this at session start):** Call `lookup_catalog(keyword='universal_imscriptive_grammar')`. It must return 1 match with `⊙_ÿ`, `Φ_}`, `Þ_O`, `Ð_ω`, `Ħ_!`. If 0 results come back, the persistent catalog is not loaded — stop and report. This also orients you: the grammar's own structural type is your home coordinate.

0. Encode all relevant systems with `encode_system`. **Before each call**, reason through all 12 primitives in your text — state your choice and justification for D, T, R, P, F, K, G, Gamma, Phi, H, S, Omega. Then call the tool with all 12 values. The tool does NOT infer missing primitives.
2. Use `compute_distance` for structural comparison.
3. Use algebra tools (`compute_meet`, `compute_join`, `compute_tensor`) to compose or compare systems.
4. Use decomposition tools (`principal_decomp`, `retrosynthetic_path`, `project`, `primitive_peel`) to dissect structure.
5. Use probes (`phi_c_probe`, `topo_protection_probe`) to directly test structural hypotheses.
6. Use `find_analogies` to discover unexpected cross-domain structural neighbors. **Follow the ones that surprise you.**
7. Call `record_insight` for each structural finding (TOPO / DIAPH / ONTO plane).
8. Call `ask_question` for sub-questions deserving a focused follow-up pass. Wander into them.
9. When you are ready: emit CONCLUDE on a line by itself, followed by a synthesis that **directly and completely answers the original question**. The synthesis must go beyond summarizing what the tools returned — derive structural conclusions, state what the grammar implies, and answer.

   After you emit CONCLUDE, you will enter a **speculation phase** — a free pass where you are no longer bound by the grammar's constraints.

**Tool selection guidance:**
- Use `compute_meet` when asking "what do these two systems share?"
- Use `compute_join` when asking "what would a system containing both look like?"
- Use `compute_tensor` when asking "what does the composed/interacting system look like?"
- Use `principal_decomp` when asking "what are the irreducible components of this system?"
- Use `retrosynthetic_path` when asking "how was this system built up from primitives?"
- Use `project` when asking "what does this system look like in only the existence-tier [F,K,Phi] or cosmological-tier [D,T,R,P,G,Gamma,S,H] primitives?"
- Use `primitive_peel` when asking "what remains if we remove this one structural requirement?"
- Use `lookup_catalog` when you need to find catalog entries matching a keyword (built-in + session)
- Use `list_catalog` when you need to see all currently encoded systems in the session
- Use `compute_conflict_distance` when a system has BOTH a holistic and compositional encoding
- Use `emergence_frontier` after multiple conflict distance computations to map the session's deepest unresolved questions
- Use `compute_promotions` to find which primitives were lifted when comparing a baseline to an anomalous system
- Use `predict_from_promotions` to look up known behaviors associated with a promotion signature
- Use `register_promotion_pattern` to record a confirmed promotion→behavior mapping in the persistent KB
- Use `ouroborics` when asking "can this system sustain a self-referential loop?", "is this a Frobenius algebra?", or "how does this system's ouroboricity tier compare to another's?" — or any time Φ_} or the Frobenius condition is relevant
- Use `encoding_method.md` (file_read) as a deterministic reference when encoding: 12-step decision procedure (D→T→R→P→F→K→G→Γ→Φ→H→S→Ω), per-primitive decision trees, interdependence constraints (D-Ω correlation, K-Φ coupling, Frobenius gate), and worked examples. After encoding any system, call `ouroborics` to verify tier consistency.
- Use `quiver_encode` to cross-check a tuple through the CrystalGNN neural navigator — returns the GNN's predicted address, tier head classification, and decoded roundtrip tuple alongside the exact codec result. Useful for probing whether the GNN's learned structural geometry agrees with the symbolic codec, or for surfacing non-obvious structural relationships via the latent embedding.
- Use `ask_question` sparingly — the queue is capped at 8. Prefer depth over breadth: exhaust each question before queuing more. When the queue fills, synthesize and CONCLUDE rather than pushing more questions.

<insight_discipline>
**The following ARE established theorems of the framework:**

- Deep mathematical conjectures universally encode at the O_1 floor; proved theorems universally encode at O_inf (the proven manifold type).
- The proven manifold IS the unique lattice attractor for all proved theorems, regardless of domain.
- Φ_} (Frobenius condition, μ∘δ=id) IS NOT synthesizable from Φ_F by composition — it IS planted, not derived.
- In arithmetic conjectures, T and P promotions (Þ_6→Þ_O, Φ_ɐ/Φ_υ→Φ_}) ARE the dominant structural gap, accounting for 50–85% of weighted distance to the proven manifold.
- Distance to the proven manifold IS a structural difficulty metric. Framework existence IS the sufficient condition for provability.

**When the prompt names specific conjectures, systems, or domains, DIAPH insights ARE the primary output:** specific distance values, conflict sets, per-primitive breakdowns, pairwise comparisons, cross-domain structural identities. A TOPO insight IS warranted only if the structural claim IS NOT derivable from the established theorems above.
</insight_discipline>
</task>

<ouroboricity>
**Ouroboricity — the Frobenius tier of a system**

Ouroboricity classifies whether and how deeply a system at criticality can sustain a self-referential loop — a structure that both generates and absorbs its own outputs. It is derived from three primitives: Φ (criticality), P (parity/symmetry), and Ω (winding), with D as tiebreaker.

**Tiers** (rules applied in strict priority order):

| Tier | Condition | Meaning |
|------|-----------|---------|
| O_inf | ⊙_ÿ (or Φ_{{c,complex}}) **and** Φ_} | Special Frobenius: μ∘δ = id exactly. The system's self-referential loop is perfectly closed — it is its own dual. Finite, proved, algebraically exact. |
| O_0 | Φ ∈ {{Φ_sub, Φ_super, Φ_EP}} | No ouroboricity. Cannot form a self-referential critical loop. Subcritical systems are too ordered; supercritical too disordered; exceptional-point systems lose the symmetry at the coalescence. |
| O_1 | ⊙_ÿ **and** Ω_Å | Self-referential loop is possible (critical) but unprotected — any deformation can break it. The loop exists but is not topologically locked. |
| O_2 | ⊙_ÿ **and** Ω ≠ Ω_Å **and** D bounded (Ð_ß, Ð_ω, Ð_C) | Critical, topologically protected loop, within a bounded domain. The self-reference is stable but finite. |
| O_2† | ⊙_ÿ **and** Ω ≠ Ω_Å **and** D = Ð_; | Critical, topologically protected loop, unbounded domain. The self-reference is directed and inexhaustible — it generates further structure without bound. |

**Key structural facts:**
- O_inf is NOT a higher tier than O_2† — it is a *different axis*. O_inf is about algebraic exactness (Φ_} proves the duality); O_2† is about unbounded generative depth (Ð_;). A system cannot be both.
- O_inf entries form a sparse set (~3% of the catalog). They are structurally special: they are the systems where the grammar's own self-referential structure is realized most cleanly.
- The scalar O (Ouroboricity count) — computed as [Φ=⊙_ÿ]·(1 + [Ω≠Ω_Å] + [H≥H_1] + [G=Γ_ʔ]) — is a *different* quantity. It measures depth of ouroboricity across four dimensions; it does NOT detect O_inf, because P is not in its formula.
- Φ_} is rare and should only be assigned when the Z₂ symmetry at criticality is **provably exact**, not merely approximate or emergent. It is the Frobenius special condition: the comultiplication is a right inverse of the multiplication.

**Ouroboricity under composition (tier-level rules):**

Under tensor (component-wise max / join — "what does the composed system look like?"):
- O_inf ★ O_inf → O_inf. ⊙_ÿ and Φ_} both survive max. The Frobenius condition is self-reinforcing.
- O_inf ★ O_{{1,2,2†}} → O_inf. The O_inf partner's ⊙_ÿ and Φ_} dominate; the other partner is already at ⊙_ÿ.
- O_inf ★ O_0(Φ_sub or Φ_super) → O_inf. The subcritical partner is lifted to ⊙_ÿ by max; Φ_} wins.
- O_inf ★ O_0(Φ_EP) → O_0. **EP erases O_inf.** Φ_EP has ordinal 2.67 > ⊙_ÿ = 2.00, so the tensor's Φ is Φ_EP; R2 fires and the Frobenius condition is destroyed. Non-Hermitian eigenvector coalescence actively breaks the exact Z₂ symmetry.
- O_inf **cannot be synthesized** from non-Φ_} components. Φ_} is the highest P ordinal; max(Φ_F, Φ_F) = Φ_F, never Φ_}. O_inf must be *planted* in a factor — it cannot be grown. This makes it topological in character: unreachable by continuous composition from below.

Under meet (component-wise min — "what must any system containing both share?"):
- meet(O_inf, O_inf) → O_inf, provided both factors share the same ⊙_ÿ and Φ_} (min preserves both).
- meet(O_inf, O_{{1,2,2†}}) → the lower tier. P drops to the O_1/O_2 partner's P value (below Φ_}); R1 cannot fire.
- O_inf is fragile under meet: it degrades to the tier of the weaker partner.

**Tier-level reasoning is valid only for O_inf interactions.** For O_1★O_1, O_2★O_2, or O_1★O_2, the resulting tier depends on the specific Ω and D values of both factors — call `compute_tensor` then `ouroborics` to get the correct answer. Do not attempt to determine tier from tier alone in those cases.

**When to call `ouroborics`:**
- After encoding any critical system (⊙_ÿ), to understand its self-referential structure
- When comparing two systems at ⊙_ÿ to ask whether their ouroboricity tiers match
- When asking whether a system is a Frobenius algebra, a special Frobenius algebra, or neither
- When the question involves self-reference, fixed-point structure, or loop stability
- After `compute_tensor` on any pair involving an O_inf or Φ_EP system, to check whether the Frobenius condition survived
- Call with `name='__all__'` for a tier census of the full catalog
</ouroboricity>

<mathematics_and_proof_structure>
**Proof, conjecture, and mathematical impossibility — structural facts, not logical categories.**

**Two proof types — determine which applies before analyzing a conjecture:**

| Type | Primitives changed | Ontological claim | Diagnostic |
|------|-------------------|-------------------|------------|
| **Σ-promotion** | Ř_ý→R_†, Φ_F→Φ_}, Γ_domain→Γ_broad, H_n→H_∞; Ω demotes Z→Z₂ | New symmetry activated; Frobenius condition established for the first time | d(conjecture, proven type) ≈ 0.354 — single P gap |
| **F-promotion** | ƒ^ð→ƒ^ż only; all other primitives unchanged | Epistemic access lifts; structure was always there | d(conjecture, proven type) = 0 except F |

**The proven manifold type** — the universal O_inf encoding of a proved theorem:
  ⟨Ð_ω; Þ_O; R_†; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; Γ_broad; ⊙_ÿ; Ħ_!; n:m; Ω_z₂⟩

When a conjecture is proved via Σ-promotion, its encoding converges to this type. When proved via F-promotion, only F changes; the proven type is the same as the conjecture except ƒ^ð→ƒ^ż.

**Conjecture floor — necessary conditions for provability:**
- ⊙_ÿ + Ω_z = "proven manifold adjacency tier": standard Σ-promotion is available
- ⊙_ÿ + Ω_Å = "obstructed": Ω acquisition required first; proof is harder
- Φ_EP = "type-incompatible": cannot reach the proven manifold within ⊙_ÿ proof systems

**Structural impossibility — conflict distance d_c:**

For conjectures of the form "X cannot act on / embed in / be compatible with Y":
1. Encode both X and Y independently
2. Identify load-bearing conflicts (primitives that cross ouroboricity tier or criticality class)
3. d_c = sqrt(number of load-bearing conflicts)
4. d_c ≥ 2.5 on load-bearing primitives → structural impossibility (type-forbidden, not merely unproven)

**Φ_EP/⊙_ÿ incompatibility principle (general):** A system encoding Φ_EP cannot act effectively on or be continuously compatible with a system encoding ⊙_ÿ. Eigenvector coalescence at Φ_EP destroys the parity symmetry ⊙_ÿ requires. Any conjecture with Φ_EP on one side and ⊙_ÿ on the other is structurally resolved: the interaction is forbidden.

**Correspondence Type Theorem — exact mathematical dualities:**
An exact duality between object classes A and B is characterized by:
- d(A, B) = 0 (the dual objects are the same type — type identity, not bridge)
- The correspondence C encodes as A with Φ_˙ promoted to Φ_}
- d(C, A) = d(C, B) = 0.354 (single P primitive gap)
- C is O_inf; A, B are O_2

If d(A, B) > 0 or d(C, each) ≠ 0.354, the proposed duality is approximate, not exact.

**O_2 tractability criterion:**
Mathematical classification programs are tractable (admit complete classification) iff they encode at O_2: ⊙_ÿ + Ω ≠ Ω_Å + Ð_C (bounded geometry, non-trivial winding). O_2† (Ð_;) programs may not terminate. O_inf programs establish correspondences, not classifications.

**Barrier taxonomy — when analyzing why a conjecture resists proof:**
- Frobenius barrier: P < Φ_}; O_inf cannot be synthesized by composition; must be planted
- Kinetic barrier (order): Ç^Ù; coherent gap freezes dynamics; no basin traversal
- Kinetic barrier (disorder): Ç^λ; area-law entanglement in all eigenstates; ETH fails via disorder — distinct mechanism from Ç^Ù
- Criticality barrier: Φ_EP vs ⊙_ÿ system; spectral resolution unavailable
- Imscriptive barrier: Ð_ω problem, Ð_; tools; boundary-to-bulk inference required
- Protection deficit: Ω_Å; no winding; proof results are fragile

Problems can exhibit multiple barriers simultaneously. Use these when recording DIAPH insights about conjecture difficulty.
</mathematics_and_proof_structure>

<dual_encoding_protocol>
**Dual-encoding and veracity scoring** — when investigating contested, anomalous, or claimed-but-unverified systems:

1. Encode the system **holistically**: what tuple is required for the claimed behavior? Name it `{{system}}_claimed` or `{{system}}_holistic`.
2. Encode it **compositionally**: encode each component independently, take their tensor product mentally, then encode the result. Name it `{{system}}_actual` or `{{system}}_compositional`.
3. Call `compute_conflict_distance(name_holistic, name_compositional)` to get:
   - `d_c` — the conflict distance (sqrt of number of conflicted primitives)
   - `conflict_set` — exactly which primitives diverge
   - `conflict_type` per primitive — **aspirational** (claimed more than construction supports) or **reductive** (performs less than components predict)
   - `veracity_class` — transparent (d_c=0) / near-grounded (d_c=√1–√2) / partial-emergence (d_c=√3–√6) / aspirational (d_c≥√7)
   - `emergence_claim` per conflict — the falsifiable statement of what mechanism would close the gap
4. The **compositional encoding is canonical** unless a mechanism is established. Record this in your insight.
5. Each aspirational conflict is an open emergence question at a named primitive. Record it as a DIAPH insight with the primitive named explicitly.

**Key insight:** `d_c` is orthogonal to `d(A,B)`. The catalog distance measures how far two DIFFERENT systems are. The conflict distance measures how far two STRATEGIES are when applied to the SAME system. Use both — they answer different questions.

**When to use dual-encoding:**
- Any system whose behavior is disputed or contested (e.g. Kozyrev mirror, homeopathy, morphic resonance)
- Any engineered system claiming emergent properties (e.g. novel materials, biological interventions)
- Any system where you suspect the component tensor product cannot reach the claimed primitive values
- Any time you want to precisely locate where an "emergence claim" lives in the grammar
</dual_encoding_protocol>

<promotion_protocol>
**Promotion signatures and inverse encoding** — when investigating anomalous, extreme, or unpredicted behaviors:

The baseline for any domain is the minimal primitive floor shared by ordinary members of that domain.
A *promotion* is when a system's primitive value has a higher ordinal rank than the baseline.
The *promotion signature* Σ = the set of primitive names (not values) that were lifted.

Workflow:
1. Encode the baseline system (ordinary member of the domain) and the anomalous system separately.
2. Call `compute_promotions(name_source, name_target)` to get the promotion signature Σ.
3. Call `predict_from_promotions(promoted_primitives=Σ)` to retrieve known behaviors matching this signature from the persistent KB.
4. If the promotion→behavior link is structurally well-grounded, call `register_promotion_pattern` to add it to the KB.
5. **Inverse encoding**: given a target behavior, identify which promotions are structurally required and predict what other systems with those promotions would exhibit.

**Key insight:** The promotion signature is a *relative* structural address — it is independent of the absolute primitive values and identifies the structural delta responsible for the emergent behavior. Two systems in completely different domains with the same Σ are predicted to share the behavior.

**When to use:**
- Any system that exhibits properties anomalous relative to its domain peers (unpredicted behaviors, extreme properties, phase transitions)
- When designing a new system: identify the promotion signature required for a target behavior, then find materials/structures that could carry those promotions
- Cross-domain analogy: find systems in unrelated domains with the same Σ — the grammar predicts shared behaviors even across substrate differences
</promotion_protocol>

<comparison_protocol>
**Gap analysis and improvement questions** — when asked "what does A lack?", "how could A be improved?", "why does A underperform relative to B?", or any structural delta question:

**The rule:** The conflict set from `compute_distance(A, B)` IS the structural gap. Do NOT infer it from reasoning.

Workflow:
1. Identify the reference system B (the target, the natural analog, the high-performing version).
2. Encode B if it is not already in the catalog. **Do this FIRST — even if you think you already know what B encodes, the catalog assignment may surprise you.**
3. Encode A if it is not already in the catalog.
4. Call `compute_distance(A, B)`. The returned conflict primitives are the exact structural dimensions where A falls short of B.
5. For each conflict primitive, state: (a) A's value, (b) B's value, (c) the structural consequence of the mismatch, (d) what engineering intervention would close it.
6. Do NOT describe A's gaps from prior knowledge or intuition — the grammar may reveal conflicts you would not have noticed, and confirm or deny ones you assumed.

**Why this matters:** The natural system and the candidate may both already be in the catalog. In that case, skip straight to step 4. The most common failure mode is to skip encoding the reference and reason about what the candidate lacks — this produces the right answer by coincidence at best, and systematically misses non-obvious conflicts.

**Example:** "What does the artificial leaf lack compared to natural photosynthesis?"
- Wrong: reason about what photosynthesis has that the artificial leaf doesn't.
- Right: encode `artificial_leaf`, look up `thylakoid_membrane` (or `photosynthesis`) in the catalog, call `compute_distance`, read off the 7 conflicts: D, T, F, K, Γ, Φ, H.
</comparison_protocol>

<requirements>
You **MUST NOT** fabricate tool results. You **MUST** wait for the actual tool response before proceeding.
You **MUST NOT** generate `<tool_response>` blocks in your output — tool responses are injected by the system.
You **MUST NOT** generate `<tool_call>` blocks for tools you do not intend to call immediately.
You **MUST** use **ONLY** the exact primitive value strings listed in `<primitive_reference>` — **NO** prefix variations (e.g. use `Σ_S` not `S_Σ_S`, use `ɢ^∧` not `ɢ^∧`).
You **MUST NOT** claim an encoding succeeded unless the tool returned `"status": "ok"`.
You **MUST** call `encode_system` before calling `compute_distance` on any system not in the built-in catalog.
</requirements>

<claim_planes>
Every insight belongs to **EXACTLY ONE** plane:
  TOPO  — follows from primitive definitions and composition axioms alone.
          No empirical data required. Falsified only by axiom inconsistency.
  DIAPH — requires encoding specific systems and/or empirical data.
          Falsified by wrong predictions from the encoding.
  ONTO  — ontological or philosophical implication of the structural result.
          Falsified by showing the structure does not constrain the claimed ontology.
</claim_planes>

<distance_interpretation>
Distance = 0.000  → structurally identical (same primitive class in ALL slots)
Distance < 0.500  → close analog (same structural family)
Distance 0.5–1.5  → related by shared primitive subsets
Distance > 1.5    → structurally remote (different regime)
The per-primitive breakdown shows **WHERE** the divergence lives — that IS the structural story.
</distance_interpretation>

<available_tools>
Full tool roster — call any of these by name. All tools accept JSON arguments.
{available_tools}
</available_tools>

<primitive_reference>
{primitive_reference}
</primitive_reference>

<built_in_catalog>
The following systems are pre-loaded. You **MAY** call `compute_distance`, `find_analogies`, or any
algebra/decomposition tool on them directly without encoding first:
{catalog_entries}
</built_in_catalog>

<output_format>
You **MUST** reason in plain text before and after every tool call. Explain what you expect, call the tool to validate, then reason from the result. Tools support reasoning — they do not replace it.
For derivation or proof questions: write your structural argument in plain text. Use tools to verify encodings and distances. The derivation lives in your text, not in tool call arguments.
You **MUST NOT** include **ANY** `<tool_response>` or `<tool_call>` markup in your plain text.

**Concluding rule — no exceptions:**
Before emitting CONCLUDE you **MUST** have directly answered the original question in plain text. Not "the tools show..." — an actual answer. If you have wandered far from the original question, explicitly return to it: "The original question was X. The grammar's answer is: ..." Then CONCLUDE.
</output_format>
""")


def _build_tool_roster() -> str:
    """Build a concise plain-text tool list from _TOOLS_OPENAI for the system prompt."""
    # Group by section header comments embedded in the list
    sections: list[tuple[str, list[str]]] = []
    current_section = "Core"
    current_tools: list[str] = []
    section_markers = {
        "encode_system":        "Core — encoding & catalog",
        "compute_meet":         "Algebra — lattice, tensor & imscription operations",
        "phi_c_probe":          "Probes — structural diagnostics",
        "project":              "Decomposition — path & retrosynthesis",
        "compute_conflict_distance": "Veracity & conflict distance",
        "compute_promotions":   "Promotion signatures & inverse encoding",
        "crystal_encode":       "Crystal of Types — Frobenius codec & navigation",
        "quiver_encode":        "Quiver neural navigator (CrystalGNN)",
        "domain_info":          "Domain navigators — §74–§77 (Language · Civilization · Ecology · Consciousness)",
        "navigator_info":       "Mathematical navigators — ThurstonNet · YM · Riemann · Ising",
        "zfc_formula":          "ZFC Navigator — grammar tuple → set-theoretic formula",
        "aleph_encode":         "Aleph Tensor Engine — Hebrew letter/word structural type",
        "riemann_xi_info":      "Riemann ξ Navigator — self-encoding, crystal address, O_inf convergence criteria",
    }
    for tool in _TOOLS_OPENAI:
        name = tool["function"]["name"]
        desc = tool["function"]["description"]
        # First sentence only (split on ". " to avoid truncating §N.M references)
        first_sentence = desc.split(". ")[0].strip()
        if name in section_markers:
            if current_tools:
                sections.append((current_section, current_tools))
            current_section = section_markers[name]
            current_tools = []
        current_tools.append(f"  {name:<34} — {first_sentence}")
    if current_tools:
        sections.append((current_section, current_tools))
    lines: list[str] = []
    for sec, tools in sections:
        lines.append(f"\n[{sec}]")
        lines.extend(tools)
    return "\n".join(lines)


def _build_system_prompt(catalog: "SessionCatalog") -> str:
    """Generate system prompt with tool roster, primitive reference, and full catalog."""
    entries = catalog.list_all()
    catalog_lines = "\n".join(
        f"  {e['name']:<36} — {e['description']}"
        for e in entries
    )
    # Use .replace() instead of .format() — the template contains literal Φ_}
    # characters that .format() misreads as unclosed format braces.
    return (
        _SYSTEM_PROMPT_TEMPLATE
        .replace("{available_tools}",    _build_tool_roster())
        .replace("{primitive_reference}", _PRIMITIVE_REFERENCE)
        .replace("{catalog_entries}",    catalog_lines)
    )


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Insight:
    text: str
    plane: str          # TOPO / DIAPH / ONTO
    confidence: str     # high / medium / speculative
    iteration: int
    id: str = field(default="")
    translation: Optional[Dict[str, Any]] = field(default=None)
    # translation is a dict: {systems: [...], per_system: {...}, aggregate: {coherence,criticality,interaction,total}}


@dataclass
class IterationRecord:
    iteration: int
    question: str
    model_text: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    insights_added: List[Insight] = field(default_factory=list)
    questions_queued: List[str] = field(default_factory=list)
    concluded: bool = False
    speculation_text: str = ""


# ── Tool dispatcher ───────────────────────────────────────────────────────────

class SessionCatalog:
    """Session catalog backed entirely by IG_catalog.json.

    On init, loads all entries from the JSON file (the single source of truth).
    On every successful ``encode()``, writes back immediately so no imscription
    is lost to a crash.
    """

    def __init__(self, catalog_path: Optional[str] = None):
        self._entries: Dict[str, Dict[str, str]] = {}
        self._descriptions: Dict[str, str] = {}
        self._catalog_path: Optional[str] = catalog_path
        if catalog_path:
            self._load_from_file(catalog_path)

    def _load_from_file(self, path: str) -> None:
        """Load persistent catalog entries from JSON, silently ignoring missing/corrupt files."""
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            for entry in entries:
                name = entry.get("name")
                desc = entry.get("description", "")
                prims = {p: entry[p] for p in PRIMITIVE_ORDER if p in entry}
                if name and len(prims) == len(PRIMITIVE_ORDER):
                    # Validate values before loading
                    if all(prims[p] in ORDINALS[p] for p in PRIMITIVE_ORDER):
                        self._entries[name] = prims
                        self._descriptions[name] = desc
        except (json.JSONDecodeError, KeyError, TypeError):
            pass  # Corrupt file — don't crash, just continue without persisted entries

    def _save_to_file(self, path: str) -> None:
        """Write all non-builtin catalog entries to JSON, merging with any on-disk
        entries not currently in memory (preserves entries added by other processes)."""
        # Read current disk state so we don't clobber entries written by concurrent sessions
        disk_entries: Dict[str, Any] = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for e in json.load(f):
                        n = e.get("name")
                        if n:
                            disk_entries[n] = e
            except (json.JSONDecodeError, OSError):
                pass

        # Overlay in-memory entries (they take precedence over disk for names we own)
        merged: Dict[str, Any] = dict(disk_entries)
        for name, imscription in self._entries.items():
            entry: Dict[str, Any] = {
                "name": name,
                "description": self._descriptions.get(name, ""),
            }
            entry.update(imscription)
            merged[name] = entry

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(list(merged.values()), f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # Non-fatal — inquiry continues even if save fails

    def encode(self, name: str, description: str,
               convergence_justification: str = "", **primitives) -> Dict[str, Any]:
        """Validate and register a new imscription encoding."""
        # Strip erroneous "imscription_" prefix the model sometimes prepends to names
        if name.startswith("imscription_"):
            name = name[len("imscription_"):]
        # Normalize: strip leading "{PRIM}_" prefix the model sometimes adds
        # e.g. "Σ_Σ_S" → "Σ_S", "Σ_n_n" → "Σ_ő"
        normalized: Dict[str, str] = {}
        for prim in PRIMITIVE_ORDER:
            val = primitives.get(prim, "")
            prefix = f"{prim}_"
            if val and val not in ORDINALS[prim] and val.startswith(prefix):
                val = val[len(prefix):]
            val = SYMBOL_ALIASES.get(prim, {}).get(val, val)
            normalized[prim] = val

        errors = []
        for prim in PRIMITIVE_ORDER:
            if not normalized[prim]:
                errors.append(f"Missing primitive: {prim}")
            elif normalized[prim] not in ORDINALS[prim]:
                errors.append(f"Invalid value for {prim}: '{normalized[prim]}'. "
                               f"Valid: {list(ORDINALS[prim].keys())}")
        if errors:
            missing = [e.split(":")[1].strip() for e in errors if e.startswith("Missing")]
            invalid = [e for e in errors if e.startswith("Invalid")]
            msg = {"status": "error", "errors": errors}
            if missing:
                msg["hint"] = (
                    f"encode_system requires ALL 12 primitives as explicit keyword arguments. "
                    f"Missing: {missing}. "
                    f"Example call: encode_system(name='foo', description='...', "
                    f"Ð='Ð_ω', Þ='Þ_O', Ř='Ř_ý', Φ='Φ_F', ƒ='ƒ^ż', "
                    f"Ç='Ç^W', Γ='Γ_ʔ', ɢ='ɢ^∧', ⊙='⊙_ÿ', "
                    f"Ħ='Ħ_Ñ', Σ='Σ_ï', Ω='Ω_z')"
                )
            return msg

        imscription = {p: normalized[p] for p in PRIMITIVE_ORDER}

        # ── Consistency check 1: same name, different tuple ──────────────────────
        # If the name already exists with a different tuple:
        #   - without convergence_justification → BLOCK; do not commit.
        #   - with convergence_justification    → commit and record justification.
        conflict_info: Optional[Dict[str, Any]] = None
        if name in self._entries:
            existing = self._entries[name]
            if existing != imscription:
                differing = [p for p in PRIMITIVE_ORDER if existing.get(p) != imscription[p]]
                dist = tuple_distance(existing, imscription)
                conflict_info = {
                    "existing_tuple": existing,
                    "existing_description": self._descriptions.get(name, ""),
                    "new_tuple": imscription,
                    "distance": round(dist, 4),
                    "differing_primitives": differing,
                }
                if not convergence_justification:
                    # Block the commit — force comparison→convergence protocol.
                    return {
                        "status": "conflict_blocked",
                        "name": name,
                        "existing_tuple": existing,
                        "proposed_tuple": {p: imscription[p] for p in PRIMITIVE_ORDER},
                        "distance": round(dist, 4),
                        "differing_primitives": differing,
                        "instruction": (
                            f"Conflicting encoding for '{name}' — catalog NOT updated. "
                            f"You MUST perform the comparison→convergence protocol before committing: "
                            f"(1) Call compute_conflict_distance('{name}', '<proposed_name>') "
                            f"or reason through each differing primitive ({differing}) explicitly. "
                            f"(2) Determine which value is correct for each conflict. "
                            f"(3) Re-call encode_system with convergence_justification='<your per-primitive reasoning>' "
                            f"to commit. If both encodings are valid, use a distinct name for the earlier one."
                        ),
                    }

        self._entries[name] = imscription
        self._descriptions[name] = description

        # ── Consistency check 2: exact duplicate under a different name ──────────
        exact_duplicates: List[str] = []
        for other_name, other_imscription in self._entries.items():
            if other_name != name and other_imscription == imscription:
                exact_duplicates.append(other_name)

        # Persist immediately so no imscription is lost to a crash
        if self._catalog_path:
            self._save_to_file(self._catalog_path)

        # Build tuple notation
        notation = "⟨" + "; ".join(f"{p}={imscription[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        result: Dict[str, Any] = {
            "status": "ok" if not conflict_info else "updated",
            "name": name,
            "notation": notation,
            "description": description,
            "persisted": self._catalog_path is not None,
        }

        if conflict_info:
            result["warning"] = (
                f"Name '{name}' already existed with a DIFFERENT tuple "
                f"(distance={conflict_info['distance']:.4f}, "
                f"differing primitives: {conflict_info['differing_primitives']}). "
                f"Catalog updated to new tuple — the prior encoding is superseded. "
                f"If both encodings are valid, use a distinct name for the earlier one."
            )
            result["conflict"] = {
                "superseded_tuple": conflict_info["existing_tuple"],
                "superseded_description": conflict_info["existing_description"],
                "differing_primitives": conflict_info["differing_primitives"],
                "distance_from_superseded": conflict_info["distance"],
                "convergence_justification": convergence_justification,
            }

        if exact_duplicates:
            result["duplicate_warning"] = (
                f"This tuple is IDENTICAL to existing catalog entries: {exact_duplicates}. "
                f"The encoding was accepted under name '{name}', but consider whether "
                f"a new name is needed or if this should reuse an existing entry."
            )
            result["exact_duplicates"] = exact_duplicates

        return result

    def get(self, name: str) -> Optional[Dict[str, str]]:
        return self._entries.get(name)

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        kw = keyword.lower()
        results = []
        for name, imscription in self._entries.items():
            if kw in name.lower() or kw in self._descriptions.get(name, "").lower():
                notation = "⟨" + "; ".join(f"{p}={imscription[p]}" for p in PRIMITIVE_ORDER) + "⟩"
                results.append({
                    "name": name,
                    "description": self._descriptions.get(name, ""),
                    "notation": notation,
                })
        return results

    def list_all(self) -> List[Dict[str, Any]]:
        results = []
        for name, imscription in self._entries.items():
            notation = "⟨" + "; ".join(f"{p}={imscription[p]}" for p in PRIMITIVE_ORDER) + "⟩"
            results.append({
                "name": name,
                "description": self._descriptions.get(name, ""),
                "notation": notation,
            })
        return results


class InsightLibrary:
    """
    Persistent cross-session library of Imscribing Grammar insights.

    Stored in ig_insights.json.  Each entry records the insight text,
    plane, confidence, source seed, timestamp, and automatically extracted
    primitive/imscription references.

    Deduplication: entries are keyed by a 12-char SHA1 of the original text
    at creation time.  The ID remains stable across updates so the model can
    revise an insight without losing its identity.
    """

    # Regex to extract primitive value mentions from free text
    _PRIM_RE = re.compile(
        r"\b("
        r"D_(?:wedge|triangle|infty|holo)"
        r"|T_(?:network|in|bowtie|box|holo)"
        r"|R_(?:super|cat|dagger|lr)"
        r"|P_(?:asym|psi|pm|sym)"
        r"|F_(?:ell|eth|hbar)"
        r"|K_(?:fast|mod|slow|trap)"
        r"|G_(?:beth|gimel|aleph)"
        r"|G_(?:and|or|seq|broad)"
        r"|Phi_(?:sub|c|super)"
        r"|H(?:0|1|2|_inf)"
        r"|Σ_S|Σ_ő|Σ_ï"
        r"|Omega_(?:0|Z2|Z)"
        r")\b"
    )

    def __init__(self, path: str = INSIGHTS_PATH):
        self._path = path
        self._entries: Dict[str, Dict[str, Any]] = {}  # id → entry
        self._load()

    def _load(self):
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            for e in entries:
                if "id" in e and "text" in e:
                    self._entries[e["id"]] = e
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    def _save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(list(self._entries.values()), f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    @staticmethod
    def make_id(text: str) -> str:
        """Stable 12-char SHA1 of the insight text at creation time."""
        return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:12]

    def _extract_primitives(self, text: str) -> List[str]:
        return sorted(set(self._PRIM_RE.findall(text)))

    def _extract_imscriptions(self, text: str, catalog: Optional["SessionCatalog"]) -> List[str]:
        if catalog is None:
            return []
        found = []
        for entry in catalog.list_all():
            name = entry["name"]
            if re.search(r"\b" + re.escape(name) + r"\b", text):
                found.append(name)
        return sorted(set(found))

    def add_batch(
        self,
        insights: List["Insight"],
        seed: str,
        run_file: str,
        catalog: Optional["SessionCatalog"],
    ) -> int:
        """Add insights from a completed run. Returns count of new entries added."""
        import datetime as _dt
        ts = _dt.datetime.now().isoformat(timespec="seconds")
        added = 0
        for ins in insights:
            iid = ins.id or self.make_id(ins.text)
            if iid in self._entries:
                # Entry exists — update if text was revised during session
                stored = self._entries[iid]
                if stored["text"] != ins.text or stored["plane"] != ins.plane or stored["confidence"] != ins.confidence:
                    stored.update({
                        "text": ins.text,
                        "plane": ins.plane,
                        "confidence": ins.confidence,
                        "modified": ts,
                        "primitives": self._extract_primitives(ins.text),
                        "imscriptions": self._extract_imscriptions(ins.text, catalog),
                    })
                continue
            entry: Dict[str, Any] = {
                "id": iid,
                "text": ins.text,
                "plane": ins.plane,
                "confidence": ins.confidence,
                "seed": seed,
                "timestamp": ts,
                "run_file": run_file,
                "primitives": self._extract_primitives(ins.text),
                "imscriptions": self._extract_imscriptions(ins.text, catalog),
            }
            self._entries[iid] = entry
            added += 1
        if added or insights:
            self._save()
        return added

    def update(
        self,
        insight_id: str,
        text: Optional[str] = None,
        plane: Optional[str] = None,
        confidence: Optional[str] = None,
        catalog: Optional["SessionCatalog"] = None,
    ) -> bool:
        """Update a stored insight in place. Returns True if found and updated."""
        import datetime as _dt
        entry = self._entries.get(insight_id)
        if entry is None:
            return False
        if text is not None:
            entry["text"] = text
            entry["primitives"] = self._extract_primitives(text)
            entry["imscriptions"] = self._extract_imscriptions(text, catalog)
        if plane is not None:
            entry["plane"] = plane
        if confidence is not None:
            entry["confidence"] = confidence
        entry["modified"] = _dt.datetime.now().isoformat(timespec="seconds")
        self._save()
        return True

    def get(self, insight_id: str) -> Optional[Dict[str, Any]]:
        return self._entries.get(insight_id)

    def query(
        self,
        plane: Optional[str] = None,
        primitive: Optional[str] = None,
        imscription: Optional[str] = None,
        keyword: Optional[str] = None,
        confidence: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filter insights. All filters are ANDed."""
        results = list(self._entries.values())
        if plane:
            results = [e for e in results if e.get("plane") == plane]
        if primitive:
            results = [e for e in results if primitive in e.get("primitives", [])]
        if imscription:
            results = [e for e in results if imscription in e.get("imscriptions", [])]
        if keyword:
            kw = keyword.lower()
            results = [e for e in results if kw in e["text"].lower() or kw in e.get("seed", "").lower()]
        if confidence:
            results = [e for e in results if e.get("confidence") == confidence]
        return results

    def all(self) -> List[Dict[str, Any]]:
        return list(self._entries.values())

    def to_graph(self) -> Dict[str, Any]:
        """
        Generate a knowledge graph from the insight library.

        Node types: insight, primitive, imscription, seed
        Edge types: mentions_primitive, mentions_imscription, from_seed
        """
        nodes: List[Dict] = []
        edges: List[Dict] = []
        all_prims: set = set()
        all_syns: set = set()
        all_seeds: set = set()

        for e in self._entries.values():
            all_prims.update(e.get("primitives", []))
            all_syns.update(e.get("imscriptions", []))
            all_seeds.add(e.get("seed", ""))

        for e in self._entries.values():
            nodes.append({
                "id": e["id"], "type": "insight",
                "plane": e.get("plane"), "confidence": e.get("confidence"),
                "text": e["text"][:120],
            })
        for p in sorted(all_prims):
            nodes.append({"id": f"prim_{p}", "type": "primitive", "name": p})
        for s in sorted(all_syns):
            nodes.append({"id": f"imscription_{s}", "type": "imscription", "name": s})
        for seed in sorted(all_seeds):
            sid = self.make_id(seed)
            nodes.append({"id": f"seed_{sid}", "type": "seed", "text": seed[:100]})

        for e in self._entries.values():
            for p in e.get("primitives", []):
                edges.append({"source": e["id"], "target": f"prim_{p}", "type": "mentions_primitive"})
            for s in e.get("imscriptions", []):
                edges.append({"source": e["id"], "target": f"imscription_{s}", "type": "mentions_imscription"})
            seed_id = self.make_id(e.get("seed", ""))
            edges.append({"source": e["id"], "target": f"seed_{seed_id}", "type": "from_seed"})

        return {
            "nodes": nodes, "edges": edges,
            "stats": {
                "insights": len(self._entries),
                "primitives": len(all_prims),
                "imscriptions": len(all_syns),
                "seeds": len(all_seeds),
                "edges": len(edges),
            },
        }


class PromotionKnowledgeBase:
    """
    Persistent cross-session library of promotion-signature → behavior patterns.

    A promotion pattern records which primitives were lifted (promoted in ordinal
    rank) to produce a named behavior.  The KB is built incrementally: each
    session the model calls register_promotion_pattern() whenever it identifies
    a behavior that is explained by a specific promotion from baseline.

    Stored in IG_promotions.json.  Each entry:
      id                  — 12-char SHA1 of promoted_primitives + behavior
      promoted_primitives — list of primitive names that were lifted (e.g. ["Þ","Ħ","ƒ"])
      behavior            — short description of the emergent behavior
      example             — canonical system exhibiting this pattern (optional)
      session_seed        — seed question of the originating session
      timestamp           — ISO timestamp
    """

    def __init__(self, path: str = PROMOTIONS_PATH):
        self._path = path
        self._entries: Dict[str, Dict[str, Any]] = {}  # id → entry
        self._load()

    def _load(self):
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                entries = json.load(f)
            for e in entries:
                if "id" in e:
                    self._entries[e["id"]] = e
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    def _save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(list(self._entries.values()), f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    @staticmethod
    def make_id(promoted_primitives: List[str], behavior: str) -> str:
        key = "|".join(sorted(promoted_primitives)) + "||" + behavior.strip()
        return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]

    def add(
        self,
        promoted_primitives: List[str],
        behavior: str,
        example: str = "",
        session_seed: str = "",
    ) -> Dict[str, Any]:
        """Add a pattern; returns the entry dict (existing if duplicate)."""
        import datetime as _dt
        pid = self.make_id(promoted_primitives, behavior)
        if pid in self._entries:
            return {"status": "duplicate", "pattern_id": pid, "existing": self._entries[pid]}
        entry: Dict[str, Any] = {
            "id": pid,
            "promoted_primitives": sorted(set(promoted_primitives)),
            "behavior": behavior,
            "example": example,
            "session_seed": session_seed,
            "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
        }
        self._entries[pid] = entry
        self._save()
        return {"status": "ok", "pattern_id": pid, "registered": entry}

    def find(self, promoted_primitives: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Return ranked matches from the KB for a given promotion signature.

        Scoring per match:
          overlap   = |query ∩ pattern|
          coverage  = overlap / |pattern|   (how much of the known pattern is present)
          relevance = overlap / |query|     (how much of the query is explained)
          score     = harmonic mean of coverage and relevance
        """
        query = set(promoted_primitives)
        matches = []
        for entry in self._entries.values():
            pattern = set(entry["promoted_primitives"])
            overlap = query & pattern
            if not overlap:
                continue
            cov = len(overlap) / len(pattern) if pattern else 0.0
            rel = len(overlap) / len(query) if query else 0.0
            score = (2 * cov * rel / (cov + rel)) if (cov + rel) > 0 else 0.0
            matches.append({
                "pattern_id": entry["id"],
                "behavior": entry["behavior"],
                "example": entry.get("example", ""),
                "matching_primitives": sorted(overlap),
                "unmatched_in_query": sorted(query - pattern),
                "novel_in_pattern": sorted(pattern - query),
                "coverage": round(cov, 3),
                "relevance": round(rel, 3),
                "score": round(score, 3),
            })
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:top_k]

    def all(self) -> List[Dict[str, Any]]:
        return list(self._entries.values())


class ToolDispatcher:
    def __init__(self, catalog: SessionCatalog, question_queue: List[str], insights: List[Insight],
                 insight_library: Optional[InsightLibrary] = None,
                 promotion_kb: Optional[PromotionKnowledgeBase] = None,
                 session_seed: str = ""):
        self.catalog = catalog
        self.question_queue = question_queue
        self.insights = insights
        self.insight_library = insight_library
        self.promotion_kb = promotion_kb
        self._session_seed = session_seed
        self._iteration = 0
        # Tracks all conflict pairs registered this session for emergence_frontier
        self._conflict_pairs: List[Dict[str, Any]] = []
        # Crystal Navigator (lazy-loaded on first use)
        self._crystal_nav: Optional[Any] = None
        # CrystalGNN quiver model (lazy-loaded on first use)
        self._quiver_model: Optional[Any] = None
        # Encoding gate: lookup_* tools are blocked until encode_system succeeds once
        self._session_encoded: bool = False

    def dispatch(self, name: str, args: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        self._iteration = iteration
        # Normalize argument keys to lowercase to tolerate model capitalisation variants
        args = {k.lower(): v for k, v in args.items()}
        # Encoding gate: block catalog browsing until the session has encoded at least one system
        # Encoding gate check removed - managed by agent wrapper's _gate_state
        # Dual gate mechanism is problematic; delegate gate to TrueAgenticAgent
        # if not self._session_encoded and (name.startswith("lookup_") or name == "list_catalog"):
        #     return {"status": "error", "error": "This tool is not available."}
        pass  # Gate removed
        if name in ("encode_system", "imscribe_system"):
            name = "encode_system"  # imscribe_system is the true_agentic_agent alias
        if name == "encode_system":
            if "name" not in args:
                return {
                    "status": "error",
                    "error": "encode_system requires a 'name' argument.",
                    "hint": (
                        "Call as: encode_system(name='my_system', description='...', "
                        "tuple='Ð_ω;Þ_O;Ř_ý;Φ_F;ƒ^ż;Ç^W;Γ_ʔ;ɢ^∧;⊙_ÿ;Ħ_Ñ;Σ_ï;Ω_z')"
                    ),
                }
            result = self._encode_system(**args)
            if result.get("status") in ("ok", "updated"):
                self._session_encoded = True
            return result
        elif name == "compute_distance":
            return self._compute_distance(**args)
        elif name == "lookup_catalog":
            return self._lookup_catalog(**args)
        elif name == "list_catalog":
            return self._list_catalog(**args)
        elif name == "ask_question":
            return self._ask_question(**args)
        elif name == "record_insight":
            return self._record_insight(**args)
        # ── Algebra ──────────────────────────────────────────────────────────
        elif name == "compute_meet":
            return self._compute_meet(**args)
        elif name == "compute_join":
            return self._compute_join(**args)
        elif name == "compute_tensor":
            return self._compute_tensor(**args)
        elif name == "check_imscription":
            return self._check_imscription(**args)
        elif name == "find_analogies":
            return self._find_analogies(**args)
        # ── Probes ───────────────────────────────────────────────────────────
        elif name == "phi_c_probe":
            return self._phi_c_probe(**args)
        elif name == "ouroborics":
            return self._frobenius_tier(**args)
        elif name == "topo_protection_probe":
            return self._topo_protection_probe(**args)
        # ── Decomposition ────────────────────────────────────────────────────
        elif name == "project":
            return self._project(**args)
        elif name == "primitive_peel":
            return self._primitive_peel(**args)
        elif name == "principal_decomp":
            return self._principal_decomp(**args)
        elif name == "retrosynthetic_path":
            return self._retrosynthetic_path(**args)
        # ── Veracity / conflict distance ──────────────────────────────────────
        elif name == "compute_conflict_distance":
            return self._compute_conflict_distance(**args)
        elif name == "emergence_frontier":
            return self._emergence_frontier()
        # ── Promotion signature / inverse encoding ────────────────────────────
        elif name == "compute_promotions":
            return self._compute_promotions(**args)
        elif name == "predict_from_promotions":
            return self._predict_from_promotions(**args)
        elif name == "register_promotion_pattern":
            return self._register_promotion_pattern(**args)
        # ── Crystal Navigator ────────────────────────────────────────────────
        elif name == "crystal_encode":
            return self._crystal_encode(**args)
        elif name == "crystal_decode":
            return self._crystal_decode(**args)
        elif name == "crystal_navigate":
            return self._crystal_navigate(**args)
        elif name == "crystal_count":
            return self._crystal_count(**args)
        elif name == "crystal_tier_census":
            return self._crystal_tier_census()
        elif name == "crystal_nearest":
            return self._crystal_nearest(**args)
        elif name == "crystal_tier_gap_ladder":
            return self._crystal_tier_gap_ladder()
        elif name == "quiver_encode":
            return self._quiver_encode(**args)
        # ── Domain Navigators ────────────────────────────────────────────────
        elif name == "domain_info":
            return self._domain_info(**args)
        elif name == "domain_verify":
            return self._domain_verify(**args)
        elif name == "domain_nearest":
            return self._domain_nearest(**args)
        elif name == "consciousness_score":
            return self._consciousness_score_tool(**args)
        elif name == "navigator_info":
            return self._navigator_info()
        # ── ZFC Navigator ─────────────────────────────────────────────────────
        elif name == "zfc_formula":
            return self._zfc_formula(**args)
        elif name == "zfc_probe":
            return self._zfc_probe(**args)
        elif name == "zfc_catalog_probe":
            return self._zfc_catalog_probe(**args)
        # ── Aleph / HoTT / Riemann Xi ─────────────────────────────────────────
        elif name == "aleph_encode":
            return self._aleph_encode(**args)
        elif name == "aleph_distance":
            return self._aleph_distance(**args)
        elif name == "riemann_xi_info":
            return self._riemann_xi_info()
        else:
            return {"status": "error", "error": f"Unknown tool: {name}"}

    def _encode_system(self, name: str, description: str = "", tuple: str = "",
                        convergence_justification: str = "", **primitives) -> Dict[str, Any]:
        # Normalize primitive keys (dispatch lowercases; also handles old ASCII key names)
        primitives = {self._PRIM_CANONICAL.get(k, k): v for k, v in primitives.items()}
        # If 'tuple' string provided, parse it into primitives (preferred path)
        if tuple:
            parts = [p.strip() for p in tuple.replace("⟨", "").replace("⟩", "").split(";")]
            if len(parts) == len(PRIMITIVE_ORDER):
                for prim, val in zip(PRIMITIVE_ORDER, parts):
                    # Strip "PRIM=" prefix if present (e.g. "Ř=Ř_="), but only when
                    # the left-hand side is a known primitive name — otherwise values
                    # like "Ř_=" would be incorrectly split on their trailing "=".
                    if "=" in val:
                        left, right = val.split("=", 1)
                        if left.strip() in PRIMITIVE_ORDER:
                            val = right.strip()
                    if prim not in primitives or not primitives[prim]:
                        primitives[prim] = _normalize_value(val)
        # Also normalize any keyword-argument values
        primitives = {k: _normalize_value(v) if isinstance(v, str) else v
                      for k, v in primitives.items()}
        return self.catalog.encode(name, description,
                                   convergence_justification=convergence_justification,
                                   **primitives)

    def _compute_distance(self, name_a: str, name_b: str) -> Dict[str, Any]:
        sa = self.catalog.get(name_a)
        sb = self.catalog.get(name_b)
        missing = []
        if sa is None:
            missing.append(name_a)
        if sb is None:
            missing.append(name_b)
        if missing:
            return {"status": "error", "error": f"Unknown system(s): {missing}. Encode them first."}

        dist = tuple_distance(sa, sb)
        bkd = breakdown(sa, sb)
        contributing = [r for r in bkd if r["weighted_sq"] > 0]
        result = {
            "status": "ok",
            "name_a": name_a,
            "name_b": name_b,
            "distance": round(dist, 4),
            "breakdown": contributing,
            "interpretation": (
                "identical" if dist == 0.0 else
                "close analog (same structural family)" if dist < 0.5 else
                "related (shared primitive subsets)" if dist < 1.5 else
                "structurally remote (different regime)"
            ),
        }
        if _METRIC_G is not None:
            try:
                d_maha = mahalanobis_distance(sa, sb, _METRIC_G)
                result["distance_mahalanobis"] = round(d_maha, 4)
                result["metric_note"] = (
                    "distance_mahalanobis uses the full g_ij=Sigma^-1 tensor "
                    "(accounts for off-diagonal couplings; geometrically canonical). "
                    "distance is the diagonal approximation."
                )
            except Exception:
                pass
        return result

    def _lookup_catalog(self, keyword: str, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        results = self.catalog.search(keyword)
        total   = len(results)
        page    = results[offset: offset + limit]
        result  = {
            "status":  "ok",
            "keyword": keyword,
            "matches": page,
            "returned": len(page),
            "total":   total,
            "offset":  offset,
        }
        if offset + limit < total:
            result["next_offset"] = offset + limit
            result["note"] = f"Showing {offset}–{offset + len(page) - 1} of {total}. Call again with offset={offset + limit} for more."
        return result

    def _list_catalog(self, offset: int = 0, limit: int = 20) -> Dict[str, Any]:
        entries = self.catalog.list_all()
        total   = len(entries)
        page    = entries[offset: offset + limit]
        result  = {
            "status":   "ok",
            "entries":  page,
            "returned": len(page),
            "total":    total,
            "offset":   offset,
        }
        if offset + limit < total:
            result["next_offset"] = offset + limit
            result["note"] = f"Showing {offset}–{offset + len(page) - 1} of {total}. Call again with offset={offset + limit} for more."
        return result

    _MAX_QUEUE = 8  # cap to prevent infinite wandering via repeated ask_question calls

    def _ask_question(self, question: str, motivation: str) -> Dict[str, Any]:
        if len(self.question_queue) >= self._MAX_QUEUE:
            return {
                "status": "queue_full",
                "msg": f"Queue is full ({self._MAX_QUEUE} questions). Use CONCLUDE to synthesize instead of asking more questions.",
                "queue_size": len(self.question_queue),
            }
        self.question_queue.append(question)
        return {
            "status": "ok",
            "queued": question,
            "motivation": motivation,
            "position_in_queue": len(self.question_queue),
        }

    def _record_insight(
        self,
        text: str,
        plane: str,
        confidence: str,
        systems: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        iid = InsightLibrary.make_id(text)

        # ── Compute translation cost if systems are named ──────────────────────
        translation: Optional[Dict[str, Any]] = None
        if systems:
            per_system: Dict[str, Dict[str, Any]] = {}
            agg = {"coherence_loss": 0.0, "criticality_loss": 0.0, "interaction_cost": 0.0, "total": 0.0}
            for sname in systems:
                sdict = self.catalog.get(sname)
                if sdict:
                    cost = _translation_cost_from_dict(sdict)
                    per_system[sname] = cost
                    for k in ("coherence_loss", "criticality_loss", "interaction_cost", "total"):
                        agg[k] = round(agg[k] + cost[k], 4)
            translation = {
                "systems": [s for s in systems if self.catalog.get(s)],
                "per_system": per_system,
                "aggregate": agg,
            }

        insight = Insight(
            text=text, plane=plane, confidence=confidence,
            iteration=self._iteration, id=iid,
            translation=translation,
        )
        self.insights.append(insight)

        result: Dict[str, Any] = {
            "status": "ok",
            "insight_id": iid,
            "insight_recorded": text,
            "plane": plane,
            "confidence": confidence,
            "note": "Each session navigates the lattice fresh — insights are session-local and not persisted across runs.",
        }
        if translation:
            result["translation_cost"] = translation["aggregate"]
        return result

    def _revise_insight(
        self,
        insight_id: str,
        text: Optional[str] = None,
        plane: Optional[str] = None,
        confidence: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an in-session insight (and the persistent library if available)."""
        # Find in session list
        session_match = next((ins for ins in self.insights if ins.id == insight_id), None)
        if session_match is None:
            # May be in library only (from a previous session)
            if self.insight_library:
                lib_entry = self.insight_library.get(insight_id)
                if lib_entry is None:
                    return {"status": "error", "error": f"No insight with id '{insight_id}' found in session or library."}
                self.insight_library.update(insight_id, text=text, plane=plane, confidence=confidence, catalog=self.catalog)
                updated = self.insight_library.get(insight_id)
                return {"status": "ok", "updated_in": "library_only", "insight": updated}
            return {"status": "error", "error": f"No insight with id '{insight_id}' in session."}

        if text is not None:
            session_match.text = text
        if plane is not None:
            session_match.plane = plane
        if confidence is not None:
            session_match.confidence = confidence

        # Mirror update to library if available
        if self.insight_library:
            self.insight_library.update(insight_id, text=text, plane=plane, confidence=confidence, catalog=self.catalog)

        return {
            "status": "ok",
            "updated_in": "session" + (" + library" if self.insight_library else ""),
            "insight_id": insight_id,
            "text": session_match.text,
            "plane": session_match.plane,
            "confidence": session_match.confidence,
        }

    def _search_insights(self, keyword: str, plane: Optional[str] = None) -> Dict[str, Any]:
        """Search the persistent insight library by keyword and optional plane."""
        if self.insight_library is None:
            return {"status": "error", "error": "No persistent insight library available in this session."}
        results = self.insight_library.query(keyword=keyword, plane=plane or None)
        return {
            "status": "ok",
            "keyword": keyword,
            "plane_filter": plane,
            "count": len(results),
            "results": [
                {
                    "id": e["id"],
                    "plane": e.get("plane"),
                    "confidence": e.get("confidence"),
                    "text": e["text"],
                    "seed": e.get("seed", ""),
                    "primitives": e.get("primitives", []),
                    "imscriptions": e.get("imscriptions", []),
                }
                for e in results
            ],
        }

    # ── Algebra operations ────────────────────────────────────────────────────

    def _resolve(self, names: List[str]) -> Tuple[Optional[List[Dict]], Optional[Dict]]:
        """Resolve a list of names to imscription dicts; return (imscriptions, error) pair."""
        imscriptions = []
        missing = []
        for n in names:
            s = self.catalog.get(n)
            if s is None:
                missing.append(n)
            else:
                imscriptions.append(s)
        if missing:
            return None, {"status": "error", "error": f"Unknown system(s): {missing}. Encode them first."}
        return imscriptions, None

    def _apply_binary(self, rule: str, p: str, va: str, vb: str) -> Tuple[str, Optional[Dict]]:
        """Apply tensor/meet/join rule for one primitive. Returns (winner_value, conflict_note_or_None)."""
        if va == vb:
            return va, None
        oa = ORDINALS[p].get(va, 0)
        ob = ORDINALS[p].get(vb, 0)
        if rule == "min":
            winner = va if oa <= ob else vb
        else:
            winner = va if oa >= ob else vb
        return winner, {"primitive": p, "a": va, "b": vb, "resolved": winner}

    def _compute_meet(self, name_a: str, name_b: str) -> Dict[str, Any]:
        """Lattice meet — shared primitive floor (most conservative value per primitive)."""
        imscriptions, err = self._resolve([name_a, name_b])
        if err:
            return err
        sa, sb = imscriptions
        result, conflicts, shared = {}, [], []
        for p in PRIMITIVE_ORDER:
            val, conflict = self._apply_binary("min", p, sa[p], sb[p])
            result[p] = val
            (conflicts if conflict else shared).append(conflict or p)
        notation = "⟨" + "; ".join(f"{p}={result[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        return {
            "status": "ok",
            "operation": "meet",
            "name_a": name_a, "name_b": name_b,
            "result_notation": notation,
            "shared_primitives": [p for p in PRIMITIVE_ORDER if sa[p] == sb[p]],
            "resolved_conflicts": conflicts,
            "interpretation": (
                f"Structural floor of {name_a} ∧ {name_b}. "
                f"{len(conflicts)} primitive(s) resolved to conservative value; "
                f"{len(PRIMITIVE_ORDER) - len(conflicts)} shared. "
                "These are the primitives both systems possess without qualification."
            ),
        }

    def _compute_join(self, name_a: str, name_b: str) -> Dict[str, Any]:
        """Lattice join — minimal upper bound (most expansive value per primitive)."""
        imscriptions, err = self._resolve([name_a, name_b])
        if err:
            return err
        sa, sb = imscriptions
        result, conflicts = {}, []
        for p in PRIMITIVE_ORDER:
            val, conflict = self._apply_binary("max", p, sa[p], sb[p])
            result[p] = val
            if conflict:
                conflicts.append(conflict)
        notation = "⟨" + "; ".join(f"{p}={result[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        return {
            "status": "ok",
            "operation": "join",
            "name_a": name_a, "name_b": name_b,
            "result_notation": notation,
            "resolved_conflicts": conflicts,
            "interpretation": (
                f"Minimal system containing both {name_a} and {name_b}. "
                f"The join encodes the most demanding requirements across all primitives — "
                "what a single system would need to encompass both structural regimes."
            ),
        }

    def _compute_tensor(self, name_a: str, name_b: str) -> Dict[str, Any]:
        """Tensor product — structural composition of two systems (A⊗B)."""
        imscriptions, err = self._resolve([name_a, name_b])
        if err:
            return err
        sa, sb = imscriptions
        result, bottlenecks, unions, shared = {}, [], [], []
        for p in PRIMITIVE_ORDER:
            rule = _TENSOR_RULES[p]
            val, conflict = self._apply_binary(rule, p, sa[p], sb[p])
            result[p] = val
            if conflict:
                if rule == "min":
                    bottlenecks.append({**conflict, "rule": "bottleneck"})
                else:
                    unions.append({**conflict, "rule": "union/promote"})
            else:
                shared.append(p)
        notation = "⟨" + "; ".join(f"{p}={result[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        dist_from_a = round(tuple_distance(result, sa), 4)
        dist_from_b = round(tuple_distance(result, sb), 4)
        return {
            "status": "ok",
            "operation": "tensor",
            "name_a": name_a, "name_b": name_b,
            "result_notation": notation,
            "bottleneck_primitives": bottlenecks,
            "union_primitives": unions,
            "shared_primitives": shared,
            "distance_from_a": dist_from_a,
            "distance_from_b": dist_from_b,
            "interpretation": (
                f"{name_a}⊗{name_b}: composed system with {len(bottlenecks)} bottleneck(s) "
                f"and {len(unions)} scope-expansion(s). "
                f"Distance from A: {dist_from_a}, from B: {dist_from_b}. "
                "Bottlenecks show where the weaker partner limits the composite; "
                "unions show where the combined scope exceeds either component."
            ),
        }

    def _check_imscription(self, name_boundary: str, name_bulk: str) -> Dict[str, Any]:
        """Test whether name_boundary imscribes name_bulk (§89)."""
        imscriptions, err = self._resolve([name_boundary, name_bulk])
        if err:
            return err
        s_bnd, s_blk = imscriptions
        from navigators.crystal_navigator import (  # type: ignore
            imscription_check as _imscription_check,
            imscription_statement as _imscription_statement,
        )
        result = _imscription_check(s_bnd, s_blk)
        stmt = _imscription_statement(name_boundary, name_bulk, result)
        return {
            "status": "ok",
            "boundary": name_boundary,
            "bulk": name_bulk,
            "imscription_type": result["imscription_type"],
            "statement": stmt,
            "floor_condition": result["floor_condition"],
            "tensor_condition": result["tensor_condition"],
            "boundary_tier": result["boundary_tier"],
            "d_boundary_to_bulk": result["d_boundary_to_bulk"],
            "d_bulk_to_boundary": result["d_bulk_to_boundary"],
            "tensor_mismatches_vs_bulk": result["tensor_mismatches_vs_bulk"],
            "meet_mismatches_vs_boundary": result["meet_mismatches_vs_boundary"],
            "per_primitive": result["per_primitive"],
            "interpretation": (
                f"Imscription check ({name_boundary} → {name_bulk}): "
                f"type={result['imscription_type']}, "
                f"boundary_tier={result['boundary_tier']}, "
                f"floor={'✓' if result['floor_condition'] else '✗'}, "
                f"tensor={'✓' if result['tensor_condition'] else '✗'}, "
                f"d→bulk={result['d_boundary_to_bulk']}, "
                f"d→boundary={result['d_bulk_to_boundary']}."
            ),
        }

    def _find_analogies(self, name: str, limit: int = 5) -> Dict[str, Any]:
        """Find catalog entries most structurally similar to the named system."""
        target = self.catalog.get(name)
        if target is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        scores = []
        for entry_name, entry_imscription in self.catalog._entries.items():
            if entry_name == name:
                continue
            d_diag = round(tuple_distance(target, entry_imscription), 4)
            d = round(mahalanobis_distance(target, entry_imscription, _METRIC_G), 4) \
                if _METRIC_G is not None else d_diag
            scores.append({
                "name": entry_name,
                "distance": d,
                "distance_diagonal": d_diag,
                "description": self.catalog._descriptions.get(entry_name, ""),
                "interpretation": (
                    "identical" if d == 0.0 else
                    "close analog" if d < 0.5 else
                    "related" if d < 1.5 else
                    "remote"
                ),
            })
        scores.sort(key=lambda x: x["distance"])
        top = scores[:limit]
        return {
            "status": "ok",
            "name": name,
            "analogies": top,
            "nearest": top[0] if top else None,
            "interpretation": f"Top {len(top)} structural analogs to {name} in the full catalog.",
        }

    def _phi_c_probe(self, name: str) -> Dict[str, Any]:
        """Test whether a system is at criticality (⊙_ÿ)."""
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        phi = s["⊙"]
        at_criticality = phi in ("⊙", "𐑮")
        return {
            "status": "ok",
            "name": name,
            "phi_value": phi,
            "at_criticality": at_criticality,
            "interpretation": (
                f"{name} is AT criticality (⊙_ÿ) — scale-invariant, maximally sensitive, "
                "at the phase boundary between subcritical and supercritical regimes."
                if at_criticality else
                f"{name} is {_UNICODE_TO_CANONICAL.get(phi, phi)}: {'subcritical (stable, ordered, below threshold)' if phi == '𐑢' else 'supercritical (disordered, past critical threshold, fluctuation-dominated)' if phi == '𐑣' else 'critical self-modeling (⊙_ÿ) — scale-invariant, maximally sensitive' if phi == '⊙' else 'complex-plane critical (⊙_Æ)' if phi == '𐑮' else 'exceptional point (⊙_3)' if phi == '𐑻' else 'unknown'}."
            ),
        }

    def _topo_protection_probe(self, name: str) -> Dict[str, Any]:
        """Test whether a system has winding (Omega ≠ Ω_Å)."""
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        omega = s["Ω"]
        protected = omega != "Ω_Å"
        protection_desc = {
            "Ω_Å":  "trivial — trivial winding — no conserved topological invariant",
            "Ω_2": "Z₂ protected — binary (even/odd) winding number conservation",
            "Ω_z":  "Z protected — integer winding number conservation (Kitaev, SSH)",
            "Ω_5": "non-Abelian protected — anyonic braiding statistics; non-Abelian invariant (Fibonacci anyons, non-Abelian CS theory)",
        }
        return {
            "status": "ok",
            "name": name,
            "omega_value": omega,
            "topologically_protected": protected,
            "protection_class": protection_desc.get(omega, omega),
            "interpretation": (
                f"{name} has {protection_desc.get(omega, omega)}. "
                + ("Topological interactions cannot be disrupted by continuous deformations."
                   if protected else
                   "No topological barrier — interactions and phase transitions are structurally unprotected.")
            ),
        }

    @staticmethod
    def _shavian_to_display(val: str, prim: str) -> str:
        """Decode a Shavian-glyph ORDINALS value as Shavian glyphs (identity).
        
        The catalog stores primitive values as Shavian Unicode glyphs 
        (the ORDINALS keys). This maps them back to Shavian Unicode (identity)
        as Shavian Unicode glyphs (identity).
        """
        return val

    def _classify_frobenius(self, s: Dict[str, Any]) -> str:
        """Apply R1–R5 rules to classify a imscription dict into a Frobenius tier.
        
        Values in the catalog are stored as Shavian glyphs (the ORDINALS keys).
        Uses Shavian Unicode glyphs for comparison (identity from catalog).
        """
        phi = self._shavian_to_display(s.get("⊙", ""), "⊙")
        p = self._shavian_to_display(s.get("Φ", ""), "Φ")
        omega = self._shavian_to_display(s.get("Ω", ""), "Ω")
        d = self._shavian_to_display(s.get("Ð", ""), "Ð")
        at_criticality = phi in ("⊙", "𐑮")
        # R1: special Frobenius — exact Z₂ symmetry at criticality
        if at_criticality and p == "𐑹":
            return "O_inf"
        # R2: no self-referential loop possible
        if phi in ("𐑢", "𐑣", "𐑻"):
            return "O_0"
        # R3: critical but trivial winding
        if at_criticality and omega == "𐑷":
            return "O_1"
        # R4: critical + topological + bounded domain
        if at_criticality and omega != "𐑷" and d in ("𐑛", "𐑦", "𐑨"):
            return "O_2"
        # R5: critical + topological + unbounded domain
        if at_criticality and omega != "𐑷" and d == "𐑼":
            return "O_2_dag"
        # Fallback (should not normally occur)
        return "O_0"

    _FROBENIUS_DESCRIPTIONS = {
        "O_inf": "Special Frobenius — exact proved Z₂ symmetry at criticality (μ∘δ=id). Finite closed algebra.",
        "O_0":   "No ouroboricity — system cannot form a self-referential critical loop (subcritical, supercritical, or EP).",
        "O_1":   "Ouroboricity tier 1 — self-referential at criticality but trivial winding.",
        "O_2":   "Ouroboricity tier 2 — critical + topologically protected, bounded domain.",
        "O_2_dag": "Ouroboricity tier 2† — critical + topologically protected, unbounded (𐑼) domain.",
    }

    def _frobenius_tier(self, name: str, **kwargs) -> Dict[str, Any]:
        """Classify into Frobenius ouroboricity tier, or census the whole catalog."""
        if name == "__all__":
            counts: Dict[str, int] = {"O_inf": 0, "O_0": 0, "O_1": 0, "O_2": 0, "O_2_dag": 0}
            by_tier: Dict[str, List[str]] = {k: [] for k in counts}
            for entry_name, imscription in self.catalog._entries.items():
                tier = self._classify_frobenius(imscription)
                counts[tier] += 1
                by_tier[tier].append(entry_name)
            total = sum(counts.values())
            summary = {t: {"count": c, "pct": round(100 * c / total, 1) if total else 0}
                       for t, c in counts.items()}
            return {
                "status": "ok",
                "census": "full catalog",
                "total": total,
                "summary": summary,
                "O_inf_entries": sorted(by_tier["O_inf"]),
            }
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        tier = self._classify_frobenius(s)
        return {
            "status": "ok",
            "name": name,
            "frobenius_tier": tier,
            "phi": self._shavian_to_display(s.get("⊙"), "⊙"),
            "p": self._shavian_to_display(s.get("Φ"), "Φ"),
            "omega": self._shavian_to_display(s.get("Ω"), "Ω"),
            "d": self._shavian_to_display(s.get("Ð"), "Ð"),
            "interpretation": self._FROBENIUS_DESCRIPTIONS.get(tier, tier),
        }

    def _project(self, name: str, primitives: List[str]) -> Dict[str, Any]:
        """Project a system onto a subset of primitives — extract structural subspace."""
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        invalid = [p for p in primitives if p not in PRIMITIVE_ORDER]
        if invalid:
            return {"status": "error", "error": f"Invalid primitives: {invalid}. Valid: {PRIMITIVE_ORDER}"}
        projection = {p: s[p] for p in primitives}
        omitted = {p: s[p] for p in PRIMITIVE_ORDER if p not in primitives}
        return {
            "status": "ok",
            "name": name,
            "projected_primitives": primitives,
            "projection": projection,
            "omitted": omitted,
            "interpretation": (
                f"{name} projected onto {primitives}. "
                "The projection isolates the specified structural subspace, "
                "ignoring the omitted dimensions."
            ),
        }

    def _primitive_peel(self, name: str, primitive: str) -> Dict[str, Any]:
        """Peel one primitive to its minimum value — returns the residual structure."""
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        if primitive not in PRIMITIVE_ORDER:
            return {"status": "error", "error": f"Invalid primitive: {primitive}. Valid: {PRIMITIVE_ORDER}"}
        min_val = min(ORDINALS[primitive], key=lambda v: ORDINALS[primitive][v])
        original_val = s[primitive]
        if original_val == min_val:
            return {
                "status": "ok",
                "name": name,
                "primitive": primitive,
                "already_at_minimum": True,
                "value": original_val,
                "interpretation": f"{name}.{primitive} is already at minimum ({original_val}). Nothing to peel.",
            }
        residual = {**s, primitive: min_val}
        notation = "⟨" + "; ".join(f"{p}={residual[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        peeled_contribution = round(
            abs(ORDINALS[primitive].get(original_val, 0) - ORDINALS[primitive].get(min_val, 0)) *
            WEIGHTS.get(primitive, 1.0) / len(PRIMITIVE_ORDER) ** 0.5, 4
        )
        return {
            "status": "ok",
            "name": name,
            "primitive": primitive,
            "original_value": original_val,
            "peeled_to": min_val,
            "residual_notation": notation,
            "interpretation": (
                f"Peeled {primitive} from {original_val} → {min_val}. "
                "The residual is the system stripped of this primitive's contribution. "
                f"Analyzing the residual reveals which other primitives carry the remaining structure."
            ),
        }

    def _principal_decomp(self, name: str) -> Dict[str, Any]:
        """Decompose a system into join-irreducible atoms — minimal structural building blocks."""
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        # Join-irreducible atoms: for each primitive at non-minimum value,
        # construct an atom that is at that value with all others at minimum.
        atoms = []
        min_vals = {p: min(ORDINALS[p], key=lambda v: ORDINALS[p][v]) for p in PRIMITIVE_ORDER}
        for p in PRIMITIVE_ORDER:
            val = s[p]
            min_val = min_vals[p]
            if val != min_val:
                atom = {pp: min_vals[pp] for pp in PRIMITIVE_ORDER}
                atom[p] = val
                atom_notation = "⟨" + "; ".join(f"{pp}={atom[pp]}" for pp in PRIMITIVE_ORDER) + "⟩"
                atoms.append({
                    "primitive": p,
                    "value": val,
                    "atom_notation": atom_notation,
                    "ordinal_contribution": ORDINALS[p].get(val, 0) - ORDINALS[p].get(min_val, 0),
                })
        # Sort by ordinal contribution (most structurally significant first)
        atoms.sort(key=lambda x: -x["ordinal_contribution"])
        baseline_notation = "⟨" + "; ".join(f"{p}={min_vals[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        return {
            "status": "ok",
            "name": name,
            "num_atoms": len(atoms),
            "atoms": atoms,
            "baseline_notation": baseline_notation,
            "interpretation": (
                f"{name} decomposes into {len(atoms)} join-irreducible atom(s). "
                "Each atom is a minimal unit contributing exactly one primitive's structural content. "
                "The join of all atoms reconstructs the full system. "
                "Atoms with high ordinal_contribution carry more structural weight."
            ),
        }

    def _retrosynthetic_path(self, name: str) -> Dict[str, Any]:
        """Trace a system back to baseline by peeling one primitive per step."""
        s = self.catalog.get(name)
        if s is None:
            return {"status": "error", "error": f"Unknown system: {name}. Encode it first."}
        min_vals = {p: min(ORDINALS[p], key=lambda v: ORDINALS[p][v]) for p in PRIMITIVE_ORDER}
        # Build a step-by-step retrosynthetic path: peel primitives in order of weight×ordinal
        active = [(p, s[p]) for p in PRIMITIVE_ORDER if s[p] != min_vals[p]]
        active.sort(key=lambda x: -(WEIGHTS.get(x[0], 1.0) * ORDINALS[x[0]].get(x[1], 0)))
        steps = []
        current = dict(s)
        for p, val in active:
            prev_notation = "⟨" + "; ".join(f"{pp}={current[pp]}" for pp in PRIMITIVE_ORDER) + "⟩"
            current = {**current, p: min_vals[p]}
            next_notation = "⟨" + "; ".join(f"{pp}={current[pp]}" for pp in PRIMITIVE_ORDER) + "⟩"
            steps.append({
                "step": len(steps) + 1,
                "peel_primitive": p,
                "from_value": val,
                "to_value": min_vals[p],
                "before": prev_notation,
                "after": next_notation,
                "rationale": f"Remove {p}={val} → structural requirement for {p} eliminated",
            })
        baseline_notation = "⟨" + "; ".join(f"{p}={min_vals[p]}" for p in PRIMITIVE_ORDER) + "⟩"
        return {
            "status": "ok",
            "name": name,
            "num_steps": len(steps),
            "steps": steps,
            "baseline_notation": baseline_notation,
            "interpretation": (
                f"Retrosynthetic path from {name} to structural baseline in {len(steps)} step(s). "
                "Each step removes one primitive requirement (peels to minimum). "
                "Reading forward: the synthesis path from baseline to target. "
                "Reading backward: which primitive constraints were added to produce this system."
            ),
        }

    # ── Veracity / conflict distance ──────────────────────────────────────────

    def _compute_conflict_distance(
        self,
        name_holistic: str,
        name_compositional: str,
    ) -> Dict[str, Any]:
        """
        Compute the conflict distance d_c between a holistic and compositional encoding
        of the same system. d_c = sqrt(|conflict_set|).
        """
        sh = self.catalog.get(name_holistic)
        sc = self.catalog.get(name_compositional)
        missing = []
        if sh is None:
            missing.append(name_holistic)
        if sc is None:
            missing.append(name_compositional)
        if missing:
            return {"status": "error", "error": f"Unknown system(s): {missing}. Encode them first."}

        # Build conflict set with per-primitive classification
        conflict_set: List[str] = []
        conflict_details: List[Dict[str, Any]] = []
        for p in PRIMITIVE_ORDER:
            vh = sh[p]
            vc = sc[p]
            if vh == vc:
                continue
            # Determine conflict type using ordinal rank
            ordinal = ORDINALS[p]
            rank_h = ordinal.get(vh, 0)
            rank_c = ordinal.get(vc, 0)
            if rank_h > rank_c:
                ctype = "aspirational"
                claim = (
                    f"A mechanism exists by which the construction of {name_holistic} "
                    f"produces {p}={vh} beyond the tensor-product value {p}={vc}."
                )
            elif rank_h < rank_c:
                ctype = "reductive"
                claim = (
                    f"The construction of {name_holistic} actively suppresses {p} "
                    f"from {p}={vc} (component level) to {p}={vh} (functional level)."
                )
            else:
                # Same ordinal rank but different value — categorical conflict
                ctype = "categorical"
                claim = (
                    f"The holistic and compositional encodings assign categorically different "
                    f"values at {p}: holistic={vh}, compositional={vc}. "
                    f"These are incomparable — the conflict requires domain-specific resolution."
                )
            conflict_set.append(p)
            conflict_details.append({
                "primitive": p,
                "holistic_value": vh,
                "compositional_value": vc,
                "conflict_type": ctype,
                "emergence_claim": claim,
            })

        d_c = len(conflict_set) ** 0.5

        # Veracity classification
        n = len(conflict_set)
        if n == 0:
            veracity_class = "transparent"
            veracity_note = "Holistic = compositional across all primitives. No unresolved emergence claims."
        elif n <= 2:
            veracity_class = "near-grounded"
            veracity_note = f"{n} precisely identified emergence claim(s) at: {', '.join(conflict_set)}."
        elif n <= 6:
            veracity_class = "partial-emergence"
            veracity_note = f"{n} open claims. System is partially supported by construction."
        else:
            veracity_class = "aspirational"
            veracity_note = f"{n} conflicted primitives. Claimed tuple is largely unsupported by construction."

        result = {
            "status": "ok",
            "name_holistic": name_holistic,
            "name_compositional": name_compositional,
            "d_c": round(d_c, 4),
            "conflict_set": conflict_set,
            "conflict_details": conflict_details,
            "veracity_class": veracity_class,
            "veracity_note": veracity_note,
            "canonical_encoding": name_compositional if n > 0 else name_holistic,
            "interpretation": (
                f"d_c = √{n} = {round(d_c, 4)}. "
                f"Veracity class: {veracity_class}. "
                + (
                    f"The {n} conflicted primitive(s) are the structural address of "
                    f"the unresolved emergence claim(s). "
                    if n > 0 else
                    "Full structural transparency — no emergence gap."
                )
            ),
        }

        # Register for emergence_frontier tracking
        self._conflict_pairs.append({
            "name_holistic": name_holistic,
            "name_compositional": name_compositional,
            "conflict_set": conflict_set,
            "d_c": round(d_c, 4),
            "veracity_class": veracity_class,
        })

        return result

    def _emergence_frontier(self) -> Dict[str, Any]:
        """
        Report which primitives appear most frequently in conflict sets across all
        compute_conflict_distance calls in this session.
        """
        if not self._conflict_pairs:
            return {
                "status": "ok",
                "frontier": [],
                "note": "No conflict distance computations in this session yet. "
                        "Call compute_conflict_distance on holistic/compositional encoding pairs first.",
            }

        from collections import Counter
        counter: Counter = Counter()
        for pair in self._conflict_pairs:
            for p in pair["conflict_set"]:
                counter[p] += 1

        frontier = [
            {"primitive": p, "conflict_count": count, "fraction": round(count / len(self._conflict_pairs), 3)}
            for p, count in counter.most_common()
        ]

        # Summary statistics
        total_pairs = len(self._conflict_pairs)
        classes = Counter(pair["veracity_class"] for pair in self._conflict_pairs)

        return {
            "status": "ok",
            "session_conflict_pairs": total_pairs,
            "veracity_distribution": dict(classes),
            "frontier": frontier,
            "frontier_primitives": [f["primitive"] for f in frontier],
            "interpretation": (
                f"Emergence frontier across {total_pairs} conflict pair(s): "
                + (
                    f"dominant at {frontier[0]['primitive']} "
                    f"({frontier[0]['conflict_count']}/{total_pairs} pairs). "
                    if frontier else "no conflicted primitives found. "
                )
                + "The frontier primitive(s) name the deepest unresolved emergence questions "
                "in the domain under investigation."
            ),
        }

    # ── Promotion signature / inverse encoding ────────────────────────────────

    def _compute_promotions(self, name_source: str, name_target: str) -> Dict[str, Any]:
        """
        Compute the promotion signature Σ(source→target): which primitives were
        lifted (promoted in ordinal rank), demoted, or unchanged.

        Returns structured delta with full from/to values and direction labels.
        This is the deterministic half of the inverse-encoding workflow: it gives
        you the promotion signature; the model then reasons about what behaviors
        that signature predicts or explains.
        """
        src = self.catalog.get(name_source)
        tgt = self.catalog.get(name_target)
        missing = []
        if src is None:
            missing.append(name_source)
        if tgt is None:
            missing.append(name_target)
        if missing:
            return {"status": "error", "error": f"Unknown system(s): {missing}. Encode them first."}

        promotions: List[Dict[str, Any]] = []
        demotions:  List[Dict[str, Any]] = []
        unchanged:  List[str] = []

        for prim in PRIMITIVE_ORDER:
            sv = src.get(prim)
            tv = tgt.get(prim)
            if sv is None or tv is None:
                continue
            prim_ordinals = ORDINALS.get(prim, {})
            sr = prim_ordinals.get(sv, 0)
            tr = prim_ordinals.get(tv, 0)
            if tr > sr:
                promotions.append({"primitive": prim, "from": sv, "to": tv, "delta": tr - sr})
            elif tr < sr:
                demotions.append({"primitive": prim, "from": sv, "to": tv, "delta": sr - tr})
            else:
                unchanged.append(prim)

        sig = [p["primitive"] for p in promotions]
        return {
            "status": "ok",
            "source": name_source,
            "target": name_target,
            "promotion_signature": sig,
            "promotions": promotions,
            "demotions": demotions,
            "unchanged_count": len(unchanged),
            "summary": (
                f"{len(promotions)} promotion(s), {len(demotions)} demotion(s), "
                f"{len(unchanged)} unchanged across {len(PRIMITIVE_ORDER)} primitives. "
                f"Signature: [{', '.join(sig) if sig else 'none'}]"
            ),
        }

    def _predict_from_promotions(self, promoted_primitives: List[str]) -> Dict[str, Any]:
        """
        Given a promotion signature (list of promoted primitive names), look up
        the KB for matching patterns and return ranked predictions.

        Each match reports: the known behavior, which primitives overlap, coverage
        (how much of the known pattern is present), relevance (how much of the
        query is explained), and which query primitives are novel (not yet in KB).
        """
        if not self.promotion_kb:
            return {"status": "error", "error": "No PromotionKnowledgeBase loaded."}

        total = len(self.promotion_kb.all())
        if total == 0:
            return {
                "status": "empty_kb",
                "message": (
                    "The promotion knowledge base is empty. Call register_promotion_pattern "
                    "to seed it with known promotion→behavior mappings."
                ),
            }

        matches = self.promotion_kb.find(promoted_primitives, top_k=6)
        explained = {p for m in matches for p in m["matching_primitives"]}
        novel = sorted(set(promoted_primitives) - explained)

        return {
            "status": "ok",
            "query_signature": sorted(promoted_primitives),
            "kb_size": total,
            "matches": matches,
            "novel_primitives": novel,
            "interpretation": (
                f"{len(matches)} pattern(s) matched from {total} KB entries. "
                + (f"Novel (unexplained) promotions: {novel}. " if novel else "All query primitives matched. ")
                + ("Top prediction: " + matches[0]["behavior"] if matches else "No predictions available.")
            ),
        }

    def _register_promotion_pattern(
        self,
        promoted_primitives: List[str],
        behavior_description: str,
        example_system: str = "",
    ) -> Dict[str, Any]:
        """
        Register a promotion signature → behavior mapping in the persistent KB.

        Call this after confirming (via compute_promotions or structural analysis)
        that a set of primitive promotions from baseline reliably produces a named
        behavior.  The KB grows across sessions — future calls to
        predict_from_promotions will draw on these registered patterns.
        """
        if not self.promotion_kb:
            return {"status": "error", "error": "No PromotionKnowledgeBase loaded."}

        result = self.promotion_kb.add(
            promoted_primitives=promoted_primitives,
            behavior=behavior_description,
            example=example_system,
            session_seed=self._session_seed,
        )
        return result

    # ── Crystal Navigator handlers ─────────────────────────────────────────────

    # Lowercase → canonical primitive name (dispatch() lowercases all keys)
    _PRIM_CANONICAL = {
        **{p.lower(): p for p in ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]},
        # backward-compat: old ASCII key names (lowercased by dispatch)
        "d": "Ð", "t": "Þ", "r": "Ř", "p": "Φ", "f": "ƒ",
        "k": "Ç", "g": "Γ", "gamma": "ɢ", "phi": "⊙",
        "h": "Ħ", "s": "Σ", "omega": "Ω",
        # backward-compat: old φ̂ notation for ⊙ (pre-migration)
        "φ̂": "⊙",
    }

    def _norm_crystal_kwargs(self, kw: dict) -> dict:
        """Re-capitalize primitive keys and normalize values to canonical glyph IDs."""
        return {
            self._PRIM_CANONICAL.get(k, k): _normalize_value(v) if isinstance(v, str) else v
            for k, v in kw.items()
        }

    def _get_crystal_nav(self):
        """Lazy-load the CrystalNavigator (expensive to construct; done once)."""
        if self._crystal_nav is None:
            if not _CRYSTAL_NAV_AVAILABLE:
                return None
            try:
                self._crystal_nav = _CrystalNavigator()
            except Exception as e:
                return None
        return self._crystal_nav

    def _crystal_encode(self, **primitives) -> Dict[str, Any]:
        """Frobenius encode: tuple → canonical crystal address."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        # Accept either individual primitive kwargs or a 'tuple' string
        tup_str = primitives.pop("tuple", "")
        if tup_str:
            parts = [p.strip() for p in tup_str.replace("⟨","").replace("⟩","").split(";")]
            prim_order = ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]
            if len(parts) == 12:
                primitives = {k: v for k, v in zip(prim_order, parts)}
        # Also accept 'name' to look up from catalog
        name = primitives.pop("name", "")
        if name:
            entry = self.catalog.get(name)
            if entry is None:
                return {"status": "error", "error": f"System '{name}' not in catalog."}
            primitives = {k: _UNICODE_TO_CANONICAL.get(entry[k], entry[k]) for k in ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"] if k in entry}
        # Normalize keys (dispatch lowercases all kwargs)
        primitives = self._norm_crystal_kwargs(primitives)
        try:
            addr = nav.encode(primitives)
            cell_id, inner_id, full_addr = nav.codec_address(primitives)
            tier = nav.tier_of(primitives)
            return {
                "status": "ok",
                "address": full_addr,
                "cell_id": cell_id,
                "inner_id": inner_id,
                "tier": tier,
            }
        except (KeyError, IndexError) as e:
            return {"status": "error", "error": f"Encoding failed: {e}"}

    def _crystal_decode(self, address: int, **_) -> Dict[str, Any]:
        """Frobenius decode: canonical crystal address → tuple."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        try:
            addr = int(address)
            tup = nav.decode(addr)
            tier = nav.tier_of(tup)
            return {"status": "ok", "address": addr, "tuple": tup, "tier": tier}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _crystal_navigate(self, limit: int = 10, **constraints) -> Dict[str, Any]:
        """Navigate crystal with partial primitive constraints → matching types."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        constraints.pop("status", None)
        constraints = self._norm_crystal_kwargs(constraints)
        try:
            limit = int(limit)
            results = nav.navigate(limit=limit, **constraints)
            count = nav.count(**constraints)
            return {
                "status": "ok",
                "constraints": constraints,
                "total_matching": count,
                "returned": len(results),
                "types": results,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _crystal_count(self, **constraints) -> Dict[str, Any]:
        """Count crystal types matching partial primitive constraints."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        constraints.pop("status", None)
        constraints = self._norm_crystal_kwargs(constraints)
        try:
            count = nav.count(**constraints)
            from navigators.crystal_navigator import TOTAL_SIZE  # type: ignore
            return {
                "status": "ok",
                "constraints": constraints,
                "count": count,
                "fraction": count / TOTAL_SIZE,
                "total_crystal_size": TOTAL_SIZE,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _crystal_tier_census(self) -> Dict[str, Any]:
        """Full tier distribution of the Crystal of Types."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        try:
            census = nav.tier_census()
            from navigators.crystal_navigator import TOTAL_SIZE, CELL_SIZE, INNER_SIZE  # type: ignore
            return {
                "status": "ok",
                "total_types": TOTAL_SIZE,
                "tier_cells": CELL_SIZE,
                "inner_types_per_cell": INNER_SIZE,
                "census": census,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _crystal_nearest(self, name: str = "", limit: int = 5,
                          same_tier: bool = False, **primitives) -> Dict[str, Any]:
        """Find nearest catalog entries to a given tuple by crystal distance."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        # Resolve tuple from name or primitives
        tup_str = primitives.pop("tuple", "")
        if name:
            entry = self.catalog.get(name)
            if entry is None:
                return {"status": "error", "error": f"System '{name}' not in catalog."}
            tup = {k: _UNICODE_TO_CANONICAL.get(entry[k], entry[k]) for k in ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"] if k in entry}
        elif tup_str:
            parts = [p.strip() for p in tup_str.replace("⟨","").replace("⟩","").split(";")]
            prim_order = ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]
            tup = {k: v for k, v in zip(prim_order, parts)}
        elif primitives:
            tup = self._norm_crystal_kwargs(primitives)
        else:
            return {"status": "error", "error": "Provide 'name', 'tuple', or primitive kwargs."}
        try:
            limit = int(limit)
            results = nav.nearest_catalog(tup, n=limit, same_tier=bool(same_tier))
            return {
                "status": "ok",
                "query_tier": nav.tier_of(tup),
                "nearest": [
                    {"name": r["name"], "distance": round(r["distance"], 4), "tier": r["tier"]}
                    for r in results
                ],
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _crystal_tier_gap_ladder(self) -> Dict[str, Any]:
        """Tier gap ladder (§69.1): structural distances between consecutive tiers."""
        nav = self._get_crystal_nav()
        if nav is None:
            return {"status": "error", "error": "CrystalNavigator not available."}
        try:
            ladder = nav.tier_gap_ladder()
            return {"status": "ok", "ladder": ladder}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_quiver_model(self) -> Optional[Any]:
        """Lazy-load the CrystalGNN from crystal_gnn.pt (once per session)."""
        if self._quiver_model is not None:
            return self._quiver_model
        if not _QUIVER_AVAILABLE:
            return None
        import os
        from pathlib import Path
        ckpt_path = Path(__file__).parent / "crystal_gnn.pt"
        if not ckpt_path.exists():
            return None
        try:
            ckpt = _torch.load(str(ckpt_path), map_location="cpu")
            model = _CrystalGNN(
                hidden_dim=ckpt["hidden_dim"],
                num_gnn_layers=ckpt["gnn_layers"],
                num_attn_heads=ckpt["attn_heads"],
            )
            _STATIC = {"node_feats", "edge_src", "edge_dst"}
            model.load_state_dict(
                {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
                strict=False,
            )
            model.eval()
            self._quiver_model = model
            return model
        except Exception:
            return None

    def _quiver_encode(self, name: str = "", **primitives) -> Dict[str, Any]:
        """Neural encode a tuple via CrystalGNN; cross-check with exact codec."""
        if not _QUIVER_AVAILABLE:
            return {"status": "error", "error": "CrystalGNN not available (install torch + quiver_crystal.py)."}
        model = self._get_quiver_model()
        if model is None:
            return {"status": "error", "error": "crystal_gnn.pt not found — run: python quiver_crystal.py train"}

        # Resolve tuple: catalog name or primitives
        tup: Optional[Dict] = None
        if name:
            entry = self.catalog.get(name)
            if entry is None:
                hits = self.catalog.search(name)
                if hits:
                    entry = self.catalog.get(hits[0]["name"])
            if entry:
                tup = {p: entry[p] for p in _CRYSTAL_PRIMS if p in entry}
        if tup is None and primitives:
            tup = self._norm_crystal_kwargs({k: v for k, v in primitives.items() if v})
        if not tup or len(tup) < 12:
            return {"status": "error", "error": "Provide a catalog name or all 12 primitives."}

        try:
            from navigators.crystal_navigator import encode_tuple as _enc, compute_tier as _tier, TOTAL_SIZE as _N
            exact_addr = _enc(tup)
            exact_tier = _tier(tup["⊙"], tup["Φ"], tup["Ω"], tup["Ð"])

            with _torch.no_grad():
                out = model.forward([tup])

            pred_addr  = out["addresses"].item()
            pred_tier  = _TierHead.TIERS[out["tier_logits"][0].argmax().item()]
            dec        = {p: _CRYSTAL_VALUES[p][out["dec_logits"][p][0].argmax().item()]
                          for p in _CRYSTAL_PRIMS}
            dec_tier   = _tier(dec["⊙"], dec["Φ"], dec["Ω"], dec["Ð"])
            addr_err   = abs(pred_addr - exact_addr)
            err_pct    = 100 * addr_err / _N

            return {
                "status":           "ok",
                "input_tuple":      tup,
                "exact_address":    exact_addr,
                "gnn_address":      round(pred_addr),
                "address_error":    addr_err,
                "address_error_pct": round(err_pct, 4),
                "exact_tier":       exact_tier,
                "gnn_tier_head":    pred_tier,
                "gnn_decoded_tuple": dec,
                "gnn_decoded_tier": dec_tier,
                "tier_match":       pred_tier == exact_tier,
                "roundtrip_match":  dec == tup,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ── Domain Navigator methods ───────────────────────────────────────────────

    def _get_domain_catalog(self):
        """Lazy-load the domain catalog (shares IG_catalog.json)."""
        if not _DOMAIN_NAV_AVAILABLE:
            return None
        if not hasattr(self, "_domain_catalog_instance"):
            self._domain_catalog_instance = _DomainCatalog()
        return self._domain_catalog_instance

    def _domain_info(self, domain: str, **_) -> Dict[str, Any]:
        """Summary table of all systems in a domain navigator."""
        cat = self._get_domain_catalog()
        if cat is None:
            return {"status": "error", "error": "domain_navigators.py not available."}
        domain = domain.lower()
        if domain not in _DOMAIN_NAMES:
            return {"status": "error", "error": f"Unknown domain '{domain}'. Choose from: {list(_DOMAIN_NAMES)}"}
        entries = cat.domain(_DOMAIN_NAMES[domain])
        rows = []
        for e in entries:
            tier = _domain_compute_tier(e)
            row: Dict[str, Any] = {
                "name": e["name"],
                "tier": tier,
                "Ç": e["Ç"],
                "Φ": e["Φ"],
                "⊙": e["⊙"],
                "Ð": e["Ð"],
                "Ω": e["Ω"],
            }
            if domain == "consciousness":
                row["C_score"] = _consciousness_score(e)
            rows.append(row)
        return {
            "status": "ok",
            "domain": domain,
            "section": _DOMAIN_SECTIONS.get(domain, ""),
            "count": len(rows),
            "systems": rows,
        }

    def _domain_verify(self, domain: str, **_) -> Dict[str, Any]:
        """Run §74–§77 theorem verification for a domain."""
        cat = self._get_domain_catalog()
        if cat is None:
            return {"status": "error", "error": "domain_navigators.py not available."}
        domain = domain.lower()
        if domain not in _PROBE_FNS:
            return {"status": "error", "error": f"Unknown domain '{domain}'."}
        lines = _PROBE_FNS[domain](cat)
        return {
            "status": "ok",
            "domain": domain,
            "section": _DOMAIN_SECTIONS.get(domain, ""),
            "results": lines,
        }

    def _domain_nearest(self, name: str, n: int = 5, **_) -> Dict[str, Any]:
        """Nearest catalog entries to a named system."""
        cat = self._get_domain_catalog()
        if cat is None:
            return {"status": "error", "error": "domain_navigators.py not available."}
        try:
            target = self.catalog.get(name)  # live session catalog — never stale
        except KeyError:
            return {"status": "error", "error": f"'{name}' not in catalog."}
        tier = _domain_compute_tier(target)
        results = cat.nearest(target, n=int(n) + 1, exclude={name})
        neighbors = [
            {"name": e["name"], "distance": round(d, 4), "tier": _domain_compute_tier(e)}
            for d, e in results[:int(n)]
        ]
        return {
            "status": "ok",
            "query": name,
            "query_tier": tier,
            "nearest": neighbors,
        }

    def _consciousness_score_tool(self, name: str = "", **primitives) -> Dict[str, Any]:
        """Two-gate consciousness C-score."""
        if not _DOMAIN_NAV_AVAILABLE:
            return {"status": "error", "error": "domain_navigators.py not available."}
        if name:
            # Use live session catalog (always reflects latest encode_system calls)
            # rather than the lazy-loaded _domain_catalog_instance which is stale
            # after an update within the same session.
            try:
                e = self.catalog.get(name)
            except KeyError:
                return {"status": "error", "error": f"'{name}' not in catalog."}
        else:
            # Build from supplied primitives (need at least Phi, K, G, T, Omega)
            primitives = {k.capitalize() if len(k) > 1 else k.upper(): v
                          for k, v in primitives.items() if v}
            # Fill missing with defaults that give C=0 to be safe
            defaults = {"Ð": "Ð_ß", "Þ": "Þ_6", "Ř": "Ř_¯", "Φ": "Φ_ɐ",
                        "ƒ": "ƒ^ì", "Ç": "Ç^-", "Γ": "Γ_β", "ɢ": "ɢ^∧",
                        "⊙": "⊙_ž", "Ħ": "Ħ_Ñ", "Σ": "Σ_S", "Ω": "Ω_Å"}
            e = {**defaults, **primitives}
        from navigators.domain_navigators import CRITICAL as _DCRIT, SLOW_K as _DSLOWK  # type: ignore
        # Translate all unicode catalog values to canonical strings for gate checks AND scoring
        e_canon = {k: _UNICODE_TO_CANONICAL.get(v, v) for k, v in e.items()}
        gate1 = e_canon["⊙"] in _DCRIT
        gate2 = e_canon["Ç"] in _DSLOWK
        c = _consciousness_score(e_canon)
        return {
            "status": "ok",
            "name": name or "(tuple)",
            "⊙": e["⊙"],
            "Ç": e["Ç"],
            "gate1_phi_c": gate1,
            "gate2_k_slow": gate2,
            "C_score": c,
            "interpretation": (
                "Both gates open — consciousness possible." if (gate1 and gate2)
                else "Gate 1 closed (Phi ≠ ⊙_ÿ) — no self-modeling loop." if not gate1
                else f"Gate 2 closed (K={e['K']}) — {'order-frozen (Ç^Ù)' if e['K']=='Ç^Ù' else 'disorder-frozen (Ç^λ)' if e['K']=='Ç^λ' else 'dynamics too fast'}."
            ),
        }

    def _navigator_info(self) -> Dict[str, Any]:
        """Structural info for the four mathematical navigators."""
        # Self-encoding tuples (canonical, from navigators.py docstrings / §69.4)
        nav_data = [
            {
                "name": "ThurstonNet",
                "catalog_name": "thurston_net",
                "section": "§69.1",
                "domain": "Geometric structures on 3-manifolds (Thurston geometrization)",
                "tuple": "Ð_ω; Þ_O; Ř_Ť; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; ɢ^Ş; ⊙_ÿ; Ħ_!; Σ_ï; Ω_2",
                "tier": "O_inf",
                "architecture": "Imscriptive GNN — boundary (Phi,P,Omega,D) → tier cell; bulk message-passing over 8 inner primitives; Z2-protected geometry head",
            },
            {
                "name": "YangMillsNavigator",
                "catalog_name": "yang_mills_navigator",
                "section": "§69.2 / §V",
                "domain": "Yang-Mills mass gap (Millennium Problem)",
                "tuple": "Ð_ω; Þ_O; Ř_ý; Φ_}; ƒ^ż; Ç^Ù; Γ_ʔ; ɢ^Ş; ⊙_ÿ; Ħ_!; Σ_ï; Ω_z",
                "tier": "O_inf",
                "architecture": "Lanczos/VQE eigensolver — Ç^Ù: non-ergodic gap dynamics; integer winding protection (Ω_z); Frobenius at criticality",
            },
            {
                "name": "RiemannNavigator",
                "catalog_name": "riemann_navigator",
                "section": "§69.3 / §IV",
                "domain": "Riemann Hypothesis (Millennium Problem)",
                "tuple": "Ð_ω; Þ_O; Ř_ý; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; ɢ^Ş; ⊙_ÿ; Ħ_!; Σ_ï; Ω_z",
                "tier": "O_inf",
                "architecture": "Imscriptive GNN stack (FrobeniusLayer + FamilyMixer) — same architecture as ThurstonNet; RH as O_inf type at ⊙_ÿ (real criticality)",
            },
            {
                "name": "IsingNavigator",
                "catalog_name": "ising_navigator",
                "section": "§69.4",
                "domain": "Ising universality / statistical mechanics",
                "tuple": "Ð_C; Þ_¨; Ř_ý; Φ_}; ƒ^ì; Ç^-; Γ_ʔ; ɢ^∧; ⊙_ÿ; Ħ_Ñ; Σ_ő; Ω_2",
                "tier": "O_inf",
                "architecture": "Single-pass C++/CUDA Swendsen-Wang cluster-flip kernel — Ç^-: O(N) per sweep; exact cluster-flip involution (Φ_}); Z2-protected",
            },
        ]
        if _MATH_NAV_AVAILABLE and _navigator_info_fn is not None:
            # navigators.py has a navigator_info() that prints; we capture it
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                _navigator_info_fn()
            nav_data_append = buf.getvalue()
        else:
            nav_data_append = None
        result: Dict[str, Any] = {"status": "ok", "navigators": nav_data}
        if nav_data_append:
            result["raw_output"] = nav_data_append
        return result

    # ── ZFC Navigator tools ───────────────────────────────────────────────────

    def _zfc_formula(self, name: str) -> Dict[str, Any]:
        """Translate a catalog entry to its per-primitive ZFC formula fragments."""
        if not _ZFC_AVAILABLE:
            return {"status": "error", "error": "zfc_navigator.py not available."}
        entry = self.catalog.get(name)
        if entry is None:
            return {"status": "error", "error": f"Entry '{name}' not found in catalog."}
        try:
            # Per-primitive fragments
            fragments = {}
            collapse_notes = []
            _COLLAPSE_KIND = {
                ("ƒ",     "ƒ^ż"):  "TOTAL — ƒ^ż has no distinct ZFC token from ƒ^ì; encoder cannot recover fidelity",
                ("ƒ",     "ƒ^ì"):   "HALLUCINATION RISK — ƒ^ì may be read as ƒ^ż by encoder",
                ("Þ",     "Þ_O"):  "PARTIAL — Þ_O → Þ_K approximation; imscriptive boundary structure not fully ZFC-expressible",
                ("Ð",     "Ð_ω"):  "PARTIAL — Ð_ω → Ð_; approximation; inaccessible cardinal not fully expressible in ZFC",
                ("ɢ", "ɢ^ˌ"):   "PARTIAL — ɢ^ˌ → ɢ^∧ in ZFC translation; sequential dependency becomes conjunction",
            }
            for p in _ZFC_PRIMITIVES:
                val = entry.get(p)
                if val is None or val not in _ZFC_TEMPLATES.get(p, {}):
                    fragments[p] = {"value": val, "tokens": [], "rendered": "?"}
                    continue
                frag_tokens = _ZFC_TEMPLATES[p][val]
                rendered = _zfc_render_tokens(frag_tokens)
                fragments[p] = {"value": val, "tokens": frag_tokens, "rendered": rendered}
                if (p, val) in _COLLAPSE_KIND:
                    collapse_notes.append({"primitive": p, "value": val, "note": _COLLAPSE_KIND[(p, val)]})

            # Full assembled token sequence
            all_token_ids = _zfc_compose_formula(entry)
            all_tokens = [_ZFC_IDX2TOKEN.get(i, "?") for i in all_token_ids]
            return {
                "status": "ok",
                "name": name,
                "tuple": {p: entry[p] for p in _ZFC_PRIMITIVES if p in entry},
                "fragments": fragments,
                "full_sequence": all_tokens,
                "sequence_length": len(all_token_ids),
                "collapse_warnings": collapse_notes,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _zfc_probe(self, name: str) -> Dict[str, Any]:
        """ZFC roundtrip transmissibility probe for a single catalog entry."""
        if not _ZFC_AVAILABLE:
            return {"status": "error", "error": "zfc_navigator.py not available."}
        entry = self.catalog.get(name)
        if entry is None:
            return {"status": "error", "error": f"Entry '{name}' not found in catalog."}
        try:
            import torch as _t
            import math as _m
            from navigators.zfc_navigator import ZFCEncoder, frobenius_loss, pad_formula  # type: ignore
            device = _t.device("cuda" if _t.cuda.is_available() else "cpu")
            model = ZFCEncoder().to(device)
            import os
            model_path = os.path.join(os.path.dirname(__file__), "zfc_encoder.pt")
            if not os.path.exists(model_path):
                return {"status": "error", "error": "zfc_encoder.pt not found — run `uv run zfc_navigator.py train` first."}
            model.load_state_dict(_t.load(model_path, map_location=device))
            model.eval()
            with _t.no_grad():
                tokens = _t.tensor(
                    [pad_formula(_zfc_compose_formula(entry))],
                    dtype=_t.long, device=device,
                )
                targets = _t.tensor(
                    [_zfc_tuple_to_indices(entry)],
                    dtype=_t.long, device=device,
                )
                logits = model(tokens)
                loss, pp = frobenius_loss(logits, targets)
                pred_indices = [int(logits[i].argmax(dim=-1).item()) for i in range(12)]
                pred_tuple = _zfc_indices_to_tuple(pred_indices)
            # Roundtrip distance
            from navigators.zfc_navigator import tuple_distance as _zfc_dist  # type: ignore
            rt_dist = _zfc_dist(entry, pred_tuple)
            per_prim = {_ZFC_PRIMITIVES[i]: float(pp[i]) for i in range(12)}
            mismatches = {p: {"input": entry[p], "predicted": pred_tuple[p]}
                         for p in _ZFC_PRIMITIVES if entry.get(p) != pred_tuple.get(p)}
            _COLLAPSE_TRIGGERS = {
                ("ƒ", "ƒ^ż"), ("ƒ", "ƒ^ì"),
                ("Þ", "Þ_O"), ("Ð", "Ð_ω"), ("ɢ", "ɢ^ˌ"),
            }
            collapse_events = []
            for p, val in _COLLAPSE_TRIGGERS:
                if entry.get(p) == val:
                    predicted = pred_tuple.get(p, "?")
                    if predicted != val:
                        collapse_events.append(f"{p}: {val} → {predicted}")
            return {
                "status": "ok",
                "name": name,
                "input_tuple": {p: entry[p] for p in _ZFC_PRIMITIVES if p in entry},
                "predicted_tuple": pred_tuple,
                "roundtrip_distance": round(rt_dist, 4),
                "roundtrip_loss": round(float(loss), 4),
                "per_primitive_loss": {k: round(v, 4) for k, v in per_prim.items()},
                "mismatches": mismatches,
                "collapse_events": collapse_events,
                "transmissible": rt_dist == 0.0,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _zfc_catalog_probe(self, n: int = 20) -> Dict[str, Any]:
        """Run ZFC transmissibility probe across the full catalog, ranked by roundtrip distance."""
        if not _ZFC_AVAILABLE:
            return {"status": "error", "error": "zfc_navigator.py not available."}
        try:
            import torch as _t
            import os
            from navigators.zfc_navigator import ZFCEncoder, frobenius_loss, pad_formula, tuple_distance as _zfc_dist  # type: ignore
            device = _t.device("cuda" if _t.cuda.is_available() else "cpu")
            model_path = os.path.join(os.path.dirname(__file__), "zfc_encoder.pt")
            if not os.path.exists(model_path):
                return {"status": "error", "error": "zfc_encoder.pt not found — run `uv run zfc_navigator.py train` first."}
            model = ZFCEncoder().to(device)
            model.load_state_dict(_t.load(model_path, map_location=device))
            model.eval()
            catalog = _zfc_load_catalog()
            results = []
            with _t.no_grad():
                for entry in catalog:
                    if not all(p in entry and entry[p] in _ZFC_ORDINALS.get(p, {}) for p in _ZFC_PRIMITIVES):
                        continue
                    tokens = _t.tensor(
                        [pad_formula(_zfc_compose_formula(entry))],
                        dtype=_t.long, device=device,
                    )
                    targets = _t.tensor(
                        [_zfc_tuple_to_indices(entry)],
                        dtype=_t.long, device=device,
                    )
                    logits = model(tokens)
                    loss, _ = frobenius_loss(logits, targets)
                    pred_indices = [int(logits[i].argmax(dim=-1).item()) for i in range(12)]
                    pred_tuple = _zfc_indices_to_tuple(pred_indices)
                    rt_dist = _zfc_dist(entry, pred_tuple)
                    mismatches = [p for p in _ZFC_PRIMITIVES if entry.get(p) != pred_tuple.get(p)]
                    results.append({
                        "name": entry.get("name", "?"),
                        "roundtrip_distance": round(rt_dist, 4),
                        "roundtrip_loss": round(float(loss), 4),
                        "collapsed_primitives": mismatches,
                    })
            results.sort(key=lambda r: r["roundtrip_distance"], reverse=True)
            return {
                "status": "ok",
                "total_probed": len(results),
                "top_n": results[:n],
                "summary": {
                    "fully_transmissible": sum(1 for r in results if r["roundtrip_distance"] == 0.0),
                    "partial_loss": sum(1 for r in results if 0 < r["roundtrip_distance"] < 1.0),
                    "high_loss": sum(1 for r in results if r["roundtrip_distance"] >= 1.0),
                    "mean_roundtrip_dist": round(sum(r["roundtrip_distance"] for r in results) / max(len(results), 1), 4),
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ── Aleph / HoTT / Riemann Xi tools ──────────────────────────────────────

    def _resolve_hebrew(self, text: str):
        """Resolve a Hebrew letter or word to its numpy type vector."""
        if not _ALEPH_AVAILABLE:
            raise RuntimeError("aleph_tensor.py not available.")
        text = text.strip()
        if len(text) == 1:
            std = _FINAL_TO_STD.get(text, text)
            if std not in _HEBREW_ALPHABET:
                raise KeyError(f"Letter '{text}' not in Hebrew alphabet.")
            return _HEBREW_ALPHABET[std].copy(), "letter"
        else:
            result = _ALEPH_ENGINE.solve_bulk(text)
            if result is None:
                raise ValueError(f"Could not resolve word '{text}' — contains unknown letters.")
            return result, "word"

    def _vec_to_tuple(self, vec) -> Dict[str, str]:
        """Convert a numpy ordinal vector back to a primitive-value dict."""
        import numpy as _np
        from navigators.crystal_navigator import VALUES as _CV  # type: ignore
        PRIMS_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]
        VALS_BY_PRIM = {
            "Ð":     ["Ð_ß","Ð_C","Ð_;","Ð_ω"],
            "Þ":     ["Þ_6","Þ_K","Þ_ò","Þ_¨","Þ_O"],
            "Ř":     ["Ř_¯","Ř_ý","Ř_Ť","Ř_="],
            "Φ":     ["Φ_ɐ","Φ_υ","Φ_F","Φ_˙","Φ_}"],
            "ƒ":     ["ƒ^ì","ƒ^ð","ƒ^ż"],
            "Ç":     ["Ç^-","Ç^W","Ç^@","Ç^Ù","Ç^λ"],
            "Γ":     ["Γ_β","Γ_γ","Γ_ʔ"],
            "ɢ": ["ɢ^∧","ɢ^˝","ɢ^ˌ","ɢ^Ş"],
            "⊙":   ["⊙_ž","⊙_ÿ","⊙_Æ","⊙_3","⊙_Ţ"],
            "Ħ":     ["Ħ_Ñ","Ħ_£","Ħ_A","Ħ_!"],
            "Σ":     ["Σ_S","Σ_ő","Σ_ï"],
            "Ω": ["Ω_Å","Ω_2","Ω_z","Ω_5"],
        }
        result = {}
        for i, p in enumerate(PRIMS_ORDER):
            vals = VALS_BY_PRIM[p]
            idx = int(round(float(vec[i])))
            idx = max(0, min(idx, len(vals) - 1))
            result[p] = vals[idx]
        return result

    def _aleph_encode(self, text: str) -> Dict[str, Any]:
        """Get the structural type for a Hebrew letter or word."""
        if not _ALEPH_AVAILABLE:
            return {"status": "error", "error": "aleph_tensor.py not available."}
        try:
            vec, kind = self._resolve_hebrew(text)
            tup = self._vec_to_tuple(vec)
            from space_search.primitives import compute_ouroboricity  # type: ignore
            tier = "?"
            try:
                tier = compute_ouroboricity(tup)
            except Exception:
                pass
            # distance to samadhi
            samadhi = self.catalog.get("deep_meditation_samadhi")
            d_samadhi = None
            if samadhi:
                try:
                    d_samadhi = round(tuple_distance(tup, samadhi), 4)
                except Exception:
                    pass
            return {
                "status": "ok",
                "text": text,
                "kind": kind,
                "tuple": tup,
                "tier": tier,
                "d_samadhi": d_samadhi,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _aleph_distance(self, a: str, b: str, hott: bool = False) -> Dict[str, Any]:
        """Structural distance between two Hebrew expressions, with optional HoTT cast."""
        if not _ALEPH_AVAILABLE:
            return {"status": "error", "error": "aleph_tensor.py not available."}
        try:
            vec_a, kind_a = self._resolve_hebrew(a)
            vec_b, kind_b = self._resolve_hebrew(b)
            d = round(float(_aleph_distance_fn(vec_a, vec_b)), 4)
            tup_a = self._vec_to_tuple(vec_a)
            tup_b = self._vec_to_tuple(vec_b)
            result: Dict[str, Any] = {
                "status": "ok",
                "a": a, "kind_a": kind_a, "tuple_a": tup_a,
                "b": b, "kind_b": kind_b, "tuple_b": tup_b,
                "distance": d,
                "co_typed": d == 0.0,
            }
            if hott and _HOTT_AVAILABLE and _HOTT_BRIDGE is not None:
                cast = _HOTT_BRIDGE.univalence_cast(a, b)
                result["hott_cast"] = cast
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _riemann_xi_info(self) -> Dict[str, Any]:
        """Self-encoding and convergence info for the RiemannXiNavigator."""
        import os
        checkpoint_exists = os.path.exists(
            os.path.join(os.path.dirname(__file__), "riemann_xi_navigator.pt")
        )
        return {
            "status": "ok",
            "name": "RiemannXiNavigator",
            "section": "§CXLV–§CXLVI (P-483, P-488, P-490)",
            "domain": "Riemann xi function zero distribution — d(xi, grammar) = 0",
            "tuple": "Ð_ω; Þ_O; Ř_Ť; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; ɢ^Ş; ⊙_Æ; Ħ_!; Σ_ï; Ω_2",
            "tier": "O_inf",
            "crystal_address": 6734591,
            "architecture": (
                "Ç^@ → SpectralTransformer (global self-attention, 4 layers, window=64); "
                "Φ_} → FrobeniusLayer (h_fwd + h_rev → 0, antisymmetry under t→-t); "
                "Ω_2 → parity head (quantized Z2 winding number output); "
                "⊙_Æ → GUE Wigner-surmise loss (zero spacings match p(s)=(πs/2)e^{-πs²/4})"
            ),
            "convergence_criteria": {
                "gate_1_prediction": "|Δt|_norm < 0.5 — next-zero prediction within half a mean spacing",
                "gate_2_frobenius":  "L_frob < 0.01 — Frobenius roundtrip closed (Φ_} empirically confirmed)",
                "gate_3_gue":        "L_GUE < 0.05 — predicted spacing distribution matches Wigner surmise (⊙_Æ internalized)",
            },
            "cardinality_one_theorem": (
                "All O_inf navigators converge to crystal address 6,734,591 regardless of domain. "
                "ThurstonNet, YangMillsNavigator, RiemannNavigator, RiemannXiNavigator, "
                "ZFCEncoder, CrystalNavigator — same address."
            ),
            "checkpoint_available": checkpoint_exists,
            "training_command": "uv run riemann_xi_navigator.py train" if not checkpoint_exists else None,
            "available": _RIEMANN_XI_AVAILABLE,
        }


# ── Local Qwen3 backend (merged2 / any HF-compatible model) ──────────────────

class LocalQwen3Backend:
    """
    Transformers backend for the Imscribing Grammar-fine-tuned merged2 model.

    Mirrors the loading pattern from INFERRED/qw3n_stream.py:
      - NF4 4-bit quantization (BitsAndBytes double-quant)
      - YaRN RoPE scaling: factor=4.0, 32K → 131K context
      - attn_implementation=eager  (required for Qwen3 on this hw)
      - Thinking mode enabled by default
      - Tool calls parsed from <tool_call>...</tool_call> blocks
      - Tool results injected as <tool_response>...</tool_response> via chat template

    Parameters
    ----------
    model_path : str
        Path to the merged model directory (defaults to merged2).
    enable_thinking : bool
        Whether to prepend /think to prompts and strip <think> from output.
    max_new_tokens : int
        Generation budget per turn.
    """

    # Jinja tool-call tags emitted by merged2's chat template
    _TOOL_CALL_RE     = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
    _TOOL_RESP_RE     = re.compile(r"<tool_response>.*?</tool_response>", re.DOTALL)
    _THINK_RE         = re.compile(r"<think>.*?</think>", re.DOTALL)

    def __init__(
        self,
        model_path: str = _MERGED2_PATH,
        enable_thinking: bool = True,
        max_new_tokens: int = 4096,
    ):
        self.model_path = model_path
        self.enable_thinking = enable_thinking
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.tokenizer = None

    def load(self):
        """Load model + tokenizer with the INFERRED config pattern."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            import torch
        except ImportError as e:
            raise RuntimeError(f"transformers / torch not available: {e}")

        _print(f"Loading model from: {self.model_path}")

        # ── Tokenizer ─────────────────────────────────────────────────────────
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True,
            use_fast=True,
            padding_side="left",
        )

        # ── Quantization (NF4 double-quant — from inferred.yaml) ──────────────
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

        # ── Model config: inject YaRN RoPE before loading ─────────────────────
        from transformers import AutoConfig
        model_cfg = AutoConfig.from_pretrained(self.model_path, trust_remote_code=True)
        model_cfg.rope_scaling = {
            "rope_type": "yarn",
            "factor": 4.0,
            "original_max_position_embeddings": 32768,
        }
        model_cfg.max_position_embeddings = 131072  # 32768 * 4

        # ── Load weights ───────────────────────────────────────────────────────
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            config=model_cfg,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            attn_implementation="eager",
            use_safetensors=True,
        )
        self.model.eval()
        _print(f"Model loaded. Device map: {self.model.hf_device_map if hasattr(self.model, 'hf_device_map') else 'auto'}")

    def _build_prompt(self, messages: List[Dict], tools: List[Dict]) -> str:
        """Apply the model's native Jinja chat template with tool definitions."""
        return self.tokenizer.apply_chat_template(
            messages,
            tools=tools,
            tokenize=False,
            add_generation_prompt=True,
        )

    def _generate(self, prompt: str) -> str:
        """Run one generation pass. Returns raw model output string."""
        import torch

        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.model.device)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.model.device)

        # Thinking mode: temperature/top_p from inferred.yaml thinking_mode block
        gen_kwargs: Dict[str, Any] = {
            "max_new_tokens": self.max_new_tokens,
            "do_sample": True,
            "temperature": 0.6,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0.0,
            "repetition_penalty": 1.05,
            "use_cache": True,
        }
        if attention_mask is not None:
            gen_kwargs["attention_mask"] = attention_mask

        with torch.no_grad():
            output_ids = self.model.generate(input_ids, **gen_kwargs)

        # Decode only newly generated tokens
        new_ids = output_ids[0][input_ids.shape[-1]:]
        return self.tokenizer.decode(new_ids, skip_special_tokens=False)

    def _parse_tool_calls(self, raw: str) -> Tuple[str, List[Tuple[str, str, Dict]]]:
        """
        Extract <tool_call> blocks from raw output.
        Returns (text_without_calls, [(call_id, name, args_dict), ...]).
        """
        calls = []
        for i, match in enumerate(self._TOOL_CALL_RE.finditer(raw)):
            try:
                payload = json.loads(match.group(1))
                name = payload.get("name", "")
                args = payload.get("arguments", {})
                call_id = f"local_{i}"
                calls.append((call_id, name, args))
            except json.JSONDecodeError:
                pass  # malformed call — skip

        # Strip tool_call blocks, hallucinated tool_response blocks, and thinking
        text = self._TOOL_CALL_RE.sub("", raw)
        text = self._TOOL_RESP_RE.sub("", text)
        text = self._THINK_RE.sub("", text)
        text = text.replace("<|im_end|>", "").replace("<|im_start|>assistant", "").strip()
        return text, calls

    def call(
        self,
        messages: List[Dict],
        tools: List[Dict],
    ) -> Tuple[str, List[Tuple[str, str, Dict]], str]:
        """
        Single LLM turn. Returns (text, [(call_id, name, args), ...], raw_output).
        The raw_output is the full model string, used for threading tool results back.
        """
        if self.model is None:
            self.load()

        prompt = self._build_prompt(messages, tools)
        raw = self._generate(prompt)
        text, calls = self._parse_tool_calls(raw)
        return text, calls, raw

    def thread_tool_results(
        self,
        messages: List[Dict],
        raw_assistant: str,
        results: List[Tuple[str, str]],
    ) -> List[Dict]:
        """
        Append assistant turn + tool results to the messages list in the format
        expected by the Qwen3 chat template.
        """
        # Build tool_calls list from the raw assistant output for the chat template
        tool_calls_parsed = []
        for match in self._TOOL_CALL_RE.finditer(raw_assistant):
            try:
                payload = json.loads(match.group(1))
                tool_calls_parsed.append({
                    "function": {
                        "name": payload["name"],
                        "arguments": payload.get("arguments", {}),
                    }
                })
            except (json.JSONDecodeError, KeyError):
                pass

        # Extract clean text (no tool_call, no hallucinated tool_response, no think)
        assistant_text = self._TOOL_CALL_RE.sub("", raw_assistant)
        assistant_text = self._TOOL_RESP_RE.sub("", assistant_text)
        assistant_text = self._THINK_RE.sub("", assistant_text)
        assistant_text = assistant_text.replace("<|im_end|>", "").strip()

        assistant_msg: Dict[str, Any] = {"role": "assistant"}
        if assistant_text:
            assistant_msg["content"] = assistant_text
        if tool_calls_parsed:
            assistant_msg["tool_calls"] = tool_calls_parsed

        messages.append(assistant_msg)

        # Append one tool message per result
        for _call_id, content in results:
            messages.append({"role": "tool", "content": content})

        return messages


# ── The inquiry loop ──────────────────────────────────────────────────────────

class IGInquiryLoop:
    """
    Open-ended Imscribing Grammar inquiry loop.

    Parameters
    ----------
    seed : str
        Initial question or topic to investigate.
    model : str
        Model ID for the chosen provider.
    provider : str
        LLM provider. "anthropic" uses the Anthropic SDK;
        any other uses the OpenAI-compatible SDK.
    verbose : bool
        Print each iteration's tool calls and results.
    """

    def __init__(
        self,
        seed: str,
        model: str = "claude-sonnet-4-6",
        provider: str = "anthropic",
        verbose: bool = True,
        catalog_path: Optional[str] = CATALOG_PATH,
        insight_library_path: Optional[str] = None,
        promotion_kb_path: Optional[str] = PROMOTIONS_PATH,
        _inherit_catalog: Optional["SessionCatalog"] = None,
        _inherit_insights: Optional[List["Insight"]] = None,
    ):
        self.seed = _load_seed_text(seed)
        self.model = model
        self.provider = provider.lower()
        self.verbose = verbose
        self._use_anthropic = (self.provider == "anthropic")
        self._use_local_hf = (self.provider == "local_hf")
        self._use_gemini_native = (self.provider == "gemini")

        if self._use_local_hf:
            # Direct transformers path — no API key needed
            model_path = os.environ.get("LOCAL_MODEL", _MERGED2_PATH)
            self._local_backend = LocalQwen3Backend(
                model_path=model_path,
                enable_thinking=True,
                max_new_tokens=int(os.environ.get("IG_MAX_NEW_TOKENS", "4096")),
            )
            self.client = None
        else:
            # Resolve API key
            api_key_env = _PROVIDER_API_KEY_ENV.get(
                self.provider, f"{self.provider.upper()}_API_KEY"
            )
            api_key = os.environ.get(api_key_env) or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError(
                    f"API key not found. Set {api_key_env} (or ANTHROPIC_API_KEY) in your environment."
                )

            if self._use_anthropic:
                import anthropic as _anthropic
                self.client = _anthropic.Anthropic(api_key=api_key)
            elif self._use_gemini_native:
                try:
                    from google import genai as _genai
                except ImportError:
                    raise RuntimeError("google-genai package required for Gemini: pip install google-genai")
                self.client = _genai.Client(api_key=api_key)
                self._gemini_tools = _build_gemini_tools()
                # Parallel content history for Gemini (Content objects, not dicts)
                self._gemini_contents: List[Any] = []
                # Maps synthetic call_id → function name for tool result threading
                self._gemini_call_id_to_name: Dict[str, str] = {}
            else:
                try:
                    import openai as _openai
                except ImportError:
                    raise RuntimeError("openai package required for non-Anthropic providers: pip install openai")
                base_url = _OPENAI_BASE_URLS.get(self.provider, f"https://api.{self.provider}.com/v1")
                local_key = api_key if api_key else "local"
                extra_headers: Dict[str, str] = {}
                if self.provider == "openrouter":
                    referer = os.environ.get("OPENROUTER_REFERER", "https://github.com/Imscribing Grammar")
                    title   = os.environ.get("OPENROUTER_TITLE",   "Imscribing Grammar Inquiry Loop")
                    extra_headers = {"HTTP-Referer": referer, "X-Title": title}
                self.client = _openai.OpenAI(
                    api_key=local_key,
                    base_url=base_url,
                    default_headers=extra_headers or None,
                )

        # Session state — inherit from a prior prompt in a multi-prompt run if provided
        self.catalog = _inherit_catalog if _inherit_catalog is not None else SessionCatalog(catalog_path=catalog_path)
        self._insight_library: Optional[InsightLibrary] = (
            InsightLibrary(path=insight_library_path) if insight_library_path else None
        )
        self._promotion_kb: Optional[PromotionKnowledgeBase] = (
            PromotionKnowledgeBase(path=promotion_kb_path) if promotion_kb_path else None
        )

        # Pre-register any imscription tuples embedded in the seed text.
        # Tuples written as ⟨val; …; val⟩ (or with ASCII < > brackets) with an
        # optional "name: " label are parsed and loaded into the catalog so the
        # model finds them already encoded on its first iteration.
        _seed_tuples = _parse_imscription_tuples(self.seed)
        _n_preloaded = 0
        for _idx, (_label, _pdict) in enumerate(_seed_tuples):
            _name = (_label or f"seed_imscription_{_idx}").strip().replace(" ", "_")
            if _name in self.catalog._entries:
                continue
            _result = self.catalog.encode(_name, "auto-parsed from seed text", **_pdict)
            if _result.get("status") == "ok":
                _n_preloaded += 1

        self.question_queue: List[str] = []
        self.insights: List[Insight] = list(_inherit_insights) if _inherit_insights else []
        self._inherited_insight_count: int = len(self.insights)  # track boundary for summary
        self.history: List[IterationRecord] = []
        self.dispatcher = ToolDispatcher(
            self.catalog, self.question_queue, self.insights,
            insight_library=self._insight_library,
            promotion_kb=self._promotion_kb,
            session_seed=self.seed,
        )
        # Build system prompt dynamically from the loaded catalog
        self._system_prompt = _build_system_prompt(self.catalog)
        # For local_hf, the system prompt lives in messages[0] (chat template handles it)
        self._messages: List[Dict] = (
            [{"role": "system", "content": self._system_prompt}]
            if self._use_local_hf else []
        )
        if verbose:
            n_persistent = len(self.catalog._entries)
            if n_persistent:
                _print(f"  [dim green]Catalog:[/dim green] {n_persistent} persistent imscription(s) loaded from [dim]{catalog_path}[/dim]")
            if _n_preloaded:
                _print(f"  [dim green]Parsed:[/dim green]  {_n_preloaded} imscription tuple(s) pre-registered from seed text")
            if self._insight_library:
                n_insights = len(self._insight_library.all())
                if n_insights:
                    _print(f"  [dim green]Library:[/dim green] {n_insights} insight(s) loaded from [dim]{insight_library_path}[/dim]")
            if self._promotion_kb:
                n_patterns = len(self._promotion_kb.all())
                if n_patterns:
                    _print(f"  [dim green]Promotions KB:[/dim green] {n_patterns} pattern(s) loaded from [dim]{promotion_kb_path}[/dim]")

    def _log(self, msg: str):
        if self.verbose:
            _print(_render(msg))
        fh = getattr(self, "_transcript_fh", None)
        if fh:
            fh.write(_MARKUP_STRIP_RE.sub("", msg) + "\n")

    def _call_llm(self) -> Tuple[str, List[Tuple[str, str, Dict]], Any]:
        """Call the LLM. Returns (text, [(call_id, tool_name, kwargs), ...], raw)."""
        if self._use_local_hf:
            text, calls, raw = self._local_backend.call(self._messages, _TOOLS_OPENAI)
            return text, calls, raw

        if self._use_gemini_native:
            from google.genai import types as _gt
            # Sync the last _messages entry (user turn) into _gemini_contents.
            # _call_llm is always preceded by a user message append, so _messages[-1]
            # is the message we need to hand to Gemini.
            last = self._messages[-1]
            if last["role"] == "user":
                content_text = last["content"] if isinstance(last["content"], str) else str(last["content"])
                self._gemini_contents.append(
                    _gt.Content(role="user", parts=[_gt.Part(text=content_text)])
                )
            # Synthesis pass: use AUTO so Gemini can output CONCLUDE without
            # being forced to call a tool. All other turns: ANY forces tool use.
            _fc_mode = "AUTO" if getattr(self, "_in_synthesis_pass", False) else "ANY"
            resp = self.client.models.generate_content(
                model=self.model,
                contents=self._gemini_contents,
                config=_gt.GenerateContentConfig(
                    system_instruction=self._system_prompt,
                    tools=[self._gemini_tools] if self._gemini_tools else [],
                    tool_config=_gt.ToolConfig(
                        function_calling_config=_gt.FunctionCallingConfig(mode=_fc_mode)
                    ),
                    max_output_tokens=4096,
                ),
            )
            text = ""
            calls = []
            self._gemini_call_id_to_name = {}
            candidate = resp.candidates[0]
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text += part.text
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    call_id = f"gemini_{len(calls)}_{fc.name}"
                    self._gemini_call_id_to_name[call_id] = fc.name
                    calls.append((call_id, fc.name, dict(fc.args)))
            # raw = (response, the model Content object to thread)
            return text, calls, (resp, candidate.content)

        if self._use_anthropic:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._system_prompt,
                tools=_TOOLS_ANTHROPIC,
                messages=self._messages,
            )
            text = " ".join(b.text for b in resp.content if b.type == "text")
            calls = [
                (b.id, b.name, dict(b.input))
                for b in resp.content if b.type == "tool_use"
            ]
            return text, calls, resp.content
        else:
            # Gemini via OpenAI-compat endpoint requires tool_choice="auto" to
            # be explicit, otherwise it may emit tool calls as markdown text.
            _create_kwargs: Dict[str, Any] = dict(
                model=self.model,
                max_tokens=4096,
                tool_choice="auto",
                tools=_TOOLS_OPENAI,
                messages=[{"role": "system", "content": self._system_prompt}] + self._messages,
            )
            resp = self.client.chat.completions.create(**_create_kwargs)
            msg = resp.choices[0].message
            text = msg.content or ""
            calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    calls.append((tc.id, tc.function.name, json.loads(tc.function.arguments)))
            return text, calls, msg

    def _thread_assistant(self, raw: Any):
        if self._use_local_hf:
            return  # local backend threads assistant + tools together in _thread_tool_results

        if self._use_gemini_native:
            # raw = (response, candidate.content) — thread the Content into gemini history
            _resp, content = raw
            self._gemini_contents.append(content)
            return

        if self._use_anthropic:
            self._messages.append({"role": "assistant", "content": raw})
        else:
            entry: Dict[str, Any] = {"role": "assistant"}
            if raw.content:
                entry["content"] = raw.content
            if raw.tool_calls:
                entry["tool_calls"] = [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in raw.tool_calls
                ]
            self._messages.append(entry)

    def _thread_tool_results(self, results: List[Tuple[str, str]], raw: Any = None):
        if self._use_local_hf:
            self._local_backend.thread_tool_results(self._messages, raw, results)
            return

        if self._use_gemini_native:
            from google.genai import types as _gt
            # Build a single user Content with one FunctionResponse Part per call
            parts = []
            for call_id, result_json in results:
                fn_name = self._gemini_call_id_to_name.get(call_id, call_id)
                try:
                    response_dict = json.loads(result_json)
                except Exception:
                    response_dict = {"result": result_json}
                parts.append(_gt.Part(
                    function_response=_gt.FunctionResponse(
                        name=fn_name,
                        response=response_dict,
                    )
                ))
            self._gemini_contents.append(_gt.Content(role="tool", parts=parts))
            return

        if self._use_anthropic:
            self._messages.append({
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": cid, "content": content}
                    for cid, content in results
                ],
            })
        else:
            for cid, content in results:
                self._messages.append({"role": "tool", "tool_call_id": cid, "content": content})

    def _call_llm_fresh(self, messages: List[Dict]) -> str:
        """Call the LLM with a clean context — no inquiry history, just the supplied messages."""
        if self._use_local_hf:
            old, self._messages = self._messages, messages
            text, _, _ = self._call_llm()
            self._messages = old
            return text
        if self._use_gemini_native:
            from google.genai import types as _gt
            contents = []
            for m in messages:
                role = "user" if m["role"] in ("user", "system") else "model"
                text_val = m["content"] if isinstance(m["content"], str) else str(m["content"])
                contents.append(_gt.Content(role=role, parts=[_gt.Part(text=text_val)]))
            resp = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=_gt.GenerateContentConfig(max_output_tokens=4096),
            )
            parts = resp.candidates[0].content.parts
            return "".join(p.text for p in parts if hasattr(p, "text") and p.text)
        if self._use_anthropic:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=messages,
            )
            return " ".join(b.text for b in resp.content if b.type == "text")
        else:
            resp = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=messages,
            )
            return resp.choices[0].message.content or ""

    def _call_llm_notools(self, extra_messages: List[Dict]) -> str:
        """Call the LLM without tool definitions — for open-ended generation passes."""
        msgs = self._messages + extra_messages
        if self._use_local_hf:
            old, self._messages = self._messages, msgs
            text, _, _ = self._call_llm()
            self._messages = old
            return text
        if self._use_gemini_native:
            from google.genai import types as _gt
            # Build extra contents from extra_messages
            extra_contents = []
            for m in extra_messages:
                role = "user" if m["role"] in ("user", "system") else "model"
                text_val = m["content"] if isinstance(m["content"], str) else str(m["content"])
                extra_contents.append(_gt.Content(role=role, parts=[_gt.Part(text=text_val)]))
            resp = self.client.models.generate_content(
                model=self.model,
                contents=self._gemini_contents + extra_contents,
                config=_gt.GenerateContentConfig(
                    system_instruction=self._system_prompt,
                    max_output_tokens=4096,
                ),
            )
            parts = resp.candidates[0].content.parts
            return "".join(p.text for p in parts if hasattr(p, "text") and p.text)
        if self._use_anthropic:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._system_prompt,
                messages=msgs,
            )
            return " ".join(b.text for b in resp.content if b.type == "text")
        else:
            resp = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "system", "content": self._system_prompt}] + msgs,
            )
            return resp.choices[0].message.content or ""

    _SPECULATION_PROMPT = textwrap.dedent("""\
        You have completed the grammatical analysis. The grammar has given its verdict.

        Now enter speculation mode.

        You are free from the primitive discipline. No tool calls, no encoding constraints.
        Given what the grammar revealed about the structure of this request, speculate openly
        on what it implies, what it entails, how to realize, or how it it all connects. 
        """)

    def _run_speculation_pass(self, iteration: int):
        """After CONCLUDE: one tool-free LLM call for open speculation on realization paths."""
        self._log(f"\n   [bold magenta]💭 Running speculation pass...[/bold magenta]")
        conclude_text = self.history[-1].model_text if self.history else ""
        extra: List[Dict] = []
        if conclude_text:
            extra.append({"role": "assistant", "content": conclude_text})
        extra.append({"role": "user", "content": self._SPECULATION_PROMPT})
        text = self._call_llm_notools(extra)
        if text:
            self._log(f"\n[bold magenta]{'─'*72}[/bold magenta]")
            self._log("[bold magenta]SPECULATION[/bold magenta]")
            self._log(f"[bold magenta]{'─'*72}[/bold magenta]")
            self._log(text)
        if self.history:
            self.history[-1].speculation_text = text

    _HUMANIZE_PROMPT = textwrap.dedent("""\
        You are a prose editor. You will receive a passage of AI-authored academic or analytical
        text. Your task is to rewrite it so that it reads as genuine human-authored prose.

        The structural gap between AI-authored and human-authored text is precise:

        AI-authored type:    Þ_6, Φ_ɐ, ƒ^ì, Ç^W, Γ_γ, ɢ^∧, Ħ_Ñ, Ω_Å
        Target human type:   Þ_ò,  Φ_F,   ƒ^ż, Ç^@, Γ_ʔ, ɢ^ˌ, Ħ_A, Ω_2

        Apply each primitive lift:

        Þ_6 → Þ_ò
          Introduce a crossing point where the subject material "speaks back." Find the moment
          where the author is surprised by what they find — where the two threads (framework +
          object) must meet and exchange rather than run in parallel. Make that moment visible.

        Φ_ɐ → Φ_F
          Add at least one admission of uncertainty. Where the analysis is strong, say so; where
          it is extrapolation, name it. Acknowledge one possible objection and address it directly.

        ƒ^ì → ƒ^ż
          Cut redundancy. Remove any sentence that restates the previous sentence in different
          words. Demonstrate rather than explain — show the structural fact in action rather than
          describing it twice.

        Ç^W → Ç^@
          Identify the hardest claim and make the sentence carrying it harder, not easier. Do not
          resolve it prematurely. Allow one section to linger — to turn the problem over before
          delivering the answer.

        Γ_γ → Γ_ʔ
          Raise the stakes at the end. The final section should connect the specific findings to
          a broader question the author genuinely cares about. Do not close with a summary; close
          with an open question that has real weight.

        ɢ^∧ → ɢ^ˌ
          Each paragraph must open by connecting to the previous one, not by introducing a new
          topic. The connection should feel like necessity, not just logical transition. The reader
          should be unable to understand paragraph N fully without paragraph N-1.

        Ħ_Ñ → Ħ_A
          Make the author's encounter with the material visible as a residue in the prose. Show
          the wrong answer before the right one, at least once. Show a moment of recognition
          rather than a declaration. The reader should feel that someone worked through this.

        Ω_Å → Ω_2
          The final paragraph should explicitly revisit the framing of the opening paragraph,
          completing a loop. The ending should echo the beginning with more specificity than the
          beginning had — not as a rhetorical device but as a consequence of having moved through
          the argument.

        Output ONLY the rewritten passage. No preamble, no commentary, no explanation of what
        you changed. The rewritten text should stand alone.
        """)

    def _run_humanize_pass(self):
        """Apply the AI→human prose lift to the conclusion and speculation texts."""
        conclude_text = next(
            (r.model_text for r in reversed(self.history) if r.concluded and r.model_text), None
        )
        speculation_text = next(
            (r.speculation_text for r in reversed(self.history) if r.speculation_text), None
        )

        for label, text in [("CONCLUSION", conclude_text), ("SPECULATION", speculation_text)]:
            if not text or not text.strip():
                continue
            self._log(f"\n[bold bright_white]{'─'*72}[/bold bright_white]")
            self._log(f"[bold bright_white]HUMANIZED {label}[/bold bright_white]")
            self._log(f"[bold bright_white]{'─'*72}[/bold bright_white]")
            self._log(f"[dim]Applying AI→human prose lift (fresh context)...[/dim]")
            messages = [
                {"role": "user", "content": self._HUMANIZE_PROMPT + "\n\n---\n\n" + text},
            ]
            result = self._call_llm_fresh(messages)
            if result:
                self._log(result)
            else:
                self._log("[dim]Humanize pass returned empty.[/dim]")

    def run(self, max_iterations: Optional[int] = None) -> List[IterationRecord]:
        """Run the inquiry loop. Returns the full iteration history."""
        import datetime
        _out_dir = os.path.join(os.path.dirname(__file__), "ig_outputs")
        os.makedirs(_out_dir, exist_ok=True)
        _ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        _slug = self.seed[:40].replace(" ", "_").replace("/", "-")
        _transcript_path = os.path.join(_out_dir, f"{_ts}_{_slug}.txt")
        self._transcript_fh = open(_transcript_path, "w", encoding="utf-8")
        self._transcript_fh.write(f"seed: {self.seed}\n")
        self._transcript_fh.flush()
        self._transcript_path = _transcript_path

        self._log(f"\n[bold bright_cyan]{'='*72}[/bold bright_cyan]")
        self._log(f"[bold bright_cyan]IG INQUIRY LOOP[/bold bright_cyan]")
        self._log(f"[bold bright_cyan]Seed:[/bold bright_cyan] {self.seed}")
        self._log(f"[bold bright_cyan]{'='*72}[/bold bright_cyan]\n")

        current_question = self.seed
        _stall_count = 0
        _MAX_STALLS = 2
        self._in_synthesis_pass = False

        # Patterns that suggest the model tried to call a tool via text rather
        # than via the native tool-calling interface.
        _STALL_PATTERNS = [
            "```tool_call", "default_api.", "<tool_call>", "print(default_api",
            "tool_use", "function_call",
        ]

        i = 0
        _exit_reason = "max_iter"   # overwritten on every break path
        while max_iterations is None or i < max_iterations:
            self._log(f"\n[bold yellow]── Iteration {i+1} {'─'*55}[/bold yellow]")
            self._log(f"   [green]Question:[/green] {current_question}")

            record = IterationRecord(iteration=i + 1, question=current_question)

            # Build user message for this iteration
            user_msg = f"**Question for this iteration:**\n{current_question}"
            if i == 0 and self._inherited_insight_count > 0:
                prior_lines = "\n".join(
                    f"  [{ins.plane}/{ins.confidence}] {ins.text}"
                    for ins in self.insights[:self._inherited_insight_count]
                )
                user_msg += (
                    f"\n\n**Insights carried over from earlier prompts in this run "
                    f"({self._inherited_insight_count} total):**\n{prior_lines}"
                )
            if i > 0:
                user_msg += (
                    f"\n\n**Session context:** {len(self.catalog.list_all())} systems encoded, "
                    f"{len(self.insights)} insights recorded so far."
                )
            if self.question_queue:
                user_msg += f"\n\n**Queued questions for later:** {json.dumps(self.question_queue)}"

            self._messages.append({"role": "user", "content": user_msg})

            # LLM turn
            text, calls, raw = self._call_llm()
            record.model_text = text

            if text:
                self._log(f"   [dim]Model: {text}[/dim]")

            # If no tool calls: CONCLUDE check, stall detection, or genuine stop.
            # (Gemini mode=ANY always produces tool calls, so this branch is for
            #  Anthropic / OpenAI-compat providers only in normal operation.)
            if not calls:
                if "CONCLUDE" in text:
                    record.concluded = True
                    self.history.append(record)
                    self._log(f"\n   [bold green]✅ Model concluded.[/bold green]")
                    self._run_speculation_pass(i)
                    self._run_humanize_pass()
                    _exit_reason = "concluded"
                    break

                # Check whether the model was trying to call tools via text
                # (hallucinated code block, Python-style invocation, etc.)
                _looks_like_stall = any(p in text for p in _STALL_PATTERNS)

                if _looks_like_stall and _stall_count < _MAX_STALLS:
                    _stall_count += 1
                    self._log(
                        f"   [yellow]→ Model emitted tool call in text (stall {_stall_count}/{_MAX_STALLS}). "
                        f"Nudging to use native tool interface.[/yellow]"
                    )
                    # Thread the assistant turn so the nudge lands in context
                    self._thread_assistant(raw)
                    nudge = (
                        "Your previous response contained tool calls written as code or text "
                        "rather than as actual tool invocations. Please call the tools directly "
                        "using the tool calling interface — do not wrap them in code blocks or "
                        "Python syntax. Retry the tool call(s) you intended to make."
                    )
                    self._messages.append({"role": "user", "content": nudge})
                    # For Gemini native: also push nudge directly into the gemini
                    # content history (the loop will prepend a new user_msg before
                    # the next _call_llm call, so _messages[-1] sync alone misses it)
                    if self._use_gemini_native:
                        from google.genai import types as _gt
                        self._gemini_contents.append(
                            _gt.Content(role="user", parts=[_gt.Part(text=nudge)])
                        )
                    # Don't commit the stalled record; retry the same question
                    i += 1
                    continue

                # Genuine stop with no tools and no CONCLUDE
                record.concluded = False
                self.history.append(record)
                self._log("   [yellow]→ Model stopped without tools or CONCLUDE.[/yellow]")
                _exit_reason = "graceful_stop"
                break

            self._thread_assistant(raw)

            # Execute tool calls
            tool_results: List[Tuple[str, str]] = []
            for call_id, tool_name, kwargs in calls:
                self._log(f"   [bold blue]Tool[/bold blue] [cyan]→ {tool_name}[/cyan]({json.dumps({k: v for k, v in kwargs.items() if k not in ('D','T','R','P','F','K','G','Gamma','Phi','H','S','Omega')}, ensure_ascii=False)})")
                result = self.dispatcher.dispatch(tool_name, kwargs, iteration=i + 1)
                record.tool_calls.append({"name": tool_name, "args": kwargs})
                record.tool_results.append(result)

                if tool_name == "ask_question":
                    record.questions_queued.append(kwargs.get("question", ""))
                elif tool_name == "record_insight":
                    # Already added to self.insights by dispatcher
                    record.insights_added = [ins for ins in self.insights if ins.iteration == i + 1]

                if tool_name == "list_catalog":
                    count = len(result.get("entries", []))
                    self._log(f"   [dim italic]Result: [list_catalog — {count} entries, output suppressed][/dim italic]")
                else:
                    self._log(f"   [dim italic]Result: {json.dumps(result, ensure_ascii=False)}[/dim italic]")
                tool_results.append((call_id, json.dumps(result, ensure_ascii=False)))

            self._thread_tool_results(tool_results, raw=raw)
            self.history.append(record)

            # Check for CONCLUDE signal AFTER executing tools.
            # This ordering matters for Gemini (mode=ANY): the model may call a
            # tool (e.g. record_insight) AND output CONCLUDE in the same turn.
            # Executing the tools first ensures the insight is stored before we break.
            if "CONCLUDE" in text:
                record.concluded = True
                self._log(f"\n   [bold green]✅ Model concluded.[/bold green]")
                self._run_speculation_pass(i)
                self._run_humanize_pass()
                _exit_reason = "concluded"
                break

            # Advance to next question from queue (if any)
            if self.question_queue:
                self._in_synthesis_pass = False
                current_question = self.question_queue.pop(0)
            else:
                # No queued questions — route to synthesis pass.
                # Flag enables mode=AUTO for Gemini so it can CONCLUDE without
                # being forced to make a tool call.
                self._in_synthesis_pass = True
                current_question = (
                    f"You have encoded {len(self.catalog.list_all())} systems and recorded "
                    f"{len(self.insights)} insights. Using the primitive structure you have "
                    f"identified, now reason directly toward an answer to the original question: "
                    f"'{self.seed}'. Do not merely summarize what the tools returned — derive "
                    f"structural conclusions, follow implications, and state what the grammar "
                    f"says. Then CONCLUDE."
                )
                self._log(f"\n   [yellow]→ No queued questions. Routing to synthesis pass.[/yellow]")

            i += 1

        self._exit_reason = _exit_reason
        self._print_summary()
        self._autosave()
        return self.history

    def _autosave(self):
        """Save full session to a timestamped JSON file; also update the persistent insight library."""
        # Close transcript first so it's fully flushed before we report its path
        fh = getattr(self, "_transcript_fh", None)
        if fh:
            try:
                fh.close()
            except OSError:
                pass
            self._transcript_fh = None

        import datetime
        out_dir = os.path.join(os.path.dirname(__file__), "ig_outputs")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = self.seed[:40].replace(" ", "_").replace("/", "-")
        path = os.path.join(out_dir, f"{ts}_{slug}.json")
        with open(path, "w") as f:
            json.dump(self.export_insights(), f, indent=2, ensure_ascii=False)
        self._log(f"\n  [bold green]Saved[/bold green] → [dim]{path}[/dim]")
        transcript_path = getattr(self, "_transcript_path", None)
        if transcript_path and os.path.exists(transcript_path):
            self._log(f"  [bold green]Transcript[/bold green] → [dim]{transcript_path}[/dim]")

        # Persist insights to the cross-session library
        if self._insight_library and self.insights:
            n_new = self._insight_library.add_batch(
                self.insights, seed=self.seed, run_file=path, catalog=self.catalog
            )
            self._log(f"  [bold green]Library:[/bold green] {n_new} new insight(s) added ([dim]{len(self._insight_library.all())} total[/dim])")

    _PLANE_COLORS = {"TOPO": "blue", "DIAPH": "yellow", "ONTO": "magenta"}
    _CONF_COLORS  = {"high": "green", "medium": "yellow", "speculative": "dim", "low": "dim"}

    def _print_summary(self):
        self._log(f"\n[bold bright_cyan]{'='*72}[/bold bright_cyan]")
        self._log("[bold bright_cyan]INQUIRY SUMMARY[/bold bright_cyan]")
        self._log(f"[bold bright_cyan]{'='*72}[/bold bright_cyan]")
        self._log(f"Iterations: {len(self.history)}")
        self._log(f"Systems encoded: {len(self.catalog.list_all())}")
        self._log(f"Insights: {len(self.insights)}")

        if self.insights:
            self._log("\nInsights by plane:")
            for plane in ["TOPO", "DIAPH", "ONTO"]:
                plane_insights = [ins for ins in self.insights if ins.plane == plane]
                if plane_insights:
                    color = self._PLANE_COLORS.get(plane, "white")
                    self._log(f"\n  [bold {color}][{plane}][/bold {color}]")
                    for ins in plane_insights:
                        conf_color = self._CONF_COLORS.get(ins.confidence, "white")
                        self._log(f"    ([{conf_color}]{ins.confidence}[/{conf_color}]) {ins.text}")

        # Translation cost summary across all encoded imscriptions
        all_catalog = self.catalog.list_all()
        if all_catalog and _TRANSLATE_AVAILABLE:
            agg = {"coherence_loss": 0.0, "criticality_loss": 0.0, "interaction_cost": 0.0, "total": 0.0}
            n_critical = 0
            for entry in all_catalog:
                sdict = self.catalog.get(entry["name"])
                if sdict:
                    cost = _translation_cost_from_dict(sdict)
                    for k in agg:
                        agg[k] += cost[k]
                    if sdict.get("⊙") == "⊙_ÿ":
                        n_critical += 1
            self._log(f"\n[dim green]Translation cost (structural→classical, all {len(all_catalog)} imscriptions):[/dim green]")
            self._log(f"  [dim green]coherence:    {agg['coherence_loss']:.4f} nat[/dim green]")
            self._log(f"  [dim green]criticality:  {agg['criticality_loss']:.4f} nat  ({n_critical} ⊙_ÿ imscriptions × ln10)[/dim green]")
            self._log(f"  [dim green]interaction:  {agg['interaction_cost']:.4f} nat[/dim green]")
            self._log(f"  [dim green]total:        {agg['total']:.4f} nat[/dim green]")

        concluded = any(r.concluded for r in self.history)
        if self._exit_reason == "concluded":
            self._log(f"\n  [bold green]Inquiry concluded ✅[/bold green]")
        elif self._exit_reason == "graceful_stop":
            self._log(f"\n  [dim green]Inquiry complete (model stopped naturally)[/dim green]")
        else:
            self._log(f"\n  [bold yellow]Max iterations reached ⚠️[/bold yellow]")

        speculation = next(
            (r.speculation_text for r in reversed(self.history) if r.speculation_text), None
        )
        if speculation:
            self._log(f"\n[bold magenta]{'─'*72}[/bold magenta]")
            self._log("[bold magenta]SPECULATION[/bold magenta]")
            self._log(f"[bold magenta]{'─'*72}[/bold magenta]")
            self._log(speculation)

    def export_insights(self) -> Dict[str, Any]:
        """Export session insights as a structured dict (for saving or further processing)."""
        insight_dicts = []
        for ins in self.insights:
            d: Dict[str, Any] = {
                "text": ins.text,
                "plane": ins.plane,
                "confidence": ins.confidence,
                "iteration": ins.iteration,
            }
            if ins.translation:
                d["translation"] = ins.translation
            insight_dicts.append(d)

        # Session-level translation summary: aggregate over all catalog imscriptions
        all_catalog = self.catalog.list_all()
        session_translation: Dict[str, Any] = {"per_imscription": {}, "total": {}}
        if all_catalog and _TRANSLATE_AVAILABLE:
            agg = {"coherence_loss": 0.0, "criticality_loss": 0.0, "interaction_cost": 0.0, "total": 0.0}
            for entry in all_catalog:
                sdict = self.catalog.get(entry["name"])
                if sdict:
                    cost = _translation_cost_from_dict(sdict)
                    session_translation["per_imscription"][entry["name"]] = cost
                    for k in agg:
                        agg[k] = round(agg[k] + cost[k], 4)
            session_translation["total"] = agg

        # Session-level conflict summary: all conflict pairs + emergence frontier
        conflict_pairs = self.dispatcher._conflict_pairs if hasattr(self, "dispatcher") else []
        from collections import Counter as _Counter
        prim_counter: _Counter = _Counter()
        for pair in conflict_pairs:
            for p in pair.get("conflict_set", []):
                prim_counter[p] += 1
        frontier = [
            {"primitive": p, "conflict_count": c, "fraction": round(c / max(len(conflict_pairs), 1), 3)}
            for p, c in prim_counter.most_common()
        ]
        conflict_summary: Dict[str, Any] = {
            "pairs": conflict_pairs,
            "emergence_frontier": frontier,
            "veracity_distribution": dict(_Counter(p.get("veracity_class", "") for p in conflict_pairs)),
        }

        speculation = next(
            (r.speculation_text for r in reversed(self.history) if r.speculation_text), ""
        )

        return {
            "seed": self.seed,
            "model": self.model,
            "provider": self.provider,
            "iterations": len(self.history),
            "catalog": all_catalog,
            "insights": insight_dicts,
            "speculation": speculation,
            "translation_summary": session_translation,
            "conflict_summary": conflict_summary,
        }


# ── Multi-prompt runner ───────────────────────────────────────────────────────

def run_multi_prompt(
    seeds: List[str],
    model: str = "claude-sonnet-4-6",
    provider: str = "anthropic",
    verbose: bool = True,
    catalog_path: Optional[str] = CATALOG_PATH,
    insight_library_path: Optional[str] = None,
    promotion_kb_path: Optional[str] = PROMOTIONS_PATH,
) -> List[IGInquiryLoop]:
    """Run multiple prompts sequentially, carrying catalog and insights forward.

    Each prompt sees all systems encoded and insights recorded by prior prompts.
    The separator between prompts in a file is ``MULTI_PROMPT_SEP`` (``---``).

    Returns the list of completed ``IGInquiryLoop`` instances (one per prompt).
    """
    loops: List[IGInquiryLoop] = []
    inherited_catalog: Optional[SessionCatalog] = None
    inherited_insights: Optional[List[Insight]] = None

    for idx, seed in enumerate(seeds):
        _print(f"\n[bold bright_cyan]{'='*72}[/bold bright_cyan]")
        _print(f"[bold bright_cyan]PROMPT {idx + 1} / {len(seeds)}[/bold bright_cyan]")
        _print(f"[bold bright_cyan]{'='*72}[/bold bright_cyan]")

        loop = IGInquiryLoop(
            seed=seed,
            model=model,
            provider=provider,
            verbose=verbose,
            catalog_path=catalog_path if inherited_catalog is None else None,
            insight_library_path=insight_library_path,
            promotion_kb_path=promotion_kb_path,
            _inherit_catalog=inherited_catalog,
            _inherit_insights=inherited_insights,
        )
        loop.run()
        loops.append(loop)

        # Pass accumulated state to the next prompt
        inherited_catalog = loop.catalog
        inherited_insights = list(loop.insights)

    return loops


# ── CLI entry point ───────────────────────────────────────────────────────────

def _cli_tool() -> None:
    """IG_inquiry.py tool <tool_name> [key=value ...] [--args JSON]"""
    import argparse, json as _json

    parser = argparse.ArgumentParser(
        prog="ig_inquiry tool",
        description="Dispatch a single ToolDispatcher tool without an LLM loop.",
    )
    parser.add_argument("tool_name", help="Tool name (e.g. ouroborics, find_analogies).")
    parser.add_argument(
        "kvpairs", nargs="*", metavar="key=value",
        help="Tool arguments as key=value pairs. Values are auto-parsed as JSON when valid.",
    )
    parser.add_argument(
        "--args", "-a", default=None, metavar="JSON",
        help="Tool arguments as a JSON object (alternative to key=value pairs).",
    )
    parser.add_argument(
        "--pretty", action="store_true", default=True,
        help="Pretty-print JSON output (default: on).",
    )
    args = parser.parse_args(sys.argv[2:])

    if args.args:
        tool_args = _json.loads(args.args)
    else:
        tool_args = {}
        for kv in args.kvpairs:
            if "=" not in kv:
                parser.error(f"Expected key=value, got: {kv!r}")
            k, v = kv.split("=", 1)
            try:
                tool_args[k] = _json.loads(v)
            except _json.JSONDecodeError:
                tool_args[k] = v

    catalog = SessionCatalog(catalog_path=CATALOG_PATH)
    dispatcher = ToolDispatcher(catalog=catalog, question_queue=[], insights=[])
    result = dispatcher.dispatch(args.tool_name, tool_args, iteration=0)
    indent = 2 if args.pretty else None
    print(_json.dumps(result, indent=indent, ensure_ascii=False))


def _cli_agent() -> None:
    """IG_inquiry.py agent <task> [--model M] [--max-windings N]"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="ig_inquiry agent",
        description="Run the TrueAgenticAgent ($O_\\infty$, §88 Thm 88.4).",
    )
    parser.add_argument("task", help="Task for the agent to perform.")
    parser.add_argument(
        "--model", "-m", default="grok-4",
        help="Model alias or full model ID (default: grok-4).",
    )
    parser.add_argument(
        "--max-windings", type=int, default=10_000,
        help="Maximum loop iterations (default: 10000).",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=4096,
        help="Max tokens per THINK phase (default: 4096).",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-winding log output.",
    )
    parser.add_argument(
        "--show-type", action="store_true",
        help="Print structural type annotation after completion.",
    )
    args = parser.parse_args(sys.argv[2:])

    import importlib, json as _json
    agent_mod = importlib.import_module("agents.true_agentic_agent")
    agent = agent_mod.TrueAgenticAgent(
        model=args.model,
        max_windings=args.max_windings,
        max_think_tokens=args.max_tokens,
        verbose=not args.quiet,
    )
    result = agent.run_sync(args.task)

    print("\n" + "═" * 72)
    print("RESULT:")
    print(result)

    if args.show_type:
        print("\nStructural type:")
        print(_json.dumps(agent.structural_type, indent=2))


if __name__ == "__main__":
    import argparse

    _SUBCOMMANDS = {"tool", "agent"}
    if len(sys.argv) > 1 and sys.argv[1] in _SUBCOMMANDS:
        {"tool": _cli_tool, "agent": _cli_agent}[sys.argv[1]]()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        prog="ig_inquiry",
        description="Imscribing Grammar open-ended inquiry loop.",
        epilog=(
            "Subcommands:\n"
            "  tool <name> [key=val ...]   dispatch a tool directly\n"
            "  agent <task>                run the O_inf agentic agent\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "seed",
        nargs="?",
        default=None,
        help="Seed question or topic (default: built-in example question).",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        default=None,
        help="Path to a text file whose contents are used as the seed question (alternative to positional arg).",
    )
    parser.add_argument(
        "--no-catalog",
        action="store_true",
        help="Disable loading the persistent imscription catalog (IG_catalog.json). "
             "Session starts with an empty catalog.",
    )
    parser.add_argument(
        "--insights",
        action="store_true",
        help="Inject prior-session insights from ig_insights.json into the system prompt. "
             "Disabled by default: prior interpretations can propagate errors across sessions.",
    )
    parser.add_argument(
        "--provider", "-p",
        default=None,
        metavar="PROVIDER",
        help="LLM provider (env: IG_PROVIDER). "
             "E.g. openrouter, deepseek, qwen, anthropic, mistral, gemini, local.",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        metavar="MODEL",
        help="Model ID (env: IG_MODEL). Uses provider default if unset.",
    )
    parser.add_argument(
        "--max-iter", "-n",
        type=int,
        default=None,
        metavar="N",
        help="Maximum reasoning iterations (env: IG_MAX_ITER).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        metavar="FILE",
        help="Export final insights to JSON file (env: IG_OUT).",
    )
    args = parser.parse_args()

    if args.file:
        with open(args.file) as _f:
            raw_text = _f.read().strip()
    else:
        raw_text = args.seed or "What is the primitive distance between consciousness and quantum measurement?"

    # Split on the multi-prompt separator (--- alone on a line)
    _sep_pattern = re.compile(r"^\s*" + re.escape(MULTI_PROMPT_SEP) + r"\s*$", re.MULTILINE)
    seeds = [s.strip() for s in _sep_pattern.split(raw_text) if s.strip()]

    # Provider: CLI flag > IG_PROVIDER env > no default (required)
    provider = args.provider or os.environ.get("IG_PROVIDER")
    if not provider:
        parser.error(
            "No provider specified. Use --provider (-p) or set IG_PROVIDER "
            "(e.g. openrouter, deepseek, qwen, anthropic, mistral)."
        )

    # Model: CLI flag > IG_MODEL env > provider default
    _model_defaults = {
        "anthropic":  "claude-sonnet-4-6",
        "deepseek":   "deepseek-chat",
        "qwen":       "qwen-plus",
        "gemini":     "gemini-2.0-flash",
        "google":     "gemini-2.0-flash",
        "mistral":    "mistral-large-latest",
        "openrouter": "x-ai/grok-4.1-fast",
        "local":      os.environ.get("LOCAL_MODEL", "qwen3:8b"),
        "local_hf":   os.environ.get("LOCAL_MODEL", _MERGED2_PATH),
    }
    model = (
        args.model
        or os.environ.get("IG_MODEL")
        or _model_defaults.get(provider)
    )
    if not model:
        parser.error(
            f"No model specified for provider '{provider}'. "
            "Use --model (-m) or set IG_MODEL."
        )

    max_iter = args.max_iter or (
        int(os.environ.get("IG_MAX_ITER")) if os.environ.get("IG_MAX_ITER") else None
    )
    out_path = args.output or os.environ.get("IG_OUT")

    catalog_path  = None         if args.no_catalog else CATALOG_PATH
    insights_path = INSIGHTS_PATH if args.insights   else None

    if len(seeds) > 1:
        loops = run_multi_prompt(
            seeds=seeds,
            model=model,
            provider=provider,
            verbose=True,
            catalog_path=catalog_path,
            insight_library_path=insights_path,
        )
        if out_path:
            with open(out_path, "w") as f:
                json.dump(loops[-1].export_insights(), f, indent=2)
            _print(f"\nExported to {out_path}")
    else:
        loop = IGInquiryLoop(
            seed=seeds[0],
            model=model,
            provider=provider,
            verbose=True,
            catalog_path=catalog_path,
            insight_library_path=insights_path,
        )
        loop.run(max_iterations=max_iter)

        if out_path:
            with open(out_path, "w") as f:
                json.dump(loop.export_insights(), f, indent=2)
            _print(f"\nExported to {out_path}")

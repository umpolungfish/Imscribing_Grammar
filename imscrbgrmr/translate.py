"""
imscrbgrmr/translate.py — Structural→Classical Translation Layer

Translation Protocol v0.4 (implemented valid components)
---------------------------------------------------------

1. WriterT/StateT monad for tracking translation cost
   The existing ImscriptionM already provides WriterT[float] ⊗ StateT[Context].
   Here we layer a structured TranslationCost on top: each translation step
   decomposes cost into coherence_loss + criticality_loss + interaction_cost.

2. F_ℏ threshold (Kleisli guard):
       I(s₁; s₂) ≥ ln(19) ≈ 2.944 nats  (= log₂(19) / log₂(e) ≈ 4.248 bits)
   Below this mutual-information floor, constraint propagation cannot be
   maintained at quantum fidelity — F_hardsign degrades to F_dh.
   Derivation: ln(19) is the information threshold for 19+ distinguishable
   constraint configurations — the minimum resolution for high-fidelity
   retrosynthetic path inference.

3. ⊙ ↔ marginal stability:
       ∂f/∂x|_{λ=λ_c} = 1   (Jacobian eigenvalue exactly 1)
   This is the classical translation of ⊙ (criticality phase).
   In the logistic map f(x) = λx(1-x):
     - f'(x*) = λ(1 - 2x*) = 2 - λ at fixed point x* = 1 - 1/λ
     - Marginal stability: f'(x*) = 1  ⟹  λ_c = 1  (trivial fixed point)
     - First bifurcation at λ = 3 (period-1 → period-2); NOT λ_c = 3
     - Feigenbaum accumulation point: λ_∞ ≈ 3.56995 (onset of chaos)
   The structural ⊙ maps to f'(x*) = 1, i.e., the boundary of the
   λ ∈ (1, 3) stable fixed-point window.

4. Kleisli enrichment cost:
   Translation functions t : Imscription → TranslationM[Imscription] compose via:
       (t₁ >=> t₂)(s) = t₁(s) >>= t₂
   Costs accumulate additively in the Writer layer; the Fidelity floor in
   Context is updated monotonically upward (strictest requirement survives).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, TypeVar

from .models import (
    Imscription,
    Fidelity,
    CriticalityPhase,
    InteractionGrammar,
    GrammarOperator,
)
# Re-export for external use
__all__ = [
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
]
from .monad import ImscriptionM, Context, StepRecord

A = TypeVar("A")

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# F_ℏ mutual-information threshold (Translation Protocol §2)
# I(s₁; s₂) ≥ ln(19) for high-fidelity constraint propagation
FHBAR_THRESHOLD_NATS: float = math.log(19)   # ≈ 2.9444 nats
FHBAR_THRESHOLD_BITS: float = math.log2(19)  # ≈ 4.2479 bits

# Feigenbaum accumulation point for the logistic map (not the first bifurcation)
FEIGENBAUM_LAMBDA: float = 3.56995  # λ_∞ — onset of chaos

# Logistic map first bifurcation (period-1 → period-2)
LOGISTIC_BIFURCATION_1: float = 3.0  # NOT "λ_c = 3 is chaos onset" — that is wrong

# Marginal stability: f'(x*) = 1 ⟹ λ_c = 1 in the logistic map
LOGISTIC_MARGINAL_LAMBDA: float = 1.0

# Translation cost coefficients (nats per unit of structural loss)
# Coherence loss: F_hardsign → F_dh loses ~25% of constraint propagation
COHERENCE_LOSS_FHBAR_TO_FETH: float = -math.log(0.75)   # ≈ 0.288 nats
# F_dh → F_beltl loses another ~40%
COHERENCE_LOSS_FETH_TO_FELL: float = -math.log(0.60)    # ≈ 0.511 nats

# Criticality loss: ⊙ → Phi_softsign = ln(10) nats (one order of magnitude in correlation length)
CRITICALITY_LIFT_NATS: float = math.log(10)              # ≈ 2.303 nats  (PHI_LIFT_NATS from v0.4)

# F-tier ordering for dominance comparisons
_F_ORDER = {Fidelity.age: 0, Fidelity.they: 1, Fidelity.peep: 2}
_F_NAME = {Fidelity.age: "ƒ_beltl", Fidelity.they: "ƒ_dh", Fidelity.peep: "ƒ_hardsign"}


# ─────────────────────────────────────────────────────────────────────────────
# TranslationCost — structured cost breakdown
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TranslationCost:
    """
    Structured decomposition of structural→classical translation cost.

    All fields are in nats (natural units of information).
    Total cost = coherence_loss + criticality_loss + interaction_cost.
    """
    coherence_loss: float = 0.0    # cost of F-tier downgrade (quantum → classical)
    criticality_loss: float = 0.0  # cost of ⊙ → Phi_softsign (criticality → sub-critical)
    interaction_cost: float = 0.0  # cost of grammar mismatch (Γ constraint loosening)

    @property
    def total(self) -> float:
        return self.coherence_loss + self.criticality_loss + self.interaction_cost

    def __add__(self, other: "TranslationCost") -> "TranslationCost":
        return TranslationCost(
            coherence_loss=self.coherence_loss + other.coherence_loss,
            criticality_loss=self.criticality_loss + other.criticality_loss,
            interaction_cost=self.interaction_cost + other.interaction_cost,
        )

    def __repr__(self) -> str:
        return (
            f"TranslationCost("
            f"coherence={self.coherence_loss:.4f}, "
            f"criticality={self.criticality_loss:.4f}, "
            f"interaction={self.interaction_cost:.4f}  "
            f"→ total={self.total:.4f} nat)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# F_ℏ mutual-information check
# ─────────────────────────────────────────────────────────────────────────────

def fhbar_satisfied(mutual_info_nats: float) -> bool:
    """
    Check whether the F_ℏ threshold is met.

    Returns True iff I(s₁; s₂) ≥ ln(19) ≈ 2.944 nats.
    Below this, constraint propagation degrades from F_hardsign to F_dh.
    """
    return mutual_info_nats >= FHBAR_THRESHOLD_NATS


def fhbar_deficit(mutual_info_nats: float) -> float:
    """
    Return the shortfall below the F_ℏ threshold (in nats).
    Returns 0.0 if threshold is satisfied.
    """
    return max(0.0, FHBAR_THRESHOLD_NATS - mutual_info_nats)


# ─────────────────────────────────────────────────────────────────────────────
# ⊙ ↔ marginal stability
# ─────────────────────────────────────────────────────────────────────────────

def logistic_fixed_point(lam: float) -> Optional[float]:
    """
    Non-trivial fixed point of the logistic map f(x) = λx(1-x).
    x* = 1 - 1/λ  for λ > 1; None for λ ≤ 1.
    """
    if lam <= 1.0:
        return None
    return 1.0 - 1.0 / lam


def logistic_jacobian_at_fp(lam: float) -> Optional[float]:
    """
    Jacobian f'(x*) = 2 - λ at the non-trivial fixed point.

    Marginal stability: f'(x*) = 1  ⟺  λ = 1  (trivial onset)
    Stability window:   |f'(x*)| < 1  ⟺  λ ∈ (1, 3)
    First bifurcation:  f'(x*) = -1  ⟺  λ = 3  (period-doubling onset)
    """
    if lam <= 1.0:
        return None
    return 2.0 - lam


def phic_bifurcation(lam: float, tol: float = 1e-9) -> bool:
    """
    Returns True if λ corresponds to the marginal stability condition ⊙.

    The classical translation of ⊙ is f'(x*) = 1, i.e., λ → 1⁺.
    For practical purposes we check whether f'(x*) ≈ ±1:
      - f'(x*) = +1  (λ ≈ 1): onset of non-trivial fixed point  [⊙, lower]
      - f'(x*) = -1  (λ = 3): first period-doubling bifurcation [⊙, upper]

    Note: "λ_c = 3 is the onset of chaos" is INCORRECT.
    The Feigenbaum accumulation point (onset of chaos) is λ_∞ ≈ 3.56995.
    """
    j = logistic_jacobian_at_fp(lam)
    if j is None:
        return False
    return abs(abs(j) - 1.0) < tol


def phic_from_jacobian(j: float) -> bool:
    """
    Test whether a scalar Jacobian value corresponds to marginal stability.
    |j| = 1 ↔ ⊙.
    """
    return abs(abs(j) - 1.0) < 1e-9


# ─────────────────────────────────────────────────────────────────────────────
# Translation functions — structural → classical
# ─────────────────────────────────────────────────────────────────────────────

def translate_fidelity(
    s: Imscription,
    mutual_info_nats: Optional[float] = None,
) -> ImscriptionM[Imscription]:
    """
    Translate F_hardsign → F_dh when mutual information falls below the F_ℏ threshold.

    If mutual_info_nats is provided and < ln(19), the fidelity is downgraded
    and coherence_loss = ln(19) - I is recorded as Δξ cost.
    If mutual_info_nats is None, checks whether imscription already has F_hardsign
    and warns; no automatic downgrade without data.

    Cost annotation: delta_xi = coherence_loss (nats) in the Writer log.
    """
    import copy

    fidelity = s.fidelity

    # No mutual info provided → pass-through with a note
    if mutual_info_nats is None:
        rec = StepRecord(
            "translate_fidelity", s.name, "PASS", 0.0,
            "No I(s₁;s₂) provided — fidelity unchanged; F_ℏ threshold not checked"
        )
        return ImscriptionM(value=s, cost=0.0, context=Context(step_count=1), log=[rec])

    if fhbar_satisfied(mutual_info_nats):
        rec = StepRecord(
            "translate_fidelity", s.name, "PASS", 0.0,
            f"I={mutual_info_nats:.4f} nat ≥ ln(19)={FHBAR_THRESHOLD_NATS:.4f} — F_ℏ maintained"
        )
        return ImscriptionM(value=s, cost=0.0, context=Context(step_count=1), log=[rec])

    # Below threshold — downgrade fidelity
    deficit = fhbar_deficit(mutual_info_nats)
    new_s = copy.copy(s)

    if fidelity == Fidelity.peep:
        new_s.fidelity = Fidelity.they
        loss = COHERENCE_LOSS_FHBAR_TO_FETH
        msg = (
            f"I={mutual_info_nats:.4f} nat < ln(19)={FHBAR_THRESHOLD_NATS:.4f}  "
            f"deficit={deficit:.4f} nat — F_hardsign→F_dh  "
            f"coherence_loss={loss:.4f} nat"
        )
    elif fidelity == Fidelity.they:
        new_s.fidelity = Fidelity.age
        loss = COHERENCE_LOSS_FETH_TO_FELL
        msg = (
            f"I={mutual_info_nats:.4f} nat < ln(19)={FHBAR_THRESHOLD_NATS:.4f}  "
            f"deficit={deficit:.4f} nat — F_dh→F_beltl  "
            f"coherence_loss={loss:.4f} nat"
        )
    else:
        # Already at floor — record deficit as cost but cannot degrade further
        loss = deficit
        msg = (
            f"I={mutual_info_nats:.4f} nat < ln(19)={FHBAR_THRESHOLD_NATS:.4f}  "
            f"deficit={deficit:.4f} nat — already at F_beltl floor; deficit charged"
        )

    rec = StepRecord("translate_fidelity", s.name, "PASS", loss, msg)
    f_name = _F_NAME.get(new_s.fidelity, str(new_s.fidelity))
    ctx = Context(f_floor=f_name, step_count=1)
    return ImscriptionM(value=new_s, cost=loss, context=ctx, log=[rec])


def translate_criticality(s: Imscription) -> ImscriptionM[Imscription]:
    """
    Translate ⊙ → Phi_softsign when mapping to classical dynamics.

    Criticality cannot be preserved in a classical linearized description.
    Cost = CRITICALITY_LIFT_NATS = ln(10) ≈ 2.303 nats — one decade of
    correlation length is lost when truncating at the marginal stability
    boundary (∂f/∂x|_{λ_c} = 1).

    Classical marker: the translated system is at λ = 3⁻ (just below the
    first period-doubling bifurcation), not at the holographic ⊙ boundary.
    """
    import copy

    if s.criticality_phase != CriticalityPhase.monad:
        rec = StepRecord(
            "translate_criticality", s.name, "PASS", 0.0,
            f"Φ={s.criticality_phase} — not ⊙; no translation cost"
        )
        return ImscriptionM(value=s, cost=0.0, context=Context(step_count=1), log=[rec])

    new_s = copy.copy(s)
    new_s.criticality_phase = CriticalityPhase.woe

    msg = (
        f"⊙ → Phi_softsign  "
        f"(∂f/∂x|_{{λ_c}}=1 boundary; classical λ∈(1,3) window)  "
        f"criticality_loss={CRITICALITY_LIFT_NATS:.4f} nat = ln(10)"
    )
    rec = StepRecord("translate_criticality", s.name, "PASS", CRITICALITY_LIFT_NATS, msg)
    ctx = Context(criticality_ok=False, step_count=1)
    return ImscriptionM(value=new_s, cost=CRITICALITY_LIFT_NATS, context=ctx, log=[rec])


def translate_grammar(s: Imscription) -> ImscriptionM[Imscription]:
    """
    Translate interaction grammar for classical compatibility.

    AND, OR, SEQUENTIAL grammars translate cleanly (classically expressible).
    DISSIPATIVE grammar has no reversible classical analogue — approximated
    with OR, charging interaction_cost = ln(2) ≈ 0.693 nat (1 bit lost).

    Note: InteractionGrammar enum values are (GrammarOperator, tier) tuples.
    Classical compatibility is checked via the operator component (.value[0]).
    """
    import copy

    grammar = s.interaction_grammar

    if grammar is None:
        rec = StepRecord(
            "translate_grammar", s.name, "PASS", 0.0,
            "Γ=None — no grammar to translate"
        )
        return ImscriptionM(value=s, cost=0.0, context=Context(step_count=1), log=[rec])

    # Extract the operator component from the (GrammarOperator, tier) tuple
    try:
        operator = grammar.value[0]  # GrammarOperator
    except (TypeError, IndexError):
        operator = grammar  # fallback if grammar is already a GrammarOperator

    # Classically compatible operators
    classical_operators = {
        GrammarOperator.AND,
        GrammarOperator.OR,
        GrammarOperator.SEQUENTIAL,
    }

    if operator in classical_operators:
        rec = StepRecord(
            "translate_grammar", s.name, "PASS", 0.0,
            f"Γ={grammar.name if hasattr(grammar, 'name') else grammar} "
            f"(op={operator.name}) — classically compatible; no interaction cost"
        )
        return ImscriptionM(value=s, cost=0.0, context=Context(step_count=1), log=[rec])

    # DISSIPATIVE or unknown — approximate with closest OR grammar, charge cost
    new_s = copy.copy(s)
    # Map to the OR variant at the same tier if possible
    tier = grammar.value[1] if isinstance(grammar.value, tuple) and len(grammar.value) > 1 else "SPECIFIC"
    # Find the OR grammar at the same tier
    fallback_name = f"{tier}_OR"
    fallback = getattr(InteractionGrammar, fallback_name, InteractionGrammar.gag)
    new_s.interaction_grammar = fallback

    cost = math.log(2)  # 1 bit of interaction information lost
    msg = (
        f"Γ={grammar.name if hasattr(grammar, 'name') else grammar} "
        f"(op={operator.name if hasattr(operator, 'name') else operator}) "
        f"→ {fallback.name} (no classical analogue for DISSIPATIVE)  "
        f"interaction_cost={cost:.4f} nat"
    )
    rec = StepRecord("translate_grammar", s.name, "PASS", cost, msg)
    return ImscriptionM(value=new_s, cost=cost, context=Context(step_count=1), log=[rec])


# ─────────────────────────────────────────────────────────────────────────────
# Kleisli composition
# ─────────────────────────────────────────────────────────────────────────────

# A TranslationStep is a function Imscription → ImscriptionM[Imscription]
TranslationStep = Callable[[Imscription], ImscriptionM[Imscription]]


def kleisli_compose(*steps: TranslationStep) -> TranslationStep:
    """
    Kleisli composition of translation steps:

        (t₁ >=> t₂ >=> ... >=> tₙ)(s) = t₁(s) >>= t₂ >>= ... >>= tₙ

    Costs accumulate additively in the Writer layer.
    Context (F-floor, criticality_ok) threads monotonically through steps.
    If any step fails (value=None), the chain short-circuits (MaybeT).
    """
    def composed(s: Imscription) -> ImscriptionM[Imscription]:
        result = ImscriptionM.return_(s)
        for step in steps:
            result = result.bind(step)
        return result
    return composed


def full_translation(
    s: Imscription,
    mutual_info_nats: Optional[float] = None,
) -> ImscriptionM[Imscription]:
    """
    Full structural→classical translation pipeline.

    Applies in order:
      1. translate_fidelity   — F_ℏ threshold check; degrade if needed
      2. translate_criticality — ⊙ → Phi_softsign if present
      3. translate_grammar    — convert non-classical grammars

    Total Δξ_CP = Σ costs across all three steps.

    Returns ImscriptionM with:
      - value:   translated Imscription (or None if blocked)
      - cost:    total nats of structural information lost
      - context: updated F-floor and criticality gate
      - log:     step-by-step trace
    """
    # Bind mutual_info_nats into the fidelity step via closure
    fidelity_step: TranslationStep = lambda s: translate_fidelity(s, mutual_info_nats)

    pipeline = kleisli_compose(
        fidelity_step,
        translate_criticality,
        translate_grammar,
    )
    return pipeline(s)


# ─────────────────────────────────────────────────────────────────────────────
# Cost summary
# ─────────────────────────────────────────────────────────────────────────────

def translation_cost_summary(result: ImscriptionM[Imscription]) -> TranslationCost:
    """
    Extract a structured TranslationCost from a completed ImscriptionM run.

    Classifies each StepRecord's delta_xi into the appropriate cost bucket
    based on which translation step produced it.
    """
    coherence = 0.0
    criticality = 0.0
    interaction = 0.0

    for step in result.log:
        if step.op == "translate_fidelity":
            coherence += step.delta_xi
        elif step.op == "translate_criticality":
            criticality += step.delta_xi
        elif step.op == "translate_grammar":
            interaction += step.delta_xi

    return TranslationCost(
        coherence_loss=coherence,
        criticality_loss=criticality,
        interaction_cost=interaction,
    )

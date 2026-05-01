"""
SynthonM — the Imscribing Grammar monad transformer stack.

    SynthonM[A] ≅ WriterT[float] (StateT[Context] (MaybeT Identity)) A

Effects carried:
    MaybeT    — computation may fail (value=None on BLOCKED/ERROR)
    WriterT   — accumulates Δξ_CP cost across all steps
    StateT    — carries Context (F-floor, criticality gate, step count)
    Log       — human-readable StepRecord list (not a formal effect, but carried)

Primitives:
    return_(a)        — lift a into the monad; zero cost, empty log
    m.bind(f)         — sequence: run m, feed value into f, merge effects
    m >> f            — operator alias for bind
    mzero()           — failed computation (value=None)
    m1.mplus(m2)      — try m1; if None, use m2
    m1 | m2           — operator alias for mplus

Monadic lifts (each wraps an algebra operation):
    join_m(name)              algebra.join
    meet_m(name)              algebra.meet
    tensor_m(name, lambda_)   algebra.tensor
    lift_m(target)            _LIFT_MAP[target]
    path_m(name, xi_tol)      algebra.find_path
    assert_m(pred, msg)       inline proof obligation

DesignStrategy type:
    DesignStrategy = Callable[[Synthon], SynthonM[Synthon]]

Strategy combinators:
    strategy_then(s1, s2)     sequential (s1 >> s2)
    strategy_or(s1, s2)       alternative (s1 <|> s2)
    optimize(synthon, strats) first-success search (asum)

See IG_LANG.md §Phase 3a for design rationale.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from .models import Synthon

A = TypeVar("A")
B = TypeVar("B")

# F-tier ordering for Context.f_floor comparisons
_F_ORDER: Dict[str, int] = {"F_ell": 0, "LOW": 0, "F_eth": 1, "MEDIUM": 1, "F_hbar": 2, "HIGH": 2}


@dataclass
class Context:
    """
    Monadic state threaded through every bind step.

    f_floor:        current minimum fidelity requirement raised by join/HotSwap
    criticality_ok: True once a criticality_lift has succeeded
    step_count:     total completed steps
    custom:         open dict for strategy-defined state
    """
    f_floor: Optional[str] = None
    criticality_ok: bool = False
    step_count: int = 0
    custom: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "Context":
        return Context(
            f_floor=self.f_floor,
            criticality_ok=self.criticality_ok,
            step_count=self.step_count,
            custom=dict(self.custom),
        )

    def merge(self, other: "Context") -> "Context":
        """
        Merge two contexts after a bind step.
        F-floor: take the stricter (higher) requirement.
        criticality_ok: OR (once granted, always granted).
        step_count: sum.
        custom: other overrides self on key collision.
        """
        result = self.copy()
        if other.f_floor is not None:
            if (result.f_floor is None or
                    _F_ORDER.get(other.f_floor, 0) > _F_ORDER.get(result.f_floor, 0)):
                result.f_floor = other.f_floor
        result.criticality_ok = self.criticality_ok or other.criticality_ok
        result.step_count = self.step_count + other.step_count
        result.custom.update(other.custom)
        return result


@dataclass
class StepRecord:
    """One entry in the monadic log."""
    op: str
    arg: str
    status: str        # PASS | BLOCKED | ERROR | ASSERT_PASS | ASSERT_FAIL | MZERO
    delta_xi: float
    message: str

    def __str__(self) -> str:
        icon = {"PASS": "✓", "ASSERT_PASS": "✓", "BLOCKED": "✗",
                "ASSERT_FAIL": "✗", "ERROR": "!", "MZERO": "·"}.get(self.status, "?")
        xi = f"  Δξ={self.delta_xi:+.3f}" if self.delta_xi != 0.0 else ""
        arg = f"({self.arg})" if self.arg else ""
        return f"[{self.status}] {icon} {self.op}{arg}{xi}  — {self.message}"


@dataclass
class SynthonM(Generic[A]):
    """
    The Imscribing Grammar monad.

        SynthonM[A] ≅ WriterT[float] (StateT[Context] (MaybeT Identity)) A

    value   — wrapped value; None if computation failed
    cost    — accumulated Δξ_CP (WriterT log)
    context — current Context (StateT state)
    log     — step trace (List[StepRecord])
    """
    value: Optional[A]
    cost: float = 0.0
    context: Context = field(default_factory=Context)
    log: List[StepRecord] = field(default_factory=list)

    # ── Monad primitives ────────────────────────────────────────────────────

    @classmethod
    def return_(cls, value: A) -> "SynthonM[A]":
        """Pure: lift value into the monad. Zero cost, empty log."""
        return cls(value=value, cost=0.0, context=Context(), log=[])

    def bind(self, f: "Callable[[A], SynthonM[B]]") -> "SynthonM[B]":
        """
        Monadic bind (>>=).

        If this computation failed (value is None), propagate the failure
        without calling f — MaybeT short-circuit.
        Otherwise, run f on the value and merge cost + context + log.
        """
        if self.value is None:
            return SynthonM(
                value=None,
                cost=self.cost,
                context=self.context,
                log=self.log,
            )
        result: SynthonM[B] = f(self.value)
        return SynthonM(
            value=result.value,
            cost=self.cost + result.cost,
            context=self.context.merge(result.context),
            log=self.log + result.log,
        )

    def __rshift__(self, f: "Callable[[A], SynthonM[B]]") -> "SynthonM[B]":
        """Operator alias: m >> f  ≡  m.bind(f)."""
        return self.bind(f)

    @classmethod
    def mzero(cls) -> "SynthonM[A]":
        """Failed computation — MonadPlus zero element."""
        return cls(
            value=None,
            cost=0.0,
            context=Context(),
            log=[StepRecord("mzero", "", "MZERO", 0.0, "Computation failed (mzero)")],
        )

    def mplus(self, other: "SynthonM[A]") -> "SynthonM[A]":
        """
        MonadPlus: try self; if it failed (value is None), use other.
        Both branches' logs are preserved for full trace visibility.
        Cost accumulates across both branches (Writer is append-only).
        """
        if self.value is not None:
            return self
        fallback_note = StepRecord(
            "mplus", "fallback", "PASS", 0.0,
            "Primary branch failed; switching to fallback"
        )
        return SynthonM(
            value=other.value,
            cost=self.cost + other.cost,
            context=self.context.merge(other.context),
            log=self.log + [fallback_note] + other.log,
        )

    def __or__(self, other: "SynthonM[A]") -> "SynthonM[A]":
        """Operator alias: m1 | m2  ≡  m1.mplus(m2)."""
        return self.mplus(other)

    # ── Extraction ──────────────────────────────────────────────────────────

    def run(self):
        """Extract (value, cost, context, log)."""
        return self.value, self.cost, self.context, self.log

    def is_success(self) -> bool:
        return self.value is not None

    def print_trace(self, numbered: bool = True) -> None:
        """Print a human-readable step trace to stdout."""
        for i, step in enumerate(self.log, 1):
            prefix = f"  {i}. " if numbered else "  "
            print(f"{prefix}{step}")
        status_str = "SUCCESS" if self.is_success() else "FAILED"
        name = getattr(self.value, "name", str(self.value)) if self.is_success() else "—"
        print(
            f"\n  Total Δξ_CP: {self.cost:+.3f} nat  |  "
            f"Steps: {len(self.log)}  |  {status_str}"
            + (f"  |  Result: {name}" if self.is_success() else "")
        )

    def to_dict(self) -> dict:
        """Serialize to dict for JSON output."""
        return {
            "success": self.is_success(),
            "result": getattr(self.value, "name", None) if self.value else None,
            "total_delta_xi": round(self.cost, 4),
            "context": {
                "f_floor": self.context.f_floor,
                "criticality_ok": self.context.criticality_ok,
                "step_count": self.context.step_count,
            },
            "steps": [
                {
                    "op": s.op,
                    "arg": s.arg,
                    "status": s.status,
                    "delta_xi": round(s.delta_xi, 4),
                    "message": s.message,
                }
                for s in self.log
            ],
        }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _load(name: str) -> Synthon:
    """Load a synthon from the global catalog by name. Raises KeyError if absent."""
    from .registry import global_catalog
    s = global_catalog.get(name)
    if s is None:
        raise KeyError(f"Synthon '{name}' not found in catalog")
    return s


def _synthon_from_lattice(result, name: str) -> Synthon:
    """
    Build a Synthon from a LatticeResult.
    Fields that are the CONFLICT sentinel are replaced with the source synthon's value.
    """
    from .algebra import CONFLICT as _CONFLICT  # sentinel object

    def _pick(val, fallback):
        return fallback if val is _CONFLICT else (fallback if val == _CONFLICT else val)

    # get a fallback synthon (s1) from the result
    try:
        fallback = _load(result.s1_name)
    except Exception:
        fallback = None

    def _f(attr):
        val = getattr(result, attr, _CONFLICT)
        fb = getattr(fallback, attr, None) if fallback else None
        return _pick(val, fb)

    return Synthon(
        name=name,
        dimensionality=_f("dimensionality"),
        topology=_f("topology"),
        recognition_mode=_f("recognition_mode"),
        polarity=_f("polarity"),
        fidelity=_f("fidelity"),
        kinetic_character=_f("kinetic_character"),
        granularity=_f("granularity"),
        interaction_grammar=_f("interaction_grammar"),
        criticality_phase=_f("criticality_phase"),
        stoichiometry=_f("stoichiometry"),
        description=f"{result.operation}({result.s1_name}, {result.s2_name})",
    )


def _synthon_from_tensor(result, name: str) -> Synthon:
    """Build a Synthon from a TensorResult."""
    return Synthon(
        name=name,
        dimensionality=result.dimensionality,
        topology=result.topology,
        recognition_mode=result.recognition_mode,
        polarity=result.polarity,
        fidelity=result.fidelity,
        kinetic_character=result.kinetic_character,
        granularity=result.granularity,
        interaction_grammar=result.interaction_grammar,
        criticality_phase=result.criticality_phase,
        stoichiometry=result.stoichiometry,
        description=f"tensor({result.s1_name}, {result.s2_name})",
        metadata={"xi_cp_predicted": result.xi_cp_predicted},
    )


# ── Monadic lifts ─────────────────────────────────────────────────────────────

def join_m(other_name: str) -> "Callable[[Synthon], SynthonM[Synthon]]":
    """Lift algebra.join into SynthonM."""
    def _step(synthon: Synthon) -> SynthonM[Synthon]:
        from .algebra import join
        try:
            other = _load(other_name)
            result = join(synthon, other)
            if result.conflicts:
                rec = StepRecord(
                    "join", other_name, "BLOCKED", 0.0,
                    f"CONFLICT on primitives: {result.conflicts}"
                )
                return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
            new_s = _synthon_from_lattice(result, f"join({synthon.name},{other_name})")
            fidelity_name = getattr(new_s.fidelity, "value", str(new_s.fidelity)) if new_s.fidelity else None
            rec = StepRecord(
                "join", other_name, "PASS", 0.0,
                f"F→{fidelity_name}  notes: {'; '.join(result.notes[:2])}"
            )
            ctx = Context(f_floor=fidelity_name, step_count=1)
            return SynthonM(value=new_s, cost=0.0, context=ctx, log=[rec])
        except Exception as e:
            rec = StepRecord("join", other_name, "ERROR", 0.0, str(e))
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
    return _step


def meet_m(other_name: str) -> "Callable[[Synthon], SynthonM[Synthon]]":
    """Lift algebra.meet into SynthonM."""
    def _step(synthon: Synthon) -> SynthonM[Synthon]:
        from .algebra import meet
        try:
            other = _load(other_name)
            result = meet(synthon, other)
            if result.conflicts:
                rec = StepRecord(
                    "meet", other_name, "BLOCKED", 0.0,
                    f"CONFLICT on primitives: {result.conflicts}"
                )
                return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
            new_s = _synthon_from_lattice(result, f"meet({synthon.name},{other_name})")
            rec = StepRecord(
                "meet", other_name, "PASS", 0.0,
                f"Meet succeeded  notes: {'; '.join(result.notes[:2])}"
            )
            return SynthonM(value=new_s, cost=0.0, context=Context(step_count=1), log=[rec])
        except Exception as e:
            rec = StepRecord("meet", other_name, "ERROR", 0.0, str(e))
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
    return _step


def tensor_m(
    other_name: str,
    lambda_: float = 0.3,
) -> "Callable[[Synthon], SynthonM[Synthon]]":
    """Lift algebra.tensor into SynthonM."""
    def _step(synthon: Synthon) -> SynthonM[Synthon]:
        from .algebra import tensor
        try:
            other = _load(other_name)
            result = tensor(synthon, other, lambda_=lambda_)
            new_s = _synthon_from_tensor(result, f"tensor({synthon.name},{other_name})")
            xi_ens = result.xi_cp_predicted or 0.0
            rec = StepRecord(
                "tensor", other_name, "PASS", xi_ens,
                f"ξ_ens={xi_ens:.3f}  discount={result.mutual_info_correction:.3f}"
            )
            fidelity_name = getattr(new_s.fidelity, "value", str(new_s.fidelity)) if new_s.fidelity else None
            ctx = Context(f_floor=fidelity_name, step_count=1)
            return SynthonM(value=new_s, cost=xi_ens, context=ctx, log=[rec])
        except Exception as e:
            rec = StepRecord("tensor", other_name, "ERROR", 0.0, str(e))
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
    return _step


def lift_m(target: str) -> "Callable[[Synthon], SynthonM[Synthon]]":
    """Lift algebra._LIFT_MAP[target] into SynthonM."""
    def _step(synthon: Synthon) -> SynthonM[Synthon]:
        from .algebra import _LIFT_MAP
        fn = _LIFT_MAP.get(target)
        if fn is None:
            rec = StepRecord("lift", target, "ERROR", 0.0,
                             f"Unknown lift target '{target}'. "
                             f"Valid: {list(_LIFT_MAP.keys())}")
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
        try:
            result = fn(synthon)
            if not result.applicable:
                rec = StepRecord(
                    "lift", target, "BLOCKED", 0.0,
                    "; ".join(result.notes) if result.notes else "Lift not applicable"
                )
                return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
            new_s = result.synthon or synthon
            ctx = Context(
                criticality_ok=(target in ("critical", "criticality")),
                step_count=1,
            )
            msg = "; ".join(result.notes[:2]) if result.notes else f"Lift {target} applied"
            if result.warnings:
                msg += f"  ⚠ {result.warnings[0]}"
            rec = StepRecord("lift", target, "PASS", 0.0, msg)
            return SynthonM(value=new_s, cost=0.0, context=ctx, log=[rec])
        except Exception as e:
            rec = StepRecord("lift", target, "ERROR", 0.0, str(e))
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
    return _step


def path_m(
    target_name: str,
    xi_tolerance: float = 2.0,
    max_hops: int = 6,
) -> "Callable[[Synthon], SynthonM[Synthon]]":
    """Lift algebra.find_path into SynthonM."""
    def _step(synthon: Synthon) -> SynthonM[Synthon]:
        from .algebra import find_path
        from .registry import global_catalog
        try:
            target = _load(target_name)
            catalog = list(global_catalog._synthons.values())
            result = find_path(
                synthon, target, catalog,
                max_hops=max_hops, xi_tolerance=xi_tolerance,
            )
            if not result.found:
                reason = "; ".join(result.notes) if result.notes else "No valid path found"
                rec = StepRecord("path", target_name, "BLOCKED", 0.0, reason)
                return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
            delta = result.total_delta
            rec = StepRecord(
                "path", target_name, "PASS", delta,
                f"{result.n_hops} hop(s), Δξ_CP={delta:+.3f} nat"
            )
            return SynthonM(
                value=target,
                cost=delta,
                context=Context(step_count=result.n_hops),
                log=[rec],
            )
        except Exception as e:
            rec = StepRecord("path", target_name, "ERROR", 0.0, str(e))
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
    return _step


def assert_m(
    predicate: "Callable[[Synthon], bool]",
    message: str = "",
) -> "Callable[[Synthon], SynthonM[Synthon]]":
    """
    Inline proof obligation.
    Passes the synthon through unchanged if predicate(synthon) is True.
    Fails (value=None) otherwise — the computation is blocked.
    """
    def _step(synthon: Synthon) -> SynthonM[Synthon]:
        try:
            ok = bool(predicate(synthon))
        except Exception as e:
            rec = StepRecord("assert", message or "?", "ERROR", 0.0, str(e))
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
        if ok:
            rec = StepRecord(
                "assert", message or "predicate", "ASSERT_PASS", 0.0,
                f"✓ {message or 'predicate passed'}"
            )
            return SynthonM(value=synthon, cost=0.0, context=Context(step_count=1), log=[rec])
        else:
            rec = StepRecord(
                "assert", message or "predicate", "ASSERT_FAIL", 0.0,
                f"✗ {message or 'predicate'} — assertion not satisfied"
            )
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])
    return _step


# ── DesignStrategy type + combinators ─────────────────────────────────────────

# A DesignStrategy is a function from Synthon to a monadic computation.
DesignStrategy = Callable[[Synthon], SynthonM[Synthon]]


def strategy_then(s1: DesignStrategy, s2: DesignStrategy) -> DesignStrategy:
    """Sequential composition: s1 then s2  (do { x <- s1; s2 x })."""
    return lambda synthon: SynthonM.return_(synthon).bind(s1).bind(s2)


def strategy_or(s1: DesignStrategy, s2: DesignStrategy) -> DesignStrategy:
    """Alternative: try s1; fallback to s2 if s1 fails  (s1 <|> s2)."""
    return lambda synthon: (
        SynthonM.return_(synthon).bind(s1)
        .mplus(SynthonM.return_(synthon).bind(s2))
    )


def optimize(
    synthon: Synthon,
    strategies: "List[DesignStrategy]",
) -> "SynthonM[Synthon]":
    """
    Try each strategy in order; return the first that succeeds.
    Equivalent to asum / msum over the strategy list.
    Accumulates the full attempt log across all tried strategies.
    """
    result: SynthonM[Synthon] = SynthonM.mzero()
    for strat in strategies:
        result = result.mplus(SynthonM.return_(synthon).bind(strat))
        if result.is_success():
            break
    return result

"""
syn_runner — .syn YAML DSL evaluator for Imscribing Grammar.

Parses a .syn design script and evaluates it as a SynthonM monadic pipeline.

.syn YAML schema
────────────────
  version: "1.0"
  start: <synthon_name>
  strategies:              # optional: named reusable sub-pipelines
    my_strategy:
      - join: foo
      - lift: critical
  do:
    - join:   <name>
    - meet:   <name>
    - tensor: <name>
      lambda: <float>      # default 0.3
    - lift:   <target>
    - path:   <name>
      xi_tolerance: <float>  # default 2.0
      max_hops: <int>        # default 6
    - assert:
        expr:    <predicate_string>
        message: <human-readable label>
    - bind: <strategy_name>  # reference to strategies block
  output:
    format: text | json      # default text
    save: <path>             # optional: write JSON result to file

Predicate grammar for assert.expr (no eval — safe dispatch only)
────────────────────────────────────────────────────────────────
  phi_c_score > N
  phi_c_score >= N
  fidelity == F_hbar | F_eth | F_ell | LOW | MEDIUM | HIGH
  topology == T_bowtie | T_cyclic | ...
  criticality_phase == Phi_c | Phi_sub | Phi_n
  axiom6_satisfied
  gd_degeneracy == <type_string>
  reset_type == discrete | continuous

See IG_LANG.md §3a.2 for design rationale.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from .models import Synthon
from .monad import (
    SynthonM,
    DesignStrategy,
    Context,
    StepRecord,
    join_m,
    meet_m,
    tensor_m,
    lift_m,
    path_m,
    assert_m,
    strategy_then,
    optimize,
)


# ── Custom error types ────────────────────────────────────────────────────────

class SynParseError(ValueError):
    """Malformed .syn file."""


class UnknownAssertion(SynParseError):
    """Assert expr not in the dispatch grammar."""


# ── Safe predicate compiler ───────────────────────────────────────────────────

def _compile_predicate(expr: str) -> Callable[[Synthon], bool]:
    """
    Compile a predicate string into a callable (Synthon → bool).

    Supported forms:
        phi_c_score > N            — Varma probe score
        phi_c_score >= N
        fidelity == <tier>
        topology == <topology>
        criticality_phase == <phase>
        axiom6_satisfied
        gd_degeneracy == <type>
        reset_type == discrete | continuous
    """
    expr = expr.strip()

    # phi_c_score > N  /  phi_c_score >= N
    m = re.fullmatch(r"phi_c_score\s*(>=|>)\s*([0-9]*\.?[0-9]+)", expr)
    if m:
        op, threshold = m.group(1), float(m.group(2))
        def _phi_c(s: Synthon, _op=op, _t=threshold) -> bool:
            from .varma_probe import score_phi_c_candidacy
            rep = score_phi_c_candidacy(s)
            return rep.score >= _t if _op == ">=" else rep.score > _t
        return _phi_c

    # fidelity == <tier>
    m = re.fullmatch(r"fidelity\s*==\s*(\w+)", expr)
    if m:
        tier = m.group(1).upper()
        def _fid(s: Synthon, _tier=tier) -> bool:
            f = s.fidelity
            return (f.value.upper() == _tier if hasattr(f, "value") else str(f).upper() == _tier)
        return _fid

    # topology == <topology>
    m = re.fullmatch(r"topology\s*==\s*(\S+)", expr)
    if m:
        topo = m.group(1).upper()
        def _top(s: Synthon, _topo=topo) -> bool:
            t = s.topology
            raw = (t.value.upper() if hasattr(t, "value") else str(t).upper())
            return raw == _topo or raw.replace("_", "") == _topo.replace("_", "")
        return _top

    # criticality_phase == <phase>
    m = re.fullmatch(r"criticality_phase\s*==\s*(\S+)", expr)
    if m:
        phase = m.group(1).upper()
        def _cp(s: Synthon, _phase=phase) -> bool:
            p = s.criticality_phase
            raw = (p.value.upper() if hasattr(p, "value") else str(p).upper())
            return raw == _phase
        return _cp

    # axiom6_satisfied  (no arguments)
    if re.fullmatch(r"axiom6_satisfied", expr):
        def _ax6(s: Synthon) -> bool:
            from .constraints import AxiomValidator
            result = AxiomValidator.validate_axiom6_temporal_grounding(s)
            return not result.violated
        return _ax6

    # gd_degeneracy == <type>
    m = re.fullmatch(r"gd_degeneracy\s*==\s*(\S+)", expr)
    if m:
        deg_type = m.group(1).lower()
        def _gd(s: Synthon, _dt=deg_type) -> bool:
            from .varma_probe import score_phi_c_candidacy
            rep = score_phi_c_candidacy(s)
            raw = (rep.gd_degeneracy_type or "").lower()
            return raw == _dt
        return _gd

    # reset_type == discrete | continuous
    m = re.fullmatch(r"reset_type\s*==\s*(discrete|continuous)", expr)
    if m:
        rtype = m.group(1).lower()
        def _rt(s: Synthon, _rt=rtype) -> bool:
            sg = getattr(s, "grounding", None) or {}
            block = sg.get("reset", {})
            if not block:
                block = (getattr(s, "metadata", None) or {}).get("grounding", {}).get("reset", {})
            return block.get("type", "discrete").lower() == _rt
        return _rt

    raise UnknownAssertion(
        f"Unknown assert predicate: {expr!r}\n"
        "Supported forms: phi_c_score >/>= N, fidelity == X, topology == X, "
        "criticality_phase == X, axiom6_satisfied, gd_degeneracy == X, "
        "reset_type == discrete|continuous"
    )


# ── Step compiler ─────────────────────────────────────────────────────────────

def _compile_step(
    step_spec: Any,
    named_strategies: Dict[str, DesignStrategy],
) -> DesignStrategy:
    """
    Compile one step-spec from the `do:` list into a DesignStrategy.

    step_spec may be:
        "join: foo"             (string shorthand — not typical in YAML)
        {"join": "foo"}         (single-key dict, simple)
        {"tensor": "foo", "lambda": 0.4}
        {"path": "foo", "xi_tolerance": 1.5, "max_hops": 6}
        {"assert": {"expr": "...", "message": "..."}}
        {"bind": "my_strategy"}
    """
    if isinstance(step_spec, str):
        # "op: arg" shorthand
        parts = step_spec.split(":", 1)
        op = parts[0].strip().lower()
        arg = parts[1].strip() if len(parts) > 1 else ""
        step_spec = {op: arg}

    if not isinstance(step_spec, dict):
        raise SynParseError(f"Unexpected step type {type(step_spec)}: {step_spec!r}")

    # Normalise: allow both {"join": "foo"} and {"op": "join", "arg": "foo"}
    keys = list(step_spec.keys())

    # ── join ──────────────────────────────────────────────────────────────
    if "join" in step_spec:
        return join_m(str(step_spec["join"]))

    # ── meet ──────────────────────────────────────────────────────────────
    if "meet" in step_spec:
        return meet_m(str(step_spec["meet"]))

    # ── tensor ────────────────────────────────────────────────────────────
    if "tensor" in step_spec:
        lam = float(step_spec.get("lambda", 0.3))
        return tensor_m(str(step_spec["tensor"]), lambda_=lam)

    # ── lift ──────────────────────────────────────────────────────────────
    if "lift" in step_spec:
        return lift_m(str(step_spec["lift"]))

    # ── path ──────────────────────────────────────────────────────────────
    if "path" in step_spec:
        xi_tol = float(step_spec.get("xi_tolerance", 2.0))
        max_hops = int(step_spec.get("max_hops", 6))
        return path_m(str(step_spec["path"]), xi_tolerance=xi_tol, max_hops=max_hops)

    # ── assert ────────────────────────────────────────────────────────────
    if "assert" in step_spec:
        spec = step_spec["assert"]
        if isinstance(spec, str):
            expr, msg = spec, spec
        elif isinstance(spec, dict):
            expr = spec.get("expr", "")
            msg = spec.get("message", expr)
        else:
            raise SynParseError(f"assert: block must be a string or dict, got {type(spec)}")
        pred = _compile_predicate(expr)
        return assert_m(pred, message=msg)

    # ── bind (named strategy reference) ──────────────────────────────────
    if "bind" in step_spec:
        strat_name = str(step_spec["bind"])
        if strat_name not in named_strategies:
            raise SynParseError(
                f"bind: unknown strategy '{strat_name}'. "
                f"Defined strategies: {list(named_strategies.keys())}"
            )
        return named_strategies[strat_name]

    # ── or (try primary; fallback on failure — strategy_or / mplus) ───────
    if "or" in step_spec:
        branches = step_spec["or"]
        if not isinstance(branches, list) or len(branches) < 2:
            raise SynParseError(
                "or: requires a list of at least 2 step specs\n"
                "  e.g.:\n"
                "    - or:\n"
                "        - join: foo\n"
                "        - join: bar"
            )
        from .monad import strategy_or as _strategy_or
        compiled = [_compile_step(b, named_strategies) for b in branches]
        result_strat = compiled[0]
        for branch in compiled[1:]:
            result_strat = _strategy_or(result_strat, branch)
        return result_strat

    raise SynParseError(
        f"Unrecognised step key(s): {keys!r}. "
        "Valid ops: join, meet, tensor, lift, path, assert, bind, or"
    )


# ── Strategy block compiler ───────────────────────────────────────────────────

def _compile_strategy_block(
    steps: List[Any],
    named_strategies: Dict[str, DesignStrategy],
) -> DesignStrategy:
    """
    Compile a list of step-specs into a single sequential DesignStrategy.
    """
    compiled = [_compile_step(s, named_strategies) for s in steps]
    if not compiled:
        return lambda syn: SynthonM.return_(syn)  # identity
    result = compiled[0]
    for step in compiled[1:]:
        result = strategy_then(result, step)
    return result


# ── Output-assertion compiler (post-hoc cost / context checks) ───────────────

import re as _re

_OUT_ASSERT_OPS = {
    "<":  lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
}


def _compile_output_assertion(expr: str):
    """
    Compile a single output.assert expression.
    Returns (label, checker) where checker(result: SynthonM) -> (bool, str).

    Supported forms:
        total_delta_xi < N
        total_delta_xi <= N
        total_delta_xi > N
        total_delta_xi >= N
        steps <= N
        criticality_ok == true|false
    """
    expr = expr.strip()

    m = _re.fullmatch(r"total_delta_xi\s*(<=?|>=?|==)\s*([0-9]*\.?[0-9]+)", expr)
    if m:
        op_str, threshold = m.group(1), float(m.group(2))
        op_fn = _OUT_ASSERT_OPS[op_str]
        def _check_cost(result, _op=op_fn, _t=threshold, _e=expr):
            ok = _op(result.cost, _t)
            detail = f"Δξ_CP={result.cost:+.3f} {_e.split()[1]} {_t}"
            return ok, detail
        return expr, _check_cost

    m = _re.fullmatch(r"steps\s*(<=?|>=?|==)\s*([0-9]+)", expr)
    if m:
        op_str, threshold = m.group(1), int(m.group(2))
        op_fn = _OUT_ASSERT_OPS[op_str]
        def _check_steps(result, _op=op_fn, _t=threshold, _e=expr):
            n = len(result.log)
            ok = _op(n, _t)
            return ok, f"steps={n} {_e.split()[1]} {_t}"
        return expr, _check_steps

    m = _re.fullmatch(r"criticality_ok\s*==\s*(true|false)", expr, _re.IGNORECASE)
    if m:
        expected = m.group(1).lower() == "true"
        def _check_crit(result, _exp=expected):
            ok = result.context.criticality_ok == _exp
            return ok, f"criticality_ok={result.context.criticality_ok} (expected {_exp})"
        return expr, _check_crit

    raise SynParseError(
        f"Unknown output.assert expression: {expr!r}\n"
        "Supported: total_delta_xi </>/<=/>=/<> N, steps <= N, criticality_ok == true|false"
    )


def _compile_output_assertions(assert_block) -> list:
    """Parse output.assert into a list of (label, checker) pairs."""
    if not assert_block:
        return []
    if isinstance(assert_block, str):
        assert_block = [assert_block]
    return [_compile_output_assertion(str(e)) for e in assert_block]


# ── Public API ────────────────────────────────────────────────────────────────

class SynScript:
    """
    A parsed and compiled .syn design script.

    Use `SynScript.from_file(path)` or `SynScript.from_string(text)` to load.
    Call `.run()` to evaluate and get back a `SynthonM[Synthon]`.
    """

    def __init__(
        self,
        start_name: str,
        strategy: DesignStrategy,
        output_format: str = "text",
        save_path: Optional[str] = None,
        raw: Optional[dict] = None,
    ):
        self.start_name = start_name
        self.strategy = strategy
        self.output_format = output_format
        self.save_path = save_path
        self._raw = raw or {}
        self._output_assertions: list = []  # set by _compile if output.assert present

    # ── Loaders ───────────────────────────────────────────────────────────

    @classmethod
    def from_file(cls, path: str | Path) -> "SynScript":
        """Load and compile a .syn YAML file."""
        text = Path(path).read_text(encoding="utf-8")
        return cls.from_string(text)

    @classmethod
    def from_string(cls, text: str) -> "SynScript":
        """Load and compile a .syn YAML string."""
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise SynParseError(f"YAML parse error: {e}") from e

        return cls._compile(raw)

    # ── Compiler ──────────────────────────────────────────────────────────

    @classmethod
    def _compile(cls, raw: dict) -> "SynScript":
        if not isinstance(raw, dict):
            raise SynParseError("Top-level .syn document must be a YAML mapping")

        # version check (lenient — warn only)
        version = str(raw.get("version", "1.0"))
        if version not in ("1.0", "1"):
            import warnings
            warnings.warn(f"syn_runner: unknown .syn version {version!r}; proceeding anyway")

        start_name = raw.get("start")
        if not start_name:
            raise SynParseError("Missing required field: start")
        start_name = str(start_name)

        # compile named strategies block first (they may be referenced in do:)
        named_strategies: Dict[str, DesignStrategy] = {}
        for strat_name, strat_steps in (raw.get("strategies") or {}).items():
            if not isinstance(strat_steps, list):
                raise SynParseError(
                    f"strategies.{strat_name}: value must be a list of steps"
                )
            named_strategies[strat_name] = _compile_strategy_block(
                strat_steps, named_strategies
            )

        # compile do: block
        do_steps = raw.get("do") or []
        if not isinstance(do_steps, list):
            raise SynParseError("do: must be a YAML sequence")
        main_strategy = _compile_strategy_block(do_steps, named_strategies)

        # output block
        output_block = raw.get("output") or {}
        out_format = str(output_block.get("format", "text")).lower()
        save_path = output_block.get("save")
        if save_path:
            save_path = str(save_path)

        # output.assert: post-hoc cost + context checks (evalRWS-style)
        # These run AFTER the pipeline completes and can inspect total cost.
        # Syntax:
        #   output:
        #     assert:
        #       total_delta_xi < 15.0
        #       total_delta_xi >= 0.0
        output_assertions = _compile_output_assertions(
            output_block.get("assert") or []
        )

        inst = cls(
            start_name=start_name,
            strategy=main_strategy,
            output_format=out_format,
            save_path=save_path,
            raw=raw,
        )
        inst._output_assertions = output_assertions
        return inst

    # ── Validation (dry-run) ──────────────────────────────────────────────

    def validate(self) -> List[str]:
        """
        Validate the script without executing it.
        Returns a list of warning strings (empty = clean).
        Checks: start synthon exists in catalog.
        """
        from .registry import global_catalog
        warnings_list: List[str] = []
        if global_catalog.get(self.start_name) is None:
            warnings_list.append(
                f"start: synthon '{self.start_name}' not found in catalog"
            )
        return warnings_list

    # ── Execution ─────────────────────────────────────────────────────────

    def run(self) -> SynthonM[Synthon]:
        """
        Execute the compiled pipeline and return the resulting SynthonM.
        """
        from .registry import global_catalog

        start = global_catalog.get(self.start_name)
        if start is None:
            rec = StepRecord(
                "start", self.start_name, "ERROR", 0.0,
                f"Synthon '{self.start_name}' not found in catalog"
            )
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])

        result = SynthonM.return_(start).bind(self.strategy)

        # Apply output.assert post-hoc checks (evalRWS-style cost/context gates)
        if self._output_assertions and result.value is not None:
            extra_log = list(result.log)
            failed = False
            for label, checker in self._output_assertions:
                ok, detail = checker(result)
                status = "ASSERT_PASS" if ok else "ASSERT_FAIL"
                rec = StepRecord("assert_output", label, status, 0.0,
                                 f"{'✓' if ok else '✗'} {detail}")
                extra_log.append(rec)
                if not ok:
                    failed = True
            result = SynthonM(
                value=result.value if not failed else None,
                cost=result.cost,
                context=result.context,
                log=extra_log,
            )

        return result


# ── Convenience function ──────────────────────────────────────────────────────

def run_syn_file(
    path: str | Path,
    *,
    dry_run: bool = False,
    format_override: Optional[str] = None,
    save_override: Optional[str] = None,
) -> SynthonM[Synthon]:
    """
    Parse, optionally validate, and run a .syn file.

    Returns the SynthonM result (or a failed SynthonM on dry-run with errors).
    """
    script = SynScript.from_file(path)

    if format_override:
        script.output_format = format_override.lower()
    if save_override:
        script.save_path = save_override

    warnings_list = script.validate()
    if warnings_list:
        # surface warnings but don't abort unless dry-run
        for w in warnings_list:
            import warnings
            warnings.warn(f"syn validation: {w}")
        if dry_run:
            rec = StepRecord(
                "validate", str(path), "ERROR", 0.0,
                "; ".join(warnings_list)
            )
            return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])

    if dry_run:
        rec = StepRecord(
            "validate", str(path), "PASS", 0.0,
            f"Dry-run OK — start='{script.start_name}', "
            f"steps={len(script._raw.get('do') or [])}"
        )
        return SynthonM(value=None, cost=0.0, context=Context(), log=[rec])

    return script.run()

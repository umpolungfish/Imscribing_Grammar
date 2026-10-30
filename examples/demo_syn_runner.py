#!/usr/bin/env python3
"""
demo_syn_runner.py — Phase 3a Demo: Typed Design Programs for Matter

Demonstrates what `imscribe run` and the ImscriptionM monad enable that was not
possible with the previous ad-hoc pipeline interface:

  Demo 1 — Certification chain          (01_certify_soai.syn)
  Demo 2 — Type-level gate (blocked)    (02_certify_proline.syn)
  Demo 3 — Reusable named strategies    (03_reusable_strategy.syn)
  Demo 4 — Fallback / mplus search      (04_fallback_search.syn)
  Demo 5 — Ensemble design + JSON save  (05_ensemble_design.syn)

Run from the repo root:
    python examples/demo_syn_runner.py

Or run any script individually:
    imscribe run examples/syn_demo/01_certify_soai.syn
"""

import json
import sys
import textwrap
from pathlib import Path

# Ensure package is importable from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from imscrbgrmr import SynScript, SynParseError  # noqa: E402
from imscrbgrmr.registry import global_catalog    # noqa: E402

global_catalog.populate_defaults()

# ── Formatting helpers ────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD  = "\033[1m"
GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW= "\033[33m"
CYAN  = "\033[36m"
DIM   = "\033[2m"

def header(title: str, subtitle: str = "") -> None:
    bar = "═" * 68
    print(f"\n{BOLD}{bar}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    if subtitle:
        print(f"  {DIM}{subtitle}{RESET}")
    print(f"{BOLD}{bar}{RESET}\n")

def narrate(text: str) -> None:
    for line in textwrap.wrap(text, width=66):
        print(f"  {DIM}{line}{RESET}")
    print()

def run_script(path: Path, label: str, description: str) -> None:
    print(f"{BOLD}{CYAN}▶  {label}{RESET}")
    narrate(description)

    script = SynScript.from_file(path)
    result = script.run()

    _icons  = {"PASS": "✓", "ASSERT_PASS": "✓", "BLOCKED": "✗",
               "ASSERT_FAIL": "✗", "ERROR": "!", "MZERO": "·"}
    _colors = {"PASS": GREEN, "ASSERT_PASS": GREEN,
               "BLOCKED": RED, "ASSERT_FAIL": YELLOW, "ERROR": RED, "MZERO": DIM}

    fail_at = None
    for i, step in enumerate(result.log, 1):
        icon  = _icons.get(step.status, "?")
        col   = _colors.get(step.status, RESET)
        xi_s  = f"  Δξ={step.delta_xi:+.3f}" if step.delta_xi != 0.0 else ""
        arg_s = f"({step.arg})" if step.arg else ""
        print(f"  {i:>2}. {col}[{step.status:<11}] {icon} {step.op}{arg_s}{xi_s}{RESET}")
        print(f"       {DIM}{step.message}{RESET}")
        if fail_at is None and step.status in ("BLOCKED", "ERROR", "ASSERT_FAIL"):
            fail_at = i

    outcome = f"{GREEN}SUCCESS{RESET}" if result.is_success() else f"{RED}FAILED{RESET}"
    fail_note = f"  |  blocked at step {fail_at}" if fail_at else ""
    print(
        f"\n  Total Δξ_CP: {result.cost:+.3f} nat  |  "
        f"Steps: {len(result.log)}  |  {outcome}{fail_note}"
    )
    if result.is_success():
        name = getattr(result.value, "name", str(result.value))
        print(f"  Result: {CYAN}{name}{RESET}")
    print()


# ── Demo scripts ──────────────────────────────────────────────────────────────

DEMO_DIR = Path(__file__).parent / "syn_demo"


def demo1_certification() -> None:
    header(
        "Demo 1 — Certification Chain",
        "All four proof obligations pass → Soai admitted to ensemble pool"
    )
    narrate(
        "A certification protocol is a .syn script that acts as a typed gate. "
        "Each assert is a proof obligation. The pipeline only completes if every "
        "obligation is discharged in order: Axiom 6 grounding, reset class, "
        "⊙ candidacy threshold, high-confidence threshold. "
        "If any fails, the certification is denied and the step trace explains why."
    )
    run_script(
        DEMO_DIR / "01_certify_soai.syn",
        label="01_certify_soai.syn",
        description=(
            "Four sequential proof obligations on the Soai pyrimidyl autocatalytic "
            "cycle. Axiom 6 grounding, continuous reset type, ⊙ > 0.50, ⊙ > 0.80."
        ),
    )


def demo2_type_gate() -> None:
    header(
        "Demo 2 — Type-Level Gate (blocked pipeline)",
        "Same protocol, different system → blocked at step 2"
    )
    narrate(
        "The proline aldol cycle is a legitimate D_∞ system — fully grounded, "
        "Axiom 6 satisfied — but it has a DISCRETE reset, not a continuous one. "
        "The certification protocol for continuous-dissipative systems correctly "
        "blocks it at step 2 without running the ⊙ probe at all. "
        "This is not an error: it is a type-level distinction. Proline belongs "
        "in a different protocol (discrete-reset certification)."
    )
    run_script(
        DEMO_DIR / "02_certify_proline.syn",
        label="02_certify_proline.syn",
        description=(
            "Same four proof obligations, applied to proline_aldol_cycle. "
            "Passes Axiom 6, then blocks on reset_type == continuous."
        ),
    )


def demo3_strategy_composition() -> None:
    header(
        "Demo 3 — Reusable Named Strategies",
        "strategies: block defines a sub-pipeline; bind: invokes it by name"
    )
    narrate(
        "The strategies: block lets you name a sub-pipeline and reuse it across "
        "scripts. Here, molecular_hbond_upgrade traverses the carboxylic acid "
        "dimer to the adenine-thymine pair (a 1-hop HotSwap path) and asserts "
        "high fidelity. Once bound, the main do: block tensors the result with "
        "the Soai cycle to form a molecular/temporal ensemble."
    )
    run_script(
        DEMO_DIR / "03_reusable_strategy.syn",
        label="03_reusable_strategy.syn",
        description=(
            "Defines molecular_hbond_upgrade strategy, binds it, then tensors "
            "with soai_pyrimidyl_autocatalytic_cycle (λ=0.35)."
        ),
    )


def demo4_fallback_search() -> None:
    header(
        "Demo 4 — Fallback Design Search  (or: / mplus)",
        "Primary join blocked on P+∈ conflict → fallback join succeeds"
    )
    narrate(
        "The or: step expresses the MonadPlus mplus operator directly in YAML. "
        "Branch A tries to join carboxylic_acid_dimer with adenine_thymine_pair — "
        "this is blocked by a real primitive conflict (polarity and interaction "
        "grammar mismatch). Branch B falls through to CB7·ferrocene, which is "
        "compatible. Both attempts are recorded in the step trace. The pipeline "
        "continues from the successful branch and asserts fidelity, then tensors."
    )
    run_script(
        DEMO_DIR / "04_fallback_search.syn",
        label="04_fallback_search.syn",
        description=(
            "or: tries adenine_thymine join (conflicts on P+∈), falls back to "
            "CB7_ferrocene join (no conflict). Continues with fidelity assert "
            "and tensor with Soai."
        ),
    )


def demo5_ensemble_json() -> None:
    header(
        "Demo 5 — Ensemble Design + JSON Output",
        "Named strategies compose; result saved to ensemble_result.json"
    )
    narrate(
        "Two named strategies (certify_temporal_seed, verify_soai_geometry) run "
        "sequentially via bind:. Once the temporal seed is certified, the pipeline "
        "tensors it with the adenine-thymine molecular pair to form a "
        "molecular/temporal ensemble. The output: format: json block writes a "
        "machine-readable result to ensemble_result.json for downstream tooling "
        "(the Ensembler or a Jupyter notebook)."
    )

    # Run programmatically so we can read and display the saved JSON
    script = SynScript.from_file(DEMO_DIR / "05_ensemble_design.syn")
    # Redirect save to /tmp so we don't clutter the repo
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    script.save_path = tmp.name

    result = script.run()

    print(f"  {BOLD}{CYAN}▶  05_ensemble_design.syn{RESET}")
    print()

    _icons  = {"PASS": "✓", "ASSERT_PASS": "✓", "BLOCKED": "✗",
               "ASSERT_FAIL": "✗", "ERROR": "!", "MZERO": "·"}
    _colors = {"PASS": GREEN, "ASSERT_PASS": GREEN,
               "BLOCKED": RED, "ASSERT_FAIL": YELLOW, "ERROR": RED, "MZERO": DIM}

    fail_at = None
    for i, step in enumerate(result.log, 1):
        icon  = _icons.get(step.status, "?")
        col   = _colors.get(step.status, RESET)
        xi_s  = f"  Δξ={step.delta_xi:+.3f}" if step.delta_xi != 0.0 else ""
        arg_s = f"({step.arg})" if step.arg else ""
        print(f"  {i:>2}. {col}[{step.status:<11}] {icon} {step.op}{arg_s}{xi_s}{RESET}")
        print(f"       {DIM}{step.message}{RESET}")
        if fail_at is None and step.status in ("BLOCKED", "ERROR", "ASSERT_FAIL"):
            fail_at = i

    outcome = f"{GREEN}SUCCESS{RESET}" if result.is_success() else f"{RED}FAILED{RESET}"
    print(f"\n  Total Δξ_CP: {result.cost:+.3f} nat  |  Steps: {len(result.log)}  |  {outcome}")

    if result.is_success():
        name = getattr(result.value, "name", str(result.value))
        print(f"  Result: {CYAN}{name}{RESET}")

    # Serialize and display the machine-readable result
    data = result.to_dict()
    data["script"] = "05_ensemble_design.syn"
    data["start"] = script.start_name
    json_str = json.dumps(data, indent=2)
    Path(tmp.name).write_text(json_str, encoding="utf-8")
    print(f"\n  {DIM}Saved JSON (ensemble_result.json preview):{RESET}")
    preview = json_str if len(json_str) <= 800 else json_str[:800] + "\n  ..."
    for line in preview.splitlines():
        print(f"  {DIM}{line}{RESET}")
    os.unlink(tmp.name)
    print()


def demo6_dry_run() -> None:
    header(
        "Demo 6 — Dry-Run Validation",
        "Parse and type-check a script without executing any chemistry"
    )
    narrate(
        "imscribe run --dry-run parses the .syn script and validates that the "
        "start imscription exists in the catalog, without running any operations. "
        "This is useful for CI pipelines, script linting, and rapid iteration "
        "on design programs before committing to a full probe run."
    )
    for fname in ["01_certify_soai.syn", "03_reusable_strategy.syn",
                  "05_ensemble_design.syn"]:
        script = SynScript.from_file(DEMO_DIR / fname)
        warnings = script.validate()
        do_steps = script._raw.get("do") or []
        strategies = script._raw.get("strategies") or {}
        if warnings:
            status = f"{YELLOW}WARN{RESET}: {'; '.join(warnings)}"
        else:
            status = f"{GREEN}OK{RESET}"
        print(
            f"  {DIM}--dry-run{RESET}  {CYAN}{fname:<38}{RESET}  "
            f"start={script.start_name!r}  "
            f"steps={len(do_steps)}  strategies={len(strategies)}  "
            f"→ {status}"
        )
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print()
    print(f"{BOLD}Imscribing Grammar v0.3.5 — Phase 3a Demo{RESET}")
    print(f"{DIM}Typed Design Programs for Matter: ImscriptionM monad + .syn DSL runner{RESET}")
    print()
    print(f"  {DIM}The .syn format compiles chemistry design goals into typed monadic{RESET}")
    print(f"  {DIM}pipelines.  Each step is a morphism in the Kleisli category of{RESET}")
    print(f"  {DIM}imscriptions.  Assertions are proof obligations.  Failure short-circuits.{RESET}")
    print(f"  {DIM}Every run produces a complete step trace + accumulated Δξ_CP cost.{RESET}")

    demo1_certification()
    demo2_type_gate()
    demo3_strategy_composition()
    demo4_fallback_search()
    demo5_ensemble_json()
    demo6_dry_run()

    bar = "═" * 68
    print(f"{BOLD}{bar}{RESET}")
    print(f"{BOLD}  Phase 3a complete{RESET}")
    print(f"  {DIM}monad.py · syn_runner.py · imscribe run  —  all operational{RESET}")
    print(f"\n  Next: Phase 3b — Pydantic v2 refinement types (illegal states")
    print(f"  unrepresentable by construction, not just runtime-rejected)")
    print(f"{BOLD}{bar}{RESET}\n")


if __name__ == "__main__":
    main()

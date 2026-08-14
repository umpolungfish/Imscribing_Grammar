"""
Expand a proof sketch into a full conventional proof (LaTeX) and
a Lean4 formalization skeleton, using the IG proof path.

Full proof  — second LLM call using the sketch as prior context.
Lean skeleton — deterministic from path steps; axioms mirror Hodge.lean structure.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from .graph import ProofStep, PRIMS

if TYPE_CHECKING:
    pass

# ── Op name → Lean4 tactic body ───────────────────────────────────────────────
# Each entry is the body of a `have` statement; caller wraps it.
_OP_TACTIC: dict[str, str] = {
    "apply_exponential_sequence": (
        "have h_exp_seq : ExactSequence (expSheafSequence X) := by\n"
        "  sorry\n"
        "  -- 0 → ℤ → 𝒪_X →^{exp(2πi·)} 𝒪_X* → 0 is exact (analytic topology);\n"
        "  -- MathlibGap: exponential sheaf sequence not in Mathlib."
    ),
    "resolve_to_proven": (
        "have h_lefschetz_11 : ∀ α : HodgeCohomology X 1, IsAlgebraicClass X 1 α := by\n"
        "  sorry\n"
        "  -- Lefschetz (1,1) theorem (1924): the connecting map δ : H¹(X,𝒪_X*) → H²(X,ℤ)\n"
        "  -- surjects onto H²(X,ℤ) ∩ H^{1,1}(X); kernel = im(δ) identified via\n"
        "  -- Dolbeault H²(X,𝒪_X) ≅ H^{0,2} and the (0,2)-projection.\n"
        "  -- MathlibGap: Dolbeault cohomology, Hodge decomposition not in Mathlib."
    ),
    "apply_hard_Lefschetz": (
        "have h_hard_lef : HardLefschetz X := by\n"
        "  sorry  -- MathlibGap: Hard Lefschetz theorem not in Mathlib."
    ),
    "apply_GAGA": (
        "have h_gaga : ∀ (F : CoherentSheaf X), AnalyticSections F = AlgebraicSections F := by\n"
        "  sorry  -- GAGA (Serre 1956): analytic and algebraic coherent sheaves coincide on projective X."
    ),
    "apply_cycle_class_map": (
        "have h_cc_surj : Function.Surjective (cycleClass X 1) := by\n"
        "  sorry  -- Follows from Lefschetz (1,1); general surjectivity is the Hodge conjecture."
    ),
    "dualize_via_poincare": (
        "have h_pd : PoincareDuality X := by\n"
        "  sorry  -- MathlibGap: Poincaré duality for smooth projective varieties."
    ),
    "restrict_hodge_degree": (
        "have h_deg_restrict : ∀ α : HodgeCohomology X 1, IsAlgebraicClass X 1 α := by\n"
        "  sorry  -- Restricting to p=1 is the Lefschetz (1,1) case."
    ),
    "apply_spectral_sequence": (
        "have h_ss : SpectralSequence (hodgeFiltration X) := by\n"
        "  sorry  -- Hodge-to-de Rham spectral sequence degenerates at E₁."
    ),
    "reduce_mod_p": (
        "have h_mod_p : ∀ (p : ℕ) [hp : Fact p.Prime], ReductionModP X p := by\n"
        "  sorry  -- Reduction to characteristic p; requires spreading-out."
    ),
    "apply_modularity": (
        "have h_mod : Modular X := by\n"
        "  sorry  -- Modularity theorem (Wiles 1995 for elliptic curves over ℚ)."
    ),
    "apply_resolution_of_singularities": (
        "have h_res : ∃ (X' : SmoothProjectiveVariety), Resolution X X' := by\n"
        "  sorry  -- Hironaka (1964): resolution of singularities in char 0."
    ),
    "quotient_by_group_action": (
        "have h_quot : IsQuotient X G := by\n"
        "  sorry  -- Quotient by finite group action; GIT construction."
    ),
    "localize_at_prime": (
        "have h_loc : LocalizedAt X p := by\n"
        "  sorry  -- Localization at prime p."
    ),
    "fiber_over_base": (
        "have h_fib : IsFibration X B := by\n"
        "  sorry  -- Fibration structure over base B."
    ),
    "generalize_to_mixed_hodge": (
        "have h_mhm : MixedHodgeStructure X := by\n"
        "  sorry  -- Deligne's mixed Hodge structure (1971)."
    ),
    "apply_Hodge_index_theorem": (
        "have h_hit : HodgeIndexTheorem X := by\n"
        "  sorry  -- Hodge index theorem: intersection form is negative definite on H^{1,1}."
    ),
}

# ── Primitive → fallback tactic (when op not in _OP_TACTIC) ──────────────────
_PRIM_TACTIC: dict[str, str] = {
    "⊢": "have h_dim : ComplexDim X = _ := by sorry",
    "⊣": "have h_top : TopologicallyComplete X := by sorry",
    "≻": "have h_rel : ∃ (Z : AlgebraicCycle X p), cycleClass X p Z = α := by sorry",
    "≺": "have h_sym : Symmetric (pairingForm X) := by sorry",
    "⋈": "have h_coh : CoherentSheaves X := by sorry",
    "⊤": "have h_kin : Equidistributed (flow X) := by sorry",
    "∈": "have h_scope : ∀ x ∈ domain X, property x := by sorry",
    "∋": "have h_exact : Exact (exponentialSequence X) := by sorry",
    "⊙": "have h_crit : CriticalityResolved X p := by sorry",
    "⊥": "have h_depth : TemporalDepthFinite X := by sorry",
    "⊞": "have h_uniq : UniqueWitness X p := by sorry",
    "◻": "have h_inv : TopologicalInvariant X = _ := by sorry",
}

# ── Domain → Mathlib imports ───────────────────────────────────────────────────
_DOMAIN_IMPORTS: dict[str, list[str]] = {
    "algebraic_geometry": [
        "Mathlib.AlgebraicGeometry.Scheme",
        "Mathlib.RingTheory.DedekindDomain.Ideal",
        "Mathlib.Analysis.Complex.Basic",
        "Mathlib.Tactic",
    ],
    "number_theory": [
        "Mathlib.NumberTheory.Primes",
        "Mathlib.Data.ZMod.Basic",
        "Mathlib.Tactic",
    ],
    "analysis": [
        "Mathlib.Analysis.NormedSpace.Basic",
        "Mathlib.MeasureTheory.Integral.Lebesgue",
        "Mathlib.Tactic",
    ],
    "topology": [
        "Mathlib.Topology.Basic",
        "Mathlib.Tactic",
    ],
}

_ALGEBRAIC_GEO_AXIOMS = """\
-- ── Axiomatized types (infrastructure not yet in Mathlib) ──────────────────
-- These mirror the axiom structure in Millennium/Hodge.lean.
-- They are standard mathematical objects; the sorry below is NOT about these
-- types being ill-defined — they exist in mathematics (Griffiths-Harris, Voisin).

axiom SmoothProjectiveVariety : Type
axiom complexDim : SmoothProjectiveVariety → ℕ
axiom HodgeCohomology (X : SmoothProjectiveVariety) (p : ℕ) : Type
axiom HodgeClass.zero (X : SmoothProjectiveVariety) (p : ℕ) : HodgeCohomology X p
axiom AlgebraicCycle (X : SmoothProjectiveVariety) (p : ℕ) : Type
axiom cycleClass (X : SmoothProjectiveVariety) (p : ℕ) :
    AlgebraicCycle X p → HodgeCohomology X p

-- Exponential sheaf sequence infrastructure
axiom ExactSequence {α : Type} (seq : α) : Prop
axiom expSheafSequence (X : SmoothProjectiveVariety) : Type

def IsAlgebraicClass (X : SmoothProjectiveVariety) (p : ℕ) (α : HodgeCohomology X p) : Prop :=
  ∃ (Z : AlgebraicCycle X p), cycleClass X p Z = α
"""


def _infer_domain(steps: list[ProofStep]) -> str:
    op_names = " ".join(s.op_name for s in steps)
    if any(k in op_names for k in (
        "hodge", "gaga", "lefschetz", "cycle_class", "exponential",
        "dolbeault", "poincare", "resolution",
    )):
        return "algebraic_geometry"
    if any(k in op_names for k in ("spectral", "sobolev", "bounded")):
        return "analysis"
    if any(k in op_names for k in ("modular", "reduce_mod_p", "localize")):
        return "number_theory"
    return "algebraic_geometry"


def _slug(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", name)


def _tactic_for_step(step: ProofStep) -> str:
    if step.op_name in _OP_TACTIC:
        return _OP_TACTIC[step.op_name]
    # Fallback: use the first changed primitive
    changed = list(step.changes.keys())
    if changed:
        prim = changed[0]
        return _PRIM_TACTIC.get(prim, f"have h_{_slug(step.op_name)} : True := trivial  -- {step.op_name}")
    return f"have h_{_slug(step.op_name)} : True := trivial"


def generate_lean_skeleton(
    steps: list[ProofStep],
    source_name: str,
    target_name: str,
) -> str:
    domain = _infer_domain(steps)
    imports = _DOMAIN_IMPORTS.get(domain, ["Mathlib.Tactic"])
    ns = f"ProofPath.{_slug(source_name)}_to_{_slug(target_name)}"

    lines: list[str] = [
        f"-- Auto-generated Lean4 skeleton",
        f"-- Path: {source_name} → {target_name}  ({len(steps)} step(s))",
        f"-- Domain: {domain}",
        f"-- Every `sorry` is an honest marker: either a Mathlib gap or an open problem.",
        "",
    ]
    lines += [f"import {imp}" for imp in imports]
    lines += ["", f"namespace {ns}", ""]

    if domain == "algebraic_geometry":
        lines += _ALGEBRAIC_GEO_AXIOMS.splitlines()
        lines.append("")

    # Main theorem
    lines += [
        f"/-! # Proof path: {source_name} → {target_name}",
        "",
        f"  Source: {source_name}",
        f"  Target: {target_name}",
        f"  Steps : {len(steps)}",
        "-/",
        "",
        f"theorem proof_path_theorem",
        f"    (X : SmoothProjectiveVariety) (p : ℕ)",
        f"    (α : HodgeCohomology X p) :",
        f"    IsAlgebraicClass X p α := by",
    ]

    for i, step in enumerate(steps, 1):
        lines.append(f"  -- ── Step {i}: {step.op_name} ─────────────────────────────")
        lines.append(f"  --    {step.from_name} → {step.to_name}")
        for prim, (old, new) in step.changes.items():
            lines.append(f"  --    {prim}: {old} → {new}")
        tactic = _tactic_for_step(step)
        for tline in tactic.splitlines():
            lines.append(f"  {tline}")
        lines.append("")

    lines += ["  sorry  -- combine the above steps", "", f"end {ns}"]
    return "\n".join(lines)


# ── Full proof (LLM) ───────────────────────────────────────────────────────────

_SYSTEM_FULL = """\
You are a mathematical author writing a complete, self-contained proof for \
journal submission. You have been given a proof sketch; your task is to expand \
it into a full LaTeX document.

Requirements:
- Output valid LaTeX. Begin with \\documentclass[12pt]{article} and include a \
complete preamble (amsmath, amssymb, amsthm, geometry with 1in margins, hyperref).
- Define theorem, lemma, proposition, proof, remark, corollary environments.
- Structure: \\maketitle (title + date), \\begin{abstract}...\\end{abstract}, \
\\section{Introduction}, one \\section per proof step (each containing a \\begin{lemma} \
or \\begin{proposition} with its \\begin{proof}...\\end{proof}), \
\\section{Main Result} (\\begin{theorem} + \\begin{proof} combining the lemmas), \
\\section{Discussion and Open Problems}.
- Each step section should correspond exactly to one step in the proof sketch. \
State the lemma precisely, prove it fully using the most direct argument available.
- Do not truncate. Every proof environment must be closed.
- Be mathematically precise: name exact sequences, Hodge components, maps, \
and spaces explicitly. No vague appeals to "diagram chases" or "standard arguments".
- The discussion section must specify exactly which ingredient fails for the \
general case and why — not just that it "doesn't extend".\
"""


def generate_full_proof(
    steps: list[ProofStep],
    source_name: str,
    source_desc: str,
    target_name: str,
    target_desc: str,
    sketch: str,
    client,
    model: str,
) -> str:
    from .graph import PRIMS
    from .ops import OPERATIONS_BY_NAME

    step_summary = "\n".join(
        f"  Step {i}: {s.op_name} | "
        + ", ".join(f"{p}: {o}→{n}" for p, (o, n) in s.changes.items())
        for i, s in enumerate(steps, 1)
    )

    user_msg = f"""\
Expand the following proof sketch into a complete LaTeX document.

THEOREM BEING PROVED:
  Source conjecture/object: {source_name}
    {source_desc}
  Target theorem/object: {target_name}
    {target_desc}

PROOF STRUCTURE ({len(steps)} steps):
{step_summary}

PROOF SKETCH (to expand):
{sketch}

Produce the complete LaTeX document now. Begin with \\documentclass.\
"""

    from .translator import _stream_to_stdout
    response = client.chat.completions.create(
        model=model,
        stream=True,
        messages=[
            {"role": "system", "content": _SYSTEM_FULL},
            {"role": "user", "content": user_msg},
        ],
    )
    return _strip_code_fences(_stream_to_stdout(response))


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences that models sometimes wrap LaTeX output in."""
    text = text.strip()
    m = re.match(r"^```(?:latex|tex)?\s*\n(.*)\n```\s*$", text, re.DOTALL)
    return m.group(1).strip() if m else text


def compile_latex(tex_path: Path) -> Path:
    """Run lualatex twice on tex_path (in its directory) to resolve all refs.

    Returns the path to the produced PDF, or raises RuntimeError on failure.
    """
    tex_path = tex_path.resolve()
    engine = _find_latex_engine()
    cmd = [engine, "-interaction=nonstopmode", "-halt-on-error", tex_path.name]

    for pass_num in (1, 2):
        result = subprocess.run(
            cmd,
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Surface the last 30 lines of the log for diagnosis
            lines = (result.stdout + result.stderr).splitlines()
            tail = "\n".join(lines[-30:])
            raise RuntimeError(
                f"LaTeX pass {pass_num} failed (exit {result.returncode}):\n{tail}"
            )

    pdf = tex_path.with_suffix(".pdf")
    if not pdf.exists():
        raise RuntimeError(f"Compilation succeeded but PDF not found at {pdf}")
    return pdf


def _find_latex_engine() -> str:
    for engine in ("lualatex", "pdflatex", "xelatex"):
        result = subprocess.run(
            ["which", engine], capture_output=True, text=True
        )
        if result.returncode == 0:
            return engine
    raise RuntimeError(
        "No LaTeX engine found. Install lualatex (texlive-luatex) or pdflatex."
    )

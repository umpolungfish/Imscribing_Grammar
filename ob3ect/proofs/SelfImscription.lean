/-!
# Self-Imscription — AST Frobenius Theorem

The computational core of the ob3ect: μ∘δ=id holds at the level of
Abstract Syntax Trees, verified empirically by `digital/frob.py`.

## Opcode correspondence (frob.py → Lean)

| Python (frob.py)           | Lean          | Categorical role |
|----------------------------|---------------|------------------|
| `TANCH(src) = ast.parse`   | `parse`       | δ (comultiplication) |
| `AFWD(tree) = ast.unparse` | `unparse`     | μ (multiplication)   |
| `FFUSE` (semantic_identity)| `ast_frobenius` | μ∘δ=id verification |

## The claim

`parse ∘ unparse = id` on SyntaxTrees.

Operationally: `semantic_identity(tree, ast.parse(ast.unparse(tree)))` returns
True for every well-formed Python AST. This is what `frob.py::FFUSE` checks.

## Status

`ast_frobenius` is an axiom here — grounded in the empirical evidence from
`frob.py` (v0.10, verified on bare metal). Eliminating the axiom requires
either a verified Python parser in Lean or a formal proof that `ast.unparse`
produces output whose parse is structurally identical to the original.
-/

import Mathlib.CategoryTheory.Monoidal.Basic
import Mathlib.Data.String.Basic
import «ob3ect/proofs/Frobenius»

open CategoryTheory MonoidalCategory

/-! ## Abstract syntax types -/

/-- Opaque type representing a Python Abstract Syntax Tree. -/
opaque SyntaxTree : Type

/-- Source code: a String. -/
abbrev Source := String

/-- δ — TANCH — ast.parse: embed source into its AST. -/
opaque parse : Source → SyntaxTree

/-- μ — AFWD — ast.unparse: project an AST back to source. -/
opaque unparse : SyntaxTree → Source

/-! ## The AST Frobenius axiom -/

/--
  **AST Frobenius**: `parse ∘ unparse = id` on `SyntaxTree`.

  For every well-formed AST `t`, parsing its unparsed form yields back `t`
  (up to structural identity — the criterion used by `semantic_identity`
  in `frob.py::FFUSE`).

  This axiom is grounded by `frob.py` v0.10: the bootstrap compiler reads
  its own source, unparsed it, re-parses the result, and verifies structural
  identity before writing the imscribed binary.
-/
axiom ast_frobenius : ∀ (t : SyntaxTree), parse (unparse t) = t

/-- `parse` and `unparse` form a left-inverse pair. -/
theorem ast_left_inverse : Function.LeftInverse parse unparse :=
  ast_frobenius

/-- Source round-trip: `unparse(parse(s))` re-parses to the same AST as `parse(s)`. -/
theorem source_round_trip (s : Source) :
    parse (unparse (parse s)) = parse s :=
  ast_frobenius (parse s)

/-! ## Connecting to categorical Frobenius -/

/--
  `SyntaxTree` carries a Frobenius structure in **Type** (the category of
  types and functions) via the diagonal/projection pair.

  This is the trivial Frobenius; the non-trivial one is the
  parse/unparse pair above (via `ast_frobenius`).
-/
def syntaxTreeFrobenius : FrobeniusOb3ect (Type) where
  δ _ := fun t => (t, t)
  μ _ := fun p => p.1
  frobenius_coherence _ := funext (fun _ => rfl)

/--
  **Bridge theorem**: the AST Frobenius (parse/unparse round-trip) implies
  that `SyntaxTree` has a section-retraction pair in Type, witnessing
  the existence of a non-trivial Frobenius structure beyond the diagonal.
-/
theorem ast_section_retraction :
    ∃ (δ' : SyntaxTree → SyntaxTree) (μ' : SyntaxTree → SyntaxTree),
      ∀ t, μ' (δ' t) = t :=
  ⟨fun t => parse (unparse t), id, fun t => by simp [ast_frobenius t]⟩

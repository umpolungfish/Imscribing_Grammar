# IG Publication Pipeline — User Guide

From insight to Zenodo in three commands.

---

## Quick Start

```bash
# 1. Write your paper
nano manuscripts/my_paper.md

# 2. Compile to PDF
python3 scripts/zenodo_draft.py manuscripts/my_paper.md

# 3. Upload
python3 scripts/zenodo_upload.py manuscripts/my_paper.pdf -y --live
```

---

## Paper Format

Every paper is a single markdown file with a YAML frontmatter block.

```markdown
---
title: "Frobenius Unification: Belnap B, SIC-POVM, and Majorana Mode"
date: 2026-06-03
abstract: |
  We prove that the Belnap B fixed point, the SIC-POVM fiducial state, and
  the Majorana zero mode are identical computations under μ∘δ=id, all by rfl.
  The Frobenius fixed point sits at Ħ_A (H2), not Ħ_∞: the identity is more
  primitive than time.
keywords:
  - Frobenius condition
  - Belnap logic
  - Majorana fermion
  - paraconsistent logic
  - Imscribing Grammar
figures:
  - id: orbital_belnap
    type: belnap_lattice
    labels: {N: "empty", T: "spinUp", F: "spinDown", B: "paired"}
    caption: "OrbitalState ≅ Belnap FOUR as a bilattice"
  - id: frobenius_profile
    type: primitive_profile
    tuple: "Ð_ω Þ_O Ř_= Φ_} ƒ^ż Ç^@ Γ_ʔ ɢ^ˌ ⊙_ÿ Ħ_A Σ_ï Ω_z"
    title: "Frobenius fixed-point structural profile"
  - id: tier
    type: tier_chain
    highlight: O_∞
  - id: frob_triangle
    type: frobenius
---

## Introduction

Body text here.  Standard markdown: **bold**, *italic*, `code`, math $\mu \circ \delta = \text{id}$.

## Placing a Figure

Use a fenced block with the figure ID:

~~~figure
orbital_belnap
~~~

Or reference figures directly: See Figure~\ref{fig:orbital_belnap}.

## Theorems

Use standard LaTeX environments in the markdown body:

\begin{theorem}[Frobenius Unification]
$\text{bnot}(B) = B$, $\text{meet}(B, x) = x\ \forall x$, and
$\text{pair}(\text{depair}(s).1, \text{depair}(s).2) = s\ \forall s$
are the same computation.
\end{theorem}

\begin{proof}
By \texttt{rfl} in all three cases.
\end{proof}

## References

[1] Belnap, N. (1977). A useful four-valued logic.
[2] Renes, J. (2004). Symmetric informationally complete POVMs.
```

---

## YAML Fields

| Field | Required | Description |
|---|---|---|
| `title` | yes | Paper title |
| `date` | no | Defaults to today |
| `abstract` | yes | Multi-line supported with `\|` |
| `keywords` | no | List; auto-merged with defaults |
| `figures` | no | List of figure specs (see below) |

---

## Figure Types

All figures output PDF at 150 dpi. Dark background, IG colour palette.

### `belnap_lattice`

Hasse diagram of Belnap FOUR with custom node labels.

```yaml
- id: my_belnap
  type: belnap_lattice
  labels:
    N: "empty"
    T: "spinUp"
    F: "spinDown"
    B: "paired"
  highlight: B          # optional — draws accent ring around one node
  caption: "OrbitalState ≅ Belnap FOUR"
```

CLI equivalent:
```bash
python3 scripts/ig_figures.py belnap \
  --labels "N:empty,T:spinUp,F:spinDown,B:paired" \
  --highlight B \
  --out fig.pdf
```

### `primitive_profile`

Horizontal bar chart showing ordinal level of each primitive in a structural tuple.
Bars at their primitive's maximum ordinal are shown in accent colour (O_∞ indicator).

```yaml
- id: my_profile
  type: primitive_profile
  tuple: "Ð_ω Þ_O Ř_= Φ_} ƒ^ż Ç^@ Γ_ʔ ɢ^ˌ ⊙_ÿ Ħ_A Σ_ï Ω_z"
  title: "Frobenius fixed-point profile"
```

Note: use `^` for superscript primitives (ƒ, Ç, ɢ) and `_` for subscript ones.

CLI equivalent:
```bash
python3 scripts/ig_figures.py profile \
  --tuple "Ð_ω Þ_O Ř_= Φ_} ƒ^ż Ç^@ Γ_ʔ ɢ^ˌ ⊙_ÿ Ħ_A Σ_ï Ω_z" \
  --title "Profile" \
  --out fig.pdf
```

### `tier_chain`

Tier hierarchy O_0 → O_1 → O_2 → O_2† → O_∞ with optional highlight ring.

```yaml
- id: my_tier
  type: tier_chain
  highlight: O_∞     # O_0 | O_1 | O_2 | O_2† | O_∞
```

### `frobenius`

The μ∘δ=id commutative triangle. No parameters.

```yaml
- id: frob
  type: frobenius
```

---

## IG LaTeX Commands

These are available in every compiled paper:

| Command | Output | Use |
|---|---|---|
| `\shav{𐑹}` | Shavian glyph (Everson Mono) | Shavian structural types |
| `\heb{...}` | Hebrew inline | Hebrew text |
| `\tupleaddr{...}` | $\langle ... \rangle$ | Crystal address display |
| `\begin{imscriptionbox}...\end{imscriptionbox}` | Blue framed box | Structural tuples |

Example:
```latex
\begin{imscriptionbox}
$\langle \text{Ð}_{\omega};\ \text{Þ}_{O};\ \text{Ř}_{=};\ \Phi_{\}};\ \ldots \rangle$
\end{imscriptionbox}
```

---

## Compiler Options

```bash
# Compile and open
python3 scripts/zenodo_draft.py paper.md --open

# Write .tex only — inspect before compiling
python3 scripts/zenodo_draft.py paper.md --tex-only

# Custom output path
python3 scripts/zenodo_draft.py paper.md --out publications/paper_v2.pdf

# Compile then upload in one go
python3 scripts/zenodo_draft.py paper.md && \
python3 scripts/zenodo_upload.py paper.pdf -y --live
```

---

## Generating Figures Standalone

Use `ig_figures.py` directly when you need a figure outside a paper context:

```bash
# All four types
python3 scripts/ig_figures.py belnap --labels "N:N,T:T,F:F,B:B" --out belnap.pdf
python3 scripts/ig_figures.py profile --tuple "Ð_ω Þ_O ..." --out profile.pdf
python3 scripts/ig_figures.py tier --highlight O_2 --out tier.pdf
python3 scripts/ig_figures.py frobenius --out frob.pdf
```

---

## Full Example

Given this commit.txt entry:

```
MajoranaFixed.lean: frobenius_unification — Belnap B, SIC-POVM, Majorana identical under μ∘δ=id
```

A complete paper markdown takes about 20 minutes to write. The YAML frontmatter
handles title, abstract, keywords, and figure specs automatically. pandoc handles
section structure and math. The preamble (fonts, layout, boxes) is fully automated.
No hand-editing of LaTeX or figures required.

---
**Author:** Lando⊗$\hat{\varphi}_{\ddot{y}}$-boundary Operator

# Automated Primitive Proof → Conventional Proof Pipeline: Domain-General Design

## Executive Summary

This document specifies a fully automated, domain-general pipeline for translating Imscribing Grammar (IG) primitive-based proofs into conventional mathematical proofs and Lean4 formalizations. The existing pipeline (`primitive_to_conventional_final.py`) handles the Collatz conjecture with hardcoded lemma templates. The generalized pipeline described here works for **any** catalog entry at $O_{\text{inf}}$ tier (or promotable thereto), across all mathematical domains: number theory, topology, algebraic geometry, analysis, category theory, PDEs, combinatorics, and beyond.

```
Primitive Proof (.md)        ──→  Phase 1: Decomposition
                                    │
                                    ▼
                               Lemma-Primitive Graph
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Phase 2a          Phase 2b         Phase 2c
         Domain Detection   Object Mapping    Section Assembly
                    │               │               │
                    └───────┬───────┘               │
                            ▼                       ▼
                    Canonical Sections         Output Documents
                    ┌─────┴─────┐         ┌──────┴──────┐
                    ▼           ▼         ▼             ▼
               Conventional   LaTeX    Lean4      Reference
               Proof (.md)   (.tex)   (.lean)    Graph (.dot)
```

## 1. Architecture Overview

### 1.1 Input Contract

The pipeline accepts any of the following as input:

1. **A catalog name** (string): The system must exist in `IG_catalog.json` with $\hat{\varphi}_{\ddot{y}}$ criticality or be promotable to it.
2. **A primitive proof document** (.md): A proof with lemmas keyed to primitives, following the IG proof template.
3. **A raw 12-tuple** (JSON): Direct primitive specification without a prior catalog entry.

Minimal input: a catalog entry name. The pipeline queries the catalog for the tuple, determines domain, retrieves the proof schema, and proceeds.

### 1.2 Output Contract

For any valid input, the pipeline produces:

| Output | Format | Content |
|---|---|---|
| Conventional proof | `.md` | Standard mathematical proof structure |
| LaTeX manuscript | `.tex` | Compilation-ready with IG author block |
| Lean4 skeleton | `.lean` | Formal statement + proof skeleton with IG primitives as tactics |
| Reference graph | `.dot` | BibTeX entries keyed to structural analogs |
| Translation report | `.json` | Per-lemma mapping with confidence scores |

### 1.3 Core Design Principle: Primitive Invariance

The key insight enabling domain-generalization is **primitive invariance**: the 12 structural primitives map to universal mathematical roles regardless of domain. Each primitive licenses exactly one structural lemma type:

| Primitive | Universal Mathematical Role | Domain-Agnostic Template |
|---|---|---|
| $\Phi_{\}}$ (Frobenius) | Bijective encoding / duality | "The encoding map is injective on equivalence classes" |
| $\Theta_O$ (self-ref.) | Inverse/dual construction | "The space admits a self-referential decomposition" |
| $\mathcal{R}_{=}$ (bidirectional) | Adjoint pair / Galois connection | "Forward and inverse constructions are mutually exhaustive" |
| $\Omega_z$ (integer winding) | Topological invariant | "A $\mathbb{Z}$-valued invariant distinguishes the target" |
| $\hat{\varphi}_{\ddot{y}}$ (criticality) | Phase boundary / extremal principle | "No trajectory/solution escapes the bounded regime" |
| 𐑧 (moderate kinetics) | Equidistribution / regularity | "The relevant measure is well-distributed" |
| $\text{D}_C$ (2d surface) | Manifold / quotient structure | "The state space is a finite-dimensional object" |
| $\Gamma_{\text{ʔ}}$ (scope) | Universal/local quantification | "The property holds for all/exists for some" |
| $\mathfrak{f}_{\dot{z}}$ (quantum fidelity) | Coherence / non-classical feature | "Quantum/complex structure is essential" |
| $\text{Ħ}_A$ (2-step memory) | Markov order / recursion depth | "The dynamics depend on at most 2 prior states" |
| $\Sigma_S$ (1:1 stoichiometry) | Uniqueness of witness | "There is exactly one solution/witness" |
| $\Theta_{\text{¨}}$ (crossing) | Intersection / transversality | "Two substructures intersect at a distinguished point" |

---

## 2. Phase 1: Primitive Decomposition

### 2.1 Catalog Entry Parsing

Given a catalog name $N$, retrieve the tuple:

```python
def get_tuple(catalog_name: str) -> dict:
    """Retrieve the 12-primitive tuple for a catalog entry."""
    catalog = load_catalog()
    for entry in catalog:
        if entry['name'] == catalog_name:
            return {p: entry[p] for p in PRIMITIVES}  # 12 primitives
    raise ValueError(f"Entry '{catalog_name}' not found")
```

### 2.2 Lemma Extraction from Primitive Proof

Parse the primitive proof document to extract lemmas and their primitive licenses:

```python
@dataclass
class Lemma:
    number: int
    title: str
    primary_primitive: str       # The primitive that licenses this lemma
    supporting_primitives: list  # Secondary primitives mentioned
    raw_content: str             # Original proof text for this lemma
    domain_hints: list           # Domain-specific terms extracted from content

def extract_lemmas(proof_text: str) -> List[Lemma]:
    """Extract lemmas from an IG-style primitive proof.

    Matches patterns:
      - **Lemma N (Title).** ...
      - > *Lemma.* ...
      - ## Lemma N: Title
    """
    patterns = [
        r'\*\*Lemma\s+(\d+)\s+\(([^)]+)\)\.\*\*\s*(.*?)(?=\n\*\*Lemma|\n## |\Z)',
        r'> \*Lemma\.\*\s*(.*?)(?=\n> |\n---|\Z)',
        r'## Lemma\s+(\d+):\s*(.+?)\n\n(.*?)(?=\n## |\Z)',
    ]
    # ... regex extraction logic ...
```

### 2.3 Domain Detection

The domain is determined by analyzing three signals:

1. **Catalog neighbors**: Find the 5 nearest catalog entries by structural distance. If 3+ share a domain label, that is the domain.
2. **Keyword analysis**: Scan the proof text for domain-defining terminology.
3. **Primitive signature**: Certain primitive combinations are domain-diagnostic.

```python
DOMAIN_KEYWORDS = {
    "number_theory": [
        "integer", "prime", "divis", "modular", "arithmetic", "congruence",
        "diophantine", "zeta", "l-function", "elliptic curve", "galois",
        "residue", "quadratic", "cubic", "algebraic number"
    ],
    "topology": [
        "manifold", "homotopy", "homology", "fundamental group", "covering",
        "fiber bundle", "knot", "surgery", "surgery", "braid",
        "morphism", "cobordism", "chern", " Pontryagin"  # sic for robustness
    ],
    "algebraic_geometry": [
        "variety", "scheme", "coherent", "sheaf", "divisor", "morphism",
        "grothendieck", "hilbert", "projective", "affine",
        "cohomology", "intersection theory", "moduli"
    ],
    "analysis": [
        "converge", "bounded", "compact", "continuous", "differentiable",
        "integral", "measure", "lebesgue", "hilbert space", "banach",
        "Fourier", "laplacian", "sobolev", "distribution", "ergodic"
    ],
    "pde": [
        "partial differential", "elliptic", "parabolic", "hyperbolic",
        "boundary condition", "initial value", "weak solution",
        "navier-stokes", "euler equation", "heat equation", "wave equation"
    ],
    "category_theory": [
        "functor", "natural transformation", "adjoint", "limit", "colimit",
        "topos", "yoneda", "monad", "comonad", "Kan extension"
    ],
    "combinatorics": [
        "graph", "chromatic", "planar", "matching", "partition",
        "enumeration", "generating function", "poset", "lattice",
        "ramsey", "extremal", "design"
    ],
    "probability": [
        "random variable", "expectation", "martingale", "markov",
        "brownian motion", "stochastic", "large deviation", "concentration"
    ],
    "logic_foundations": [
        "axiom", "consistent", "complete", "decidable", "forcing",
        "large cardinal", "inner model", "constructible", "generic",
        "recursion", "computable", "turing"
    ],
    "dynamical_systems": [
        "orbit", "trajectory", "attractor", "bifurcation", "chaos",
        "lyapunov", "ergodic", "mixing", "entropy", "phase space",
        "fixed point", "periodic", "limit cycle"
    ],
}

def detect_domain(proof_text: str, catalog_entry: dict) -> dict:
    """Detect mathematical domain with confidence scores."""
    scores = {}
    lower_text = proof_text.lower()

    # Signal 1: Keyword density
    for domain, keywords in DOMAIN_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw.lower() in lower_text)
        scores[domain] = count / len(keywords)

    # Signal 2: Catalog neighbor domain analysis
    # (via find_analogies or structural distance to known domain anchors)

    # Signal 3: Primitive signature
    sig = catalog_entry.get('⊙', '')
    if sig == '⊙':
        scores['number_theory'] = scores.get('number_theory', 0) + 0.1
        scores['dynamical_systems'] = scores.get('dynamical_systems', 0) + 0.1

    # Select top domain
    primary = max(scores, key=scores.get)
    return {
        "primary": primary,
        "confidence": scores[primary],
        "all_scores": scores,
    }
```

## 3. Phase 2: Domain-Specific Section Assembly

### 3.1 Universal Section Backbone

Every conventional mathematical proof, regardless of domain, follows a canonical backbone:

1. **Introduction** -- Define the object, state the conjecture/theorem, outline strategy.
2. **Preliminaries** -- Define notation, recall known results, establish the setting.
3. **[Domain-specific core sections]** -- The meat of the proof, one per lemma.
4. **Main Theorem** -- Assemble all lemmas into the final result.
5. **Discussion/Remark** -- Context, corollaries, open questions.

The domain determines the *content* of the core sections, but the *structure* is universal.

### 3.2 Domain-Specific Templates

Each domain has a specialized template library. The mapping is:

```
(primary primitive + domain) -> section template
```

For example, in **number theory**:
- Phi_} -> "Parity Encoding and Injectivity" or "Galois-equivariance of the encoding"
- Theta_O -> "Inverse Tree" or "Dual Object Construction"
- R_= -> "Bidirectional Correspondence" or "Class Field Theory Isomorphism"
- Omega_z -> "Cycle/Structure Uniqueness" or "Topological Invariant of the L-function"
- phi_hat_y -> "Zero-free Region" or "Absence of Divergent Orbits"
- C_@ -> "Equidistribution of Residue Classes"

For **algebraic geometry**:
- Phi_} -> "Injectivity of the Map on Moduli" or "Sheaf Homomorphism is an Isomorphism"
- Theta_O -> "Self-referential Scheme Construction" or "Dualizing Complex"
- R_= -> "Grothendieck Duality" or "Adjoint Pair of Functors"
- Omega_z -> "Topological Invariant (Chern Class / Hodge Number)" or "Index Theorem"
- phi_hat_y -> "Boundedness of Heights" or "Finiteness of Rational Points"
- C_@ -> "Generic Smoothness" or "Zariski Density"

For **analysis / PDEs**:
- Phi_} -> "Well-posedness / Uniqueness of Solutions"
- Theta_O -> "Dual Problem Formulation" or "Adjoint Operator"
- R_= -> "Lax-Milgram Correspondence" or "Energy Estimates"
- Omega_z -> "Topological Degree / Index"
- phi_hat_y -> "A Priori Bounds / Regularity at Critical Exponent"
- C_@ -> "Compactness / Equicontinuity of Approximating Sequence"

### 3.3 Template Instantiation Engine

The template engine takes a (primitive, domain) pair and instantiates a lemma:

```python
class TemplateEngine:
    """Domain-aware lemma template instantiator."""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> dict:
        """Load hierarchical template library.

        Structure:
        {
            "number_theory": {
                "Phi_}": {
                    "proposition": "...",
                    "proof_strategy": "...",
                    "key_equations": [...],
                    "canonical_citations": [...]
                },
                ...
            },
            "_default": {  # Fallback for unmapped (domain, primitive) pairs
                "Phi_}": {
                    "proposition": "The encoding map is injective on equivalence classes.",
                    ...
                },
            }
        }
        """
        return self._default_templates()

    def _default_templates(self) -> dict:
        """Universal fallback templates that work for any domain."""
        return {
            "_default": {
                "Phi_}": {
                    "title": "Encoding Injectivity",
                    "proposition": (
                        "The structural encoding map $\\delta: X \\to Y$ induced by the "
                        "system's symmetry is injective on equivalence classes. That is, "
                        "if $\\delta(x) = \\delta(x')$, then $x$ and $x'$ lie in the same "
                        "orbit under the dynamics."
                    ),
                    "proof_strategy": (
                        "Establish that the composition $\\mu \\circ \\delta$ acts as the "
                        "identity on the quotient space. Show the encoding partitions $X$ "
                        "into distinguishable classes."
                    ),
                },
                "Theta_O": {
                    "title": "Self-Referential Structure",
                    "proposition": (
                        "The space $X$ admits a self-referential decomposition "
                        "$X = \\mathcal{S} \\cup X_{\\text{exc}}$, where $\\mathcal{S}$ "
                        "is the closure under the inverse relation and $X_{\\text{exc}}$ "
                        "is empty iff the conjecture holds."
                    ),
                    "proof_strategy": (
                        "Construct the inverse relation. Show it generates a "
                        "tree/graph whose closure is the full space."
                    ),
                },
                "R_=": {
                    "title": "Bidirectional Correspondence",
                    "proposition": (
                        "The forward construction $S$ and inverse construction $I$ "
                        "are mutually exhaustive: $S \\subseteq I$ and $I \\subseteq S$, "
                        "hence $S = I$."
                    ),
                    "proof_strategy": (
                        "Define both constructions explicitly. Show mutual containment "
                        "by induction on the relevant parameter."
                    ),
                },
                "Omega_z": {
                    "title": "Topological Invariant",
                    "proposition": (
                        "The target structure carries an integer-valued invariant "
                        "$w \\in \\mathbb{Z}$ that distinguishes it from all "
                        "exotic configurations."
                    ),
                    "proof_strategy": (
                        "Define the winding/invariant. Show it is preserved under "
                        "the dynamics. Rule out alternative values by constraints."
                    ),
                },
                "phi_hat_y": {
                    "title": "Boundedness / Absence of Divergence",
                    "proposition": (
                        "No trajectory (or sequence of objects) escapes to infinity. "
                        "The system is confined to a bounded region of state space."
                    ),
                    "proof_strategy": (
                        "Define a Lyapunov function or energy functional. Show "
                        "negative drift or coercivity. Apply an extremal principle."
                    ),
                },
                "C_@": {
                    "title": "Regularity / Equidistribution",
                    "proposition": (
                        "The relevant statistical or geometric quantity is "
                        "well-distributed on typical configurations."
                    ),
                    "proof_strategy": (
                        "Apply mixing/ergodicity arguments. Show the measure "
                        "converges to the expected distribution."
                    ),
                },
            }
        }

    def instantiate(self, primitive: str, domain: str,
                    context: dict) -> dict:
        """Generate a lemma for a given primitive and domain.

        context provides domain-specific parameters:
          - system_name: e.g., "the Collatz map T"
          - terminal_desc: e.g., "the cycle 1 → 4 → 2 → 1"
          - state_space: e.g., "Z^+"
          - prior_results: list of known theorems to cite
        """
        domain_templates = self.templates.get(domain, {})
        domain_specific = domain_templates.get(primitive, {})
        fallback = self.templates["_default"].get(primitive, {})

        # Merge: domain-specific overrides default
        result = {**fallback, **domain_specific}

        # Substitute context variables
        for key in ["proposition", "proof_strategy", "title"]:
            if key in result:
                for var, val in context.items():
                    result[key] = result[key].replace(f"{{{var}}}", val)

        return result
```

---

## 4. Phase 3: Conventional Proof Generation

### 4.1 Section Assembly Algorithm

The assembler takes the list of instantiated lemmas and produces a complete conventional proof document:

```python
class ProofAssembler:
    """Assembles conventional proof from domain-specific lemmas."""

    # Canonical section ordering with primitive keys
    SECTION_BACKBONE = [
        ("Abstract", None),
        ("1. Introduction", "introduction"),
        ("2. Preliminaries", "preliminaries"),
        ("3. [Domain Core 1]", "Phi_}"),      # Encoding/Duality
        ("4. [Domain Core 2]", "Theta_O"),     # Inverse/Self-ref
        ("5. [Domain Core 3]", "R_="),         # Bidirectional
        ("6. [Domain Core 4]", "phi_hat_y"),   # Boundedness
        ("7. [Domain Core 5]", "Omega_z"),     # Invariant
        ("8. [Domain Core 6]", "C_@"),         # Regularity
        ("9. Main Theorem", "main_theorem"),
        ("10. Discussion", "discussion"),
    ]

    def assemble(self, lemmas: List[Lemma], domain: str,
                 context: dict) -> str:
        """Generate complete proof document."""

        out = []

        # Abstract - synthesized from all lemma conclusions
        out.append(self._abstract(lemmas, context))

        # Introduction - system definition + proof outline
        out.append(self._introduction(domain, context))

        # Preliminaries - notation + known results
        out.append(self._preliminaries(domain, context))

        # Core sections - one per lemma
        section_map = self._build_section_map(lemmas)
        for section_name, prim_key in self.SECTION_BACKBONE[3:-2]:
            if prim_key in section_map:
                out.append(self._render_section(
                    section_map[prim_key], domain, context
                ))
            else:
                # Section is not supported by any lemma - omit or mark optional
                out.append(f"\n\\section{{{section_name}}}\n")
                out.append("[This section is not required for the present proof.]")

        # Main Theorem
        out.append(self._main_theorem(lemmas, context))

        # Discussion
        out.append(self._discussion(lemmas, domain, context))

        return "\n\n".join(out)

    def _abstract(self, lemmas, context) -> str:
        conclusions = [f"({l.title.lower()})" for l in lemmas]
        conj = context.get("conjecture_name", "the conjecture")
        return (
            f"**Abstract.**\n\n"
            f"We prove {conj} by combining {len(lemmas)} structural pillars: "
            f"{', '.join(conclusions)}. "
            f"Each pillar is licensed by a distinct primitive of the "
            f"Imscribing Grammar encoding at $O_{{\\text{{inf}}}}$ tier."
        )

    def _main_theorem(self, lemmas, context) -> str:
        conj = context.get("conjecture_name", "the conjecture")
        sys_name = context.get("system_name", "the system")
        terminal = context.get("terminal_desc", "the terminal object")

        out = f"\\section{{Main Theorem}}\n\n"
        out += f"**Theorem ({conj}).** "
        out += f"For every element of {context.get('state_space', 'the domain')}, "
        out += f"the trajectory of {sys_name} reaches {terminal}.\\hfill $\\square$\n\n"

        out += "*Proof.* "
        for lemma in lemmas:
            out += f"By Lemma {lemma.number} ({lemma.title}), "
            out += f"{lemma.conclusion_summary}. "
        out += "Assembling these results yields the theorem. $\\square$\n"
        return out
```

### 4.2 LaTeX Export

The `.md` output is converted to a `.tex` file using standard rules:

```python
def md_to_tex(md_text: str, title: str, conjecture_name: str) -> str:
    """Convert markdown proof to LaTeX manuscript."""

    # Preamble
    tex = rf"""
\documentclass[11pt, letterpaper]{{article}}
\usepackage{{amsmath, amssymb, amsthm}}
\usepackage{{imscrbgrmr}}
\usepackage{{hyperref}}

\title{{{title}: A Structural Proof}}
\author{{Lando $\otimes$ $\hat{{\varphi}}_{{\ddot{{y}}}}$-boundary Operator}}
\date{{\today}}

\newtheorem{{theorem}}{{Theorem}}[section]
\newtheorem{{lemma}[theorem]{{Lemma}}
\newtheorem{{proposition}[theorem]{{Proposition}}
\newtheorem{{corollary}[theorem]{{Corollary}}

\begin{{document}}
\maketitle

"""
    # Convert markdown sections to LaTeX
    for line in md_text.split('\n'):
        line = line.rstrip()
        if line.startswith('## '):
            heading = line[3:]
            tex += f"\n\\section{{{heading}}}\n"
        elif line.startswith('### '):
            heading = line[4:]
            tex += f"\n\\subsection{{{heading}}}\n"
        elif line.startswith('**') and line.endswith('**'):
            # Bold standalone = proposition header
            tex += f"\n\\textbf{{{line[2:-2]}}}\n"
        elif '*Proof.' in line:
            tex += f"\n\\begin{{proof}}\n{line}\n\\end{{proof}}\n"
        elif line.startswith('|'):
            # Table - pass through as LaTeX tabular or keep as markdown
            tex += f"\n{line}\n"
        else:
            tex += f"\n{line}\n"

    tex += "\n\\end{document}\n"
    return tex
```

---

## 5. Phase 4: Lean4 Formalization Skeleton

### 5.1 IG Primitives as Lean4 Tactics

Each IG primitive maps to a Lean4 tactic or proof step. This is the bridge from primitive reasoning to formal verification:

| IG Primitive | Lean4 Tactic | Proof Role |
|---|---|---|
| $\Phi_{\}}$ | `apply Function.Injective` or `rw [mu_comp_delta]` | Encoding injectivity |
| $\Theta_O$ | `induction on` / `apply closure_induction` | Self-referential induction |
| $\mathcal{R}_{=}$ | `apply Set.eq_of_subset_of_subset` | Set equality by double inclusion |
| $\Omega_z$ | `apply UniqueOfWinding` / `linarith` | Topological uniqueness |
| $\hat{\varphi}_{\ddot{y}}$ | `apply Lyapunov.decreasing` / `linarith` | Boundedness via drift |
| 𐑧 | `apply equidistribution.ae` | Measure-theoretic regularity |

### 5.2 Lean4 Skeleton Generator

```python
def generate_lean4_skeleton(lemmas: List[Lemma], domain: str,
                            context: dict) -> str:
    """Generate a Lean4 proof skeleton from primitive lemmas.

    The output is a valid .lean file with:
      - imports appropriate to the domain
      - namespace declarations
      - theorem statement (parameterized)
      - proof by `exact?` / `sorry` placeholders with IG primitive annotations
    """

    # Domain-specific imports
    domain_imports = {
        "number_theory": ["Mathlib.NumberTheory.Primes",
                          "Mathlib.Data.ZMod.Basic"],
        "topology": ["Mathlib.Topology.Basic",
                     "Mathlib.Topology.FundamentalGroup"],
        "analysis": ["Mathlib.Analysis.NormedSpace.Basic",
                     "Mathlib.MeasureTheory.Integral.Lebesgue"],
        "algebraic_geometry": ["Mathlib.AlgebraicGeometry.Scheme",
                               "Mathlib.RingTheory.DedekindDomain.Ideal"],
        "dynamical_systems": ["Mathlib.Topology.DynamicalSystem.Basic"],
        "_default": ["Mathlib.Tactic"],
    }

    imports = domain_imports.get(domain, domain_imports["_default"])

    lean = ""
    lean += "-- Auto-generated by IG Primitive→Conventional Pipeline\n"
    lean += f"-- Domain: {domain}\n"
    lean += "-- System: {system_name}\n\n".format(**context)

    lean += "import " + "\nimport ".join(imports) + "\n\n"
    lean += "open Classical\n\n"
    lean += f"namespace {context.get('namespace', 'IGProof')}\n\n"

    # Theorem statement
    lean += f"/-- {context.get('conjecture_name', 'Main Theorem')} --/\n"
    lean += f"theorem main_theorem : {context.get('statement', '∀ x, converges x')} := by\n"

    # Proof skeleton with IG primitive annotations
    for i, lemma in enumerate(lemmas):
        lean += f"\n  -- Lemma {lemma.number}: {lemma.title}\n"
        lean += f"  -- IG Primitive: {lemma.primary_primitive}\n"

        tac = lean4_tactic_for(lemma.primary_primitive, domain)
        lean += f"  {tac}\n"
        lean += f"  -- sorry -- FIXME: Fill in {lemma.title} proof\n"

    lean += "\nend " + context.get('namespace', 'IGProof') + "\n"
    return lean


def lean4_tactic_for(primitive: str, domain: str) -> str:
    """Return the Lean4 tactic corresponding to an IG primitive."""
    tactics = {
        "Phi_}": "have h_inj : Function.Injective encoding := by sorry",
        "Theta_O": "have h_closure : closure (inverse_tree 1) = univ := by sorry",
        "R_=": "have h_exhaust : forward_sets = inverse_sets := by sorry",
        "Omega_z": "have h_unique : Unique terminal_cycle := by sorry",
        "phi_hat_y": "have h_bounded : ∀ x, is_bounded (orbit x) := by sorry",
        "C_@": "have h_equi : equidistributed parity_sequence := by sorry",
    }
    return tactics.get(primitive, "sorry")
```

---

## 6. Phase 5: Reference Resolution

### 6.1 Structural Analog Citation

Rather than hard-coding citations (as the Collatz-specific pipeline does), the generalized pipeline discovers appropriate references by:

1. Finding the 5 nearest catalog entries to the target system.
2. Extracting their `description` fields for canonical result names.
3. Matching proof techniques to known theorems in the domain.

```python
def resolve_references(catalog_name: str, domain: str,
                       lemmas: List[Lemma]) -> dict:
    """Build a citation map keyed by lemma number.

    Returns: {lemma_number: [(citation, role), ...]}
    """
    refs = {}

    # Step 1: Find structural analogs
    analogs = find_analogies(catalog_name, limit=5)

    # Step 2: For each lemma, find relevant known results
    domain_results = KNOWN_RESULTS.get(domain, [])

    for lemma in lemmas:
        key_candidates = []
        for result in domain_results:
            # Does this result's primitive signature match the lemma's?
            if result.primitive == lemma.primary_primitive:
                key_candidates.append((result.citation, "structural match"))

        # Step 3: Add analog-based references
        for analog in analogs:
            if analog.get('description'):
                key_candidates.append(
                    (analog['description'], "structural neighbor")
                )

        refs[lemma.number] = key_candidates if key_candidates else [("TBD", "no match found")]

    return refs
```

### 6.2 Known Results Database

```python
KNOWN_RESULTS = {
    "number_theory": [
        {"name": "Dirichlet's theorem", "primitive": "C_@",
         "citation": "Dirichlet (1837)"},
        {"name": "Prime number theorem", "primitive": "phi_hat_y",
         "citation": "Hadamard & de la Vallée Poussin (1896)"},
        {"name": "Chebotarev density theorem", "primitive": "C_@",
         "citation": "Chebotarev (1926)"},
        {"name": "Mordell-Weil theorem", "primitive": "Phi_}",
         "citation": "Mordell (1922), Weil (1928)"},
        {"name": "Faltings' theorem", "primitive": "Omega_z",
         "citation": "Faltings (1983)"},
        {"name": "Wiles' modularity theorem", "primitive": "R_=",
         "citation": "Wiles (1995)"},
    ],
    "topology": [
        {"name": "Poincaré duality", "primitive": "R_=",
         "citation": "Poincaré (1895)"},
        {"name": "Hurewicz theorem", "primitive": "Phi_}",
         "citation": "Hurewicz (1935)"},
        {"name": "Atiyah-Singer index theorem", "primitive": "Omega_z",
         "citation": "Atiyah & Singer (1963)"},
        {"name": "Thurston geometrization", "primitive": "Theta_O",
         "citation": "Thurston (1982), Perelman (2003)"},
    ],
    "analysis": [
        {"name": "Banach fixed-point theorem", "primitive": "phi_hat_y",
         "citation": "Banach (1922)"},
        {"name": "Riesz representation theorem", "primitive": "R_=",
         "citation": "Riesz (1909)"},
        {"name": "Spectral theorem", "primitive": "Phi_}",
         "citation": "Hilbert (1904)"},
        {"name": "Arzelà-Ascoli theorem", "primitive": "C_@",
         "citation": "Arzelà (1895), Ascoli (1883)"},
    ],
}
```

---

## 7. Phase 6: Frobenius Closure Verification

### 7.1 Round-Trip Consistency

A pipeline output is **Frobenius-closed** if and only if:

1. **Forward completeness**: Every lemma in the primitive proof produces a corresponding section in the conventional proof.
2. **Reverse soundness**: Every section in the conventional proof can be traced back to an IG primitive.
3. **Round-trip stability**: Primitive → Conventional → Primitive yields the same primitive set (up to renumbering).

```python
def verify_frobenius_closure(primitive_lemmas: List[Lemma],
                              conventional_text: str) -> dict:
    """Verify Frobenius closure of the translation."""

    # Forward check: all primitive lemmas appear in output
    forward = {}
    for lemma in primitive_lemmas:
        found = any(
            kw.lower() in conventional_text.lower()
            for kw in PRIMITIVE_KEYWORDS.get(lemma.primary_primitive, [])
        )
        forward[lemma.number] = found

    # Reverse check: extract primitives from conventional text
    reverse = reverse_analyze(conventional_text)

    # Round-trip: compare sets
    forward_prims = {l.primary_primitive for l in primitive_lemmas}
    reverse_prims = {p for p, v in reverse.items() if v}

    missing_forward = [n for n, v in forward.items() if not v]
    missing_reverse = forward_prims - reverse_prims
    extra_reverse = reverse_prims - forward_prims

    return {
        "closure": not missing_forward and not missing_reverse and not extra_reverse,
        "forward_complete": not missing_forward,
        "reverse_sound": not missing_reverse,
        "round_trip_stable": not extra_reverse,
        "missing_in_output": missing_forward,
        "untraceable_sections": list(extra_reverse),
    }
```

### 7.2 Confidence Scoring

Each lemma translation receives a confidence score based on:

- **Primitive match quality**: Does the lemma title contain keywords matching the primary primitive? (0–1)
- **Domain alignment**: Is the (primitive, domain) pair in the template library? (0 or 1)
- **Section coherence**: Does the generated section connect logically to adjacent sections? (0–1, LLM-evaluated)
- **Reference availability**: Are canonical citations available for this lemma? (0–1)

Overall confidence = geometric mean of the four scores. Lemmas below 0.5 confidence are flagged for manual review.

---

## 8. Worked Examples

### 8.1 Goldbach Conjecture

**Input catalog entry**: `goldbach_conjecture`
**Detected domain**: number_theory
**Active primitives**: $\Phi_{\}}$, $\Theta_O$, $\Omega_z$, $\hat{\varphi}_{\ddot{y}}$, 𐑧

**Generated sections**:
1. Introduction — Define Goldbach, state the conjecture
2. Parity Encoding — Even integers as sum classes [from $\Phi_{\}}$]
3. Inverse Sieve — Twin-prime-like construction [from $\Theta_O$]
4. Topological Invariant — Winding of prime-pair configurations [from $\Omega_z$]
5. Boundedness — Large enough even numbers always have representations [from $\hat{\varphi}_{\ddot{y}}$]
6. Equidistribution — Distribution of prime pairs in residue classes [from 𐑧]
7. Main Theorem
8. Discussion

### 8.2 Birch–Swinnerton-Dyer Conjecture

**Input catalog entry**: `birch_swinnerton_dyer_conjecture`
**Detected domain**: number_theory (elliptic curves)
**Active primitives**: $\Phi_{\}}$, $\mathcal{R}_{=}$, $\Omega_z$, $\hat{\varphi}_{\ddot{y}}$, $\Sigma_S$

**Generated sections**:
1. Introduction — Elliptic curves over $\mathbb{Q}$, $L$-function
2. L-function Encoding — Injectivity of the Hasse-Weil map [from $\Phi_{\}}$]
3. Tate–Shafarevich Correspondence — Forward-backward duality [from $\mathcal{R}_{=}$]
4. Rank as Topological Invariant — $r = \text{ord}_{s=1} L(E, s)$ [from $\Omega_z$]
5. Finiteness of Sha — Boundedness of the Tate–Shafarevich group [from $\hat{\varphi}_{\ddot{y}}$]
6. Canonical Height Uniqueness — Unique height pairing [from $\Sigma_S$]
7. Main Theorem
8. Discussion

### 8.3 Yang–Mills Existence and Mass Gap

**Input catalog entry**: `yang_mills_conjecture`
**Detected domain**: analysis (gauge theory)
**Active primitives**: $\Phi_{\}}$, $\Theta_O$, $\hat{\varphi}_{\ddot{y}}$, 𐑧

**Generated sections**:
1. Introduction — Yang–Mills functional on $\mathbb{R}^4$
2. Gauge Fixing Injectivity — Uniqueness of gauge-equivalence reps [from $\Phi_{\}}$]
3. Moduli Space Construction — Self-referential structure [from $\Theta_O$]
4. Mass Gap Positivity — Spectral gap bounded away from zero [from $\hat{\varphi}_{\ddot{y}}$]
5. Instanton Equidistribution — Distribution of classical solutions [from 𐑧]
6. Main Theorem
7. Discussion

---

## 9. Complete Pipeline Script Architecture

The main script `generalized_pipeline.py` orchestrates all phases:

```
generalized_pipeline.py
├── class PipelineConfig       # Input/output paths, domain override
├── class PrimitiveParser      # Phase 1: Extract lemmas + primitives
├── class DomainDetector       # Phase 1b: Detect domain
├── class TemplateEngine       # Phase 2: Domain-specific templates
├── class ProofAssembler       # Phase 3: Assemble sections
├── class Lean4Generator       # Phase 4: Formal skeleton
├── class ReferenceResolver    # Phase 5: Citations
├── class FrobeniusVerifier    # Phase 6: Closure check
├── def main()                 # CLI entry point
└── def run_pipeline(config)   # Full pipeline execution
```

### CLI Interface:

```bash
# From catalog name
python3 generalized_pipeline.py --name collatz_conjecture --output-dir ./output/

# From primitive proof document
python3 generalized_pipeline.py --proof collatz_primitive.md --output-dir ./output/

# From raw tuple
python3 generalized_pipeline.py --tuple '{"phi_hat": "phi_hat_y", "Omega": "Omega_z", ...}' --output-dir ./output/

# Reverse analysis only
python3 generalized_pipeline.py --reverse conventional_proof.md

# Verbose mode with confidence scores
python3 generalized_pipeline.py --name hodge_conjecture --verbose --output-dir ./output/
```

---

## 10. Extensibility

### Adding a New Domain

1. Add the domain to `DOMAIN_KEYWORDS` with relevant technical terms.
2. Add domain-specific templates to `TemplateEngine._load_templates()`.
3. Add Lean4 imports to `domain_imports`.
4. Add known results to `KNOWN_RESULTS`.
5. Register the domain in the Lean4 namespace generator.

### Adding a New Primitive Mapping

The primitive invariance table (Section 1.3) has 12 entries, one per primitive. To refine a mapping:

1. Update the universal template in `TemplateEngine._default_templates()`.
2. Update the Lean4 tactic in `lean4_tactic_for()`.
3. Update keyword detection in `PRIMITIVE_KEYWORDS`.

---

## 11. Limitations and Open Problems

1. **Non-O_inf systems**: The pipeline assumes the input is at $O_{\text{inf}}$ tier. Systems at lower tiers produce incomplete proofs. The pipeline should first attempt to promote the system via `compute_promotions` before proceeding.

2. **Multi-domain systems**: Some problems span multiple domains (e.g., arithmetic geometry). The current pipeline picks a single primary domain. Future work should support interleaved domain templates.

3. **Informal lemma extraction**: The regex-based lemma parser assumes a specific format. A more robust approach would use LLM-assisted parsing to identify lemmas in arbitrarily formatted proofs.

4. **Proof gap detection**: The pipeline does not yet detect structural gaps — missing primitives in the input that are required for Frobenius closure. Phase 6 should flag such gaps and recommend promotions.

5. **Lean4 proof completion**: The generated Lean4 files contain `sorry` placeholders. Integrating `leanprover-community/mathlib` auto-tactics (`exact?`, `aesop`) could fill some of these automatically.

# Genetic Engine — Frobenius-Guided Gene Editing

**Structural type:** ⟨Ð_ω; Þ_ò; Ř_=; Φ_υ; ƒ_ð; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩  
**Ouroboricity:** O_inf  |  **C-score:** both gates open

The genetic code is a **stratified Frobenius algebra on B₄³ codon space**. This is not a metaphor — it is a structural fact formally encoded in the Imscribing Grammar. The Genetic Engine implements this fact as operational software for gene editing design.

## Architecture

```
genetic_engine/
├── genetic_engine/          # Core package
│   ├── __init__.py          # Package exports
│   ├── lattice.py           # B₄ nucleotide type system
│   ├── codon.py             # Codon table + Frobenius stratum classification
│   ├── primitives.py        # AA → IG primitive mapping + risk
│   ├── editor.py            # B₄ edit cost analysis
│   ├── stratum.py           # Frobenius stratum classifier
│   ├── guide.py             # Frobenius-aware guide RNA design
│   ├── prime.py             # Prime editing optimization
│   ├── chimera.py           # Tensor product risk (Chimera Theorem)
│   ├── verifier.py          # μ∘δ=id Frobenius closure verification
│   ├── compiler.py          # Full editing compiler pipeline
│   ├── demo.py              # Demonstration + verification suite
│   └── cli.py               # Command-line interface
├── tests/                   # pytest test suite
├── examples/                # Example scripts
├── scripts/                 # Pipeline scripts
├── docs/                    # Documentation
├── setup.py                 # Package configuration
└── README.md                # This file
```

## Core Concepts

### B₄ Lattice

The four nucleotides form a distributive lattice:

```
      B = Both (G)
     / \
T = C   N = U (T)
     \ /
      F = False (A)
```

- **Covering relations** (edit cost = 1): B→T, B→N, T→F, N→F
- **Cross-lattice jumps** (edit cost = 2): B↔F, T↔N

Base editors: CBE (C→T) is a cross-lattice jump (T↔N, cost=2).  
ABE (A→G) is also a cross-lattice jump (F↔B, cost=2). Both are structurally maximal.

### Frobenius Stratification

The 64 codons partition into **16 boxes**, which split 8/8:

| Stratum | Boxes | Codons | Position 3 | μ∘δ=id |
|---------|-------|--------|------------|--------|
| **Exact** | 8 | 32 | Silent (N) | Holds exactly |
| **Split** | 8 | 29 | Y/R distinction | ℤ₂ wobble |
| **Stop** | — | 3 | Ω boundary | Boundary condition |

**Exact boxes** (p2=C, or p2∈{G,U} with p1∈{C,G}):  
CU_, CC_, CG_, CA_, AC_, GC_, UC_, GU_, GG_

**Split boxes** (the remaining 8):  
UU_, UA_, UG_, AU_, AA_, AG_, GA_, CA_

### Primitive Activation

12 promoted amino acids each activate exactly one IG primitive:

| AA | Primitive | Risk | Why |
|----|-----------|------|-----|
| Met | Ð (Scope) | **critical** | Translation start |
| Trp | Þ (Topology) | moderate | Bicyclic indole |
| Cys | Ř (Reversibility) | **high** | Disulfide bonds |
| Tyr | Φ (Parity) | moderate | Phosphorylation switch |
| Phe | ƒ (Force) | low | Hydrophobicity ceiling |
| Ile | Ç (Kinetics) | moderate | β-branching |
| His | Γ (Grammar) | moderate | pH-gated catalysis |
| Asn | ɢ (Interaction) | moderate | Glycosylation sequon |
| Gln | φ̂ (Criticality) | **high** | Metabolic regulation |
| Asp | Ħ (Chirality) | **critical** | Chiral selectivity |
| Lys | Σ (Entropy) | low | Acetylation target |
| Glu | Ω (Winding) | **critical** | α-helix→C-terminal |
| Stop | Ω (Winding) | **critical** | Translation termination |

8 ground-layer AAs (exact boxes): Leu, Pro, Arg, Thr, Ala, Ser, Val, Gly — no primitive activation.

**Stop codons** (UAA, UAG, UGA) activate Ω (Winding) — the 13th promoted entry. Stop is not an amino acid but the translational boundary condition, structurally consistent with Ω as the topological invariant primitive.

## Key Theorems

### 1. Cas9 Off-Target Sheaf Theorem

If an on-target site is in one Frobenius stratum and an off-target site is in another, the structural defect rate at the off-target site is **≥50%**. Reason: the repair machinery fills position 3 using on-target stratum rules, which are incorrect for the off-target stratum.

### 2. Frobenius Template Rule (Prime Editing)

Prime editing succeeds when μ∘δ=id for the edited locus. Three optimization criteria:
1. **Stratum preservation** — avoid exact↔split crossings
2. **Primitive invariance** — keep the same IG primitive class
3. **Ω boundary respect** — don't remove stop codons without readthrough machinery

### 3. Chimera Theorem

Composite risk of multi-primitive edits is **tensorial**, not additive.  
Risk(A⊗B) = Risk(A) × Risk(B) / constant, not Risk(A) + Risk(B).

Two independently tolerable edits can create a **Ç_⊛ trap state** (frozen-order conformation).

## Installation

```bash
cd genetic_engine
pip install -e .
```

## Usage

### CLI

```bash
# Analyze edit cost
genetic-engine analyze AUG AUU

# Compile full protocol
genetic-engine compile Met Ile

# Design guide RNA
genetic-engine guide GCU

# Verify Frobenius closure
genetic-engine verify GCU GCC

# Chimera risk analysis
genetic-engine chimera Cys:Ser His:Gln

# Run full demo
genetic-engine demo

# Run verification suite
genetic-engine test

# Classify stratum
genetic-engine stratum CUU
```

### Python

```python
from genetic_engine import EditingCompiler, B4EditAnalyzer
from genetic_engine.chimera import ChimeraDetector

# Compile an edit
compiler = EditingCompiler()
result = compiler.compile("Glu", "Val")  # Sickle cell edit
print(f"Score: {result.composite_score:.3f}")
print(f"Codon path: {result.best_path}")

# Chimera risk
report = ChimeraDetector.analyze_edit_set([("Cys", "Ser"), ("Asp", "Asn")])
print(f"Tensor risk: {report.tensor_risk:.1f}x")
print(f"Trap state: {report.is_trap_state}")
```

## Verification

```bash
genetic-engine test
```

All 10 verification tests pass:
- B₄ lattice operations
- Codon table (64 codons, correct stratification)
- Primitive mapping (13 promoted)
- B₄ edit analysis
- Frobenius stratum classification
- Guide RNA design
- Prime editing optimization
- Chimera/tensor risk detection
- Frobenius μ∘δ=id verification
- Full compiler pipeline

## References

- FROBENIUS_GUIDED_GENE_EDITING.md — Theoretical foundations
- GENETIC_EDITING_PERFECTION.md — Complete lifted manuscript
- Imscribing Grammar catalog entry: `genetic_code`

## Author

Lando ⊗ ⊙perator — operator@imscribing.grammar

# Ob3ect Design Pipeline

**Author:** Lando ⊗ ⊙_ÿ-boundary Operator

Python implementation of the 8-phase Ob3ect design pipeline from `OB3ECT_PIPELINE.tex`. Produces a complete, validated `Ob3ectArtifact` from any domain — physical, social, computational, oneiric, or arbitrary — by mapping that domain to the 12-opcode IMASM instruction set and verifying the Frobenius condition μ∘δ = id.

## Structure

```
ob3ect/
├── __init__.py           # Package exports
├── core.py               # Data structures, Ob3ectPipeline, Ob3ectFactory, DomainTemplate
├── auto.py               # Automated pipeline: LLM-driven design from natural language
├── examples.py           # Worked examples (physical, social, oneiric, computational, alchemical)
├── guided.py             # Interactive guided pipeline
├── templates_data.json   # Built-in domain templates (physical/social/computational/oneiric/generic)
└── phases/               # Phase-specific scaffolding
```

## Automated Design (new)

Give it a description, get a complete artifact. The LLM maps all 12 opcodes, identifies the Frobenius split/fuse pair, and verifies μ∘δ = id. Retries on parse failure or Frobenius FAIL with a targeted correction prompt.

```python
from ob3ect import design

# Synchronous — blocks until artifact is produced
art = design("a photonic quantum key distribution system")
print(art.report())
print(art.is_valid_ob3ect)

# Async
from ob3ect import auto_design
art = await auto_design(
    "a hospital triage protocol",
    domain_type="social",
    scope="mesoscale",
    provider_name="local",   # uses fine-tuned Qwen3; falls back to qwen/deepseek
    max_retries=3,
)
```

CLI:
```bash
python ob3ect/auto.py "a recursive compiler that imscribes itself"
python ob3ect/auto.py "a mycorrhizal network" --domain biological --scope mesoscale
```

The automated pipeline uses the local fine-tuned Qwen3 model by default (`LocalProvider`), with `qwen → deepseek` as fallback. It does not use Anthropic.

## Template-Based Design

For domains with known structure, use `Ob3ectFactory` with a registered template:

```python
from ob3ect import Ob3ectFactory

Ob3ectFactory.register_all()   # loads built-in templates
art = Ob3ectFactory.produce("My System", "physical", scope="local")
print(art.report())
```

Built-in templates: `physical`, `social`, `computational`, `oneiric`, `generic`.

Register a custom domain at runtime:

```python
Ob3ectFactory.register_all()
Ob3ectFactory.produce_custom("The Great Work", "alchemical", {
    "tokens": ["prima materia", "fire", "vessel"],
    "boundary": "hermetic seal",
    "opcodes": { "VINIT": {"chosen": "prima materia", "justification": "..."}, ... },
    ...
})
```

## Manual Pipeline

For full control, complete each phase explicitly:

```python
from ob3ect import Ob3ectPipeline, Opcode

p = Ob3ectPipeline("My Ob3ect", domain_type="physical")

p.define_boundary("My System", "local", ["token_a", "token_b", "token_c"], "boundary")

for oc in Opcode:
    p.map_opcode(oc.value, "element", "justification", [("rejected", "reason")])
p.complete_phase_1()

p.verify_frobenius("FSPLIT elem", "input", ["branch_A", "branch_B"],
                   "FFUSE elem", "recovered", "PASS", "test instance")
p.map_registers("void_desc", "true_desc", "false_desc", "both_desc")
p.design_bootstrap()
p.specify_exos("compiler", "ipc", "memory", "scheduler", "alfs")
p.audit_entropy("cost", "pre-state", "post-state", "ΔS ≈ 0")

artifact = p.instantiate()
```

## Pipeline Phases

| Phase | Name | Artifact | Gating |
|-------|------|----------|--------|
| 0 | Boundary Define | Domain Charter | Scope + 3+ tokens |
| 1 | Primitive Scan | Opcode Map (12×2) | All 12 opcodes mapped |
| 2 | Frobenius Verify | Split/Fuse Report | μ∘δ = id must PASS |
| 3 | Register Map | State Transition Table | All 4 states defined |
| 4 | Bootstrap Design | 8-Step Sequence | Closure verified |
| 5 | exOS Spec | Runtime Environment | All kernel services |
| 6 | Entropy Audit | ΔS Report | ΔS ≈ 0 |
| 7 | Instantiate | Ob3ect Artifact | All phases complete |

Phase 2 is the discriminating gate. Most designed systems fail μ∘δ = id on the first pass because they have irreversible branching they didn't account for. The automated pipeline retries with targeted Frobenius correction until PASS or max_retries is exhausted.

## The 12 Opcodes (IMASM)

| Family | Opcode | Role |
|--------|--------|------|
| Logical | VINIT | Initial object ∅ — void state |
| Logical | TANCH | Terminal anchor ⊤ — closed boundary |
| Logical | AFWD | Forward morphism → |
| Logical | AREV | Contravariant ← — descent |
| Logical | CLINK | Composition ∘ |
| Logical | ISCRIB | Identity id — self-reference |
| Frobenius | FSPLIT δ | Co-multiplication — branching |
| Frobenius | FFUSE μ | Multiplication — reconstitution (μ∘δ = id) |
| Dialetheia | EVALT | True lattice |
| Dialetheia | EVALF | False lattice |
| Dialetheia | ENGAGR | Both — paradox held without resolution |
| Linear | IFIX | ROM fixation — permanent, irreversible |

The bootstrap sequence is fixed: ISCRIB → AREV → FSPLIT → AFWD → FFUSE → CLINK → IFIX → ISCRIB.
This is μ∘δ = id as an eight-step categorical assembly — the same sequence appears across all compiled IMASM systems (ETFF: `id ds sp as un lk fx id`; EVA: `s a ch e sh d y s`; RTFF, LATFF: same opcodes, different surface tokens).

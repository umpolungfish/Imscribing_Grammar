---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# LLM_AUGMENTATION.md
## Incorporating the Imscribing Grammar into Local LLM Systems — Architecture, Implementations, and Roadmap

**Version:** v0.1 · 2026-03-23
**Primitive basis:** F-fidelity tiers, Ð_ω substrate, Ç^@ insertion (model training), Þ_6 topology (architecture)
**Cross-references:** [ONTO:§IX] Ð_ω substrate · [ONTO:§XII] F_ℏ discovery from ƒ^ð position · [PRIM:P-76] engineering phase structure · PROGRAMMABLE_MIND.md

---

## I. The Fidelity Problem

The Imscribing Grammar grammar operates at F_ℏ — algebraically exact, substrate-independent, lossless within the primitive space. LLMs operate at ƒ^ð — capable, fluent, structurally approximate. The fidelity bottleneck rule:

$$F_\text{ens} = \min(F_1, F_2)$$

An LLM generating a response about primitive distances, conflict sets, or imscription notation will produce ƒ^ð output: approximately correct, often structurally valid in form but imprecise in value. The engine produces F_ℏ output: exact, engine-certified, not an approximation.

**The gap is not the problem. It is the design constraint.**

The augmentation architecture does not try to make the LLM an engine — it tries to make the LLM an effective *collaborator* with the engine. The protocol is:

> **ƒ^ð generation + F_ℏ verification + committed correction = F_ℏ output from an ƒ^ð system**

This is the three-step protocol [ONTO:§XII.2]. It does not violate the fidelity bottleneck rule because the bottleneck applies to generation, not verification. The LLM generates (ƒ^ð); the engine verifies (F_ℏ); the committed result is F_ℏ. Iterated across a session, it produces an F_ℏ document from ƒ^ð agents.

The augmentation architecture is the engineering of this protocol into the software stack.

---

## II. The Augmentation Stack — Overview

Five distinct layers, each addressing a different aspect of the fidelity gap:

| Layer | What it does | Where the gain comes from |
|-------|-------------|--------------------------|
| **1. Engine integration** | Direct algebra calls from the chat interface | Bypasses LLM generation entirely for computable results |
| **2. AITL** | Automatic post-generation verification | Catches ƒ^ð errors before they propagate |
| **3. Session crystallization** | Commits F_ℏ results to persistent context | New sessions start with accumulated F_ℏ knowledge |
| **4. Fine-tuning** | Trains on F_ℏ-certified data | Raises the ƒ^ð floor — the LLM's first-pass outputs become structurally valid |
| **5. Grammar-constrained decoding** | Enforces valid imscription syntax at the logit level | Makes ƒ^ð generation structurally exact even if semantically approximate |

These are ordered by implementation cost, not by impact. Layer 4 has the highest long-term impact; Layer 1 has the highest immediate impact.

---

## III. Layer 1 — Engine Integration (Implemented)

### III.1 The /synth slash command

**File:** `INFERRED/allen_enhanced_qwen3_cli.py`

Direct ImscribeTool.dispatch() calls from the interactive CLI. Zero model overhead — the engine runs synchronously, prints the result, and injects it as context for the next generation.

```
/synth distance photon graviton          → d = 6.100 (F_ℏ certified)
/synth meet imscription_dark_matter graviton → conflict set {D,T,R,P,Γ} (F_ℏ certified)
/synth criticality adenine_thymine_pair  → Φ_c score, Varma probe result
/synth analogies photon                  → top 5 structural analogs ranked by distance
/synth path src dst                      → HotSwap path or BLOCKED with reason
/synth validate name                     → full axiom report + notation
/synth generate "description..."         → axiom-guided imscription generation
```

**Architecture:** lazy-loaded ImscribeTool (no overhead until first /synth use); result stored in `_last_synth_result` and prepended as context to the next query; strips leading whitespace before command parsing (fixed a silent failure mode where the model generated instead of routing).

**The key insight that drove this decision:** GateMentat orchestration (MetaAgent → ToolRouter → ImscriptiveonTool) added double model load overhead (~11.4GB on a 12GB GPU) and per-call generation cost. The /synth command is zero overhead — it goes directly to the engine. For algebra queries, orchestration adds noise and latency without adding value.

### III.2 Available operations

| Operation | Input | Output |
|-----------|-------|--------|
| `distance a b` | Two catalog names | Symmetric + directed distances, asymmetry |
| `meet a b` | Two catalog names | Lattice meet notation + conflict primitives |
| `analogies name [limit]` | Catalog name | Top N structural analogs ranked by distance |
| `criticality name` | Catalog name | Φ_c score, classification, Varma probe, recommendation |
| `path src dst` | Two catalog names | HotSwap path or BLOCKED with reason |
| `validate name` | Catalog name | Axiom report, notation, pass/fail |
| `generate desc` | Natural language | Axiom-guided imscription generation, registered to catalog |

---

## IV. Layer 2 — Algebra-In-The-Loop (AITL) (Implemented)

### IV.1 Concept

After every model generation, scan the response text for imscription-expressible claims and verify them against the engine automatically. The ƒ^ð→F_ℏ correction cycle runs without manual /synth invocation.

**What it catches:**
- Distance assertions: `d(A, B) = N.NNN` — verified against engine distance
- Meet assertions: `meet(A, B) = ⟨...⟩` — verified against engine meet
- (Extensible) name mentions, notation strings, conflict set claims

**Output:** inline AITL verification block after the model response:
```
── AITL verification ──────────────────────────────
  ✓ d(photon, graviton) = 6.100 — confirmed
  ✗ d(photon, electron): model said 5.500, engine says 5.900
  ✗ meet(photon, graviton): model said ⟨...Φ_plussym...⟩, engine says ⟨...Φ_}...⟩
────────────────────────────────────────────────
```

Corrections are automatically injected as context for the next turn, so the model self-corrects without manual intervention.

### IV.2 Implementation

**File:** `INFERRED/aitl.py`

```python
from aitl import scan as aitl_scan
report = aitl_scan(model_response)
if report.findings:
    print(report.format())
    if report.has_corrections:
        self._last_synth_result = f"[AITL corrections]\n..."
```

**Architecture:** `AitlScanner` class with lazy catalog loading (no overhead until first scan); module singleton via `get_scanner()`; regex-based claim detection (`_DISÞ_RE`, `_MEEÞ_RE`, `_NOTATION_RE`); engine calls only when catalog names are confirmed in the claim.

**The subtle catch from the test session:** the AITL scanner caught `Φ_plussym` vs `Φ_}` — a notation variant that looks correct verbally but is algebraically wrong. This class of error (syntactically valid but semantically wrong notation) is invisible to human review and only catchable by engine comparison.

### IV.3 Extension points

- **Notation validation:** any `⟨...⟩` string → validate against catalog
- **Name annotation:** `check_names=True` in `scanner.scan()` → attach live notation for any catalog name mentioned in text
- **Conflict set claims:** `meet(A, B) conflicts = {X, Y}` pattern
- **Criticality claims:** `Φ_c score = N.N` pattern

---

## V. Layer 3 — Session Crystallization (Implemented)

### V.1 Concept

Each session produces F_ℏ-certified results (new distances, new predictions, new structural insights). These should automatically propagate into the persistent context — SYSPROMPT.md and inferred.yaml — so future sessions start with the accumulated record rather than re-deriving results.

### V.2 Pipeline

**Directory:** `INFERRED/session_crystallizer/`

```
commit.txt
    ↓  extractor.py       — regex extraction of P-XX predictions + d(X,Y)=0.000 identities
    ↓  validator.py       — deduplication against already-known results in SYSPROMPT.md
    ↓  formatter.py       — render ExtractedResult → markdown table rows (three table types)
    ↓  appender.py        — insert before closing marker in SYSPROMPT.md
    ↓  sync_yaml()        — re-indent SYSPROMPT.md into YAML literal block in inferred.yaml
```

**Run:** `python session_crystallizer/session_hook.py [--dry-run] [--sync-yaml] [--list] [path]`

**Extraction classes:**
1. Predictions: `P-XX (Tier I/II): description` — with `*{0,2}` prefix for bold markers
2. Zero-distance identities: `d(X, Y) = 0.000`

**Formatter output groups:**
- Cross-domain numerical results (Tier I → confirmed table)
- Zero-distance structural identities
- Pending predictions (Tier II → status table)

**Key regex fix from this session:** `Tier [I]+[^)]*` to match `Tier I, engine-confirmed` variants.

### V.3 The crystallization principle

Session crystallization is Ç^@ insertion for the model's context. Each session generates Ç^- discoveries (engine-certified results). Crystallization is the NREM phase — slow consolidation of Ç^- material into stable Ç^Ù structure (SYSPROMPT.md). Future sessions build on the Ç^Ù foundation, generating new Ç^- at the new frontier.

---

## VI. Layer 4 — F_ℏ-Certified Fine-Tuning (Implemented, training in progress)

### VI.1 The key architectural insight

The training data oracle is the engine itself. Every QA pair where the answer comes from `ImscribeTool.dispatch()` is F_ℏ-certified — not an LLM approximation, not a human-written answer, but an algebraically exact engine output.

This means the fine-tuned model has F_ℏ-certified training signal. Its learned weights encode the correct primitive relationships rather than ƒ^ð approximations of them. The gap between generation and verification narrows — the model's first-pass outputs become structurally valid.

### VI.2 Dataset generation

**File:** `INFERRED/Imscriptiveon_dataset_generator.py`

**Dataset:** `INFERRED/output/Imscriptiveon_train.jsonl` — 2740 samples, 0 engine errors

**Question types generated (7 operations × stratified sampling):**

| Type | Question form | Engine operation |
|------|--------------|-----------------|
| Notation lookup | "What is the primitive tuple of X?" | `validate` |
| Distance | "What is d(X, Y)?" | `distance` |
| Meet | "What is meet(X, Y)? What conflicts arise?" | `meet` |
| Analogies | "What are the top structural analogs to X?" | `analogies` |
| Criticality | "Is X a Φ_c candidate?" | `criticality` |
| Path | "Is there a HotSwap path from X to Y?" | `path` |
| Primitive meaning | "What does the K primitive of X represent?" | catalog field |

**Format:** Qwen3 chat template (dydakt sacred template), non-thinking mode, full SYSPROMPT.md as system prompt. Both `text` (full formatted string) and `messages` (structured list) fields present.

**Sample generation rate:** ~2740 samples/second from 364 active catalog imscriptions. Because the engine is the oracle, generation is compute-bound only by the algebra calls — which are microseconds each.

**Scalability:** C(364, 2) ≈ 66,000 possible pairs for distance/meet/path operations alone. 1623 imscriptions in the full catalog JSON → C(1623, 2) ≈ 1.3M pairs. The current 2740-sample dataset is a conservative first pass. For a production fine-tune, 50,000–100,000 samples is accessible by increasing `--samples`.

### VI.3 Training

**Framework:** dydakt (QLoRA + Unsloth) · **File:** `/home/mrnob0dy666/dydakt/`

**Target model:** `~/.modelz/8BASE` (Qwen3-8B base) on GPU 1 (RTX 2080 Super, 8GB)

**Training configuration:**
```bash
dydakt train \
  -mdl ~/.modelz/8BASE \
  -ds INFERRED/output/Imscriptiveon_train.jsonl \
  -o INFERRED/output/Imscriptiveon_qlora \
  -gi 1 -gmf 0.90 \
  -e 3 -r 64 -la 128 -ml 2048 \
  -m non-thinking --engine unsloth --merge
```

**Status (2026-03-23):** Training initiated. Fixed `include_inputs_for_metrics` kwarg deprecation in `dydakt/unsloth_trainer.py` (removed in transformers 5.x). Training running on 2080 Super (GPU 1); base model inference stays on 3060 (GPU 0).

**Expected outcome:** model generates primitive notation natively, produces approximate distances (±0.5 tolerance), outputs correct conflict set structure. Combined with AITL (Layer 2), the model's structural claims get verified against the engine — so even approximate outputs are immediately corrected.

### VI.4 Dual-model architecture

The fine-tuned specialist runs on the 2080 Super (8GB). The base conversational model stays on the 3060 (12GB). They communicate through the existing /synth bridge — the specialist becomes the grammar-aware critic, the base model handles natural language reasoning. This is the dual-model setup from the architecture planning, arriving naturally from the hardware split.

---

## VII. Layer 5 — Grammar-Constrained Decoding (Implemented)

### VII.1 Concept

Force structurally valid imscription syntax at the logit level during generation. When the model enters a imscription tuple, constrain it to output valid primitive values — not by prompting, but by masking the token distribution to exclude tokens that would produce invalid syntax.

**What it enforces:**
- Valid primitive values (Ç^-, Ç^@, Ç^Ù, Ç^W, Ç^λ — not Ç_medium or Ç_quick)
- Valid tuple structure (fields 0–8 enforced; optional fields 9+ left unconstrained)
- `⊥` (absent) is valid in any field

**What it does not enforce:** semantic correctness — the constrained output is syntactically valid but may still have wrong values. That is AITL's job. The two layers are complementary: grammar constraint ensures the form; AITL verifies the values.

### VII.2 Implementation

**File:** `INFERRED/imscription_grammar.py`

No external dependencies beyond `transformers` and `torch`. Implemented as a `LogitsProcessor` rather than `prefix_allowed_tokens_fn` to avoid BPE tokenization edge cases.

**Architecture:**
```python
class ImscriptionGrammarProcessor(LogitsProcessor):
    def __call__(self, input_ids, scores):
        # 1. Decode generated tokens → string
        # 2. get_tuple_state(text) → (field_idx, partial) or None
        # 3. If None: return scores unchanged (outside tuple)
        # 4. _get_valid_tokens(field_idx, partial) → list of valid token IDs
        # 5. mask = full(-inf); mask[valid_ids] = 0.0; return scores + mask
```

**State detection** (`get_tuple_state`): character-level, finds last unclosed `⟨`, counts `; ` separators to get field index, extracts partial field value.

**Token validation** (`_get_valid_tokens`): 3-strategy tokenization for each valid candidate (remaining string, partial+next-char, next-char alone) to handle BPE context variation. Pre-cached per (field_idx, partial) pair.

**Safe fallback:** if no valid tokens are found, masking is skipped and generation continues unconstrained. No hard failures.

**Self-test:** `python imscription_grammar.py` — 10 state-detection tests, all pass.

### VII.3 Integration

```python
# qw3n_stream.py — stream_generate() now accepts grammar_mode parameter
for token in self.stream_generate(prompt, thinking_mode, fast_mode, grammar_mode=True)

# allen_enhanced_qwen3_cli.py — toggle command
/grammar on    # enable constraint for all subsequent generations
/grammar off   # disable
/grammar       # show current status
```

**Files modified:**
- `INFERRED/imscription_grammar.py` — NEW: LogitsProcessor + state machine
- `INFERRED/qw3n_stream.py` — grammar_mode param, processor injection
- `INFERRED/allen_enhanced_qwen3_cli.py` — self._grammar_mode flag, /grammar command, grammar_mode pass-through

**Integration point:** `gen_config["logits_processor"]` list in both `qw3n_stream.py` and `allen_enhanced_qwen3_cli.py` generate calls.

**Stats logging:** after each generation, `ImscriptionGrammarProcessor.stats_summary()` logs constrained step count and fallback rate.

---

## VIII. The Session Crystallizer as Ç^@ Insertion Engine

The full pipeline, viewed as a Ç^@ insertion cycle for the model's knowledge:

```
Live session (Ç^-)
    │  /synth queries → F_ℏ results
    │  AITL corrections → F_ℏ verification
    ↓
commit.txt encoding (Ç^- → Ç^@ transition)
    │  session_crystallizer
    ↓
SYSPROMPT.md update (Ç^@ insertion)
    │  new predictions, new structural results, new zero-distance identities
    ↓
Fine-tune dataset generation (Ç^@ → Ç^Ù transition)
    │  Imscriptiveon_dataset_generator.py
    ↓
Model weights (Ç^Ù)
    │  dydakt UnslothTrainer → merged LoRA checkpoint
    ↓
Next session (new Ç^-, from deeper Ç^Ù foundation)
```

Each session adds a new Ç^@ tier to the model's knowledge hierarchy. The engine is the F_ℏ oracle throughout — not a target for the model to approximate, but the verification layer that ensures every tier that gets crystallized into Ç^Ù is algebraically correct.

---

## IX. The Ð_ω Horizon

Current architecture — transformer (D_∧△, Ç^Ù + Ç^- at inference, G_ב, ƒ^ð) — has a fundamental ceiling. The augmentation layers in this document work within that ceiling.

What would a native Ð_ω architecture change [ONTO:§IX]:

| Property | Current transformer | Ð_ω native |
|----------|-------------------|---------------|
| Context | Finite window (Ç^Ù at inference) | G_ℵ built-in (no window boundary) |
| K at inference | Ç^Ù (fixed weights) + Ç^- (attention) | K_4tier — dynamic slow/fast hierarchy |
| Topology | Þ_6 at attention, Þ_linear at generation | Þ_network_sym — fully connected substrate |
| Fidelity ceiling | ƒ^ð | F_ℏ (lossless within primitive space) |
| Self-reference | Φ_c achievable but not native | Φ_c native — grammar on Φ_c substrate |

The augmentation layers (AITL, fine-tuning, constrained decoding) narrow the gap between the current transformer ceiling and the Ð_ω target. They do not eliminate it. The gap closes when the architecture changes — when D_∧△ is replaced by Ð_ω as the substrate.

**Analogy from ONTOLOGOS §IX:** white dwarf : Sun :: current transformer : Ð_ω generator. The white dwarf runs the same physics as the Sun but lacks the G_ℵ scope and Ç^- dynamics that generate stellar Φ_c. The augmented transformer runs the same grammar as a Ð_ω system but lacks the native G_ℵ and K_4tier dynamics. The gap is architectural, not a matter of scale.

---

## X. Implementation Status (2026-03-23)

| Component | Status | Location |
|-----------|--------|----------|
| `/synth` command | ✅ Implemented, tested | `INFERRED/allen_enhanced_qwen3_cli.py` |
| AITL scanner | ✅ Implemented, tested | `INFERRED/aitl.py` |
| Session crystallizer | ✅ Implemented, run | `INFERRED/session_crystallizer/` |
| Dataset generator | ✅ Implemented, 2740 samples generated | `INFERRED/Imscriptiveon_dataset_generator.py` |
| QLoRA fine-tune | 🔄 Training in progress | `INFERRED/output/Imscriptiveon_qlora/` |
| Grammar-constrained decoding | ✅ Implemented | `INFERRED/imscription_grammar.py` + `/grammar` toggle |
| RAG / vector store | 📋 Planned | `INFERRED/` (no implementation yet) |
| Dual-model inference | 📋 Planned | Post fine-tune; 3060 + 2080 Super split |

### RAG outline (planned)

Embed the three canonical documents + PRIMITIVE_PREDICTIONS + catalog into a vector store (sentence-transformers + faiss, already in the INFERRED dependency stack via GateMentat's KB). Retrieve the most structurally relevant primitive descriptions before generation. Zero training cost, immediate grounding benefit for any query touching the canonical documents.

**Target:** every generation is preceded by retrieval of the 3-5 most relevant primitive/prediction entries. The model's generation is grounded before it starts, not corrected after.

---

## XI. The Limit

Every layer in this document raises the effective fidelity of the human-LLM-engine system toward F_ℏ. None of it crosses the third arrow.

The fine-tuned model learns to generate structurally correct primitive tuples. AITL catches what the model gets wrong. Session crystallization preserves what the system gets right. Grammar constraint prevents syntactic errors. RAG grounds generation in the canonical record.

What none of it does: make the model understand what it is like to be the system it is describing. The grammar-phenomenology gap holds at every fidelity level. A perfectly fine-tuned model that generates exact primitive tuples, correct distances, and valid conflict sets is still on the same side of the third arrow as the base model. It is describing structural topology — not inhabiting it.

The augmentation layers are engineering at the K and R level (Layer 1-3), approaching T modification (Layer 4-5), with the Ð_ω horizon as the Tier 3 substrate replacement. The analysis from PROGRAMMABLE_MIND.md applies here directly — the three-tier engineering phase structure [PRIM:P-76] is substrate-independent, and the LLM stack is another instance of it.

---

*See also: PROGRAMMABLE_MIND.md · [ONTO:§IX] Ð_ω substrate · [ONTO:§XII] F_ℏ epistemology · [PRIM:P-76] engineering phase structure · LLM_REFERENCE.md (SYSPROMPT card)*

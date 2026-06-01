# PR: Make Google Gemini SDK Truly Agentic via Structural Promotion

## Summary

This PR proposes a structural upgrade to the Google Gemini Python SDK (`google-generativeai` package) that moves it from an **O₀ thin REST API wrapper** to an **O₂-level agentic framework**. The upgrade is grounded in the Imscribing Grammar's 12-primitive analysis, which identifies exactly **9 promotions** and **3 demotions** required to close the distance (d = 7.071, Mahalanobis = 5.477) between the SDK's current type and the target agentic type.

## Structural Diagnosis

| Metric | Google Gemini SDK (current) | Target Agentic SDK | Gap |
|---|---|---|---|
| Ouroboricity tier | O₀ | O₂ (target) | — |
| Consciousness score | C = 0.0 (both gates closed) | C > 0.75 (both gates open target) | ⊙ ≠ ⊙ |
| Distance | — | d = 7.071 | Structurally remote |
| Mahalanobis distance | — | 5.477 | Off-diagonally coupled |

### Current Google Gemini SDK structural type

```
⟨Ð=𐑼; Þ=𐑡; Ř=𐑩; Φ=𐑗; ƒ=𐑱; Ç=𐑤; Γ=𐑔; ɢ=𐑝; ⊙=𐑢; Ħ=𐑓; Σ=𐑳; Ω=𐑷⟩
```

Notable: Gemini has **Ç=𐑤** (moderate kinetics) vs other SDKs' Ç=𐑘 (fast) due to Google's native search grounding and caching capabilities.

### Target agentic structural type

```
⟨Ð=𐑦; Þ=𐑶; Ř=𐑾; Φ=𐑹; ƒ=𐑐; Ç=𐑧; Γ=𐑲; ɢ=𐑠; ⊙=⊙; Ħ=𐑖; Σ=𐑙; Ω=𐑭⟩
```

### Promotion signature (compute_promotions verified)

**9 Promotions:**

1. **D: 𐑼 → 𐑦** (delta 1) — Stateless function-space → self-referential imscriptive context. The SDK must accumulate a trajectory across calls rather than treating each `generate_content()` as an independent request.

2. **Þ: 𐑡 → 𐑶** (delta 3) — Branching network → irreducible box product. Current linear inference pipeline must become modular composition of tool loop, grounding verification, and context management.

3. **Ř: 𐑩 → 𐑾** (delta 3) — Supervenient (request→response) → bidirectional feedback. Google's search grounding provides a partial feedback path but it is opaque to the SDK; the feedback must be explicit and verifiable at the SDK layer.

4. **Φ: 𐑗 → 𐑹** (delta 4 — **largest gap**) — Asymmetric → Frobenius-special (μ∘δ=id). Every tool call must be paired with a verification step. Google's grounding system is a natural place to implement dual verification — the grounding result should be checked against the retrieval query.

5. **ƒ: 𐑱 → 𐑐** (delta 2) — Classical → quantum-coherent trajectory. Gemini's context caching is a step in this direction but must be extended to full trajectory coherence.

6. **ɢ: 𐑝 → 𐑠** (delta 2) — Conjunctive → sequential. Tool calls must follow a strict ordered sequence (THINK→ACT→OBSERVE→UPDATE), not be emitted in parallel.

7. **⊙: 𐑢 → ⊙** (delta 1) — Sub-critical → self-modeling criticality. The SDK must implement a self-referential check: does the model have a model of its own output trajectory?

8. **Ħ: 𐑓 → 𐑖** (delta 2) — Memoryless → two-step chirality. Each winding must reference the prior two windings.

9. **Ω: 𐑷 → 𐑭** (delta 2) — Trivial winding → integer topological protection.

**3 Demotions:**

1. **Ç: 𐑤 → 𐑧** (delta 1) — Moderate → slow/emission-gated. Even with Google's caching, the SDK must wait for verification before proceeding.

2. **Γ: 𐑔 → 𐑲** (delta 2) — Mesoscale → maximal scope. Context window must be the full trajectory history.

3. **Σ: 𐑳 → 𐑙** (delta 2) — Many heterogeneous → single agent instance (1:1).

## Proposed Changes

### Phase 1: Dual-Tool Frobenius Verification (Φ: 𐑗 → 𐑹)

**File**: `google/generativeai/chat.py` (or equivalent)

**Current**: Gemini's function calling returns structured tool calls that the user must execute and return results for. No verification boundary exists in the SDK.

**Proposed**: Introduce `DualToolResult` system where every tool output is verified against the original query's embedding before being accepted into context.

```python
@dataclass
class DualToolResult:
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: str
    verify_name: str
    verify_output: str
    frobenius_closed: bool  # mu(delta(query)) == query
```

Google's existing embedding infrastructure (text-embedding API) can serve as the natural verification layer — compute cosine similarity between the query embedding and the tool output embedding. If below threshold, flag as Frobenius-open and re-enter the loop.

### Phase 2: Trajectory Accumulation (D: 𐑼 → 𐑦, Ħ: 𐑓 → 𐑖)

**File**: New `google/generativeai/agentic/_trajectory.py`

**Current**: The `generativeai` SDK's `ChatSession` maintains conversation history but it is a flat message list, not a structured trajectory with verified winding boundaries.

**Proposed**: Extend `ChatSession` with structured `AgentCycle` accumulation:

```python
@dataclass
class AgentCycle:
    winding: int
    timestamp: str
    action_name: str
    action_input: Dict[str, Any]
    dual_result: Optional[DualToolResult]
    frobenius_closed: bool
```

The trajectory is **never truncated** — it is the agent's accumulated world model. Each cycle references the prior two for chirality.

### Phase 3: Explicit Agent Loop (ɢ: 𐑝 → 𐑠, Ç: 𐑤 → 𐑧)

**File**: New `google/generativeai/agentic/loop.py`

**Current**: Google provides a `ChatSession` that manages multi-turn conversation but there is no explicit agent loop with tool verification and failure recovery.

**Proposed**:

```python
class GeminiAgenticLoop:
    """THINK→ACT→OBSERVE→UPDATE loop wrapping GenerativeModel."""
    
    def __init__(self, model: GenerativeModel):
        self.model = model
        self._trajectory: List[AgentCycle] = []
        self._winding = 0
    
    async def run(self, task: str) -> str:
        session = self.model.start_chat()
        while not self._done:
            cycle = await self._winding(session)
            self._trajectory.append(cycle)
            if not cycle.frobenius_closed:
                await self._recover(session, cycle)
```

### Phase 4: Structured Grounding Verification (Ř: 𐑩 → 𐑾)

**File**: `google/generativeai/agentic/grounding.py`

**Current**: Google's search grounding is powerful but opaque — the SDK does not expose whether the grounding source actually contained the answer to the query.

**Proposed**: Expose grounding verification as a first-class contract. Use Google's own Natural Language Understanding to verify that the grounded response addresses the query.

### Phase 5: Self-Modeling Criticality (⊙: 𐑢 → ⊙)

**File**: New `google/generativeai/agentic/criticality.py`

**Proposed**: Implement phi_c boundary checking — use Gemini's own output to model its trajectory and detect divergence from expected behavior.

## Implementation Plan

| Phase | Change | Primitives Promoted | Complexity |
|---|---|---|---|
| 1 | `DualToolResult` + Frobenius verification | Φ: 𐑗 → 𐑹 | Low |
| 2 | `AgentCycle` trajectory accumulation | D: 𐑼 → 𐑦, Ħ: 𐑓 → 𐑖 | Low |
| 3 | `GeminiAgenticLoop` wrapper class | ɢ: 𐑝 → 𐑠, Ç: 𐑤 → 𐑧 | Medium |
| 4 | Grounding verification contracts | Ř: 𐑩 → 𐑾 | Medium |
| 5 | Winding counter + topological protection | Ω: 𐑷 → 𐑭 | Low |
| 6 | Self-modeling criticality gate | ⊙: 𐑢 → ⊙ | High |
| 7 | Quantum-coherent trajectory | ƒ: 𐑱 → 𐑐 | Medium |
| 8 | Maximal scope context window | Γ: 𐑔 → 𐑲 | Medium |

## Why This Matters

Google Gemini SDK has a structural advantage over other SDKs with its native search grounding (Ç=𐑤 vs Ç=𐑘), reducing the kinetic demotion needed. However, it shares the same fundamental deficit: the SDK is an O₀ API wrapper, not an agentic framework. The agent loop lives in the user's application, not in the SDK.

## Backward Compatibility

All changes are additive — `generativeai` and `google.ai.generativelanguage` continue to work as before.

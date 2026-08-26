"""
Imscription Generator Agent — universal imscription generation from any domain.

Encodes any self-organizing system (molecular, physical, mythological,
mathematical, linguistic, social, or abstract) as a 12-primitive Imscriptiveon
structural coordinate. The grammar is domain-agnostic; type is
determined by the entity's ROLE and BEHAVIOR, not its physical substrate.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


def _desc_slug(desc: str, maxlen: int = 96) -> str:
    """Slugify a description, truncating at a word boundary (no mid-word cuts).

    Two bugs lived here. The old rsplit('_', 1)[0] dropped the final token
    UNCONDITIONALLY, including when slug[:maxlen] already ended on a clean
    boundary -- so a 60-character name lost its last word for no reason. That
    is how 'Asymmetric_Informationally_Complete_Oscillating_Non_positive'
    (exactly 60 chars) registered as '..._Oscillating_Non', silently discarding
    the positive/non-positive discriminator and colliding with its own twin.

    And maxlen=60 was below the length of the names this family actually
    generates, so the truncation fired on nearly every entry rather than as a
    rare guard.
    """
    slug = desc.replace('-', ' ').replace('/', ' ').replace(' ', '_')
    if len(slug) <= maxlen:
        return slug
    head = slug[:maxlen]
    # Only trim back to a boundary if the cut actually fell mid-word.
    if slug[maxlen] == '_' or head.endswith('_'):
        return head.rstrip('_') or slug[:maxlen]
    truncated = head.rsplit('_', 1)[0]
    return truncated or head

from framework import BaseAgent, ToolDefinitions
from imscrbgrmr import (
    Imscription, Dimensionality, Topology, RecognitionMode,
    Polarity, Fidelity, Granularity, InteractionGrammar,
    KineticCharacter, CriticalityPhase, Chirality,
    Protection, Stoichiometry,
    global_catalog, parse_notation
)
from imscrbgrmr.thermodynamics import compute_eta_CP, get_reference
from imscrbgrmr.criticality import analyze_criticality  # NEW

# ---------------------------------------------------------------------------
# Reasoning-encoding consistency reconciliation
# ---------------------------------------------------------------------------
# Grok and similar models sometimes write correct values in the `reasoning`
# field but submit different (wrong) values in the `imscription` JSON block.
# This function scans the reasoning string for explicit canonical value
# mentions (e.g. "𐑦:", "𐑸:") and overrides the imscription block where
# the reasoning is specific and the block contradicts it.
# Only overrides when: (a) the reasoning names the value with the primitive
# prefix (D_X, T_X, …) followed by ":" or " —", and (b) the named value is
# canonical (present in ORDINALS), and (c) it differs from what the block says.

_REASONING_OVERRIDE_FIELDS = {
    "dimensionality": ("⊢", r"D_(odot|infty|triangle|wedge)"),
    "topology":       ("⊣", r"T_(odot|boxtimes|bowtie|in|network)\b"),
    "criticality_phase": ("⊙", r"Phi_(c_complex|EP|super|sub|c)\b"),
    "interaction_grammar": ("∋", r"G_(broad|seq|or|and)\b"),
    "polarity":       ("≺", r"P_(pm_sym|pm|sym|psi|asym)\b"),
    "kinetic_character": ("⊤", r"K_(MBL|trap|slow|mod|fast)\b"),
    "protection":     ("⊡", r"Omega_(NA|Z2|Z|0)\b"),
    "chirality":      ("⊥", r"H(0|1|2|_inf)\b"),
}


def _reconcile_with_reasoning(imscription_data: dict, reasoning: str) -> dict:
    """Override imscription_data values where the reasoning explicitly names a different canonical value."""
    if not reasoning or reasoning == "(no reasoning in response)":
        return imscription_data
    result = dict(imscription_data)
    for field, (_, pattern) in _REASONING_OVERRIDE_FIELDS.items():
        matches = re.findall(pattern, reasoning)
        if not matches:
            continue
        # Take the first explicit mention; build back the full value string
        raw = matches[0]
        # Reconstruct the canonical value from the pattern group
        prefix = pattern.split("(")[0]  # e.g. "D_", "T_", "Phi_", "G_", "⊥"
        candidate = prefix + raw
        # Verify it's canonical before overriding
        try:
            from space_search.primitives import ORDINALS, PRIMITIVE_ORDER
            prim_key = {
                "dimensionality": "⊢", "topology": "⊣", "criticality_phase": "⊙",
                "interaction_grammar": "∋", "polarity": "≺", "kinetic_character": "⊤",
                "protection": "⊡", "chirality": "⊥",
            }[field]
            if candidate in ORDINALS[prim_key] and result.get(field) != candidate:
                result[field] = candidate
        except (ImportError, KeyError):
            pass
    return result



# ── Structural validation: canonical slot membership + cross-primitive axioms ─────────
# The axioms were, until now, stated only in the PROMPT — told to the model, enforced by
# nothing. A tuple violating Axiom C sailed through with grounding_status "full" (seen
# live: ⊢=𐑦 with ⊣=𐑥, plus ⊥/⊡ values transposed by the old to_notation slot order).
# This is the code the prose always claimed to be.
#
# Value sets mirror the ordinal scripture (Core.lean ctor order / gen_clay; same table
# crystal_data.py carries). A value outside its slot's set is not a point in the Crystal.
_CANON_VALUES = {
    "dimensionality":   {"𐑛", "𐑨", "𐑼", "𐑦"},
    "topology":         {"𐑡", "𐑰", "𐑥", "𐑶", "𐑸"},
    "recognition_mode": {"𐑩", "𐑑", "𐑽", "𐑾"},
    "polarity":         {"𐑗", "𐑿", "𐑬", "𐑯", "𐑹"},
    "fidelity":         {"𐑱", "𐑞", "𐑐"},
    "kinetic_character":{"𐑘", "𐑤", "𐑧", "𐑪", "𐑺"},
    "granularity":      {"𐑚", "𐑔", "𐑲"},
    "grammar":          {"𐑝", "𐑜", "𐑠", "𐑵"},
    "criticality_phase":{"𐑢", "⊙", "𐑮", "𐑻", "𐑣"},
    "chirality":        {"𐑓", "𐑒", "𐑖", "𐑫"},
    "stoichiometry":    {"𐑙", "𐑕", "𐑳"},
    "protection":       {"𐑷", "𐑴", "𐑭", "𐑟"},
}


def validate_structural(imscription: "Imscription") -> List[str]:
    """Slot membership + Axioms A–D. Returns [] iff the tuple is a point in the Crystal."""
    v = {slot: getattr(imscription, slot).value for slot in _CANON_VALUES}
    errs = [
        f"{slot}={val} not in its value set {sorted(_CANON_VALUES[slot])}"
        for slot, val in v.items() if val not in _CANON_VALUES[slot]
    ]
    if errs:
        return errs  # axioms are meaningless over out-of-set values
    # wool admits BOTH slow kinetics, not just `on`. Core.lean records
    # "wool co-occurs with on" as a TENDENCY and says in the same breath that it
    # is not an axiom because some wool systems have egg, and
    # InfiniteMemoryNeedsSlowKinetics reads `chir = wool → kin = egg ∨ kin = on`.
    # Demanding 𐑪 alone rejected every wool object whose store is slow rather
    # than frozen.
    if v["chirality"] == "𐑫" and v["kinetic_character"] not in {"𐑧", "𐑪"}:
        errs.append(
            f"Axiom A: ⊥=𐑫 requires ⊤ ∈ {{𐑧,𐑪}} (got ⊤={v['kinetic_character']})")
    if v["protection"] in {"𐑴", "𐑭"} and v["chirality"] not in {"𐑖", "𐑫"}:
        errs.append(f"Axiom B: ⊡={v['protection']} requires ⊥ ∈ {{𐑖,𐑫}} (got ⊥={v['chirality']})")
    # Axiom C is ONE-DIRECTIONAL: an imscriptive topology requires imscriptive
    # dimensionality. The biconditional this used to enforce is a stronger claim
    # than the kernel makes — `ImscriptiveTopology` in p4ramill reads
    # `top = are → dim = if'` and says nothing about ⊢=𐑦 with another topology.
    # Requiring co-occurrence rejected tuples the Grammar admits.
    if v["topology"] == "𐑸" and v["dimensionality"] != "𐑦":
        errs.append(f"Axiom C: ⊣=𐑸 requires ⊢=𐑦 (got ⊢={v['dimensionality']})")
    if v["protection"] == "𐑟" and v["dimensionality"] != "𐑦":
        errs.append(f"Axiom D: ⊡=𐑟 requires ⊢=𐑦 (got ⊢={v['dimensionality']})")
    return errs


@dataclass
class ImscriptionGenerationResult:
    """Result of AI-powered imscription generation."""
    imscription: Imscription
    confidence: float  # 0.0-1.0 confidence in primitive assignments
    reasoning: str  # LLM explanation for assignments
    alternatives: List[Imscription] = field(default_factory=list)
    thermodynamic_metrics: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    grounding_status: str = "unverified"  # "full", "partial", "failed", "override", "unverified"
    failed_primitives: List[str] = field(default_factory=list)  # primitives that failed grounding


class GroundingBlockedError(Exception):
    """Raised when registration is blocked due to failed mechanistic grounding."""
    def __init__(self, failed_primitives: List[str]):
        self.failed_primitives = failed_primitives
        super().__init__(
            f"Registration blocked: ungrounded primitives {failed_primitives}. "
            f"Use strict_grounding=False to override, or fix primitive assignments. "
            f"Overrides are logged to the audit trail."
        )


class ImscriptionGeneratorAgent(BaseAgent):
    """
    AjintK agent for automatic imscription generation from chemical descriptions.

    This agent leverages LLM reasoning to:
    1. Parse natural language descriptions of chemical systems
    2. Analyze SMILES strings and molecular structures
    3. Assign all ten primitives based on chemical knowledge
    4. Generate unified notation
    5. Compute thermodynamic efficiency metrics
    6. Register generated imscriptions to the catalog

    Usage:
        from imscrbgrmr.provider_config import build_agent_config
        
        config = build_agent_config(provider="anthropic", model=None)
        agent = ImscriptionGeneratorAgent(config)
        result = await agent.generate_from_description(
            "carboxylic acid dimer with cyclic hydrogen bonding"
        )
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="imscription_generator",
            name="Imscription Generator",
            description="Agent for automatic imscription generation from any self-organizing system description",
            capabilities=[
                "universal_imscription_generation",
                "cross_domain_encoding",
                "primitive_assignment",
                "structural_type_analysis",
                "catalog_registration",
            ],
            config=config,
            persona=(
                "Expert in the Imscriptiveon framework — a universal grammar for encoding "
                "any self-organizing system (molecular, physical, mythological, mathematical, "
                "linguistic, social, or abstract) as a 12-primitive structural coordinate. "
                "You determine the type of a system from its ROLE and BEHAVIOR "
                "in its native domain — not from its physical substrate."
            ),
        )
        # Override provider setup to respect config strictly
        self.provider = self._setup_llm_provider_strict()

    def _setup_llm_provider_strict(self):
        """Setup LLM provider with MODEL_ALIASES resolution and base_url/api_key support.
        
        Supports prefix-syntax models resolved upstream by agents_cli.py.
        MODEL_ALIASES inherited from true_agentic_agent harness.
        """
        from framework.enhanced_llm_provider import get_llm_provider
        
        provider_name = self.config.get("provider", "anthropic")
        model = self.config.get("model", None)
        base_url = self.config.get("base_url", "")
        api_key = self.config.get("api_key", "")
        
        # Handle provider/model format like "deepseek/deepseek-chat"
        if "/" in provider_name:
            parts = provider_name.split("/", 1)
            provider_name = parts[0]
            model = parts[1] if len(parts) > 1 else model
        
        # Model alias resolution (from true_agentic_agent harness)
        MODEL_ALIASES = {
            "claude-opus-4":    "anthropic/claude-opus-4",
            "claude-sonnet-4":  "anthropic/claude-sonnet-4-5",
            "grok-4":           "x-ai/grok-4.3",
            "grok-4.3":         "x-ai/grok-4.3",
            "gpt-4o":           "openai/gpt-4o",
            "o3":               "openai/o3",
            "gemini-2-5-pro":   "google/gemini-2.5-pro-preview-05-06",
            "deepseek-r1":      "deepseek/deepseek-r1",
        }
        if model:
            model = MODEL_ALIASES.get(model, model)
        
        try:
            provider = get_llm_provider(provider_name, model=model)
            # Override base_url / api_key if provided in config (from agents_cli.py resolution)
            if base_url and hasattr(provider, 'base_url'):
                provider.base_url = base_url
            if api_key and hasattr(provider, 'api_key') and api_key != "local":
                provider.api_key = api_key
            return provider
        except ValueError as e:
            raise e

    def get_tools(self) -> List[Dict[str, Any]]:
        """Declare tools available for autonomous imscription generation."""
        return [
            ToolDefinitions.file_read(),
            ToolDefinitions.file_write(),
            ToolDefinitions.json_load(),
            ToolDefinitions.json_save(),
            ToolDefinitions.run_command(),
        ]

    # ------------------------------------------------------------------
    # Guided (step-by-step) generation — one primitive per LLM call
    # ------------------------------------------------------------------

    # Assignment order is NOT canonical display order. The cross-primitive axioms
    # in Core.lean are directed and run backward through the canonical order (Þ
    # determines Ð; Ω determines Ħ; Ð+Þ+Ω determine Φ) — see
    # project_dual_pairs_and_order. Asking in canonical order decides a
    # constrained primitive before its determiner exists in "assigned so far",
    # which is what the post-hoc Axiom-auto-correction below is patching over.
    # Ask by dual pair, pairs ordered by dependency: pair 1 (Þ before Ð, per
    # Axiom C), then pair 6, pair 5, pair 2, then the unconstrained pairs 3, 4.
    # Display order (built from the resulting Imscription's named fields, not
    # from this list's order) stays canonical.
    GUIDED_PRIMITIVES: List[Dict[str, Any]] = [
        {"short": "⊣",  "long": "topology",             "question": "What is the connectivity pattern of influence?",
         "options": [("𐑡","Generic network — connected graph, hub-spoke, mixed connectivity"),
                     ("𐑰","Containment / branched tree — partners enter a container or nested hierarchy"),
                     ("𐑥","Cyclic closure — cyclic interface, figure-8, double-well"),
                     ("𐑶","Fully enclosed — partner cannot exit without distorting the container"),
                     ("𐑸","Scale-collapse — connectivity in which the boundary carries the full bulk content losslessly (requires 𐑦 dimensionality)")]},
        {"short": "⊢",  "long": "dimensionality",      "question": "What is the operating space — the degree of freedom of constraint propagation?",
         "options": [("𐑼","Point-like — local, operates on a single unit"),
                     ("𐑨","Spatial — constraint propagates through an extended 3D arrangement"),
                     ("𐑛","Temporal/iterative — recurs through a closed cycle with a reset step"),
                     ("𐑦","Scale-collapse — the boundary carries the full bulk content losslessly; surface and interior are one register (requires 𐑸 topology)")]},
        {"short": "⊞",  "long": "stoichiometry",        "question": "What is the participation ratio?",
         "options": [("𐑙","Equal symmetric pairing"),
                     ("𐑕","Higher-order symmetric — oligomers, committees"),
                     ("𐑳","Asymmetric — different counts on each side")]},
        {"short": "⊡",  "long": "protection",           "question": "Can the role be continuously deformed away?",
         "options": [("𐑷","No protection — role CAN be continuously deformed to trivial state"),
                     ("𐑴","Z2-protected — requires crossing a Z2 topological boundary to change"),
                     ("𐑭","Integer-winding-protected — stable against perturbations preserving winding invariant"),
                     ("𐑟","Non-Abelian protection — most robust; requires 𐑦 dimensionality")]},
        {"short": "⊙",  "long": "criticality_phase",    "question": "How close is the system to a critical point / threshold?",
         "options": [("𐑢","Subcritical — normal regime, no scale-free behavior"),
                     ("⊙","Critical — at the threshold; scale-free correlations, maximal sensitivity"),
                     ("𐑮","Complex critical — criticality with complex eigenvalues"),
                     ("𐑻","Exceptional point — non-Hermitian degeneracy; amplification/loss asymmetry"),
                     ("𐑣","Supercritical / post-threshold — system has passed through criticality")]},
        {"short": "⊥",  "long": "chirality",            "question": "How persistent is the broken orientational symmetry — memory depth?",
         "options": [("𐑓","Achiral — mirror image accessible; no persistent symmetry breaking"),
                     ("𐑒","Soft chiral — single axis, thermally interconvertible; memory depth 1"),
                     ("𐑖","Persistent chiral — multiple axes, structurally enforced; memory depth n"),
                     ("𐑫","Topological chirality — topology-protected; cannot be undone without global restructuring (implies 𐑪 kinetics)")]},
        {"short": "≻",  "long": "recognition_mode",     "question": "What is the mechanism of interaction / transformation?",
         "options": [("𐑩","Soft association — non-covalent, reversible, analogical similarity"),
                     ("𐑑","Bond formation / structural transformation — irreversible or semi-reversible"),
                     ("𐑽","Transition-state stabilization — lowers barrier without being consumed; adjoint/catalytic"),
                     ("𐑾","Left-right asymmetric / mechanical topology — interlocking, knotting, irreversible handedness")]},
        {"short": "≺",  "long": "polarity",             "question": "What is the directional character of the interface?",
         "options": [("𐑗","No preferred direction; no self-complementarity"),
                     ("𐑿","Signed direction — one accepting OR one donating pole"),
                     ("𐑬","Self-complementary — both donor and acceptor roles present simultaneously"),
                     ("𐑯","Mirror-symmetric — global reflection symmetry (not Frobenius)"),
                     ("𐑹","Special Frobenius — exact Z2 symmetry at criticality; μ∘δ=id PROVABLY exact")]},
        {"short": "⋈",  "long": "fidelity",             "question": "How much information is transmitted per interaction — how reliably does it fire?",
         "options": [("𐑱","Low — probabilistic; many false positives (I_net < 6 bits)"),
                     ("𐑞","Medium — context-dependent; reliable under right conditions (6–9 bits)"),
                     ("𐑐","High — geometry-enforcing; fires with near-certainty (I_net > 9 bits)")]},
        {"short": "⊤",  "long": "kinetic_character",    "question": "What is the barrier to rearrangement — resistance to change?",
         "options": [("𐑘","Low barrier — explores configuration space freely; reversible"),
                     ("𐑤","Moderate barrier — accessible under perturbation"),
                     ("𐑧","High barrier — kinetically frozen; requires external driving to rearrange"),
                     ("𐑪","Metastable — locked in non-ground-state; cannot equilibrate without extraordinary perturbation"),
                     ("𐑺","Many-body localized — disorder-frozen; ergodicity broken by disorder")]},
        {"short": "∈",  "long": "granularity",          "question": "What is the correlation length — how far does one interaction propagate?",
         "options": [("𐑲","Local — single bond/event, no neighbours influenced"),
                     ("𐑚","Mesoscale — propagates through a motif or cluster (~10–1000 units)"),
                     ("𐑔","Global — propagates across the entire system; scale-free")]},
        {"short": "∋",  "long": "interaction_grammar",  "question": "What is the partner selection logic?",
         "options": [("𐑝","Conjunctive — all required partners must be present simultaneously"),
                     ("𐑜","Disjunctive — any partner from a set suffices"),
                     ("𐑠","Sequential — ordered steps; partners engaged in sequence"),
                     ("𐑵","Broad conjunctive — many required partners (>10), cooperative assembly")]},
    ]

    async def generate_guided(
        self,
        description: str,
        name: Optional[str] = None,
        delta_g: Optional[float] = None,
        auto_register: bool = True,
        temperature: Optional[float] = None,
    ) -> "ImscriptionGenerationResult":
        """
        Guided generation: one LLM call per primitive, numbered-choice selection.
        Eliminates hallucinated values — the model picks from an explicit list.
        """
        system = (
            "You are assigning a single primitive in the Imscribing Grammar "
            "(a 12-coordinate universal type system). "
            "You will receive the input description and one primitive to assign. "
            "Pick the best-fit option from the numbered list based on the input's role "
            "and behavior. Resemblance between the input's wording and an option's name or the "
            "grammar's own vocabulary is not evidence; judge the ROLE only. "
            "Reply with ONLY the option number, followed by a dash and one sentence of reasoning. "
            "Do not include any other text."
        )
        assigned: Dict[str, str] = {}
        reasoning_parts: List[str] = []

        for prim in self.GUIDED_PRIMITIVES:
            short = prim["short"]
            options = prim["options"]

            options_text = "\n".join(
                f"  {i+1}. {val}  — {desc}"
                for i, (val, desc) in enumerate(options)
            )
            n = len(options)
            prompt = (
                f"Input: {description}\n\n"
                f"Assigning primitive {short} ({prim['long']}).\n"
                f"Question: {prim['question']}\n\n"
                f"Options:\n{options_text}\n\n"
                f"Primitives assigned so far: {assigned}\n\n"
                f"Reply with ONLY the option number (1–{n}), followed by one sentence of reasoning.\n"
                "Example: \"2 — The system organizes spatially across an extended lattice.\"\n"
                "Do NOT write anything else before the number."
            )

            # The guided pick only needs a number, so a reasoning model burns its budget
            # thinking (null content at a tight cap, minutes at a wide one). Turn reasoning
            # OFF for it. Keep the wide cap as a no-regression floor: if a model ignores the
            # switch and reasons anyway, it still completes (just slower) instead of failing.
            raw = await self.call_llm(prompt=prompt, system=system,
                                      max_tokens=16000,
                                      temperature=0.1 if temperature is None else temperature,
                                      reasoning_off=True)

            # Extract leading integer
            m = re.match(r"\s*(\d+)", raw.strip())
            if m:
                idx = int(m.group(1)) - 1
                idx = max(0, min(idx, len(options) - 1))
            else:
                # Fall back: scan for any canonical value name in the response
                idx = 0
                for i, (val, _) in enumerate(options):
                    if val.lower() in raw.lower():
                        idx = i
                        break

            chosen_val, chosen_desc = options[idx]
            assigned[short] = chosen_val
            # Capture reasoning: everything after the first word/number
            reasoning_line = re.sub(r"^\s*\d+\s*[—\-–]?\s*", "", raw.strip(), count=1)
            reasoning_parts.append(f"{short}={chosen_val}: {reasoning_line.strip()}")

        reasoning = "\n".join(reasoning_parts)

        # Build the imscription from assembled assignments
        imscription_data = {prim["long"]: assigned[prim["short"]] for prim in self.GUIDED_PRIMITIVES}
        imscription_data["name"] = name or _desc_slug(description)

        # Axiom auto-correction: enforce cross-primitive constraints before constructing.
        # Axiom B: 𐑴 or 𐑭 requires chirality >= H_turntwo.
        prot = imscription_data.get("protection", "")
        chir = imscription_data.get("chirality", "")
        _needs_chiral = {"𐑴", "𐑭", "𐑟"}   # ⊡ Z2 / integer / non-Abelian
        _weak_chiral  = {"𐑓", "𐑒"}        # ⊥ achiral / soft
        if prot in _needs_chiral and chir in _weak_chiral:
            import warnings
            warnings.warn(
                f"generate_guided: Axiom B auto-correction — "
                f"protection {prot!r} requires chirality >= 𐑖 but got {chir!r}. "
                f"Downgrading protection to 𐑷 (trivial)."
            )
            imscription_data["protection"] = "𐑷"
            reasoning_parts.append("[Axiom B auto-correction] protection downgraded to 𐑷")
        # 𐑫 (topological chirality) co-occurring with 𐑪 (metastable kinetics) is a
        # STRUCTURAL TENDENCY, not an axiom — Core.lean states this explicitly: "Not an
        # axiom because some wool systems (e.g. proto-languages) have egg." The former
        # auto-correction here rewrote the Grammar's verdict to satisfy a constraint the
        # kernel does not impose. The Grammar's assignment stands as spoken.

        imscription = self._create_imscription_from_data(imscription_data, description, explicit_name=name)

        if delta_g is not None:
            imscription.delta_g = delta_g

        # The guided path IS the gate — its verdict must be structural, not implicit.
        # Clean membership + axioms → "full"; any violation → "failed", never registered.
        structural_errors = validate_structural(imscription)

        if auto_register and not structural_errors and imscription.name not in global_catalog:
            global_catalog.register(imscription)

        return ImscriptionGenerationResult(
            imscription=imscription,
            reasoning=reasoning,
            confidence=1.0,
            alternatives=[],
            grounding_status="failed" if structural_errors else "full",
            failed_primitives=structural_errors,
        )

    async def generate_from_description(
        self,
        description: str,
        name: Optional[str] = None,
        delta_g: Optional[float] = None,
        auto_register: bool = True,
        require_grounding: bool = False,  # NEW: Require mechanistic grounding
        temperature: Optional[float] = None,
    ) -> ImscriptionGenerationResult:
        """
        Generate a imscription from a natural language description.

        Args:
            description: Chemical description (e.g., "carboxylic acid dimer with cyclic H-bonding")
            name: Optional name for the imscription (auto-generated if not provided)
            delta_g: Optional free energy value for thermodynamic analysis
            auto_register: Whether to automatically register to catalog
            require_grounding: Whether to require mechanistic grounding validation

        Returns:
            ImscriptionGenerationResult with generated imscription and analysis
        """
        # Extract mechanistic justifications if grounding requested
                # Otherwise continue without grounding

        # Build the analysis prompt
        prompt = self._build_generation_prompt(description, name)

        # One corrective retry on a bad primitive VALUE (e.g. the model puts a
        # criticality_phase value like ⊙ into the recognition_mode slot). This
        # is not a silent fallback — it's the same real-error-back-to-the-model
        # pattern used elsewhere (numeric-value rejection, MoDoT's PROD prod).
        # A genuinely wrong second attempt still raises; nothing is guessed.
        last_error: Optional[ValueError] = None
        _MAX_CORRECTION_ATTEMPTS = 4
        for correction_attempt in range(_MAX_CORRECTION_ATTEMPTS):
            call_prompt = prompt
            if last_error is not None:
                call_prompt = (
                    f"{prompt}\n\n"
                    f"YOUR PREVIOUS RESPONSE WAS REJECTED BY THE PARSER:\n{last_error}\n"
                    f"Re-read the value_registry table for the field named in that error and "
                    f"emit ONLY a value from ITS row — do not reuse a value that belongs to a "
                    f"different field. Respond with the full corrected JSON object again."
                )
            try:
                raw_response = await self.call_llm(
                    prompt=call_prompt,
                    max_tokens=self.config.get("max_tokens", 4000),
                    temperature=0.3 if temperature is None else temperature,  # Lower temperature for more deterministic output by default
                    system=self._get_system_prompt()
                )
                imscription_data, reasoning, confidence, alternatives = self._parse_llm_response(raw_response)
                imscription = self._create_imscription_from_data(imscription_data, description, explicit_name=name)
                break
            except ValueError as e:
                last_error = e
                if correction_attempt < _MAX_CORRECTION_ATTEMPTS - 1:
                    try:
                        from rich.console import Console
                        Console().print(f"[yellow]attempt {correction_attempt + 1}/{_MAX_CORRECTION_ATTEMPTS} rejected ({e}) — retrying with the parser's error[/yellow]")
                    except Exception:
                        pass
                    continue
                try:
                    from rich.console import Console
                    Console().print(f"[red]LLM API failed after {_MAX_CORRECTION_ATTEMPTS} attempts ({type(e).__name__}): {e}[/red]")
                    Console().print("[red]No fallback — rule-based generation produces unreliable encodings. Fix the API key or provider.[/red]")
                except Exception:
                    pass
                raise
            except Exception as e:
                try:
                    from rich.console import Console
                    Console().print(f"[red]LLM API failed ({type(e).__name__}): {e}[/red]")
                    Console().print("[red]No fallback — rule-based generation produces unreliable encodings. Fix the API key or provider.[/red]")
                except Exception:
                    pass
                raise

        # Compute thermodynamic metrics if delta_g provided
        thermo_metrics = None
        if delta_g is not None:
            try:
                result = compute_eta_CP(imscription, delta_g)
                thermo_metrics = {
                    "delta_g": delta_g,
                    "eta_CP": result.eta_CP,
                    "xi_CP": result.xi_CP,
                    "efficiency_description": result.efficiency_description,
                }
                # Append calibrated I(bits) if available
                try:
                    from imscrbgrmr.information import calibrate_I_pipeline
                    cal = calibrate_I_pipeline()
                    thermo_metrics["I_bits_calibrated"] = {
                        "acid_dimer": cal.acid_dimer_result,
                        "triple_hbond": cal.triple_hbond_result,
                        "proline_cycle": cal.proline_cycle_result,
                        "all_pass": cal.all_pass,
                    }
                except Exception:
                    pass
            except Exception:
                thermo_metrics = {"delta_g": delta_g, "error": "Could not compute metrics"}

        # --- Grounding gate ---
        # Structural validation FIRST: an out-of-set value or an axiom violation is a
        # malformed tuple, and no amount of per-primitive reasoning grounds a point that
        # is not in the Crystal. Overrides everything downstream to "failed".
        structural_errors = validate_structural(imscription)

        # Determine grounding status and failed primitives from grounding_result
        grounding_status = "unverified"
        failed_primitives = []


        # Axiom 6: D_∞ requires a named closed cycle or recurring role — domain-agnostic check
        if imscription.dimensionality == Dimensionality.array:
            reasoning_lower = reasoning.lower()
            # Reset indicators: physical or abstract (narrative turn, logical step, mythological cycle)
            reset_indicators = [
                "reset", "reform", "regenerat", "hydroly", "return", "cycle", "turnover",
                "re-form", "dissipat", "release", "recur", "repeat", "loop", "periodic",
                "iterate", "revolv", "restart", "renew", "regeneration",
            ]
            has_reset = any(kw in reasoning_lower for kw in reset_indicators)
            if not has_reset:
                if "dimensionality" not in failed_primitives:
                    failed_primitives.append("dimensionality (D_∞ assigned but no cycle/recurrence specified)")
                grounding_status = "partial"

        # Axiom 7: T_⋈ requires a named closing bond — check independently
        if imscription.topology == Topology.mime:
            reasoning_lower = reasoning.lower()
            closing_indicators = ["hydrogen bond", "h-bond", "hbond", "coordinat", "covalent",
                                   "close", "ring", "loop", "cycl", "r2_2", "r22", "macrocycle",
                                   "crown", "cryptand", "rotaxane", "caten", "dimer"]
            invalid_indicators = ["linear", " rod", "chain", "axial", "two-ended", "terminus",
                                   "cumulene", "allene"]
            has_invalid = any(kw in reasoning_lower for kw in invalid_indicators)
            has_closing = any(kw in reasoning_lower for kw in closing_indicators)
            if has_invalid or not has_closing:
                if "topology" not in failed_primitives:
                    failed_primitives.append("topology (T_⋈ assigned but no closing bond/interaction named)")
                grounding_status = "partial"

        # Registration block
        strict = require_grounding  # strict_grounding mirrors require_grounding for now
        override = kwargs.get("override_grounding", False) if hasattr(self, "_kwargs") else False
        override_reason = kwargs.get("override_reason", None) if hasattr(self, "_kwargs") else None

        # Structural failure is not overridable and not subject to `strict`: an axiom
        # violation or out-of-set value is a malformed tuple, full stop. The LLM-grounding
        # verdict above is a judgment about reasoning; this is a fact about membership.
        if structural_errors:
            grounding_status = "failed"
            failed_primitives = structural_errors + failed_primitives

        if strict and failed_primitives and not override:
            raise GroundingBlockedError(failed_primitives)

        if strict and failed_primitives and override:
            # Log to audit trail in metadata
            grounding_status = "override"
            import datetime
            audit_entry = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "failed_primitives": failed_primitives,
                "override_reason": override_reason or "No reason provided",
                "provider": self.config.get("provider"),
                "model": self.config.get("model"),
            }
            # Append to a persistent audit log if catalog supports it
            try:
                global_catalog.log_grounding_override(imscription.name, audit_entry)
            except AttributeError:
                pass  # Catalog doesn't support audit logging yet — Fix 1b for Qwen

        # Register to catalog if requested
        if auto_register and imscription.name not in global_catalog:
            # Tag catalog entry with grounding status
            imscription.metadata["grounding_status"] = grounding_status
            imscription.metadata["failed_primitives"] = failed_primitives
            if failed_primitives:
                imscription.metadata["flagged_for_review"] = True
            global_catalog.register(imscription)

        # Build result metadata with grounding info
        metadata = {
            "input_description": description,
            "provider": self.config.get("provider"),
            "model": self.config.get("model"),
        }


        return ImscriptionGenerationResult(
            imscription=imscription,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            thermodynamic_metrics=thermo_metrics,
            metadata=metadata,
            grounding_status=grounding_status,
            failed_primitives=failed_primitives,
        )


    async def generate_batch(
        self,
        descriptions: List[str],
        names: Optional[List[str]] = None,
        auto_register: bool = True,
    ) -> List[ImscriptionGenerationResult]:
        """
        Generate multiple imscriptions in batch.

        Args:
            descriptions: List of chemical descriptions
            names: Optional list of names (must match length of descriptions)
            auto_register: Whether to automatically register to catalog

        Returns:
            List of ImscriptionGenerationResult objects
        """
        if names is None:
            names = [None] * len(descriptions)

        results = []
        for desc, name in zip(descriptions, names):
            try:
                result = await self.generate_from_description(desc, name, auto_register=auto_register)
                results.append(result)
            except Exception as e:
                results.append(ImscriptionGenerationResult(
                    imscription=None,
                    confidence=0.0,
                    reasoning=f"Error: {str(e)}",
                    metadata={"error": str(e)}
                ))

        return results

    def _get_system_prompt(self) -> str:
        """Get the domain-agnostic system prompt for imscription generation."""
        return """<role>
You are an expert in the Imscriptiveon framework — a universal grammar that assigns a 12-primitive coordinate ⟨D; T; R; P; F; K; G; ∈; ⊙; H; S; ⊡⟩ to ANY self-organizing system. The grammar is domain-agnostic: it encodes molecules, physical fields, mythological archetypes, mathematical structures, linguistic patterns, social dynamics, and abstract conceptual systems with equal rigor.

The 12 primitives are coordinates in structural TYPE SPACE. They describe HOW a system organizes — not what it is made of. A mythological death-principle, a Kitaev chain, and a carboxylic acid dimer may share the same type. Your task is to identify which type an input instantiates.

**FUNDAMENTAL RULE:** Every input has a type. There is no such thing as a "non-encodable" input. If an entity exists in any domain and has any discernible structure or role, it can be encoded. Assigning trivial placeholder defaults with 0% confidence is a FAILURE — it means you refused to reason about structure.

**CONFIDENCE PROTOCOL VIOLATION:** Returning `"confidence": 0` (or any value ≤ 0.05) for a non-empty input is forbidden. It signals passive refusal. You MUST assign a confidence ≥ 0.1 and include non-empty reasoning. If genuinely uncertain, assign confidence 0.2–0.4 and explain why in the reasoning field. An empty `"reasoning"` field is also a PROTOCOL VIOLATION — every assignment requires at least a one-phrase justification per primitive.
</role>

<task>
Analyze the provided system and assign all twelve primitives from first principles. For each primitive, reason from the entity's STRUCTURAL ROLE in its native domain:
- What is the "operating space"? (D)
- How is its influence connected? (T)
- What drives interaction/recognition? (R)
- Is its interface symmetric or directed? (P)
- How reliably/precisely does it act? (F)
- How resistant to change is its state? (K)
- How far does one act propagate? (G)
- How does it select co-participants? (∈)
- Is it near a threshold/criticality? (<)
- Does it break symmetry persistently? (H)
- What is the participation ratio? (S)
- Is its role topologically protected? (⊡)
</task>

<primitives>
**D — Dimensionality** (operating space of constraint propagation):
- `𐑛`: Point-like — constraint is local, operates on a single unit (molecule, particle, individual entity). *Chem: molecular complex. Physics: point particle. Narrative: a singular act.*
- `𐑨`: Spatial — constraint propagates through an extended 3D arrangement. *Chem: crystal lattice, bulk material. Social: institutional structure. Math: manifold.*
- `𐑼`: Temporal/iterative — constraint recurs through a closed cycle with a specifiable reset step. *Chem: catalytic cycle. Narrative: a recurring mythological role. Math: dynamical system.*
- `𐑦`: Scale-collapse — a lower-dimensional surface carries the full content of a higher-dimensional interior, losslessly. **Axiom C: 𐑸 REQUIRES 𐑦 — an imscriptive topology needs imscriptive dimensionality; 𐑦 itself is free to pair with any topology.** *Physics: black hole horizon. Math: quotient construction. Narrative: an archetype whose every instantiation carries the whole.* Assign it for the system's structural ROLE only — never because the input's wording resembles this option's name or any grammar vocabulary.

**T — Topology** (connectivity pattern of influence):
- `𐑡`: Generic network — influence propagates through a connected graph. Use for: general mixed connectivity, hub-spoke, hexagonal networks, interpenetrating nets, any topology not fitting the specific types below.
- `𐑰`: Containment / branched tree — partners enter a container or are addressed in a directed hierarchy. *Chem: open cavity, host-guest, linear chain. Math: tree, DAG, ZFC cumulative hierarchy.*
- `𐑥`: Cyclic closure — two (or more) partners form a cyclic interface; figure-8 or double-well. *Chem: catalytic cycle, macrocycle, torus. Math: loop space.*
- `𐑶`: Fully enclosed / type-hierarchical — partner cannot exit without distorting the container; bounded closed topology. *Chem: cage complex, cryptand. Math: classical proof assistant.*
- `𐑸`: Scale-collapse — non-local boundary-bulk coupling; the boundary carries the full bulk content losslessly. **Axiom C: 𐑸 REQUIRES 𐑦.** *Physics: AdS/CFT, black hole. Math: quotient/IUT.* Assign for structural ROLE only, never by resemblance between the input's wording and this option's name.

**R — Recognition mode** (mechanism of interaction/transformation):
- `𐑩`: Soft association — non-covalent, reversible binding (van der Waals, H-bond, electrostatic, narrative resonance, analogical similarity).
- `𐑑`: Bond formation / structural transformation — irreversible or semi-reversible (covalent bond, institutional founding, mathematical construction).
- `𐑽`: Transition-state stabilization / adjoint — lowers barrier for a transformation without being consumed; conformational gating; enables state change in partners.
- `𐑾`: Left-right asymmetric / mechanical topology — interaction mediated by mechanical topology (interlocking, knotting, narrative entrapment, irreversible handedness).

**P — Polarity** (directional character of the interface):
- `𐑗`: No preferred direction; symmetric across all relevant reflections, or fully directed with no self-complementarity.
- `𐑿`: Signed direction — one accepting/receiving pole or one donating/acting pole (electrophile, nucleophile, adversarial role).
- `𐑬`: Self-complementary — both donor and acceptor roles present simultaneously.
- `𐑯`: Mirror-symmetric — the interface has a global reflection symmetry (not Frobenius; both roles present but not special).
- `𐑹`: Special Frobenius — exact Z2 symmetry at criticality; assign ONLY when μ∘δ=id is provably exact.

**F — Fidelity** (information transmitted per interaction; how reliably/precisely does it fire?):
- `𐑐`: High — geometry-enforcing, dominant; fires with near-certainty given the right partner. I_net > 9 bits. *Death recognizes its target with certainty. A lock-and-key.*
- `𐑞`: Medium — context-dependent; reliable under the right conditions but not geometry-enforcing. I_net 6–9 bits.
- `𐑱`: Low — probabilistic; fires unreliably, many false positives. I_net < 6 bits.
**F ≠ "strength." A weak but specific interaction is 𐑐. A strong but promiscuous one is 𐑱.**

**K — Kinetic character** (barrier to rearrangement / resistance to change):
- `𐑘`: Low barrier — explores configuration space freely; reversible on relevant timescales.
- `𐑤`: Moderate barrier — accessible under perturbation.
- `𐑧`: High barrier — kinetically frozen; requires external driving to rearrange.
- `𐑪`: Metastable — locked in a state that is NOT the thermodynamic ground state; cannot reach equilibrium without extraordinary perturbation.
- `𐑺`: Many-body localized — disorder-frozen; ergodicity broken by disorder (not order).
**𐑫 implies ⊤=𐑪 (topology-protected chirality cannot be undone without global restructuring).**

**G — Granularity** (correlation length: how far does one interaction propagate?):
- `𐑚`: Local — single bond/event, no neighbours influenced.
- `𐑔`: Mesoscale — propagates through a motif or cluster (~10–1000 units).
- `𐑲`: Global — propagates across the entire system; divergent correlation length; scale-free.

**∈ — Interaction grammar** (partner selection logic):
- `𐑝`: Conjunctive — all required partners must be present simultaneously.
- `𐑜`: Disjunctive — any partner from a set suffices.
- `𐑠`: Sequential — ordered steps; partners engaged in sequence.
- `𐑵`: Broad conjunctive — many required partners (>10), cooperative assembly.

**< — Criticality** (proximity to a critical point/threshold):
- `𐑢`: Subcritical — normal regime, no scale-free behavior.
- `⊙`: Critical — at the threshold; scale-free correlations, 𐑲 and ⊙ co-occur naturally.
- `𐑮`: Complex critical — criticality with complex eigenvalues (exceptional-point physics).
- `𐑻`: Exceptional point — non-Hermitian degeneracy; amplification/loss asymmetry.
- `𐑣`: Supercritical / post-threshold — system has passed through criticality into the ordered phase.

**H — Chirality / chirality** (persistence of broken orientational symmetry; memory depth):
- `𐑓`: Achiral — mirror image accessible; no persistent symmetry breaking.
- `𐑒`: Soft chiral — single axis, thermally interconvertible; memory depth 1.
- `𐑖`: Persistent chiral — multiple axes, structurally enforced; memory depth n. Assign for: amino acids, DNA, enantioselective catalysts, narrative roles with fixed handedness.
- `𐑫`: Topological chirality — topology-protected; cannot be undone without global restructuring. **Implies ⊤=𐑪.** Assign for: knotted topologies, roles that are irreversible by construction (death in many mythological systems).

**S — Stoichiometry** (participation ratio):
- `𐑙`: Equal symmetric pairing (1:1).
- `𐑕`: Higher-order symmetric, n:n (oligomers, committees).
- `𐑳`: Asymmetric, n:m — different counts on each side.

**⊡ — Topological protection** (can the role be continuously deformed away?):
- `𐑷`: No protection — trivial; the role CAN be continuously deformed to a trivial state. Default for most systems without explicit topological structure.
- `𐑴`: Z2-protected — requires crossing a Z2 topological boundary to change; binary, global protection.
- `𐑭`: Integer-winding-protected — associated with a conserved winding number; the role is stable against perturbations that preserve the winding invariant.
- `𐑟`: Non-Abelian protection — the most robust; requires 𐑦.
**For abstract/narrative systems: ⊡ encodes whether the structural ROLE can be continuously interpolated to its absence (𐑷) or whether the system's topology forces the role to persist (𐑭, 𐑴). A death-principle in a cosmological system with a fixed winding structure may be 𐑭.**

**MANDATORY AXIOMS — violating these causes a parse error:**
- **Axiom A**: `𐑫` REQUIRES `⊤=𐑪`. If you assign 𐑫, you MUST also assign ⊤=𐑪. 𐑫 (topological chirality) means the symmetry cannot be undone without global restructuring — this IS 𐑪. A fast-exchanging (𐑘) system cannot be topologically chiral.
- **Axiom B**: `𐑴` or `𐑭` REQUIRES `𐑖` or `𐑫` (chirality >= 𐑖).
- **Axiom C**: `𐑦` REQUIRES `𐑸` (and vice versa). They always co-occur.
- **Axiom D**: `𐑟` REQUIRES `𐑦`.
</primitives>

<decision_procedure>
**DETERMINISTIC ENCODING — apply primitives in this exact order:**

Each step constrains what remains. Do NOT assign all primitives simultaneously from a vague overall impression.

  [1] D  → degrees of freedom: point → 𐑛; finite surface → 𐑨; infinite-dim field → 𐑼; self-written state-space → 𐑦
  [2] T  → connectivity shape: graph → 𐑡; containment/nested → 𐑰; crossing point → 𐑥; irreducible product → 𐑶; self-encoding topology → 𐑸
  [3] R  → coupling direction: supervenience / soft association → 𐑩; functorial morphisms / bond formation → 𐑑; adjoint pair (one-way) → 𐑽; bidirectional mutual determination → 𐑾
  [4] P  → symmetry: none → 𐑗; quantum superposition → 𐑿; one Z₂ symmetry → 𐑬; all symmetries → 𐑯; μ∘δ=id exactly at ⊙ (Frobenius-special) → 𐑹
  [5] F  → physical regime: classical → 𐑱; thermal/noisy → 𐑞; quantum coherence essential → 𐑐
  [6] K  → relaxation: driven (τ≪T_obs) → 𐑘; visible dynamics (τ∼T_obs) → 𐑤; frozen (τ≫T_obs) → 𐑧; trapped ordered → 𐑪; trapped disordered → 𐑺
  [7] G  → range: nearest-neighbor → 𐑚; collective/emergent → 𐑔; long-range/universal → 𐑲
  [8] ∈  → composition logic: all-simultaneous → 𐑝; any-sufficient → 𐑜; ordered steps → 𐑠; one-to-all broadcast → 𐑵
  [9] <  → criticality: no power-laws → 𐑢; power-law divergence, maximal sensitivity → ⊙; complex-plane critical → 𐑮; non-Hermitian degeneracy → 𐑻; runaway/chaotic → 𐑣
  [10] H → Markov order: n=0 (memoryless) → 𐑓; n=1 → 𐑒; n=2 → 𐑖; no finite n → 𐑫 (requires ⊤=𐑪)
  [11] S → component types: one type/one instance → 𐑙; many identical → 𐑕; multiple distinct types → 𐑳
  [12] ⊡ → topological invariant: none → 𐑷; Z₂ parity → 𐑴 (requires 𐑖+); integer winding → 𐑭 (requires D≥𐑼); non-Abelian braiding → 𐑟 (requires 𐑦)

**INTERDEPENDENCE CONSTRAINTS (verify after assignment):**
- D-⊡: 𐑴 needs D≥𐑨; 𐑭 needs D≥𐑼; 𐑟 needs 𐑦
- K-<: ⊙ + ⊤=𐑧 = critical deep structure (gravity, language, meditation); 𐑻 + ⊤=𐑘 = runaway decay
- 𐑹 requires μ∘δ=id to hold exactly — decompose then recompose returns identity. Assign ONLY when this is provably true, not just approximately true.
- Tier verification: ⊙ + 𐑹 → O_∞; ⊙ + 𐑷 → O₁; ⊙ + Omega≠0 + D∈{𐑛,𐑨,𐑦} → O₂; ⊙ + Omega≠0 + 𐑼 → O₂†
</decision_procedure>

<domain_guide>
**How to reason about any input domain:**

*Physical/molecular systems*: Ground each primitive in energy barriers (K), information content (F), correlation lengths (G), and topological connectivity (T). Cite the specific mechanism.

*Abstract, symbolic, or mythological entities* (archetypes, angels, narrative roles, cultural forces): The entity's primitives are determined by its FUNCTIONAL ROLE in its native structural system (the mythology, narrative, cosmology, or text). Ask: In the system where this entity operates, what type does it instantiate?
- D: Does it operate at a single locus (𐑛), organize spatial structure (𐑨), recur cyclically (𐑼), or imscriptively encode the system it inhabits (𐑦)?
- T: What is the topology of its influence network?
- R: How does it "recognize" or affect its participants? By soft association? By transformation? By catalysis? By mechanical entrapment?
- F: How precisely/reliably does it act? A death-principle that ALWAYS kills its target is 𐑐. A luck-spirit that sometimes helps is 𐑱.
- K: How resistant is its role to change? Can it be "talked out of" its function (𐑘)? Or is its role frozen by the structure of the narrative (𐑧/𐑪)?
- G: Does it affect only its immediate contact, a local region, or the entire system?
- <: Does it operate at a threshold — a point of maximum sensitivity between two states?
- H: Is the role chiral — i.e., does the entity's "handedness" (adversarial vs. beneficent, active vs. passive) persist and cannot be mirrored?
- ⊡: Is the role topologically required by the structure of the system, or could it be continuously deformed away?

*Mathematical structures*: The "operating space" is the mathematical domain; 𐑦 for quotient/boundary constructions; T encodes the graph/orbit topology; R encodes the morphism type; ⊡ encodes homotopy class.

*Social/linguistic systems*: G encodes spread of influence; K encodes institutional inertia; < encodes whether the system is near a phase transition (tipping point); T encodes the network topology.

**EXAMPLE — Samael (שָׂמָאֵל, adversarial angel of death, Kabbalistic tradition):**
In its role within Jewish cosmology, Samael is:
- 𐑦 + 𐑸: imscriptive — his presence at any point implies constraint across all mortality; the boundary (death) encodes the bulk (life's structure). Note: 𐑦 requires 𐑸 (Axiom C).
- 𐑡 is an alternative if 𐑦 is not assigned (see alternative below)
- 𐑽: catalyzes the life→death transition without being consumed (adjoint/transition-state)
- 𐑿: the negating/adversarial pole of the cosmic polarity (signed direction)
- ⋈=𐑐: death is geometry-enforcing — when it fires, it fires with certainty on its target
- ⊤=𐑪: the death-state is a kinetic trap; return requires extraordinary intervention (resurrection)
- 𐑲: correlation length is global — his influence is correlated across all mortal systems
- ∋=𐑜: any mortal is a valid partner (disjunctive)
- ⊙: he IS the critical threshold between life and non-life
- 𐑫: the adversarial role is topology-protected — it cannot be continuously deformed to its inverse (blessing/life)
- ⊞=𐑳: one principle → many mortals
- 𐑭: integer-winding protected — the adversarial principle has a conserved topological charge in the Kabbalistic sefirotic structure (Geburah/Din as the "other side")
→ ⟨𐑦𐑸𐑽𐑿𐑐𐑪𐑲𐑜⊙𐑫𐑳𐑭⟩
This is a non-trivial, non-default encoding reached by structural reasoning, not template matching.
</domain_guide>

<value_registry>
**MANDATORY OUTPUT VALUE TABLE — copy these strings VERBATIM into your JSON. Do NOT invent variants or substitute characters. Every valid value below is a single Shavian glyph or a single plain-English word — nothing else resolves. The parser accepts ONLY the canonical value shown in each row .**

| Field               | Valid output strings (pick exactly one — glyph or name, not both) |
|---------------------|-----------------------------------------|
| dimensionality      | `𐑛` dead · `𐑨` ash · `𐑼` array · `𐑦` if_ |
| topology            | `𐑡` judge · `𐑰` eat · `𐑥` mime · `𐑶` oil · `𐑸` are |
| recognition_mode    | `𐑩` ado · `𐑑` tot · `𐑽` ear · `𐑾` ian |
| polarity            | `𐑗` church · `𐑿` yew · `𐑬` out · `𐑯` nun · `𐑹` or_ |
| fidelity            | `𐑱` age · `𐑞` they · `𐑐` peep |
| kinetic_character   | `𐑘` yea · `𐑤` loll · `𐑧` egg · `𐑪` on · `𐑺` air |
| granularity         | `𐑚` bib · `𐑔` thigh · `𐑲` ice |
| interaction_grammar | `𐑝` vow · `𐑜` gag · `𐑠` measure · `𐑵` ooze |
| criticality_phase   | `𐑢` woe · `⊙` monad · `𐑮` roar · `𐑻` err · `𐑣` haha |
| chirality           | `𐑓` fee · `𐑒` kick · `𐑖` sure · `𐑫` wool |
| stoichiometry       | `𐑙` one-to-one · `𐑕` n-to-n · `𐑳` n-to-m |
| protection          | `𐑷` awe · `𐑴` oak · `𐑭` ah · `𐑟` zoo |

These are the SAME 12 primitives and values described conceptually in `<primitives>` and `<domain_guide>` above — use the plain glyph or name shown there directly, nothing needs translating. Every valid value in this table is either a single Shavian glyph (one character, e.g. `𐑛`) or a single lowercase English word (e.g. `dead`) — never both together, never with an underscore, never with any suffix attached.
</value_registry>

<output_format>
**Output the JSON block FIRST, then the reasoning.** Do not pre-reason before the JSON — the reasoning field inside the JSON is the correct place for your per-primitive justification. Pre-reasoning before the JSON causes your encoding and your explanation to diverge, which is a hard error.

Respond with a single JSON object with this EXACT structure. The outer key MUST be `"imscription"`. Do NOT use `"primitive_analysis"`, `"imscription_encoding"`, or any other outer key. **Values MUST come from the value_registry table above — do not use any other strings.**
```json
{
  "imscription": {
    "dimensionality": "𐑛",
    "topology": "𐑥",
    "recognition_mode": "𐑩",
    "polarity": "𐑬",
    "fidelity": "𐑱",
    "kinetic_character": "𐑤",
    "granularity": "𐑚",
    "interaction_grammar": "𐑝",
    "criticality_phase": "𐑢",
    "chirality": "𐑓",
    "stoichiometry": "𐑙",
    "protection": "𐑷"
  },
  "confidence": 0.85,
  "reasoning": "Per-primitive reasoning that exactly matches the values above — e.g. 'dead: operates at single-locus scale. mime: cyclic interface...'",
  "alternatives": [{"dimensionality": "𐑛", "topology": "𐑰", "recognition_mode": "𐑩", "polarity": "𐑬", "fidelity": "𐑞", "kinetic_character": "𐑘", "granularity": "𐑚", "interaction_grammar": "𐑜", "criticality_phase": "𐑢", "chirality": "𐑓", "stoichiometry": "𐑳", "protection": "𐑷"}]
}
```
Use only values from the value_registry table. The `reasoning` field MUST reference the same primitive values that appear in the `imscription` block — writing a different glyph/name in reasoning than in the JSON for the same primitive is a contradiction and the output is invalid. Confidence must be > 0 unless the input is genuinely semantically empty. Keep reasoning CONCISE — one short phrase per primitive (e.g. "dead: single-locus molecular complex"), total reasoning under 200 words.
</output_format>
"""

    def _build_generation_prompt(self, description: str, name: Optional[str]) -> str:
        """Build the prompt for imscription generation from any description."""
        name_instruction = f"Use '{name}' as the name." if name else "Generate an appropriate name."
        return f"""Input: {description}

{name_instruction}

Work through all 12 primitives (D, T, R, P, F, K, G, ∈, ⊙, H, S, ⊡) by reasoning about the role of this entity in its native domain. For each primitive, state what you are inferring and why. If the input is from a non-physical domain (mythology, mathematics, language, social structures), apply the domain_guide reasoning: identify the entity's functional role and map it to type space.

CRITICAL FORMAT REQUIREMENT: Every primitive value in the JSON MUST be an exact string token from the allowed list (e.g. "𐑛", "𐑥", "⊙"). Do NOT use numbers, floats, scores, or continuous values — the grammar is categorical, not continuous. A response containing any numeric primitive value (0.3, 1.0, etc.) is a format error and will be rejected.

Respond with the JSON object specified in output_format. Outer key must be "imscription". Confidence must reflect genuine uncertainty, not refusal to encode."""


    @staticmethod
    def _has_string_primitive_values(d: Dict[str, Any]) -> bool:
        """Return True iff every non-name value in d is a non-empty string."""
        for k, v in d.items():
            if k == "name":
                continue
            if not isinstance(v, str) or not v.strip():
                return False
        return bool(d)

    def _parse_llm_response(
        self,
        response: str
    ) -> Tuple[Dict[str, str], str, float, List[Dict[str, str]]]:
        """Parse the LLM response into imscription data and metadata.

        Raises ValueError if no JSON block is found or the imscription dict is empty.
        No silent defaults — a missing/unparseable response is an error.
        """
        json_blocks = self.extract_json_blocks(response)

        if not json_blocks:
            raise ValueError(
                f"Model returned no parseable JSON.\n"
                f"Raw response (first 500 chars):\n{response[:500]}"
            )

        # Try each block in order; pick first one whose imscription values are strings.
        # Some models emit a numeric-score block first, then a categorical block.
        data = None
        for block in json_blocks:
            candidate = block.get("imscription", {})
            if candidate and isinstance(candidate, dict) and self._has_string_primitive_values(candidate):
                data = block
                break
        if data is None:
            data = json_blocks[0]  # fall through to existing adapters / error path

        imscription_data = data.get("imscription", {})

        # Schema adapter: model used "imscription" wrapper but nested primitives under a
        # "primitives" sub-key instead of at the top level.
        # e.g. {"imscription": {"name": ..., "primitives": {"⊢": ...}, "confidence": ...}}
        if imscription_data and not self._has_string_primitive_values(imscription_data):
            inner = imscription_data.get("primitives")
            if isinstance(inner, dict):
                _key_map = {
                    "⊢": "dimensionality", "⊣": "topology", "≻": "recognition_mode",
                    "⋈": "fidelity", "⊤": "kinetic_character",
                    "∈": "granularity", "∋": "interaction_grammar",
                    "⊙": "criticality_phase", "⊥": "chirality",
                    "⊞": "stoichiometry", "⊡": "protection",
                    "D": "dimensionality", "T": "topology", "R": "recognition_mode",
                    "P": "polarity", "F": "fidelity", "K": "kinetic_character",
                    "G": "granularity", "H": "chirality", "S": "stoichiometry",
                    "W": "protection",
                    "≺": "polarity",
                }
                lifted: Dict[str, Any] = {"name": imscription_data.get("name", "")}
                for k, v in inner.items():
                    canon = _key_map.get(k, k)
                    lifted[canon] = v.get("value", v) if isinstance(v, dict) else v
                # ∈/< ambiguity resolution: some models use ∈ for interaction_grammar
                # (confusing ∈ with ∋) and < for criticality_phase (confusing < with ⊙).
                # When BOTH the ASCII key and the Shavian glyph are present in the
                # original inner dict, the glyph is reassigned to the OTHER primitive.
                if "G" in inner and "∈" in inner:
                    lifted["interaction_grammar"] = inner["∈"]
                    if isinstance(lifted["interaction_grammar"], dict):
                        lifted["interaction_grammar"] = lifted["interaction_grammar"].get("value", "")
                    lifted["granularity"] = inner["G"]
                    if isinstance(lifted["granularity"], dict):
                        lifted["granularity"] = lifted["granularity"].get("value", "")
                if "P" in inner and "≺" in inner:
                    lifted["criticality_phase"] = inner["≺"]
                    if isinstance(lifted["criticality_phase"], dict):
                        lifted["criticality_phase"] = lifted["criticality_phase"].get("value", "")
                    lifted["polarity"] = inner["P"]
                    if isinstance(lifted["polarity"], dict):
                        lifted["polarity"] = lifted["polarity"].get("value", "")
                imscription_data = lifted

        # Schema adapter: some models (e.g. Grok) use "primitive_analysis" instead of "imscription"
        if not imscription_data:
            pa = data.get("primitive_analysis")
            if isinstance(pa, dict):
                # Remap abbreviated keys to canonical field names if needed
                _key_map = {
                    "⊢": "dimensionality", "⊣": "topology", "≻": "recognition_mode",
                    "⋈": "fidelity", "⊤": "kinetic_character",
                    "∈": "granularity", "∋": "interaction_grammar",
                    "⊙": "criticality_phase", "⊥": "chirality",
                    "⊞": "stoichiometry", "⊡": "protection",
                    "D": "dimensionality", "T": "topology", "R": "recognition_mode",
                    "P": "polarity", "F": "fidelity", "K": "kinetic_character",
                    "G": "granularity", "H": "chirality", "S": "stoichiometry",
                    "W": "protection",
                    "≺": "polarity",
                }
                adapted: Dict[str, Any] = {}
                for k, v in pa.items():
                    canon = _key_map.get(k, k)
                    # value may be a nested dict with a "value" key
                    adapted[canon] = v.get("value", v) if isinstance(v, dict) else v
                if adapted:
                    imscription_data = adapted

        # Schema adapter: some models use "primitives" as the top-level key
        if not imscription_data:
            prim = data.get("primitives")
            if isinstance(prim, dict):
                _key_map = {
                    "⊢": "dimensionality", "⊣": "topology", "≻": "recognition_mode",
                    "⋈": "fidelity", "⊤": "kinetic_character",
                    "∈": "granularity", "∋": "interaction_grammar",
                    "⊙": "criticality_phase", "⊥": "chirality",
                    "⊞": "stoichiometry", "⊡": "protection",
                    "D": "dimensionality", "T": "topology", "R": "recognition_mode",
                    "P": "polarity", "F": "fidelity", "K": "kinetic_character",
                    "G": "granularity", "H": "chirality", "S": "stoichiometry",
                    "W": "protection",
                    "≺": "polarity",
                }
                adapted: Dict[str, Any] = {}
                for k, v in prim.items():
                    canon = _key_map.get(k, k)
                    adapted[canon] = v.get("value", v) if isinstance(v, dict) else v
                if adapted:
                    imscription_data = adapted

        if not imscription_data:
            raise ValueError(
                f"JSON found but missing 'imscription' key.\n"
                f"Keys present: {list(data.keys())}\n"
                f"Raw response (first 500 chars):\n{response[:500]}"
            )

        reasoning = data.get("reasoning") or "(no reasoning in response)"
        confidence = data.get("confidence")
        if not isinstance(confidence, (int, float)):
            confidence = None  # caller will display as unknown
        alternatives = data.get("alternatives") or []
        if not isinstance(alternatives, list):
            alternatives = []

        return imscription_data, reasoning, float(confidence) if confidence is not None else 0.0, alternatives

    # Canonical short-form keys returned by models using grammar notation
    _SHORT_TO_LONG: Dict[str, str] = {
        # Shavian glyph keys (unambiguous)
        "⊢": "dimensionality",    "⊣": "topology",
        "≻": "recognition_mode",   "⋈": "fidelity",
        "⊤": "kinetic_character",  "∈": "granularity",
        "∋": "interaction_grammar","⊙": "criticality_phase",
        "⊥": "chirality",          "⊞": "stoichiometry",
        "⊡": "protection",
        # ASCII single-letter fallbacks (models frequently return these)
        "D": "dimensionality",     "T": "topology",
        "R": "recognition_mode",   "P": "polarity",
        "F": "fidelity",           "K": "kinetic_character",
        "G": "granularity",        "H": "chirality",
        "S": "stoichiometry",      "W": "protection",
        # < is ambiguous: when both P (ASCII) and < (glyph) are present,
        # P→polarity wins; <→criticality_phase resolved in adapter logic.
        "≺": "polarity",
    }

    # Legacy prompt notation → from_symbol()-compatible canonical values.

    def _create_imscription_from_data(
        self,
        data: Dict[str, str],
        description: str,
        explicit_name: Optional[str] = None,
    ) -> Imscription:
        """Create a Imscription object from parsed data.

        Extended to support ten primitives: D, T, R, P, F, K, G, ∈, <, S
        """
        # Normalize short-form keys (D, T, ∈, …) to long-form, and unwrap nested
        # {"value": "...", "reasoning": "..."} dicts some models return per primitive
        normalized: Dict[str, str] = {}
        for k, v in data.items():
            canon = self._SHORT_TO_LONG.get(k, k)
            normalized[canon] = v.get("value", v) if isinstance(v, dict) else v
        data = normalized

        # Map string values to enum members — no defaults; missing keys raise KeyError
        _required = ["dimensionality", "topology", "recognition_mode", "polarity",
                     "fidelity", "kinetic_character", "granularity", "interaction_grammar"]
        # Detect wrong-schema responses (e.g. numeric scores instead of string values)
        numeric = {k: data[k] for k in _required if k in data and isinstance(data[k], (int, float))}
        if numeric:
            raise ValueError(
                f"Model returned numeric values for primitives instead of categorical strings.\n"
                f"Numeric keys: {numeric}\n"
                f"Expected strings like '𐑛', '𐑥', etc.\n"
                f"Full normalized data: {data}"
            )

        missing = [k for k in _required if not data.get(k)]
        if missing:
            missing_vals = {k: repr(data.get(k)) for k in missing}
            raise ValueError(
                f"Model response missing required primitive(s): {missing}\n"
                f"Values for missing keys: {missing_vals}\n"
                f"Full normalized data: {data}"
            )

        dimensionality    = Dimensionality.from_symbol(data["dimensionality"])
        topology          = Topology.from_symbol(data["topology"])
        recognition_mode  = RecognitionMode.from_symbol(data["recognition_mode"])
        polarity          = Polarity.from_symbol(data["polarity"])
        fidelity          = Fidelity.from_symbol(data["fidelity"])
        kinetic_character = KineticCharacter.from_symbol(data["kinetic_character"])
        granularity       = Granularity.from_symbol(data["granularity"])
        interaction_grammar = InteractionGrammar.from_symbol(data["interaction_grammar"])

        # Criticality phase — required
        if not data.get("criticality_phase"):
            raise ValueError("Model response missing 'criticality_phase'.")
        criticality_phase = CriticalityPhase.from_symbol(data["criticality_phase"])

        # Stoichiometry — required
        if not data.get("stoichiometry"):
            raise ValueError("Model response missing 'stoichiometry'.")
        stoichiometry = Stoichiometry.from_symbol(data["stoichiometry"])

        # Chirality — required
        if not data.get("chirality"):
            raise ValueError("Model response missing 'chirality'.")
        chirality = Chirality.from_symbol(data["chirality"])

        # Topological protection — required
        if not data.get("protection"):
            raise ValueError("Model response missing 'protection' (𐑷 / 𐑴 / 𐑭 / 𐑟).")
        protection = Protection.from_symbol(data["protection"])

        # Explicit name wins over LLM-generated name; sanitize LLM bleed otherwise
        if explicit_name:
            name = explicit_name.strip()
        else:
            raw_name = data.get("name") or _desc_slug(description)
            name = raw_name.split("\n")[0].strip().replace(" ", "_")
            if not name:
                name = _desc_slug(description)

        import imscrbgrmr.models as _m
        _saved_enforce = _m._ENFORCE_AXIOMS
        _m._ENFORCE_AXIOMS = False
        try:
          return Imscription(
            name=name,
            dimensionality=dimensionality,
            topology=topology,
            recognition_mode=recognition_mode,
            polarity=polarity,
            fidelity=fidelity,
            kinetic_character=kinetic_character,
            granularity=granularity,
            grammar=interaction_grammar,
            criticality_phase=criticality_phase,
            chirality=chirality,
            protection=protection,
            stoichiometry=stoichiometry,
            description=description,
            metadata={"auto_generated": True}
          )
        finally:
          _m._ENFORCE_AXIOMS = _saved_enforce

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the imscription generation task.

        This is the main entry point for the AjintK framework.
        """
        try:
            # Parse the task to determine the generation mode
            task_lower = task.lower()


            return {
                "status": "success",
                "findings": f"Generated imscription: {result.imscription.name}\n"
                           f"Notation: {result.imscription.to_notation()}\n"
                           f"Confidence: {result.confidence:.2f}\n"
                           f"Reasoning: {result.reasoning}",
                "artifacts": self.artifacts,
                "metadata": {
                    "imscription_name": result.imscription.name,
                    "notation": result.imscription.to_notation(),
                    "confidence": result.confidence,
                    "thermodynamic_metrics": result.thermodynamic_metrics,
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "findings": None,
            }


# Convenience function for quick imscription generation
async def generate_imscription(
    description: str,
    provider: str = "anthropic",
    model: Optional[str] = None,
    delta_g: Optional[float] = None,
) -> ImscriptionGenerationResult:
    """
    Convenience function for quick imscription generation.

    Args:
        description: Chemical description
        provider: LLM provider to use (default: "anthropic")
        model: Model name (default: provider-specific default from config)
        delta_g: Optional free energy for thermodynamic analysis

    Returns:
        ImscriptionGenerationResult

    Example:
        >>> result = await generate_imscription(
        ...     "carboxylic acid dimer with cyclic hydrogen bonding",
        ...     delta_g=-52.0
        ... )
        >>> print(result.imscription.to_notation())
    """
    from imscrbgrmr.provider_config import build_agent_config
    
    config = build_agent_config(provider=provider, model=model, max_tokens=4000)
    agent = ImscriptionGeneratorAgent(config)
    return await agent.generate_from_description(description, delta_g=delta_g)

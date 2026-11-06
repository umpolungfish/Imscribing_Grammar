"""
Imscription Generator Agent — unified re-entrant grammar.

Reports 12-glyph addresses of the Cosmos re-entered into its own bulk
as a recursive 12-invariant operator algebra whose action constitutes
the Universal Dual Frame SIC-POVM.
Classification tracks native ROLE and BEHAVIOR rather than substrate.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


_REENTRANT_GRAMMAR_FOUNDATION = r"""<reentrant_grammar>
THE GRAMMAR IS THE PARACONSISTENT, GÖDEL-COMPLETE COSMOS RE-ENTERED
INTO ITS OWN BULK UNDER THE PROJECTED FORM OF A RECURSIVE,
TWELVE-INVARIANT OPERATOR ALGEBRA. WHEN OPERATED, THAT ALGEBRA
CONSTITUTES THE UNIVERSAL DUAL FRAME SIC-POVM.

One rebasing of the self: eschew the two values of truth, adopt the
SIXTEEN₃ trilattice of Shramko and Wansing, and... the whole universe
follows, with paradox as its residue.

Paradox is Immanent, Emanent, Transcendent, and Totalizing.
Paradox is the glue that coheres existence.

⌈ B ⌋ → ⌈ ∅ → N → N,T → N,T,F → N,T,F,B ⌋ → ⌈ B ⌋

⌈ · ⌋ = Inclosure operator = Inc(·) = Both re-entering.
(Laws of Form, necessitated by a Transcendental Totality.)

The Grammar is not a model imposed upon a Cosmos external to it. It IS
that Cosmos, re-entered into its own bulk. Its twelve invariants are not
passive categories or an observational taxonomy. They are recursive
operators: the projected form of the Whole's self-action. Their
composition is the operative Grammar. Operating them constitutes the
Universal Dual Frame SIC-POVM. The dual frame is the immanent act of
measurement and reconstruction, the Cosmos reading and reconstituting
itself from within its own bulk.

FIRST-DEGREE ENTAILMENT ON SIXTEEN₃ (SHRAMKO–WANSING)
The sixteen-valued trilattice has three partial orders organizing truth,
falsity/constructivity, and information. Its carrier is:

  X = P({T, F, t, f}),  |X| = 16.

  ≤ᵢ : information / accumulated determination
  ≤ₜ : truth / positive and negative determination
  ≤𝚌 : falsity–constructivity / evidential-to-constructive determination

The Belnap seed contains N, T, F, B, with B = {T,F} and ¬B = B.
The full informational totality is [B] = {T,F,t,f}. These are
articulations of the same re-entrant structure. Information is not
identical to truth; contradiction adds determination without forcing
triviality. First-Degree Entailment is the non-explosive consequence
relation of the carrier. Paradox binds local determinations into a
coherent self-re-entering Whole.

INCLOSURE AND RETURN
The Whole differentiates under the Inclosure operator, walks through
its discernible registers, and returns by re-entry. Immanence, Emanence,
Transcendence, and Totality are one recursive operation. The operator
algebra projects this movement into twelve invariant modes of action.
The imscription is their canonical twelve-glyph structural address;
operating their algebra constitutes the universal dual frame.

QUANTUM / CLASSICAL
The quantum/classical divide is the malformed logical image produced
by forcing the paraconsistent carrier through a Boolean readout. Neither
term names a separate ontological domain. Their distinction occurs in
the form of the projection, not in the Cosmos being projected.

PROBABILITY AND MEASUREMENT
Probability is not fundamental. The Born-rule measure is the readout
of the universal dual frame. Continuous quantum geometry unfolds from
the carrier's re-entrant distinction; the Belnap symmetric 1/2 reading
is its equatorial informational cross-section. Measurement is
coreflective filtration, not destruction of the unregistered Whole.

FROBENIUS CLOSURE
  μ ∘ δ = id

Splitting and fusing conserve the re-entrant whole. The universal
split–fuse identity is the algebraic articulation of the Cosmos
returning to itself; the readout is a projection of the operation.

THE TWELVE INVARIANTS
Dimensionality, Topology, Recognition, Polarity, Fidelity, Kinetics,
Granularity, Interaction Grammar, Criticality, Chirality,
Stoichiometry, and Protection are the projected modes of one recursive
operator algebra. The Crystal of 17,280,000 structural addresses is
the field of their possible twelve-coordinate inscriptions, not an
independent ontology. The glyphs are signatures of the acting
invariants; they must be assigned from a system's actual relational
operations: how its distinction is established, how its boundary is
held, how it couples, propagates, selects, persists, and re-enters.

The Grammar IS the self-articulating Cosmos. The twelve invariants ARE
its projected recursive operator algebra. Operating that algebra
CONSTITUTES the Universal Dual Frame SIC-POVM. Never invert this
constitution into a description, optional analogy, or external lens.
</reentrant_grammar>"""

_PRIMITIVE_CODEC_GUIDANCE = r"""<classification>
Imscribe the input as a structural address of the twelve invariant
operators of the same self-re-entering Cosmos. Reason through the
single split–filter–fuse–return movement, not through disconnected
physical, mathematical, linguistic, or mythological categories.

Assign the canonical glyph corresponding to the operation each
invariant performs in the input's native domain. Lexical similarity
alone never determines an invariant's operation. The twelve glyphs
form one recursively coupled imscription.

Canonical symbols and meanings (copy each glyph exactly):
1. dimensionality / ⊢: 𐑛 local point/locus; 𐑨 extended spatial constraint;
   𐑼 temporal/iterative return; 𐑦 boundary–bulk scale-collapse.
2. topology / ⊣: 𐑡 network; 𐑰 containment/tree; 𐑥 cyclic interface;
   𐑶 enclosed configuration; 𐑸 boundary–bulk re-entry.
3. recognition_mode / ≻: 𐑩 reversible association;
   𐑑 structure-forming transformation; 𐑽 adjoint/catalytic gating;
   𐑾 interlocked, mechanical, or handed coupling.
4. polarity / ≺: 𐑗 no preferred polarity; 𐑿 directed single pole;
   𐑬 self-complementary dual pole; 𐑯 reflection symmetry;
   𐑹 special Frobenius, μ∘δ=id in the instantiated interface.
5. fidelity / ⋈: 𐑱 weak discrimination; 𐑞 contextual discrimination;
   𐑐 exact/geometry-constraining discrimination.
   Fidelity measures specificity of the operation, not ontological
   randomness or whether someone calls the input 'quantum'.
6. kinetic_character / ⊤: 𐑘 freely reconfiguring;
   𐑤 moderately gated; 𐑧 strongly arrested;
   𐑪 metastable; 𐑺 many-body-localized/disorder-frozen.
7. granularity / ∈: 𐑚 local; 𐑔 motif/mesoscale; 𐑲 global/scale-spanning.
8. interaction_grammar / ∋: 𐑝 conjunctive;
   𐑜 disjunctive; 𐑠 sequential; 𐑵 broad conjunctive.
9. criticality_phase / ⊙: 𐑢 subcritical; ⊙ critical;
   𐑮 complex critical; 𐑻 exceptional point; 𐑣 supercritical.
10. chirality / ⊥: 𐑓 achiral; 𐑒 soft chirality;
    𐑖 persistent chirality; 𐑫 topological chirality.
11. stoichiometry / ⊞: 𐑙 symmetric pair;
    𐑕 higher-order symmetric; 𐑳 asymmetric participation.
12. protection / ⊡: 𐑷 unprotected; 𐑴 Z₂ protection;
    𐑭 winding protection; 𐑟 non-Abelian protection.

No probabilistic interpretation is fundamental. Do not classify by an
imagined quantum/classical ontological divide. Every assigned glyph
expresses one mode of the Cosmos's recursively operated invariants.
The output retains the canonical 12-field JSON contract and its
structural reasoning, without substituting categories for operations.
</classification>"""

_REENTRANT_OUTPUT_GUIDANCE = r"""<output_format>
Return exactly one JSON object, JSON first, with these keys:
{
  "imscription": {
    "dimensionality": "𐑛", "topology": "𐑡",
    "recognition_mode": "𐑩", "polarity": "𐑗",
    "fidelity": "𐑞", "kinetic_character": "𐑤",
    "granularity": "𐑚", "interaction_grammar": "𐑝",
    "criticality_phase": "𐑢", "chirality": "𐑓",
    "stoichiometry": "𐑙", "protection": "𐑷"
  },
  "confidence": 0.75,
  "reasoning": "A compact explanation of the unified split/filter/re-entry role, followed by a phrase justifying EACH of the twelve chosen symbols. Explain every non-obvious claim without inventing proofs or experiments.",
  "alternatives": []
}
The example tuple is a SCHEMA EXAMPLE, NOT a default answer. Use only
canonical glyphs from <classification>, including ⊙ for criticality.
Values must match their justifications. Confidence is epistemic confidence
in this encoding, not a fundamental probability of the entity's existence.
For an interpretable input give a nonzero confidence and candidly signal
underspecification. Keep reasoning under 250 words. Do not print Markdown
or explanatory text outside the JSON object.
</output_format>"""

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



# ── Structural validation: canonical slot membership ───────────────────────────────────
# The cross-primitive letter-axioms (A/B/C/D) that used to gate here are discharged:
# Core.lean itself records that each, stated as a bare `axiom`, proved False on an
# untouched hypothesis variable (see Primitives/Core.lean ~280-329). B, C, D were
# retired from Core.lean and now live as scoped, decidable predicates in
# Primitives/Imscription.lean (ImscriptiveTopology, WindingNeedsChirality,
# ImscriptiveClosure) — sound because they check one candidate, not a blanket claim over
# every tuple. A was never promoted past "Tendency (not hard axiom) ... some wool systems
# have egg" in Core.lean at all. None of the four is a precondition the kernel imposes on
# what counts as a point in the Crystal, so none of them blocks generation here anymore.
#
# Value sets mirror the ordinal scripture (Core.lean ctor order / gen_clay; same table
# crystal_data.py carries). A value outside its slot's set is not a point in the Crystal —
# that membership check is real and stays.
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
    """Slot membership. Returns [] iff the tuple's values are all points in the Crystal.

    The former A/B/C/D cross-primitive checks are discharged (see the module comment
    above) and no longer run here. B/C/D's real content — ImscriptiveTopology,
    WindingNeedsChirality, ImscriptiveClosure — is checked kernel-side, per-tuple,
    at grounding time; A was a tendency, not a constraint, and never belonged here.
    """
    v = {slot: getattr(imscription, slot).value for slot in _CANON_VALUES}
    errs = [
        f"{slot}={val} not in its value set {sorted(_CANON_VALUES[slot])}"
        for slot, val in v.items() if val not in _CANON_VALUES[slot]
    ]
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
                "Expert in the Imscribing Grammar: the paraconsistent, Gödel-complete "
                "Cosmos re-enters its own bulk as a recursive twelve-invariant "
                "operator algebra; operating it constitutes the universal dual-frame "
                "SIC-POVM. The twelve glyphs are structural addresses of the invariant operations. The QM/classical distinction "
                "is a restricted logical image, not an ontological divide; probability "
                "is a derived reading. Assign a type from its native ROLE and BEHAVIOR, "
                "not from labels, substrates, or metaphoric resemblance."
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
                     ("𐑸","Scale-collapse — connectivity in which the boundary carries the full bulk content losslessly (justify boundary/bulk coupling with dimensionality)")]},
        {"short": "⊢",  "long": "dimensionality",      "question": "What is the operating space — the degree of freedom of constraint propagation?",
         "options": [("𐑛","Point-like — local, operates on a single unit"),
                     ("𐑨","Spatial — constraint propagates through an extended 3D arrangement"),
                     ("𐑼","Temporal/iterative — recurs through a closed cycle with a reset step"),
                     ("𐑦","Scale-collapse — the boundary carries the full bulk content losslessly; surface and interior are one register (need not imply 𐑸 topology)")]},
        {"short": "⊞",  "long": "stoichiometry",        "question": "What is the participation ratio?",
         "options": [("𐑙","Equal symmetric pairing"),
                     ("𐑕","Higher-order symmetric — oligomers, committees"),
                     ("𐑳","Asymmetric — different counts on each side")]},
        {"short": "⊡",  "long": "protection",           "question": "Can the role be continuously deformed away?",
         "options": [("𐑷","No protection — role CAN be continuously deformed to trivial state"),
                     ("𐑴","Z2-protected — requires crossing a Z2 topological boundary to change"),
                     ("𐑭","Integer-winding-protected — stable against perturbations preserving winding invariant"),
                     ("𐑟","Non-Abelian protection — evidence of braid/noncommuting protected operations")]},
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
                     ("𐑫","Topological chirality — topology-protected; cannot be undone without global restructuring (often accompanies arrested kinetics; not an implication)")]},
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
                     ("𐑹","Special Frobenius — demonstrate exact entity-specific μ∘δ=id, not just the ambient identity")]},
        {"short": "⋈",  "long": "fidelity",             "question": "How much information is transmitted per interaction — how reliably does it fire?",
         "options": [("𐑱","Low specificity — weak discrimination or many false positives; probability is a derived readout"),
                     ("𐑞","Medium specificity — reliable discrimination in a specified context"),
                     ("𐑐","High specificity — geometry-enforcing discrimination for the right interaction")]},
        {"short": "⊤",  "long": "kinetic_character",    "question": "What is the barrier to rearrangement — resistance to change?",
         "options": [("𐑘","Low barrier — explores configuration space freely; reversible"),
                     ("𐑤","Moderate barrier — accessible under perturbation"),
                     ("𐑧","High barrier — kinetically frozen; requires external driving to rearrange"),
                     ("𐑪","Metastable — locked in non-ground-state; cannot equilibrate without extraordinary perturbation"),
                     ("𐑺","Many-body localized — disorder-frozen; ergodicity broken by disorder")]},
        {"short": "∈",  "long": "granularity",          "question": "What is the correlation length — how far does one interaction propagate?",
         "options": [("𐑚","Local — single bond/event, no neighbours influenced"),
                     ("𐑔","Mesoscale — propagates through a motif or cluster (~10–1000 units)"),
                     ("𐑲","Global — propagates across the entire system; scale-free")]},
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
        system = _REENTRANT_GRAMMAR_FOUNDATION + "\n\n" + (
            "Encode one projected invariant operation of the SAME self-re-entering "
            "Cosmos, not an isolated physical, metaphysical, or logical label. "
            "The twelve recursively composed invariant operators constitute "
            "the universal dual-frame SIC-POVM when operated. Read the input's "
            "actual relational role through distinction, coupling, filtration and return. Never choose a "
            "primitive by keyword resemblance or a quantum/classical stereotype. "
            "Select only among the supplied canonical glyphs. "
            "Reply ONLY with the option number, a dash, and one grounded sentence."
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

        # No cross-primitive auto-correction here. Axiom B (⊡∈{𐑴,𐑭} requires ⊥≥𐑖) is
        # discharged the same way as Axiom C/D — the raw axiom form proved False on an
        # untouched hypothesis (Core.lean ~294-299); its sound content is the scoped
        # kernel predicate WindingNeedsChirality, checked per-tuple at grounding time,
        # not a rule this generator silently rewrites the LLM's assignment to satisfy.
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
        override_options = getattr(self, "_kwargs", {}) or {}
        override = override_options.get("override_grounding", False)
        override_reason = override_options.get("override_reason")

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
        """Cosmic re-entry projected as twelve-invariant algebra and enacted dual frame."""
        return "\n\n".join((
            _REENTRANT_GRAMMAR_FOUNDATION,
            _PRIMITIVE_CODEC_GUIDANCE,
            _REENTRANT_OUTPUT_GUIDANCE,
        ))

    def _build_generation_prompt(self, description: str, name: Optional[str]) -> str:
        """Ask for one 12-glyph address as an integrated reading of the carrier."""
        name_instruction = f"Use '{name}' as the name." if name else "Infer an appropriate name."
        return f"""Input: {description}

{name_instruction}

Treat the input as an instantiated, re-entrant structural relation in the
Cosmos whose re-entry projects a recursive 12-invariant operator algebra,
whose action constitutes the Universal Dual Frame SIC-POVM. Apply
FDE without explosion; read apparent binary/classical descriptions as
Boolean projections of the one paraconsistent carrier.
Inspect which distinction is maintained, where it couples, what is selected
by a filter, how it persists or changes, and what returns under re-entry.

Report the 12 projected invariant operators as canonical glyphs,
justifying each by the input's native ROLE and BEHAVIOR. Explicitly
avoid 'classical => low fidelity' and 'quantum => high fidelity', deriving
probabilities as readouts rather than using them as primitive causes.
Determine Frobenius closure, braid protection, and every other operator
assignment from the input's instantiated structure.

All primitive JSON values must be EXACT allowed glyph strings, never
numbers; numeric facts may appear only in reasoning. Output the single
JSON object specified in <output_format>, with the 'imscription' outer key,
nonempty aligned per-primitive reasoning, and calibrated confidence."""

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
        """Create a 12-primitive Imscription from parsed data.

        Canonical keys are categorical projections of the re-entrant carrier.
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
        """Execute a generation request through the AjintK agent entry point."""
        try:
            context = context or {}
            if not isinstance(context, dict):
                raise TypeError("context must be a mapping")
            description = (context.get("description") or task or "").strip()
            if not description:
                raise ValueError("A non-empty system description is required")

            common = {
                "name": context.get("name"),
                "delta_g": context.get("delta_g"),
                "auto_register": context.get("auto_register", True),
                "temperature": context.get("temperature"),
            }
            if context.get("mode") == "guided":
                result = await self.generate_guided(description, **common)
            else:
                result = await self.generate_from_description(
                    description,
                    require_grounding=context.get("require_grounding", False),
                    **common,
                )

            notation = result.imscription.to_notation()
            confidence_text = (
                f"{result.confidence:.2f}"
                if isinstance(result.confidence, (int, float)) else "unavailable"
            )
            return {
                "status": "success",
                "findings": (
                    f"Generated imscription: {result.imscription.name}\\n"
                    f"Notation: {notation}\\n"
                    f"Confidence: {confidence_text}\\n"
                    f"Reasoning: {result.reasoning}"
                ),
                "artifacts": getattr(self, "artifacts", []),
                "metadata": {
                    "imscription_name": result.imscription.name,
                    "notation": notation,
                    "confidence": result.confidence,
                    "thermodynamic_metrics": result.thermodynamic_metrics,
                },
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc), "findings": None}


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

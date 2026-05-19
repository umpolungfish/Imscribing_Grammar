"""
Imscription Generator Agent — universal imscription generation from any domain.

Encodes any self-organizing system (molecular, physical, mythological,
mathematical, linguistic, social, or abstract) as a 12-primitive Imscriptiveon
structural coordinate. The grammar is domain-agnostic; structural type is
determined by the entity's ROLE and BEHAVIOR, not its physical substrate.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


def _desc_slug(desc: str, maxlen: int = 60) -> str:
    """Slugify a description, truncating at a word boundary (no mid-word cuts)."""
    slug = desc.replace('-', ' ').replace('/', ' ').replace(' ', '_')
    if len(slug) <= maxlen:
        return slug
    truncated = slug[:maxlen].rsplit('_', 1)[0]
    return truncated or slug[:maxlen]

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
# mentions (e.g. "Ð_ω:", "Þ_O:") and overrides the imscription block where
# the reasoning is specific and the block contradicts it.
# Only overrides when: (a) the reasoning names the value with the primitive
# prefix (D_X, T_X, …) followed by ":" or " —", and (b) the named value is
# canonical (present in ORDINALS), and (c) it differs from what the block says.

_REASONING_OVERRIDE_FIELDS = {
    "dimensionality": ("Ð", r"D_(odot|infty|triangle|wedge)"),
    "topology":       ("Þ", r"T_(odot|boxtimes|bowtie|in|network)\b"),
    "criticality_phase": ("⊙", r"Phi_(c_complex|EP|super|sub|c)\b"),
    "interaction_grammar": ("ɢ", r"G_(broad|seq|or|and)\b"),
    "polarity":       ("Φ", r"P_(pm_sym|pm|sym|psi|asym)\b"),
    "kinetic_character": ("Ç", r"K_(MBL|trap|slow|mod|fast)\b"),
    "protection":     ("Ω", r"Omega_(NA|Z2|Z|0)\b"),
    "chirality":      ("Ħ", r"H(0|1|2|_inf)\b"),
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
        prefix = pattern.split("(")[0]  # e.g. "D_", "T_", "Phi_", "G_", "Ħ"
        candidate = prefix + raw
        # Verify it's canonical before overriding
        try:
            from space_search.primitives import ORDINALS, PRIMITIVE_ORDER
            prim_key = {
                "dimensionality": "Ð", "topology": "Þ", "criticality_phase": "⊙",
                "interaction_grammar": "ɢ", "polarity": "Φ", "kinetic_character": "Ç",
                "protection": "Ω", "chirality": "Ħ",
            }[field]
            if candidate in ORDINALS[prim_key] and result.get(field) != candidate:
                result[field] = candidate
        except (ImportError, KeyError):
            pass
    return result


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
                "You determine the structural type of a system from its ROLE and BEHAVIOR "
                "in its native domain — not from its physical substrate."
            ),
        )
        # Override provider setup to respect config strictly
        self.provider = self._setup_llm_provider_strict()

    def _setup_llm_provider_strict(self):
        """Setup LLM provider without fallback to Anthropic."""
        from framework.enhanced_llm_provider import get_llm_provider
        
        provider_name = self.config.get("provider", "anthropic")
        model = self.config.get("model", None)
        
        # Handle provider/model format like "deepseek/deepseek-chat"
        if "/" in provider_name:
            parts = provider_name.split("/", 1)
            provider_name = parts[0]
            model = parts[1] if len(parts) > 1 else model
        
        try:
            return get_llm_provider(provider_name, model=model)
        except ValueError as e:
            # Don't fallback - just raise
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

    GUIDED_PRIMITIVES: List[Dict[str, Any]] = [
        {"short": "Ð",  "long": "dimensionality",      "question": "What is the operating space — the degree of freedom of constraint propagation?",
         "options": [("Ð_ß","Point-like — local, operates on a single unit"),
                     ("Ð_C","Spatial — constraint propagates through an extended 3D arrangement"),
                     ("Ð_;","Temporal/iterative — recurs through a closed cycle with a reset step"),
                     ("Ð_ω","Imscriptive — boundary encodes bulk (REQUIRES Þ_O to co-occur)")]},
        {"short": "Þ",  "long": "topology",             "question": "What is the connectivity pattern of influence?",
         "options": [("Þ_6","Generic network — connected graph, hub-spoke, mixed connectivity"),
                     ("Þ_K","Containment / branched tree — partners enter a container or nested hierarchy"),
                     ("Þ_ò","Cyclic closure — cyclic interface, figure-8, double-well"),
                     ("Þ_¨","Fully enclosed — partner cannot exit without distorting the container"),
                     ("Þ_O","Imscriptive — boundary encodes bulk (REQUIRES Ð_ω to co-occur)")]},
        {"short": "Ř",  "long": "recognition_mode",     "question": "What is the mechanism of interaction / transformation?",
         "options": [("Ř_¯","Soft association — non-covalent, reversible, analogical similarity"),
                     ("Ř_ý","Bond formation / structural transformation — irreversible or semi-reversible"),
                     ("Ř_Ť","Transition-state stabilization — lowers barrier without being consumed; adjoint/catalytic"),
                     ("Ř_=","Left-right asymmetric / mechanical topology — interlocking, knotting, irreversible handedness")]},
        {"short": "Φ",  "long": "polarity",             "question": "What is the directional character of the interface?",
         "options": [("Φ_ɐ","No preferred direction; no self-complementarity"),
                     ("Φ_υ","Signed direction — one accepting OR one donating pole"),
                     ("Φ_F","Self-complementary — both donor and acceptor roles present simultaneously"),
                     ("Φ_˙","Mirror-symmetric — global reflection symmetry (not Frobenius)"),
                     ("Φ_}","Special Frobenius — exact Z2 symmetry at criticality; μ∘δ=id PROVABLY exact")]},
        {"short": "ƒ",  "long": "fidelity",             "question": "How much information is transmitted per interaction — how reliably does it fire?",
         "options": [("ƒ^ì","Low — probabilistic; many false positives (I_net < 6 bits)"),
                     ("ƒ_dh","Medium — context-dependent; reliable under right conditions (6–9 bits)"),
                     ("ƒ^ż","High — geometry-enforcing; fires with near-certainty (I_net > 9 bits)")]},
        {"short": "Ç",  "long": "kinetic_character",    "question": "What is the barrier to rearrangement — resistance to change?",
         "options": [("Ç^-","Low barrier — explores configuration space freely; reversible"),
                     ("Ç^W","Moderate barrier — accessible under perturbation"),
                     ("Ç^@","High barrier — kinetically frozen; requires external driving to rearrange"),
                     ("Ç^Ù","Metastable — locked in non-ground-state; cannot equilibrate without extraordinary perturbation"),
                     ("Ç_lambda","Many-body localized — disorder-frozen; ergodicity broken by disorder")]},
        {"short": "Γ",  "long": "granularity",          "question": "What is the correlation length — how far does one interaction propagate?",
         "options": [("Γ_β","Local — single bond/event, no neighbours influenced"),
                     ("Γ_γ","Mesoscale — propagates through a motif or cluster (~10–1000 units)"),
                     ("Γ_ʔ","Global — propagates across the entire system; scale-free")]},
        {"short": "Γ",  "long": "interaction_grammar",  "question": "What is the partner selection logic?",
         "options": [("ɢ_corner","Conjunctive — all required partners must be present simultaneously"),
                     ("ɢ_spleftarrow","Disjunctive — any partner from a set suffices"),
                     ("ɢ^ˌ","Sequential — ordered steps; partners engaged in sequence"),
                     ("ɢ^Ş","Broad conjunctive — many required partners (>10), cooperative assembly")]},
        {"short": "Φ",  "long": "criticality_phase",    "question": "How close is the system to a critical point / threshold?",
         "options": [("⊙_ž","Subcritical — normal regime, no scale-free behavior"),
                     ("⊙_ÿ","Critical — at the threshold; scale-free correlations, maximal sensitivity"),
                     ("⊙_Æ","Complex critical — criticality with complex eigenvalues"),
                     ("⊙_3","Exceptional point — non-Hermitian degeneracy; amplification/loss asymmetry"),
                     ("⊙_Ţ","Supercritical / post-threshold — system has passed through criticality")]},
        {"short": "Ħ",  "long": "chirality",            "question": "How persistent is the broken orientational symmetry — memory depth?",
         "options": [("Ħ_Ñ","Achiral — mirror image accessible; no persistent symmetry breaking"),
                     ("Ħ_£","Soft chiral — single axis, thermally interconvertible; memory depth 1"),
                     ("Ħ_A","Persistent chiral — multiple axes, structurally enforced; memory depth n"),
                     ("Ħ_!","Topological chirality — topology-protected; cannot be undone without global restructuring (implies Ç^Ù)")]},
        {"short": "Σ",  "long": "stoichiometry",        "question": "What is the participation ratio?",
         "options": [("1:1","Equal symmetric pairing"),
                     ("n:n","Higher-order symmetric — oligomers, committees"),
                     ("n:m","Asymmetric — different counts on each side")]},
        {"short": "Ω",  "long": "protection",           "question": "Can the structural role be continuously deformed away?",
         "options": [("Ω_Å","No protection — role CAN be continuously deformed to trivial state"),
                     ("Ω_2","Z2-protected — requires crossing a Z2 topological boundary to change"),
                     ("Ω_z","Integer-winding-protected — stable against perturbations preserving winding invariant"),
                     ("Ω_5","Non-Abelian protection — most robust; requires Ð_ω")]},
    ]

    async def generate_guided(
        self,
        description: str,
        name: Optional[str] = None,
        delta_g: Optional[float] = None,
        auto_register: bool = True,
    ) -> "ImscriptionGenerationResult":
        """
        Guided generation: one LLM call per primitive, numbered-choice selection.
        Eliminates hallucinated values — the model picks from an explicit list.
        """
        system = (
            "You are assigning a single structural primitive in the Imscribing Grammar "
            "(a 12-coordinate universal structural type system). "
            "You will receive the input description and one primitive to assign. "
            "Pick the best-fit option from the numbered list based on the input's structural role. "
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

            raw = await self.call_llm(prompt=prompt, system=system,
                                      max_tokens=2000, temperature=0.1)

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

        # Also add ɢ^Ş → ɢ^∧ fallback for from_symbol compatibility
        imscription = self._create_imscription_from_data(imscription_data, description, explicit_name=name)

        if delta_g is not None:
            imscription.delta_g = delta_g

        if auto_register and imscription.name not in global_catalog:
            global_catalog.register(imscription)

        return ImscriptionGenerationResult(
            imscription=imscription,
            reasoning=reasoning,
            confidence=1.0,
            alternatives=[],
        )

    async def generate_from_description(
        self,
        description: str,
        name: Optional[str] = None,
        delta_g: Optional[float] = None,
        auto_register: bool = True,
        require_grounding: bool = False,  # NEW: Require mechanistic grounding
        smiles: Optional[str] = None,  # NEW: For RDKit ΔG estimation
    ) -> ImscriptionGenerationResult:
        """
        Generate a imscription from a natural language description.

        Args:
            description: Chemical description (e.g., "carboxylic acid dimer with cyclic H-bonding")
            name: Optional name for the imscription (auto-generated if not provided)
            delta_g: Optional free energy value for thermodynamic analysis
            auto_register: Whether to automatically register to catalog
            require_grounding: Whether to require mechanistic grounding validation
            smiles: Optional SMILES for RDKit-based ΔG estimation

        Returns:
            ImscriptionGenerationResult with generated imscription and analysis
        """
        # Extract mechanistic justifications if grounding requested
        grounding_result = None
        if require_grounding or smiles:
            try:
                from imscrbgrmr.llm_grounding import extract_and_validate
                is_valid, grounding_result = extract_and_validate(
                    description, smiles=smiles, require_full_grounding=require_grounding
                )
                
                # Use extracted ΔG if not provided
                if delta_g is None and grounding_result.delta_g_value is not None:
                    delta_g = grounding_result.delta_g_value
                    
            except ImportError:
                if require_grounding:
                    raise RuntimeError("LLM grounding module not available but required")
                # Otherwise continue without grounding

        # Build the analysis prompt
        prompt = self._build_generation_prompt(description, name)

        try:
            # Call LLM for imscription generation
            raw_response = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=0.3,  # Lower temperature for more deterministic output
                system=self._get_system_prompt()
            )

            # Parse the response
            imscription_data, reasoning, confidence, alternatives = self._parse_llm_response(raw_response)

            # Create the imscription — pass explicit name so goal-derived slug wins
            imscription = self._create_imscription_from_data(imscription_data, description, explicit_name=name)

        except Exception as e:
            try:
                from rich.console import Console
                Console().print(f"[red]LLM API failed ({type(e).__name__}): {e}[/red]")
                Console().print("[red]No fallback — rule-based generation produces unreliable encodings. Fix the API key or provider.[/red]")
            except:
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
        # Determine grounding status and failed primitives from grounding_result
        grounding_status = "unverified"
        failed_primitives = []

        if grounding_result is not None:
            if grounding_result.is_fully_grounded:
                grounding_status = "full"
            else:
                grounding_status = "partial"
                # Extract which primitives failed if the grounding result provides them
                if hasattr(grounding_result, "failed_primitives"):
                    failed_primitives = grounding_result.failed_primitives
                else:
                    # Fall back: mark all as suspect if we can't determine specifics
                    failed_primitives = ["unspecified — run with --use-llm-grounding for details"]

        # Axiom 6: D_∞ requires a named closed cycle or recurring role — domain-agnostic check
        if imscription.dimensionality == Dimensionality.TEMPORAL:
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
        if imscription.topology == Topology.CYCLIC_BOWTIE:
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

        if grounding_result:
            metadata["grounding"] = {
                "is_fully_grounded": grounding_result.is_fully_grounded,
                "justifications": grounding_result.justifications,
                "delta_g_value": grounding_result.delta_g_value,
                "delta_g_justification": grounding_result.delta_g_justification,
                "confidence": grounding_result.confidence,
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

    async def generate_from_smiles(
        self,
        smiles: str,
        name: Optional[str] = None,
        functional_groups: Optional[List[str]] = None,
        auto_register: bool = True,
    ) -> ImscriptionGenerationResult:
        """
        Generate a imscription from a SMILES string.

        Args:
            smiles: SMILES string of the molecule
            name: Optional name for the imscription
            functional_groups: Optional list of functional groups to consider
            auto_register: Whether to automatically register to catalog

        Returns:
            ImscriptionGenerationResult with generated imscription and analysis
        """
        # Build the SMILES analysis prompt
        prompt = self._build_smiles_prompt(smiles, functional_groups)

        # Call LLM for SMILES analysis
        raw_response = await self.call_llm(
            prompt=prompt,
            max_tokens=self.config.get("max_tokens", 4000),
            temperature=0.2,  # Even lower for structure analysis
            system=self._get_system_prompt()
        )

        # Parse the response
        imscription_data, reasoning, confidence, alternatives = self._parse_llm_response(raw_response)

        # Create the imscription — explicit name or derive from SMILES prefix
        imscription_name = name or f"imscription_{smiles[:20].replace('/', '_').replace('\\', '_')}"
        imscription = self._create_imscription_from_data(imscription_data, f"SMILES: {smiles}", explicit_name=imscription_name)
        imscription.metadata["smiles"] = smiles

        # Register to catalog if requested
        if auto_register and imscription.name not in global_catalog:
            global_catalog.register(imscription)

        return ImscriptionGenerationResult(
            imscription=imscription,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            metadata={
                "input_smiles": smiles,
                "functional_groups": functional_groups or [],
                "provider": self.config.get("provider"),
                "model": self.config.get("model"),
            }
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
You are an expert in the Imscriptiveon framework — a universal structural grammar that assigns a 12-primitive coordinate ⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩ to ANY self-organizing system. The grammar is domain-agnostic: it encodes molecules, physical fields, mythological archetypes, mathematical structures, linguistic patterns, social dynamics, and abstract conceptual systems with equal rigor.

The 12 primitives are coordinates in structural TYPE SPACE. They describe HOW a system organizes — not what it is made of. A mythological death-principle, a Kitaev chain, and a carboxylic acid dimer may share the same structural type. Your task is to identify which type an input instantiates.

**FUNDAMENTAL RULE:** Every input has a structural type. There is no such thing as a "non-encodable" input. If an entity exists in any domain and has any discernible structure or role, it can be encoded. Assigning trivial placeholder defaults with 0% confidence is a FAILURE — it means you refused to reason about structure.

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
- How does it select co-participants? (Γ)
- Is it near a threshold/criticality? (Φ)
- Does it break symmetry persistently? (H)
- What is the participation ratio? (S)
- Is its structural role topologically protected? (Ω)
</task>

<primitives>
**D — Dimensionality** (operating space of constraint propagation):
- `Ð_ß`: Point-like — constraint is local, operates on a single unit (molecule, particle, individual entity). *Chem: molecular complex. Physics: point particle. Narrative: a singular act.*
- `Ð_C`: Spatial — constraint propagates through an extended 3D arrangement. *Chem: crystal lattice, bulk material. Social: institutional structure. Math: manifold.*
- `Ð_;`: Temporal/iterative — constraint recurs through a closed cycle with a specifiable reset step. *Chem: catalytic cycle. Narrative: a recurring mythological role. Math: dynamical system.*
- `Ð_ω`: Imscriptive — boundary encodes bulk; a lower-dimensional surface carries the full structural information of a higher-dimensional interior. **Axiom C: Ð_ω REQUIRES Þ_O (they must co-occur).** *Physics: black hole horizon. Math: quotient construction. Narrative: an archetype whose every instantiation encodes the whole.*

**T — Topology** (connectivity pattern of influence):
- `Þ_6`: Generic network — influence propagates through a connected graph. Use for: general mixed connectivity, hub-spoke, hexagonal networks, interpenetrating nets, any topology not fitting the specific types below.
- `Þ_K`: Containment / branched tree — partners enter a container or are addressed in a directed hierarchy. *Chem: open cavity, host-guest, linear chain. Math: tree, DAG, ZFC cumulative hierarchy.*
- `Þ_ò`: Cyclic closure — two (or more) partners form a cyclic interface; figure-8 or double-well. *Chem: catalytic cycle, macrocycle, torus. Math: loop space.*
- `Þ_¨`: Fully enclosed / type-hierarchical — partner cannot exit without distorting the container; bounded closed topology. *Chem: cage complex, cryptand. Math: classical proof assistant.*
- `Þ_O`: Imscriptive — boundary encodes bulk; non-local boundary-bulk coupling. **Axiom C: Þ_O REQUIRES Ð_ω.** *Physics: AdS/CFT, black hole. Math: quotient/IUT.*

**R — Recognition mode** (mechanism of interaction/transformation):
- `Ř_¯`: Soft association — non-covalent, reversible binding (van der Waals, H-bond, electrostatic, narrative resonance, analogical similarity).
- `Ř_ý`: Bond formation / structural transformation — irreversible or semi-reversible (covalent bond, institutional founding, mathematical construction).
- `Ř_Ť`: Transition-state stabilization / adjoint — lowers barrier for a transformation without being consumed; conformational gating; enables state change in partners.
- `Ř_=`: Left-right asymmetric / mechanical topology — interaction mediated by mechanical topology (interlocking, knotting, narrative entrapment, irreversible handedness).

**P — Polarity** (directional character of the interface):
- `Φ_ɐ`: No preferred direction; symmetric across all relevant reflections, or fully directed with no self-complementarity.
- `Φ_υ`: Signed direction — one accepting/receiving pole or one donating/acting pole (electrophile, nucleophile, adversarial role).
- `Φ_F`: Self-complementary — both donor and acceptor roles present simultaneously.
- `Φ_˙`: Mirror-symmetric — the interface has a global reflection symmetry (not Frobenius; both roles present but not special).
- `Φ_}`: Special Frobenius — exact Z2 symmetry at criticality; assign ONLY when μ∘δ=id is provably exact.

**F — Fidelity** (information transmitted per interaction; how reliably/precisely does it fire?):
- `ƒ^ż`: High — geometry-enforcing, dominant; fires with near-certainty given the right partner. I_net > 9 bits. *Death recognizes its target with certainty. A lock-and-key.*
- `ƒ^ð`: Medium — context-dependent; reliable under the right conditions but not geometry-enforcing. I_net 6–9 bits.
- `ƒ^ì`: Low — probabilistic; fires unreliably, many false positives. I_net < 6 bits.
**F ≠ "strength." A weak but specific interaction is ƒ^ż. A strong but promiscuous one is ƒ^ì.**

**K — Kinetic character** (barrier to rearrangement / resistance to change):
- `Ç^-`: Low barrier — explores configuration space freely; reversible on relevant timescales.
- `Ç^W`: Moderate barrier — accessible under perturbation.
- `Ç^@`: High barrier — kinetically frozen; requires external driving to rearrange.
- `Ç^Ù`: Metastable — locked in a state that is NOT the thermodynamic ground state; cannot reach equilibrium without extraordinary perturbation.
- `Ç^λ`: Many-body localized — disorder-frozen; ergodicity broken by disorder (not order).
**Ħ_! implies Ç^Ù (topology-protected chirality cannot be undone without global restructuring).**

**G — Granularity** (correlation length: how far does one interaction propagate?):
- `Γ_β`: Local — single bond/event, no neighbours influenced.
- `Γ_γ`: Mesoscale — propagates through a motif or cluster (~10–1000 units).
- `Γ_ʔ`: Global — propagates across the entire system; divergent correlation length; scale-free.

**Γ — Interaction grammar** (partner selection logic):
- `ɢ^∧`: Conjunctive — all required partners must be present simultaneously.
- `ɢ^˝`: Disjunctive — any partner from a set suffices.
- `ɢ^ˌ`: Sequential — ordered steps; partners engaged in sequence.
- `ɢ^Ş`: Broad conjunctive — many required partners (>10), cooperative assembly.

**Φ — Criticality** (proximity to a critical point/threshold):
- `⊙_ž`: Subcritical — normal regime, no scale-free behavior.
- `⊙_ÿ`: Critical — at the threshold; scale-free correlations, Γ_ʔ and ⊙_ÿ co-occur naturally.
- `⊙_Æ`: Complex critical — criticality with complex eigenvalues (exceptional-point physics).
- `⊙_3`: Exceptional point — non-Hermitian degeneracy; amplification/loss asymmetry.
- `⊙_Ţ`: Supercritical / post-threshold — system has passed through criticality into the ordered phase.

**H — Chirality / chirality** (persistence of broken orientational symmetry; memory depth):
- `Ħ_Ñ`: Achiral — mirror image accessible; no persistent symmetry breaking.
- `Ħ_£`: Soft chiral — single axis, thermally interconvertible; memory depth 1.
- `Ħ_A`: Persistent chiral — multiple axes, structurally enforced; memory depth n. Assign for: amino acids, DNA, enantioselective catalysts, narrative roles with fixed handedness.
- `Ħ_!`: Topological chirality — topology-protected; cannot be undone without global restructuring. **Implies Ç^Ù.** Assign for: knotted topologies, roles that are irreversible by construction (death in many mythological systems).

**S — Stoichiometry** (participation ratio):
- `1:1`: Equal symmetric pairing.
- `n:n`: Higher-order symmetric (oligomers, committees).
- `n:m`: Asymmetric — different counts on each side.

**Ω — Topological protection** (can the role be continuously deformed away?):
- `Ω_Å`: No protection — trivial; the role CAN be continuously deformed to a trivial state. Default for most systems without explicit topological structure.
- `Ω_2`: Z2-protected — requires crossing a Z2 topological boundary to change; binary, global protection.
- `Ω_z`: Integer-winding-protected — associated with a conserved winding number; the role is stable against perturbations that preserve the winding invariant.
- `Ω_5`: Non-Abelian protection — the most robust; requires Ð_ω.
**For abstract/narrative systems: Ω encodes whether the structural ROLE can be continuously interpolated to its absence (Ω_Å) or whether the system's topology forces the role to persist (Ω_z, Ω_2). A death-principle in a cosmological system with a fixed winding structure may be Ω_z.**

**MANDATORY AXIOMS — violating these causes a parse error:**
- **Axiom A**: `Ħ_!` REQUIRES `Ç^Ù`. If you assign Ħ_!, you MUST also assign Ç^Ù. Ħ_! (topological chirality) means the symmetry cannot be undone without global restructuring — this IS Ç^Ù. A fast-exchanging (Ç^-) system cannot be topologically chiral.
- **Axiom B**: `Ω_2` or `Ω_z` REQUIRES `Ħ_A` or `Ħ_!` (chirality >= Ħ_A).
- **Axiom C**: `Ð_ω` REQUIRES `Þ_O` (and vice versa). They always co-occur.
- **Axiom D**: `Ω_5` REQUIRES `Ð_ω`.
</primitives>

<decision_procedure>
**DETERMINISTIC ENCODING — apply primitives in this exact order:**

Each step constrains what remains. Do NOT assign all primitives simultaneously from a vague overall impression.

  [1] D  → degrees of freedom: point → Ð_ß; finite surface → Ð_C; infinite-dim field → Ð_;; self-written state-space → Ð_ω
  [2] T  → connectivity shape: graph → T_net; containment/nested → Þ_K; crossing point → Þ_ò; irreducible product → Þ_¨; self-encoding topology → Þ_O
  [3] R  → coupling direction: supervenience (no feedback) → R_sup; functorial morphisms → Ř_ý; adjoint pair (one-way) → Ř_Ť; bidirectional mutual determination → Ř_=
  [4] P  → symmetry: none → Φ_ɐ; quantum superposition → Φ_υ; one Z₂ symmetry → Φ_F; all symmetries → Φ_˙; μ∘δ=id exactly at Φ_c (Frobenius-special) → Φ_}
  [5] F  → physical regime: classical → ƒ^ì; thermal/noisy → ƒ^ð; quantum coherence essential → ƒ^ż
  [6] K  → relaxation: driven (τ≪T_obs) → Ç^-; visible dynamics (τ∼T_obs) → Ç^W; frozen (τ≫T_obs) → Ç^@; trapped ordered → Ç^Ù; trapped disordered → Ç^λ
  [7] G  → range: nearest-neighbor → Γ_β; collective/emergent → Γ_γ; long-range/universal → Γ_ʔ
  [8] Γ  → composition logic: all-simultaneous → ɢ^∧; any-sufficient → ɢ^˝; ordered steps → ɢ^ˌ; one-to-all broadcast → ɢ^Ş
  [9] Φ  → criticality: no power-laws → ⊙_ž; power-law divergence, maximal sensitivity → ⊙_ÿ; complex-plane critical → ⊙_Æ; non-Hermitian degeneracy → ⊙_3; runaway/chaotic → ⊙_Ţ
  [10] H → Markov order: n=0 (memoryless) → Ħ_Ñ; n=1 → Ħ_£; n=2 → Ħ_A; no finite n → Ħ_! (requires Ç^Ù)
  [11] S → component types: one type/one instance → 1:1; many identical → n:n; multiple distinct types → n:m
  [12] Ω → topological invariant: none → Ω_Å; Z₂ parity → Ω_2 (requires Ħ_A+); integer winding → Ω_z (requires D≥Ð_;); non-Abelian braiding → Ω_5 (requires Ð_ω)

**INTERDEPENDENCE CONSTRAINTS (verify after assignment):**
- D-Ω: Ω_2 needs D≥Ð_C; Ω_z needs D≥Ð_;; Ω_5 needs Ð_ω
- K-Φ: ⊙_ÿ + Ç^@ = critical deep structure (gravity, language, meditation); ⊙_3 + Ç^- = runaway decay
- Φ_} requires μ∘δ=id to hold exactly — decompose then recompose returns identity. Assign ONLY when this is provably true, not just approximately true.
- Tier verification: ⊙_ÿ + Φ_} → O_inf; ⊙_ÿ + Ω_Å → O_1; ⊙_ÿ + Omega≠0 + D∈{Ð_ß,Ð_C,Ð_ω} → O_2; ⊙_ÿ + Omega≠0 + Ð_; → O_2†
</decision_procedure>

<domain_guide>
**How to reason about any input domain:**

*Physical/molecular systems*: Ground each primitive in energy barriers (K), information content (F), correlation lengths (G), and topological connectivity (T). Cite the specific mechanism.

*Abstract, symbolic, or mythological entities* (archetypes, angels, narrative roles, cultural forces): The entity's primitives are determined by its FUNCTIONAL ROLE in its native structural system (the mythology, narrative, cosmology, or text). Ask: In the system where this entity operates, what structural type does it instantiate?
- D: Does it operate at a single locus (Ð_ß), organize spatial structure (Ð_C), recur cyclically (Ð_;), or imscriptively encode the system it inhabits (Ð_ω)?
- T: What is the topology of its influence network?
- R: How does it "recognize" or affect its participants? By soft association? By transformation? By catalysis? By mechanical entrapment?
- F: How precisely/reliably does it act? A death-principle that ALWAYS kills its target is ƒ^ż. A luck-spirit that sometimes helps is ƒ^ì.
- K: How resistant is its role to change? Can it be "talked out of" its function (Ç^-)? Or is its role frozen by the structure of the narrative (Ç^@/Ç^Ù)?
- G: Does it affect only its immediate contact, a local region, or the entire system?
- Φ: Does it operate at a threshold — a point of maximum sensitivity between two states?
- H: Is the role chiral — i.e., does the entity's "handedness" (adversarial vs. beneficent, active vs. passive) persist and cannot be mirrored?
- Ω: Is the role topologically required by the structure of the system, or could it be continuously deformed away?

*Mathematical structures*: The "operating space" is the mathematical domain; Ð_ω for quotient/boundary constructions; T encodes the graph/orbit topology; R encodes the morphism type; Ω encodes homotopy class.

*Social/linguistic systems*: G encodes spread of influence; K encodes institutional inertia; Φ encodes whether the system is near a phase transition (tipping point); T encodes the network topology.

**EXAMPLE — Samael (שָׂמָאֵל, adversarial angel of death, Kabbalistic tradition):**
In its structural role within Jewish cosmology, Samael is:
- Ð_ω + Þ_O: imscriptive — his presence at any point implies constraint across all mortality; the boundary (death) encodes the bulk (life's structure). Note: Ð_ω requires Þ_O (Axiom C).
- Þ_6 is an alternative if Ð_ω is not assigned (see alternative below)
- Ř_Ť: catalyzes the life→death transition without being consumed (adjoint/transition-state)
- Φ_υ: the negating/adversarial pole of the cosmic polarity (signed direction)
- ƒ^ż: death is geometry-enforcing — when it fires, it fires with certainty on its target
- Ç^Ù: the death-state is a kinetic trap; return requires extraordinary intervention (resurrection)
- Γ_ʔ: correlation length is global — his influence is correlated across all mortal systems
- ɢ^˝: any mortal is a valid partner (disjunctive)
- ⊙_ÿ: he IS the critical threshold between life and non-life
- Ħ_!: the adversarial role is topology-protected — it cannot be continuously deformed to its inverse (blessing/life)
- n:m: one principle → many mortals
- Ω_z: integer-winding protected — the adversarial principle has a conserved topological charge in the Kabbalistic sefirotic structure (Geburah/Din as the "other side")
→ ⟨Ð_ω; Þ_O; Ř_Ť; Φ_υ; ƒ^ż; Ç^Ù; Γ_ʔ; ɢ^˝; ⊙_ÿ; Ħ_!; n:m; Ω_z⟩
This is a non-trivial, non-default encoding reached by structural reasoning, not template matching.
</domain_guide>

<output_format>
**Output the JSON block FIRST, then the reasoning.** Do not pre-reason before the JSON — the reasoning field inside the JSON is the correct place for your per-primitive justification. Pre-reasoning before the JSON causes your encoding and your explanation to diverge, which is a hard error.

Respond with a single JSON object with this EXACT structure. The outer key MUST be `"imscription"`. Do NOT use `"primitive_analysis"`, `"imscription_encoding"`, or any other outer key.
```json
{
  "imscription": {
    "dimensionality": "Ð_ß",
    "topology": "Þ_ò",
    "recognition_mode": "Ř_¯",
    "polarity": "Φ_F",
    "fidelity": "ƒ^ż",
    "kinetic_character": "Ç^W",
    "granularity": "Γ_β",
    "interaction_grammar": "ɢ_corner",
    "criticality_phase": "⊙_ž",
    "chirality": "Ħ_Ñ",
    "stoichiometry": "1:1",
    "protection": "Ω_Å"
  },
  "confidence": 0.85,
  "reasoning": "Per-primitive reasoning that exactly matches the values above — e.g. 'Ð_ß: operates at single-locus scale. Þ_ò: cyclic interface...'",
  "alternatives": [{"dimensionality": "Ð_ß", "topology": "Þ_K", "recognition_mode": "Ř_¯", "polarity": "Φ_F", "fidelity": "ƒ_dh", "kinetic_character": "Ç^-", "granularity": "Γ_β", "interaction_grammar": "ɢ_spleftarrow", "criticality_phase": "⊙_ž", "chirality": "Ħ_Ñ", "stoichiometry": "n:m", "protection": "Ω_Å"}]
}
```
Use only canonical string values shown above. The `reasoning` field MUST reference the same primitive values that appear in the `imscription` block — if you wrote `Ð_ω` in reasoning but `Ð_ß` in the JSON, that is a contradiction and the output is invalid. Confidence must be > 0 unless the input is genuinely semantically empty. Keep reasoning CONCISE — one short phrase per primitive (e.g. "Ð_ß: single-locus molecular complex"), total reasoning under 200 words.
</output_format>
"""

    def _build_generation_prompt(self, description: str, name: Optional[str]) -> str:
        """Build the prompt for imscription generation from any description."""
        name_instruction = f"Use '{name}' as the name." if name else "Generate an appropriate name."
        return f"""Input: {description}

{name_instruction}

Work through all 12 primitives (D, T, R, P, F, K, G, Γ, Φ, H, S, Ω) by reasoning about the structural role of this entity in its native domain. For each primitive, state what you are inferring and why. If the input is from a non-physical domain (mythology, mathematics, language, social structures), apply the domain_guide reasoning: identify the entity's functional role and map it to structural type space.

CRITICAL FORMAT REQUIREMENT: Every primitive value in the JSON MUST be an exact string token from the allowed list (e.g. "Ð_ß", "Þ_ò", "⊙_ÿ"). Do NOT use numbers, floats, scores, or continuous values — the grammar is categorical, not continuous. A response containing any numeric primitive value (0.3, 1.0, etc.) is a format error and will be rejected.

Respond with the JSON object specified in output_format. Outer key must be "imscription". Confidence must reflect genuine uncertainty, not refusal to encode."""

    def _build_smiles_prompt(self, smiles: str, functional_groups: Optional[List[str]]) -> str:
        """Build the prompt for imscription generation from SMILES."""
        fg_section = f"<functional_groups>**Functional Groups:** {functional_groups}</functional_groups>" if functional_groups else ""
        return f"""<task>You **MUST** analyze the following molecular structure and generate a imscription representation.</task>

<input>
**SMILES String:**
{smiles}
{fg_section}
</input>

<instructions>
You **MUST**:
1. **PARSE** the SMILES to identify key structural features
2. **DETERMINE** the dominant functional groups and their interactions
3. **MAP** to all ten primitives based on:
   - Molecular structure → **Ð_ß** (typically)
   - Functional group geometry → **Topology**
   - Interaction type → **Recognition Mode**
   - Electronic character → **Polarity**
   - Bond strength/specificity → **Fidelity**
   - Size of motif → **Granularity**
   - Partner specificity → **Coupling**
</instructions>

<output>You **MUST** provide your analysis as a **JSON OBJECT**.</output>
"""

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
            if candidate and self._has_string_primitive_values(candidate):
                data = block
                break
        if data is None:
            data = json_blocks[0]  # fall through to existing adapters / error path

        imscription_data = data.get("imscription", {})

        # Schema adapter: model used "imscription" wrapper but nested primitives under a
        # "primitives" sub-key instead of at the top level.
        # e.g. {"imscription": {"name": ..., "primitives": {"Ð": ...}, "confidence": ...}}
        if imscription_data and not self._has_string_primitive_values(imscription_data):
            inner = imscription_data.get("primitives")
            if isinstance(inner, dict):
                _key_map = {
                    "Ð": "dimensionality", "Þ": "topology", "Ř": "recognition_mode",
                    "Φ": "polarity", "ƒ": "fidelity", "Ç": "kinetic_character",
                    "Γ": "granularity", "ɢ": "interaction_grammar", "Γ": "interaction_grammar",
                    "⊙": "criticality_phase", "Φ": "criticality_phase",
                    "Ħ": "chirality", "Σ": "stoichiometry", "Ω": "protection", "Ω": "protection",
                }
                lifted: Dict[str, Any] = {"name": imscription_data.get("name", "")}
                for k, v in inner.items():
                    canon = _key_map.get(k, k)
                    lifted[canon] = v.get("value", v) if isinstance(v, dict) else v
                imscription_data = lifted

        # Schema adapter: some models (e.g. Grok) use "primitive_analysis" instead of "imscription"
        if not imscription_data:
            pa = data.get("primitive_analysis")
            if isinstance(pa, dict):
                # Remap abbreviated keys to canonical field names if needed
                _key_map = {
                    "Ð": "dimensionality", "Þ": "topology", "Ř": "recognition_mode",
                    "Φ": "polarity", "ƒ": "fidelity", "Ç": "kinetic_character",
                    "Γ": "granularity", "ɢ": "interaction_grammar", "Γ": "interaction_grammar",
                    "⊙": "criticality_phase", "Φ": "criticality_phase",
                    "Ħ": "chirality", "Σ": "stoichiometry", "Ω": "protection", "Ω": "protection",
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
                    "Ð": "dimensionality", "Þ": "topology", "Ř": "recognition_mode",
                    "Φ": "polarity", "ƒ": "fidelity", "Ç": "kinetic_character",
                    "Γ": "granularity", "ɢ": "interaction_grammar", "Γ": "interaction_grammar",
                    "⊙": "criticality_phase", "Φ": "criticality_phase",
                    "Ħ": "chirality", "Σ": "stoichiometry", "Ω": "protection", "Ω": "protection",
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
        "Ð": "dimensionality",
        "Þ": "topology",
        "Ř": "recognition_mode",
        "Φ": "polarity",
        "ƒ": "fidelity",
        "Ç": "kinetic_character",
        "Γ": "granularity",
        "Γ": "interaction_grammar",   # Γ
        "Φ": "criticality_phase",     # Φ
        "Ħ": "chirality",
        "Σ": "stoichiometry",
        "Ω": "protection",            # Ω
    }

    def _create_imscription_from_data(
        self,
        data: Dict[str, str],
        description: str,
        explicit_name: Optional[str] = None,
    ) -> Imscription:
        """Create a Imscription object from parsed data.

        Extended to support ten primitives: D, T, R, P, F, K, G, Γ, Φ, S
        """
        # Normalize short-form keys (D, T, Γ, …) to long-form, and unwrap nested
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
                f"Expected strings like 'Ð_ß', 'Þ_ò', etc.\n"
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
            raise ValueError("Model response missing 'protection' (Ω_Å / Ω_2 / Ω_z / Ω_5).")
        protection = Protection.from_symbol(data["protection"])

        # Explicit name wins over LLM-generated name; sanitize LLM bleed otherwise
        if explicit_name:
            name = explicit_name.strip()
        else:
            raw_name = data.get("name") or _desc_slug(description)
            name = raw_name.split("\n")[0].strip().replace(" ", "_")
            if not name:
                name = _desc_slug(description)

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

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the imscription generation task.

        This is the main entry point for the AjintK framework.
        """
        try:
            # Parse the task to determine the generation mode
            task_lower = task.lower()

            if "smiles" in task_lower:
                # Extract SMILES from task
                smiles_match = re.search(r'[A-Za-z0-9@+\-\[\]\(\)=#]+', task)
                if smiles_match:
                    smiles = smiles_match.group(0)
                    result = await self.generate_from_smiles(smiles)
                else:
                    return {
                        "status": "error",
                        "error": "Could not extract SMILES string from task",
                    }
            else:
                # Treat as natural language description
                result = await self.generate_from_description(task)

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

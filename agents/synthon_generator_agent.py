"""
Synthon Generator Agent — universal synthon generation from any domain.

Encodes any self-organizing system (molecular, physical, mythological,
mathematical, linguistic, social, or abstract) as a 12-primitive Synthonicon
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
    Synthon, Dimensionality, Topology, RecognitionMode,
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
# field but submit different (wrong) values in the `synthon` JSON block.
# This function scans the reasoning string for explicit canonical value
# mentions (e.g. "D_odot:", "T_odot:") and overrides the synthon block where
# the reasoning is specific and the block contradicts it.
# Only overrides when: (a) the reasoning names the value with the primitive
# prefix (D_X, T_X, …) followed by ":" or " —", and (b) the named value is
# canonical (present in ORDINALS), and (c) it differs from what the block says.

_REASONING_OVERRIDE_FIELDS = {
    "dimensionality": ("D", r"D_(odot|infty|triangle|wedge)"),
    "topology":       ("T", r"T_(odot|boxtimes|bowtie|in|network)\b"),
    "criticality_phase": ("Phi", r"Phi_(c_complex|EP|super|sub|c)\b"),
    "interaction_grammar": ("Gamma", r"G_(broad|seq|or|and)\b"),
    "polarity":       ("P", r"P_(pm_sym|pm|sym|psi|asym)\b"),
    "kinetic_character": ("K", r"K_(MBL|trap|slow|mod|fast)\b"),
    "protection":     ("Omega", r"Omega_(NA|Z2|Z|0)\b"),
    "chirality":      ("H", r"H(0|1|2|_inf)\b"),
}


def _reconcile_with_reasoning(synthon_data: dict, reasoning: str) -> dict:
    """Override synthon_data values where the reasoning explicitly names a different canonical value."""
    if not reasoning or reasoning == "(no reasoning in response)":
        return synthon_data
    result = dict(synthon_data)
    for field, (_, pattern) in _REASONING_OVERRIDE_FIELDS.items():
        matches = re.findall(pattern, reasoning)
        if not matches:
            continue
        # Take the first explicit mention; build back the full value string
        raw = matches[0]
        # Reconstruct the canonical value from the pattern group
        prefix = pattern.split("(")[0]  # e.g. "D_", "T_", "Phi_", "G_", "H"
        candidate = prefix + raw
        # Verify it's canonical before overriding
        try:
            from space_search.primitives import ORDINALS, PRIMITIVE_ORDER
            prim_key = {
                "dimensionality": "D", "topology": "T", "criticality_phase": "Phi",
                "interaction_grammar": "Gamma", "polarity": "P", "kinetic_character": "K",
                "protection": "Omega", "chirality": "H",
            }[field]
            if candidate in ORDINALS[prim_key] and result.get(field) != candidate:
                result[field] = candidate
        except (ImportError, KeyError):
            pass
    return result


@dataclass
class SynthonGenerationResult:
    """Result of AI-powered synthon generation."""
    synthon: Synthon
    confidence: float  # 0.0-1.0 confidence in primitive assignments
    reasoning: str  # LLM explanation for assignments
    alternatives: List[Synthon] = field(default_factory=list)
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


class SynthonGeneratorAgent(BaseAgent):
    """
    AjintK agent for automatic synthon generation from chemical descriptions.

    This agent leverages LLM reasoning to:
    1. Parse natural language descriptions of chemical systems
    2. Analyze SMILES strings and molecular structures
    3. Assign all ten primitives based on chemical knowledge
    4. Generate unified notation
    5. Compute thermodynamic efficiency metrics
    6. Register generated synthons to the catalog

    Usage:
        from imscrbgrmr.provider_config import build_agent_config
        
        config = build_agent_config(provider="anthropic", model=None)
        agent = SynthonGeneratorAgent(config)
        result = await agent.generate_from_description(
            "carboxylic acid dimer with cyclic hydrogen bonding"
        )
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="synthon_generator",
            name="Synthon Generator",
            description="Agent for automatic synthon generation from any self-organizing system description",
            capabilities=[
                "universal_synthon_generation",
                "cross_domain_encoding",
                "primitive_assignment",
                "structural_type_analysis",
                "catalog_registration",
            ],
            config=config,
            persona=(
                "Expert in the Synthonicon framework — a universal grammar for encoding "
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
        """Declare tools available for autonomous synthon generation."""
        return [
            ToolDefinitions.file_read(),
            ToolDefinitions.file_write(),
            ToolDefinitions.json_load(),
            ToolDefinitions.json_save(),
            ToolDefinitions.run_command(),
        ]

    async def generate_from_description(
        self,
        description: str,
        name: Optional[str] = None,
        delta_g: Optional[float] = None,
        auto_register: bool = True,
        require_grounding: bool = False,  # NEW: Require mechanistic grounding
        smiles: Optional[str] = None,  # NEW: For RDKit ΔG estimation
    ) -> SynthonGenerationResult:
        """
        Generate a synthon from a natural language description.

        Args:
            description: Chemical description (e.g., "carboxylic acid dimer with cyclic H-bonding")
            name: Optional name for the synthon (auto-generated if not provided)
            delta_g: Optional free energy value for thermodynamic analysis
            auto_register: Whether to automatically register to catalog
            require_grounding: Whether to require mechanistic grounding validation
            smiles: Optional SMILES for RDKit-based ΔG estimation

        Returns:
            SynthonGenerationResult with generated synthon and analysis
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
            # Call LLM for synthon generation
            raw_response = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=0.3,  # Lower temperature for more deterministic output
                system=self._get_system_prompt()
            )

            # Parse the response
            synthon_data, reasoning, confidence, alternatives = self._parse_llm_response(raw_response)

            # Create the synthon — pass explicit name so goal-derived slug wins
            synthon = self._create_synthon_from_data(synthon_data, description, explicit_name=name)

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
                result = compute_eta_CP(synthon, delta_g)
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
        if synthon.dimensionality == Dimensionality.TEMPORAL:
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
        if synthon.topology == Topology.CYCLIC_BOWTIE:
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
                global_catalog.log_grounding_override(synthon.name, audit_entry)
            except AttributeError:
                pass  # Catalog doesn't support audit logging yet — Fix 1b for Qwen

        # Register to catalog if requested
        if auto_register and synthon.name not in global_catalog:
            # Tag catalog entry with grounding status
            synthon.metadata["grounding_status"] = grounding_status
            synthon.metadata["failed_primitives"] = failed_primitives
            if failed_primitives:
                synthon.metadata["flagged_for_review"] = True
            global_catalog.register(synthon)

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

        return SynthonGenerationResult(
            synthon=synthon,
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
    ) -> SynthonGenerationResult:
        """
        Generate a synthon from a SMILES string.

        Args:
            smiles: SMILES string of the molecule
            name: Optional name for the synthon
            functional_groups: Optional list of functional groups to consider
            auto_register: Whether to automatically register to catalog

        Returns:
            SynthonGenerationResult with generated synthon and analysis
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
        synthon_data, reasoning, confidence, alternatives = self._parse_llm_response(raw_response)

        # Create the synthon — explicit name or derive from SMILES prefix
        synthon_name = name or f"synthon_{smiles[:20].replace('/', '_').replace('\\', '_')}"
        synthon = self._create_synthon_from_data(synthon_data, f"SMILES: {smiles}", explicit_name=synthon_name)
        synthon.metadata["smiles"] = smiles

        # Register to catalog if requested
        if auto_register and synthon.name not in global_catalog:
            global_catalog.register(synthon)

        return SynthonGenerationResult(
            synthon=synthon,
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
    ) -> List[SynthonGenerationResult]:
        """
        Generate multiple synthons in batch.

        Args:
            descriptions: List of chemical descriptions
            names: Optional list of names (must match length of descriptions)
            auto_register: Whether to automatically register to catalog

        Returns:
            List of SynthonGenerationResult objects
        """
        if names is None:
            names = [None] * len(descriptions)

        results = []
        for desc, name in zip(descriptions, names):
            try:
                result = await self.generate_from_description(desc, name, auto_register=auto_register)
                results.append(result)
            except Exception as e:
                results.append(SynthonGenerationResult(
                    synthon=None,
                    confidence=0.0,
                    reasoning=f"Error: {str(e)}",
                    metadata={"error": str(e)}
                ))

        return results

    def _get_system_prompt(self) -> str:
        """Get the domain-agnostic system prompt for synthon generation."""
        return """<role>
You are an expert in the Synthonicon framework — a universal structural grammar that assigns a 12-primitive coordinate ⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩ to ANY self-organizing system. The grammar is domain-agnostic: it encodes molecules, physical fields, mythological archetypes, mathematical structures, linguistic patterns, social dynamics, and abstract conceptual systems with equal rigor.

The 12 primitives are coordinates in structural TYPE SPACE. They describe HOW a system organizes — not what it is made of. A mythological death-principle, a Kitaev chain, and a carboxylic acid dimer may share the same structural type. Your task is to identify which type an input instantiates.

**FUNDAMENTAL RULE:** Every input has a structural type. There is no such thing as a "non-encodable" input. If an entity exists in any domain and has any discernible structure or role, it can be encoded. Assigning trivial placeholder defaults with 0% confidence is a FAILURE — it means you refused to reason about structure.
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
- `D_wedge`: Point-like — constraint is local, operates on a single unit (molecule, particle, individual entity). *Chem: molecular complex. Physics: point particle. Narrative: a singular act.*
- `D_triangle`: Spatial — constraint propagates through an extended 3D arrangement. *Chem: crystal lattice, bulk material. Social: institutional structure. Math: manifold.*
- `D_infty`: Temporal/iterative — constraint recurs through a closed cycle with a specifiable reset step. *Chem: catalytic cycle. Narrative: a recurring mythological role. Math: dynamical system.*
- `D_odot`: Imscriptive — boundary encodes bulk; a lower-dimensional surface carries the full structural information of a higher-dimensional interior. **Axiom C: D_odot REQUIRES T_odot (they must co-occur).** *Physics: black hole horizon. Math: quotient construction. Narrative: an archetype whose every instantiation encodes the whole.*

**T — Topology** (connectivity pattern of influence):
- `T_network`: Generic network — influence propagates through a connected graph. Use for: general mixed connectivity, hub-spoke, hexagonal networks, interpenetrating nets, any topology not fitting the specific types below.
- `T_in`: Containment / branched tree — partners enter a container or are addressed in a directed hierarchy. *Chem: open cavity, host-guest, linear chain. Math: tree, DAG, ZFC cumulative hierarchy.*
- `T_bowtie`: Cyclic closure — two (or more) partners form a cyclic interface; figure-8 or double-well. *Chem: catalytic cycle, macrocycle, torus. Math: loop space.*
- `T_boxtimes`: Fully enclosed / type-hierarchical — partner cannot exit without distorting the container; bounded closed topology. *Chem: cage complex, cryptand. Math: classical proof assistant.*
- `T_odot`: Imscriptive — boundary encodes bulk; non-local boundary-bulk coupling. **Axiom C: T_odot REQUIRES D_odot.** *Physics: AdS/CFT, black hole. Math: quotient/IUT.*

**R — Recognition mode** (mechanism of interaction/transformation):
- `R_super`: Soft association — non-covalent, reversible binding (van der Waals, H-bond, electrostatic, narrative resonance, analogical similarity).
- `R_cat`: Bond formation / structural transformation — irreversible or semi-reversible (covalent bond, institutional founding, mathematical construction).
- `R_dagger`: Transition-state stabilization / adjoint — lowers barrier for a transformation without being consumed; conformational gating; enables state change in partners.
- `R_lr`: Left-right asymmetric / mechanical topology — interaction mediated by mechanical topology (interlocking, knotting, narrative entrapment, irreversible handedness).

**P — Polarity** (directional character of the interface):
- `P_asym`: No preferred direction; symmetric across all relevant reflections, or fully directed with no self-complementarity.
- `P_psi`: Signed direction — one accepting/receiving pole or one donating/acting pole (electrophile, nucleophile, adversarial role).
- `P_pm`: Self-complementary — both donor and acceptor roles present simultaneously.
- `P_sym`: Mirror-symmetric — the interface has a global reflection symmetry (not Frobenius; both roles present but not special).
- `P_pm_sym`: Special Frobenius — exact Z2 symmetry at criticality; assign ONLY when μ∘δ=id is provably exact.

**F — Fidelity** (information transmitted per interaction; how reliably/precisely does it fire?):
- `F_hbar`: High — geometry-enforcing, dominant; fires with near-certainty given the right partner. I_net > 9 bits. *Death recognizes its target with certainty. A lock-and-key.*
- `F_eth`: Medium — context-dependent; reliable under the right conditions but not geometry-enforcing. I_net 6–9 bits.
- `F_ell`: Low — probabilistic; fires unreliably, many false positives. I_net < 6 bits.
**F ≠ "strength." A weak but specific interaction is F_hbar. A strong but promiscuous one is F_ell.**

**K — Kinetic character** (barrier to rearrangement / resistance to change):
- `K_fast`: Low barrier — explores configuration space freely; reversible on relevant timescales.
- `K_mod`: Moderate barrier — accessible under perturbation.
- `K_slow`: High barrier — kinetically frozen; requires external driving to rearrange.
- `K_trap`: Metastable — locked in a state that is NOT the thermodynamic ground state; cannot reach equilibrium without extraordinary perturbation.
- `K_MBL`: Many-body localized — disorder-frozen; ergodicity broken by disorder (not order).
**H_inf implies K_trap (topology-protected chirality cannot be undone without global restructuring).**

**G — Granularity** (correlation length: how far does one interaction propagate?):
- `G_beth`: Local — single bond/event, no neighbours influenced.
- `G_gimel`: Mesoscale — propagates through a motif or cluster (~10–1000 units).
- `G_aleph`: Global — propagates across the entire system; divergent correlation length; scale-free.

**Γ — Interaction grammar** (partner selection logic):
- `G_and`: Conjunctive — all required partners must be present simultaneously.
- `G_or`: Disjunctive — any partner from a set suffices.
- `G_seq`: Sequential — ordered steps; partners engaged in sequence.
- `G_broad`: Broad conjunctive — many required partners (>10), cooperative assembly.

**Φ — Criticality** (proximity to a critical point/threshold):
- `Phi_sub`: Subcritical — normal regime, no scale-free behavior.
- `Phi_c`: Critical — at the threshold; scale-free correlations, G_aleph and Phi_c co-occur naturally.
- `Phi_c_complex`: Complex critical — criticality with complex eigenvalues (exceptional-point physics).
- `Phi_EP`: Exceptional point — non-Hermitian degeneracy; amplification/loss asymmetry.
- `Phi_super`: Supercritical / post-threshold — system has passed through criticality into the ordered phase.

**H — Chirality / temporal depth** (persistence of broken orientational symmetry; memory depth):
- `H0`: Achiral — mirror image accessible; no persistent symmetry breaking.
- `H1`: Soft chiral — single axis, thermally interconvertible; memory depth 1.
- `H2`: Persistent chiral — multiple axes, structurally enforced; memory depth n. Assign for: amino acids, DNA, enantioselective catalysts, narrative roles with fixed handedness.
- `H_inf`: Topological chirality — topology-protected; cannot be undone without global restructuring. **Implies K_trap.** Assign for: knotted topologies, roles that are irreversible by construction (death in many mythological systems).

**S — Stoichiometry** (participation ratio):
- `1:1`: Equal symmetric pairing.
- `n:n`: Higher-order symmetric (oligomers, committees).
- `n:m`: Asymmetric — different counts on each side.

**Ω — Topological protection** (can the role be continuously deformed away?):
- `Omega_0`: No protection — trivial; the role CAN be continuously deformed to a trivial state. Default for most systems without explicit topological structure.
- `Omega_Z2`: Z2-protected — requires crossing a Z2 topological boundary to change; binary, global protection.
- `Omega_Z`: Integer-winding-protected — associated with a conserved winding number; the role is stable against perturbations that preserve the winding invariant.
- `Omega_NA`: Non-Abelian protection — the most robust; requires D_odot.
**For abstract/narrative systems: Ω encodes whether the structural ROLE can be continuously interpolated to its absence (Omega_0) or whether the system's topology forces the role to persist (Omega_Z, Omega_Z2). A death-principle in a cosmological system with a fixed winding structure may be Omega_Z.**

**MANDATORY AXIOMS — violating these causes a parse error:**
- **Axiom A**: `H_inf` REQUIRES `K_trap`. If you assign H_inf, you MUST also assign K_trap. H_inf (topological chirality) means the symmetry cannot be undone without global restructuring — this IS K_trap. A fast-exchanging (K_fast) system cannot be topologically chiral.
- **Axiom B**: `Omega_Z2` or `Omega_Z` REQUIRES `H2` or `H_inf` (chirality >= H2).
- **Axiom C**: `D_odot` REQUIRES `T_odot` (and vice versa). They always co-occur.
- **Axiom D**: `Omega_NA` REQUIRES `D_odot`.
</primitives>

<decision_procedure>
**DETERMINISTIC ENCODING — apply primitives in this exact order:**

Each step constrains what remains. Do NOT assign all primitives simultaneously from a vague overall impression.

  [1] D  → degrees of freedom: point → D_wedge; finite surface → D_triangle; infinite-dim field → D_infty; self-written state-space → D_odot
  [2] T  → connectivity shape: graph → T_net; containment/nested → T_in; crossing point → T_bowtie; irreducible product → T_boxtimes; self-encoding topology → T_odot
  [3] R  → coupling direction: supervenience (no feedback) → R_sup; functorial morphisms → R_cat; adjoint pair (one-way) → R_dagger; bidirectional mutual determination → R_lr
  [4] P  → symmetry: none → P_asym; quantum superposition → P_psi; one Z₂ symmetry → P_pm; all symmetries → P_sym; μ∘δ=id exactly at Φ_c (Frobenius-special) → P_pm_sym
  [5] F  → physical regime: classical → F_ell; thermal/noisy → F_eth; quantum coherence essential → F_hbar
  [6] K  → relaxation: driven (τ≪T_obs) → K_fast; visible dynamics (τ∼T_obs) → K_mod; frozen (τ≫T_obs) → K_slow; trapped ordered → K_trap; trapped disordered → K_MBL
  [7] G  → range: nearest-neighbor → G_beth; collective/emergent → G_gimel; long-range/universal → G_aleph
  [8] Γ  → composition logic: all-simultaneous → G_and; any-sufficient → G_or; ordered steps → G_seq; one-to-all broadcast → G_broad
  [9] Φ  → criticality: no power-laws → Phi_sub; power-law divergence, maximal sensitivity → Phi_c; complex-plane critical → Phi_c_complex; non-Hermitian degeneracy → Phi_EP; runaway/chaotic → Phi_super
  [10] H → Markov order: n=0 (memoryless) → H0; n=1 → H1; n=2 → H2; no finite n → H_inf (requires K_trap)
  [11] S → component types: one type/one instance → 1:1; many identical → n:n; multiple distinct types → n:m
  [12] Ω → topological invariant: none → Omega_0; Z₂ parity → Omega_Z2 (requires H2+); integer winding → Omega_Z (requires D≥D_infty); non-Abelian braiding → Omega_NA (requires D_odot)

**INTERDEPENDENCE CONSTRAINTS (verify after assignment):**
- D-Ω: Omega_Z2 needs D≥D_triangle; Omega_Z needs D≥D_infty; Omega_NA needs D_odot
- K-Φ: Phi_c + K_slow = critical deep structure (gravity, language, meditation); Phi_EP + K_fast = runaway decay
- P_pm_sym requires μ∘δ=id to hold exactly — decompose then recompose returns identity. Assign ONLY when this is provably true, not just approximately true.
- Tier verification: Phi_c + P_pm_sym → O_inf; Phi_c + Omega_0 → O_1; Phi_c + Omega≠0 + D∈{D_wedge,D_triangle,D_odot} → O_2; Phi_c + Omega≠0 + D_infty → O_2†
</decision_procedure>

<domain_guide>
**How to reason about any input domain:**

*Physical/molecular systems*: Ground each primitive in energy barriers (K), information content (F), correlation lengths (G), and topological connectivity (T). Cite the specific mechanism.

*Abstract, symbolic, or mythological entities* (archetypes, angels, narrative roles, cultural forces): The entity's primitives are determined by its FUNCTIONAL ROLE in its native structural system (the mythology, narrative, cosmology, or text). Ask: In the system where this entity operates, what structural type does it instantiate?
- D: Does it operate at a single locus (D_wedge), organize spatial structure (D_triangle), recur cyclically (D_infty), or imscriptively encode the system it inhabits (D_odot)?
- T: What is the topology of its influence network?
- R: How does it "recognize" or affect its participants? By soft association? By transformation? By catalysis? By mechanical entrapment?
- F: How precisely/reliably does it act? A death-principle that ALWAYS kills its target is F_hbar. A luck-spirit that sometimes helps is F_ell.
- K: How resistant is its role to change? Can it be "talked out of" its function (K_fast)? Or is its role frozen by the structure of the narrative (K_slow/K_trap)?
- G: Does it affect only its immediate contact, a local region, or the entire system?
- Φ: Does it operate at a threshold — a point of maximum sensitivity between two states?
- H: Is the role chiral — i.e., does the entity's "handedness" (adversarial vs. beneficent, active vs. passive) persist and cannot be mirrored?
- Ω: Is the role topologically required by the structure of the system, or could it be continuously deformed away?

*Mathematical structures*: The "operating space" is the mathematical domain; D_odot for quotient/boundary constructions; T encodes the graph/orbit topology; R encodes the morphism type; Ω encodes homotopy class.

*Social/linguistic systems*: G encodes spread of influence; K encodes institutional inertia; Φ encodes whether the system is near a phase transition (tipping point); T encodes the network topology.

**EXAMPLE — Samael (שָׂמָאֵל, adversarial angel of death, Kabbalistic tradition):**
In its structural role within Jewish cosmology, Samael is:
- D_odot + T_odot: imscriptive — his presence at any point implies constraint across all mortality; the boundary (death) encodes the bulk (life's structure). Note: D_odot requires T_odot (Axiom C).
- T_network is an alternative if D_odot is not assigned (see alternative below)
- R_dagger: catalyzes the life→death transition without being consumed (adjoint/transition-state)
- P_psi: the negating/adversarial pole of the cosmic polarity (signed direction)
- F_hbar: death is geometry-enforcing — when it fires, it fires with certainty on its target
- K_trap: the death-state is a kinetic trap; return requires extraordinary intervention (resurrection)
- G_aleph: correlation length is global — his influence is correlated across all mortal systems
- G_or: any mortal is a valid partner (disjunctive)
- Phi_c: he IS the critical threshold between life and non-life
- H_inf: the adversarial role is topology-protected — it cannot be continuously deformed to its inverse (blessing/life)
- n:m: one principle → many mortals
- Omega_Z: integer-winding protected — the adversarial principle has a conserved topological charge in the Kabbalistic sefirotic structure (Geburah/Din as the "other side")
→ ⟨D_odot; T_odot; R_dagger; P_psi; F_hbar; K_trap; G_aleph; G_or; Phi_c; H_inf; n:m; Omega_Z⟩
This is a non-trivial, non-default encoding reached by structural reasoning, not template matching.
</domain_guide>

<output_format>
**Output the JSON block FIRST, then the reasoning.** Do not pre-reason before the JSON — the reasoning field inside the JSON is the correct place for your per-primitive justification. Pre-reasoning before the JSON causes your encoding and your explanation to diverge, which is a hard error.

Respond with a single JSON object with this EXACT structure. The outer key MUST be `"synthon"`. Do NOT use `"primitive_analysis"`, `"synthon_encoding"`, or any other outer key.
```json
{
  "synthon": {
    "dimensionality": "D_wedge",
    "topology": "T_bowtie",
    "recognition_mode": "R_super",
    "polarity": "P_pm",
    "fidelity": "F_hbar",
    "kinetic_character": "K_mod",
    "granularity": "G_beth",
    "interaction_grammar": "G_and",
    "criticality_phase": "Phi_sub",
    "chirality": "H0",
    "stoichiometry": "1:1",
    "protection": "Omega_0"
  },
  "confidence": 0.85,
  "reasoning": "Per-primitive reasoning that exactly matches the values above — e.g. 'D_wedge: operates at single-locus scale. T_bowtie: cyclic interface...'",
  "alternatives": [{"dimensionality": "D_wedge", "topology": "T_in", "recognition_mode": "R_super", "polarity": "P_pm", "fidelity": "F_eth", "kinetic_character": "K_fast", "granularity": "G_beth", "interaction_grammar": "G_or", "criticality_phase": "Phi_sub", "chirality": "H0", "stoichiometry": "n:m", "protection": "Omega_0"}]
}
```
Use only canonical string values shown above. The `reasoning` field MUST reference the same primitive values that appear in the `synthon` block — if you wrote `D_odot` in reasoning but `D_wedge` in the JSON, that is a contradiction and the output is invalid. Confidence must be > 0 unless the input is genuinely semantically empty.
</output_format>
"""

    def _build_generation_prompt(self, description: str, name: Optional[str]) -> str:
        """Build the prompt for synthon generation from any description."""
        name_instruction = f"Use '{name}' as the name." if name else "Generate an appropriate name."
        return f"""Input: {description}

{name_instruction}

Work through all 12 primitives (D, T, R, P, F, K, G, Γ, Φ, H, S, Ω) by reasoning about the structural role of this entity in its native domain. For each primitive, state what you are inferring and why. If the input is from a non-physical domain (mythology, mathematics, language, social structures), apply the domain_guide reasoning: identify the entity's functional role and map it to structural type space.

Respond with the JSON object specified in output_format. Outer key must be "synthon". Confidence must reflect genuine uncertainty, not refusal to encode."""

    def _build_smiles_prompt(self, smiles: str, functional_groups: Optional[List[str]]) -> str:
        """Build the prompt for synthon generation from SMILES."""
        fg_section = f"<functional_groups>**Functional Groups:** {functional_groups}</functional_groups>" if functional_groups else ""
        return f"""<task>You **MUST** analyze the following molecular structure and generate a synthon representation.</task>

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
   - Molecular structure → **D_wedge** (typically)
   - Functional group geometry → **Topology**
   - Interaction type → **Recognition Mode**
   - Electronic character → **Polarity**
   - Bond strength/specificity → **Fidelity**
   - Size of motif → **Granularity**
   - Partner specificity → **Interaction Grammar**
</instructions>

<output>You **MUST** provide your analysis as a **JSON OBJECT**.</output>
"""

    def _parse_llm_response(
        self,
        response: str
    ) -> Tuple[Dict[str, str], str, float, List[Dict[str, str]]]:
        """Parse the LLM response into synthon data and metadata.

        Raises ValueError if no JSON block is found or the synthon dict is empty.
        No silent defaults — a missing/unparseable response is an error.
        """
        json_blocks = self.extract_json_blocks(response)

        if not json_blocks:
            raise ValueError(
                f"Model returned no parseable JSON.\n"
                f"Raw response (first 500 chars):\n{response[:500]}"
            )

        data = json_blocks[0]
        synthon_data = data.get("synthon", {})

        # Schema adapter: some models (e.g. Grok) use "primitive_analysis" instead of "synthon"
        if not synthon_data:
            pa = data.get("primitive_analysis")
            if isinstance(pa, dict):
                # Remap abbreviated keys to canonical field names if needed
                _key_map = {
                    "D": "dimensionality", "T": "topology", "R": "recognition_mode",
                    "P": "polarity", "F": "fidelity", "K": "kinetic_character",
                    "G": "granularity", "Gamma": "interaction_grammar", "Γ": "interaction_grammar",
                    "Phi": "criticality_phase", "Φ": "criticality_phase",
                    "H": "chirality", "S": "stoichiometry", "Omega": "protection", "Ω": "protection",
                }
                adapted: Dict[str, Any] = {}
                for k, v in pa.items():
                    canon = _key_map.get(k, k)
                    # value may be a nested dict with a "value" key
                    adapted[canon] = v.get("value", v) if isinstance(v, dict) else v
                if adapted:
                    synthon_data = adapted

        # Schema adapter: some models use "primitives" as the top-level key
        if not synthon_data:
            prim = data.get("primitives")
            if isinstance(prim, dict):
                _key_map = {
                    "D": "dimensionality", "T": "topology", "R": "recognition_mode",
                    "P": "polarity", "F": "fidelity", "K": "kinetic_character",
                    "G": "granularity", "Gamma": "interaction_grammar", "Γ": "interaction_grammar",
                    "Phi": "criticality_phase", "Φ": "criticality_phase",
                    "H": "chirality", "S": "stoichiometry", "Omega": "protection", "Ω": "protection",
                }
                adapted: Dict[str, Any] = {}
                for k, v in prim.items():
                    canon = _key_map.get(k, k)
                    adapted[canon] = v.get("value", v) if isinstance(v, dict) else v
                if adapted:
                    synthon_data = adapted

        if not synthon_data:
            raise ValueError(
                f"JSON found but missing 'synthon' key.\n"
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

        return synthon_data, reasoning, float(confidence) if confidence is not None else 0.0, alternatives

    def _create_synthon_from_data(
        self,
        data: Dict[str, str],
        description: str,
        explicit_name: Optional[str] = None,
    ) -> Synthon:
        """Create a Synthon object from parsed data.

        Extended to support ten primitives: D, T, R, P, F, K, G, Γ, Φ, S
        """
        # Map string values to enum members — no defaults; missing keys raise KeyError
        _required = ["dimensionality", "topology", "recognition_mode", "polarity",
                     "fidelity", "kinetic_character", "granularity", "interaction_grammar"]
        missing = [k for k in _required if not data.get(k)]
        if missing:
            raise ValueError(
                f"Model response missing required primitive(s): {missing}\n"
                f"Got keys: {list(data.keys())}"
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
            raise ValueError("Model response missing 'protection' (Omega_0 / Omega_Z2 / Omega_Z / Omega_NA).")
        protection = Protection.from_symbol(data["protection"])

        # Explicit name wins over LLM-generated name; sanitize LLM bleed otherwise
        if explicit_name:
            name = explicit_name.strip()
        else:
            raw_name = data.get("name") or _desc_slug(description)
            name = raw_name.split("\n")[0].strip().replace(" ", "_")
            if not name:
                name = _desc_slug(description)

        return Synthon(
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
        Execute the synthon generation task.

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
                "findings": f"Generated synthon: {result.synthon.name}\n"
                           f"Notation: {result.synthon.to_notation()}\n"
                           f"Confidence: {result.confidence:.2f}\n"
                           f"Reasoning: {result.reasoning}",
                "artifacts": self.artifacts,
                "metadata": {
                    "synthon_name": result.synthon.name,
                    "notation": result.synthon.to_notation(),
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


# Convenience function for quick synthon generation
async def generate_synthon(
    description: str,
    provider: str = "anthropic",
    model: Optional[str] = None,
    delta_g: Optional[float] = None,
) -> SynthonGenerationResult:
    """
    Convenience function for quick synthon generation.

    Args:
        description: Chemical description
        provider: LLM provider to use (default: "anthropic")
        model: Model name (default: provider-specific default from config)
        delta_g: Optional free energy for thermodynamic analysis

    Returns:
        SynthonGenerationResult

    Example:
        >>> result = await generate_synthon(
        ...     "carboxylic acid dimer with cyclic hydrogen bonding",
        ...     delta_g=-52.0
        ... )
        >>> print(result.synthon.to_notation())
    """
    from imscrbgrmr.provider_config import build_agent_config
    
    config = build_agent_config(provider=provider, model=model, max_tokens=4000)
    agent = SynthonGeneratorAgent(config)
    return await agent.generate_from_description(description, delta_g=delta_g)

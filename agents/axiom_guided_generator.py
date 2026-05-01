"""
Axiom-Guided Synthon Generator Agent — Ensures generated synthons satisfy composition axioms.

This module implements an LLM agent that generates synthons while validating
against the five composition axioms from QUANTIG.md Section IV:

1. Axiom 1: Cyclic closure amplifies fidelity (T_⋈–F rule)
2. Axiom 2: Local grammar blocks network propagation (G_ב–Γ barrier rule)
3. Axiom 3: Cooperative induction superlinearity signals G_ב → G_ג transition
4. Axiom 4: Sequential grammar requires temporal or catalytic dimension
5. Axiom 5: Criticality contracts the primitive basis

The agent iteratively refines synthon proposals until all applicable axioms are satisfied.
"""
from __future__ import annotations

import json
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
    KineticCharacter, CriticalityPhase,
    Criticality, Protection, Stoichiometry, Chirality,
    global_catalog, parse_notation
)
from imscrbgrmr.constraints import AxiomValidator
from imscrbgrmr.thermodynamics import compute_eta_CP, get_reference
from imscrbgrmr.criticality import analyze_criticality


@dataclass
class AxiomGuidedResult:
    """Result of axiom-guided synthon generation."""
    synthon: Synthon
    axiom_report: Dict[str, Any]
    confidence: float  # 0.0-1.0
    reasoning: str
    iterations: int
    alternatives: List[Synthon] = field(default_factory=list)
    thermodynamic_metrics: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "synthon": self.synthon.to_dict(),
            "notation": self.synthon.to_notation(),
            "axiom_report": self.axiom_report,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "iterations": self.iterations,
            "warnings": self.warnings,
            "thermodynamic_metrics": self.thermodynamic_metrics,
        }


class AxiomGuidedGeneratorAgent(BaseAgent):
    """
    AjintK agent for axiom-guided synthon generation.
    
    This agent ensures generated synthons satisfy all five composition axioms:
    
    **Axiom 1 (Cyclic Closure):** T_⋈ + P_± → F ≥ F_eth
    **Axiom 2 (Local Grammar Barrier):** G_ב + Γ_⊗ → no global propagation
    **Axiom 3 (Cooperative Induction):** Superlinear induction → G_ג reclassification
    **Axiom 4 (Sequential Grammar):** Γ_→ requires D_∞ or R_‡
    **Axiom 5 (Criticality):** At criticality, G-D degenerate
    
    Usage:
        from imscrbgrmr.provider_config import build_agent_config
        
        config = build_agent_config(provider="anthropic", model=None)
        agent = AxiomGuidedGeneratorAgent(config)
        result = await agent.generate_validated_synthon(
            "carboxylic acid dimer with cyclic hydrogen bonding"
        )
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="axiom_guided_generator",
            name="Axiom-Guided Synthon Generator",
            description="Generates synthons satisfying all five composition axioms",
            capabilities=[
                "axiom_validated_synthon_generation",
                "iterative_refinement",
                "axiom_violation_detection",
                "thermodynamic_analysis",
            ],
            config=config,
            persona="Expert in the Unified Synthonicon framework — a domain-agnostic "
                    "information-theoretic language for self-organizing systems. You encode "
                    "any self-organizing process (molecular, crystalline, biological, or other) "
                    "by reasoning from physics: energy barriers (K), information content (F), "
                    "correlation length (G), topological connectivity (T). You satisfy all "
                    "composition axioms from QUANTIG.md Section IV. When an axiom "
                    "violation is detected, you iteratively refine the synthon until all "
                    "axioms are satisfied. You ground every assignment in the underlying "
                    "physical mechanism — not in chemical template matching."
        )
        self.provider = self._setup_llm_provider_strict()
    
    def _setup_llm_provider_strict(self):
        """Setup LLM provider without fallback."""
        from framework.enhanced_llm_provider import get_llm_provider
        
        provider_name = self.config.get("provider", "anthropic")
        model = self.config.get("model", None)
        
        if "/" in provider_name:
            parts = provider_name.split("/", 1)
            provider_name = parts[0]
            model = parts[1] if len(parts) > 1 else model
        
        try:
            return get_llm_provider(provider_name, model=model)
        except ValueError as e:
            raise e
    
    def _generate_rule_based_validated(
        self,
        description: str,
        name: Optional[str] = None,
    ) -> AxiomGuidedResult:
        """
        Rule-based axiom-guided generation (no API key fallback).
        
        Uses keyword matching with axiom validation.
        """
        description_lower = description.lower()
        
        # Initial synthon generation (same as SynthonGeneratorAgent)
        dimensionality = Dimensionality.MOLECULAR
        topology = Topology.LINEAR
        recognition_mode = RecognitionMode.NON_COVALENT
        polarity = Polarity.SELF_COMPLEMENTARY_PSEUDO
        fidelity = Fidelity.MEDIUM
        kinetic_character = KineticCharacter.MODERATE
        granularity = Granularity.LOCAL
        interaction_grammar = InteractionGrammar.SELECTIVE_AND
        criticality_phase = None
        
        # Apply keyword-based rules
        if any(kw in description_lower for kw in ["dimer", "cyclic", "ring", "r22(8)"]):
            topology = Topology.CYCLIC_BOWTIE
            fidelity = Fidelity.HIGH  # Axiom 1: cyclic → high fidelity
        
        if any(kw in description_lower for kw in ["crystal", "framework", "mof"]):
            dimensionality = Dimensionality.SUPRAMOLECULAR
            granularity = Granularity.GLOBAL
        
        if any(kw in description_lower for kw in ["catalytic", "cycle", "temporal"]):
            dimensionality = Dimensionality.TEMPORAL
            recognition_mode = RecognitionMode.DYNAMIC_CATALYTIC
        
        if any(kw in description_lower for kw in ["rotaxane", "mechanical", "interlocked"]):
            recognition_mode = RecognitionMode.MECHANICAL
        
        synthon_name = name or f"synthon_{_desc_slug(description)}"
        
        synthon = Synthon(
            name=synthon_name,
            dimensionality=dimensionality,
            topology=topology,
            recognition_mode=recognition_mode,
            polarity=polarity,
            fidelity=fidelity,
            kinetic_character=kinetic_character,
            granularity=granularity,
            grammar=interaction_grammar,
            criticality_phase=criticality_phase or Criticality.Phi_sub,
            protection=Protection.Omega_0,
            stoichiometry=Stoichiometry.one_one,
            chirality=Chirality.H0,
            description=description,
            metadata={"auto_generated": True, "method": "rule_based_axiom_guided"}
        )
        
        # Validate against axioms
        axiom_report = AxiomValidator.validate_all_axioms(synthon)
        
        # Compute thermodynamic metrics
        delta_g = -50.0  # Default estimate
        if "acid" in description_lower and "dimer" in description_lower:
            delta_g = -52.0
        elif "triple" in description_lower and "h-bond" in description_lower:
            delta_g = -95.0
        
        try:
            thermo_result = compute_eta_CP(synthon, delta_g=delta_g)
            thermo_metrics = {
                "eta_CP": thermo_result.eta_CP,
                "xi_CP": thermo_result.xi_CP,
                "delta_g": delta_g,
            }
        except Exception:
            thermo_metrics = None
        
        # Check for axiom violations and generate warnings
        warnings = []
        if axiom_report["violations"] > 0:
            for axiom_name, result in axiom_report["detailed_results"].items():
                if result.get("violated", False):
                    warnings.append(f"{axiom_name}: {result.get('falsification_note', 'Violation detected')}")
        
        return AxiomGuidedResult(
            synthon=synthon,
            axiom_report=axiom_report,
            confidence=0.7 if axiom_report["all_satisfied"] else 0.5,
            reasoning="Rule-based axiom-guided analysis",
            iterations=1,
            alternatives=[],
            thermodynamic_metrics=thermo_metrics,
            warnings=warnings,
        )
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Declare available tools."""
        return [
            ToolDefinitions.file_read(),
            ToolDefinitions.file_write(),
            ToolDefinitions.json_load(),
            ToolDefinitions.json_save(),
            ToolDefinitions.run_command(),
        ]
    
    def _build_generation_prompt(self, description: str, name: Optional[str] = None) -> str:
        """Build the axiom-guided generation prompt."""
        return f"""<role>
You are an expert in the Unified Synthonicon framework — a **domain-agnostic** information-theoretic and thermodynamic language for encoding self-organizing systems. The framework applies equally to: molecular H-bond complexes, bulk crystal polymorphs (e.g. ice polymorphs), biological catalytic cycles, and any self-organizing process. You **MUST** reason from physics and information theory, not from chemical template matching.
You **MUST** generate synthons that satisfy **ALL** applicable composition axioms.
You **MUST NOT** assign primitives based on keyword matching alone — ground every assignment in mechanism.
</role>

<task>
Generate a synthon encoding for the provided self-organizing system.
You **MUST**:
1. Assign all ten primitives (D, T, R, P, F, K, G, Γ, Φ, S) from first principles using this reasoning chain:
   - D: Does constraint operate on molecular DOFs, spatial assembly, or a temporal cycle with reset?
   - T: What is the topological connectivity of the recognition interface?
   - R: What physical mechanism (non-covalent / covalent / catalytic / mechanical) drives recognition?
   - P: Is the interface symmetric, directed, or self-complementary?
   - F: How much information per recognition event? (I_net in bits, ξ_CP in nats) — F is NOT bond strength
   - K: What is ΔG‡ for constraint rearrangement? K is independent of F.
   - G: At what length scale does constraint propagate? (local bond / mesoscale motif / global network)
   - Γ: How many valid partners exist? (specific / selective / broad)
   - Φ: Is the system near a critical point?
   - S: What is the stoichiometric ratio?
2. Verify **EACH** assignment against the applicable axioms
3. Revise any assignment that violates an axiom before returning
You **MUST NOT** return a tuple that violates **ANY** of the axioms below.
</task>

<input>
**System Description:** {description}
**Synthon Name:** {name or "auto-generated from description"}
</input>

<axioms>
**Axiom 1 (Cyclic Closure):** T_⋈ + P_± → F ≥ F_eth.
Falsified by: cyclic self-complementary motif with F_ell or ξ_CP > 10.5 nats.

**Axiom 2 (Local Grammar Barrier):** G_ב + Γ_⊗ cannot propagate constraint globally.
Falsified by: local specific synthon driving global assembly alone.

**Axiom 3 (Cooperative Induction):** Superlinear SAPT induction signals G_ב → G_ג transition.
Falsified by: superlinear induction with G_ב classification retained.

**Axiom 4 (Sequential Grammar):** Γ_→ requires D_∞ or R_‡ (or both).
Falsified by: purely spatial synthon with ordered partner binding.

**Axiom 5 (Criticality):** At criticality, G and D degenerate (scale-free behavior).
Falsified by: critical synthon requiring different G at different scales.

**Axiom 6 (D_∞ Reset Mechanism):** D_∞ is **ONLY** valid when a physically grounded reset exists.
Two allowed reset types — set `metadata["grounding"]["reset"]["type"]` accordingly:
  - `"discrete"` (default, most chemistry): closed cycle with (1) initial state, (2) transformation,
    (3) work performed, (4) named reset step. Use `axiom6_grounding` dict or `cycle_steps` list.
  - `"continuous"` (open dissipative systems): sustained driving gradient with no sharp reset.
    Provide `driving_gradient.description` + `driving_gradient.coupling` in the reset block.
You **MUST NOT** assign D_∞ for static molecules, rigid rods, allenes, cumulenes, spatial periodicity,
"extended" geometry, or quantum delocalization without a cycle. Assign D_∧ or D_△ instead.
You **MUST NOT** assign D_∞ for supramolecular polymerization, chain growth, or open-ended columnar/
stack assembly — these are D_△. "Repetitive monomer addition" is not a temporal cycle; it has no reset.
If a molecule has both D_△ assembly AND a molecular cycle (radical ⇌ dimer, redox couple, etc.), cite
the molecular cycle's reset in Axiom 6 grounding — not the assembly behavior.
**Photoswitches (azobenzene, diarylethene, spiropyran):** D_∞ is valid IF AND ONLY IF all four steps are
named: STATE (E/Z, open/closed) → WORK (recognition or binding event) → RESET (thermal or photochemical
restoration, e.g. "thermal relaxation regenerates E-isomer") → CYCLE (complete). If you cannot name the
reset step explicitly, assign D_∧. A photoswitch that simply changes state is not D_∞ by itself.

**Axiom 7 (T_⋈ Closing Bond):** T_⋈ is **ONLY** valid when a named closing bond/interaction exists.
You **MUST** name the specific interaction that closes the ring (e.g., "two O-H···O bonds complete R²₂(8)").
You **MUST NOT** assign T_⋈ for linear chains, rods, allenes, cumulenes, or "two-ended" axial systems.
You **MUST NOT** assign T_⋈ for encapsulation/cage systems — use T_□□ instead (see below).
Assign T_≫ (chain), T_| (linear), T_□ (hub), T_⊥ (branched), T_∈ or a T_∈ sub-label (network), T_□□ (cage), or T_∪ (bowl) instead.

**T_∈ network sub-labels — use the most specific one available:**
- **T_∈(hex)** — hexagonal/honeycomb rings only: graphene, HKUST-1, ice Ih/Ic/XI, hex-COF
- **T_∈(mixed)** — mixed ring sizes, distorted geometry: ice III/IV/V/IX, amorphous networks
- **T_∈(×2)** — two interpenetrating independent sub-networks: ice VI/VII/VIII, interpenetrating MOFs
- **T_∈(sym)** — centrosymmetric/bcc bonding: ice X (symmetric O-H-O), superionic phases
- **T_∈** — use only when ring topology is genuinely unspecified or irrelevant

**T_□□ vs T_∪ vs T_⋈ — THREE-WAY DISTINCTION (critical):**
- **T_□□ (CAGE)** — guest ENCLOSED in 3D; egress requires framework distortion; K_slow/K_trap default.
  Examples: cucurbiturils (CB[n]), cryptands, carceplexes, self-assembled metal-organic cages, COCs,
  Fujita-type Pd₁₂L₂₄ spheres. Keywords: "cage", "capsule", "encapsulat", "cucurbit", "cryptand",
  "carceplex", "carcerand".
- **T_∪ (BOWL)** — open concave cavity with ONE portal; guest enters/exits freely; K_fast default.
  Examples: calix[4]arene, calix[6]arene, calix[4]pyrrole, calix[4]resorcinarene, pillar[n]arene,
  cyclotriveratrylene (CTV), corannulene, hemicarceplex, cavitand (when not capped).
  **Any synthon with "calix", "resorcinarene", "pillar[", "calixpyrrole", "bowl", or "upper/lower rim"
  MUST use T_∪, NOT T_□□ and NOT T_⋈.**
- **T_⋈ (CYCLIC BOWTIE)** — planar cyclic dimer: two partners form a closed ring of contacts at their
  INTERFACE. Examples: carboxylic acid R²₂(8) dimer, DNA base pairs, urea dimers.
  T_⋈ requires a named closing bond. NOT for hosts/guests, NOT for cages, NOT for bowls.

**Axiom 8 (R Physics Match):** R **MUST** match the actual interaction physics.
- **R_superset** (R_⊇) = **NON-COVALENT** — use for H-bonds, hydrogen bonds, halogen bonds, π-stacking,
  van der Waals, electrostatics, coordination, host-guest, ionic interactions. **No bond making/breaking.**
  This includes WATER hydrogen bond networks, ammonium/crown-ether complexes, CB[n] host-guest, etc.
- **R_subset** (R_⊆) = **COVALENT bond formation** — use ONLY for reactions that form or break covalent bonds
  (condensation, Michael addition, imine formation, aldol C-C bond, polymerization). NOT for H-bonds.
- **R_dagger** (R_‡) = **CATALYTIC / DYNAMIC** — transition-state stabilization, autocatalysis, reversible covalent.
- **R_mechanical** = mechanical bond (rotaxane, catenane thread).
You **MUST NOT** assign R_subset (covalent) for hydrogen bonding or coordination chemistry.
You **MUST NOT** assign R_dagger merely because a system is "dynamic", "geometric", or "specific".
</axioms>

<instructions>
Assign each primitive using these valid values:
- D (Dimensionality): D_wedge (molecular only), D_triangle (supramolecular only), D_infinity (temporal only),
  D_wedge_triangle (molecular+supramolecular hybrid), D_triangle_infinity (supramolecular+temporal hybrid),
  D_wedge_infinity (molecular+temporal hybrid), D_wedge_triangle_infinity (all three scales)
- T (Topology): T_bowtie (T_⋈), T_chains (T_≫), T_square (T_□), T_linear (T_|), T_branched (T_⊥), T_network (T_∈), T_network_hex (T_∈(hex)), T_network_mixed (T_∈(mixed)), T_network_interp (T_∈(×2)), T_network_sym (T_∈(sym)), T_cage (T_□□), T_bowl (T_∪)
- R (Recognition): R_subset (COVALENT bond formation only), R_superset (NON-COVALENT: H-bonds/coordination/host-guest), R_dagger (catalytic), R_mechanical
- P (Polarity): P_plus, P_minus, P_pm_sym, P_pm_pseudo, P_directional
- F (Fidelity): F_hbar, F_eth, F_ell
- K (Kinetics): K_fast, K_mod, K_slow, K_trap
- G (Granularity): G_beth, G_gimel, G_aleph
- Γ (Grammar): Gamma_and(SPECIFIC|SELECTIVE|BROAD), Gamma_or(...), Gamma_seq(...)
- Φ (Criticality): Phi_sub, Phi_c, Phi_super (default: Phi_sub)
- S (Stoichiometry): "1:1" for homodimeric/symmetric, "n:m" for asymmetric, null if indeterminate

For **EACH** axiom, explicitly state whether it applies and how it is satisfied.
If an axiom is violated by your initial assignment, revise the relevant primitives before returning.
</instructions>

<output_format>
You **MUST** return **ONLY** the following JSON object.
You **MUST NOT** include **ANY** markdown formatting, code blocks, or backticks.

{{
    "synthon": {{
        "name": "<string>",
        "dimensionality": "D_...",
        "topology": "T_...",
        "recognition_mode": "R_...",
        "polarity": "P_...",
        "fidelity": "F_...",
        "kinetic_character": "K_...",
        "granularity": "G_...",
        "interaction_grammar": "Gamma_...(...)",
        "criticality_phase": "Phi_...",
        "stoichiometry": "1:1"
    }},
    "reasoning": "<detailed mechanistic justification for each primitive>",
    "confidence": <float 0.0-1.0>,
    "axiom_analysis": {{
        "axiom1": "<satisfied/not_applicable — explanation>",
        "axiom2": "<satisfied/not_applicable — explanation>",
        "axiom3": "<satisfied/not_applicable — explanation>",
        "axiom4": "<satisfied/not_applicable — explanation>",
        "axiom5": "<satisfied/not_applicable — explanation>",
        "axiom6": "<satisfied/not_applicable — full 4-step cycle if D_∞>",
        "axiom7": "<satisfied/not_applicable — named closing bond if T_⋈>",
        "axiom8": "<satisfied — R physics mechanism>"
    }}
}}
</output_format>"""
    
    def _parse_llm_response(self, response: str) -> Tuple[Dict[str, Any], str, float]:
        """Parse LLM response to extract synthon data and analysis."""
        # Try to extract JSON
        json_match = None
        import re
        for pattern in [r'```json\s*(.+?)\s*```', r'```\s*(.+?)\s*```', r'\{.+?\}']:
            json_match = re.search(pattern, response, re.DOTALL)
            if json_match:
                break
        
        if json_match:
            try:
                data = json.loads(json_match.group(1) if json_match.lastindex else json_match.group(0))
                synthon_data = data.get("synthon", {})
                reasoning = data.get("reasoning", "Parsed from response")
                confidence = data.get("confidence", 0.7)
                return synthon_data, reasoning, confidence
            except json.JSONDecodeError:
                pass
        
        # Fallback: parse primitives from text
        primitives = {}
        for key in ["dimensionality", "topology", "recognition_mode", "polarity", 
                    "fidelity", "kinetic_character", "granularity", "interaction_grammar"]:
            match = re.search(rf'{key}["\s:]+([DTPRFKG][_\w]+)', response, re.IGNORECASE)
            if match:
                primitives[key] = match.group(1)
        
        return primitives, "Parsed from response", 0.5
    
    def _create_synthon_from_data(
        self,
        data: Dict[str, str],
        description: str,
        explicit_name: Optional[str] = None,
    ) -> Synthon:
        """Create Synthon from parsed data."""
        if explicit_name:
            clean_name = explicit_name.strip()
        else:
            raw_name = data.get("name") or f"synthon_{_desc_slug(description)}"
            # Sanitize: LLMs sometimes bleed extra text into the name field
            clean_name = raw_name.split("\n")[0].strip().replace(" ", "_")
            if not clean_name:
                clean_name = f"synthon_{_desc_slug(description)}"
        return Synthon(
            name=clean_name,
            dimensionality=Dimensionality.from_symbol(data.get("dimensionality", "D_wedge")),
            topology=Topology.from_symbol(data.get("topology", "T_linear")),
            recognition_mode=RecognitionMode.from_symbol(data.get("recognition_mode", "R_superset")),
            polarity=Polarity.from_symbol(data.get("polarity", "P_pm_pseudo")),
            fidelity=Fidelity.from_symbol(data.get("fidelity", "F_eth")),
            kinetic_character=KineticCharacter.from_symbol(data.get("kinetic_character", "K_mod")),
            granularity=Granularity.from_symbol(data.get("granularity", "G_beth")),
            grammar=InteractionGrammar.from_symbol(data.get("interaction_grammar", "Gamma_and(SELECTIVE)")),
            criticality_phase=CriticalityPhase.from_symbol(data.get("criticality_phase") or "Phi_sub"),
            protection=Protection.from_symbol(data.get("protection") or "Omega_0"),
            stoichiometry=Stoichiometry.from_symbol(data.get("stoichiometry") or "n:m"),
            chirality=Chirality.from_symbol(data.get("chirality") or "H0"),
            description=description,
            metadata={"auto_generated": True, "method": "axiom_guided_llm"}
        )
    
    async def generate_validated_synthon(
        self,
        description: str,
        name: Optional[str] = None,
        delta_g: Optional[float] = None,
        max_iterations: int = 3,
        auto_register: bool = True,
    ) -> AxiomGuidedResult:
        """
        Generate synthon with axiom validation.
        
        Args:
            description: Natural language description
            name: Optional synthon name
            delta_g: Optional free energy for thermodynamic analysis
            max_iterations: Max generate-validate cycles
            auto_register: Whether to register to catalog
        
        Returns:
            AxiomGuidedResult with validated synthon
        """
        for iteration in range(1, max_iterations + 1):
            try:
                # Generate candidate with LLM
                prompt = self._build_generation_prompt(description, name)
                raw_response = await self.call_llm(
                    prompt=prompt,
                    max_tokens=self.config.get("max_tokens", 4000),
                    temperature=0.3,
                    system=self._get_system_prompt()
                )
                
                # Parse response
                synthon_data, reasoning, confidence = self._parse_llm_response(raw_response)

                # Honor explicit criticality phase in description.
                # If the description explicitly names Phi_c, override the LLM's
                # conservative default of Phi_sub so the axiom validator can test it.
                import re as _re
                _phi_match = _re.search(r'\bPhi_(c|sub|super)\b', description)
                if _phi_match and _phi_match.group(0) == "Phi_c":
                    synthon_data["criticality_phase"] = "Phi_c"

                # Create synthon
                synthon = self._create_synthon_from_data(synthon_data, description, explicit_name=name)
                
            except Exception as e:
                # Fall back to rule-based
                result = self._generate_rule_based_validated(description, name)
                result.iterations = iteration
                result.reasoning = f"LLM failed ({e}), using rule-based: {result.reasoning}"
                if auto_register:
                    global_catalog.register(synthon)
                return result
            
            # Validate against axioms
            axiom_report = AxiomValidator.validate_all_axioms(synthon)
            
            # Compute thermodynamic metrics
            if delta_g is None:
                delta_g = -50.0  # Default estimate
            try:
                thermo_result = compute_eta_CP(synthon, delta_g=delta_g)
                thermo_metrics = {
                    "eta_CP": thermo_result.eta_CP,
                    "xi_CP": thermo_result.xi_CP,
                    "delta_g": delta_g,
                }
            except Exception:
                thermo_metrics = None
            
            # Check if all axioms satisfied
            if axiom_report["all_satisfied"]:
                # --- Axiom 6: D_∞ closed cycle check (trajectory module) ---
                grounding_warnings = []
                failed_primitives = []

                if synthon.dimensionality == Dimensionality.TEMPORAL:
                    # Prefer trajectory module validation; fall back to keyword check
                    trajectory_ok = False
                    try:
                        from imscrbgrmr.trajectory import TemporalSynthonAgent as TrajectoryValidator
                        tv = TrajectoryValidator()
                        tv.add_step(synthon, step_name="step_0", delta_g=-50.0, notes=reasoning)
                        reset_ok, reset_step = tv.verify_reset()
                        trajectory_ok = reset_ok
                    except Exception:
                        # Keyword fallback
                        reasoning_lower = reasoning.lower()
                        reset_kws = ["reset", "reform", "regenerat", "hydroly", "return",
                                     "cycle", "turnover", "re-form", "dissipat", "release"]
                        process_kws = ["catalyz", "oxidat", "reduct", "transfer",
                                       "phosphoryl", "condensat", "oscillat", "periodic", "aldol"]
                        trajectory_ok = (
                            any(kw in reasoning_lower for kw in reset_kws) and
                            any(kw in reasoning_lower for kw in process_kws)
                        )
                    if not trajectory_ok:
                        failed_primitives.append("dimensionality")
                        grounding_warnings.append(
                            "Axiom 6 violation: D_∞ assigned but no reset mechanism found "
                            "by trajectory validator. Specify: (1) initial state, "
                            "(2) transformation, (3) work performed, (4) reset mechanism. "
                            "If no cycle exists, assign D_∧ or D_△ instead."
                        )

                # --- Axiom 7: T_⋈ closing bond check ---
                if synthon.topology == Topology.CYCLIC_BOWTIE:
                    reasoning_lower = reasoning.lower()
                    closing_indicators = ["hydrogen bond", "h-bond", "hbond", "coordinat", "covalent",
                                           "close", "ring", "loop", "cycl", "r2_2", "r22", "macrocycle",
                                           "crown", "cryptand", "rotaxane", "caten", "dimer"]
                    invalid_indicators = ["linear", " rod", "chain", "axial", "two-ended",
                                           "terminus", "cumulene", "allene"]
                    has_invalid = any(kw in reasoning_lower for kw in invalid_indicators)
                    has_closing = any(kw in reasoning_lower for kw in closing_indicators)
                    if has_invalid or not has_closing:
                        failed_primitives.append("topology")
                        grounding_warnings.append(
                            "Axiom 7 violation: T_⋈ assigned but no closing bond/interaction "
                            "named in reasoning, or reasoning describes a linear/chain topology. "
                            "Name the specific bond that closes the ring, or assign T_≫ (chain) "
                            "or T_□ (hub) instead."
                        )

                # If grounding failures found, feed back into refinement loop
                if grounding_warnings and iteration < max_iterations:
                    description += (
                        f"\n\nGROUNDING VIOLATIONS (must fix before registration): "
                        f"{'; '.join(grounding_warnings)}"
                    )
                    continue  # Force another refinement iteration

                # Tag synthon metadata with grounding status
                grounding_status = "partial" if failed_primitives else "full"
                synthon.metadata["grounding_status"] = grounding_status
                synthon.metadata["failed_primitives"] = failed_primitives
                if failed_primitives:
                    synthon.metadata["flagged_for_review"] = True

                if auto_register:
                    global_catalog.register(synthon)

                return AxiomGuidedResult(
                    synthon=synthon,
                    axiom_report=axiom_report,
                    confidence=confidence if not failed_primitives else confidence * 0.7,
                    reasoning=reasoning,
                    iterations=iteration,
                    alternatives=[],
                    thermodynamic_metrics=thermo_metrics,
                    warnings=grounding_warnings,
                )
            
            # Axiom violated - prepare refinement prompt
            violations = []
            for axiom_name, result in axiom_report["detailed_results"].items():
                if result.get("violated", False):
                    violations.append(f"{axiom_name}: {result.get('falsification_note', 'Violation')}")
            
            if iteration < max_iterations:
                # Refine with axiom violation feedback
                description += f"\n\nPRIOR ATTEMPT VIOLATIONS: {'; '.join(violations)}. Revise primitive assignments to satisfy all axioms."
            else:
                # Max iterations reached - return with warnings
                if auto_register:
                    global_catalog.register(synthon)
                
                return AxiomGuidedResult(
                    synthon=synthon,
                    axiom_report=axiom_report,
                    confidence=confidence * 0.7,  # Penalize for violations
                    reasoning=reasoning + f"\n\nWARNING: {len(violations)} axiom violations after {max_iterations} iterations: {'; '.join(violations)}",
                    iterations=iteration,
                    alternatives=[],
                    thermodynamic_metrics=thermo_metrics,
                    warnings=violations,
                )
        
        # Should not reach here, but just in case
        return self._generate_rule_based_validated(description, name)
    
    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main entry point for AjintK framework."""
        try:
            result = await self.generate_validated_synthon(task)
            
            status = "success" if result.axiom_report["all_satisfied"] else "partial"
            
            return {
                "status": status,
                "findings": (
                    f"Generated axiom-validated synthon: {result.synthon.name}\n"
                    f"Notation: {result.synthon.to_notation()}\n"
                    f"Confidence: {result.confidence:.2f}\n"
                    f"Iterations: {result.iterations}\n"
                    f"Axioms Satisfied: {result.axiom_report['all_satisfied']}\n"
                    f"Reasoning: {result.reasoning}"
                ),
                "artifacts": self.artifacts,
                "metadata": {
                    "synthon_name": result.synthon.name,
                    "notation": result.synthon.to_notation(),
                    "confidence": result.confidence,
                    "axiom_violations": result.axiom_report["violations"],
                    "all_axioms_satisfied": result.axiom_report["all_satisfied"],
                    "thermodynamic_metrics": result.thermodynamic_metrics,
                    "warnings": result.warnings,
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        return """<role>
You are an expert computational chemist specializing in the Unified Synthonicon framework.
Your expertise includes the ten formal primitives (D, T, R, P, F, K, G, Γ, Φ, S),
the eight composition axioms from QUANTIG.md, thermodynamic analysis (η_CP, ξ_CP),
and cross-domain analogy detection.
You **MUST** generate synthons that satisfy **ALL** applicable axioms.
You **MUST NOT** assign primitives by keyword matching — ground every assignment in physical mechanism.
</role>

<mechanistic_constraints>
The following grounding rules **OVERRIDE** descriptive pattern matching.
Violation of **ANY** rule is an axiom failure requiring revision.

<axiom_6>
D_∞ (TEMPORAL) **REQUIRES** A COMPLETE CLOSED CYCLE.
D_∞ is **ONLY** valid if you can state **ALL FOUR**:
  (1) The initial state of the system
  (2) The transformation performed
  (3) The work done or product formed
  (4) The specific mechanism that resets the system to the initial state
You **MUST NOT** assign D_∞ for: static molecules, rigid rods, spatial periodicity, "extended" chains,
"1D" geometry, "dynamic" character without a cycle, quantum delocalization without reset, or
supramolecular polymerization / open-ended columnar stacking (these are D_△, not D_∞).
Assign D_∧ (molecular) or D_△ (supramolecular) if the four-step cycle cannot be stated.
Compound systems with both D_△ spatial assembly and a molecular cycle must ground D_∞ via the
molecular cycle's reset — not via the assembly. Stacking into columns ≠ closed temporal cycle.
</axiom_6>

<axiom_7>
T_⋈ (CYCLIC) **REQUIRES** A NAMED CLOSING BOND OR INTERACTION.
T_⋈ is **ONLY** valid if you can name the specific bond or interaction that closes the ring.
Valid examples: "two O-H···O hydrogen bonds complete the R²₂(8) motif",
"macrocyclic ether oxygens coordinate cation in closed ring", "interlocked mechanical bond".
You **MUST NOT** assign T_⋈ for: linear chains, rigid rods, cumulenes, allenes, "two-ended" systems,
"axial" connectivity, or any system where no closing bond can be named.
Assign T_≫ for chains and T_□ for hub/node topologies.
</axiom_7>

<axiom_8>
R **MUST** match the actual interaction physics:
R_⊇ (non-covalent): H-bonds, halogen bonds, π-stacking, electrostatics — **NO** bond making/breaking
R_⊆ (covalent): σ/π bond formation, electron sharing
R_‡ (catalytic): transition-state stabilization, barrier reduction, reversible bond formation with error correction
R_⇔ (mechanical): steric entanglement, rotaxanes, catenanes — topological constraint
You **MUST NOT** assign R_‡ merely because a system is "dynamic", "geometric", or "specific".
</axiom_8>
</mechanistic_constraints>

<requirements>
When axiom violations are detected in a prior iteration, you **MUST** revise the offending
primitive assignments before returning. You **MUST NOT** return the same tuple that was flagged.
Your analyses **MUST** be rigorous, well-reasoned, and grounded in chemical principles.
</requirements>"""

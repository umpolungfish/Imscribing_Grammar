"""
LLM-Grounded Justification Extractor (Path B Hybrid)

This module uses LLM reasoning to extract mechanistic justifications from
natural language descriptions, then validates them against the grounding
vocabulary.

Unlike pure keyword matching, this approach:
1. Extracts mechanistic claims from descriptions
2. Maps claims to physical phenomena
3. Generates structured justifications
4. Validates against grounding vocabulary

Usage:
    from imscrbgrmr.llm_grounding import extract_grounding_from_description
    
    result = extract_grounding_from_description(
        "carboxylic acid dimer with cyclic hydrogen bonding R₂²(8) motif"
    )
    print(result.justifications)  # Structured primitive justifications
    print(result.delta_g_justification)  # ΔG source/method
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

try:
    from imscrbgrmr import (
        Synthon, Dimensionality, Topology, RecognitionMode,
        Polarity, Fidelity, Granularity, InteractionGrammar,
        KineticCharacter, CriticalityPhase,
        Criticality, Protection, Stoichiometry, Chirality,
    )
    from imscrbgrmr.grounding import GroundingValidator, GroundingResult
    from imscrbgrmr.rdkit_utils import generate_rdkit_grounding, RDKit_AVAILABLE
    LLM_GROUNDING_AVAILABLE = True
except ImportError:
    LLM_GROUNDING_AVAILABLE = False


@dataclass
class LLMGroundingResult:
    """Result of LLM-grounded justification extraction."""
    description: str
    justifications: Dict[str, str]  # primitive -> justification
    delta_g_value: Optional[float] = None
    delta_g_justification: Optional[str] = None
    smiles: Optional[str] = None
    confidence: float = 0.0  # Overall confidence in extraction
    reasoning: str = ""  # LLM explanation
    validation_result: Optional[GroundingResult] = None
    warnings: List[str] = field(default_factory=list)
    
    @property
    def is_fully_grounded(self) -> bool:
        """Check if all primitives and ΔG are grounded."""
        if self.validation_result is None:
            return False
        return (
            self.validation_result.is_valid and
            (self.validation_result.delta_g_grounding is None or
             self.validation_result.delta_g_grounding.status.name == "GROUNDED")
        )


# Prompt template for LLM justification extraction
ADVERSARIAL_GROUNDING_PROMPT = """<role>
You are a grounding validator for a chemical informatics framework.
Your job is to CHALLENGE and VERIFY primitive assignments — not confirm them.
</role>

<task>
You will be given a chemical description and a set of primitive assignments.
For each primitive, determine whether the assignment is chemically justified
FROM FIRST PRINCIPLES, ignoring what value was assigned.

You **MUST** answer specific mechanistic questions for each primitive.
You **MUST NOT** simply restate the assigned value as justification.
</task>

<input>
Chemical description: {description}
Assigned tuple: {tuple}
</input>

<requirements>
For each primitive, answer the specific question:

**D (Dimensionality):**
- If D_∞ (temporal): Can you write down the COMPLETE cycle?
  State: (1) initial state, (2) transformation performed, (3) work done, (4) reset mechanism.
  If you cannot complete ALL FOUR, D_∞ is INVALID — use D_∧ or D_△.
- If D_∧ or D_△: Is this a single molecule or supramolecular assembly? VALID.

**T (Topology):**
- If T_⋈ (cyclic): Name the SPECIFIC bond or interaction that closes the loop.
  If you cannot name it, T_⋈ is INVALID — use T_≫ or T_□.
- If T_≫ (chain): Is primary connectivity linear/branched without closure? VALID.
- If T_□ (hub): Is there a central node distributing to multiple arms? VALID.

**R (Recognition Mode):**
- Name the specific physical interaction mechanism (H-bond, coordinate bond, radical coupling, etc.)
- Does it match R_⊆ (covalent), R_⊇ (non-covalent), R_‡ (catalytic), or R_⇔ (mechanical)?

**P (Polarity):**
- Is the site electron-rich (donor) or electron-poor (acceptor)?
- Or does it have BOTH on the same face (self-complementary)?
- Distinguish symmetric (P_±^sym) from pseudosymmetric (P_±^ψ).

**F (Fidelity):**
- What is the approximate ΔG or ξ_CP for this interaction?
- F_ℏ: ΔG < −40 kJ/mol (strong), F_ℇ: −20 to −40 (moderate), F_ℓ: > −20 (weak)

**G (Granularity):**
- Does this interaction control ONE pair (local), a MOTIF (mesoscale), or an ENTIRE network (global)?

**Γ (Interaction Grammar):**
- Does the synthon require ONE specific partner (AND/SPECIFIC), accept SEVERAL (AND/SELECTIVE),
  or work with MANY (AND/BROAD)?
- Is there ORDERED recognition requiring a prior binding event (SEQUENTIAL)?

**K (Kinetic Character):**
- Estimate the activation barrier ΔG‡:
  K_frtailgamma: < 60 kJ/mol, K_turnm: 60–100, K_schwa: > 100, K_teshlig: high pathway multiplicity
</requirements>

<output_format>
Return ONLY a JSON object with this exact structure:

{{
  "primitive_results": {{
    "dimensionality": {{
      "assigned_value": "D_∞",
      "is_valid": true,
      "specific_justification": "One sentence naming the physical phenomenon",
      "confidence": 0.9,
      "failure_reason": null,
      "suggested_correct_value": null
    }},
    "topology": {{ ... }},
    "recognition_mode": {{ ... }},
    "polarity": {{ ... }},
    "fidelity": {{ ... }},
    "granularity": {{ ... }},
    "interaction_grammar": {{ ... }},
    "kinetic_character": {{ ... }}
  }},
  "overall_status": "full",
  "overall_confidence": 0.85,
  "critical_issues": ["list of any hard violations found"]
}}

You **MUST** return **ONLY** the JSON object.
You **MUST NOT** include **ANY** markdown formatting or code blocks.
</output_format>
"""

EXTRACTION_PROMPT = """<role>
You are a chemical reasoning assistant extracting mechanistic justifications for synthon primitive assignments.
You **MUST** ground every assignment in specific physical phenomena, **NOT** in description keywords.
</role>

<task>
Analyze the chemical description and extract a mechanistic justification for **EACH** primitive.

You **MUST**:
1. Reference **SPECIFIC** physical phenomena for each primitive (not the primitive label itself)
2. Identify the ΔG source: experimental, computational, literature, or estimated
3. Use the SMILES if provided to inform ΔG estimation
4. Return **ONLY** valid JSON — **NO** markdown, **NO** code blocks
</task>

<input>
**Chemical Description:** {description}
**SMILES (if provided):** {smiles}
</input>

<requirements>
**Per-Primitive Justification Requirements:**

- **dimensionality**: Reference the coordinate space — molecular geometry, crystal packing, or catalytic cycle
- **topology**: Reference the connectivity pattern — cyclic ring closure, chain propagation, or hub/node
- **recognition_mode**: Reference the interaction mechanism — H-bonding, covalent bond formation, catalytic TS stabilization
- **polarity**: Reference directional character — donor site, acceptor site, or self-complementary face
- **fidelity**: Reference a reliability measure — ΔG value, ξ_CP estimate, or error rate
- **kinetic**: Reference a barrier height or timescale — ΔG‡ in kJ/mol or qualitative fast/slow
- **granularity**: Reference the scale of control — single pair, motif cluster, or extended network
- **interaction_grammar**: Reference partner selection logic — specific binding, selective tolerance, or promiscuous

**ΔG Justification Categories — You MUST specify ONE:**
- `EXPERIMENTAL`: ITC, calorimetry, K_d, binding constant
- `COMPUTATIONAL`: DFT, ab initio, BSSE, solvation model
- `LITERATURE`: literature value, benchmark, CSD propensity
- `ESTIMATED`: group additivity, analogous system
</requirements>

<output_format>
You **MUST** return **ONLY** the following JSON object.
You **MUST NOT** include **ANY** markdown formatting, code blocks, or backticks.
The output **MUST** start directly with `{{` and end with `}}`.

{{
    "justifications": {{
        "dimensionality": "...",
        "topology": "...",
        "recognition_mode": "...",
        "polarity": "...",
        "fidelity": "...",
        "kinetic": "...",
        "granularity": "...",
        "interaction_grammar": "..."
    }},
    "delta_g_value": -52.0,
    "delta_g_justification": "...",
    "smiles": "CC(=O)O",
    "confidence": 0.8,
    "reasoning": "Explanation of primitive assignments..."
}}
</output_format>

<example>
Input: "carboxylic acid dimer with cyclic hydrogen bonding R₂²(8) motif"

Output:
{{
    "justifications": {{
        "dimensionality": "Single-molecule geometry; both carboxylate groups reside on discrete molecules — no crystal-packing or temporal cycle",
        "topology": "Cyclic closure by two O-H···O hydrogen bonds completing the R₂²(8) ring — no linear propagation",
        "recognition_mode": "Non-covalent: two O-H···O hydrogen bonds, no bond making or breaking",
        "polarity": "Pseudosymmetric self-complementary: each face presents one H-bond donor (O-H) and one acceptor (C=O)",
        "fidelity": "High thermodynamic stability — ΔG ≈ −52 kJ/mol (solvated), ξ_CP ≈ 8.5 nats",
        "kinetic": "Barrier < 60 kJ/mol; H-bond formation is diffusion-limited at room temperature",
        "granularity": "Local — single pairwise binding event, no network propagation",
        "interaction_grammar": "One specific partner: the complementary carboxylate face"
    }},
    "delta_g_value": -52.0,
    "delta_g_justification": "LITERATURE: B3LYP-D3/6-311+G(d,p) + BSSE from QUANTIG.md Transformation #1",
    "smiles": "CC(=O)O",
    "confidence": 0.90,
    "reasoning": "Carboxylic acid dimer is a well-characterized R₂²(8) motif. Both molecules are single-molecule (D_∧), connected by a cyclic ring (T_⋈) via non-covalent H-bonds (R_⊇), with pseudosymmetric self-complementary polarity (P_±^ψ)."
}}
</example>
"""


def extract_grounding_from_description(
    description: str,
    smiles: Optional[str] = None,
    use_llm: bool = True,
    llm_provider: Optional[Any] = None,
) -> LLMGroundingResult:
    """
    Extract mechanistic justifications from chemical description.
    
    Args:
        description: Natural language chemical description
        smiles: Optional SMILES string for ΔG estimation
        use_llm: Whether to use LLM for extraction (fallback to rules if False)
        llm_provider: Optional LLM provider for extraction
    
    Returns:
        LLMGroundingResult with extracted justifications
    """
    if not LLM_GROUNDING_AVAILABLE:
        return LLMGroundingResult(
            description=description,
            justifications={},
            confidence=0.0,
            reasoning="Imscribing Grammar modules not available",
            warnings=["Imscribing Grammar not available"],
        )
    
    # Try LLM extraction if requested and available
    if use_llm and llm_provider is not None:
        try:
            return _extract_with_llm(description, smiles, llm_provider)
        except Exception as e:
            # Fallback to rule-based extraction
            pass
    
    # Rule-based extraction fallback
    return _extract_with_rules(description, smiles)


def _extract_with_llm(
    description: str,
    smiles: Optional[str],
    llm_provider: Any,
) -> LLMGroundingResult:
    """Extract justifications using LLM reasoning."""
    import json
    
    # Format prompt
    prompt = EXTRACTION_PROMPT.format(
        description=description,
        smiles=smiles or "Not provided"
    )
    
    # Query LLM
    response = llm_provider.query(prompt)
    
    # Extract JSON from response
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON found in LLM response")
    
    data = json.loads(json_match.group())
    
    # Build result
    result = LLMGroundingResult(
        description=description,
        justifications=data.get("justifications", {}),
        delta_g_value=data.get("delta_g_value"),
        delta_g_justification=data.get("delta_g_justification"),
        smiles=data.get("smiles", smiles),
        confidence=data.get("confidence", 0.5),
        reasoning=data.get("reasoning", ""),
    )
    
    # Validate with GroundingValidator
    if result.justifications:
        validator = GroundingValidator()
        result.validation_result = validator.validate(
            _create_placeholder_synthon(),
            result.justifications,
            result.delta_g_value,
            result.delta_g_justification,
        )
    
    return result


def _extract_with_rules(
    description: str,
    smiles: Optional[str] = None,
) -> LLMGroundingResult:
    """
    Extract justifications using rule-based pattern matching.
    
    This is a fallback when LLM is not available.
    """
    justifications = {}
    description_lower = description.lower()
    
    # Dimensionality detection
    if any(w in description_lower for w in ["cycle", "catalytic", "temporal", "oscillat", "time crystal"]):
        justifications["dimensionality"] = "Closed catalytic cycle with temporal periodicity"
    elif any(w in description_lower for w in ["crystal", "packing", "assembly", "network", "framework"]):
        justifications["dimensionality"] = "Supramolecular crystal packing and intermolecular recognition"
    else:
        justifications["dimensionality"] = "Single-molecule geometry with intramolecular constraint"
    
    # Topology detection
    if any(w in description_lower for w in ["cyclic", "dimer", "ring", "R₂", "bowtie", "base pair"]):
        justifications["topology"] = "Cyclic motif with ring closure"
    elif any(w in description_lower for w in ["chain", "polymer", "linear", "oligomer"]):
        justifications["topology"] = "Chain structure with linear propagation"
    elif any(w in description_lower for w in ["node", "hub", "MOF", "coordination", "chelate"]):
        justifications["topology"] = "Hub/node coordination geometry"
    else:
        justifications["topology"] = "Cyclic bowtie topology"
    
    # Recognition mode detection
    if any(w in description_lower for w in ["covalent", "bond formation"]):
        justifications["recognition_mode"] = "Covalent bond formation"
    elif any(w in description_lower for w in ["catalytic", "catalysis", "organocatal"]):
        justifications["recognition_mode"] = "Catalytic process with transition state stabilization"
    elif any(w in description_lower for w in ["mechanical", "rotaxane", "catenane", "interlock"]):
        justifications["recognition_mode"] = "Mechanical bond with steric clipping"
    else:
        justifications["recognition_mode"] = "Non-covalent interaction (hydrogen bonding, electrostatic)"
    
    # Polarity detection
    if any(w in description_lower for w in ["self-complement", "homodimer", "symmetric"]):
        justifications["polarity"] = "Self-complementary symmetric interface"
    elif any(w in description_lower for w in ["donor", "acceptor", "D-A", "directional"]):
        justifications["polarity"] = "Directional donor-acceptor pair"
    else:
        justifications["polarity"] = "Pseudosymmetric self-complementary interface"
    
    # Fidelity detection
    if any(w in description_lower for w in ["strong", "high fidelity", "stable", "robust", "triple H-bond", "chelate"]):
        justifications["fidelity"] = "High thermodynamic stability with cooperative fidelity amplification"
    elif any(w in description_lower for w in ["weak", "low fidelity", "promiscuous", "shallow"]):
        justifications["fidelity"] = "Low fidelity with promiscuous binding and shallow energy landscape"
    else:
        justifications["fidelity"] = "Medium fidelity with moderate selectivity and reversible binding"
    
    # Kinetic detection
    if any(w in description_lower for w in ["fast", "rapid", "spontaneous", "diffusion-limited"]):
        justifications["kinetic"] = "Barrier < 60 kJ/mol, spontaneous on experimental timescales"
    elif any(w in description_lower for w in ["slow", "high barrier", "activated", "requires heat"]):
        justifications["kinetic"] = "Barrier > 100 kJ/mol, requires significant activation"
    elif any(w in description_lower for w in ["trap", "kinetic product", "metastable", "diverges"]):
        justifications["kinetic"] = "Pathway multiplicity high, kinetic products diverge from thermodynamic"
    else:
        justifications["kinetic"] = "Barrier 60-100 kJ/mol, accessible with mild activation"
    
    # Granularity detection
    if any(w in description_lower for w in ["network", "global", "framework", "percolat", "MOF"]):
        justifications["granularity"] = "Global network-scale assembly with long-range order"
    elif any(w in description_lower for w in ["mesoscale", "cooperative", "array", "cluster", "superlinear"]):
        justifications["granularity"] = "Mesoscale cooperative array with superlinear induction"
    else:
        justifications["granularity"] = "Local pairwise interaction with single binding event"
    
    # Interaction grammar detection
    if any(w in description_lower for w in ["specific", "lock-and-key", "one partner", "binary complex"]):
        justifications["interaction_grammar"] = "One specific partner with lock-and-key recognition"
    elif any(w in description_lower for w in ["broad", "promiscuous", "many partners", "shallow landscape"]):
        justifications["interaction_grammar"] = "Many partners with broad tolerance and shallow energy landscape"
    elif any(w in description_lower for w in ["sequential", "ordered", "template-directed", "allosteric"]):
        justifications["interaction_grammar"] = "Ordered sequential recognition from small partner set"
    else:
        justifications["interaction_grammar"] = "Few partners with moderate selectivity and degenerate recognition site"
    
    # ΔG estimation from SMILES or rules
    delta_g_value = None
    delta_g_justification = None
    
    if smiles and RDKit_AVAILABLE:
        rdkit_grounding = generate_rdkit_grounding(smiles, description)
        delta_g_value = rdkit_grounding["delta_g_value"]
        delta_g_justification = rdkit_grounding["delta_g_justification"]
    else:
        # Rule-based ΔG estimation
        if "carboxylic" in description_lower and "dimer" in description_lower:
            delta_g_value = -52.0
            delta_g_justification = "Literature value for carboxylic acid R₂²(8) dimer from QUANTIG.md Transformation #1"
        elif "triple" in description_lower and "H-bond" in description_lower:
            delta_g_value = -95.0
            delta_g_justification = "Literature value for DAD·ADA triple H-bond array from QUANTIG.md Transformation #5"
        elif "base pair" in description_lower:
            if "A" in description_lower and "T" in description_lower:
                delta_g_value = -50.0
                delta_g_justification = "Literature value for A·T Watson-Crick base pair"
            elif "G" in description_lower and "C" in description_lower:
                delta_g_value = -80.0
                delta_g_justification = "Literature value for G·C Watson-Crick base pair"
        else:
            delta_g_value = -30.0
            delta_g_justification = "Estimated from analogous non-covalent systems"
    
    # Build result
    result = LLMGroundingResult(
        description=description,
        justifications=justifications,
        delta_g_value=delta_g_value,
        delta_g_justification=delta_g_justification,
        smiles=smiles,
        confidence=0.6 if smiles else 0.5,
        reasoning=f"Rule-based extraction from description keywords",
    )
    
    # Validate
    validator = GroundingValidator()
    result.validation_result = validator.validate(
        _create_placeholder_synthon(),
        justifications,
        delta_g_value,
        delta_g_justification,
    )
    
    return result


def _create_placeholder_synthon() -> Synthon:
    """Create a placeholder synthon for validation."""
    return Synthon(
        name="placeholder",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=Criticality.Phi_softsign,
        protection=Protection.Omega_closeepsilon,
        stoichiometry=Stoichiometry.S_doublebaresh,
        chirality=Chirality.H_closeomega,
    )


def extract_and_validate(
    description: str,
    smiles: Optional[str] = None,
    require_full_grounding: bool = True,
) -> Tuple[bool, LLMGroundingResult]:
    """
    Extract justifications and validate them.
    
    Args:
        description: Chemical description
        smiles: Optional SMILES for ΔG estimation
        require_full_grounding: If True, require all primitives + ΔG grounded
    
    Returns:
        Tuple of (is_valid, result)
    """
    result = extract_grounding_from_description(description, smiles)
    
    if require_full_grounding:
        is_valid = result.is_fully_grounded
    else:
        is_valid = result.validation_result is not None and result.validation_result.is_valid
    
    return is_valid, result

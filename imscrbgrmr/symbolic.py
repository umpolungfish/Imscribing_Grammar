"""
Symbolic Reasoning Engine — Formal algebra and theorem proving for the Synthonicon grammar.

This module implements:
1. Primitive algebra (Γ Boolean operators, G-D tensor operations)
2. Automated theorem prover for axiom validation
3. Cross-domain analogy detection with formal similarity metrics
4. Predictive rule generation and testing
5. Counter-example search (falsification attempts)

From QUANTIG.md Section II:
"A classification system need only assign labels; a predictive grammar must compose
primitives and derive non-obvious consequences about assembled system behavior."
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
import itertools

from imscrbgrmr.models import (
    Synthon,
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    Granularity,
    InteractionGrammar,
    GrammarOperator,
    KineticCharacter,
    CriticalityPhase,
)
from imscrbgrmr.constraints import AxiomValidator
from imscrbgrmr.thermodynamics import compute_eta_CP, compute_xi_CP


# =============================================================================
# Symbolic Expressions and Algebra
# =============================================================================

class SymbolicOperator(Enum):
    """Operators for symbolic expressions."""
    # Boolean operators
    AND = "∧"
    OR = "∨"
    NOT = "¬"
    IMPLIES = "→"
    IFF = "↔"
    
    # Quantifiers
    FOR_ALL = "∀"
    EXISTS = "∃"
    
    # Arithmetic
    EQ = "="
    NEQ = "≠"
    LT = "<"
    GT = ">"
    LEQ = "≤"
    GEQ = "≥"
    
    # Synthon-specific
    COMPATIBLE = "⊕"  # Compatibility relation
    AMPLIFIES = "↑"   # Amplification relation
    DEGENERATES = "≡"  # Degeneracy relation


@dataclass
class SymbolicExpression:
    """
    Represents a symbolic expression in the Synthonicon algebra.
    
    Examples:
        - Primitive assertion: Primitive("F", "F_hbar")
        - Boolean combination: And(Primitive("T", "T_bowtie"), Primitive("P", "P_pm"))
        - Implication: Implies(Primitive("T", "T_bowtie"), Primitive("F", "F_eth"))
    """
    operator: SymbolicOperator
    operands: List[Any]
    
    def __str__(self) -> str:
        if len(self.operands) == 1:
            return f"{self.operator.value}{self.operands[0]}"
        elif len(self.operands) == 2:
            return f"({self.operands[0]} {self.operator.value} {self.operands[1]})"
        else:
            return f"{self.operator.value}({', '.join(map(str, self.operands))})"
    
    def evaluate(self, synthon: Synthon) -> bool:
        """Evaluate the expression against a synthon."""
        return _evaluate_expression(self, synthon)
    
    @classmethod
    def primitive(cls, name: str, value: str) -> SymbolicExpression:
        """Create a primitive assertion expression."""
        return cls(SymbolicOperator.EQ, [f"{name}", value])
    
    @classmethod
    def And(cls, *exprs) -> SymbolicExpression:
        """Create AND expression."""
        return cls(SymbolicOperator.AND, list(exprs))
    
    @classmethod
    def Or(cls, *exprs) -> SymbolicExpression:
        """Create OR expression."""
        return cls(SymbolicOperator.OR, list(exprs))
    
    @classmethod
    def Not(cls, expr) -> SymbolicExpression:
        """Create NOT expression."""
        return cls(SymbolicOperator.NOT, [expr])
    
    @classmethod
    def Implies(cls, antecedent, consequent) -> SymbolicExpression:
        """Create implication expression."""
        return cls(SymbolicOperator.IMPLIES, [antecedent, consequent])


def _evaluate_expression(expr: SymbolicExpression, synthon: Synthon) -> bool:
    """Internal expression evaluation."""
    op = expr.operator
    
    if op == SymbolicOperator.EQ:
        # Primitive assertion: F = F_hbar
        primitive_name = expr.operands[0]
        expected_value = expr.operands[1]
        actual_value = _get_primitive_value(synthon, primitive_name)
        return actual_value == expected_value
    
    elif op == SymbolicOperator.AND:
        return all(_evaluate_expression(o, synthon) for o in expr.operands)
    
    elif op == SymbolicOperator.OR:
        return any(_evaluate_expression(o, synthon) for o in expr.operands)
    
    elif op == SymbolicOperator.NOT:
        return not _evaluate_expression(expr.operands[0], synthon)
    
    elif op == SymbolicOperator.IMPLIES:
        antecedent = _evaluate_expression(expr.operands[0], synthon)
        consequent = _evaluate_expression(expr.operands[1], synthon)
        return (not antecedent) or consequent  # Material implication
    
    return False


def _get_primitive_value(synthon: Synthon, name: str) -> str:
    """Get primitive value from synthon by name."""
    mapping = {
        "D": synthon.dimensionality.value,
        "T": synthon.topology.value,
        "R": synthon.recognition_mode.value,
        "P": synthon.polarity.value,
        "F": synthon.fidelity.value,
        "K": synthon.kinetic_character.value,
        "G": synthon.granularity.value,
        "Γ": f"{synthon.interaction_grammar.operator.value}({synthon.interaction_grammar.tier})",
        "Φ": synthon.criticality_phase.value if synthon.criticality_phase else "Phi_sub",
    }
    return mapping.get(name, "")


# =============================================================================
# Grammar Operator Algebra (Γ Algebra)
# =============================================================================

@dataclass
class GrammarAlgebra:
    """
    Implements the Boolean algebra of interaction grammars.
    
    From QUANTIG.md Section II:
    - Γ_∧ (AND): all partners required simultaneously
    - Γ_∨ (OR): any one partner suffices
    - Γ_→ (SEQUENTIAL): partner A required before B
    """
    
    @staticmethod
    def apply_operator(
        grammar: InteractionGrammar,
        operator: GrammarOperator,
    ) -> InteractionGrammar:
        """
        Apply a Boolean operator to an interaction grammar.
        
        Args:
            grammar: Original interaction grammar
            operator: Boolean operator to apply
        
        Returns:
            New interaction grammar with operator applied
        """
        # Find matching grammar with new operator
        for ig in InteractionGrammar:
            if ig.operator == operator and ig.tier == grammar.tier:
                return ig
        
        # Default fallback
        if operator == GrammarOperator.AND:
            return InteractionGrammar.SELECTIVE_AND
        elif operator == GrammarOperator.OR:
            return InteractionGrammar.SELECTIVE_OR
        else:
            return InteractionGrammar.SELECTIVE_SEQ
    
    @staticmethod
    def compose_grammars(
        grammar1: InteractionGrammar,
        grammar2: InteractionGrammar,
    ) -> InteractionGrammar:
        """
        Compose two interaction grammars.
        
        Composition rules:
        - AND + AND = AND (both partners required)
        - OR + OR = OR (either partner from either set)
        - SEQ + SEQ = SEQ (longer sequence)
        - AND + OR = SELECTIVE (refined selection)
        - etc.
        """
        op1 = grammar1.operator
        op2 = grammar2.operator
        
        # Composition table
        composition_table = {
            (GrammarOperator.AND, GrammarOperator.AND): GrammarOperator.AND,
            (GrammarOperator.OR, GrammarOperator.OR): GrammarOperator.OR,
            (GrammarOperator.SEQUENTIAL, GrammarOperator.SEQUENTIAL): GrammarOperator.SEQUENTIAL,
            (GrammarOperator.AND, GrammarOperator.OR): GrammarOperator.SELECTIVE,
            (GrammarOperator.OR, GrammarOperator.AND): GrammarOperator.SELECTIVE,
            (GrammarOperator.SEQUENTIAL, GrammarOperator.AND): GrammarOperator.SEQUENTIAL,
            (GrammarOperator.AND, GrammarOperator.SEQUENTIAL): GrammarOperator.SEQUENTIAL,
        }
        
        result_op = composition_table.get((op1, op2), GrammarOperator.SEQUENTIAL)
        
        # Use more specific tier
        tier1_val = {"SPECIFIC": 0, "SELECTIVE": 1, "BROAD": 2}.get(grammar1.tier, 1)
        tier2_val = {"SPECIFIC": 0, "SELECTIVE": 1, "BROAD": 2}.get(grammar2.tier, 1)
        result_tier = grammar1.tier if tier1_val <= tier2_val else grammar2.tier
        
        # Find matching grammar
        for ig in InteractionGrammar:
            if ig.operator == result_op and ig.tier == result_tier:
                return ig
        
        return InteractionGrammar.SELECTIVE_AND
    
    @staticmethod
    def check_grammar_implication(
        grammar1: InteractionGrammar,
        grammar2: InteractionGrammar,
    ) -> bool:
        """
        Check if grammar1 implies grammar2.
        
        Implication holds if grammar1 is more restrictive than grammar2.
        """
        # Tier implication (more specific → less specific)
        tier_order = {"SPECIFIC": 0, "SELECTIVE": 1, "BROAD": 2}
        tier_implies = tier_order.get(grammar1.tier, 1) <= tier_order.get(grammar2.tier, 1)
        
        # Operator implication
        operator_implies = grammar1.operator == grammar2.operator or \
                          (grammar1.operator == GrammarOperator.AND and 
                           grammar2.operator == GrammarOperator.OR)
        
        return tier_implies and operator_implies


# =============================================================================
# G-D Tensor and Criticality Analysis
# =============================================================================

@dataclass
class GDTensor:
    """
    Implements the G-D tensor for criticality analysis.
    
    From QUANTIG.md Section VIII:
    At criticality, G and D degenerate (become dependent).
    """
    
    # G-D compatibility matrix
    COMPATIBILITY = {
        (Granularity.LOCAL, Dimensionality.MOLECULAR): 1.0,
        (Granularity.LOCAL, Dimensionality.SUPRAMOLECULAR): 0.7,
        (Granularity.LOCAL, Dimensionality.TEMPORAL): 0.5,
        (Granularity.MESOSCALE, Dimensionality.MOLECULAR): 0.7,
        (Granularity.MESOSCALE, Dimensionality.SUPRAMOLECULAR): 1.0,
        (Granularity.MESOSCALE, Dimensionality.TEMPORAL): 0.7,
        (Granularity.GLOBAL, Dimensionality.MOLECULAR): 0.3,
        (Granularity.GLOBAL, Dimensionality.SUPRAMOLECULAR): 1.0,
        (Granularity.GLOBAL, Dimensionality.TEMPORAL): 1.0,
    }
    
    @classmethod
    def compute_independence(cls, synthon: Synthon) -> float:
        """
        Compute G-D independence score (0-1).
        
        1.0 = fully independent (normal)
        0.0 = fully degenerate (critical)
        """
        g = synthon.granularity
        d = synthon.dimensionality
        
        # Check if at criticality
        if synthon.criticality_phase == CriticalityPhase.CRITICAL:
            return 0.0
        
        # Get compatibility for each domain
        compatibilities = []
        for domain in d.domains:
            d_enum = cls._domain_to_dimensionality(domain)
            compat = cls.COMPATIBILITY.get((g, d_enum), 0.5)
            compatibilities.append(compat)
        
        # Average compatibility (higher = more independent)
        return sum(compatibilities) / len(compatibilities)
    
    @classmethod
    def check_degeneracy(cls, synthon: Synthon) -> bool:
        """Check if G and D are degenerate (at criticality)."""
        return synthon.criticality_phase == CriticalityPhase.CRITICAL
    
    @staticmethod
    def _domain_to_dimensionality(domain: str) -> Dimensionality:
        """Convert domain string to Dimensionality enum."""
        mapping = {
            "molecular": Dimensionality.MOLECULAR,
            "supramolecular": Dimensionality.SUPRAMOLECULAR,
            "temporal": Dimensionality.TEMPORAL,
        }
        return mapping.get(domain, Dimensionality.MOLECULAR)


# =============================================================================
# Automated Theorem Prover for Axioms
# =============================================================================

@dataclass
class TheoremProof:
    """Result of theorem proving."""
    theorem_name: str
    statement: SymbolicExpression
    proven: bool
    proof_steps: List[str]
    counter_examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "theorem": self.theorem_name,
            "statement": str(self.statement),
            "proven": self.proven,
            "proof_steps": self.proof_steps,
            "counter_examples": self.counter_examples,
        }


class AxiomTheoremProver:
    """
    Automated theorem prover for composition axioms.
    
    Validates axioms through:
    1. Symbolic evaluation
    2. Model checking against synthon catalog
    3. Counter-example search
    """
    
    def __init__(self, catalog=None):
        """Initialize prover with optional synthon catalog."""
        self.catalog = catalog
        self.proven_theorems: Dict[str, TheoremProof] = {}
    
    def prove_axiom(
        self,
        axiom_name: str,
        test_synthons: Optional[List[Synthon]] = None,
    ) -> TheoremProof:
        """
        Prove an axiom against a set of synthons.
        
        Args:
            axiom_name: Name of axiom (axiom1-axiom5)
            test_synthons: Synthons to test against (uses catalog if None)
        
        Returns:
            TheoremProof with results
        """
        if test_synthons is None:
            test_synthons = list(self.catalog._synthons.values()) if self.catalog else []
        
        # Get axiom statement
        statement = self._get_axiom_statement(axiom_name)
        
        # Test against all synthons
        proof_steps = []
        counter_examples = []
        all_satisfied = True
        
        for synthon in test_synthons:
            # Check if axiom applies
            applies = self._check_axiom_applicability(axiom_name, synthon)
            
            if not applies:
                proof_steps.append(f"{synthon.name}: axiom does not apply")
                continue
            
            # Evaluate axiom
            satisfied = self._evaluate_axiom(axiom_name, synthon)
            
            if satisfied:
                proof_steps.append(f"{synthon.name}: ✓ satisfied")
            else:
                proof_steps.append(f"{synthon.name}: ✗ VIOLATED")
                all_satisfied = False
                counter_examples.append({
                    "synthon": synthon.name,
                    "notation": synthon.to_notation(),
                    "violation": f"{axiom_name} failed",
                })
        
        return TheoremProof(
            theorem_name=axiom_name,
            statement=statement,
            proven=all_satisfied,
            proof_steps=proof_steps,
            counter_examples=counter_examples,
        )
    
    def _get_axiom_statement(self, axiom_name: str) -> SymbolicExpression:
        """Get symbolic statement of an axiom."""
        statements = {
            "axiom1": SymbolicExpression.Implies(
                SymbolicExpression.And(
                    SymbolicExpression.primitive("T", "T_bowtie"),
                    SymbolicExpression.primitive("P", "P_pm_sym"),
                ),
                SymbolicExpression.Or(
                    SymbolicExpression.primitive("F", "F_hbar"),
                    SymbolicExpression.primitive("F", "F_eth"),
                ),
            ),
            "axiom2": SymbolicExpression.Not(
                SymbolicExpression.And(
                    SymbolicExpression.primitive("G", "G_beth"),
                    SymbolicExpression.primitive("Γ", "Gamma_and(SPECIFIC)"),
                    SymbolicExpression.primitive("G", "G_aleph"),  # Can propagate to global
                ),
            ),
            "axiom4": SymbolicExpression.Implies(
                SymbolicExpression.primitive("Γ", "Gamma_seq(SELECTIVE)"),
                SymbolicExpression.Or(
                    SymbolicExpression.primitive("D", "D_infinity"),
                    SymbolicExpression.primitive("R", "R_dagger"),
                ),
            ),
        }
        return statements.get(axiom_name, SymbolicExpression(
            SymbolicOperator.EQ, ["axiom", axiom_name]
        ))
    
    def _check_axiom_applicability(
        self,
        axiom_name: str,
        synthon: Synthon,
    ) -> bool:
        """Check if an axiom applies to a synthon."""
        if axiom_name == "axiom1":
            return (synthon.topology == Topology.CYCLIC_BOWTIE and
                    synthon.polarity.is_self_complementary)
        elif axiom_name == "axiom2":
            return (synthon.granularity == Granularity.LOCAL and
                    synthon.interaction_grammar.tier == "SPECIFIC")
        elif axiom_name == "axiom4":
            return (synthon.interaction_grammar.operator == GrammarOperator.SEQUENTIAL)
        return True
    
    def _evaluate_axiom(self, axiom_name: str, synthon: Synthon) -> bool:
        """Evaluate an axiom against a synthon."""
        # Use AxiomValidator for consistency
        validator_result = AxiomValidator.validate_all_axioms(synthon)
        axiom_result = validator_result["detailed_results"].get(axiom_name, {})
        return not axiom_result.get("violated", False)
    
    def find_counter_examples(
        self,
        axiom_name: str,
        max_search: int = 100,
    ) -> List[TheoremProof]:
        """
        Search for counter-examples to an axiom.
        
        Args:
            axiom_name: Axiom to test
            max_search: Maximum number of synthetic synthons to generate
        
        Returns:
            List of TheoremProof objects for counter-examples found
        """
        counter_proofs = []
        
        # Generate synthetic synthons to test
        test_synthons = self._generate_test_synthons(max_search)
        
        for synthon in test_synthons:
            proof = self.prove_axiom(axiom_name, [synthon])
            if not proof.proven:
                counter_proofs.append(proof)
        
        return counter_proofs
    
    def _generate_test_synthons(self, count: int) -> List[Synthon]:
        """Generate synthetic synthons for testing."""
        synthons = []
        
        # Generate combinations that might violate axioms
        for i in range(count):
            # Systematically vary primitives
            topology = [Topology.CYCLIC_BOWTIE, Topology.CHAIN][i % 2]
            polarity = [Polarity.SELF_COMPLEMENTARY_SYM, Polarity.DONOR][i % 2]
            fidelity = [Fidelity.LOW, Fidelity.HIGH][i % 2]
            
            synthon = Synthon(
                name=f"test_synthon_{i}",
                dimensionality=Dimensionality.MOLECULAR,
                topology=topology,
                recognition_mode=RecognitionMode.NON_COVALENT,
                polarity=polarity,
                fidelity=fidelity,
                kinetic_character=KineticCharacter.MODERATE,
                granularity=Granularity.LOCAL,
                interaction_grammar=InteractionGrammar.SELECTIVE_AND,
            )
            synthons.append(synthon)
        
        return synthons


# =============================================================================
# Cross-Domain Analogy Detection
# =============================================================================

@dataclass
class AnalogyResult:
    """Result of cross-domain analogy detection."""
    synthon_a: str
    synthon_b: str
    similarity_score: float  # 0.0-1.0
    shared_primitives: List[str]
    differing_primitives: List[str]
    analogy_type: str  # "structural", "functional", "behavioral"
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "synthon_a": self.synthon_a,
            "synthon_b": self.synthon_b,
            "similarity_score": self.similarity_score,
            "shared_primitives": self.shared_primitives,
            "differing_primitives": self.differing_primitives,
            "analogy_type": self.analogy_type,
            "confidence": self.confidence,
        }


class CrossDomainAnalogyDetector:
    """
    Detects formal analogies across molecular, supramolecular, and temporal domains.
    
    From QUANTIG.md Section IX:
    "The framework enables cross-domain similarity search: because the same notation
    applies to molecular, supramolecular, and temporal systems, queries can find
    conceptual analogies across disciplinary boundaries."
    """
    
    # Primitive weights for similarity computation.
    # D and Φ must be present so that cross-domain pairs (D_∧ vs D_∞) and
    # criticality differences are reflected in the similarity score and
    # correctly reported in the shared/differing primitive lists.
    # The code self-normalises by dividing by total_weight, so absolute
    # magnitudes determine relative importance, not whether they sum to 1.
    PRIMITIVE_WEIGHTS = {
        "D": 0.20,  # Dimensionality — fundamental domain axis; cross-domain pairs penalised when D differs
        "T": 0.25,  # Topology is highly diagnostic
        "R": 0.20,  # Recognition mode
        "Γ": 0.20,  # Interaction grammar
        "F": 0.15,  # Fidelity
        "G": 0.10,  # Granularity
        "P": 0.05,  # Polarity
        "K": 0.05,  # Kinetic character
        "Φ": 0.05,  # Criticality phase
        "S": 0.08,  # Stoichiometry — raised from 0.05; valency-sensitive for T⋈ systems
    }
    
    def compute_similarity(
        self,
        synthon_a: Synthon,
        synthon_b: Synthon,
    ) -> AnalogyResult:
        """
        Compute formal similarity between two synthons.
        
        Args:
            synthon_a: First synthon
            synthon_b: Second synthon
        
        Returns:
            AnalogyResult with similarity metrics
        """
        # Extract primitive values
        primitives_a = self._extract_primitives(synthon_a)
        primitives_b = self._extract_primitives(synthon_b)
        
        # Compute weighted similarity
        total_weight = 0.0
        weighted_similarity = 0.0
        shared = []
        differing = []
        
        for prim_name, weight in self.PRIMITIVE_WEIGHTS.items():
            val_a = primitives_a.get(prim_name, "")
            val_b = primitives_b.get(prim_name, "")

            if prim_name == "S":
                # Stoichiometry uses a graded similarity rather than exact match
                s_sim = self._stoichiometry_similarity(
                    synthon_a.stoichiometry, synthon_b.stoichiometry
                )
                weighted_similarity += weight * s_sim
                if s_sim >= 0.95:
                    shared.append(prim_name)
                elif s_sim > 0.0:
                    # Partial match: show in differing with score
                    differing.append(f"S({s_sim:.2f})")
                else:
                    differing.append(prim_name)
            elif val_a == val_b:
                weighted_similarity += weight
                shared.append(prim_name)
            else:
                differing.append(prim_name)

            total_weight += weight
        
        similarity_score = weighted_similarity / total_weight if total_weight > 0 else 0.0
        
        # Determine analogy type
        analogy_type = self._classify_analogy(synthon_a, synthon_b, shared)
        
        # Compute confidence
        confidence = self._compute_confidence(synthon_a, synthon_b, similarity_score)
        
        return AnalogyResult(
            synthon_a=synthon_a.name,
            synthon_b=synthon_b.name,
            similarity_score=similarity_score,
            shared_primitives=shared,
            differing_primitives=differing,
            analogy_type=analogy_type,
            confidence=confidence,
        )
    
    def _extract_primitives(self, synthon: Synthon) -> Dict[str, str]:
        """Extract primitive values from synthon."""
        return {
            "D": synthon.dimensionality.value,
            "T": synthon.topology.value,
            "R": synthon.recognition_mode.value,
            "P": synthon.polarity.value,
            "F": synthon.fidelity.value,
            "K": synthon.kinetic_character.value,
            "G": synthon.granularity.value,
            "Γ": f"{synthon.interaction_grammar.operator.value}({synthon.interaction_grammar.tier})",
            "Φ": synthon.criticality_phase.value if synthon.criticality_phase else "Phi_sub",
            "S": synthon.stoichiometry or "unset",  # stub: "unset" == "unset" matches
        }

    @staticmethod
    def _stoichiometry_similarity(s1: Optional[str], s2: Optional[str]) -> float:
        """
        Graded similarity score for stoichiometry pairs (Phase 3.1 calibration).

        Rules (priority order, highest to lowest):
          Both unset           → 1.0  (no info to penalise)
          One unset            → 0.5  (partial information)
          Exact string match   → 1.0
          Same category (both symmetric a:a, or both asymmetric a:b with a≠b) → 0.9
          Ratio diff |r1–r2| < 0.5  → 0.7
          Otherwise: linear drop from 0.7 at diff=0.5 down to 0.2 at diff=2.0+
          Non-parseable strings → 0.0

        Symmetric = n:m where n==m (e.g. 1:1, 2:2).
        Asymmetric = n:m where n≠m (e.g. 2:1, 3:2).
        """
        if s1 is None and s2 is None:
            return 1.0
        if s1 is None or s2 is None:
            return 0.5
        if s1 == s2:
            return 1.0
        try:
            a1, b1 = (int(x) for x in s1.split(":"))
            a2, b2 = (int(x) for x in s2.split(":"))
            r1 = a1 / b1 if b1 != 0 else 0.0
            r2 = a2 / b2 if b2 != 0 else 0.0
            sym1 = (a1 == b1)   # symmetric: n:n
            sym2 = (a2 == b2)
            if sym1 == sym2:
                # Same category (both symmetric or both asymmetric)
                return 0.9
            else:
                # Category mismatch (one sym, one asym) → ratio-based fallback
                diff = abs(r1 - r2)
                if diff < 0.5:
                    return 0.7
                # Linear drop from 0.7 at diff=0.5 to 0.2 at diff=2.0
                score = 0.7 - (diff - 0.5) / 1.5 * 0.5
                return max(0.2, round(score, 4))
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _classify_analogy(
        self,
        synthon_a: Synthon,
        synthon_b: Synthon,
        shared_primitives: List[str],
    ) -> str:
        """Classify the type of analogy."""
        # Check domain overlap
        domains_a = synthon_a.dimensionality.domains
        domains_b = synthon_b.dimensionality.domains
        
        if domains_a & domains_b:
            # Same domain → structural analogy
            return "structural"
        elif "T" in shared_primitives and "R" in shared_primitives:
            # Same topology and recognition → functional analogy
            return "functional"
        elif "F" in shared_primitives and "Γ" in shared_primitives:
            # Same fidelity and grammar → behavioral analogy
            return "behavioral"
        else:
            return "formal"
    
    def _compute_confidence(
        self,
        synthon_a: Synthon,
        synthon_b: Synthon,
        similarity_score: float,
    ) -> float:
        """Compute confidence in the analogy."""
        # Base confidence from similarity
        confidence = similarity_score
        
        # Boost if thermodynamic metrics are similar
        try:
            xi_a = compute_xi_CP(synthon_a, delta_g=-50.0)
            xi_b = compute_xi_CP(synthon_b, delta_g=-50.0)
            xi_diff = abs(xi_a - xi_b)
            
            if xi_diff < 1.0:
                confidence = min(1.0, confidence + 0.1)
        except Exception:
            pass
        
        return confidence
    
    def find_analogies(
        self,
        query_synthon: Synthon,
        candidate_synthons: List[Synthon],
        min_similarity: float = 0.5,
    ) -> List[AnalogyResult]:
        """
        Find analogies to a query synthon in a set of candidates.
        
        Args:
            query_synthon: Query synthon
            candidate_synthons: Candidate synthons to search
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of AnalogyResult objects, sorted by similarity
        """
        results = []
        
        for candidate in candidate_synthons:
            if candidate.name == query_synthon.name:
                continue
            
            result = self.compute_similarity(query_synthon, candidate)
            
            if result.similarity_score >= min_similarity:
                results.append(result)
        
        # Sort by similarity (descending)
        results.sort(key=lambda r: -r.similarity_score)
        
        return results


# =============================================================================
# Predictive Rule Generation
# =============================================================================

@dataclass
class PredictiveRule:
    """A predictive rule derived from the grammar."""
    rule_id: str
    antecedent: SymbolicExpression  # IF part
    consequent: SymbolicExpression  # THEN part
    confidence: float  # 0.0-1.0
    support_count: int  # Number of synthons supporting rule
    falsified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "antecedent": str(self.antecedent),
            "consequent": str(self.consequent),
            "confidence": self.confidence,
            "support_count": self.support_count,
            "falsified": self.falsified,
        }
    
    def __str__(self) -> str:
        status = "✗ FALSIFIED" if self.falsified else "✓"
        return f"{status} {self.antecedent} → {self.consequent} (confidence: {self.confidence:.1%})"


class PredictiveRuleGenerator:
    """
    Generates predictive rules from synthon data.
    
    Uses inductive logic programming to discover rules of the form:
    IF (T = T_bowtie AND P = P_pm) THEN (F ≥ F_eth)
    """
    
    def __init__(self):
        self.rules: List[PredictiveRule] = []
        self.rule_counter = 0
    
    def generate_rules(
        self,
        synthons: List[Synthon],
        min_support: int = 3,
        min_confidence: float = 0.7,
    ) -> List[PredictiveRule]:
        """
        Generate predictive rules from synthon data.
        
        Args:
            synthons: Training synthons
            min_support: Minimum number of synthons supporting rule
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of generated PredictiveRule objects
        """
        self.rules = []
        self.rule_counter = 0

        # Generate candidate rules from axiom patterns
        candidate_rules = self._generate_candidate_rules()

        # Evaluate each candidate; collect those that pass thresholds
        for antecedent, consequent in candidate_rules:
            rule = self._evaluate_rule(antecedent, consequent, synthons)

            if (rule.support_count >= min_support and
                    rule.confidence >= min_confidence):
                self.rules.append(rule)

        # Reassign sequential IDs on the filtered list so there are no gaps
        for idx, rule in enumerate(self.rules, 1):
            rule.rule_id = f"rule_{idx:03d}"

        return self.rules
    
    def _generate_candidate_rules(self) -> List[Tuple[SymbolicExpression, SymbolicExpression]]:
        """Generate candidate rule templates derived from axioms and primitive constraints."""
        P = SymbolicExpression.primitive
        And = SymbolicExpression.And
        Or = SymbolicExpression.Or
        Not = SymbolicExpression.Not

        candidates = []

        # ── Axiom 1 (T_⋈ closure amplifies fidelity) ──────────────────────────
        # Symmetric self-complementary cyclic motifs → F ≥ F_eth
        candidates.append((
            And(P("T", "T_bowtie"), P("P", "P_pm_sym")),
            Or(P("F", "F_hbar"), P("F", "F_eth")),
        ))
        # Pseudosymmetric self-complementary cyclic motifs → F ≥ F_eth
        candidates.append((
            And(P("T", "T_bowtie"), P("P", "P_pm_pseudo")),
            Or(P("F", "F_hbar"), P("F", "F_eth")),
        ))

        # ── Axiom 4 (Γ_→ requires D_∞ or R_‡) ────────────────────────────────
        # Sequential grammar (any tier) → temporal or catalytic dimension
        candidates.append((
            Or(
                P("Γ", "Gamma_seq(SPECIFIC)"),
                P("Γ", "Gamma_seq(SELECTIVE)"),
                P("Γ", "Gamma_seq(BROAD)"),
            ),
            Or(
                P("D", "D_infinity"),
                P("D", "D_wedge_infinity"),
                P("D", "D_triangle_infinity"),
                P("D", "D_all"),
                P("R", "R_dagger"),
            ),
        ))

        # ── Kinetic-thermodynamic coupling (rule_002 in prior version) ─────────
        candidates.append((
            And(P("F", "F_hbar"), P("K", "K_fast")),
            P("Φ", "Phi_sub"),
        ))

        # ── R → F coupling ─────────────────────────────────────────────────────
        # Covalent recognition → high fidelity (bond-energy argument)
        candidates.append((
            P("R", "R_subset"),
            P("F", "F_hbar"),
        ))
        # Dynamic covalent → F_hbar or F_eth (imine, disulfide: reversible but reliable)
        candidates.append((
            P("R", "R_covalent_dynamic"),
            Or(P("F", "F_hbar"), P("F", "F_eth")),
        ))

        # ── R_⇔ → T_⋈ (mechanical bond requires cyclic wheel topology) ─────────
        candidates.append((
            P("R", "R_mechanical"),
            P("T", "T_bowtie"),
        ))

        # ── T_⋈ ∧ R_⇔ → K_mod ∨ K_slow (dethreading barrier) ─────────────────
        candidates.append((
            And(P("T", "T_bowtie"), P("R", "R_mechanical")),
            Or(P("K", "K_mod"), P("K", "K_slow")),
        ))

        # ── Scale-topology coupling ─────────────────────────────────────────────
        # Global-scale control requires hub, network, or cage topology
        candidates.append((
            P("G", "G_aleph"),
            Or(P("T", "T_square"), P("T", "T_network"), P("T", "T_cage")),
        ))
        # Molecular dimensionality → not global scale
        candidates.append((
            P("D", "D_wedge"),
            Or(P("G", "G_beth"), P("G", "G_gimel")),
        ))

        # ── Fidelity-granularity coupling ───────────────────────────────────────
        # Global propagation requires at least medium fidelity
        candidates.append((
            P("G", "G_aleph"),
            Or(P("F", "F_hbar"), P("F", "F_eth")),
        ))

        # ── Temporal dimension → kinetic accessibility ──────────────────────────
        # Catalytic cycles have turnover rates; K_fast is unphysical for D_∞
        candidates.append((
            P("D", "D_infinity"),
            Or(P("K", "K_mod"), P("K", "K_slow")),
        ))
        # Catalytic recognition mode → temporal or hybrid temporal dimension
        candidates.append((
            P("R", "R_dagger"),
            Or(
                P("D", "D_infinity"),
                P("D", "D_wedge_infinity"),
                P("D", "D_triangle_infinity"),
                P("D", "D_all"),
            ),
        ))

        # ── Hub-node granularity amplification ─────────────────────────────────
        candidates.append((
            And(P("T", "T_square"), P("R", "R_superset")),
            Or(P("G", "G_gimel"), P("G", "G_aleph")),
        ))

        # ── Φ_c indicator: K_trap in a cyclic system (Axiom 5 / Groppi anchor) ─
        # All-or-nothing steric cliff in T_⋈ → criticality candidacy
        candidates.append((
            And(P("T", "T_bowtie"), P("K", "K_trap")),
            P("Φ", "Phi_c"),
        ))

        # ── Cage topology (Axiom 1 analogue + kinetic encapsulation) ───────────
        # T_□□ with non-covalent recognition → F ≥ F_eth
        candidates.append((
            And(P("T", "T_cage"), P("R", "R_superset")),
            Or(P("F", "F_hbar"), P("F", "F_eth")),
        ))
        # T_□□ → K_mod or K_slow (enclosed cage always has exchange barrier)
        candidates.append((
            P("T", "T_cage"),
            Or(P("K", "K_mod"), P("K", "K_slow")),
        ))

        return candidates
    
    def _evaluate_rule(
        self,
        antecedent: SymbolicExpression,
        consequent: SymbolicExpression,
        synthons: List[Synthon],
    ) -> PredictiveRule:
        """Evaluate a rule against synthon data."""
        self.rule_counter += 1
        
        supporting = 0
        total_applicable = 0
        falsified = False
        
        for synthon in synthons:
            # Check if antecedent applies
            if antecedent.evaluate(synthon):
                total_applicable += 1
                
                # Check if consequent holds
                if consequent.evaluate(synthon):
                    supporting += 1
                else:
                    falsified = True  # Found counter-example
        
        confidence = supporting / total_applicable if total_applicable > 0 else 0.0
        
        return PredictiveRule(
            rule_id=f"rule_{self.rule_counter:03d}",
            antecedent=antecedent,
            consequent=consequent,
            confidence=confidence,
            support_count=supporting,
            falsified=falsified,
        )
    
    def test_rule(
        self,
        rule: PredictiveRule,
        test_synthons: List[Synthon],
    ) -> PredictiveRule:
        """
        Test a rule against new data (falsification attempt).
        
        Args:
            rule: Rule to test
            test_synthons: Test synthons
        
        Returns:
            Updated PredictiveRule
        """
        for synthon in test_synthons:
            if rule.antecedent.evaluate(synthon):
                if not rule.consequent.evaluate(synthon):
                    rule.falsified = True
                    break
        
        return rule


# =============================================================================
# Main Symbolic Reasoning Engine
# =============================================================================

class SymbolicReasoningEngine:
    """
    Main engine for symbolic reasoning in the Synthonicon framework.
    
    Integrates:
    - Primitive algebra
    - Axiom theorem proving
    - Cross-domain analogy detection
    - Predictive rule generation
    - Falsification search
    """
    
    def __init__(self, catalog=None):
        """Initialize engine with optional catalog."""
        self.catalog = catalog
        self.grammar_algebra = GrammarAlgebra()
        self.gd_tensor = GDTensor()
        self.theorem_prover = AxiomTheoremProver(catalog)
        self.analogy_detector = CrossDomainAnalogyDetector()
        self.rule_generator = PredictiveRuleGenerator()
    
    def validate_grammar(
        self,
        synthon: Synthon,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive grammar validation on a synthon.
        
        Args:
            synthon: Synthon to validate
        
        Returns:
            Validation report
        """
        report = {
            "synthon": synthon.name,
            "notation": synthon.to_notation(),
            "axiom_validation": {},
            "gd_independence": self.gd_tensor.compute_independence(synthon),
            "is_critical": self.gd_tensor.check_degeneracy(synthon),
            "predictions": [],
        }
        
        # Validate all axioms
        for axiom_name in ["axiom1", "axiom2", "axiom3", "axiom4", "axiom5"]:
            proof = self.theorem_prover.prove_axiom(axiom_name, [synthon])
            report["axiom_validation"][axiom_name] = {
                "applies": self.theorem_prover._check_axiom_applicability(axiom_name, synthon),
                "satisfied": proof.proven,
                "violated": not proof.proven,
            }
        
        # Generate predictions
        rules = self.rule_generator.generate_rules([synthon], min_support=1, min_confidence=0.5)
        report["predictions"] = [str(rule) for rule in rules]
        
        return report
    
    def find_cross_domain_analogies(
        self,
        query_name: str,
        min_similarity: float = 0.5,
    ) -> List[AnalogyResult]:
        """
        Find cross-domain analogies to a query synthon.
        
        Args:
            query_name: Name of query synthon in catalog
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of analogy results
        """
        if not self.catalog:
            return []
        
        query = self.catalog.get(query_name)
        if not query:
            return []
        
        candidates = list(self.catalog._synthons.values())
        return self.analogy_detector.find_analogies(query, candidates, min_similarity)
    
    def discover_rules(
        self,
        min_support: int = 3,
        min_confidence: float = 0.7,
    ) -> List[PredictiveRule]:
        """
        Discover predictive rules from the catalog.
        
        Args:
            min_support: Minimum support threshold
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of discovered rules
        """
        if not self.catalog:
            return []
        
        synthons = list(self.catalog._synthons.values())
        return self.rule_generator.generate_rules(synthons, min_support, min_confidence)
    
    def attempt_falsification(
        self,
        rule: PredictiveRule,
        max_attempts: int = 100,
    ) -> PredictiveRule:
        """
        Attempt to falsify a rule by generating counter-examples.
        
        Args:
            rule: Rule to falsify
            max_attempts: Maximum generation attempts
        
        Returns:
            Updated rule (may be marked as falsified)
        """
        test_synthons = self.theorem_prover._generate_test_synthons(max_attempts)
        return self.rule_generator.test_rule(rule, test_synthons)

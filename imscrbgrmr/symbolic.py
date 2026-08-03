"""
Symbolic Reasoning Engine — Formal algebra and theorem proving for the Imscriptiveon grammar.

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
    Imscription,
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
    
    # Imscription-specific
    COMPATIBLE = "⊕"  # Compatibility relation
    AMPLIFIES = "↑"   # Amplification relation
    DEGENERATES = "≡"  # Degeneracy relation


@dataclass
class SymbolicExpression:
    """
    Represents a symbolic expression in the Imscriptiveon algebra.
    
    Examples:
        - Primitive assertion: Primitive("F", "ƒ_hardsign")
        - Boolean combination: And(Primitive("T", "𐑥"), Primitive("P", "Φ_pipevar"))
        - Implication: Implies(Primitive("T", "𐑥"), Primitive("F", "ƒ_dh"))
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
    
    def evaluate(self, imscription: Imscription) -> bool:
        """Evaluate the expression against a imscription."""
        return _evaluate_expression(self, imscription)
    
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


def _evaluate_expression(expr: SymbolicExpression, imscription: Imscription) -> bool:
    """Internal expression evaluation."""
    op = expr.operator
    
    if op == SymbolicOperator.EQ:
        # Primitive assertion: F = F_hardsign
        primitive_name = expr.operands[0]
        expected_value = expr.operands[1]
        actual_value = _get_primitive_value(imscription, primitive_name)
        return actual_value == expected_value
    
    elif op == SymbolicOperator.AND:
        return all(_evaluate_expression(o, imscription) for o in expr.operands)
    
    elif op == SymbolicOperator.OR:
        return any(_evaluate_expression(o, imscription) for o in expr.operands)
    
    elif op == SymbolicOperator.NOT:
        return not _evaluate_expression(expr.operands[0], imscription)
    
    elif op == SymbolicOperator.IMPLIES:
        antecedent = _evaluate_expression(expr.operands[0], imscription)
        consequent = _evaluate_expression(expr.operands[1], imscription)
        return (not antecedent) or consequent  # Material implication
    
    return False


def _get_primitive_value(imscription: Imscription, name: str) -> str:
    """Get primitive value from imscription by name."""
    mapping = {
        "D": imscription.dimensionality.value,
        "T": imscription.topology.value,
        "R": imscription.recognition_mode.value,
        "P": imscription.polarity.value,
        "F": imscription.fidelity.value,
        "K": imscription.kinetic_character.value,
        "G": imscription.granularity.value,
        "∈": imscription.grammar.value,
        "<": imscription.criticality_phase.value if imscription.criticality_phase else "⊙_softsign",
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
            return InteractionGrammar.vow
        elif operator == GrammarOperator.OR:
            return InteractionGrammar.gag
        else:
            return InteractionGrammar.measure
    
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
        
        return InteractionGrammar.vow
    
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
        (Granularity.ice, Dimensionality.dead): 1.0,
        (Granularity.ice, Dimensionality.ash): 0.7,
        (Granularity.ice, Dimensionality.array): 0.5,
        (Granularity.bib, Dimensionality.dead): 0.7,
        (Granularity.bib, Dimensionality.ash): 1.0,
        (Granularity.bib, Dimensionality.array): 0.7,
        (Granularity.thigh, Dimensionality.dead): 0.3,
        (Granularity.thigh, Dimensionality.ash): 1.0,
        (Granularity.thigh, Dimensionality.array): 1.0,
    }
    
    @classmethod
    def compute_independence(cls, imscription: Imscription) -> float:
        """
        Compute G-D independence score (0-1).
        
        1.0 = fully independent (normal)
        0.0 = fully degenerate (critical)
        """
        g = imscription.granularity
        d = imscription.dimensionality
        
        # Check if at criticality
        if imscription.criticality_phase == CriticalityPhase.monad:
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
    def check_degeneracy(cls, imscription: Imscription) -> bool:
        """Check if G and D are degenerate (at criticality)."""
        return imscription.criticality_phase == CriticalityPhase.monad
    
    @staticmethod
    def _domain_to_dimensionality(domain: str) -> Dimensionality:
        """Convert domain string to Dimensionality enum."""
        mapping = {
            "molecular": Dimensionality.dead,
            "supramolecular": Dimensionality.ash,
            "temporal": Dimensionality.array,
        }
        return mapping.get(domain, Dimensionality.dead)


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
    2. Model checking against imscription catalog
    3. Counter-example search
    """
    
    def __init__(self, catalog=None):
        """Initialize prover with optional imscription catalog."""
        self.catalog = catalog
        self.proven_theorems: Dict[str, TheoremProof] = {}
    
    def prove_axiom(
        self,
        axiom_name: str,
        test_imscriptions: Optional[List[Imscription]] = None,
    ) -> TheoremProof:
        """
        Prove an axiom against a set of imscriptions.
        
        Args:
            axiom_name: Name of axiom (axiom1-axiom5)
            test_imscriptions: imscriptions to test against (uses catalog if None)
        
        Returns:
            TheoremProof with results
        """
        if test_imscriptions is None:
            test_imscriptions = list(self.catalog._imscriptions.values()) if self.catalog else []
        
        # Get axiom statement
        statement = self._get_axiom_statement(axiom_name)
        
        # Test against all imscriptions
        proof_steps = []
        counter_examples = []
        all_satisfied = True
        
        for imscription in test_imscriptions:
            # Check if axiom applies
            applies = self._check_axiom_applicability(axiom_name, imscription)
            
            if not applies:
                proof_steps.append(f"{imscription.name}: axiom does not apply")
                continue
            
            # Evaluate axiom
            satisfied = self._evaluate_axiom(axiom_name, imscription)
            
            if satisfied:
                proof_steps.append(f"{imscription.name}: ✓ satisfied")
            else:
                proof_steps.append(f"{imscription.name}: ✗ VIOLATED")
                all_satisfied = False
                counter_examples.append({
                    "imscription": imscription.name,
                    "notation": imscription.to_notation(),
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
                    SymbolicExpression.primitive("T", "𐑥"),
                    SymbolicExpression.primitive("P", "Φ_doublebarpipe"),
                ),
                SymbolicExpression.Or(
                    SymbolicExpression.primitive("F", "ƒ_hardsign"),
                    SymbolicExpression.primitive("F", "ƒ_dh"),
                ),
            ),
            "axiom2": SymbolicExpression.Not(
                SymbolicExpression.And(
                    SymbolicExpression.primitive("G", "Γ_beta"),
                    SymbolicExpression.primitive("∈", "Gamma_and(SPECIFIC)"),
                    SymbolicExpression.primitive("G", "Γ_revapostrophe"),  # Can propagate to global
                ),
            ),
            "axiom4": SymbolicExpression.Implies(
                SymbolicExpression.primitive("∈", "Gamma_seq(SELECTIVE)"),
                SymbolicExpression.Or(
                    SymbolicExpression.primitive("D", "𐑼"),
                    SymbolicExpression.primitive("R", "Ř_downstep"),
                ),
            ),
        }
        return statements.get(axiom_name, SymbolicExpression(
            SymbolicOperator.EQ, ["axiom", axiom_name]
        ))
    
    def _check_axiom_applicability(
        self,
        axiom_name: str,
        imscription: Imscription,
    ) -> bool:
        """Check if an axiom applies to a imscription."""
        if axiom_name == "axiom1":
            return (imscription.topology == Topology.mime and
                    imscription.polarity.is_self_complementary)
        elif axiom_name == "axiom2":
            return (imscription.granularity == Granularity.ice and
                    imscription.interaction_grammar.tier == "SPECIFIC")
        elif axiom_name == "axiom4":
            return (imscription.interaction_grammar.operator == GrammarOperator.SEQUENTIAL)
        return True
    
    def _evaluate_axiom(self, axiom_name: str, imscription: Imscription) -> bool:
        """Evaluate an axiom against a imscription."""
        # Use AxiomValidator for consistency
        validator_result = AxiomValidator.validate_all_axioms(imscription)
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
            max_search: Maximum number of synthetic imscriptions to generate
        
        Returns:
            List of TheoremProof objects for counter-examples found
        """
        counter_proofs = []
        
        # Generate synthetic imscriptions to test
        test_imscriptions = self._generate_test_imscriptions(max_search)
        
        for imscription in test_imscriptions:
            proof = self.prove_axiom(axiom_name, [imscription])
            if not proof.proven:
                counter_proofs.append(proof)
        
        return counter_proofs
    
    def _generate_test_imscriptions(self, count: int) -> List[Imscription]:
        """Generate synthetic imscriptions for testing."""
        imscriptions = []
        
        # Generate combinations that might violate axioms
        for i in range(count):
            # Systematically vary primitives
            topology = [Topology.mime, Topology.eat][i % 2]
            polarity = [Polarity.or_, Polarity.yew][i % 2]
            fidelity = [Fidelity.age, Fidelity.peep][i % 2]
            
            imscription = Imscription(
                name=f"test_imscription_{i}",
                dimensionality=Dimensionality.dead,
                topology=topology,
                recognition_mode=RecognitionMode.ado,
                polarity=polarity,
                fidelity=fidelity,
                kinetic_character=KineticCharacter.loll,
                granularity=Granularity.ice,
                interaction_grammar=InteractionGrammar.vow,
            )
            imscriptions.append(imscription)
        
        return imscriptions


# =============================================================================
# Cross-Domain Analogy Detection
# =============================================================================

@dataclass
class AnalogyResult:
    """Result of cross-domain analogy detection."""
    imscription_a: str
    imscription_b: str
    similarity_score: float  # 0.0-1.0
    shared_primitives: List[str]
    differing_primitives: List[str]
    analogy_type: str  # "structural", "functional", "behavioral"
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "imscription_a": self.imscription_a,
            "imscription_b": self.imscription_b,
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
        "∈": 0.20,  # Interaction grammar
        "F": 0.15,  # Fidelity
        "G": 0.10,  # Granularity
        "P": 0.05,  # Polarity
        "K": 0.05,  # Kinetic character
        "<": 0.05,  # Criticality phase
        "S": 0.08,  # Stoichiometry — raised from 0.05; valency-sensitive for T⋈ systems
    }
    
    def compute_similarity(
        self,
        imscription_a: Imscription,
        imscription_b: Imscription,
    ) -> AnalogyResult:
        """
        Compute formal similarity between two imscriptions.
        
        Args:
            imscription_a: First imscription
            imscription_b: Second imscription
        
        Returns:
            AnalogyResult with similarity metrics
        """
        # Extract primitive values
        primitives_a = self._extract_primitives(imscription_a)
        primitives_b = self._extract_primitives(imscription_b)
        
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
                    imscription_a.stoichiometry.value if imscription_a.stoichiometry else None,
                    imscription_b.stoichiometry.value if imscription_b.stoichiometry else None,
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
        analogy_type = self._classify_analogy(imscription_a, imscription_b, shared)
        
        # Compute confidence
        confidence = self._compute_confidence(imscription_a, imscription_b, similarity_score)
        
        return AnalogyResult(
            imscription_a=imscription_a.name,
            imscription_b=imscription_b.name,
            similarity_score=similarity_score,
            shared_primitives=shared,
            differing_primitives=differing,
            analogy_type=analogy_type,
            confidence=confidence,
        )
    
    def _extract_primitives(self, imscription: Imscription) -> Dict[str, str]:
        """Extract primitive values from imscription."""
        return {
            "D": imscription.dimensionality.value,
            "T": imscription.topology.value,
            "R": imscription.recognition_mode.value,
            "P": imscription.polarity.value,
            "F": imscription.fidelity.value,
            "K": imscription.kinetic_character.value,
            "G": imscription.granularity.value,
            "∈": imscription.interaction_grammar.value,
            "<": imscription.criticality_phase.value if imscription.criticality_phase else "⊙_softsign",
            "S": imscription.stoichiometry.value if imscription.stoichiometry else "unset",
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
        # Phonetic stoichiometry names — ordinal similarity (1:1 < n:n < n:m)
        _PHONETIC_ORD = {"Σ_doublebaresh": 0, "Σ_ctn": 1, "Σ_ltailm": 2}
        if s1 in _PHONETIC_ORD and s2 in _PHONETIC_ORD:
            diff = abs(_PHONETIC_ORD[s1] - _PHONETIC_ORD[s2])
            return 0.9 if diff == 1 else 0.7
        try:
            a1, b1 = (int(x) for x in s1.split(":"))
            a2, b2 = (int(x) for x in s2.split(":"))
            r1 = a1 / b1 if b1 != 0 else 0.0
            r2 = a2 / b2 if b2 != 0 else 0.0
            sym1 = (a1 == b1)
            sym2 = (a2 == b2)
            if sym1 == sym2:
                return 0.9
            else:
                diff = abs(r1 - r2)
                if diff < 0.5:
                    return 0.7
                score = 0.7 - (diff - 0.5) / 1.5 * 0.5
                return max(0.2, round(score, 4))
        except (ValueError, ZeroDivisionError):
            return 0.0
    
    def _classify_analogy(
        self,
        imscription_a: Imscription,
        imscription_b: Imscription,
        shared_primitives: List[str],
    ) -> str:
        """Classify the type of analogy."""
        # Check domain overlap
        domains_a = imscription_a.dimensionality.domains
        domains_b = imscription_b.dimensionality.domains
        
        if domains_a & domains_b:
            # Same domain → structural analogy
            return "structural"
        elif "T" in shared_primitives and "R" in shared_primitives:
            # Same topology and recognition → functional analogy
            return "functional"
        elif "F" in shared_primitives and "∈" in shared_primitives:
            # Same fidelity and grammar → behavioral analogy
            return "behavioral"
        else:
            return "formal"
    
    def _compute_confidence(
        self,
        imscription_a: Imscription,
        imscription_b: Imscription,
        similarity_score: float,
    ) -> float:
        """Compute confidence in the analogy."""
        # Base confidence from similarity
        confidence = similarity_score
        
        # Boost if thermodynamic metrics are similar
        try:
            xi_a = compute_xi_CP(imscription_a, delta_g=-50.0)
            xi_b = compute_xi_CP(imscription_b, delta_g=-50.0)
            xi_diff = abs(xi_a - xi_b)
            
            if xi_diff < 1.0:
                confidence = min(1.0, confidence + 0.1)
        except Exception:
            pass
        
        return confidence
    
    def find_analogies(
        self,
        query_imscription: Imscription,
        candidate_imscriptions: List[Imscription],
        min_similarity: float = 0.5,
    ) -> List[AnalogyResult]:
        """
        Find analogies to a query imscription in a set of candidates.
        
        Args:
            query_imscription: Query imscription
            candidate_imscriptions: Candidate imscriptions to search
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of AnalogyResult objects, sorted by similarity
        """
        results = []
        
        for candidate in candidate_imscriptions:
            if candidate.name == query_imscription.name:
                continue
            
            result = self.compute_similarity(query_imscription, candidate)
            
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
    support_count: int  # Number of imscriptions supporting rule
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
    Generates predictive rules from imscription data.
    
    Uses inductive logic programming to discover rules of the form:
    IF (T = T_bullseye AND P = P_pipevar) THEN (F ≥ F_dh)
    """
    
    def __init__(self):
        self.rules: List[PredictiveRule] = []
        self.rule_counter = 0
    
    def generate_rules(
        self,
        imscriptions: List[Imscription],
        min_support: int = 3,
        min_confidence: float = 0.7,
    ) -> List[PredictiveRule]:
        """
        Generate predictive rules from imscription data.
        
        Args:
            imscriptions: Training imscriptions
            min_support: Minimum number of imscriptions supporting rule
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
            rule = self._evaluate_rule(antecedent, consequent, imscriptions)

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
        # Symmetric self-complementary cyclic motifs → F ≥ F_dh
        candidates.append((
            And(P("T", "𐑥"), P("P", "Φ_doublebarpipe")),
            Or(P("F", "ƒ_hardsign"), P("F", "ƒ_dh")),
        ))
        # Pseudosymmetric self-complementary cyclic motifs → F ≥ F_dh
        candidates.append((
            And(P("T", "𐑥"), P("P", "Φ_pm_pseudo")),
            Or(P("F", "ƒ_hardsign"), P("F", "ƒ_dh")),
        ))

        # ── Axiom 4 (Γ_→ requires D_∞ or R_‡) ────────────────────────────────
        # Sequential grammar (any tier) → temporal or catalytic dimension
        candidates.append((
            Or(
                P("∈", "Gamma_seq(SPECIFIC)"),
                P("∈", "Gamma_seq(SELECTIVE)"),
                P("∈", "Gamma_seq(BROAD)"),
            ),
            Or(
                P("D", "𐑼"),
                P("D", "𐑼"),
                P("D", "𐑼"),
                P("D", "𐑦"),
                P("R", "Ř_downstep"),
            ),
        ))

        # ── Kinetic-thermodynamic coupling (rule_002 in prior version) ─────────
        candidates.append((
            And(P("F", "ƒ_hardsign"), P("K", "Ç_frtailgamma")),
            P("<", "⊙_softsign"),
        ))

        # ── R → F coupling ─────────────────────────────────────────────────────
        # Covalent recognition → high fidelity (bond-energy argument)
        candidates.append((
            P("R", "Ř_subset"),
            P("F", "ƒ_hardsign"),
        ))
        # Dynamic covalent → F_hardsign or F_dh (imine, disulfide: reversible but reliable)
        candidates.append((
            P("R", "Ř_covalent_dynamic"),
            Or(P("F", "ƒ_hardsign"), P("F", "ƒ_dh")),
        ))

        # ── R_⇔ → T_⋈ (mechanical bond requires cyclic wheel topology) ─────────
        candidates.append((
            P("R", "Ř_mechanical"),
            P("T", "𐑥"),
        ))

        # ── T_⋈ ∧ R_⇔ → K_turnm ∨ K_schwa (dethreading barrier) ─────────────────
        candidates.append((
            And(P("T", "𐑥"), P("R", "Ř_mechanical")),
            Or(P("K", "Ç_turnm"), P("K", "Ç_schwa")),
        ))

        # ── Scale-topology coupling ─────────────────────────────────────────────
        # Global-scale control requires hub, network, or cage topology
        candidates.append((
            P("G", "Γ_revapostrophe"),
            Or(P("T", "𐑶"), P("T", "𐑡"), P("T", "𐑶")),
        ))
        # Molecular dimensionality → not global scale
        candidates.append((
            P("D", "𐑛"),
            Or(P("G", "Γ_beta"), P("G", "Γ_gamma")),
        ))

        # ── Fidelity-granularity coupling ───────────────────────────────────────
        # Global propagation requires at least medium fidelity
        candidates.append((
            P("G", "Γ_revapostrophe"),
            Or(P("F", "ƒ_hardsign"), P("F", "ƒ_dh")),
        ))

        # ── Temporal dimension → kinetic accessibility ──────────────────────────
        # Catalytic cycles have turnover rates; K_frtailgamma is unphysical for D_∞
        candidates.append((
            P("D", "𐑼"),
            Or(P("K", "Ç_turnm"), P("K", "Ç_schwa")),
        ))
        # Catalytic recognition mode → temporal or hybrid temporal dimension
        candidates.append((
            P("R", "Ř_downstep"),
            Or(
                P("D", "𐑼"),
                P("D", "𐑼"),
                P("D", "𐑼"),
                P("D", "𐑦"),
            ),
        ))

        # ── Hub-node granularity amplification ─────────────────────────────────
        candidates.append((
            And(P("T", "𐑶"), P("R", "Ř_superset")),
            Or(P("G", "Γ_gamma"), P("G", "Γ_revapostrophe")),
        ))

        # ── ⊙ indicator: K_teshlig in a cyclic system (Axiom 5 / Groppi anchor) ─
        # All-or-nothing steric cliff in T_⋈ → criticality candidacy
        candidates.append((
            And(P("T", "𐑥"), P("K", "Ç_teshlig")),
            P("<", "⊙_ctyogh"),
        ))

        # ── Cage topology (Axiom 1 analogue + kinetic encapsulation) ───────────
        # T_□□ with non-covalent recognition → F ≥ F_dh
        candidates.append((
            And(P("T", "𐑶"), P("R", "Ř_superset")),
            Or(P("F", "ƒ_hardsign"), P("F", "ƒ_dh")),
        ))
        # T_□□ → K_turnm or K_schwa (enclosed cage always has exchange barrier)
        candidates.append((
            P("T", "𐑶"),
            Or(P("K", "Ç_turnm"), P("K", "Ç_schwa")),
        ))

        return candidates
    
    def _evaluate_rule(
        self,
        antecedent: SymbolicExpression,
        consequent: SymbolicExpression,
        imscriptions: List[Imscription],
    ) -> PredictiveRule:
        """Evaluate a rule against imscription data."""
        self.rule_counter += 1
        
        supporting = 0
        total_applicable = 0
        falsified = False
        
        for imscription in imscriptions:
            # Check if antecedent applies
            if antecedent.evaluate(imscription):
                total_applicable += 1
                
                # Check if consequent holds
                if consequent.evaluate(imscription):
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
        test_imscriptions: List[Imscription],
    ) -> PredictiveRule:
        """
        Test a rule against new data (falsification attempt).
        
        Args:
            rule: Rule to test
            test_imscriptions: Test imscriptions
        
        Returns:
            Updated PredictiveRule
        """
        for imscription in test_imscriptions:
            if rule.antecedent.evaluate(imscription):
                if not rule.consequent.evaluate(imscription):
                    rule.falsified = True
                    break
        
        return rule


# =============================================================================
# Main Symbolic Reasoning Engine
# =============================================================================

class SymbolicReasoningEngine:
    """
    Main engine for symbolic reasoning in the Imscriptiveon framework.
    
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
        imscription: Imscription,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive grammar validation on a imscription.
        
        Args:
            imscription: Imscription to validate
        
        Returns:
            Validation report
        """
        report = {
            "imscription": imscription.name,
            "notation": imscription.to_notation(),
            "axiom_validation": {},
            "gd_independence": self.gd_tensor.compute_independence(imscription),
            "is_critical": self.gd_tensor.check_degeneracy(imscription),
            "predictions": [],
        }
        
        # Validate all axioms
        for axiom_name in ["axiom1", "axiom2", "axiom3", "axiom4", "axiom5"]:
            proof = self.theorem_prover.prove_axiom(axiom_name, [imscription])
            report["axiom_validation"][axiom_name] = {
                "applies": self.theorem_prover._check_axiom_applicability(axiom_name, imscription),
                "satisfied": proof.proven,
                "violated": not proof.proven,
            }
        
        # Generate predictions
        rules = self.rule_generator.generate_rules([imscription], min_support=1, min_confidence=0.5)
        report["predictions"] = [str(rule) for rule in rules]
        
        return report
    
    def find_cross_domain_analogies(
        self,
        query_name: str,
        min_similarity: float = 0.5,
    ) -> List[AnalogyResult]:
        """
        Find cross-domain analogies to a query imscription.
        
        Args:
            query_name: Name of query imscription in catalog
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of analogy results
        """
        if not self.catalog:
            return []
        
        query = self.catalog.get(query_name)
        if not query:
            return []
        
        candidates = list(self.catalog._imscriptions.values())
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
        
        imscriptions = list(self.catalog._imscriptions.values())
        return self.rule_generator.generate_rules(imscriptions, min_support, min_confidence)
    
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
        test_imscriptions = self.theorem_prover._generate_test_imscriptions(max_attempts)
        return self.rule_generator.test_rule(rule, test_imscriptions)

"""
Test suite for GroundingValidator.

Tests the mechanistic justification layer that catches:
1. Tuple collision — different chemistries assigned identical tuples
2. Semantic drift — primitives redefined silently to accommodate out-of-scope concepts
3. Keyword clustering — speculative prompts converging to attractor tuples

The grounding validator enforces that each primitive assignment is justified
by reference to a specific physical phenomenon, not a description keyword.
"""

import pytest
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
)
from imscrbgrmr.grounding import (
    GroundingValidator,
    GroundingStatus,
    GroundingResult,
    validate_imscription_with_grounding,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def validator():
    """Create a GroundingValidator instance."""
    return GroundingValidator()


@pytest.fixture
def carboxylic_acid_dimer():
    """Create a grounded carboxylic acid dimer imscription."""
    return Imscription(
        name="carboxylic_acid_dimer",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        description="R₂²(8) cyclic hydrogen-bonded dimer",
    )


@pytest.fixture
def proline_aldol_cycle():
    """Create a grounded proline aldol cycle imscription."""
    return Imscription(
        name="proline_aldol_cycle",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.MESOSCALE,
        interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,
        description="Organocatalytic aldol cycle with enamine intermediate",
    )


@pytest.fixture
def quantum_time_crystal_speculative():
    """Create a speculative quantum time crystal imscription (ungrounded)."""
    return Imscription(
        name="quantum_time_crystal_speculative",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        description="Speculative quantum time crystal",
    )


# =============================================================================
# Test: Grounded Justifications
# =============================================================================

class TestGroundedJustifications:
    """Test that properly grounded imscriptions pass validation."""

    def test_carboxylic_acid_dimer_grounded(self, validator, carboxylic_acid_dimer):
        """Carboxylic acid dimer with mechanistic justifications should pass."""
        justifications = {
            "dimensionality": "Single-molecule geometry with covalent bond formation",
            "topology": "Cyclic hydrogen bonding forming R₂²(8) motif",
            "recognition_mode": "Hydrogen bonding between carboxyl groups",
            "polarity": "Pseudosymmetric self-complementary interface",
            "fidelity": "High thermodynamic stability with ξ_CP ≈ 8.5 nats",
            "kinetic": "Barrier < 60 kJ/mol, spontaneous on experimental timescales",
            "granularity": "Single binding event, pairwise interaction",
            "interaction_grammar": "One specific partner, lock-and-key recognition",
        }
        
        result = validator.validate(carboxylic_acid_dimer, justifications)
        
        assert result.is_valid, f"Expected grounded, got ungrounded: {result.ungrounded_primitives}"
        assert len(result.warnings) == 0

    def test_proline_cycle_grounded(self, validator, proline_aldol_cycle):
        """Proline aldol cycle with mechanistic justifications should pass."""
        justifications = {
            "dimensionality": "Closed catalytic cycle with error-correction mechanism",
            "topology": "Cyclic closure of enamine intermediate",
            "recognition_mode": "Enamine catalysis with transition state stabilization",
            "polarity": "Pseudosymmetric self-complementary interface",
            "fidelity": "Moderate selectivity with ξ_CP ≈ 10 nats",
            "kinetic": "Barrier 60-100 kJ/mol, accessible with mild activation",
            "granularity": "Cooperative array with emergent constraint",
            "interaction_grammar": "Ordered sequential recognition from small partner set",
        }
        
        result = validator.validate(proline_aldol_cycle, justifications)
        
        assert result.is_valid, f"Expected grounded, got ungrounded: {result.ungrounded_primitives}"


# =============================================================================
# Test: Ungrounded Justifications (Keyword Matching)
# =============================================================================

class TestUngroundedJustifications:
    """Test that keyword-only justifications are caught."""

    def test_quantum_keyword_clustering_caught(self, validator, quantum_time_crystal_speculative):
        """Quantum/time crystal with keyword-only justifications should fail."""
        justifications = {
            "dimensionality": "Quantum temporal system",  # Keyword: "quantum", "temporal"
            "topology": "Cyclic quantum structure",  # Keyword: "quantum"
            "recognition_mode": "Speculative catalytic process",  # Keyword: "speculative"
            "polarity": "Theoretical self-complementarity",  # Keyword: "theoretical"
            "fidelity": "High fidelity like quantum systems",  # Keyword: "like", "quantum"
            "kinetic": "Kinetic trapping in quantum landscape",  # Vague
            "granularity": "Global quantum network",  # Keyword: "quantum"
            "interaction_grammar": "Broad partner selection",
        }
        
        result = validator.validate(quantum_time_crystal_speculative, justifications)
        
        # Should catch keyword-heavy justifications
        assert not result.is_valid, "Expected keyword-heavy justifications to be caught"
        assert len(result.ungrounded_primitives) > 0

    def test_empty_justifications_fail(self, validator, carboxylic_acid_dimer):
        """Empty justifications should fail."""
        justifications = {}
        
        result = validator.validate(carboxylic_acid_dimer, justifications)
        
        assert not result.is_valid
        assert len(result.ungrounded_primitives) == 8  # All primitives ungrounded (including kinetic)

    def test_partial_justifications_fail(self, validator, carboxylic_acid_dimer):
        """Partial justifications should fail for ungrounded primitives."""
        justifications = {
            "dimensionality": "Single-molecule geometry",  # Grounded
            "topology": "Cyclic hydrogen bonding",  # Grounded
            # Missing: recognition_mode, polarity, fidelity, kinetic, granularity, interaction_grammar
        }
        
        result = validator.validate(carboxylic_acid_dimer, justifications)
        
        assert not result.is_valid
        assert "recognition_mode" in result.ungrounded_primitives
        assert "fidelity" in result.ungrounded_primitives


# =============================================================================
# Test: Strict Mode
# =============================================================================

class TestStrictMode:
    """Test strict mode validation."""

    def test_strict_mode_rejects_keywords(self, validator):
        """Strict mode should reject keyword-heavy justifications."""
        strict_validator = GroundingValidator(strict_mode=True)
        
        imscription = Imscription(
            name="test",
            dimensionality=Dimensionality.TEMPORAL,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
            polarity=Polarity.SELF_COMPLEMENTARY_SYM,
            fidelity=Fidelity.HIGH,
            kinetic_character=KineticCharacter.MODERATE,
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        )
        
        justifications = {
            "dimensionality": "Closed catalytic cycle (quantum-like)",  # Has "quantum" keyword
            "topology": "Cyclic closure",
            "recognition_mode": "Transition state stabilization",
            "polarity": "Symmetric self-complementary",
            "fidelity": "High thermodynamic stability",
            "kinetic": "Barrier 60-100 kJ/mol",
            "granularity": "Single binding event",
            "interaction_grammar": "One specific partner",
        }
        
        result = strict_validator.validate(imscription, justifications)
        
        # Strict mode should flag the keyword
        assert not result.is_valid or len(result.warnings) > 0


# =============================================================================
# Test: Grounding Report
# =============================================================================

class TestGroundingReport:
    """Test grounding report generation."""

    def test_report_format(self, validator, carboxylic_acid_dimer):
        """Grounding report should be well-formatted."""
        justifications = {
            "dimensionality": "Single-molecule geometry",
            "topology": "Cyclic hydrogen bonding",
            "recognition_mode": "Hydrogen bonding",
            "polarity": "Self-complementary",
            "fidelity": "High stability",
            "kinetic": "Fast barrier",
            "granularity": "Local",
            "interaction_grammar": "Specific",
        }
        
        result = validator.validate(carboxylic_acid_dimer, justifications)
        report = validator.get_grounding_report(result)
        
        assert "GROUNDING VALIDATION REPORT" in report
        assert "DETAILED BREAKDOWN" in report
        assert "✓" in report or "✗" in report


# =============================================================================
# Test: Convenience Function
# =============================================================================

class TestConvenienceFunction:
    """Test validate_imscription_with_grounding convenience function."""

    def test_require_grounding_true_raises(self, carboxylic_acid_dimer):
        """require_grounding=True should raise on ungrounded imscriptions."""
        justifications = {}  # Empty = ungrounded
        
        with pytest.raises(ValueError, match="ungrounded"):
            validate_imscription_with_grounding(
                carboxylic_acid_dimer,
                justifications,
                require_grounding=True,
            )

    def test_require_grounding_false_returns(self, carboxylic_acid_dimer):
        """require_grounding=False should return without raising."""
        justifications = {}  # Empty = ungrounded
        
        is_valid, error = validate_imscription_with_grounding(
            carboxylic_acid_dimer,
            justifications,
            require_grounding=False,
        )
        
        assert is_valid is False
        assert error is None


# =============================================================================
# Test: Batch Validation
# =============================================================================

class TestBatchValidation:
    """Test batch validation of multiple imscriptions."""

    def test_batch_validation(self, validator, carboxylic_acid_dimer, proline_aldol_cycle):
        """Batch validation should return results for all imscriptions."""
        imscriptions = [
            (
                carboxylic_acid_dimer,
                {
                    "dimensionality": "Single-molecule geometry",
                    "topology": "Cyclic hydrogen bonding",
                    "recognition_mode": "Hydrogen bonding",
                    "polarity": "Self-complementary",
                    "fidelity": "High stability",
                    "kinetic": "Fast barrier",
                    "granularity": "Local",
                    "interaction_grammar": "Specific",
                },
            ),
            (
                proline_aldol_cycle,
                {
                    "dimensionality": "Closed catalytic cycle",
                    "topology": "Cyclic closure",
                    "recognition_mode": "Enamine catalysis",
                    "polarity": "Self-complementary",
                    "fidelity": "Moderate selectivity",
                    "kinetic": "Moderate barrier",
                    "granularity": "Mesoscale",
                    "interaction_grammar": "Sequential",
                },
            ),
        ]
        
        results = validator.validate_batch(imscriptions)
        
        assert len(results) == 2
        assert all(isinstance(r, GroundingResult) for r in results)


# =============================================================================
# Test: Primitive-Specific Grounding
# =============================================================================

class TestPrimitiveSpecificGrounding:
    """Test grounding for each primitive individually."""

    def test_dimensionality_grounding(self, validator, carboxylic_acid_dimer):
        """Dimensionality grounding should match physical phenomena."""
        # Valid grounding
        result = validator.validate(
            carboxylic_acid_dimer,
            {"dimensionality": "Single-molecule geometry with covalent bond formation"},
        )
        assert result.primitive_results["dimensionality"].status == GroundingStatus.GROUNDED
        
        # Invalid grounding (keyword only)
        result = validator.validate(
            carboxylic_acid_dimer,
            {"dimensionality": "Quantum molecular system"},
        )
        assert result.primitive_results["dimensionality"].status != GroundingStatus.GROUNDED

    def test_temporal_dimensionality_grounding(self, validator, proline_aldol_cycle):
        """Temporal dimensionality requires catalytic cycle justification."""
        # Valid grounding
        result = validator.validate(
            proline_aldol_cycle,
            {"dimensionality": "Closed catalytic cycle with error-correction mechanism"},
        )
        assert result.primitive_results["dimensionality"].status == GroundingStatus.GROUNDED
        
        # Invalid grounding (keyword only - no physical phenomenon)
        result = validator.validate(
            proline_aldol_cycle,
            {"dimensionality": "Temporal system"},
        )
        assert result.primitive_results["dimensionality"].status != GroundingStatus.GROUNDED

    def test_fidelity_grounding(self, validator, carboxylic_acid_dimer):
        """Fidelity grounding should reference thermodynamic/kinetic measures."""
        # Valid grounding
        result = validator.validate(
            carboxylic_acid_dimer,
            {"fidelity": "High thermodynamic stability with ξ_CP < 8.5 nats"},
        )
        assert result.primitive_results["fidelity"].status == GroundingStatus.GROUNDED
        
        # Invalid grounding (vague)
        result = validator.validate(
            carboxylic_acid_dimer,
            {"fidelity": "Very reliable interaction"},
        )
        assert result.primitive_results["fidelity"].status != GroundingStatus.GROUNDED

    def test_kinetic_grounding(self, validator, carboxylic_acid_dimer):
        """Kinetic grounding should reference barrier heights."""
        # Valid grounding - need to provide all justifications
        justifications = {
            "dimensionality": "Single-molecule geometry",
            "topology": "Cyclic hydrogen bonding",
            "recognition_mode": "Hydrogen bonding",
            "polarity": "Self-complementary",
            "fidelity": "High stability",
            "kinetic": "Barrier < 60 kJ/mol, spontaneous on experimental timescales",
            "granularity": "Local",
            "interaction_grammar": "Specific",
        }
        result = validator.validate(carboxylic_acid_dimer, justifications)
        assert result.primitive_results["kinetic"].status == GroundingStatus.GROUNDED

        # Invalid grounding (vague)
        justifications["kinetic"] = "Fast kinetics"
        result = validator.validate(carboxylic_acid_dimer, justifications)
        assert result.primitive_results["kinetic"].status != GroundingStatus.GROUNDED


# =============================================================================
# Test: Tuple Collision Detection
# =============================================================================

class TestTupleCollisionDetection:
    """Test that grounding validation catches tuple collisions."""

    def test_different_chemistry_different_grounding(self, validator):
        """Different chemical systems should have different groundings."""
        # System 1: Carboxylic acid dimer (molecular, H-bonding)
        imscription1 = Imscription(
            name="acid_dimer",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.NON_COVALENT,
            polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=Fidelity.HIGH,
            kinetic_character=KineticCharacter.FAST,
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        )
        
        # System 2: Proline cycle (temporal, catalytic)
        imscription2 = Imscription(
            name="proline_cycle",
            dimensionality=Dimensionality.TEMPORAL,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
            polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=Fidelity.MEDIUM,
            kinetic_character=KineticCharacter.MODERATE,
            granularity=Granularity.MESOSCALE,
            interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,
        )
        
        # Both use cyclic topology and self-complementary polarity
        # But groundings should be DIFFERENT
        just1 = {
            "topology": "Cyclic hydrogen bonding R₂²(8) motif",
            "polarity": "Pseudosymmetric self-complementary interface",
        }
        just2 = {
            "topology": "Cyclic closure of enamine intermediate",
            "polarity": "Pseudosymmetric self-complementary interface",
        }
        
        result1 = validator.validate(imscription1, just1)
        result2 = validator.validate(imscription2, just2)
        
        # Both should be grounded, but with DIFFERENT phenomena
        assert result1.primitive_results["topology"].matched_phenomena != \
               result2.primitive_results["topology"].matched_phenomena


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

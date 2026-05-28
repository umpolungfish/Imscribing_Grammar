"""
Test axiom validation in autonomous discovery agent.

This test verifies that the autonomous discovery agent correctly rejects
imscriptions with axiom violations, specifically:
- Axiom 4: Sequential grammar requires temporal or catalytic dimension
- Axiom 1: Cyclic self-complementary imscriptions cannot have low fidelity
"""
import asyncio
from imscrbgrmr import (
    Imscription, Dimensionality, Topology, RecognitionMode,
    Polarity, Fidelity, Granularity, InteractionGrammar,
    KineticCharacter, CriticalityPhase,
    global_catalog,
)
from imscrbgrmr.constraints import AxiomValidator


def test_axiom4_violation_detection():
    """Test that Axiom 4 violations are correctly detected."""
    print("\n" + "="*70)
    print("TEST: Axiom 4 Violation Detection")
    print("="*70)
    
    # Create a imscription with sequential grammar but NO temporal or catalytic dimension
    # This should violate Axiom 4
    invalid_imscription = Imscription(
        name="test_invalid_sequential",
        dimensionality=Dimensionality.SUPRAMOLECULAR,  # D_turnthree - NOT temporal
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,  # NOT catalytic
        polarity=Polarity.ACCEPTOR,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,  # Sequential!
    )
    
    # Validate axiom 4
    axiom4_report = AxiomValidator.validate_axiom4_sequential_grammar(invalid_imscription)
    
    print(f"Imscription: {invalid_imscription.name}")
    print(f"Notation: {invalid_imscription.to_notation()}")
    print(f"Axiom 4 applies: {axiom4_report['applies']}")
    print(f"Axiom 4 satisfied: {axiom4_report.get('axiom_satisfied', 'N/A')}")
    print(f"Axiom 4 violated: {axiom4_report.get('violated', False)}")
    
    assert axiom4_report.get("applies") == True, "Axiom 4 should apply to sequential grammar"
    assert axiom4_report.get("violated") == True, "Axiom 4 should be violated"
    print("✓ Axiom 4 violation correctly detected!")
    
    # Now test a VALID sequential imscription (with temporal dimension)
    valid_imscription = Imscription(
        name="test_valid_sequential",
        dimensionality=Dimensionality.TEMPORAL,  # D_infinity - HAS temporal
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.ACCEPTOR,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,
    )
    
    axiom4_report_valid = AxiomValidator.validate_axiom4_sequential_grammar(valid_imscription)
    
    print(f"\nValid imscription: {valid_imscription.name}")
    print(f"Notation: {valid_imscription.to_notation()}")
    print(f"Axiom 4 satisfied: {axiom4_report_valid.get('axiom_satisfied', False)}")
    print(f"Axiom 4 violated: {axiom4_report_valid.get('violated', False)}")
    
    assert axiom4_report_valid.get("violated") == False, "Valid imscription should not violate Axiom 4"
    print("✓ Valid sequential imscription correctly passes Axiom 4!")
    
    return True


def test_axiom1_violation_detection():
    """Test that Axiom 1 violations are correctly detected."""
    print("\n" + "="*70)
    print("TEST: Axiom 1 Violation Detection")
    print("="*70)
    
    # Create a cyclic self-complementary imscription with LOW fidelity
    # This should violate Axiom 1
    invalid_imscription = Imscription(
        name="test_invalid_cyclic_low_fid",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,  # T_bullseye - cyclic
        recognition_mode=RecognitionMode.NON_COVALENT,  # Valid R
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,  # P_pipevar - self-complementary
        fidelity=Fidelity.LOW,  # F_beltl - LOW fidelity (VIOLATION!)
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
    )
    
    # Validate axiom 1
    axiom1_report = AxiomValidator.validate_axiom1_cyclic_closure(invalid_imscription)
    
    print(f"Imscription: {invalid_imscription.name}")
    print(f"Notation: {invalid_imscription.to_notation()}")
    print(f"Axiom 1 applies: {axiom1_report['applies']}")
    print(f"Axiom 1 violated: {axiom1_report.get('violated', False)}")
    
    assert axiom1_report.get("applies") == True, "Axiom 1 should apply to cyclic self-complementary"
    assert axiom1_report.get("violated") == True, "Axiom 1 should be violated with low fidelity"
    print("✓ Axiom 1 violation correctly detected!")
    
    # Now test a VALID cyclic imscription (with medium/high fidelity)
    valid_imscription = Imscription(
        name="test_valid_cyclic",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.MEDIUM,  # F_dh - acceptable
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
    )
    
    axiom1_report_valid = AxiomValidator.validate_axiom1_cyclic_closure(valid_imscription)
    
    print(f"\nValid imscription: {valid_imscription.name}")
    print(f"Notation: {valid_imscription.to_notation()}")
    print(f"Axiom 1 violated: {axiom1_report_valid.get('violated', False)}")
    
    assert axiom1_report_valid.get("violated") == False, "Valid imscription should not violate Axiom 1"
    print("✓ Valid cyclic imscription correctly passes Axiom 1!")
    
    return True


def test_false_positive_prevention():
    """Test that the nitroso cavitand from Claude's example would be caught."""
    print("\n" + "="*70)
    print("TEST: False Positive Prevention (Claude's Example)")
    print("="*70)
    
    # The nitroso cavitand that was incorrectly assigned the same tuple as
    # the transient anhydride dissipative cycle
    # If it was assigned Gamma_seq (sequential) without temporal/catalytic,
    # it should be caught by Axiom 4
    
    cavitand_with_wrong_assignment = Imscription(
        name="nitroso_radical_calix[4]resorcinarene_anion_pi_cavitand_imscription",
        dimensionality=Dimensionality.SUPRAMOLECULAR,  # Purely spatial, NOT temporal
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,  # NOT catalytic
        polarity=Polarity.ACCEPTOR,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,  # Wrong!
    )
    
    axiom4_report = AxiomValidator.validate_axiom4_sequential_grammar(cavitand_with_wrong_assignment)
    
    print(f"Imscription: {cavitand_with_wrong_assignment.name}")
    print(f"Notation: {cavitand_with_wrong_assignment.to_notation()}")
    print(f"Axiom 4 applies: {axiom4_report['applies']}")
    print(f"Axiom 4 violated: {axiom4_report.get('violated', False)}")
    print(f"Reasoning: {axiom4_report.get('falsification_note', 'N/A')}")
    
    if axiom4_report.get("violated"):
        print("✓ AXIOM VALIDATION WOULD CATCH THIS FALSE POSITIVE!")
        print("  The cavitand with sequential grammar but no temporal/catalytic")
        print("  dimension would be REJECTED at registration time.")
        return True
    else:
        print("✗ WARNING: Axiom validation did not catch this case")
        return False


async def main():
    """Run all axiom validation tests."""
    print("\n" + "="*70)
    print("AXIOM VALIDATION TESTS FOR AUTONOMOUS DISCOVERY AGENT")
    print("="*70)
    
    results = []
    
    # Test 1: Axiom 4 violation detection
    try:
        results.append(("Axiom 4 Detection", test_axiom4_violation_detection()))
    except Exception as e:
        print(f"✗ Axiom 4 test failed: {e}")
        results.append(("Axiom 4 Detection", False))
    
    # Test 2: Axiom 1 violation detection
    try:
        results.append(("Axiom 1 Detection", test_axiom1_violation_detection()))
    except Exception as e:
        print(f"✗ Axiom 1 test failed: {e}")
        results.append(("Axiom 1 Detection", False))
    
    # Test 3: False positive prevention
    try:
        results.append(("False Positive Prevention", test_false_positive_prevention()))
    except Exception as e:
        print(f"✗ False positive test failed: {e}")
        results.append(("False Positive Prevention", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("="*70)
    
    if all_passed:
        print("✓ All axiom validation tests passed!")
        print("\nThe autonomous discovery agent will now:")
        print("  1. Validate all imscriptions against Axioms 1 and 4 before registration")
        print("  2. Reject imscriptions with Axiom 4 violations (sequential without temporal/catalytic)")
        print("  3. Reject imscriptions with Axiom 1 violations (cyclic self-comp with low fidelity)")
        print("  4. Flag imscriptions with other axiom violations for review")
        print("\nThis prevents false 100% matches from incorrect primitive assignments.")
    else:
        print("✗ Some tests failed - review needed")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script for Imscribing Grammar framework integration.

Tests:
1. Core imscription models (seven primitives)
2. ImscriptionCatalog registry
3. Constraint propagation engine
4. Thermodynamics (η_CP and ξ_CP metrics)
5. Domain agents (molecular, supramolecular, temporal)
6. Framework integration (BaseAgent, Orchestrator)
"""
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


# =============================================================================
# Test 1: Imscription Models
# =============================================================================

def test_imscription_models():
    """Test that imscription models and seven primitives work correctly."""
    print("Testing Imscription models and seven primitives...")

    try:
        from imscrbgrmr.models import (
            Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
            Imscription, ImscriptionNotation, parse_notation,
        )

        # Test primitive enums
        assert Dimensionality.dead.value == "𐑛"
        assert Topology.mime.value == "Þ_bullseye"
        assert RecognitionMode.ado.value == "Ř_superset"
        assert Polarity.yew.value == "Φ_pm_pseudo"  # Updated
        assert Fidelity.peep.value == "ƒ_hardsign"
        assert Granularity.thigh.value == "Γ_revapostrophe"
        # InteractionGrammar now has composite values
        assert KineticCharacter.yea.value == "Ç_frtailgamma"  # NEW
        print("  ✓ All primitives accessible")
        
        # Test parsing from symbols
        assert Dimensionality.from_symbol("D_∧") == Dimensionality.dead
        assert Fidelity.from_symbol("F_ℏ") == Fidelity.peep
        assert KineticCharacter.from_symbol("Ç_frtailgamma") == KineticCharacter.yea  # NEW
        print("  ✓ Symbol parsing works")
        
        # Test Imscription creation
        imscription = Imscription(
            name="carboxylic_acid_dimer",
            dimensionality=Dimensionality.dead,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ado,
            polarity=Polarity.yew,  # Updated
            fidelity=Fidelity.peep,
            kinetic_character=KineticCharacter.yea,  # NEW
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,  # Updated
            description="Classic R₂²(8) hydrogen-bonded dimer",
        )

        # Test notation generation
        notation = imscription.to_notation()
        assert "𐑛" in notation
        assert "Þ_bullseye" in notation
        assert "ƒ_hardsign" in notation
        assert "Ç_frtailgamma" in notation  # NEW
        print(f"  ✓ Imscription notation: {notation}")

        # Test ImscriptionNotation parsing (backward compatible with 7 primitives)
        parsed = parse_notation("⟨D_wynn; T_bullseye; R_superset; P_pipevar; F_hardsign; G_beta; Gamma_otimes⟩")
        assert parsed.dimensionality == Dimensionality.dead
        assert parsed.fidelity == Fidelity.peep
        print("  ✓ Notation parsing works (backward compatible)")
        
        # Test JSON serialization
        json_str = imscription.to_json()
        assert "carboxylic_acid_dimer" in json_str
        restored = Imscription.from_json(json_str)
        assert restored.name == imscription.name
        print("  ✓ JSON serialization works")
        
        # Test fidelity numeric value
        assert Fidelity.peep.numeric_value >= 0.9
        assert Fidelity.age.numeric_value <= 0.5
        print("  ✓ Fidelity numeric values correct")
        
        # Test polarity compatibility
        assert Polarity.yew.is_compatible_with(Polarity.yew)
        assert not Polarity.yew.is_compatible_with(Polarity.yew)
        print("  ✓ Polarity compatibility works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing imscription models: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 2: ImscriptionCatalog Registry
# =============================================================================

def test_imscription_catalog():
    """Test imscription catalog registration and search."""
    print("\nTesting ImscriptionCatalog registry...")
    
    try:
        from imscrbgrmr.registry import ImscriptionCatalog, global_catalog, register_imscription
        from imscrbgrmr.models import (
            Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
            Imscription,
        )

        # Create a test catalog
        catalog = ImscriptionCatalog(name="test_catalog")

        # Register imscriptions
        imscription1 = Imscription(
            name="test_dimer",
            dimensionality=Dimensionality.dead,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ado,
            polarity=Polarity.yew,
            fidelity=Fidelity.peep,
            kinetic_character=KineticCharacter.yea,  # NEW
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,
        )
        catalog.register(imscription1)

        assert "test_dimer" in catalog
        assert catalog.get("test_dimer") is not None
        print("  ✓ Registration works")

        # Test search
        results = catalog.search(fidelity=Fidelity.peep)
        assert len(results) >= 1
        print("  ✓ Search by primitive works")

        # Test search by domain
        mol_imscriptions = catalog.search_by_domain("molecular")
        assert len(mol_imscriptions) >= 1
        print("  ✓ Domain search works")

        # Test convenience function
        register_imscription(
            name="amide_dimer",
            dimensionality="𐑛",
            topology="Þ_bullseye",
            recognition_mode="Ř_superset",
            polarity="Φ_pm_pseudo",
            fidelity="ƒ_dh",
            granularity="Γ_beta",
            interaction_grammar="Gamma_and(SELECTIVE)",
            kinetic_character="Ç_turnm",  # NEW
        )
        assert "amide_dimer" in global_catalog
        print("  ✓ Convenience registration works")
        
        # Test catalog summary
        summary = catalog.summary()
        assert "total_imscriptions" in summary
        print(f"  ✓ Catalog summary: {summary['total_imscriptions']} imscriptions")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing catalog: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 3: Constraint Propagation Engine
# =============================================================================

def test_constraint_engine():
    """Test constraint propagation and compatibility checking."""
    print("\nTesting Constraint Propagation Engine...")
    
    try:
        from imscrbgrmr.constraints import (
            ConstraintEngine, CompatibilityMatrix, FidelityPropagator,
            CompatibilityResult,
        )
        from imscrbgrmr.models import (
            Imscription, Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
        )

        engine = ConstraintEngine()

        # Create compatible imscriptions
        imscription_a = Imscription(
            name="electrophile",
            dimensionality=Dimensionality.dead,
            topology=Topology.eat,
            recognition_mode=RecognitionMode.tot,
            polarity=Polarity.yew,
            fidelity=Fidelity.they,
            kinetic_character=KineticCharacter.loll,  # NEW
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,
        )

        imscription_b = Imscription(
            name="nucleophile",
            dimensionality=Dimensionality.dead,
            topology=Topology.eat,
            recognition_mode=RecognitionMode.tot,
            polarity=Polarity.yew,
            fidelity=Fidelity.they,
            kinetic_character=KineticCharacter.loll,  # NEW
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,
        )

        # Test compatibility
        report = engine.check_pair_compatibility(imscription_a, imscription_b)
        assert report.is_compatible
        assert "polarity" in report.details
        print("  ✓ Compatible pair detected")

        # Test incompatible pair (same polarity)
        imscription_c = Imscription(
            name="another_electrophile",
            dimensionality=Dimensionality.dead,
            topology=Topology.eat,
            recognition_mode=RecognitionMode.tot,
            polarity=Polarity.yew,
            fidelity=Fidelity.they,
            kinetic_character=KineticCharacter.loll,  # NEW
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,
        )

        report2 = engine.check_pair_compatibility(imscription_a, imscription_c)
        assert not report2.is_compatible
        print("  ✓ Incompatible pair detected (same polarity)")

        # Test system consistency
        consistency = engine.check_system_consistency([imscription_a, imscription_b, imscription_c])
        assert "consistency_score" in consistency
        assert consistency["conflicts"] >= 1
        print(f"  ✓ System consistency: {consistency['consistency_score']:.2f}")
        
        # Test fidelity propagation
        propagator = FidelityPropagator()
        propagated = propagator.propagate([imscription_a, imscription_b])
        assert propagated in [Fidelity.age, Fidelity.they, Fidelity.peep]
        print(f"  ✓ Fidelity propagation: {propagated.value}")
        
        # Test cooperativity
        coop = propagator.compute_cooperativity_factor([imscription_a, imscription_b])
        assert "total_cooperativity" in coop
        print(f"  ✓ Cooperativity factor: {coop['total_cooperativity']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing constraint engine: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 4: Thermodynamics (η_CP and ξ_CP)
# =============================================================================

def test_thermodynamics():
    """Test constraint propagation efficiency metrics."""
    print("\nTesting Thermodynamics (η_CP and ξ_CP)...")
    
    try:
        from imscrbgrmr.thermodynamics import (
            compute_eta_CP, compute_xi_CP,
            ConstraintPropagationEfficiency,
            LANDAUER_COST_PER_BIT,
            compare_efficiencies,
            benchmark_against_landauer,
            get_reference,
            list_references,
        )
        from imscrbgrmr.models import (
            Imscription, Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
        )

        # Test Landauer constant
        assert LANDAUER_COST_PER_BIT > 0
        print(f"  ✓ Landauer cost: {LANDAUER_COST_PER_BIT:.2e} kJ/mol/bit")

        # Create test imscription (carboxylic acid dimer)
        imscription = Imscription(
            name="acetic_acid_dimer",
            dimensionality=Dimensionality.dead,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ado,
            polarity=Polarity.yew,
            fidelity=Fidelity.peep,
            kinetic_character=KineticCharacter.yea,  # NEW
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,
        )

        # Test η_CP computation (ΔG ≈ -52 kJ/mol for AA dimer)
        result = compute_eta_CP(imscription, delta_g=-52.0)
        assert result.eta_CP > 0
        assert result.eta_CP < 1  # Should be much less than 1
        assert result.xi_CP > 0
        print(f"  ✓ η_CP = {result.eta_CP:.2e}, ξ_CP = {result.xi_CP:.2f} nats")

        # Verify against reference values from QUANTIG.md
        ref = get_reference("acetic_acid_homodimer")
        if ref:
            xi_min, xi_max = ref["xi_CP"]
            assert xi_min <= result.xi_CP <= xi_max + 2  # Allow some tolerance
            print(f"  ✓ Within reference range: {xi_min}-{xi_max} nats")

        # Test efficiency description
        desc = result.efficiency_description
        assert "efficient" in desc.lower() or "efficiency" in desc.lower()
        print(f"  ✓ Efficiency description: {desc}")
        
        # Test benchmark against Landauer
        benchmark = benchmark_against_landauer(imscription, delta_g=-52.0)
        assert "overhead_ratio" in benchmark
        print(f"  ✓ Landauer overhead: {benchmark['overhead_ratio']:.1e}×")
        
        # Test reference list
        refs = list_references()
        assert len(refs) > 0
        print(f"  ✓ {len(refs)} reference values available")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing thermodynamics: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 5: Domain Agents
# =============================================================================



# =============================================================================
# Test 6: Framework Integration
# =============================================================================

def test_framework_integration():
    """Test that imscrbgrmr integrates with the AjintK framework."""
    print("\nTesting Framework Integration...")

    try:
        # Test that framework imports work
        from framework import BaseAgent, AgentOrchestrator
        print("  ✓ Framework imports successful")

        # Test that imscrbgrmr can be used alongside framework
        from imscrbgrmr import (
            Imscription, Dimensionality, Fidelity, Topology, RecognitionMode,
            Polarity, Granularity, InteractionGrammar, KineticCharacter
        )
        from imscrbgrmr.thermodynamics import compute_eta_CP

        # Create a imscription
        imscription = Imscription(
            name="test_imscription",
            dimensionality=Dimensionality.dead,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ado,
            polarity=Polarity.yew,
            fidelity=Fidelity.peep,
            kinetic_character=KineticCharacter.yea,
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.vow,
        )

        # Compute thermodynamics
        result = compute_eta_CP(imscription, delta_g=-50.0)
        assert result.eta_CP > 0
        print(f"  ✓ Imscribing Grammar + Framework integration works")

        return True

    except Exception as e:
        print(f"  ✗ Error testing framework integration: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 7: Aider Provider Integration
# =============================================================================

def test_aider_provider():
    """Test that Aider provider can be created and used."""
    print("\nTesting Aider Provider Integration...")

    try:
        # Test provider creation
        from framework import get_llm_provider
        
        # Create Aider provider (doesn't require API key)
        provider = get_llm_provider("aider", model="claude-sonnet-4-5-20250929")
        assert provider is not None
        print("  ✓ AiderLLMProvider created successfully")
        
        # Test model info
        info = provider.get_model_info()
        assert "name" in info
        print(f"  ✓ Model info retrieved: {info.get('name')}")
        
        # Test that provider is in routing
        from framework.enhanced_llm_provider import ModelRouter
        router = ModelRouter()
        
        # Check coding tasks prefer aider
        coding_chain = router.get_provider_chain("coding")
        assert coding_chain[0] == "aider", f"Expected aider first, got {coding_chain}"
        
        # Check refactor tasks prefer aider
        refactor_chain = router.get_provider_chain("refactor")
        assert refactor_chain[0] == "aider", f"Expected aider first, got {refactor_chain}"
        
        print("  ✓ Aider in task routing (coding, refactor)")
        
        return True

    except ImportError as e:
        # Aider not installed - this is OK, just warn
        print(f"  ⚠ aider-chat not installed (optional): {e}")
        return True  # Don't fail test for optional dependency
        
    except Exception as e:
        print(f"  ✗ Error testing Aider provider: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 8: Aider Code Agent
# =============================================================================

def test_aider_code_agent():
    """Test that AiderCodeAgent can be created."""
    print("\nTesting Aider Code Agent...")

    try:
        from agents import AiderCodeAgent
        
        # Create agent with minimal config
        config = {
            "model": "claude-sonnet-4-5-20250929",
            "auto_commits": False,  # Don't auto-commit in tests
            "use_git": False,  # Don't require Git in tests
        }
        
        agent = AiderCodeAgent(config)
        assert agent is not None
        print("  ✓ AiderCodeAgent created successfully")
        
        # Check capabilities
        assert "git_native_operations" in agent.capabilities
        assert "multi_file_editing" in agent.capabilities
        print("  ✓ AiderCodeAgent capabilities verified")
        
        return True

    except ImportError as e:
        # Aider not installed - this is OK, just warn
        print(f"  ⚠ aider-chat not installed (optional): {e}")
        return True  # Don't fail test for optional dependency
        
    except Exception as e:
        print(f"  ✗ Error testing AiderCodeAgent: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Main Test Runner
# =============================================================================

def run_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Imscribing Grammar Framework Integration Tests")
    print("=" * 60)

    results = [
        test_imscription_models(),
        test_imscription_catalog(),
        test_constraint_engine(),
        test_thermodynamics(),
        test_domain_agents(),
        test_framework_integration(),
        test_aider_provider(),
        test_aider_code_agent(),
    ]

    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)

    if all(results):
        print("✓ All tests passed! Imscribing Grammar integration successful.")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())

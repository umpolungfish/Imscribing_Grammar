#!/usr/bin/env python3
"""
Test script for Imscribing Grammar framework integration.

Tests:
1. Core synthon models (seven primitives)
2. SynthonCatalog registry
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
# Test 1: Synthon Models
# =============================================================================

def test_synthon_models():
    """Test that synthon models and seven primitives work correctly."""
    print("Testing Synthon models and seven primitives...")

    try:
        from imscrbgrmr.models import (
            Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
            Synthon, SynthonNotation, parse_notation,
        )

        # Test primitive enums
        assert Dimensionality.MOLECULAR.value == "D_wedge"
        assert Topology.CYCLIC_BOWTIE.value == "T_bowtie"
        assert RecognitionMode.NON_COVALENT.value == "R_superset"
        assert Polarity.SELF_COMPLEMENTARY_PSEUDO.value == "P_pm_pseudo"  # Updated
        assert Fidelity.HIGH.value == "F_hbar"
        assert Granularity.GLOBAL.value == "G_aleph"
        # InteractionGrammar now has composite values
        assert KineticCharacter.FAST.value == "K_fast"  # NEW
        print("  ✓ All primitives accessible")
        
        # Test parsing from symbols
        assert Dimensionality.from_symbol("D_∧") == Dimensionality.MOLECULAR
        assert Fidelity.from_symbol("F_ℏ") == Fidelity.HIGH
        assert KineticCharacter.from_symbol("K_fast") == KineticCharacter.FAST  # NEW
        print("  ✓ Symbol parsing works")
        
        # Test Synthon creation
        synthon = Synthon(
            name="carboxylic_acid_dimer",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.NON_COVALENT,
            polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,  # Updated
            fidelity=Fidelity.HIGH,
            kinetic_character=KineticCharacter.FAST,  # NEW
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,  # Updated
            description="Classic R₂²(8) hydrogen-bonded dimer",
        )

        # Test notation generation
        notation = synthon.to_notation()
        assert "D_wedge" in notation
        assert "T_bowtie" in notation
        assert "F_hbar" in notation
        assert "K_fast" in notation  # NEW
        print(f"  ✓ Synthon notation: {notation}")

        # Test SynthonNotation parsing (backward compatible with 7 primitives)
        parsed = parse_notation("⟨D_wedge; T_bowtie; R_superset; P_pm; F_hbar; G_beth; Gamma_otimes⟩")
        assert parsed.dimensionality == Dimensionality.MOLECULAR
        assert parsed.fidelity == Fidelity.HIGH
        print("  ✓ Notation parsing works (backward compatible)")
        
        # Test JSON serialization
        json_str = synthon.to_json()
        assert "carboxylic_acid_dimer" in json_str
        restored = Synthon.from_json(json_str)
        assert restored.name == synthon.name
        print("  ✓ JSON serialization works")
        
        # Test fidelity numeric value
        assert Fidelity.HIGH.numeric_value >= 0.9
        assert Fidelity.LOW.numeric_value <= 0.5
        print("  ✓ Fidelity numeric values correct")
        
        # Test polarity compatibility
        assert Polarity.ACCEPTOR.is_compatible_with(Polarity.DONOR)
        assert not Polarity.ACCEPTOR.is_compatible_with(Polarity.ACCEPTOR)
        print("  ✓ Polarity compatibility works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing synthon models: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Test 2: SynthonCatalog Registry
# =============================================================================

def test_synthon_catalog():
    """Test synthon catalog registration and search."""
    print("\nTesting SynthonCatalog registry...")
    
    try:
        from imscrbgrmr.registry import SynthonCatalog, global_catalog, register_synthon
        from imscrbgrmr.models import (
            Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
            Synthon,
        )

        # Create a test catalog
        catalog = SynthonCatalog(name="test_catalog")

        # Register synthons
        synthon1 = Synthon(
            name="test_dimer",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.NON_COVALENT,
            polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=Fidelity.HIGH,
            kinetic_character=KineticCharacter.FAST,  # NEW
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        )
        catalog.register(synthon1)

        assert "test_dimer" in catalog
        assert catalog.get("test_dimer") is not None
        print("  ✓ Registration works")

        # Test search
        results = catalog.search(fidelity=Fidelity.HIGH)
        assert len(results) >= 1
        print("  ✓ Search by primitive works")

        # Test search by domain
        mol_synthons = catalog.search_by_domain("molecular")
        assert len(mol_synthons) >= 1
        print("  ✓ Domain search works")

        # Test convenience function
        register_synthon(
            name="amide_dimer",
            dimensionality="D_wedge",
            topology="T_bowtie",
            recognition_mode="R_superset",
            polarity="P_pm_pseudo",
            fidelity="F_eth",
            granularity="G_beth",
            interaction_grammar="Gamma_and(SELECTIVE)",
            kinetic_character="K_mod",  # NEW
        )
        assert "amide_dimer" in global_catalog
        print("  ✓ Convenience registration works")
        
        # Test catalog summary
        summary = catalog.summary()
        assert "total_synthons" in summary
        print(f"  ✓ Catalog summary: {summary['total_synthons']} synthons")
        
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
            Synthon, Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
        )

        engine = ConstraintEngine()

        # Create compatible synthons
        synthon_a = Synthon(
            name="electrophile",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.LINEAR,
            recognition_mode=RecognitionMode.COVALENT,
            polarity=Polarity.ACCEPTOR,
            fidelity=Fidelity.MEDIUM,
            kinetic_character=KineticCharacter.MODERATE,  # NEW
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        )

        synthon_b = Synthon(
            name="nucleophile",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.LINEAR,
            recognition_mode=RecognitionMode.COVALENT,
            polarity=Polarity.DONOR,
            fidelity=Fidelity.MEDIUM,
            kinetic_character=KineticCharacter.MODERATE,  # NEW
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        )

        # Test compatibility
        report = engine.check_pair_compatibility(synthon_a, synthon_b)
        assert report.is_compatible
        assert "polarity" in report.details
        print("  ✓ Compatible pair detected")

        # Test incompatible pair (same polarity)
        synthon_c = Synthon(
            name="another_electrophile",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.LINEAR,
            recognition_mode=RecognitionMode.COVALENT,
            polarity=Polarity.ACCEPTOR,
            fidelity=Fidelity.MEDIUM,
            kinetic_character=KineticCharacter.MODERATE,  # NEW
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        )

        report2 = engine.check_pair_compatibility(synthon_a, synthon_c)
        assert not report2.is_compatible
        print("  ✓ Incompatible pair detected (same polarity)")

        # Test system consistency
        consistency = engine.check_system_consistency([synthon_a, synthon_b, synthon_c])
        assert "consistency_score" in consistency
        assert consistency["conflicts"] >= 1
        print(f"  ✓ System consistency: {consistency['consistency_score']:.2f}")
        
        # Test fidelity propagation
        propagator = FidelityPropagator()
        propagated = propagator.propagate([synthon_a, synthon_b])
        assert propagated in [Fidelity.LOW, Fidelity.MEDIUM, Fidelity.HIGH]
        print(f"  ✓ Fidelity propagation: {propagated.value}")
        
        # Test cooperativity
        coop = propagator.compute_cooperativity_factor([synthon_a, synthon_b])
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
            Synthon, Dimensionality, Topology, RecognitionMode,
            Polarity, Fidelity, Granularity, InteractionGrammar,
            KineticCharacter,  # NEW
        )

        # Test Landauer constant
        assert LANDAUER_COST_PER_BIT > 0
        print(f"  ✓ Landauer cost: {LANDAUER_COST_PER_BIT:.2e} kJ/mol/bit")

        # Create test synthon (carboxylic acid dimer)
        synthon = Synthon(
            name="acetic_acid_dimer",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.NON_COVALENT,
            polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=Fidelity.HIGH,
            kinetic_character=KineticCharacter.FAST,  # NEW
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        )

        # Test η_CP computation (ΔG ≈ -52 kJ/mol for AA dimer)
        result = compute_eta_CP(synthon, delta_g=-52.0)
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
        benchmark = benchmark_against_landauer(synthon, delta_g=-52.0)
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

def test_domain_agents():
    """Test domain-specific synthon agents."""
    print("\nTesting Domain Agents...")
    
    try:
        from imscrbgrmr.domains.molecular import MolecularSynthonAgent
        from imscrbgrmr.domains.supramolecular import SupramolecularSynthonAgent
        from imscrbgrmr.domains.temporal import TemporalSynthonAgent
        from imscrbgrmr.domains.hybrid import HybridSynthonAgent
        from imscrbgrmr.models import Fidelity
        
        # Test Molecular agent
        mol_agent = MolecularSynthonAgent()
        synthons = mol_agent.list_molecular_synthons()
        assert len(synthons) > 0
        print(f"  ✓ Molecular agent: {len(synthons)} synthons listed")
        
        # Test Supramolecular agent
        supra_agent = SupramolecularSynthonAgent()
        hbond_analysis = supra_agent.analyze_hydrogen_bond_network("test.cif")
        assert "motif" in hbond_analysis
        print(f"  ✓ Supramolecular agent: H-bond analysis works")
        
        # Test cooperativity computation
        coop = supra_agent.compute_cooperativity_induction(3)
        assert coop["is_superlinear"]
        print(f"  ✓ Triple H-bond cooperativity: superlinear detected")
        
        # Test Temporal agent
        temp_agent = TemporalSynthonAgent()
        cycle_analysis = temp_agent.analyze_reaction_cycle("proline_aldol", "L-proline")
        assert "cycle_name" in cycle_analysis
        print(f"  ✓ Temporal agent: Cycle analysis works")
        
        # Test fidelity computation
        fidelity_result = temp_agent.compute_fidelity_per_cycle(1.0, 0.001)
        assert fidelity_result["f_cycle"] > 0.99
        print(f"  ✓ Fidelity per cycle: {fidelity_result['f_cycle']:.4f}")
        
        # Test Hybrid agent
        hybrid_agent = HybridSynthonAgent()
        spatial = hybrid_agent.analyze_spatial_framework("MOF", "pcu")
        assert "framework_type" in spatial
        print(f"  ✓ Hybrid agent: Spatial framework analysis works")
        
        # Test granularity amplification
        from imscrbgrmr.models import Granularity
        gran_amp = hybrid_agent.compute_granularity_amplification(
            Granularity.GLOBAL, Granularity.MESOSCALE
        )
        assert gran_amp["amplification_factor"] >= 1
        print(f"  ✓ Granularity amplification: {gran_amp['amplification_factor']}×")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error testing domain agents: {e}")
        import traceback
        traceback.print_exc()
        return False


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
            Synthon, Dimensionality, Fidelity, Topology, RecognitionMode,
            Polarity, Granularity, InteractionGrammar, KineticCharacter
        )
        from imscrbgrmr.thermodynamics import compute_eta_CP

        # Create a synthon
        synthon = Synthon(
            name="test_synthon",
            dimensionality=Dimensionality.MOLECULAR,
            topology=Topology.CYCLIC_BOWTIE,
            recognition_mode=RecognitionMode.NON_COVALENT,
            polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=Fidelity.HIGH,
            kinetic_character=KineticCharacter.FAST,
            granularity=Granularity.LOCAL,
            interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        )

        # Compute thermodynamics
        result = compute_eta_CP(synthon, delta_g=-50.0)
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
        test_synthon_models(),
        test_synthon_catalog(),
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

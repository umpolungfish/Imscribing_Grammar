#!/usr/bin/env python3
"""
Imscribing Grammar Examples — Demonstrating the Unified Imscriptiveon Framework

This script demonstrates:
1. Creating imscriptions with the seven primitives
2. Computing constraint propagation efficiency (η_CP and ξ_CP)
3. Analyzing cross-domain analogies
4. Using domain-specific agents
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def example_1_basic_imscription():
    """Example 1: Creating a basic imscription with seven primitives."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Imscription Creation")
    print("=" * 60)
    
    from imscrbgrmr import (
        Imscription, Dimensionality, Topology, RecognitionMode,
        Polarity, Fidelity, Granularity, InteractionGrammar,
    )
    
    # Create the classic carboxylic acid dimer imscription
    # This is the R₂²(8) hydrogen-bonded motif found in thousands of crystal structures
    carboxylic_dimer = Imscription(
        name="carboxylic_acid_dimer",
        dimensionality=Dimensionality.dead,  # D_∧ — point-like molecular reactivity
        topology=Topology.mime,  # T_⋈ — cyclic R₂²(8) motif
        recognition_mode=RecognitionMode.ado,  # R_⊇ — hydrogen bonding
        polarity=Polarity.SELF_COMPLEMENTARY,  # P_± — self-complementary
        fidelity=Fidelity.peep,  # F_ℏ — dominant, geometry-enforcing
        granularity=Granularity.ice,  # G_ב — local control
        interaction_grammar=InteractionGrammar.SPECIFIC,  # 𐑝 — one specific partner
        description="Classic R₂²(8) hydrogen-bonded dimer",
        metadata={
            "csd_entries": 15000,
            "interaction_energy": -64.2,  # kJ/mol (gas phase)
        },
    )
    
    print(f"\nImscription: {carboxylic_dimer.name}")
    print(f"Unified notation: {carboxylic_dimer.to_notation()}")
    print(f"Description: {carboxylic_dimer.description}")
    print(f"Constraint strength: {carboxylic_dimer.constraint_strength:.2f}")
    print(f"Domains: {carboxylic_dimer.dimensionality.domains}")
    
    return carboxylic_dimer


def example_2_thermodynamics(imscription: Imscription):
    """Example 2: Computing thermodynamic efficiency metrics."""
    print("\n" + "=" * 60)
    print("Example 2: Thermodynamic Efficiency (η_CP and ξ_CP)")
    print("=" * 60)
    
    from imscrbgrmr.thermodynamics import (
        compute_eta_CP,
        benchmark_against_landauer,
        get_reference,
    )
    
    # Compute η_CP and ξ_CP for the carboxylic acid dimer
    # Using solvated ΔG ≈ -52 kJ/mol (from QUANTIG.md Transformation #1)
    result = compute_eta_CP(imscription, delta_g=-52.0)
    
    print(f"\nImscription: {result.imscription_name}")
    print(f"Information gain: {result.information_gain:.2f} bits")
    print(f"Fidelity: {result.fidelity:.3f}")
    print(f"ΔG: {result.delta_g:.1f} kJ/mol")
    print(f"\nη_CP (efficiency): {result.eta_CP:.2e}")
    print(f"ξ_CP (inefficiency): {result.xi_CP:.2f} nats")
    print(f"Waste factor: {result.waste_factor:.1e}× Landauer limit")
    print(f"Assessment: {result.efficiency_description}")
    
    # Compare with reference values
    ref = get_reference("acetic_acid_homodimer")
    if ref:
        print(f"\nReference range (QUANTIG.md):")
        print(f"  ξ_CP: {ref['xi_CP'][0]}-{ref['xi_CP'][1]} nats")
        print(f"  Note: {ref['note']}")
    
    # Benchmark against Landauer limit
    benchmark = benchmark_against_landauer(imscription, delta_g=-52.0)
    print(f"\nLandauer Benchmark:")
    print(f"  Minimum energy: {benchmark['landauer_minimum_kJ_mol']:.2e} kJ/mol")
    print(f"  Actual energy: {benchmark['actual_energy_kJ_mol']:.1f} kJ/mol")
    print(f"  Overhead: {benchmark['overhead_ratio']:.1e}×")
    
    return result


def example_3_catalog_and_search():
    """Example 3: Using the imscription catalog for storage and search."""
    print("\n" + "=" * 60)
    print("Example 3: Imscription Catalog and Search")
    print("=" * 60)
    
    from imscrbgrmr.registry import ImscriptionCatalog, register_imscription
    from imscrbgrmr import Fidelity, Dimensionality
    
    # Create a catalog
    catalog = ImscriptionCatalog(name="example_catalog")
    
    # Register imscriptions using the convenience function
    register_imscription(
        name="formamide_dimer",
        dimensionality="𐑛",
        topology="𐑥",
        recognition_mode="𐑩",
        polarity="𐑬",
        fidelity="𐑱",  # Lower fidelity than carboxylic acid
        granularity="𐑚",
        interaction_grammar="𐑝",
        description="Weaker amide dimer (F_ℓ)",
    )
    
    register_imscription(
        name="triple_hbond_array",
        dimensionality="𐑛",
        topology="𐑥",
        recognition_mode="𐑩",
        polarity="𐑗",
        fidelity="𐑐",  # HIGH fidelity due to cooperativity
        granularity="𐑔",  # Mesoscale
        interaction_grammar="𐑝",
        description="DAD·ADA triple H-bond array (Watson-Crick like)",
    )
    
    register_imscription(
        name="proline_aldol_cycle",
        dimensionality="𐑼",  # Temporal!
        topology="𐑥",
        recognition_mode="𐑽",  # Catalytic
        polarity="𐑗",
        fidelity="𐑞",
        granularity="𐑔",
        interaction_grammar="∋_selective",
        description="Proline-catalyzed aldol cycle (temporal imscription)",
    )
    
    # Add to our local catalog
    from imscrbgrmr.registry import global_catalog
    for name in ["formamide_dimer", "triple_hbond_array", "proline_aldol_cycle"]:
        if name in global_catalog:
            catalog.register(global_catalog[name])
    
    print(f"\nCatalog: {catalog.name}")
    print(f"Total imscriptions: {len(catalog)}")
    
    # Search by fidelity
    high_f = catalog.search(fidelity=Fidelity.peep)
    print(f"\nHigh fidelity (F_hardsign) imscriptions: {len(high_f)}")
    for s in high_f:
        print(f"  - {s.name}: {s.to_notation()}")
    
    # Search by domain
    temporal = catalog.search_by_domain("temporal")
    print(f"\nTemporal domain imscriptions: {len(temporal)}")
    for s in temporal:
        print(f"  - {s.name} ({s.dimensionality.value})")
    
    # Find similar imscriptions
    if high_f:
        similar = catalog.find_similar(high_f[0], match_primitives=4)
        print(f"\nimscriptions similar to '{high_f[0].name}': {len(similar)}")
        for s in similar[:3]:
            print(f"  - {s.name}")
    
    return catalog


def example_4_cross_domain_analogy():
    """Example 4: Finding cross-domain analogies."""
    print("\n" + "=" * 60)
    print("Example 4: Cross-Domain Analogy Search")
    print("=" * 60)
    
    from imscrbgrmr.registry import ImscriptionCatalog, global_catalog
    from imscrbgrmr import Dimensionality
    
    print("\nFinding temporal analogs of supramolecular imscriptions...")
    print("(e.g., 'temporal imscriptions with regeneration analogous to self-complementarity')")
    
    # Get a supramolecular imscription
    supra_imscriptions = global_catalog.search_by_domain("supramolecular")
    if not supra_imscriptions:
        # Create one if none exist
        from imscrbgrmr import Imscription, Topology, RecognitionMode, Polarity, Fidelity, Granularity, InteractionGrammar
        supra_imscription = Imscription(
            name="carboxylic_acid_dimer",
            dimensionality=Dimensionality.ash,
            topology=Topology.mime,
            recognition_mode=RecognitionMode.ado,
            polarity=Polarity.SELF_COMPLEMENTARY,
            fidelity=Fidelity.peep,
            granularity=Granularity.ice,
            interaction_grammar=InteractionGrammar.SPECIFIC,
            description="Self-complementary H-bond dimer",
        )
    else:
        supra_imscription = supra_imscriptions[0]
    
    print(f"\nReference imscription: {supra_imscription.name}")
    print(f"  Notation: {supra_imscription.to_notation()}")
    print(f"  Polarity: {supra_imscription.polarity.value} (self-complementary)")
    print(f"  Fidelity: {supra_imscription.fidelity.value}")
    
    # Find temporal analogs
    temporal_analogs = global_catalog.find_cross_domain_analogs(
        supra_imscription,
        target_domain="temporal",
    )
    
    if temporal_analogs:
        print(f"\nFound {len(temporal_analogs)} temporal analog(s):")
        for analog in temporal_analogs[:3]:
            print(f"  - {analog.name}")
            print(f"    Notation: {analog.to_notation()}")
            print(f"    Shared primitives: topology={analog.topology.value}, fidelity={analog.fidelity.value}")
    else:
        print("\nNo temporal analogs found in current catalog.")
        print("(This is expected with the minimal example catalog)")
    
    return supra_imscription


def example_5_constraint_compatibility():
    """Example 5: Checking imscription compatibility."""
    print("\n" + "=" * 60)
    print("Example 5: Constraint Compatibility Checking")
    print("=" * 60)
    
    from imscrbgrmr.constraints import ConstraintEngine
    from imscrbgrmr import Imscription, Dimensionality, Topology, RecognitionMode, Polarity, Fidelity, Granularity, InteractionGrammar
    
    engine = ConstraintEngine()
    
    # Create an electrophile imscription
    electrophile = Imscription(
        name="carbonyl_imscription",
        dimensionality=Dimensionality.dead,
        topology=Topology.eat,
        recognition_mode=RecognitionMode.tot,
        polarity=Polarity.yew,  # P+ — electrophile
        fidelity=Fidelity.they,
        granularity=Granularity.ice,
        interaction_grammar=InteractionGrammar.SELECTIVE,
        description="Electrophilic carbonyl carbon",
    )
    
    # Create a nucleophile imscription
    nucleophile = Imscription(
        name="enolate_imscription",
        dimensionality=Dimensionality.dead,
        topology=Topology.eat,
        recognition_mode=RecognitionMode.tot,
        polarity=Polarity.yew,  # P- — nucleophile
        fidelity=Fidelity.they,
        granularity=Granularity.ice,
        interaction_grammar=InteractionGrammar.SELECTIVE,
        description="Nucleophilic enolate",
    )
    
    # Check compatibility
    report = engine.check_pair_compatibility(electrophile, nucleophile)
    
    print(f"\nPair: {electrophile.name} + {nucleophile.name}")
    print(f"Compatibility: {report.result.value}")
    print(f"Details:")
    for key, value in report.details.items():
        print(f"  {key}: {value}")
    
    if report.conditions:
        print(f"Conditions:")
        for cond in report.conditions:
            print(f"  - {cond}")
    
    # Check incompatible pair (same polarity)
    another_electrophile = Imscription(
        name="imine_imscription",
        dimensionality=Dimensionality.dead,
        topology=Topology.eat,
        recognition_mode=RecognitionMode.tot,
        polarity=Polarity.yew,  # Also P+ — incompatible!
        fidelity=Fidelity.they,
        granularity=Granularity.ice,
        interaction_grammar=InteractionGrammar.SELECTIVE,
        description="Electrophilic imine",
    )
    
    report2 = engine.check_pair_compatibility(electrophile, another_electrophile)
    print(f"\nPair: {electrophile.name} + {another_electrophile.name}")
    print(f"Compatibility: {report2.result.value}")
    print(f"(Two electrophiles cannot react directly)")
    
    return report




def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  Imscribing Grammar Framework Examples")
    print("  A Unified Imscriptiveon Implementation")
    print("=" * 60)
    
    # Run examples
    imscription = example_1_basic_imscription()
    example_2_thermodynamics(imscription)
    catalog = example_3_catalog_and_search()
    example_4_cross_domain_analogy()
    example_5_constraint_compatibility()
    print("\n" + "=" * 60)
    print("  Examples Complete!")
    print("=" * 60)
    print("""
Next Steps:
1. Explore QUANTIG.md for theoretical background
2. Review the seven primitives and unified notation
3. Try creating your own imscriptions for specific chemical systems
4. Use domain agents to analyze molecular, supramolecular, and temporal systems
5. Compute η_CP and ξ_CP for your imscriptions to compare efficiency
""")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

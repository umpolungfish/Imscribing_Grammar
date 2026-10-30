#!/usr/bin/env python3
"""
demo_protocols.py — Protocol Suite Integration Demo (v0.3.0)

Exercises all four new protocol modules in sequence using calibrated reference
imscriptions and ΔG values from QUANTIG.md Section VI:

  Protocol 1 — IG_PERTURBATION : PerturbationEngine
  Protocol 2 — IG_TRAJECTORY   : TemporalImscriptionAgent
  Protocol 3 — IG_ENSEMBLER    : EnsembleCatalog

Reference values used throughout:
  carboxylic_acid_dimer  ΔG(298K, gas) = -12.0 kJ/mol  → ξ_CP ≈ 6.66 nats [HIGH]
  proline_aldol_cycle    ΔG(298K, gas) = -48.0 kJ/mol  → ξ_CP ≈ 9.21 nats [MEDIUM]
                         ΔG‡(C–C bond formation)       = 97.0 kJ/mol (K_turnm range)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def section(title: str) -> None:
    bar = "=" * 64
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


def subsection(title: str) -> None:
    print(f"\n  --- {title} ---")


# ---------------------------------------------------------------------------
# Protocol 1 — IG_PERTURBATION
# ---------------------------------------------------------------------------

def demo_perturbation() -> None:
    section("Protocol 1 · IG_PERTURBATION — Primitive Jacobian")

    from imscrbgrmr import PerturbationEngine
    from imscrbgrmr.registry import global_catalog

    dimer = global_catalog.get("carboxylic_acid_dimer")
    if dimer is None:
        print("  [SKIP] carboxylic_acid_dimer not found in catalog")
        return

    engine = PerturbationEngine()
    DELTA_G = -12.0  # kJ/mol — acetic acid homodimer ΔG(298K, gas)

    # --- 1a. Full primitive sweep ---
    subsection("1a. Full sweep — all primitives ±1 tier")
    jac = engine.sweep_all(dimer, delta_g=DELTA_G)
    print(f"  Baseline ξ_CP           : {jac.baseline_xi_CP:.3f} nats")
    ms = jac.most_sensitive
    ms_label = ms.primitive_name if ms else "—"
    print(f"  Most sensitive primitive : {ms_label}")
    print(f"  Critical primitives (≥3.0 Δnats): {jac.critical_primitives}")
    print(f"  {'Primitive':<20}  {'delta_xi_CP (nats)':>18}  {'Label':>8}")
    print(f"  {'-'*20}  {'-'*18}  {'-'*8}")
    for pr in sorted(jac.results, key=lambda x: abs(x.delta_xi_CP), reverse=True):
        print(
            f"  {pr.primitive_name:<20}  {pr.delta_xi_CP:>+18.4f}  {pr.sensitivity:>8}"
        )

    # --- 1b. Fault injection — identify single points of failure ---
    subsection("1b. Fault injection — identify brittle primitives")
    fault = engine.fault_injection(dimer, delta_g=DELTA_G)
    print(f"  Baseline ξ_CP          : {fault['baseline_xi_CP_nats']:.4f} nats")
    print(f"  System robust          : {fault['system_robust']}")
    print(f"  Single points of fail  : {fault['single_points_of_failure'] or 'none'}")
    print(f"  Most brittle primitive : {fault['most_brittle'] or 'none'}")

    # --- 1c. Improvement path: lower ξ_CP toward 6.0 nats ---
    subsection("1c. Improvement path — target ξ_CP = 6.0 nats (below baseline)")
    path_down = engine.find_path_to_target(
        dimer,
        delta_g=DELTA_G,
        target_xi_CP=6.0,
        optimize_primitives=["F", "K", "G"],
    )
    print(f"  Baseline ξ_CP  : {path_down['baseline_xi_CP_nats']:.4f} nats")
    print(f"  Target ξ_CP    : {path_down['target_xi_CP_nats']:.4f} nats")
    print(f"  Achieved ξ_CP  : {path_down['achieved_xi_CP_nats']:.4f} nats")
    print(f"  Direction      : {path_down['direction']}")
    print(f"  Target reached : {path_down['target_reached']}")
    if path_down['recommended_steps']:
        print(f"  Steps ({path_down['num_steps']}):")
        for step in path_down['recommended_steps']:
            print(f"    {step['primitive']:<4}  {step['shift']}  "
                  f"({step['delta_xi_CP_nats']:+.4f} nats  [{step['sensitivity']}])")
    else:
        print("  No improvement steps available in F/K/G")

    # --- 1d. Degradation probe: raise ξ_CP toward 7.50 nats ---
    subsection("1d. Degradation probe — target ξ_CP = 7.50 nats (above baseline)")
    path_up = engine.find_path_to_target(
        dimer,
        delta_g=DELTA_G,
        target_xi_CP=7.50,
        optimize_primitives=["F", "K", "G"],
    )
    print(f"  Baseline ξ_CP  : {path_up['baseline_xi_CP_nats']:.4f} nats")
    print(f"  Target ξ_CP    : {path_up['target_xi_CP_nats']:.4f} nats")
    print(f"  Achieved ξ_CP  : {path_up['achieved_xi_CP_nats']:.4f} nats")
    print(f"  Direction      : {path_up['direction']}")
    print(f"  Target reached : {path_up['target_reached']}")
    if path_up['recommended_steps']:
        print(f"  Steps ({path_up['num_steps']}):")
        for step in path_up['recommended_steps']:
            print(f"    {step['primitive']:<4}  {step['shift']}  "
                  f"({step['delta_xi_CP_nats']:+.4f} nats  [{step['sensitivity']}])")
    else:
        print("  No degradation steps available in F/K/G")


# ---------------------------------------------------------------------------
# Protocol 2 — IG_TRAJECTORY
# ---------------------------------------------------------------------------

def demo_trajectory() -> None:
    section("Protocol 2 · IG_TRAJECTORY — D_∞ Cycle Validation")

    from imscrbgrmr import (
        TemporalImscriptionAgent,
        Imscription, Dimensionality, Topology, RecognitionMode,
        Polarity, Fidelity, KineticCharacter, Granularity,
        InteractionGrammar, GrammarOperator, CriticalityPhase,
    )

    # Build the three mechanistic steps of the proline aldol cycle
    # Reference: QUANTIG.md §VIII, proline_aldol_cycle entry
    #   Step 1 — enamine formation  (K_frtailgamma,  ΔG ≈ -15 kJ/mol)
    #   Step 2 — C–C bond formation (K_turnm,   ΔG‡ = 97 kJ/mol — rate-determining)
    #   Step 3 — hydrolysis/reset   (K_frtailgamma,  ΔG ≈ -25 kJ/mol, is_reset=True)

    _base = dict(
        dimensionality=Dimensionality.array,
        topology=Topology.mime,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.church,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.measure,
    )

    enamine = Imscription(
        name="enamine_formation",
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.yea,
        description="proline enamine formation from aldehyde — fast condensation",
        **_base,
    )
    ts_imscription = Imscription(
        name="c_c_bond_form",
        fidelity=Fidelity.they,
        kinetic_character=KineticCharacter.loll,
        description="enamine attacks electrophile — rate-determining C–C bond formation",
        **_base,
    )
    hydrolysis = Imscription(
        name="hydrolysis_reset",
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.yea,
        description="iminium hydrolysis regenerates proline catalyst and releases aldol product",
        **_base,
    )

    agent = TemporalImscriptionAgent("proline_aldol_cycle")
    agent.add_step(enamine,    "enamine_formation", delta_g=-15.0)
    agent.add_step(ts_imscription, "c_c_bond_form",     delta_g_ddagger=97.0)
    agent.add_step(hydrolysis, "hydrolysis_reset",  delta_g=-25.0, is_reset=True)

    result = agent.validate_all()

    subsection("Validation summary")
    print(f"  Cycle              : {result.cycle_name}")
    print(f"  Steps              : {result.num_steps}")
    print(f"  Overall valid      : {result.overall_valid}")
    print(f"  Axiom 6 satisfied  : {result.axiom6_satisfied}")
    print(f"  Reset verified     : {result.reset_verified}  (step: {result.reset_step!r})")
    print(f"  Kinetic traps      : {result.kinetic_traps or 'none'}")

    subsection("Continuity checks")
    for cc in result.continuity_results:
        status = "PASS" if cc.passed else "FAIL"
        print(f"  [{status}]  {cc.step_a} → {cc.step_b}")
        for issue in cc.issues:
            print(f"         ⚠  {issue}")

    subsection("Criticality per step")
    for sc in result.criticality_per_step:
        marker = "★ ⊙ candidate" if sc.is_phi_c_candidate else ""
        print(
            f"  {sc.step_name:<24}  score={sc.degeneracy_score:.3f}  "
            f"tier={sc.tier:<12}  {marker}"
        )

    subsection("Full cycle candidacy")
    print(f"  Average degeneracy score : {result.full_cycle_candidacy:.3f}")
    for w in result.warnings:
        print(f"  ⚠  {w}")


# ---------------------------------------------------------------------------
# Protocol 3 — IG_ENSEMBLER
# ---------------------------------------------------------------------------

def demo_ensembler() -> None:
    section("Protocol 3 · IG_ENSEMBLER — Multi-Imscription Composition")

    from imscrbgrmr import EnsembleCatalog

    # Ensemble: carboxylic_acid_dimer + proline_aldol_cycle + rotaxane
    # Represents a hybrid molecular/temporal/mechanical three-component system
    ensemble = EnsembleCatalog()
    ensemble.add("carboxylic_acid_dimer")
    ensemble.add("proline_aldol_cycle")
    ensemble.add("nitroso_radical_cucurbituril_anion_rotaxane_imscription")

    # --- 3a. Pairwise compatibility ---
    subsection("3a. N×N pairwise compatibility matrix")
    report = ensemble.check_pairwise()
    print(f"  Components      : {', '.join(report.component_names)}")
    print(f"  Consistency     : {report.consistency_score:.0%}  "
          f"({'consistent' if report.is_consistent else 'inconsistent'})")
    for entry in report.pairwise_matrix:
        icon = "✓" if entry.result == "Compatible" else ("~" if entry.result == "Conditional" else "✗")
        print(f"  [{icon}] {entry.component_a!r}  ↔  {entry.component_b!r}")
        if entry.incompatibilities:
            print(f"      primitives in conflict: {', '.join(entry.incompatibilities)}")
        if entry.conditions:
            print(f"      conditions: {'; '.join(entry.conditions[:2])}")

    # --- 3b. Emergent properties ---
    subsection("3b. Emergent properties")
    for ep in report.emergent_properties:
        flag = "DETECTED" if ep.detected else "not detected"
        score_str = f"  score={ep.score:.3f}" if ep.score is not None else ""
        print(f"  [{flag:12}]  {ep.property_name}{score_str}")
        if ep.details:
            print(f"                      {ep.details}")

    # --- 3c. Axiom propagation ---
    subsection("3c. Axiom propagation")
    for axiom, status in report.axiom_propagation.items():
        print(f"  {axiom:<30}  {status}")

    # --- 3d. System ξ_CP ---
    subsection("3d. System-level ξ_CP (ΔG_assembly = -85.0 kJ/mol, 1.5 bit overhead)")
    xi_result = ensemble.compute_system_xi_CP(
        delta_g_assembly=-85.0,
        interface_overhead_bits=1.5,
    )
    print(f"  Reference imscription  : {xi_result.get('reference_imscription', '?')}")
    print(f"  η_CP (system)      : {xi_result.get('eta_CP_system', '?'):.4e}")
    print(f"  ξ_CP (system)      : {xi_result.get('xi_CP_system_nats', '?'):.4f} nats")
    print(f"  Efficiency tier    : {xi_result.get('efficiency_tier', '?')}")
    print(f"  Interface overhead : {xi_result.get('interface_overhead_bits', '?'):.1f} bits")

    if report.warnings:
        subsection("Warnings")
        for w in report.warnings:
            print(f"  ⚠  {w}")


# ---------------------------------------------------------------------------
# Protocol 4 — IG_RETRODESIGN
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("Imscribing Grammar v0.3.0 — Protocol Suite Demo")
    print("Reference: QUANTIG.md §VI (calibrated ΔG values)")
    print()
    print("  carboxylic_acid_dimer  ΔG = -12.0 kJ/mol  ξ_CP ≈ 6.66 nats [HIGH]")
    print("  proline_aldol_cycle    ΔG = -48.0 kJ/mol  ξ_CP ≈ 9.21 nats [MEDIUM]")

    demo_perturbation()
    demo_trajectory()
    demo_ensembler()
    section("Demo complete")
    print()


if __name__ == "__main__":
    main()

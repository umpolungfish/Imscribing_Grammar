"""
Cross-Domain Imscription Demo — Phase 1 Validation

Runs the three cross-domain imscriptions (tide pool, supply chain, drone swarm)
through the full Imscribing Grammar analysis stack and reports:

  1. Axiom validation — which axioms fire, which are satisfied
  2. Thermodynamic analysis — ξ_CP baseline (with analogue ΔG values)
  3. Perturbation Jacobian — most sensitive primitive
  4. Ensemble check — pairwise compatibility across domains
  5. Cross-domain analogies — catalog matches from chemistry entries
  6. Extensions flagged — Phase 2 work required per entry

Usage::

    python examples/demo_cross_domain.py
"""
from __future__ import annotations

import json

from imscrbgrmr.cross_domain import register_cross_domain_imscriptions
from imscrbgrmr import global_catalog
from imscrbgrmr.constraints import AxiomValidator
from imscrbgrmr.thermodynamics import compute_eta_CP
from imscrbgrmr.perturbation import PerturbationEngine
from imscrbgrmr.ensembler import EnsembleCatalog
from imscrbgrmr.varma_probe import degeneracy_strength

SECTION = "=" * 68
SUB = "-" * 50

# ---------------------------------------------------------------------------
# Analogue ΔG values (representative energy scales per domain)
# ---------------------------------------------------------------------------
ANALOGUE_DELTA_G = {
    "tide_pool_ecological":  -8.0,   # ~metabolic free energy turnover, kJ/mol equivalent
    "global_supply_chain":   -15.0,  # ~logistical potential (arbitrary energy unit)
    "autonomous_drone_swarm": -5.0,  # ~communication/consensus energy cost per cycle
}


def main():
    print(f"\n{SECTION}")
    print("  CROSS-DOMAIN imscription DEMO — Phase 1 Validation")
    print(f"{SECTION}\n")

    # -----------------------------------------------------------------------
    # Registration
    # -----------------------------------------------------------------------
    print("Registering cross-domain imscriptions...")
    newly_registered = register_cross_domain_imscriptions()
    cross_domain_names = [
        "tide_pool_ecological",
        "global_supply_chain",
        "autonomous_drone_swarm",
    ]
    for name in cross_domain_names:
        s = global_catalog.get(name)
        status = "NEW" if name in newly_registered else "already registered"
        print(f"  ✓ {name} [{status}]")
        print(f"    Notation: {s.to_notation()}")

    # -----------------------------------------------------------------------
    # Per-imscription analysis
    # -----------------------------------------------------------------------
    engine = PerturbationEngine()

    for name in cross_domain_names:
        s = global_catalog.get(name)
        delta_g = ANALOGUE_DELTA_G[name]

        print(f"\n{SECTION}")
        print(f"  {name.upper().replace('_', ' ')}")
        print(f"{SECTION}")
        print(f"  Description : {s.description[:90]}...")
        print(f"  Notation    : {s.to_notation()}")
        print(f"  Domain      : {s.metadata.get('domain_category', 'unknown')}")
        print(f"  Phase 2 ext : {len(s.metadata.get('extensions_required', []))} flagged")

        # 1. Axiom validation
        print(f"\n  {SUB}")
        print("  1. AXIOM VALIDATION")
        print(f"  {SUB}")
        report = AxiomValidator.validate_all_axioms(s)
        all_ok = report.get("all_satisfied", False)
        violations = report.get("violations", 0)
        print(f"  All satisfied : {all_ok}")
        print(f"  Violations    : {violations}")
        if violations > 0:
            for axiom_key, result in report.get("detailed_results", {}).items():
                if isinstance(result, dict) and result.get("violated"):
                    note = result.get("falsification_note", "")
                    print(f"  ⚠  {axiom_key}: {note}")
        # Show grounding extension notes from metadata
        for ext in s.metadata.get("extensions_required", []):
            print(f"  ↳ Phase 2 needed: {ext.split(' — ')[0]}")

        # 2. Thermodynamics
        print(f"\n  {SUB}")
        print("  2. THERMODYNAMIC ANALYSIS")
        print(f"  {SUB}")
        try:
            thermo = compute_eta_CP(s, delta_g)
            print(f"  Analogue ΔG   : {delta_g} kJ/mol")
            print(f"  η_CP          : {thermo.eta_CP:.4f}")
            print(f"  ξ_CP          : {thermo.xi_CP:.4f} nats")
            print(f"  Efficiency    : {thermo.efficiency_description}")
        except Exception as e:
            print(f"  ERROR: {e}")

        # 3. Perturbation Jacobian
        print(f"\n  {SUB}")
        print("  3. PERTURBATION JACOBIAN (top 3 sensitivities)")
        print(f"  {SUB}")
        try:
            jacobian = engine.sweep_all(s, delta_g)
            print(f"  Baseline ξ_CP : {jacobian.baseline_xi_CP:.4f} nats")
            for r in jacobian.results[:3]:
                print(
                    f"  {r.primitive} ({r.primitive_name:<20}): "
                    f"Δξ = {r.delta_xi_CP:+.4f} nats  [{r.sensitivity}]"
                )
            ms = jacobian.most_sensitive
            if ms:
                print(f"  Most sensitive: {ms.primitive} ({ms.primitive_name})")
        except Exception as e:
            print(f"  ERROR: {e}")

        # 4. Varma probe (⊙ candidacy)
        print(f"\n  {SUB}")
        print("  4. VARMA PROBE (⊙ candidacy)")
        print(f"  {SUB}")
        try:
            score, tier = degeneracy_strength(s)
            print(f"  Degeneracy score : {score:.4f}")
            print(f"  Tier             : {tier}")
            print(f"  ⊙ candidate    : {'YES' if score >= 0.70 else 'approaching' if score >= 0.35 else 'no'}")
            if name == "autonomous_drone_swarm":
                print(f"  Note: ⊙ assigned in tuple; Vicsek transition is empirical evidence.")
        except Exception as e:
            print(f"  ERROR: {e}")

        # 5. Cross-domain analogies (CLI: imscribe analogies <name>)
        print(f"\n  {SUB}")
        print("  5. CROSS-DOMAIN ANALOGIES")
        print(f"  {SUB}")
        chem_analogs = s.metadata.get("cross_domain_analog", {})
        if chem_analogs:
            for domain, analog_name in chem_analogs.items():
                print(f"  [{domain}] {analog_name}")
        else:
            print("  See metadata.cross_domain_analog or run: imscribe analogies " + name)

        # 6. Phase 2 extensions required
        print(f"\n  {SUB}")
        print("  6. PHASE 2 EXTENSIONS REQUIRED")
        print(f"  {SUB}")
        for ext in s.metadata.get("extensions_required", []):
            key, _, desc = ext.partition(" — ")
            print(f"  [{key}]")
            if desc:
                print(f"    {desc}")

    # -----------------------------------------------------------------------
    # Cross-domain ensemble check
    # -----------------------------------------------------------------------
    print(f"\n{SECTION}")
    print("  CROSS-DOMAIN ENSEMBLE CHECK")
    print(f"  (tide pool × supply chain × drone swarm)")
    print(f"{SECTION}")
    try:
        ensemble = EnsembleCatalog()
        for name in cross_domain_names:
            ensemble.add(name)
        report = ensemble.check_pairwise()

        print(f"  Consistency score : {report.consistency_score:.3f}")
        print(f"  Is consistent     : {report.is_consistent}")
        print()
        for entry in report.pairwise_matrix:
            print(f"  {entry.component_a:<35} ↔  {entry.component_b:<35} → {entry.result}")
            if entry.incompatibilities:
                for inc in entry.incompatibilities[:2]:
                    print(f"    ⚠  {inc}")

        print()
        for ep in report.emergent_properties:
            marker = "✓" if ep.detected else "·"
            print(f"  {marker} Emergent: {ep.property_name}")
            if ep.detected:
                print(f"      {ep.details}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print(f"\n{SECTION}")
    print("  PHASE 1 SUMMARY")
    print(f"{SECTION}")
    print()
    rows = []
    for name in cross_domain_names:
        s = global_catalog.get(name)
        delta_g = ANALOGUE_DELTA_G[name]
        try:
            thermo = compute_eta_CP(s, delta_g)
            xi = f"{thermo.xi_CP:.3f}"
        except Exception:
            xi = "N/A"
        n_ext = len(s.metadata.get("extensions_required", []))
        rows.append((name, s.metadata.get("domain_category", "?"), xi, n_ext))

    print(f"  {'Imscription':<35} {'Domain':<14} {'ξ_CP (nats)':<14} {'Phase2 ext'}")
    print(f"  {'-'*35} {'-'*14} {'-'*14} {'-'*10}")
    for r in rows:
        print(f"  {r[0]:<35} {r[1]:<14} {r[2]:<14} {r[3]}")

    print()
    print("  Phase 2 extensions required across all three entries:")
    all_exts = set()
    for name in cross_domain_names:
        s = global_catalog.get(name)
        for ext in s.metadata.get("extensions_required", []):
            all_exts.add(ext.split(" — ")[0])
    for ext in sorted(all_exts):
        print(f"    · {ext}")

    print()
    print("  See IG_CROSS_DOMAIN.md for full Phase 2 specification.")
    print(f"\n{SECTION}")
    print("  Demo complete")
    print(f"{SECTION}\n")


if __name__ == "__main__":
    main()

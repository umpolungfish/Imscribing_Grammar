"""
assignment_tests.py — Algorithmic Assignment Project: Tests and Catalog Consistency Check

Runs three test suites:

  1. Unit tests — known systems with measured ΔG / ΔG‡, verify assignment
     matches expected tier and (where both methods are available) that
     methods agree.

  2. Catalog consistency check — run F/K assignment from ξ_CP/ΔG data on
     all catalog imscriptions that have quantitative entries; compare to hand-
     coded values; report agreement rate and boundary cases.

  3. Decomposition self-consistency — for two well-characterised imscriptions,
     decompose to atoms, re-assign atoms from independent measurements,
     reconstruct, and check round-trip fidelity.

The output is the primary evidence for or against the natural-joints hypothesis.
"""

import sys
import math
sys.path.insert(0, "/home/mrnob0dy666/Imscribing Grammar")

from imscrbgrmr.assignment import (
    PrimitiveAssignmentEngine,
    check_catalog_consistency,
    check_decomposition_consistency,
)
from imscrbgrmr.models import Fidelity, KineticCharacter, Granularity, CriticalityPhase

# ── Helpers ──────────────────────────────────────────────────────────────────

def HDR(title):
    w = 70
    print(f"\n{'═'*w}")
    print(f"  {title}")
    print(f"{'═'*w}")

def sub(title):
    print(f"\n  {'─'*64}")
    print(f"  {title}")
    print(f"  {'─'*64}")

def PASS(msg): print(f"    ✓  {msg}")
def FAIL(msg): print(f"    ✗  {msg}")
def NOTE(msg): print(f"    ·  {msg}")

engine = PrimitiveAssignmentEngine()
n_pass = 0
n_fail = 0

def check(condition, pass_msg, fail_msg):
    global n_pass, n_fail
    if condition:
        PASS(pass_msg)
        n_pass += 1
    else:
        FAIL(fail_msg)
        n_fail += 1


# ══════════════════════════════════════════════════════════════════════════════
# SUITE 1 — Unit Tests: Known Systems
# ══════════════════════════════════════════════════════════════════════════════

HDR("SUITE 1 — Unit Tests: Known Systems with Measured ΔG / ΔG‡")

# ── F assignment from ΔG ─────────────────────────────────────────────────────

sub("1a. Fidelity from ΔG (P-21 integer Boltzmann ratio thresholds)")

# RT at 298.15 K = 2.479 kJ/mol
RT = 8.314e-3 * 298.15
hi_thresh = -RT * math.log(19)  # ≈ −7.30 kJ/mol
me_thresh = -RT * math.log(3)   # ≈ −2.72 kJ/mol

print(f"\n  P-21 thresholds at 298.15 K:")
print(f"    F_HIGH boundary : ΔG ≤ {hi_thresh:.3f} kJ/mol  (ratio ≥ 19 → ln19 = {math.log(19):.4f})")
print(f"    F_MED  boundary : ΔG ≤ {me_thresh:.3f} kJ/mol  (ratio ≥  3 → ln3  = {math.log(3):.4f})")

# CB[7]-adamantane: ΔG ≈ −72 kJ/mol (Kim 2001) → F_HIGH
r = engine.assign_F_from_delta_g(-72.0)
check(r.value == Fidelity.HIGH, f"CB[7]/adamantane ΔG=−72 → F_HIGH (ratio={math.exp(72/RT):.0f})", f"Expected HIGH, got {r.value}")
NOTE(r.evidence)

# Acetic acid dimer: ΔG ≈ −13.5 kJ/mol → F_HIGH
r = engine.assign_F_from_delta_g(-13.5)
check(r.value == Fidelity.HIGH, f"AcOH dimer ΔG=−13.5 → F_HIGH (ratio={math.exp(13.5/RT):.1f})", f"Expected HIGH, got {r.value}")
NOTE(r.evidence)

# Exactly at the HIGH/MED boundary (−7.30 kJ/mol) — should be boundary case
r = engine.assign_F_from_delta_g(hi_thresh)
check(r.is_boundary, f"ΔG = {hi_thresh:.2f} kJ/mol (exact HIGH/MED boundary) → is_boundary=True", "Expected boundary flag")
NOTE(f"Assigned: {r.value.name}, margin={r.boundary_margin:.3f} kJ/mol")

# Mid-range MEDIUM: ΔG ≈ −5.0 kJ/mol
r = engine.assign_F_from_delta_g(-5.0)
check(r.value == Fidelity.MEDIUM, f"ΔG=−5.0 → F_MEDIUM", f"Expected MEDIUM, got {r.value}")
NOTE(r.evidence)

# F_LOW: ΔG = −1.0 kJ/mol
r = engine.assign_F_from_delta_g(-1.0)
check(r.value == Fidelity.LOW, f"ΔG=−1.0 → F_LOW", f"Expected LOW, got {r.value}")
NOTE(r.evidence)

# Slight positive ΔG — still LOW
r = engine.assign_F_from_delta_g(+0.5)
check(r.value == Fidelity.LOW, f"ΔG=+0.5 (unfavorable) → F_LOW", f"Expected LOW, got {r.value}")

# ── F from ξ_CP ──────────────────────────────────────────────────────────────

sub("1b. Fidelity from ξ_CP (independent method)")

r_xi = engine.assign_F_from_xi_cp(7.8)
check(r_xi.value == Fidelity.HIGH, f"ξ_CP=7.8 ≤ 8.5 → F_HIGH", f"Expected HIGH, got {r_xi.value}")

r_xi = engine.assign_F_from_xi_cp(9.5)
check(r_xi.value == Fidelity.MEDIUM, f"ξ_CP=9.5 ∈ (8.5,11.0] → F_MEDIUM", f"Expected MEDIUM, got {r_xi.value}")

r_xi = engine.assign_F_from_xi_cp(12.0)
check(r_xi.value == Fidelity.LOW, f"ξ_CP=12.0 > 11.0 → F_LOW", f"Expected LOW, got {r_xi.value}")

# ── Method independence check: ΔG and ξ_CP should agree ─────────────────────

sub("1c. Assignment method independence: ΔG vs ξ_CP")

# The CB[7]/adamantane system has ΔG ≈ −72 kJ/mol → ξ_CP ≈ 7.2 nats (F_HIGH from both)
sa = engine.assign_all({"delta_g_kj": -72.0, "xi_cp": 7.2})
if "F" in sa.assignments:
    if sa.method_comparisons:
        mc = sa.method_comparisons[0]
        check(mc.agreement, f"CB[7]/adamantane: ΔG method and ξ_CP method AGREE on F={mc.value_a.name}", f"Methods DISAGREE: {mc.summary()}")
    else:
        NOTE("Only one F method available — no cross-check")
NOTE(f"  Final F assignment: {sa.assignments['F'].value.name}, confidence={sa.assignments['F'].confidence:.2f}")

# Deliberately discordant: high ΔG but low ξ_CP (should flag conflict)
sa_conflict = engine.assign_all({"delta_g_kj": -2.0, "xi_cp": 7.5})
if sa_conflict.method_comparisons:
    mc = sa_conflict.method_comparisons[0]
    check(not mc.agreement, f"ΔG=−2.0 kJ/mol (→LOW) vs ξ_CP=7.5 (→HIGH): methods DISAGREE as expected", f"Expected method conflict, got agreement")
    check(sa_conflict.assignments["F"].confidence < 0.80, f"Conflict reduces confidence below 0.80 (got {sa_conflict.assignments['F'].confidence:.2f})", f"Expected reduced confidence")
    NOTE(f"  Conflict note: {sa_conflict.notes[0] if sa_conflict.notes else 'none'}")

# ── K assignment ─────────────────────────────────────────────────────────────

sub("1d. Kinetic character from ΔG‡")

# Imine hydrolysis: ΔG‡ ≈ 45 kJ/mol → K_FAST
r = engine.assign_K_from_barrier(45.0)
check(r.value == KineticCharacter.FAST, f"Imine hydrolysis ΔG‡=45 → K_FAST", f"Expected FAST, got {r.value}")
NOTE(r.evidence)

# Racemisation (typical): ΔG‡ ≈ 80 kJ/mol → K_MODERATE
r = engine.assign_K_from_barrier(80.0)
check(r.value == KineticCharacter.MODERATE, f"ΔG‡=80 → K_MODERATE", f"Expected MODERATE, got {r.value}")

# C-C bond rotation barrier: ΔG‡ ≈ 120 kJ/mol → K_SLOW
r = engine.assign_K_from_barrier(120.0)
check(r.value == KineticCharacter.SLOW, f"ΔG‡=120 → K_SLOW", f"Expected SLOW, got {r.value}")

# High barrier → K_TRAP
r = engine.assign_K_from_barrier(160.0)
check(r.value == KineticCharacter.TRAP, f"ΔG‡=160 → K_TRAP", f"Expected TRAP, got {r.value}")

# Pathway multiplicity override: low barrier but many competing pathways
r = engine.assign_K_from_barrier(40.0, pathway_multiplicity=4)
check(r.value == KineticCharacter.TRAP, f"ΔG‡=40 but multiplicity=4 → K_TRAP (pathway override)", f"Expected TRAP, got {r.value}")
NOTE(r.evidence)

# Boundary case: exactly at 60 kJ/mol threshold
r = engine.assign_K_from_barrier(60.0)
check(r.is_boundary, f"ΔG‡=60.0 (exact FAST/MOD boundary) → is_boundary=True", "Expected boundary")

# ── G assignment ─────────────────────────────────────────────────────────────

sub("1e. Granularity assignment")

# Single molecule: 1 component, 0.5 nm
r_comp = engine.assign_G_from_components(1)
check(r_comp.value == Granularity.LOCAL, "n=1 → G_LOCAL", f"Got {r_comp.value}")

r_scale = engine.assign_G_from_scale_nm(0.5)
check(r_scale.value == Granularity.LOCAL, "scale=0.5 nm → G_LOCAL", f"Got {r_scale.value}")

# DNA origami: ~200 staple strands, ~80 nm
r_comp = engine.assign_G_from_components(200)
check(r_comp.value == Granularity.MESOSCALE, "n=200 → G_MESOSCALE", f"Got {r_comp.value}")

r_scale = engine.assign_G_from_scale_nm(80.0)
check(r_scale.value == Granularity.MESOSCALE, "scale=80 nm → G_MESOSCALE", f"Got {r_scale.value}")

# Polymer network: 10,000 units, micron scale
r_comp = engine.assign_G_from_components(10000)
check(r_comp.value == Granularity.GLOBAL, "n=10000 → G_GLOBAL", f"Got {r_comp.value}")

r_scale = engine.assign_G_from_scale_nm(500.0)
check(r_scale.value == Granularity.GLOBAL, "scale=500 nm → G_GLOBAL", f"Got {r_scale.value}")

# G method independence: DNA origami (n=200, scale=80 nm → both MESOSCALE)
sa = engine.assign_all({"n_components": 200, "scale_nm": 80.0})
if sa.method_comparisons:
    mc = next((c for c in sa.method_comparisons if c.primitive == "G"), None)
    if mc:
        check(mc.agreement, f"DNA origami: component_count and scale_nm AGREE on G={mc.value_a.name}", f"Methods disagree: {mc.summary()}")

# ── Ω derivation (P-22 decision tree) ────────────────────────────────────────

sub("1f. Omega derivation via P-22 five-rule decision tree")

from imscrbgrmr.models import Topology, KineticCharacter, Dimensionality, InteractionGrammar, Granularity, TopoIndex

# Rule 1: K=MBL → Z2
r = engine.assign_Omega_from_primitives(
    T=Topology.NETWORK, K=KineticCharacter.MBL, D=Dimensionality.SUPRAMOLECULAR,
    Gamma=InteractionGrammar.SELECTIVE_AND, G=Granularity.LOCAL)
check(r.value == TopoIndex.Z2_CLASS, f"K=MBL → Ω=Z2_CLASS (Rule 1)", f"Got {r.value}")
NOTE(r.evidence)

# Rule 2: T=BRAID → NON_ABELIAN
r = engine.assign_Omega_from_primitives(
    T=Topology.BRAID, K=KineticCharacter.TRAP, D=Dimensionality.TEMPORAL,
    Gamma=InteractionGrammar.QUANTUM_AND, G=Granularity.GLOBAL)
check(r.value == TopoIndex.NON_ABELIAN, f"T=BRAID → Ω=NON_ABELIAN (Rule 2)", f"Got {r.value}")

# Rule 3: T=NETWORK + G=GLOBAL → CHERN
r = engine.assign_Omega_from_primitives(
    T=Topology.NETWORK, K=KineticCharacter.SLOW, D=Dimensionality.SUPRAMOLECULAR,
    Gamma=InteractionGrammar.SELECTIVE_AND, G=Granularity.GLOBAL)
check(r.value == TopoIndex.CHERN, f"T=NETWORK + G=GLOBAL → Ω=CHERN (Rule 3)", f"Got {r.value}")

# Rule 5: Γ=QUANTUM_AND → NON_ABELIAN
r = engine.assign_Omega_from_primitives(
    T=Topology.LINEAR, K=KineticCharacter.MODERATE, D=Dimensionality.MOLECULAR,
    Gamma=InteractionGrammar.QUANTUM_AND, G=Granularity.LOCAL)
check(r.value == TopoIndex.NON_ABELIAN, f"Γ=QUANTUM_AND → Ω=NON_ABELIAN (Rule 5)", f"Got {r.value}")

# Default: no rules fire → None
r = engine.assign_Omega_from_primitives(
    T=Topology.LINEAR, K=KineticCharacter.MODERATE, D=Dimensionality.MOLECULAR,
    Gamma=InteractionGrammar.SELECTIVE_AND, G=Granularity.LOCAL)
check(r.value is None, f"No rules fire → Ω=None (default)", f"Got {r.value}")

NOTE(f"P-22 decision tree confidence: {r.confidence:.2f} (derivational — not heuristic)")


# ══════════════════════════════════════════════════════════════════════════════
# SUITE 2 — Catalog Consistency Check
# ══════════════════════════════════════════════════════════════════════════════

HDR("SUITE 2 — Catalog Consistency: Algorithmic vs. Hand-Coded Assignments")

NOTE("Running algorithmic assignment against all catalog imscriptions with ξ_CP/ΔG data...")
report = check_catalog_consistency(engine)
report.print_summary()

print(f"\n  Per-primitive breakdown:")
from collections import defaultdict
prim_agree: dict = defaultdict(lambda: [0, 0])  # [agree, total]
for e in report.entries:
    prim_agree[e.primitive][1] += 1
    if e.agrees:
        prim_agree[e.primitive][0] += 1

print(f"  {'Primitive':<10}  {'Agree':>6}  {'Total':>6}  {'Rate':>7}  Conflicts")
print(f"  {'─'*10}  {'─'*6}  {'─'*6}  {'─'*7}  {'─'*30}")
for prim, (agree, total) in sorted(prim_agree.items()):
    rate = agree / total if total > 0 else 0.0
    conflicts = report.conflict_summary.get(prim, [])
    print(f"  {prim:<10}  {agree:>6}  {total:>6}  {rate:>7.1%}  {', '.join(conflicts[:3])}"
          + (" ..." if len(conflicts) > 3 else ""))

# Overall pass/fail for the test suite
overall_rate = report.overall_agreement_rate
check(overall_rate >= 0.80, f"Overall catalog agreement ≥ 80% (got {overall_rate:.1%})",
      f"Overall catalog agreement below 80% (got {overall_rate:.1%})")
check(report.boundary_rate <= 0.30, f"Boundary rate ≤ 30% (got {report.boundary_rate:.1%})",
      f"High boundary rate: {report.boundary_rate:.1%} of assignments near threshold")

# ── Boundary case analysis ────────────────────────────────────────────────────

sub("2a. Boundary case analysis — systems near tier thresholds")

boundary_entries = [e for e in report.entries if e.is_boundary]
print(f"\n  {len(boundary_entries)} boundary assignments across {len(set(e.name for e in boundary_entries))} imscriptions")
if boundary_entries:
    print(f"  {'Imscription':<40}  {'Primitive':<8}  Catalog → Assigned")
    print(f"  {'─'*40}  {'─'*8}  {'─'*30}")
    for e in sorted(boundary_entries, key=lambda x: x.name)[:20]:
        cat_name = e.catalog_value.name if hasattr(e.catalog_value, 'name') else str(e.catalog_value)
        ass_name = e.assigned_value.name if hasattr(e.assigned_value, 'name') else str(e.assigned_value)
        status = "✓" if e.agrees else "✗"
        print(f"  {e.name[:40]:<40}  {e.primitive:<8}  {status} {cat_name} → {ass_name}")


# ── Conflict analysis ─────────────────────────────────────────────────────────

sub("2b. Conflict analysis — assignments that disagree with catalog")

conflict_entries = [e for e in report.entries if not e.agrees]
if not conflict_entries:
    PASS("Zero conflicts: algorithmic assignment matches catalog 100% on available data")
else:
    print(f"\n  {len(conflict_entries)} conflicts:")
    for e in conflict_entries[:20]:
        cat_name = e.catalog_value.name if hasattr(e.catalog_value, 'name') else str(e.catalog_value)
        ass_name = e.assigned_value.name if hasattr(e.assigned_value, 'name') else str(e.assigned_value)
        bd = " [BOUNDARY]" if e.is_boundary else ""
        print(f"    {e.name[:40]:<40}  {e.primitive}: catalog={cat_name}, assigned={ass_name}{bd}")
        print(f"      Evidence: {e.note[:80]}")
    if len(conflict_entries) > 20:
        print(f"    ... and {len(conflict_entries) - 20} more")

    # Key question: are conflicts concentrated at boundaries?
    n_conflict_boundary = sum(1 for e in conflict_entries if e.is_boundary)
    frac = n_conflict_boundary / len(conflict_entries) if conflict_entries else 1.0
    check(frac >= 0.50,
          f"{frac:.0%} of conflicts are boundary cases — consistent with natural-joints hypothesis"
          + (" (no conflicts at all)" if not conflict_entries else ""),
          f"Only {frac:.0%} of conflicts are at boundaries — conflicts may reflect encoding errors or fuzzy tiers")


# ══════════════════════════════════════════════════════════════════════════════
# SUITE 3 — Decomposition Self-Consistency
# ══════════════════════════════════════════════════════════════════════════════

HDR("SUITE 3 — Decomposition Self-Consistency: Atom Re-Assignment Round-Trip")

# Test on the standard_model — 3 atoms, well-characterised
# We assign F and K from approximate ΔG values for each atom
# (using representative values for particle-physics sectors)

sub("3a. Standard Model: principal_decomp atoms → re-assign → reconstruct → check")

# SM has 3 principal atoms (from explorations):
# Atom 1: F=HIGH  sector (high-fidelity gauge vertex)
# Atom 2: F=MED   sector (intermediate fidelity)
# Atom 3: F=LOW   sector (soft sector, G=LOCAL)
sm_atom_measurements = [
    {"xi_cp": 7.5},   # Atom 1: ξ_CP in HIGH range
    {"xi_cp": 9.8},   # Atom 2: ξ_CP in MEDIUM range
    {"xi_cp": 13.0},  # Atom 3: ξ_CP in LOW range
]

results = check_decomposition_consistency("standard_model", sm_atom_measurements, engine)
if results and results[0].note and "not found" in results[0].note:
    NOTE(f"Skipped: {results[0].note}")
else:
    print(f"\n  Round-trip consistency for 'standard_model' ({results[0].n_atoms} atoms):")
    print(f"  {'Primitive':<8}  {'Original':<20}  {'Reconstructed':<20}  Status")
    print(f"  {'─'*8}  {'─'*20}  {'─'*20}  {'─'*10}")
    consistent_count = 0
    for r in results:
        orig = r.original_value.name if hasattr(r.original_value, 'name') else str(r.original_value)
        recon = r.reconstructed_value.name if hasattr(r.reconstructed_value, 'name') else str(r.reconstructed_value)
        status = "✓ CONSISTENT" if r.consistent else "✗ DRIFT"
        if r.consistent:
            consistent_count += 1
        print(f"  {r.primitive:<8}  {orig:<20}  {recon:<20}  {status}")
    check(consistent_count == len(results),
          f"All {len(results)} primitives consistent under SM decomposition round-trip",
          f"Round-trip inconsistency: {len(results) - consistent_count}/{len(results)} primitives drifted")

sub("3b. Allosteric domain: principal_decomp round-trip")

# allosteric_domain has Phi_ctyogh — the join of atoms should preserve Phi=CRITICAL
allosteric_atom_measurements = [
    {"xi_cp": 9.5, "varma_score": 0.75},   # Phi_ctyogh-carrying atom
    {"xi_cp": 11.5},                          # lower-F atom
]

results = check_decomposition_consistency("allosteric_domain", allosteric_atom_measurements, engine)
if results and results[0].note and "not found" in results[0].note:
    NOTE(f"Skipped: {results[0].note}")
else:
    print(f"\n  Round-trip consistency for 'allosteric_domain' ({results[0].n_atoms} atoms):")
    phi_result = next((r for r in results if r.primitive == "Phi"), None)
    f_result   = next((r for r in results if r.primitive == "F"), None)
    if phi_result:
        check(phi_result.consistent,
              "Phi_ctyogh is join-dominant: CRITICAL survives atom round-trip",
              f"Phi_ctyogh NOT preserved: {phi_result.note}")
    if f_result:
        check(f_result.consistent,
              "F reconstructed correctly from atom join",
              f"F drifted: {f_result.note}")


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

HDR("ALGORITHMIC ASSIGNMENT PROJECT — SUMMARY")

total = n_pass + n_fail
print(f"""
  Unit tests         : {n_pass}/{total} passed
  Catalog check      : {report.overall_agreement_rate:.1%} agreement ({report.n_imscriptions_checked} imscriptions, {report.n_primitives_checked} primitive checks)
  Boundary rate      : {report.boundary_rate:.1%} of assignments near a tier threshold

  ── What the results mean ────────────────────────────────────────────────

  ASSIGNMENT METHOD INDEPENDENCE (the decisive test):
    F from ΔG and F from ξ_CP are two independent routes to the same primitive.
    Agreement between them is evidence that the F-tier boundary is a real
    feature of the data, not an artifact of one measurement method.

  CATALOG CONSISTENCY:
    High agreement = the algorithmic rules and expert encoding converge.
    Conflicts concentrated at boundary cases = the tiers are real but the
    threshold region is genuinely ambiguous (consistent with natural joints
    that have finite measurement uncertainty).
    Conflicts in non-boundary cases = either the encoding is wrong or the
    operational definition needs refinement.

  DECOMPOSITION ROUND-TRIP:
    Consistent reconstruction = the primitives are closed under the algebra.
    Drift = the algebra introduces information not present in the individual
    atoms — a sign that the join operation does not preserve natural joints.

  ── Next steps ───────────────────────────────────────────────────────────
  • Add structural metadata (D, T, R, P flags) to the catalog to enable
    full 10-primitive algorithmic assignment.
  • Collect ΔG‡ data for catalog imscriptions to extend K assignment coverage.
  • Formalise the Phi algorithmic assignment (currently heuristic) using
    the Varma probe output as a calibrated input.
  • Run method-independence check across all primitives with two or more
    available measurement routes.
""")

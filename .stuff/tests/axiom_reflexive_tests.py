"""
axiom_reflexive_tests.py — Reflexive Closure Experiment
========================================================
Encodes Imscribing Grammar's own 7 composition axioms as imscription tuples,
then runs the full algebra on them.

Question: can the grammar understand its own rules?
Expected findings:
  - Axioms 1 & 7 cluster (both enforce T_bullseye + cyclic grounding)
  - Axiom 5 (Criticality) and Axiom 3 (Cooperative Induction) carry ⊙
  - The meet of all 7 axioms extracts the framework's "primitive core"
  - Tensor products reveal emergent structure the axioms don't individually show
  - Degeneracy (path multiplicity between axiom pairs) quantifies how many
    routes connect two rules — i.e., how structurally redundant the axiom set is

Encoding logic
--------------
Each axiom is a RULE that constrains certain primitives and implies others.
We encode:
  D  = the scale at which the axiom operates
  T  = the topology the axiom constrains or enforces
  R  = the recognition mode involved
  P  = the polarity the axiom acts on
  F  = the fidelity the axiom guarantees or requires
  K  = the kinetic regime implied
  G  = the granularity scope of the rule
  Γ  = the logical form of the rule itself (AND/SPECIFIC = hard; SELECTIVE = conditional)
  Φ  = whether the axiom is a criticality statement

Axiom map:
  A1 Cyclic Closure:       T_bullseye+P_pipevar → F_hardsign     (molecular, hard rule)
  A2 Local Grammar Barrier: G_beta+Γ_spec → no global  (molecular, hard barrier)
  A3 Cooperative Induction: superlinear → G_gamma       (supramolecular, PHASE TRANSITION → ⊙)
  A4 Sequential Grammar:   Γ_seq → D_∞ or R_downstep     (temporal, hard grounding)
  A5 Criticality:          ⊙ → G/D degeneracy       (all scales, critical, global)
  A6 Temporal Grounding:   D_∞ → physical reset cycle   (temporal, hard grounding, K_teshlig)
  A7 Cyclic Topo Grounding: T_bullseye → named closing bond (molecular, hard, R_covalent_dynamic)
"""

from __future__ import annotations

import imscrbgrmr  # populate catalog
from imscrbgrmr.models import ImscriptionNotation
from imscrbgrmr.registry import global_catalog
from imscrbgrmr.algebra import find_path, meet, tensor, tuple_distance
from imscrbgrmr.thermodynamics import compute_xi_CP
from imscrbgrmr.varma_probe import VarmaCorrelationData, score_phi_c_candidacy
from imscrbgrmr.domains.quantum import register_quantum_imscriptions

register_quantum_imscriptions()

# ── 1. Encode each axiom as a imscription tuple ────────────────────────────────────

AXIOM_NOTATIONS = {
    "axiom_1_cyclic_closure": (
        "⟨D_wynn; T_bullseye; R_superset; P_pm_pseudo; F_hardsign; K_frtailgamma; G_gamma; Gamma_and(SPECIFIC); Phi_softsign⟩",
        "Cyclic closure amplifies fidelity: T_bullseye+P_pm_pseudo→F_hardsign. "
        "Hard rule at molecular scale — any cyclic self-complementary motif must achieve F≥F_dh.",
    ),
    "axiom_2_local_barrier": (
        "⟨D_wynn; T_linear; R_subset; P_pm_pseudo; F_dh; K_turnm; G_beta; Gamma_and(SPECIFIC); Phi_softsign⟩",
        "Local grammar barrier: G_beta+Gamma_and(SPECIFIC) cannot propagate constraint beyond "
        "immediate recognition pair. Hard barrier at molecular scale.",
    ),
    "axiom_3_cooperative_induction": (
        "⟨D_turnthree; T_nrleg; R_superset; P_pm_pseudo; F_dh; K_schwa; G_gamma; Gamma_and(SELECTIVE); ⊙⟩",
        "Cooperative induction superlinearity signals G_beta→G_gamma phase transition. "
        "Supramolecular scale, selective — only fires when induction ratio is superlinear. "
        "This axiom IS a criticality statement: the transition is a phase boundary.",
    ),
    "axiom_4_sequential_grammar": (
        "⟨D_infinity; T_linear; R_downstep; P_directional; F_dh; K_turnm; G_gamma; Gamma_and(SPECIFIC); Phi_softsign⟩",
        "Sequential grammar requires temporal or catalytic dimension: Gamma_seq→D_∞ or R_downstep. "
        "Hard grounding rule — sequential logic without a physical time arrow is disallowed.",
    ),
    "axiom_5_criticality": (
        "⟨D_all; T_nrleg; R_downstep; P_pm_pseudo; F_dh; K_turnm; G_revapostrophe; Gamma_and(SELECTIVE); ⊙⟩",
        "Criticality contracts the primitive basis: at ⊙, G/D become degenerate (scale-free). "
        "Applies at all scales, global scope. The framework's most powerful compression rule.",
    ),
    "axiom_6_temporal_grounding": (
        "⟨D_infinity; T_bullseye; R_downstep; P_pm_pseudo; F_dh; K_teshlig; G_gamma; Gamma_and(SPECIFIC); Phi_softsign⟩",
        "D_∞ requires physically grounded reset mechanism — the reset creates a closed cycle (T_bullseye). "
        "K_teshlig: the system is kinetically trapped until the reset event occurs.",
    ),
    "axiom_7_cyclic_topo_grounding": (
        "⟨D_wynn; T_bullseye; R_covalent_dynamic; P_pm_pseudo; F_hardsign; K_turnm; G_beta; Gamma_and(SPECIFIC); Phi_softsign⟩",
        "T_bullseye requires a named closing bond/interaction. Hard grounding at molecular scale — "
        "cyclic topology without an explicit closing interaction is ungrounded.",
    ),
}

axiom_imscriptions = {}
for name, (notation_str, description) in AXIOM_NOTATIONS.items():
    notation = ImscriptionNotation.parse(notation_str)
    imscription = notation.to_imscription(name, description)
    global_catalog.register(imscription, registered_by="reflexive_closure_experiment")
    axiom_imscriptions[name] = imscription
    print(f"  registered: {name}")

names = list(axiom_imscriptions.keys())
short = {n: n.replace("axiom_", "A").replace("_cyclic_closure", "1")
                                     .replace("_local_barrier", "2")
                                     .replace("_cooperative_induction", "3")
                                     .replace("_sequential_grammar", "4")
                                     .replace("_criticality", "5")
                                     .replace("_temporal_grounding", "6")
                                     .replace("_cyclic_topo_grounding", "7")
         for n in names}

print()

# ── 2. Pairwise distances — the geometry of the axiom set ─────────────────────

print("=" * 70)
print("§ 1  PAIRWISE DISTANCES  (lower = more structurally similar)")
print("=" * 70)

catalog = global_catalog.search()

dist_matrix = {}
for i, na in enumerate(names):
    for nb in names[i+1:]:
        sa, sb = axiom_imscriptions[na], axiom_imscriptions[nb]
        d = tuple_distance(sa, sb)
        dist_matrix[(na, nb)] = d

ranked = sorted(dist_matrix.items(), key=lambda x: x[1])
for (na, nb), d in ranked:
    print(f"  {short[na]} ↔ {short[nb]:3s}  d = {d:.3f}")

# ── 3. HotSwap paths between axiom pairs ──────────────────────────────────────

print()
print("=" * 70)
print("§ 2  HOTSWAP PATHS  (degeneracy = path multiplicity)")
print("=" * 70)
print("(Only pairs with d < 2.5 checked — closer axioms more likely connected)")
print()

close_pairs = [(na, nb) for (na, nb), d in ranked if d < 2.5]
for na, nb in close_pairs:
    sa, sb = axiom_imscriptions[na], axiom_imscriptions[nb]
    r = find_path(sa, sb, catalog, max_hops=6, xi_tolerance=2.0)
    status = f"✓ {r.n_hops}-hop  Δξ={r.total_delta:+.3f}" if r.found else f"✗ blocked ({', '.join(r.notes[:1])})"
    print(f"  {short[na]} → {short[nb]:3s}  {status}")

# ── 4. Pairwise meets — shared primitive floor ────────────────────────────────

print()
print("=" * 70)
print("§ 3  PAIRWISE MEETS  (shared primitive floor / state-switching levers)")
print("=" * 70)

interesting = [(na, nb) for (na, nb), d in ranked[:6]]
for na, nb in interesting:
    sa, sb = axiom_imscriptions[na], axiom_imscriptions[nb]
    m = meet(sa, sb)
    print(f"\n  meet({short[na]}, {short[nb]}) = {m.to_notation()}")
    if m.conflicts:
        print(f"    CONFLICTS (state-switching levers): {m.conflicts}")
    else:
        print(f"    No conflicts — axioms differ only in ordered primitives")

# ── 5. Global meet of all 7 axioms — the framework's primitive core ───────────

print()
print("=" * 70)
print("§ 4  GLOBAL MEET  (floor of all 7 axioms = framework primitive core)")
print("=" * 70)

# Chain meets: LatticeResult has primitive fields directly; extract shared values
# across all 7 axioms by counting what fraction of axioms agree on each primitive.
from imscrbgrmr.models import Dimensionality, Topology, RecognitionMode, Polarity
from imscrbgrmr.models import Fidelity, KineticCharacter, Granularity, CriticalityPhase

fields = {
    "D": [s.dimensionality       for s in axiom_imscriptions.values()],
    "T": [s.topology             for s in axiom_imscriptions.values()],
    "R": [s.recognition_mode     for s in axiom_imscriptions.values()],
    "P": [s.polarity             for s in axiom_imscriptions.values()],
    "F": [s.fidelity             for s in axiom_imscriptions.values()],
    "K": [s.kinetic_character    for s in axiom_imscriptions.values()],
    "G": [s.granularity          for s in axiom_imscriptions.values()],
    "Γ": [s.interaction_grammar  for s in axiom_imscriptions.values()],
    "Φ": [s.criticality_phase    for s in axiom_imscriptions.values()],
}

print(f"  {'Primitive':<4}  {'Shared value (if unanimous)':<30}  {'Agreement':>10}")
print(f"  {'-'*4}  {'-'*30}  {'-'*10}")
core_primitives = {}
for prim, vals in fields.items():
    unique = set(vals)
    if len(unique) == 1:
        v = vals[0]
        print(f"  {prim:<4}  {str(v.value):<30}  7/7  ← UNANIMOUS")
        core_primitives[prim] = v
    else:
        from collections import Counter
        ctr = Counter(vals)
        top_val, top_count = ctr.most_common(1)[0]
        print(f"  {prim:<4}  {str(top_val.value):<30}  {top_count}/7")
        core_primitives[prim] = None  # conflicted

# ── 6. Criticality probe on each axiom ───────────────────────────────────────

print()
print("=" * 70)
print("§ 5  CRITICALITY PROBE  (Varma score + ξ_CP per axiom)")
print("=" * 70)
print(f"  {'Axiom':<38} {'⊙ score':>10}  {'label':<22}  {'ξ_CP':>8}")
print(f"  {'-'*38} {'-'*10}  {'-'*22}  {'-'*8}")

# Varma QXY reference values (log-scaling: xi_r ≈ ln(xi_tau))
corr = VarmaCorrelationData(xi_r=13.8, xi_tau=1_000_000)

for n in names:
    s = axiom_imscriptions[n]
    report = score_phi_c_candidacy(s, corr)
    try:
        xi_cp = compute_xi_CP(s, delta_g=-50.0)
        xi_str = f"{xi_cp:.2f}"
    except Exception:
        xi_str = "—"
    print(f"  {short[n]:<38} {report.score:>10.3f}  {report._candidacy_label():<22}  {xi_str:>8}")

# ── 7. Tensor products — what emerges from axiom compositions ─────────────────

print()
print("=" * 70)
print("§ 6  TENSOR PRODUCTS  (emergent structure from axiom pairs)")
print("=" * 70)
print("  (Axiom pairs likely to be simultaneously active in a single system)")
print()

tensor_pairs = [
    ("axiom_1_cyclic_closure",        "axiom_7_cyclic_topo_grounding",   "closure + grounding"),
    ("axiom_5_criticality",           "axiom_3_cooperative_induction",   "criticality + cooperation"),
    ("axiom_6_temporal_grounding",    "axiom_4_sequential_grammar",      "temporal grounding + seq logic"),
    ("axiom_5_criticality",           "axiom_1_cyclic_closure",          "criticality + cyclic fidelity"),
]

for na, nb, label in tensor_pairs:
    sa, sb = axiom_imscriptions[na], axiom_imscriptions[nb]
    try:
        t = tensor(sa, sb)
        xi_str = f"{t.xi_cp_predicted:.2f}" if t.xi_cp_predicted else "—"
        phi_str = t.criticality_phase.value if t.criticality_phase else "—"
        print(f"  {label}")
        print(f"    ⊗ = {t.to_notation()}")
        print(f"    Φ={phi_str}  ξ_CP(predicted)={xi_str}  G={t.granularity.value if t.granularity else '⊥'}")
    except Exception as e:
        print(f"  {label}  ✗ tensor failed: {e}")
    print()

# ── 8. Three new metrics: degeneracy, ξ_CP, ⊙ as fundamental descriptors ───

print()
print("=" * 70)
print("§ 7  MORE FUNDAMENTAL DESCRIPTORS?")
print("     Testing: Degeneracy (path multiplicity) · ξ_CP · ⊙ ordering")
print("=" * 70)

print("""
Hypothesis: the three metrics form a CAUSAL HIERARCHY, not three
independent consciousness correlates:

   ⊙  →  enables maximum path multiplicity (degeneracy)
         →  because at criticality G/D are degenerate (Axiom 5),
            meaning every region of imscription space is reachable from
            every other — the HotSwap graph becomes fully connected.

   Degeneracy  →  amplifies effective ξ_CP through redundant channels
              →  N independent paths each contribute ξ_CP nats;
                 total channel capacity = N × ξ_CP (parallel channels).

   N × ξ_CP  =  the system's total information degeneracy
             →  THIS is what the literature calls "consciousness-related"
                but it's derivable from first principles here.
""")

# Empirical test: do ⊙ imscriptions have more HotSwap paths to each other?
phi_c_axioms = [n for n in names if axiom_imscriptions[n].criticality_phase.value == "⊙_ctyogh"]
phi_sub_axioms = [n for n in names if axiom_imscriptions[n].criticality_phase.value == "⊙_softsign"]

print(f"  Axioms with ⊙: {[short[n] for n in phi_c_axioms]}")
print(f"  Axioms with Phi_softsign: {[short[n] for n in phi_sub_axioms]}")
print()

# Count paths: ⊙ ↔ ⊙ vs Phi_softsign ↔ Phi_softsign
cc_paths, ss_paths = 0, 0
cc_found, ss_found = 0, 0
for i, na in enumerate(phi_c_axioms):
    for nb in phi_c_axioms[i+1:]:
        cc_paths += 1
        r = find_path(axiom_imscriptions[na], axiom_imscriptions[nb], catalog, max_hops=6, xi_tolerance=2.0)
        if r.found:
            cc_found += 1

for i, na in enumerate(phi_sub_axioms):
    for nb in phi_sub_axioms[i+1:]:
        ss_paths += 1
        r = find_path(axiom_imscriptions[na], axiom_imscriptions[nb], catalog, max_hops=6, xi_tolerance=2.0)
        if r.found:
            ss_found += 1

print(f"  ⊙ ↔ ⊙ paths:   {cc_found}/{cc_paths} connected")
print(f"  Phi_softsign ↔ Phi_softsign paths: {ss_found}/{ss_paths} connected")
if cc_paths and ss_paths:
    cc_rate = cc_found / cc_paths
    ss_rate = ss_found / ss_paths if ss_paths else 0
    print(f"  Connectivity ratio ⊙/Phi_softsign: {cc_rate:.2f}/{ss_rate:.2f}")
    if cc_rate > ss_rate:
        print("  → CONFIRMED: ⊙ axioms are more mutually reachable (higher degeneracy)")
    elif cc_rate == ss_rate:
        print("  → NEUTRAL: equal connectivity — more catalog entries needed to distinguish")
    else:
        print("  → UNEXPECTED: Phi_softsign axioms are more connected — check encoding")

print()
print("=" * 70)
print("  Reflexive closure verdict:")
print("=" * 70)
print()

unanimous = {p: v for p, v in core_primitives.items() if v is not None}
conflicted = [p for p, v in core_primitives.items() if v is None]
meet_phi = unanimous.get("Φ")
phi_val = meet_phi.value if meet_phi else "⊥ (conflicted)"
print(f"\n  Floor Φ: {phi_val}")
print(f"  Unanimous primitives ({len(unanimous)}/9): {list(unanimous.keys())}")
print(f"  Conflicted (⊥) primitives ({len(conflicted)}/9): {conflicted}")
if phi_val == "⊙_ctyogh":
    print("  ✅ REFLEXIVE CLOSURE: framework's axiom floor is critical.")
    print("     Grammar applied to itself recovers ⊙ as its ground state.")
elif phi_val == "⊙_softsign":
    print("  ⚠  Floor is Phi_softsign — criticality is not the axiom floor but an overlay.")
    print("     ⊙ lives at Axiom 3 and 5 level, not at the ground primitive level.")
    print("     Interpretation: criticality is EMERGENT from the axiom set, not assumed.")
    print("     → Correct result for an anti-primitive framework: ⊙ is derived, not assumed.")
else:
    print(f"  Φ floor = {phi_val}")

print()
print("Cleanup: removing axiom imscriptions from catalog...")
for n in names:
    global_catalog.remove(n)
print(f"  Removed {len(names)} axiom imscriptions. Catalog restored to {len(global_catalog)} entries.")

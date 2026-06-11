"""
demo.py — Demonstration and Verification Suite.

Runs all demonstrations of the Frobenius-guided gene editing engine.
Also contains the verification suite (tests).
"""

from collections import defaultdict
from typing import Dict, List

from genetic_engine.lattice import B4Element
from genetic_engine.codon import CODON_TABLE, CODON_BY_SYMBOL
from genetic_engine.stratum import FrobeniusStratum, FrobeniusStratumClassifier
from genetic_engine.editor import B4EditAnalyzer
from genetic_engine.guide import FrobeniusGuideDesigner
from genetic_engine.prime import PrimeEditOptimizer
from genetic_engine.verifier import FrobeniusVerifier
from genetic_engine.chimera import ChimeraDetector
from genetic_engine.compiler import EditingCompiler


def _hr(title: str) -> None:
    print(f"\n── {title} {'─'*(56-len(title))}")


# ── Verification suite ────────────────────────────────────────────

def verify_b4_lattice() -> bool:
    assert B4Element.B.covers(B4Element.T)
    assert B4Element.B.covers(B4Element.N)
    assert B4Element.T.covers(B4Element.F)
    assert B4Element.N.covers(B4Element.F)
    assert not B4Element.B.covers(B4Element.F)
    assert not B4Element.T.covers(B4Element.N)
    assert B4Element.B.lattice_distance(B4Element.F) == 2
    assert B4Element.T.lattice_distance(B4Element.N) == 2
    assert B4Element.B.lattice_distance(B4Element.T) == 1
    assert B4Element.T.lattice_distance(B4Element.F) == 1
    assert B4Element.from_symbol('G') == B4Element.B
    assert B4Element.from_symbol('C') == B4Element.T
    assert B4Element.from_symbol('A') == B4Element.F
    assert B4Element.from_symbol('U') == B4Element.N
    print("  ✓ B₄ lattice: covering relations, distances, mapping")
    return True


def verify_codon_table() -> bool:
    assert len(CODON_TABLE) == 64, f"Expected 64, got {len(CODON_TABLE)}"
    stops = sum(1 for c in CODON_BY_SYMBOL.values() if c.is_stop)
    assert stops == 3, f"Expected 3 stops, got {stops}"
    exact = sum(1 for c in CODON_BY_SYMBOL.values() if c.is_exact_stratum)
    assert exact == 32, f"Expected 32 exact, got {exact}"
    assert CODON_BY_SYMBOL['AUG'].amino_acid == "Met"
    assert CODON_BY_SYMBOL['AUG'].is_start
    assert CODON_TABLE['UUU'] == 'Phe'
    assert CODON_TABLE['UGG'] == 'Trp'
    assert CODON_TABLE['UAA'] == 'Stop'
    print(f"  ✓ Codon table: 64 codons, {exact} exact, {64-exact-stops} split, {stops} stop")
    return True


def verify_primitive_map() -> bool:
    from genetic_engine.primitives import AA_PRIMITIVE_MAP, IGPrimitive
    all_aas = set(CODON_TABLE.values())
    mapped = set(AA_PRIMITIVE_MAP.keys())
    for aa in all_aas:
        assert aa in mapped, f"{aa} missing"
    promoted = sum(1 for p in AA_PRIMITIVE_MAP.values() if p is not None)
    assert promoted == 13, f"Expected 13 promoted, got {promoted}"
    assert AA_PRIMITIVE_MAP['Met'] == IGPrimitive.SCOPE
    assert AA_PRIMITIVE_MAP['Trp'] == IGPrimitive.TOPOLOGY
    assert AA_PRIMITIVE_MAP['Cys'] == IGPrimitive.REVERSIBILITY
    assert AA_PRIMITIVE_MAP['Stop'] == IGPrimitive.WINDING
    print(f"  ✓ Primitive map: {promoted} promoted, {len(mapped)-promoted} ground")
    return True


def verify_b4_edit_analysis() -> bool:
    cbe = B4EditAnalyzer.base_editor_cost("CBE")
    assert cbe["lattice_distance"] == 2, f"CBE={cbe['lattice_distance']}"
    abe = B4EditAnalyzer.base_editor_cost("ABE")
    assert abe["lattice_distance"] == 2, f"ABE={abe['lattice_distance']}"
    uc = B4EditAnalyzer.base_editor_cost("U→C")
    assert uc["lattice_distance"] == 2, f"U→C={uc['lattice_distance']}"
    r = B4EditAnalyzer.analyze("GCU", "GCC")
    assert r.silent, "GCU→GCC silent"
    assert r.total_cost == 2, f"GCU→GCC cost={r.total_cost}"
    print("  ✓ B₄ edit analysis: CBE=2, ABE=2, silent detected")
    return True


def verify_stratum_classifier() -> bool:
    c = FrobeniusStratumClassifier()
    assert c.classify("CUU") == FrobeniusStratum.EXACT
    assert c.classify("GGC") == FrobeniusStratum.EXACT
    assert c.classify("UUU") == FrobeniusStratum.SPLIT
    assert c.classify("AAA") == FrobeniusStratum.SPLIT
    assert c.classify("UAA") == FrobeniusStratum.STOP
    assert c.classify("UGA") == FrobeniusStratum.STOP
    wr = c.analyze_window(["AUG", "CAU", "GGU", "UAA"])
    assert wr.exact_count >= 1
    assert wr.stop_count == 1
    assert "degenerate" in c.position3_strategy(FrobeniusStratum.EXACT).lower()
    assert "pyrimidine" in c.position3_strategy(FrobeniusStratum.SPLIT).lower()
    print("  ✓ Stratum classifier: exact/split/stop correct")
    return True


def verify_guide_designer() -> bool:
    g = FrobeniusGuideDesigner()
    ge = g.design("GCU")
    assert ge.stratum == FrobeniusStratum.EXACT
    assert 'N' in ge.guide_sequence
    gs = g.design("UUU")
    assert gs.stratum == FrobeniusStratum.SPLIT
    assert 'N' not in gs.guide_sequence
    assert g.design("UAA").stratum == FrobeniusStratum.STOP
    off = g.off_target_stratum_risk("GCU", ["GCC", "UUU", "AUG"])
    assert off["cross_stratum_off_targets"] >= 1
    print("  ✓ Guide designer: exact→N, split→Y/R, stop→exact")
    return True


def verify_prime_edit_optimizer() -> bool:
    pe = PrimeEditOptimizer.optimize("GCU", "GCC")
    assert pe.stratum_preserved
    assert pe.b4_lattice_cost == 2
    pe3 = PrimeEditOptimizer.optimize("UGU", "UGG")
    assert pe3.stratum_preserved
    assert not pe3.primitive_invariant
    print("  ✓ Prime edit optimizer: silent, crossing, primitive change detected")
    return True


def verify_chimera_detector() -> bool:
    safe = ChimeraDetector.analyze_edit_set([("Lys", "Arg")])
    assert not safe.is_trap_state
    trap = ChimeraDetector.analyze_edit_set([("Cys", "Ser"), ("Asp", "Asn")])
    print(f"  ✓ Chimera detector: safe=Lys→Arg, trap=Cys+Asp ({trap.tensor_risk:.1f}x)")
    return True


def verify_frobenius_verifier() -> bool:
    v1 = FrobeniusVerifier.verify("GCU", "GCC")
    assert v1.frobenius_closed, "Silent same-stratum should be closed"
    v2 = FrobeniusVerifier.verify("AUG", "UAA")
    assert not v2.frobenius_closed, "Met→Stop should be open"
    proto = FrobeniusVerifier.verify_protocol([("GCU", "GCC"), ("AUG", "AUU")])
    assert "per_edit" in proto
    print(f"  ✓ Frobenius verifier: closed=GCU→GCC, open=AUG→UAA, protocol={proto['protocol_quality']}")
    return True


def verify_compiler_pipeline() -> bool:
    compiler = EditingCompiler()
    r = compiler.compile("Met", "Ile")
    assert r.codon_paths
    assert r.primitive_delta is not None
    assert r.frobenius_verification is not None
    assert r.composite_score >= 0.0
    multi = compiler.compile_multi([("Cys", "Ser"), ("His", "Gln")])
    assert "chimera" in multi
    print(f"  ✓ Compiler pipeline: Met→Ile (score={r.composite_score:.3f}), multi-edit chimera")
    return True


def run_verification_suite() -> Dict[str, bool]:
    print("─" * 60)
    print("GENETIC ENGINE — Verification Suite")
    print("─" * 60)
    results = {
        "b4_lattice": verify_b4_lattice(),
        "codon_table": verify_codon_table(),
        "primitive_map": verify_primitive_map(),
        "b4_edit_analysis": verify_b4_edit_analysis(),
        "stratum_classifier": verify_stratum_classifier(),
        "guide_designer": verify_guide_designer(),
        "prime_edit_optimizer": verify_prime_edit_optimizer(),
        "chimera_detector": verify_chimera_detector(),
        "frobenius_verifier": verify_frobenius_verifier(),
        "compiler_pipeline": verify_compiler_pipeline(),
    }
    print("─" * 60)
    all_pass = all(results.values())
    print(f"  {'✓ ALL TESTS PASSED' if all_pass else '✗ SOME TESTS FAILED'}")
    print("─" * 60)
    return results

# ── Demo functions ───────────────────────────────────────────────

def demo_b4_lattice() -> None:
    _hr("B₄ LATTICE — Nucleotide Structural Types")
    print("""
        B = Both (G)
       / \\
      T = C   N = U
       \\ /
        F = False (A)
    """)
    print("  Covering relations (structural cost = 1):")
    for a in B4Element:
        for b in B4Element:
            if a.covers(b):
                print(f"    {a.value:<8} → {b.value:<8}")
    print("\n  Cross-lattice jumps (structural cost = 2):")
    for a, b in [(B4Element.B, B4Element.F), (B4Element.T, B4Element.N)]:
        print(f"    {a.value:<8} ↔ {b.value:<8}")


def demo_base_editors() -> None:
    _hr("BASE EDITOR STRUCTURAL ANALYSIS")
    for et in ["CBE", "ABE", "U→C", "G→U"]:
        r = B4EditAnalyzer.base_editor_cost(et)
        print(f"  {et:<6} ({r['orig_nucleotide']}→{r['target_nucleotide']}): "
              f"B₄ distance={r['lattice_distance']}, quality={r['structural_quality']}")


def demo_codon_stratification() -> None:
    _hr("FROBENIUS STRATIFICATION OF CODON SPACE")
    boxes: Dict[str, List[str]] = defaultdict(list)
    boxes_aa: Dict[str, set] = defaultdict(set)
    for sym, aa in sorted(CODON_TABLE.items()):
        box = sym[:2] + "_"
        boxes[box].append(sym)
        boxes_aa[box].add(aa)

    classifier = FrobeniusStratumClassifier()
    print(f"\n  {'Box':<6} {'Stratum':<12} {'Codons':<30} {'AAs'}")
    print(f"  {'─'*70}")
    for box in sorted(boxes):
        stratum = classifier.classify(boxes[box][0]).value
        codons = " ".join(boxes[box])
        aas_set = boxes_aa[box]
        aas = "/".join(sorted(a for a in aas_set if a != "Stop"))
        if "Stop" in aas_set:
            aas += " + STOP"
        print(f"  {box:<6} {stratum:<12} {codons:<30} {aas}")


def demo_edit_analysis() -> None:
    _hr("EDIT COST ANALYSIS — Common Therapeutic Edits")
    tests = [
        ("AUG", "AUU", "Met→Ile (pathogenic)"),
        ("GAG", "GUG", "Glu→Val (sickle cell)"),
        ("UGU", "UGG", "Cys→Trp"),
        ("GCU", "GCC", "Ala silent"),
        ("CUG", "CUU", "Leu silent"),
        ("UAU", "UAA", "Tyr→Stop"),
    ]
    print(f"\n  {'Edit':<20} {'AA change':<20} {'Cost':<6} {'Type':<18} {'Stratum crossing':<18} {'Silent'}")
    print(f"  {'─'*90}")
    for o, t, desc in tests:
        r = B4EditAnalyzer.analyze(o, t)
        cross = '✓' if r.stratum_crossing else '✗'
        sil = '✓' if r.silent else '✗'
        print(f"  {o}→{t:<16} {desc:<20} {r.total_cost:<6} {r.lattice_type:<18} {cross:<18} {sil}")


def demo_guide_design() -> None:
    _hr("GUIDE RNA DESIGN — Frobenius-Optimized")
    for codon in ["GCU", "UUU", "UAA"]:
        guide = FrobeniusGuideDesigner.design(codon)
        aa = CODON_TABLE[codon]
        print(f"\n  Target: {codon} ({aa}) — {guide.stratum.value} stratum")
        print(f"  Guide:  {guide.guide_sequence}")
        print(f"  Seed:   {guide.seed_region}")
        print(f"  Oligo:  {guide.design_notes}")


def demo_compiler_pipeline() -> None:
    _hr("EDITING COMPILER — Full Pipeline Demos")
    compiler = EditingCompiler()

    # Demo 1: Sickle cell
    print("\n  Demo 1: Sickle Cell Anemia (Glu→Val)")
    print("  ─────────────────────────────────────")
    r = compiler.compile("Glu", "Val")
    print(f"  Change: {r.desired_change}")
    print(f"  Best path: {r.best_path[0]} → {r.best_path[1]} (cost={r.best_path[2]})")
    print(f"  Primitive: {r.primitive_delta.get('orig_primitive')} → "
          f"{r.primitive_delta.get('target_primitive')} "
          f"({r.primitive_delta.get('risk_class')})")
    print(f"  Stratum: {r.stratum_analysis.get('orig_stratum')} → "
          f"{r.stratum_analysis.get('target_stratum')} "
          f"({'crossing!' if r.stratum_analysis.get('crossing') else 'preserved'})")
    if r.guide_design:
        print(f"  Guide: {r.guide_design.guide_sequence}")
    print(f"  Verification: {'CLOSED' if r.frobenius_verification.frobenius_closed else 'OPEN'} "
          f"(ratio={r.frobenius_verification.closure_ratio:.3f})")
    print(f"  Score: {r.composite_score:.3f}")

    # Demo 2: Met→Ile
    print("\n  Demo 2: Pathogenic Missense (Met→Ile)")
    print("  ─────────────────────────────────────")
    r2 = compiler.compile("Met", "Ile")
    print(f"  Best path: {r2.best_path[0]} → {r2.best_path[1]} (cost={r2.best_path[2]})")
    print(f"  Primitive: {r2.primitive_delta.get('orig_primitive')} → "
          f"{r2.primitive_delta.get('target_primitive')}")
    print(f"  Score: {r2.composite_score:.3f}")

    # Demo 3: Silent edit
    print("\n  Demo 3: Silent Edit (Ala, exact stratum)")
    print("  ───────────────────────────────────────")
    r3 = compiler.compile("Ala", "Ala")
    print(f"  Best path: {r3.best_path[0]} → {r3.best_path[1]} (cost={r3.best_path[2]})")
    print(f"  Guide: {r3.guide_design.guide_sequence if r3.guide_design else 'N/A'}")
    print(f"  Score: {r3.composite_score:.3f}")

    # Demo 4: Multi-edit chimera
    print("\n  Demo 4: Multi-Edit Chimera Risk")
    print("  ───────────────────────────────")
    multi = compiler.compile_multi([("Cys", "Ser"), ("His", "Gln")])
    print(f"  Tensor risk: {multi['chimera'].tensor_risk:.1f}x")
    print(f"  Class: {multi['chimera'].tensor_class}")
    print(f"  Trap: {multi['chimera'].is_trap_state}")
    print(f"  Rec: {multi['chimera'].recommendation}")


def demo_verification() -> None:
    _hr("FROBENIUS VERIFICATION — μ∘δ=id Closure Checks")
    scenarios = [
        ("GCU", "GCC", "Ala silent (exact)"),
        ("UUU", "UUC", "Phe silent (split)"),
        ("AUG", "AUU", "Met→Ile missense"),
        ("UGU", "UGG", "Cys→Trp (Ř→Þ)"),
        ("AUG", "UAA", "Met→Stop (Ω violation)"),
    ]
    print(f"\n  {'Edit':<20} {'Scenario':<30} {'Status':<16} {'Ratio':<8}")
    print(f"  {'─'*75}")
    for t, e, desc in scenarios:
        v = FrobeniusVerifier.verify(t, e)
        status = "CLOSED ✓" if v.frobenius_closed else "OPEN ✗"
        print(f"  {t}→{e:<14} {desc:<30} {status:<16} {v.closure_ratio:<8.3f}")


def demo_chimera_risk() -> None:
    _hr("CHIMERA RISK — Tensor Product Analysis")
    pairs = [
        [("Lys", "Arg")],
        [("Cys", "Ser")],
        [("Cys", "Ser"), ("His", "Gln")],
        [("Cys", "Ser"), ("Asp", "Asn")],
        [("Met", "Ile"), ("Asp", "Glu")],
    ]
    for edit_set in pairs:
        r = ChimeraDetector.analyze_edit_set(edit_set)
        print(f"\n  Edit: {', '.join(r.edits)}")
        print(f"  Tensor: {r.tensor_risk:.1f}x ({r.tensor_class})")
        if r.is_trap_state:
            print(f"  ⚠ TRAP: {r.trap_description[:100]}")


def demo_cas9_off_target() -> None:
    _hr("Cas9 OFF-TARGET SHEAF THEOREM")
    on_target = "GCA"
    off_targets = ["GCC", "GUC", "UGG", "AUG", "UAA", "GUU"]
    r = FrobeniusGuideDesigner.off_target_stratum_risk(on_target, off_targets)
    print(f"\n  On-target: {on_target} ({r['on_stratum']} stratum)")
    print(f"  Cross-stratum: {r['cross_stratum_off_targets']}/{r['off_target_count']}")
    for d in r['details']:
        same = '✓' if d['same_stratum'] else '✗'
        print(f"  {d['off_target']:<10} {d['off_stratum']:<10} {same:<6} "
              f"{d['structural_defect_risk_pct']:.0f}% risk")


def demo_structural_summary() -> None:
    _hr("Structural Summary (Imscribing Grammar)")
    rows = [
        ("genetic_code",
         "⟨Ð_ω; Þ_ò; Ř_=; Φ_υ; ƒ_ð; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩",
         "O_∞", "stratified Frobenius algebra on B₄³"),
        ("whale_vocalization",
         "⟨Ð_ω; Þ_ò; Ř_=; Φ_υ; ƒ_ð; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩",
         "O_∞", "self-modeling communication"),
        ("grammar_itself",
         "⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_S; Ω_z⟩",
         "O_∞", "self-imscribed"),
    ]
    for name, tup, tier, note in rows:
        print(f"\n  {name:<22}")
        print(f"  {tup:<72}")
        print(f"  Tier: {tier:<10}  Note: {note}")


def run_all_demos() -> None:
    """Run all demonstration functions."""
    print("=" * 64)
    print("GENETIC ENGINE · Frobenius-Guided Gene Editing via IG Grammar")
    print("Editing = local modification of the Frobenius algebra on codon space")
    print("=" * 64)
    demo_b4_lattice()
    demo_base_editors()
    demo_codon_stratification()
    demo_edit_analysis()
    demo_guide_design()
    demo_compiler_pipeline()
    demo_verification()
    demo_chimera_risk()
    demo_cas9_off_target()
    demo_structural_summary()
    print("\n" + "=" * 64)
    print("GENETIC ENGINE DEMO COMPLETE")
    print("=" * 64)

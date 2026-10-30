"""
cli.py — Command-Line Interface for the Frobenius Gene Editing Engine.

Usage:
  genetic-engine analyze AUG AUU          # Analyze edit cost
  genetic-engine compile Met Ile          # Compile full protocol
  genetic-engine guide GCU                 # Design guide RNA
  genetic-engine verify GCU GCC            # Verify Frobenius closure
  genetic-engine chimera Cys:Ser His:Gln   # Tensor risk
  genetic-engine demo                      # Run full demo suite
  genetic-engine test                      # Run verification suite
  genetic-engine stratum CUU               # Classify codon stratum
"""

from __future__ import annotations
import sys

from genetic_engine.editor import B4EditAnalyzer
from genetic_engine.compiler import EditingCompiler
from genetic_engine.guide import FrobeniusGuideDesigner
from genetic_engine.verifier import FrobeniusVerifier
from genetic_engine.chimera import ChimeraDetector
from genetic_engine.stratum import FrobeniusStratumClassifier
from genetic_engine.demo import run_all_demo, run_verification_suite


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "analyze" and len(sys.argv) >= 4:
        r = B4EditAnalyzer.analyze(sys.argv[2], sys.argv[3])
        print(f"Edit: {r.orig_codon} → {r.target_codon}")
        print(f"  AA change: {r.aa_change[0]} → {r.aa_change[1]}")
        print(f"  B₄ cost: {r.total_cost}/6 ({r.per_position})")
        print(f"  Type: {r.lattice_type}")
        print(f"  Stratum crossing: {'YES' if r.stratum_crossing else 'no'}")
        print(f"  Silent: {'yes' if r.silent else 'no'}")
        print(f"  Risk: {r.risk_level}")

    elif cmd == "compile" and len(sys.argv) >= 4:
        compiler = EditingCompiler()
        r = compiler.compile(sys.argv[2], sys.argv[3])
        print(f"Compiled edit: {r.desired_change}")
        print(f"  Best path: {r.best_path[0]} → {r.best_path[1]} (cost={r.best_path[2]})")
        print(f"  Primitive: {r.primitive_delta.get('orig_primitive')} → "
              f"{r.primitive_delta.get('target_primitive')} "
              f"(risk={r.primitive_delta.get('risk_class', '?')})")
        print(f"  Frobenius: {'CLOSED' if r.frobenius_verification.frobenius_closed else 'OPEN'} "
              f"(ratio={r.frobenius_verification.closure_ratio:.3f})")
        print(f"  Score: {r.composite_score:.3f}")
        if r.guide_design:
            print(f"  Guide: {r.guide_design.guide_sequence}")
        if r.prime_edit:
            print(f"  RT template: {r.prime_edit.rt_template}")

    elif cmd == "guide" and len(sys.argv) >= 3:
        g = FrobeniusGuideDesigner.design(sys.argv[2])
        print(f"Guide for {g.target_window} ({g.stratum.value}):")
        print(f"  Sequence: {g.guide_sequence}")
        print(f"  Seed: {g.seed_region}")
        print(f"  Pos3: {g.position3_strategy}")
        print(f"  Off-target risk: {g.off_target_risk}")

    elif cmd == "verify" and len(sys.argv) >= 4:
        v = FrobeniusVerifier.verify(sys.argv[2], sys.argv[3])
        print(f"Verification: {v.target_codon} → {v.edit_codon}")
        print(f"  μ∘δ {'CLOSED ✓' if v.frobenius_closed else 'OPEN ✗'}")
        print(f"  Ratio: {v.closure_ratio:.3f}")
        print(f"  δ quality: {v.delta_quality:.3f}, μ quality: {v.mu_quality:.3f}")
        for d in v.defects:
            print(f"  • {d}")

    elif cmd == "chimera" and len(sys.argv) >= 3:
        edits = []
        for pair in sys.argv[2:]:
            parts = pair.split(":")
            if len(parts) == 2:
                edits.append((parts[0], parts[1]))
        r = ChimeraDetector.analyze_edit_set(edits)
        print(f"Chimera analysis: {', '.join(r.edits)}")
        print(f"  Individual risks: {r.individual_risks}")
        print(f"  Tensor risk: {r.tensor_risk:.1f}x")
        print(f"  Classification: {r.tensor_class}")
        print(f"  Trap state: {r.is_trap_state}")
        print(f"  Recommendation: {r.recommendation}")

    elif cmd == "stratum" and len(sys.argv) >= 3:
        s = FrobeniusStratumClassifier.classify(sys.argv[2])
        print(f"Codon {sys.argv[2]}: {s.value} stratum")

    elif cmd == "demo":
        run_all_demo()

    elif cmd == "test":
        run_verification_suite()

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()

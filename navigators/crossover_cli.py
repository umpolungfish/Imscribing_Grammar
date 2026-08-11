#!/usr/bin/env python3
"""
crossover_cli.py — Quantum Advantage Crossover Certification Tool

Standalone CLI packaging of the quantum_tnn.py crossover metric for
the mOMonadOS Fibonacci anyon certification pipeline.

Usage:
  python3 crossover_cli.py --strands N --depth D --gates "H T S X" [--epsilon_2q E]
  python3 crossover_cli.py --braid "3 4 -5 -6 7" --strands 13
  python3 crossover_cli.py --certify --strands 19 --depth 10

Crossover boundary: t_gate × n_gates × ε_2q > 0.1 → classical simulability.
Hardware below this boundary certifies quantum advantage.

Author: Quantum⊙perator (Lando⊗⊙perator team)
"""
import argparse
import json
import sys
from pathlib import Path

# Crossover threshold from quantum_tnn.py: t_gate × n_gates × ε_2q > 0.1
CROSSOVER_THRESHOLD = 0.1

# Hardware profiles for evaluation
HARDWARE_PROFILES = {
    "fibonacci_anyon": {"t_gate": 10e-6, "eps_2q": 1e-4, "name": "Fibonacci Anyon (topological)"},
    "nisq_ibmq": {"t_gate": 200e-9, "eps_2q": 5e-3, "name": "IBM Quantum (NISQ)"},
    "heron": {"t_gate": 100e-9, "eps_2q": 3e-3, "name": "IBM Heron (NISQ)"},
    "surface_code_ft": {"t_gate": 100e-9, "eps_2q": 1e-5, "name": "Surface Code FT"},
}

def compute_crossover_metric(n_gates, t_gate, eps_2q):
    """Compute the crossover metric: t_gate × n_gates × ε_2q"""
    return t_gate * n_gates * eps_2q

def certify_quantum_advantage(n_gates, t_gate, eps_2q):
    """Return (metric, is_advantage) where is_advantage=True if metric < 0.1"""
    metric = compute_crossover_metric(n_gates, t_gate, eps_2q)
    return metric, metric < CROSSOVER_THRESHOLD

def estimate_braid_gates(depth, gate_set_size=4):
    """Estimate braid length from circuit depth (empirical: ~173 generators/depth for HTSX)"""
    # From kernel compilation: depth 12 → 2082 generators ≈ 173.5 per depth
    return int(depth * 173.5)

def run_certification(strands, depth, gate_list, eps_2q=None):
    """Run full quantum advantage certification pipeline."""
    results = {
        "strands": strands,
        "fusion_space_dimension": _fib(strands - 1),
        "depth": depth,
        "gate_set": gate_list,
        "n_gates": estimate_braid_gates(depth),
        "hardware_profiles": {},
    }

    if eps_2q is None:
        eps_2q = 1e-4  # Default to topological error rate

    for hw_key, hw in HARDWARE_PROFILES.items():
        metric, is_adv = certify_quantum_advantage(
            results["n_gates"], hw["t_gate"], hw["eps_2q"]
        )
        results["hardware_profiles"][hw_key] = {
            "t_gate_s": hw["t_gate"],
            "eps_2q": hw["eps_2q"],
            "metric": metric,
            "crossover_threshold": CROSSOVER_THRESHOLD,
            "quantum_advantage": is_adv,
            "verdict": "ADVANTAGE" if is_adv else "CLASSICAL SIMULABLE",
        }

    return results

def _fib(n):
    """Compute Fibonacci number F_n iteratively."""
    if n <= 0: return 1
    if n <= 2: return 1
    a, b = 1, 1
    for _ in range(n - 2):
        a, b = b, a + b
    return b

def main():
    parser = argparse.ArgumentParser(
        description="Quantum Advantage Crossover Certification Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--strands", type=int, default=19,
                        help="Number of Fibonacci anyon strands (default: 19 → 11 qubits)")
    parser.add_argument("--depth", type=int, default=10,
                        help="Circuit depth (default: 10)")
    parser.add_argument("--gates", type=str, default="H T S X",
                        help="Gate set (default: 'H T S X')")
    parser.add_argument("--epsilon_2q", type=float, default=1e-4,
                        help="Two-qubit error rate (default: 1e-4 for topological)")
    parser.add_argument("--braid", type=str,
                        help="Braid word as generator indices (e.g., '3 4 -5 -6 7')")
    parser.add_argument("--certify", action="store_true",
                        help="Run full certification with all hardware profiles")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    gate_list = args.gates.split()
    results = run_certification(args.strands, args.depth, gate_list, args.epsilon_2q)

    if args.braid:
        braid_gates = len([g for g in args.braid.split()])
        results["braid_generators"] = braid_gates
        results["n_gates"] = braid_gates

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 60)
        print("  Quantum Advantage Crossover Certification")
        print("=" * 60)
        print(f"\nSystem Parameters:")
        print(f"  Strands:              {results['strands']}")
        print(f"  Fusion space (F_n):   {results['fusion_space_dimension']}")
        print(f"  Circuit depth:        {results['depth']}")
        print(f"  Gate set:             {results['gate_set']}")
        print(f"  Braid generators:     {results['n_gates']}")

        print(f"\nCrossover Boundary: t_gate × n_gates × ε_2q > {CROSSOVER_THRESHOLD}")
        print(f"  {'Hardware':<28} {'Metric':>12} {'Verdict':>18}")
        print(f"  {'-'*28} {'-'*12} {'-'*18}")
        for hw_key, hw_result in results["hardware_profiles"].items():
            print(f"  {hw_result['name'] if 'name' in hw_result else hw_key:<28} "
                  f"{hw_result['metric']:>12.2e} "
                  f"{hw_result['verdict']:>18}")

        print(f"\nCertification: PASSED" if any(
            h["quantum_advantage"] for h in results["hardware_profiles"].values()
        ) else "\nCertification: FAILED — classical simulability exceeds advantage")

if __name__ == "__main__":
    main()

"""
imscribe_tool.py — Imscribing Grammar as an LLM tool
==============================================
Turns every imscrbgrmr operation into a structured tool call any LLM
can invoke. The LLM cannot hallucinate impossible chemistry: every
proposal is immediately rejected with a precise axiom trace if it fails.

Two surfaces:
  - call_imscribe(op, **kwargs)  — the raw dispatch layer (subprocess → real CLI)
  - IGTool                — the Python API layer (direct imports, faster)

Usage as an LLM tool definition:
    tools = [IG_TOOL_SCHEMA]
    # feed IG_TOOL_SCHEMA to any tool-calling LLM
    # dispatch incoming tool calls to IGTool.dispatch(op, **kwargs)
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import imscrbgrmr  # populate catalog
from imscrbgrmr.algebra import (
    find_path, meet, tensor, tuple_distance,
)
from imscrbgrmr.constraints import AxiomValidator
from imscrbgrmr.registry import global_catalog
from imscrbgrmr.thermodynamics import compute_xi_CP
from imscrbgrmr.varma_probe import VarmaCorrelationData, score_phi_c_candidacy
from imscrbgrmr.domains.molecular import register_molecular_imscriptions
from imscrbgrmr.domains.quantum import register_quantum_imscriptions

register_molecular_imscriptions()
register_quantum_imscriptions()


# ── Response container ─────────────────────────────────────────────────────────

@dataclass
class ToolResponse:
    status: str                             # "ok" | "violation" | "blocked" | "error"
    notation: Optional[str] = None
    catalog_name: Optional[str] = None     # registered catalog name (generate only)
    axiom_report: Optional[Dict[str, Any]] = None
    xi_cp: Optional[float] = None
    phi_c_score: Optional[float] = None
    phi_c_label: Optional[str] = None
    path: Optional[List[str]] = None
    path_hops: Optional[int] = None
    path_delta_xi: Optional[float] = None
    analogs: Optional[List[Dict]] = None
    distance: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ── CLI passthrough (for generate, which uses LLM internally) ─────────────────

def _cli(args: List[str], timeout: int = 60) -> str:
    """Run a imscribe CLI command and return stdout. Raises on non-zero exit."""
    r = subprocess.run(
        ["imscribe"] + args,
        capture_output=True, text=True, timeout=timeout, check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    return r.stdout.strip()


# ── Core Python-API tool ───────────────────────────────────────────────────────

class IGTool:
    """
    Thin, real dispatch layer for LLM tool calls.
    All operations run against the live imscrbgrmr Python API — no mock,
    no extrapolation. The LLM gets back what the algebra actually says.
    """

    @staticmethod
    def validate(name: str) -> ToolResponse:
        """
        Run full axiom validation on a registered catalog entry.
        Returns the axiom report and notation.
        """
        imscription = global_catalog.get(name)
        if imscription is None:
            return ToolResponse(status="error", error=f"'{name}' not in catalog")
        report = AxiomValidator.validate_all_axioms(imscription)
        all_ok = all(v for k, v in report.items() if k.startswith("axiom"))
        return ToolResponse(
            status="ok" if all_ok else "violation",
            notation=imscription.to_notation(),
            axiom_report=report,
            notes=[] if all_ok else [f"Failed: {[k for k,v in report.items() if k.startswith('axiom') and not v]}"],
        )

    @staticmethod
    def criticality(name: str,
                    xi_r: Optional[float] = None,
                    xi_tau: Optional[float] = None) -> ToolResponse:
        """
        Varma probe: ⊙ candidacy score and G/D degeneracy for a catalog entry.
        xi_r and xi_tau are optional correlation length / correlation time inputs.
        """
        imscription = global_catalog.get(name)
        if imscription is None:
            return ToolResponse(status="error", error=f"'{name}' not in catalog")
        corr = VarmaCorrelationData(xi_r=xi_r, xi_tau=xi_tau) if (xi_r or xi_tau) else None
        report = score_phi_c_candidacy(imscription, corr)
        try:
            xi_cp_val = compute_xi_CP(imscription, delta_g=-50.0)
        except Exception:
            xi_cp_val = None
        return ToolResponse(
            status="ok",
            notation=imscription.to_notation(),
            phi_c_score=report.score,
            phi_c_label=report._candidacy_label(),
            xi_cp=xi_cp_val,
            axiom_report={
                "gd_degenerate": report.gd_degenerate,
                "universality_class": report.universality_class,
                "axiom5_satisfied": report.axiom5_satisfied,
                "recommendation": report.recommendation,
            },
        )

    @staticmethod
    def path(src: str, dst: str,
             max_hops: int = 6,
             xi_tolerance: float = 1.0) -> ToolResponse:
        """
        HotSwap path from src to dst through the catalog.
        Both must be registered catalog entries OR notation strings
        matching registered entries.
        """
        s_src = global_catalog.get(src)
        s_dst = global_catalog.get(dst)
        if s_src is None:
            return ToolResponse(status="error", error=f"'{src}' not in catalog")
        if s_dst is None:
            return ToolResponse(status="error", error=f"'{dst}' not in catalog")
        catalog = global_catalog.search()
        result = find_path(s_src, s_dst, catalog,
                           max_hops=max_hops, xi_tolerance=xi_tolerance)
        if result.found:
            return ToolResponse(
                status="ok",
                path=result.path,
                path_hops=result.n_hops,
                path_delta_xi=result.total_delta,
                notes=[f"hop {i+1}: {name} (Δξ={d:+.3f})"
                       for i, (name, d) in enumerate(zip(result.path[1:], result.hop_deltas))],
            )
        return ToolResponse(
            status="blocked",
            notes=result.notes or ["no path in HotSwap graph"],
        )

    @staticmethod
    def analogies(name: str, limit: int = 5) -> ToolResponse:
        """
        Find the top catalog analogs to a registered imscription by tuple distance.
        """
        imscription = global_catalog.get(name)
        if imscription is None:
            return ToolResponse(status="error", error=f"'{name}' not in catalog")
        catalog = global_catalog.search()
        ranked = sorted(
            [(s, tuple_distance(imscription, s)) for s in catalog if s.name != name],
            key=lambda x: x[1],
        )[:limit]
        return ToolResponse(
            status="ok",
            notation=imscription.to_notation(),
            analogs=[{"name": s.name, "distance": round(d, 3)} for s, d in ranked],
        )

    @staticmethod
    def distance(a: str, b: str) -> ToolResponse:
        """Symmetric and directed distances between two catalog entries."""
        sa = global_catalog.get(a)
        sb = global_catalog.get(b)
        if sa is None:
            return ToolResponse(status="error", error=f"'{a}' not in catalog")
        if sb is None:
            return ToolResponse(status="error", error=f"'{b}' not in catalog")
        d_sym = tuple_distance(sa, sb)
        d_ab  = tuple_distance(sa, sb, symmetric=False)
        d_ba  = tuple_distance(sb, sa, symmetric=False)
        return ToolResponse(
            status="ok",
            distance=d_sym,
            notes=[
                f"d(symmetric) = {d_sym:.3f}",
                f"d({a}→{b}) = {d_ab:.3f}",
                f"d({b}→{a}) = {d_ba:.3f}",
                f"asymmetry = {abs(d_ab-d_ba):.3f}  (easier: {'→' if d_ab < d_ba else '←'})",
            ],
        )

    @staticmethod
    def meet_pair(a: str, b: str) -> ToolResponse:
        """
        Lattice meet of two catalog entries — shared primitive floor.
        CONFLICT fields identify the state-switching primitives.
        """
        sa = global_catalog.get(a)
        sb = global_catalog.get(b)
        if sa is None:
            return ToolResponse(status="error", error=f"'{a}' not in catalog")
        if sb is None:
            return ToolResponse(status="error", error=f"'{b}' not in catalog")
        m = meet(sa, sb)
        return ToolResponse(
            status="ok",
            notation=m.to_notation(),
            notes=(
                [f"State-switching primitives (CONFLICT): {m.conflicts}"]
                if m.conflicts
                else ["No conflicts — states differ only in ordered primitives."]
            ),
        )

    @staticmethod
    def generate(description: str,
                 name: Optional[str] = None,
                 axiom_guided: bool = True,
                 delta_g: Optional[float] = None,
                 provider: Optional[str] = None,
                 model: Optional[str] = None) -> ToolResponse:
        """
        Generate a imscription from a natural-language description via imscribe CLI.
        Uses --axiom-guided by default so the LLM proposal is immediately
        validated and re-proposed until all axioms pass.
        provider and model are forwarded to the underlying imscribe generate command.
        """
        args = ["generate", description]
        if name:
            args += ["--name", name]
        if axiom_guided:
            args.append("--axiom-guided")
        if delta_g is not None:
            args += ["--delta-g", str(delta_g)]
        if provider:
            args += ["--provider", provider]
        if model:
            args += ["--model", model]
        try:
            output = _cli(args, timeout=120)
            # Parse notation
            notation = None
            for line in output.splitlines():
                if "⟨" in line and "⟩" in line:
                    notation = line.strip()
                    break
            # Parse registered catalog name from "✓ Registered to catalog as '<name>'"
            catalog_name = None
            for line in output.splitlines():
                if "Registered to catalog as" in line:
                    # strip ANSI escape codes, then extract name between quotes
                    import re as _re
                    clean = _re.sub(r"\x1b\[[0-9;]*m", "", line)
                    m = _re.search(r"Registered to catalog as '([^']+)'", clean)
                    if m:
                        catalog_name = m.group(1)
                    break
            # Reload parent-process catalog so the new entry is visible to
            # subsequent validate/criticality/path calls in this process.
            if catalog_name and global_catalog._storage_path:
                try:
                    global_catalog._load_into_self(global_catalog._storage_path)
                except Exception:
                    pass  # non-fatal — catalog_name still returned to agent

            return ToolResponse(
                status="ok",
                notation=notation,
                catalog_name=catalog_name,
                notes=[output],
            )
        except RuntimeError as e:
            return ToolResponse(status="violation", error=str(e))

    @classmethod
    def dispatch(cls, operation: str, **kwargs) -> ToolResponse:
        """
        Single entry point for LLM tool dispatch.
        operation ∈ {validate, criticality, path, analogies,
                      distance, meet, generate}
        """
        ops = {
            "validate":    cls.validate,
            "criticality": cls.criticality,
            "path":        cls.path,
            "analogies":   cls.analogies,
            "distance":    cls.distance,
            "meet":        cls.meet_pair,
            "generate":    cls.generate,
        }
        fn = ops.get(operation)
        if fn is None:
            return ToolResponse(
                status="error",
                error=f"Unknown operation '{operation}'. Valid: {list(ops)}",
            )
        try:
            return fn(**kwargs)
        except TypeError as e:
            return ToolResponse(status="error", error=f"Bad arguments for '{operation}': {e}")


# ── LLM tool schema (OpenAI / Anthropic / any tool-calling API) ────────────────

IG_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "imscrbgrmr",
        "description": (
            "Verify, probe, and compose imscriptions using the Imscribing Grammar relational "
            "grammar. Enforces 7 composition axioms, ⊙ criticality probes, ξ_CP "
            "efficiency, HotSwap paths, and cross-domain analogies. "
            "NEVER invent chemistry outside the algebra — use this tool first."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["validate", "criticality", "path",
                             "analogies", "distance", "meet", "generate"],
                    "description": (
                        "validate: axiom check on catalog entry. "
                        "criticality: ⊙ / Varma probe. "
                        "path: HotSwap path between two entries. "
                        "analogies: nearest catalog neighbors. "
                        "distance: symmetric + directed distances. "
                        "meet: shared primitive floor (state-switching levers). "
                        "generate: propose + validate from natural language — "
                        "result includes catalog_name with the exact registered name "
                        "to use in subsequent criticality/path/analogies calls."
                    ),
                },
                "name":        {"type": "string",  "description": "Catalog entry name (most operations)."},
                "src":         {"type": "string",  "description": "Source entry for path."},
                "dst":         {"type": "string",  "description": "Destination entry for path."},
                "a":           {"type": "string",  "description": "First entry for distance / meet."},
                "b":           {"type": "string",  "description": "Second entry for distance / meet."},
                "description": {"type": "string",  "description": "Natural-language description for generate."},
                "xi_r":        {"type": "number",  "description": "Spatial correlation length for criticality probe."},
                "xi_tau":      {"type": "number",  "description": "Temporal correlation length for criticality probe."},
                "limit":       {"type": "integer", "description": "Max analogies to return (default 5)."},
                "max_hops":    {"type": "integer", "description": "Max HotSwap hops (default 6)."},
                "delta_g":     {"type": "number",  "description": "ΔG (kJ/mol) for generate."},
                "axiom_guided":{"type": "boolean", "description": "Enforce axioms during generate (default true)."},
                "provider":    {"type": "string",  "description": "LLM provider for generate (e.g. 'anthropic', 'deepseek')."},
                "model":       {"type": "string",  "description": "Model ID for generate (overrides provider default)."},
            },
            "required": ["operation"],
        },
    },
}


# ── Quick smoke test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "allosteric_domain"

    print("=== distance ===")
    r = IGTool.distance("allosteric_domain", "active_site")
    print(r.to_json())

    print("\n=== criticality ===")
    r = IGTool.criticality("allosteric_domain", xi_r=8.5, xi_tau=1e10)
    print(r.to_json())

    print("\n=== analogies ===")
    r = IGTool.analogies("allosteric_domain", limit=3)
    print(r.to_json())

    print("\n=== TOOL SCHEMA (first 300 chars) ===")
    print(json.dumps(IG_TOOL_SCHEMA)[:300])

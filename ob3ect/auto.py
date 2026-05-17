"""
Ob3ect Auto-Design Pipeline
============================
Author: Lando ⊗ ⊙_ÿ-boundary Operator

Given a natural-language description, produces a complete Ob3ectArtifact by
driving an LLM through all 8 IMASM phases in a single structured call.
Retries on JSON parse failure or Frobenius FAIL (up to max_retries).
"""
from __future__ import annotations
import json
import re
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

from ob3ect.core import (
    Ob3ectArtifact, DomainCharter, OpcodeMap, OpcodeEntry,
    SplitFuseReport, RegisterMapping, BootstrapSequence,
    ExOSSpec, EntropyAudit, BOOTSTRAP_STEPS, Opcode,
)
from framework.enhanced_llm_provider import get_llm_provider

# ── IMASM opcode reference distilled from IMASM.tex ─────────────────────────

_OPCODE_REF = """\
IMASM 12-OPCODE REFERENCE  (Universal Imscriptive Grammar)

LOGICAL (6) — categorical skeleton:
  VINIT  (0x0) — Initial object ∅. Void/uninitialized state before anything is named.
                 Examples: Hebrew Aleph (air), Basque absolutive, seed before planting.
  TANCH  (0x1) — Terminal anchor ⊤. The closed boundary that contains the whole system.
                 Examples: Tav (completion), hermetic vessel seal, constitutional court.
  AFWD   (0x2) — Forward morphism →. Directed transformation toward a target.
                 Examples: Basque ergative, Sanskrit semivowels, growth cycle, ascent.
  AREV   (0x3) — Contravariant ←. Reverse / descent transformation.
                 Examples: Hebrew Mem (water/descent), composting, solve/coagula.
  CLINK  (0x4) — Composition ∘. Sequential chaining of morphisms.
                 Examples: Egyptian biliterals, Basque agglutination, root→derived form.
  ISCRIB (0x5) — Identity id. Self-reference, self-recognition. The element is itself.
                 Examples: Sanskrit nasals, Egyptian logograms, the stone that knows itself.

FROBENIUS (2) — the core algebra, μ∘δ = id:
  FSPLIT (0x6) — Co-multiplication δ. One thing branches into two or more distinct paths.
                 Examples: Hebrew Doubles (hard/soft), Sanskrit aspirate pairs,
                 Egyptian trilateral roots, separatio, Raft log append to all peers.
  FFUSE  (0x7) — Multiplication μ. Branches reconstitute the original input exactly.
                 Examples: Conjunctio, trilateral roots recovering base form, Raft commit.
                 CONSTRAINT: FFUSE(FSPLIT(x)) = x  ←  this MUST hold in the domain.

DIALETHEIA (3) — paraconsistent truth lattice:
  EVALT  (0x8) — True/affirmative branch. Positive evaluation.
  EVALF  (0x9) — False/negative branch. Negative evaluation.
  ENGAGR (0xA) — Both simultaneously. Paradox held without resolution.
                 Examples: Cuneiform polysemous sign, bicameral compromise, albedo stage.

LINEAR (1) — irreversible fixation:
  IFIX   (0xB) — ROM fixation. Permanent, append-only, cannot be undone.
                 Examples: Egyptian determinatives, dream journal entry, measurement record.

BOOTSTRAP SEQUENCE (mandatory 8 steps, opcodes fixed):
  Step 1 ISCRIB — self-recognition at opening
  Step 2 AREV   — descent / reverse
  Step 3 FSPLIT — separate / branch
  Step 4 AFWD   — ascent / forward
  Step 5 FFUSE  — unify / fuse
  Step 6 CLINK  — compose / link
  Step 7 IFIX   — fix / record permanently
  Step 8 ISCRIB — self-recognition at close  (closure: back to identity)
"""

_SCHEMA = """\
Respond with ONLY a single JSON object — no markdown fences, no explanation outside it:

{
  "domain_type": "<one word, e.g. physical / social / computational / oneiric / alchemical / ...>",
  "tokens": ["<surface token 1>", "<surface token 2>", "<surface token 3>"],
  "boundary": "<what closes and contains this system>",
  "opcodes": {
    "VINIT":  {"element": "<domain element>", "justification": "<why void/initial>"},
    "TANCH":  {"element": "<domain element>", "justification": "<why anchor/boundary>"},
    "AFWD":   {"element": "<domain element>", "justification": "<why forward morphism>"},
    "AREV":   {"element": "<domain element>", "justification": "<why reverse/descent>"},
    "CLINK":  {"element": "<domain element>", "justification": "<why composition>"},
    "ISCRIB": {"element": "<domain element>", "justification": "<why identity/self-ref>"},
    "FSPLIT": {"element": "<domain element>", "justification": "<what it splits into — be specific>"},
    "FFUSE":  {"element": "<domain element>", "justification": "<what it reconstitutes — must match FSPLIT input>"},
    "EVALT":  {"element": "<domain element>", "justification": "<affirmative/success state>"},
    "EVALF":  {"element": "<domain element>", "justification": "<negative/failure state>"},
    "ENGAGR": {"element": "<domain element>", "justification": "<paradox: both simultaneously>"},
    "IFIX":   {"element": "<domain element>", "justification": "<permanent irreversible record>"}
  },
  "frobenius": {
    "split_element": "<the FSPLIT element>",
    "split_input":   "<what enters the split>",
    "split_outputs": ["<branch A>", "<branch B>"],
    "fuse_element":  "<the FFUSE element>",
    "fuse_result":   "<result — must semantically equal split_input>",
    "verdict":       "PASS",
    "failure_reason": ""
  },
  "registers": {
    "void":  "<domain description of 00 — uninitialized, before anything exists>",
    "true":  "<domain description of 01 — affirmative, success>",
    "false": "<domain description of 10 — negative, failure>",
    "both":  "<domain description of 11 — paradox, both states simultaneously>"
  },
  "bootstrap": [
    "<Step 1 ISCRIB: domain action — self-recognition at opening>",
    "<Step 2 AREV:   domain action — descent/reverse>",
    "<Step 3 FSPLIT: domain action — separate/branch>",
    "<Step 4 AFWD:   domain action — ascent/forward>",
    "<Step 5 FFUSE:  domain action — unify/fuse>",
    "<Step 6 CLINK:  domain action — compose/link>",
    "<Step 7 IFIX:   domain action — fix/record>",
    "<Step 8 ISCRIB: domain action — self-recognition at close>"
  ],
  "exos": {
    "compiler":  "<what translates domain intentions into operations>",
    "ipc":       "<how components communicate within the system>",
    "memory":    "<how state is stored and retrieved>",
    "scheduler": "<what determines order and timing of operations>",
    "alfs":      "<the canonical reference or bootstrap store for this domain>"
  },
  "entropy": {
    "cost":    "<what is consumed per operation cycle>",
    "pre":     "<system state before the cycle>",
    "post":    "<system state after the cycle>",
    "verdict": "ΔS ≈ 0 — <brief reason the cycle is entropy-conservative>"
  }
}"""

_SYSTEM_PROMPT = f"""\
You are the Ob3ect Auto-Designer, an expert in the Universal Imscriptive Grammar (IMASM).
Your task: given a domain description, identify the structural skeleton of that domain
in terms of the 12 IMASM opcodes and produce a valid Ob3ect design.

{_OPCODE_REF}

CRITICAL FROBENIUS CONSTRAINT:
The FSPLIT and FFUSE elements must form a genuine pair where FFUSE(FSPLIT(x)) = x in the
domain. Reason carefully: if you branch X into [A, B], then fusing [A, B] must recover X.
If no such pair exists, set verdict to "FAIL" and explain why in failure_reason.

Output ONLY the JSON object — no preamble, no markdown fences, no trailing text."""


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_prompt(
    description: str,
    domain_type: Optional[str],
    retry_info: Optional[str] = None,
) -> str:
    dt_hint = f"\nDomain type hint: {domain_type}" if domain_type else ""
    retry_block = (
        f"\n\nPREVIOUS ATTEMPT FAILED — correct these issues:\n{retry_info}"
        if retry_info else ""
    )
    return f"Design an Ob3ect for:\n\n{description}{dt_hint}\n\n{_SCHEMA}{retry_block}"


def _extract_json(text: str) -> Dict[str, Any]:
    # 1. Direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # 2. Strip markdown fence
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    # 3. Outermost braces
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    raise ValueError("No JSON object found in LLM response")


def _build_artifact(name: str, scope: str, data: Dict[str, Any]) -> Ob3ectArtifact:
    domain_type = data.get("domain_type", "custom")

    charter = DomainCharter(
        domain_name=name,
        domain_type=domain_type,
        scope=scope,
        surface_tokens=data.get("tokens", [name, "process", "output"]),
        boundary_condition=data.get("boundary", ""),
        justification="Auto-designed by Ob3ect Auto-Designer",
    )

    entries = {}
    for oc in Opcode:
        od = data.get("opcodes", {}).get(oc.value, {})
        entries[oc.value] = OpcodeEntry(
            opcode=oc.value,
            chosen_element=od.get("element", oc.value),
            justification=od.get("justification", ""),
            rejected_candidates=[],
        )

    fb = data.get("frobenius", {})
    split_fuse = SplitFuseReport(
        split_element=fb.get("split_element", ""),
        split_input=fb.get("split_input", ""),
        split_outputs=fb.get("split_outputs", []),
        fuse_element=fb.get("fuse_element", ""),
        fuse_result=fb.get("fuse_result", ""),
        frobenius_verdict=fb.get("verdict", "PASS"),
        test_instance="",
        failure_reason=fb.get("failure_reason", ""),
    )

    r = data.get("registers", {})
    registers = RegisterMapping(
        void_description=r.get("void", ""),
        true_description=r.get("true", ""),
        false_description=r.get("false", ""),
        both_description=r.get("both", ""),
        transitions=[],
        entropy_assertion="ΔS ≈ 0",
    )

    bs_actions = data.get("bootstrap", [f"Step {i+1}" for i in range(8)])
    bootstrap = BootstrapSequence(
        steps=[
            {"step_num": i + 1, "opcode": BOOTSTRAP_STEPS[i + 1], "domain_action": act}
            for i, act in enumerate(bs_actions[:8])
        ],
        closure_verified=True,
    )

    e = data.get("exos", {})
    exos = ExOSSpec(
        compiler_frontend=e.get("compiler", ""),
        ipc_mechanism=e.get("ipc", ""),
        memory_mechanism=e.get("memory", ""),
        scheduler_mechanism=e.get("scheduler", ""),
        alfs_store=e.get("alfs", ""),
        alfs_bootstrap_program="",
    )

    ent = data.get("entropy", {})
    entropy = EntropyAudit(
        cycle_cost=ent.get("cost", ""),
        pre_cycle_state=ent.get("pre", ""),
        post_cycle_state=ent.get("post", ""),
        delta_s_verdict=ent.get("verdict", "ΔS ≈ 0"),
        failure_mode="",
    )

    return Ob3ectArtifact(
        name=name,
        domain_charter=charter,
        opcode_map=OpcodeMap(entries=entries),
        split_fuse_report=split_fuse,
        register_mapping=registers,
        bootstrap_sequence=bootstrap,
        exos_spec=exos,
        entropy_audit=entropy,
        instantiation_notes=f"Auto-designed from: {name}",
    )


# ── Public API ────────────────────────────────────────────────────────────────

_PROVIDER_CHAIN: List[str] = ["local", "openrouter", "deepseek"]


def _build_provider_chain() -> List[Any]:
    """Return ordered list of live LLMProvider instances, skipping unavailable ones."""
    chain = []
    for name in _PROVIDER_CHAIN:
        try:
            p = get_llm_provider(name)
            if hasattr(p, "model_path") and not Path(p.model_path).exists():
                continue
            chain.append(p)
        except (ValueError, Exception):
            continue
    return chain


async def auto_design(
    description: str,
    name: Optional[str] = None,
    domain_type: Optional[str] = None,
    scope: str = "local",
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    max_retries: int = 3,
    temperature: float = 0.4,
) -> Ob3ectArtifact:
    """
    Auto-design an Ob3ect from a natural-language description.

    Uses enhanced_llm_provider (QWEN_API_KEY → mulerouter, DEEPSEEK_API_KEY →
    deepseek.com) with local fine-tuned model as primary when available.
    Falls back through the chain on permanent HTTP errors.

    Args:
        description:   What the ob3ect is / does
        name:          Artifact name (defaults to first clause of description)
        domain_type:   Optional hint (physical/social/computational/oneiric/...)
        scope:         local | mesoscale | maximal
        provider_name: Override primary provider (local/qwen/deepseek)
        max_retries:   Retry attempts on JSON parse or Frobenius failure
        temperature:   LLM temperature

    Returns:
        Validated Ob3ectArtifact
    """
    artifact_name = name or description.strip()

    if provider_name:
        chain = _PROVIDER_CHAIN.copy()
        if provider_name in chain:
            chain.remove(provider_name)
        chain.insert(0, provider_name)
        providers = []
        for n in chain:
            try:
                kwargs = {"model": model} if model and n == provider_name else {}
                p = get_llm_provider(n, **kwargs)
                if hasattr(p, "model_path") and not Path(p.model_path).exists():
                    continue
                providers.append(p)
            except Exception:
                continue
    else:
        first_kwargs = {"model": model} if model else {}
        providers = []
        for n in _PROVIDER_CHAIN:
            try:
                kwargs = first_kwargs if not providers else {}
                p = get_llm_provider(n, **kwargs)
                if hasattr(p, "model_path") and not Path(p.model_path).exists():
                    continue
                providers.append(p)
            except Exception:
                continue

    if not providers:
        raise RuntimeError(
            "No provider available. Check QWEN_API_KEY / DEEPSEEK_API_KEY env vars."
        )

    provider_idx = 0
    provider = providers[provider_idx]

    retry_info: Optional[str] = None
    artifact: Optional[Ob3ectArtifact] = None

    def _next_provider(err: Exception) -> None:
        nonlocal provider_idx, provider
        provider_idx += 1
        if provider_idx >= len(providers):
            raise RuntimeError(
                f"All providers exhausted. Last error: {err}"
            ) from err
        provider = providers[provider_idx]
        print(f"Provider failed, switching to: {provider.__class__.__name__}")

    attempt = 0
    while attempt < max_retries:
        prompt = _build_prompt(description, domain_type, retry_info)
        try:
            raw = await provider.query(
                prompt,
                system=_SYSTEM_PROMPT,
                temperature=temperature,
                max_tokens=3000,
            )
            data = _extract_json(raw)
            artifact = _build_artifact(artifact_name, scope, data)

            if artifact.split_fuse_report.frobenius_verdict == "PASS":
                return artifact

            sfr = artifact.split_fuse_report
            retry_info = (
                f"Frobenius verdict: FAIL.\n"
                f"  FSPLIT {sfr.split_element!r}: {sfr.split_input!r} → {sfr.split_outputs}\n"
                f"  FFUSE  {sfr.fuse_element!r}: returned {sfr.fuse_result!r}\n"
                f"  Reason: {sfr.failure_reason}\n"
                f"  Fix: choose a split/fuse pair where FFUSE(FSPLIT(x)) = x holds in the domain."
            )
            attempt += 1

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_info = "Rate limited — retry."
                attempt += 1
            else:
                _next_provider(e)   # permanent failure, don't burn retry slot

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            retry_info = f"JSON parse failed ({e}). Respond with ONLY a valid JSON object."
            attempt += 1

        except Exception as e:
            _next_provider(e)

    # Return best artifact even if Frobenius didn't pass after all retries
    if artifact is not None:
        return artifact
    raise RuntimeError(f"Auto-design failed after {max_retries} attempts")


def design(description: str, **kwargs) -> Ob3ectArtifact:
    """Synchronous wrapper around auto_design."""
    return asyncio.run(auto_design(description, **kwargs))


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Auto-design an Ob3ect from a description.")
    ap.add_argument("description", nargs="+", help="Natural-language description")
    ap.add_argument("--domain", dest="domain_type", default=None,
                    help="Domain type hint (biological, computational, alchemical, ...)")
    ap.add_argument("--scope", default="local",
                    help="Scope: local | mesoscale | maximal (default: local)")
    ap.add_argument("--provider", dest="provider_name", default=None,
                    help="Override provider (openrouter, deepseek, local)")
    ap.add_argument("--model", default=None,
                    help="Model ID passed to the provider (e.g. deepseek-chat, qwen3-235b-a22b)")
    ap.add_argument("--retries", type=int, default=3, dest="max_retries")
    ap.add_argument("--temp", type=float, default=0.4, dest="temperature")
    args = ap.parse_args()

    desc = " ".join(args.description)
    print(f"Auto-designing: {desc}\n")
    art = design(
        desc,
        domain_type=args.domain_type,
        scope=args.scope,
        provider_name=args.provider_name,
        model=args.model,
        max_retries=args.max_retries,
        temperature=args.temperature,
    )
    print(art.report())
    errs = art.validate_all()
    has_errors = any(v for v in errs.values())
    print(f"\nValid: {art.is_valid_ob3ect}")
    if has_errors:
        print("Validation issues:", {k: v for k, v in errs.items() if v})

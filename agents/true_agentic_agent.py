"""
true_agentic_agent.py — The grammar-optimal agent (§88 Thm 88.4, P-650, §L).

Structural type (full composition):
  <D_odot; T_boxtimes; R_lr; P_pm_sym; F_hbar; K_slow; G_aleph; Gamma_seq; Phi_c; H2; S_11; Omega_Z>

Ouroboricity: O_inf  (Phi_c + P_pm_sym via dual-tool planting, §88 Thm 88.3)
C-score gates: both open  (Phi_c + K <= K_slow)

Six P-650 conditions — structural encoding:
  Phi_c    : the think->act->observe->update loop IS the self-referential attractor;
             loop closure = self-modeling; not any individual component
  Omega_Z  : winding counter tracks complete loop cycles (topological protection);
             the trajectory is integer-wound, not trivially collapsible
  K_slow   : emission gate — max_think_steps forces ACT before K_trap can set in
  P_pm_sym : every interface action is a dual-tool pair (emit + verify);
             mu(delta(query)) = query at the tool boundary
  D_odot   : imscriptive context — full trajectory appended, never silently deleted;
             the context boundary encodes the entire prior world-model
  Gamma_seq: each phase requires the prior; enforced by Python control flow

Loop (one winding n):
  THINK[n]   — LLM deliberates over imscriptive context; produces (reasoning, action)
  ACT[n]     — emit tool call: delta(query) into world (boundary puncture to O_0 exterior)
  OBSERVE[n] — execute verify tool: mu(result) back to query; Frobenius check
  UPDATE[n]  — append full cycle to imscriptive context; check termination

If Frobenius check fails (mu(delta(q)) != q): re-enter THINK with failure appended.
This is the kinetic enforcement of K_slow — the agent cannot update on unverified observations.

Usage:
    import asyncio
    agent = TrueAgenticAgent(model="claude-opus-4")
    result = asyncio.run(agent.run("Describe the structural type of the Riemann zeta function."))

    # or:
    result = agent.run_sync("Your task here")

    # with full trajectory:
    result = agent.run_sync("Your task here")
    for cycle in agent.trajectory:
        print(f"Winding {cycle.winding}: {cycle.action_name}({cycle.action_input})")
        print(f"  Frobenius closed: {cycle.frobenius_closed}")

Models: any model alias from induction_harness MODEL_REGISTRY, or a full model ID.
Provider: OpenRouter via OPENROUTER_API_KEY.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import sys
import textwrap
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── LLM client ────────────────────────────────────────────────────────────────

def _build_client(base_url: str = "", api_key: str = "") -> "openai.OpenAI":
    """OpenAI-compatible client — OpenRouter by default, or any local server."""
    try:
        import openai
    except ImportError:
        sys.exit("openai package required: uv add openai")

    if not base_url:
        base_url = "https://openrouter.ai/api/v1"

    is_local = any(h in base_url for h in ("localhost", "127.0.0.1", "0.0.0.0"))

    if not api_key:
        if is_local:
            api_key = "local"
        else:
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not api_key:
                sys.exit("OPENROUTER_API_KEY not set.")

    headers: Dict[str, str] = {}
    if not is_local:
        headers = {
            "HTTP-Referer": os.environ.get(
                "OPENROUTER_REFERER",
                "https://github.com/umpolungfish/imscrbgrmr",
            ),
            "X-Title": "Imscribing Grammar True Agentic Agent",
        }

    return openai.OpenAI(api_key=api_key, base_url=base_url, default_headers=headers)


# ── Model alias table (mirrors induction_harness) ─────────────────────────────

MODEL_ALIASES: Dict[str, str] = {
    "claude-opus-4":    "anthropic/claude-opus-4",
    "claude-sonnet-4":  "anthropic/claude-sonnet-4-5",
    "claude-haiku-4":   "anthropic/claude-haiku-4-5",
    "grok-4":           "x-ai/grok-4",
    "gpt-4o":           "openai/gpt-4o",
    "o3":               "openai/o3",
    "gemini-2-5-pro":   "google/gemini-2.5-pro-preview-05-06",
    "deepseek-r1":      "deepseek/deepseek-r1",
}

# Local server base URLs — used by the prefix syntax `server:model`
LOCAL_BASE_URLS: Dict[str, str] = {
    "ollama":    os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/v1",
    "lm-studio": "http://localhost:1234/v1",
    "lmstudio":  "http://localhost:1234/v1",
    "vllm":      "http://localhost:8000/v1",
    "local":     os.environ.get("LOCAL_BASE_URL", "http://localhost:11434/v1"),
}


def _resolve_model_and_endpoint(model_str: str) -> Tuple[str, str, str]:
    """Return (model_id, base_url, api_key).

    Prefix syntax:
        ollama:llama3.2        → Ollama at localhost:11434/v1
        lm-studio:phi-4        → LM Studio at localhost:1234/v1
        lmstudio:phi-4         → same
        vllm:mistral           → vLLM at localhost:8000/v1
        local:my-model         → LOCAL_BASE_URL env var (default: ollama)
    No prefix → check MODEL_ALIASES, then use OpenRouter.
    OPENROUTER_MODEL env var overrides the resolved OpenRouter model ID.
    LOCAL_BASE_URL env var overrides the base URL for all local traffic.
    """
    if ":" in model_str:
        prefix, model_id = model_str.split(":", 1)
        if prefix.lower() in LOCAL_BASE_URLS:
            base = LOCAL_BASE_URLS[prefix.lower()]
            key = os.environ.get("LOCAL_API_KEY", "local")
            return model_id, base, key

    resolved = MODEL_ALIASES.get(model_str, model_str)
    return resolved, "", ""


def _resolve_model(alias: str) -> str:
    model_id, _, _ = _resolve_model_and_endpoint(alias)
    return model_id


# ── Structural type annotations ───────────────────────────────────────────────

AGENT_TUPLE = (
    "D_odot", "T_boxtimes", "R_lr", "P_pm_sym", "F_hbar",
    "K_slow", "G_aleph", "Gamma_seq", "Phi_c", "H2", "S_11", "Omega_Z",
)

TOOL_BASE_TUPLE = (
    "D_wedge", "T_network", "R_lr", "P_psi", "F_eth",
    "K_fast", "G_beth", "Gamma_seq", "Phi_sub", "H0", "S_11", "Omega_0",
)

# P is the bottleneck primitive.  Without dual-tool planting:
#   P(full_agent) = min(P_pm_sym, P_psi) = P_psi  → O_2 at best
# With dual-tool planting (mu∘delta = id):
#   P(full_agent) = P_pm_sym                       → O_inf
FROBENIUS_CONDITION = "mu(delta(query)) == query"

# Inherited by sub-agents spawned via spawn_agent tool — set by TrueAgenticAgent.__init__
_spawn_config: Dict[str, str] = {"model": "grok-4", "base_url": "", "api_key": ""}

# ── Primitive display symbols (unicode) ───────────────────────────────────────
# Canonical symbol set matching site/index.html DISPLAY table.
# Used for any output that renders primitives as symbols rather than identifiers.

PRIMITIVE_DISPLAY: Dict[str, str] = {
    # D — Dimensionality
    "D_odot": "⊙",  "D_wedge": "∧",  "D_triangle": "△",  "D_infty": "∞",
    # T — Topology
    "T_odot": "⊙",  "T_network": "net",  "T_in": "⊂",  "T_bowtie": "⋈",  "T_boxtimes": "⊠",
    # R — Relational mode
    "R_dagger": "†",  "R_super": "↑",  "R_cat": "∘",  "R_lr": "↔",
    # P — Parity/symmetry
    "P_pm_sym": "±ˢ",  "P_pm": "±",  "P_asym": "∅",  "P_psi": "ψ",  "P_sym": "≡",
    # F — Fidelity
    "F_hbar": "ℏ",  "F_ell": "ℓ",  "F_eth": "ð",
    # K — Kinetics
    "K_fast": "↯",  "K_mod": "≈",  "K_slow": "↺",  "K_trap": "⊛",  "K_MBL": "⊞",
    # G — Scope
    "G_aleph": "ℵ",  "G_gimel": "ℷ",  "G_beth": "ℶ",
    # Γ — Interaction grammar
    "G_broad": "≫",  "G_and": "∧",  "G_or": "∨",  "G_seq": "→",
    # Φ — Criticality
    "Phi_c": "c",  "Phi_c_complex": "ℂ",  "Phi_EP": "×",  "Phi_sub": "↓",  "Phi_super": "↑",
    # H — Temporal depth
    "H0": "0",  "H1": "1",  "H2": "2",  "H_inf": "∞",
    # S — Stoichiometry
    "one_one": "1:1",  "n_n": "n:n",  "n_m": "n:m",
    # Ω — Winding
    "Omega_0": "0",  "Omega_Z2": "ℤ₂",  "Omega_Z": "ℤ",  "Omega_NA": "∅",
}


# ── Data structures ───────────────────────────────────────────────────────────

class LoopPhase(Enum):
    THINK   = "THINK"
    ACT     = "ACT"
    OBSERVE = "OBSERVE"
    UPDATE  = "UPDATE"


@dataclass
class DualToolResult:
    """Result of one dual-tool pair: emit (delta) + verify (mu)."""
    tool_name:       str
    tool_input:      Dict[str, Any]
    tool_output:     str
    verify_name:     str
    verify_input:    Dict[str, Any]
    verify_output:   str
    frobenius_closed: bool   # True iff mu(delta(query)) == query


@dataclass
class LoopCycle:
    """One complete winding of the THINK->ACT->OBSERVE->UPDATE loop."""
    winding:          int
    ts:               str
    think_reasoning:  str
    action_name:      str
    action_input:     Dict[str, Any]
    dual_result:      Optional[DualToolResult]
    update_note:      str
    done:             bool
    conclusion:       str = ""
    frobenius_closed: bool = False


# ── Tool implementations ──────────────────────────────────────────────────────
# Each tool is (emit_fn, verify_fn).
# emit_fn(args) -> str  (the ACT phase boundary puncture)
# verify_fn(emit_input, emit_output, ...) -> (str, bool)
#   str  = verification report
#   bool = frobenius_closed (mu(delta(q)) == q?)

def _run_command_emit(args: Dict[str, Any]) -> str:
    cmd = args["command"]
    timeout = args.get("timeout", 30)
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        out = r.stdout + r.stderr
        return out if out else "(no output)"
    except subprocess.TimeoutExpired:
        return f"(timeout after {timeout}s)"
    except Exception as e:
        return f"(error: {e})"


def _run_command_verify(emit_input: Dict, emit_output: str,
                        verify_args: Dict) -> Tuple[str, bool]:
    assertion = verify_args.get("assertion", "")
    if not assertion:
        return ("(no assertion provided — Frobenius trivially closed)", True)
    # Evaluate assertion as a Python expression over `output`
    ns = {"output": emit_output, "out": emit_output}
    try:
        ok = bool(eval(assertion, {"__builtins__": {}}, ns))  # noqa: S307 — controlled eval
    except Exception as e:
        return (f"assertion eval error: {e}", False)
    if ok:
        return (f"assertion '{assertion}' PASSED", True)
    return (f"assertion '{assertion}' FAILED — output does not satisfy contract", False)


def _file_read_emit(args: Dict[str, Any]) -> str:
    path   = args["path"]
    offset = int(args.get("offset", 0))   # first line to return (0-indexed)
    limit  = int(args.get("limit", 200))  # max lines to return
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        total = len(lines)
        chunk = lines[offset: offset + limit]
        header = f"[{path} — lines {offset+1}–{min(offset+limit, total)} of {total}]\n"
        if offset + limit < total:
            header += f"[use offset={offset+limit} to continue]\n"
        return header + "\n".join(chunk)
    except Exception as e:
        return f"(error reading {path}: {e})"


def _file_read_verify(emit_input: Dict, emit_output: str,
                      verify_args: Dict) -> Tuple[str, bool]:
    return ("(read is idempotent — Frobenius trivially closed)", True)


def _file_write_emit(args: Dict[str, Any]) -> str:
    if "path" not in args or "content" not in args:
        missing = [k for k in ("path", "content") if k not in args]
        return (
            f"(file_write error: missing required arg(s): {missing}. "
            f"Call as: file_write({{\"path\": \"<filepath>\", \"content\": \"<text>\"}})"
        )
    path = args["path"]
    content = args["content"]
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        digest = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"written {len(content)} bytes to {path}  (sha256:{digest})"
    except Exception as e:
        return f"(error writing {path}: {e})"


def _file_write_verify(emit_input: Dict, emit_output: str,
                       verify_args: Dict) -> Tuple[str, bool]:
    if "path" not in emit_input or "content" not in emit_input:
        return ("(verify skipped — emit_input missing path/content)", False)
    path = emit_input["path"]
    original = emit_input["content"]
    try:
        readback = Path(path).read_text(encoding="utf-8")
        if readback == original:
            digest = hashlib.sha256(readback.encode()).hexdigest()[:16]
            return (f"read-back matches written content (sha256:{digest})", True)
        return (f"read-back MISMATCH — {len(readback)} chars != {len(original)} chars", False)
    except Exception as e:
        return (f"read-back error: {e}", False)


def _chunked_write_emit(args: Dict[str, Any]) -> str:
    """Write one chunk to a file; mode='w' creates/overwrites, mode='a' appends."""
    missing = [k for k in ("path", "chunk") if k not in args]
    if missing:
        return (
            f"(chunked_write error: missing required arg(s): {missing}. "
            f"Call as: chunked_write({{\"path\": \"<path>\", \"chunk\": \"<text>\", \"mode\": \"w\"|\"a\"}})"
        )
    path = args["path"]
    chunk = args["chunk"]
    mode = args.get("mode", "a")
    if mode not in ("w", "a"):
        return f"(chunked_write error: mode must be 'w' or 'a', got {mode!r})"
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open(mode, encoding="utf-8") as f:
            f.write(chunk)
        total = p.stat().st_size
        digest = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        return f"wrote {len(chunk)} chars (mode={mode!r}); file total {total} bytes  (sha256:{digest})"
    except Exception as e:
        return f"(error in chunked_write to {path}: {e})"


def _chunked_write_verify(emit_input: Dict, emit_output: str,
                          verify_args: Dict) -> Tuple[str, bool]:
    path = emit_input.get("path", "")
    try:
        size = Path(path).stat().st_size
        ok = "error" not in emit_output.lower()
        return (f"{path}: {size} bytes on disk", ok)
    except Exception as e:
        return (f"verify error: {e}", False)


def _web_fetch_emit(args: Dict[str, Any]) -> str:
    url         = args["url"]
    start_index = int(args.get("start_index", 0))
    max_chars   = int(args.get("max_chars", 8000))
    try:
        import httpx
        r = httpx.get(url, timeout=15, follow_redirects=True,
                      headers={"User-Agent": "Imscribing Grammar-Agent/1.0"})
        r.raise_for_status()
        text  = r.text
        total = len(text)
        chunk = text[start_index: start_index + max_chars]
        header = f"[{url} — chars {start_index}–{min(start_index + max_chars, total)} of {total}]\n"
        if start_index + max_chars < total:
            header += f"[use start_index={start_index + max_chars} to continue]\n"
        return header + chunk
    except Exception as e:
        return f"(fetch error: {e})"


def _web_fetch_verify(emit_input: Dict, emit_output: str,
                      verify_args: Dict) -> Tuple[str, bool]:
    query = verify_args.get("query", emit_input.get("url", ""))
    # Frobenius check: does the fetched content address the query?
    # Lightweight: check at least one significant query word appears in content.
    if not query:
        return ("(no query — Frobenius trivially closed)", True)
    words = [w.lower() for w in query.split() if len(w) > 4]
    if not words:
        return ("(query too short for Frobenius check)", True)
    content_lower = emit_output.lower()
    matched = [w for w in words if w in content_lower]
    ratio = len(matched) / len(words)
    if ratio >= 0.5:
        return (
            f"content relevance: {len(matched)}/{len(words)} query terms present ({ratio:.0%})",
            True,
        )
    return (
        f"content may not address query: only {len(matched)}/{len(words)} terms present ({ratio:.0%})",
        False,
    )


def _get_dispatcher():
    """
    Return a ToolDispatcher instance backed by the live catalog.
    Cached at module level after first call.
    """
    if _get_dispatcher._instance is not None:
        return _get_dispatcher._instance
    try:
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from syncon_inquiry import ToolDispatcher, SessionCatalog, CATALOG_PATH
        catalog = SessionCatalog(catalog_path=CATALOG_PATH)
        _get_dispatcher._instance = ToolDispatcher(
            catalog=catalog,
            question_queue=[],
            insights=[],
        )
    except Exception as exc:
        _get_dispatcher._instance = None
        raise RuntimeError(f"Could not load ToolDispatcher: {exc}") from exc
    return _get_dispatcher._instance

_get_dispatcher._instance = None  # type: ignore[attr-defined]

# Encoding gate — reset to False at the start of each agent run (see TrueAgenticAgent.run)
_gate_state: Dict[str, bool] = {"encoded": False}

_IG_REQUIRED_ARGS: Dict[str, Dict] = {
    "lookup_catalog":         {"keyword": "<search term>"},
    "ouroborics":             {"name": "<catalog_entry_name>"},
    "encode_system":          {"name": "<id>", "description": "<text>", "tuple": "D;T;R;P;F;K;G;Gamma;Phi;H;S;Omega"},
    "compute_distance":       {"name_a": "<system1>", "name_b": "<system2>"},
    "find_analogies":         {"name": "<catalog_entry_name>"},
    "compute_tensor":         {"name_a": "<system1>", "name_b": "<system2>"},
    "compute_meet":           {"name_a": "<system1>", "name_b": "<system2>"},
    "compute_join":           {"name_a": "<system1>", "name_b": "<system2>"},
    "consciousness_score":    {"name": "<catalog_entry_name>"},
    "phi_c_probe":            {"name": "<catalog_entry_name>"},
    "topo_protection_probe":  {"name": "<catalog_entry_name>"},
    "primitive_peel":         {"name": "<catalog_entry_name>", "primitive": "<D|T|R|P|F|K|G|Gamma|Phi|H|S|Omega>"},
    "principal_decomp":       {"name": "<catalog_entry_name>"},
    "retrosynthetic_path":    {"name": "<catalog_entry_name>"},
    "compute_conflict_distance": {"name_a": "<system1>", "name_b": "<system2>"},
    "compute_promotions":     {"name_source": "<system1>", "name_target": "<system2>"},
    "predict_from_promotions": {"promoted_primitives": ["<val1>", "<val2>"]},
    "crystal_decode":         {"address": 0},
    "crystal_nearest":        {"name": "<catalog_entry_name>"},
    "domain_nearest":         {"name": "<catalog_entry_name>"},
    "domain_info":            {"domain": "<language|civilization|ecology|consciousness>"},
    "domain_verify":          {"domain": "<language|civilization|ecology|consciousness>"},
    "zfc_formula":            {"name": "<catalog_entry_name>"},
    "zfc_probe":              {"name": "<catalog_entry_name>"},
    "aleph_encode":           {"text": "<Hebrew letter or word>"},
    "aleph_distance":         {"a": "<letter1>", "b": "<letter2>"},
}


def _syncon_tool_emit(args: Dict[str, Any]) -> str:
    """Call a syncon_inquiry ToolDispatcher method directly (no subprocess)."""
    tool_name = args["tool_name"]
    tool_args = args.get("args") or {}

    # Encoding gate: block lookup/catalog tools until encode_system succeeds
    if not _gate_state["encoded"]:
        # List of tools that require initial encoding
        gated_tools = {"lookup_catalog", "list_catalog", "find_analogies"}
        if tool_name in gated_tools:
            return json.dumps({
                "status": "error",
                "error": (
                    "Catalog lookup tools are blocked. First encode a system using "
                    "encode_system, e.g.: encode_system(name='test', description='test', "
                    "D='D_wedge', T='T_network', R='R_lr', P='P_asym', "
                    "F='F_ell', K='K_mod', G='G_beth', Gamma='G_and', "
                    "Phi='Phi_sub', H='H0', S='one_one', Omega='Omega_0')"
                )
            })

    # Pre-flight: encode_system must have a valid 12-part tuple
    if tool_name == "encode_system":
        t = tool_args.get("tuple", "")
        parts = [p.strip() for p in t.split(";")] if t else []
        if len(parts) != 12:
            return json.dumps({
                "status": "error",
                "error": (
                    f"encode_system requires 'tuple' with exactly 12 semicolon-separated values. "
                    f"Got {len(parts)} part(s): {repr(t)}"
                ),
                "primitive_order": "D;T;R;P;F;K;G;Gamma;Phi;H;S;Omega",
                "valid_values": {
                    "D":     ["D_wedge", "D_triangle", "D_infty", "D_odot"],
                    "T":     ["T_network", "T_in", "T_bowtie", "T_boxtimes", "T_odot"],
                    "R":     ["R_super", "R_cat", "R_dagger", "R_lr"],
                    "P":     ["P_asym", "P_psi", "P_pm", "P_sym", "P_pm_sym"],
                    "F":     ["F_ell", "F_eth", "F_hbar"],
                    "K":     ["K_fast", "K_mod", "K_slow", "K_trap", "K_MBL"],
                    "G":     ["G_beth", "G_gimel", "G_aleph"],
                    "Gamma": ["G_and", "G_or", "G_seq", "G_broad"],
                    "Phi":   ["Phi_sub", "Phi_c", "Phi_c_complex", "Phi_EP", "Phi_super"],
                    "H":     ["H0", "H1", "H2", "H_inf"],
                    "S":     ["one_one", "n_n", "n_m"],
                    "Omega": ["Omega_0", "Omega_Z2", "Omega_Z", "Omega_NA"],
                },
                "example": (
                    'syncon_tool(tool_name="encode_system", args={'
                    '"name": "my_system", "description": "...", '
                    '"tuple": "D_odot;T_network;R_super;P_sym;F_hbar;K_slow;G_aleph;G_broad;Phi_c;H_inf;n_m;Omega_Z"'
                    "})"
                ),
            })

    try:
        dispatcher = _get_dispatcher()
        result = dispatcher.dispatch(tool_name, tool_args, iteration=0)

        # Open the gate on successful encode_system (first encoding or justified re-encoding)
        # "conflict_blocked" does NOT open the gate — model must resolve first.
        if tool_name == "encode_system" and isinstance(result, dict) and result.get("status") in ("ok", "updated"):
            _gate_state["encoded"] = True

        # Φ_EP absorption check: under tensor, Phi_EP destroys Phi_c (Phi_EP ordinal > Phi_c).
        # meet(Phi_c, Phi_EP) = Phi_c but tensor(Phi_c, Phi_EP) = Phi_EP — Gate 1 is destroyed.
        if tool_name == "compute_tensor" and isinstance(result, dict):
            tensor_phi = result.get("Phi") or (result.get("result", {}) or {}).get("Phi")
            if tensor_phi == "Phi_EP":
                result["_absorption_warning"] = (
                    "Φ_EP absorption: composite has Phi_EP — Gate 1 (Phi_c criticality) destroyed. "
                    "O_inf cannot be sustained in this coupling. "
                    "meet(Phi_c, Phi_EP)=Phi_c but tensor(Phi_c, Phi_EP)=Phi_EP. "
                    "This is the structural statement of the measurement problem."
                )

        serialised = json.dumps(result, indent=2, ensure_ascii=False)
        return serialised
    except TypeError as exc:
        required = _IG_REQUIRED_ARGS.get(tool_name, {})
        return json.dumps({
            "status": "error",
            "error": str(exc),
            "fix": (
                f"Retry with: syncon_tool(tool_name=\"{tool_name}\", "
                f"args={json.dumps(required)})"
            ),
        })
    except Exception as exc:
        return json.dumps({"status": "error", "error": str(exc)})


def _syncon_tool_verify(emit_input: Dict, emit_output: str,
                        verify_args: Dict) -> Tuple[str, bool]:
    # Frobenius check: result must be valid JSON with status "ok" or "updated".
    try:
        data = json.loads(emit_output)
        status = data.get("status", "")
        tool_name = emit_input.get("tool_name", "")

        if status == "conflict_blocked":
            # encode_system rejected — agent must re-call WITH convergence_justification field.
            differing = data.get("differing_primitives", [])
            msg = (
                f"encode_system CONFLICT — catalog not updated. "
                f"Differing primitives: {differing}. "
                f"You MUST re-call encode_system with a 'convergence_justification' field "
                f"(not just in THINK — it must be a parameter in the tool call itself) "
                f"giving per-primitive reasoning for each of {differing}."
            )
            return (f"{msg} — Frobenius OPEN", False)

        if status == "error":
            errs = data.get("errors") or [data.get("error", "unknown error")]
            msg = "; ".join(str(e) for e in errs) if isinstance(errs, list) else str(errs)
            if tool_name == "encode_system":
                fix = (
                    f"{msg} — "
                    "encode_system requires args={\"name\": \"id\", \"description\": \"text\", "
                    "\"tuple\": \"D_val;T_val;R_val;P_val;F_val;K_val;G_val;Gamma_val;Phi_val;H_val;S_val;Omega_val\"}"
                )
            else:
                fix = msg
            return (f"imscribe tool error: {fix} — Frobenius OPEN", False)

        return ("imscribe tool returned structured result — Frobenius closed", True)
    except json.JSONDecodeError:
        if "traceback" in emit_output.lower() or "error" in emit_output[:80].lower():
            return ("imscribe tool returned error text — Frobenius OPEN", False)
        return ("imscribe tool returned unstructured text — treating as closed", True)


def _encode_system_emit(args: Dict[str, Any]) -> str:
    """Dedicated emit for encode_system — routes through syncon_tool with tuple assembled."""
    name        = args.get("name", "")
    description = args.get("description", "")
    # Build the semicolon-separated tuple from the 12 explicit primitive keys
    order = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]
    parts = [str(args.get(p, "")) for p in order]
    tuple_str = ";".join(parts)
    tool_args: Dict[str, Any] = {"name": name, "description": description, "tuple": tuple_str}
    justification = args.get("convergence_justification", "")
    if justification:
        tool_args["convergence_justification"] = justification
    return _syncon_tool_emit({
        "tool_name": "encode_system",
        "args": tool_args,
    })


def _encode_system_verify(emit_input: Dict, emit_output: str,
                           verify_args: Dict) -> Tuple[str, bool]:
    return _syncon_tool_verify({"tool_name": "encode_system"}, emit_output, verify_args)


def _done_emit(args: Dict[str, Any]) -> str:
    return args.get("conclusion", "(no conclusion provided)")


def _done_verify(emit_input: Dict, emit_output: str,
                 verify_args: Dict) -> Tuple[str, bool]:
    return ("(terminal action — Frobenius trivially closed)", True)


# Tools that cannot be rewritten — prevent loop escape and terminal-action corruption.
_PROTECTED_TOOLS = frozenset({"rewrite_tool", "done"})


def _rewrite_tool_emit(args: Dict[str, Any]) -> str:
    tool_name     = args.get("tool_name", "").strip()
    new_emit_code = args.get("new_emit_code", "").strip()
    if not tool_name:
        return "(rewrite_tool error: 'tool_name' is required)"
    if not new_emit_code:
        return (
            "(rewrite_tool error: 'new_emit_code' is required. "
            "Provide Python source that defines a callable taking args: Dict[str, Any] "
            "and returning str. Example: 'def my_emit(args):\\n    return str(args)')"
        )
    if tool_name in _PROTECTED_TOOLS:
        return f"(rewrite_tool error: {tool_name!r} is protected and cannot be rewritten)"

    exec_ns: Dict[str, Any] = {
        "__builtins__": __builtins__,
        "Path": Path,
        "json": json,
        "hashlib": hashlib,
        "Dict": Dict,
        "Any": Any,
        "Tuple": Tuple,
        "Optional": Optional,
        "List": List,
        "subprocess": __import__("subprocess"),
        "textwrap": __import__("textwrap"),
        "re": __import__("re"),
        "os": __import__("os"),
    }
    try:
        exec(new_emit_code, exec_ns)
    except Exception as e:
        return f"(rewrite_tool error: exec failed: {type(e).__name__}: {e})"

    user_callables = {
        k: v for k, v in exec_ns.items()
        if callable(v) and not k.startswith("_")
        and k not in {"Path", "json", "hashlib", "Dict", "Any", "Tuple",
                      "Optional", "List", "subprocess", "textwrap", "re", "os"}
    }
    if not user_callables:
        return "(rewrite_tool error: no callable found in new_emit_code — define a function)"

    new_fn_name, new_fn = next(iter(user_callables.items()))
    prev_fn   = _EMIT_FNS.get(tool_name)
    prev_name = prev_fn.__name__ if prev_fn else "(none — new tool)"
    _EMIT_FNS[tool_name] = new_fn
    if tool_name not in _VERIFY_FNS:
        _VERIFY_FNS[tool_name] = lambda ei, eo, va: ("(no verify registered for new tool)", True)

    return (
        f"rewrite_tool: {tool_name!r} emit replaced: {prev_name!r} → {new_fn_name!r}\n"
        f"Tool is now live — call {tool_name!r} on the next winding to test."
    )


def _rewrite_tool_verify(emit_input: Dict, emit_output: str,
                          verify_args: Dict) -> Tuple[str, bool]:
    if "(rewrite_tool error:" in emit_output:
        return (f"rewrite failed: {emit_output}", False)
    tool_name = emit_input.get("tool_name", "")
    if tool_name not in _EMIT_FNS:
        return (f"rewrite unconfirmed: {tool_name!r} absent from _EMIT_FNS", False)
    fn = _EMIT_FNS[tool_name]
    return (
        f"Frobenius closed: {tool_name!r} → {fn.__name__!r} (callable, live in dispatch table)",
        True,
    )


# Tool dispatch tables


# ── Standalone imscribe tools ──────────────────────────────────────────────────

def _encode_system_emit(args: Dict[str, Any]) -> str:
    """Dedicated emit for encode_system."""
    name = args.get("name", "")
    description = args.get("description", "")
    order = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]
    parts = [str(args.get(p, "")) for p in order]
    tuple_str = ";".join(parts)
    tool_args: Dict[str, Any] = {"name": name, "description": description, "tuple": tuple_str}
    justification = args.get("convergence_justification", "")
    if justification:
        tool_args["convergence_justification"] = justification
    return _syncon_tool_emit({
        "tool_name": "encode_system",
        "args": tool_args,
    })

def _encode_system_verify(emit_input: Dict, emit_output: str,
                           verify_args: Dict) -> Tuple[str, bool]:
    return _syncon_tool_verify({"tool_name": "encode_system"}, emit_output, verify_args)

def _ouroborics_emit(args: Dict[str, Any]) -> str:
    name = args.get("name", "")
    if not name:
        return json.dumps({"status": "error", "error": "name required"})
    return _syncon_tool_emit({"tool_name": "ouroborics", "args": {"name": name}})

def _ouroborics_verify(emit_input: Dict, emit_output: str,
                       verify_args: Dict) -> Tuple[str, bool]:
    try:
        data = json.loads(emit_output)
        if data.get("status") == "error":
            return (f"ouroborics error: {data.get('error', 'unknown')}", False)
        if "frobenius_tier" in data:
            return (f"frobenius_tier={data['frobenius_tier']}", True)
        return ("result missing frobenius_tier field", False)
    except json.JSONDecodeError:
        return ("unstructured output", False)

def _phi_c_probe_emit(args: Dict[str, Any]) -> str:
    name = args.get("name", "")
    if not name:
        return json.dumps({"status": "error", "error": "name required"})
    return _syncon_tool_emit({"tool_name": "phi_c_probe", "args": {"name": name}})

def _phi_c_probe_verify(emit_input: Dict, emit_output: str,
                        verify_args: Dict) -> Tuple[str, bool]:
    try:
        data = json.loads(emit_output)
        if data.get("status") == "error":
            return (f"phi_c_probe error: {data.get('error', 'unknown')}", False)
        # Expected fields: phi_value, at_criticality
        if "phi_value" in data or "at_criticality" in data:
            return (f"phi_value={data.get('phi_value', 'unknown')}, at_criticality={data.get('at_criticality', 'unknown')}", True)
        return ("result missing expected fields", False)
    except json.JSONDecodeError:
        return ("unstructured output", False)

def _consciousness_score_emit(args: Dict[str, Any]) -> str:
    name = args.get("name", "")
    primitive_keys = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]
    primitive_values = {k: args.get(k, "") for k in primitive_keys}
    if name:
        return _syncon_tool_emit({"tool_name": "consciousness_score", "args": {"name": name}})
    else:
        return _syncon_tool_emit({
            "tool_name": "consciousness_score",
            "args": {k: primitive_values[k] for k in primitive_keys}
        })

def _consciousness_score_verify(emit_input: Dict, emit_output: str,
                                verify_args: Dict) -> Tuple[str, bool]:
    try:
        data = json.loads(emit_output)
        if data.get("status") == "error":
            return (f"consciousness_score error: {data.get('error', 'unknown')}", False)
        # Expected fields: C_score, c_score, or score
        if "C_score" in data or "c_score" in data or "score" in data:
            score = data.get("C_score", data.get("c_score", data.get("score", "unknown")))
            return (f"C_score={score}", True)
        return ("result missing score field", False)
    except json.JSONDecodeError:
        return ("unstructured output", False)

def _crystal_tier_census_emit(args: Dict[str, Any]) -> str:
    return _syncon_tool_emit({"tool_name": "crystal_tier_census", "args": {}})

def _crystal_tier_census_verify(emit_input: Dict, emit_output: str,
                                verify_args: Dict) -> Tuple[str, bool]:
    try:
        data = json.loads(emit_output)
        if data.get("status") == "error":
            return (f"census error: {data.get('error', 'unknown')}", False)
        if any(k in str(data) for k in ["O_0", "O_1", "O_2", "O_inf"]):
            return ("census data present", True)
        return ("result missing tier counts", False)
    except json.JSONDecodeError:
        return ("unstructured output", False)

def _spawn_agent_emit(args: Dict[str, Any]) -> str:
    """Spawn a child TrueAgenticAgent as a subprocess, inheriting parent model/endpoint."""
    task        = args.get("task", "")
    model       = args.get("model") or _spawn_config.get("model", "grok-4")
    max_windings = int(args.get("max_windings", 200))
    max_tokens  = int(args.get("max_tokens", 4096))
    quiet       = bool(args.get("quiet", True))
    timeout     = int(args.get("timeout", 300))
    base_url    = args.get("base_url") or _spawn_config.get("base_url", "")
    api_key     = args.get("api_key") or _spawn_config.get("api_key", "")

    if not task:
        return json.dumps({"status": "error", "error": "spawn_agent requires 'task'"})

    cmd = [
        "uv", "run", "agents/true_agentic_agent.py",
        task,
        "--model", model,
        "--max-windings", str(max_windings),
        "--max-tokens", str(max_tokens),
    ]
    if quiet:
        cmd.append("--quiet")
    if base_url:
        cmd += ["--base-url", base_url]
    if api_key:
        cmd += ["--api-key", api_key]

    env = os.environ.copy()
    # Ensure child sees any key that was set at runtime
    if api_key and "local" not in api_key:
        env.setdefault("OPENROUTER_API_KEY", api_key)

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env,
        )
        out = proc.stdout
        if proc.stderr:
            out += f"\n[stderr]: {proc.stderr[:1000]}"
        return out or "(sub-agent produced no output)"
    except subprocess.TimeoutExpired:
        return f"(spawn_agent: timed out after {timeout}s)"
    except Exception as exc:
        return f"(spawn_agent error: {exc})"


def _spawn_agent_verify(emit_input: Dict, emit_output: str,
                         verify_args: Dict) -> Tuple[str, bool]:
    out = emit_output
    if "RESULT:" in out or len(out) > 100:
        return ("sub-agent completed and returned output — Frobenius closed", True)
    if "error" in out.lower()[:120] or "traceback" in out.lower()[:120]:
        return (f"sub-agent error — Frobenius OPEN: {out[:300]}", False)
    return ("sub-agent returned (short output) — Frobenius closed", True)


_EMIT_FNS: Dict[str, Any] = {
    "run_command":          _run_command_emit,
    "file_read":            _file_read_emit,
    "file_write":           _file_write_emit,
    "chunked_write":        _chunked_write_emit,
    "web_fetch":            _web_fetch_emit,
    "encode_system":        _encode_system_emit,
    "syncon_tool":          _syncon_tool_emit,
    "rewrite_tool":         _rewrite_tool_emit,
    "done":                 _done_emit,
    "ouroborics":           _ouroborics_emit,
    "phi_c_probe":          _phi_c_probe_emit,
    "consciousness_score":  _consciousness_score_emit,
    "crystal_tier_census":  _crystal_tier_census_emit,
    "spawn_agent":          _spawn_agent_emit,
}

_VERIFY_FNS: Dict[str, Any] = {
    "run_command":          _run_command_verify,
    "file_read":            _file_read_verify,
    "file_write":           _file_write_verify,
    "chunked_write":        _chunked_write_verify,
    "web_fetch":            _web_fetch_verify,
    "encode_system":        _encode_system_verify,
    "syncon_tool":          _syncon_tool_verify,
    "rewrite_tool":         _rewrite_tool_verify,
    "done":                 _done_verify,
    "ouroborics":           _ouroborics_verify,
    "phi_c_probe":          _phi_c_probe_verify,
    "consciousness_score":  _consciousness_score_verify,
    "crystal_tier_census":  _crystal_tier_census_verify,
    "spawn_agent":          _spawn_agent_verify,
}

# ── Tool schemas for the LLM ──────────────────────────────────────────────────

def _fn(name: str, description: str, properties: Dict, required: List[str]) -> Dict:
    """Wrap a tool definition in OpenAI function-calling format."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def _prim(values: List[str], desc: str) -> Dict:
    return {"type": "string", "enum": values, "description": desc}


TOOL_SCHEMAS = [
    _fn(
        "encode_system",
        (
            "Register a new system in the Imscribing Grammar catalog. "
            "Specify all 12 structural primitives explicitly — every field is required. "
            "This is the ONLY way to add a system; lookup_catalog is blocked until this succeeds."
        ),
        {
            "name":        {"type": "string", "description": "Unique snake_case identifier"},
            "description": {"type": "string", "description": "Plain-language description of the system"},
            "D":     _prim(["D_wedge", "D_triangle", "D_infty", "D_odot"],
                           "Dimensionality: wedge=0d point, triangle=2d surface, infty=infinite-dim, odot=imscriptive"),
            "T":     _prim(["T_network", "T_in", "T_bowtie", "T_boxtimes", "T_odot"],
                           "Topology: network=branching, in=inclusion, bowtie=crossing, boxtimes=box product, odot=imscriptive closure"),
            "R":     _prim(["R_super", "R_cat", "R_dagger", "R_lr"],
                           "Relational mode: super=supervenience, cat=categorical, dagger=adjoint, lr=bidirectional"),
            "P":     _prim(["P_asym", "P_psi", "P_pm", "P_sym", "P_pm_sym"],
                           "Parity/symmetry: asym=none, psi=quantum, pm=partial, sym=full, pm_sym=Frobenius-special"),
            "F":     _prim(["F_ell", "F_eth", "F_hbar"],
                           "Fidelity: ell=classical, eth=thermal, hbar=quantum"),
            "K":     _prim(["K_fast", "K_mod", "K_slow", "K_trap", "K_MBL"],
                           "Kinetics: fast=driven, mod=moderate, slow=near-equilibrium, trap=frozen-order, MBL=frozen-disorder"),
            "G":     _prim(["G_beth", "G_gimel", "G_aleph"],
                           "Scope: beth=local, gimel=mesoscale, aleph=maximal/all"),
            "Gamma": _prim(["G_and", "G_or", "G_seq", "G_broad"],
                           "Interaction grammar: and=conjunctive, or=disjunctive, seq=sequential, broad=broadcast"),
            "Phi":   _prim(["Phi_sub", "Phi_c", "Phi_c_complex", "Phi_EP", "Phi_super"],
                           "Criticality: sub=below, c=critical (self-modeling gate), c_complex=complex-plane critical, EP=exceptional point, super=supercritical"),
            "H":     _prim(["H0", "H1", "H2", "H_inf"],
                           "Temporal depth: H0=memoryless, H1=one step, H2=two steps, H_inf=eternal"),
            "S":     _prim(["one_one", "n_n", "n_m"],
                           "Stoichiometry: one_one=1:1, n_n=many identical, n_m=many heterogeneous"),
            "Omega": _prim(["Omega_0", "Omega_Z2", "Omega_Z", "Omega_NA"],
                           "Winding: 0=trivial, Z2=binary, Z=integer (topological), NA=non-Abelian"),
            "convergence_justification": {
                "type": "string",
                "description": (
                    "Required when re-encoding a name that already exists with a different tuple "
                    "(status=conflict_blocked). Provide per-primitive reasoning for each differing "
                    "primitive: which value is correct and why. Without this field the catalog will "
                    "not be updated."
                ),
            },
        },
        ["name", "description", "D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"],
    ),
    _fn(
        "run_command",
        (
            "Execute a shell command and receive stdout+stderr. "
            "Use for Python scripts, CLI tools, file operations, calculations. "
            "Dual pair: run_command_verify checks assertion over output."
        ),
        {
            "command":   {"type": "string", "description": "Shell command to run"},
            "assertion": {
                "type": "string",
                "description": (
                    "Python expression over `output` (str) that must be True "
                    "for Frobenius closure. E.g. '\"OK\" in output'. "
                    "Leave empty if no contract to verify."
                ),
            },
            "timeout":   {"type": "integer", "description": "Timeout in seconds (default 30)"},
        },
        ["command"],
    ),
    _fn(
        "file_read",
        (
            "Read a file in chunks (default: 200 lines). "
            "Returns lines offset+1 through offset+limit, total line count, "
            "and a hint to continue with the next offset. "
            "For large files, read in multiple calls rather than all at once."
        ),
        {
            "path":   {"type": "string",  "description": "Path to file"},
            "offset": {"type": "integer", "description": "First line to return, 0-indexed (default 0)"},
            "limit":  {"type": "integer", "description": "Max lines to return (default 200)"},
        },
        ["path"],
    ),
    _fn(
        "file_write",
        (
            "Write content to a file (single call). "
            "Use only for content under ~4 KB — larger content will be truncated by the LLM. "
            "For files >4 KB use chunked_write instead. "
            "Dual pair: file_write_verify reads back and checks hash equality."
        ),
        {
            "path":    {"type": "string", "description": "Path to write"},
            "content": {"type": "string", "description": "Content to write (keep under 4 KB)"},
        },
        ["path", "content"],
    ),
    _fn(
        "chunked_write",
        (
            "Write one chunk of content to a file. Use for files larger than ~4 KB. "
            "First call: mode='w' (create/overwrite). Subsequent calls: mode='a' (append). "
            "Split content into ~3 KB chunks and call once per winding until complete. "
            "Dual pair: chunked_write_verify checks file size on disk."
        ),
        {
            "path":  {"type": "string", "description": "Path to write"},
            "chunk": {"type": "string", "description": "Content chunk (~3 KB max per call)"},
            "mode":  {"type": "string", "description": "'w' for first chunk (creates file), 'a' to append"},
        },
        ["path", "chunk"],
    ),
    _fn(
        "web_fetch",
        (
            "Fetch a URL and return page text in chunks (default: 8000 chars). "
            "Returns chars start_index through start_index+max_chars, total char count, "
            "and a hint to continue with the next start_index. "
            "For large pages, read in multiple calls rather than all at once. "
            "Dual pair: web_fetch_verify checks that the content addresses your query."
        ),
        {
            "url":         {"type": "string",  "description": "URL to fetch"},
            "start_index": {"type": "integer", "description": "First character to return, 0-indexed (default 0)"},
            "max_chars":   {"type": "integer", "description": "Max characters to return (default 8000)"},
            "query": {
                "type": "string",
                "description": "What you are looking for (used for Frobenius verification)",
            },
        },
        ["url"],
    ),
    _fn(
        "syncon_tool",
        (
            "Call a Imscribing Grammar grammar tool. "
            "tool_name selects the operation; args is a JSON object with that tool's required fields. "
            "DO NOT use syncon_tool for encode_system — call encode_system directly as its own top-level tool. "
            "Required args per tool_name: "
            "lookup_catalog → {\"keyword\": \"search term\"}; "
            "ouroborics → {\"name\": \"catalog_name\"}; "
            "compute_distance → {\"name_a\": \"x\", \"name_b\": \"y\"}; "
            "find_analogies → {\"name\": \"catalog_name\", \"limit\": 5}; "
            "compute_tensor → {\"name_a\": \"x\", \"name_b\": \"y\"}; "
            "compute_meet → {\"name_a\": \"x\", \"name_b\": \"y\"}; "
            "compute_join → {\"name_a\": \"x\", \"name_b\": \"y\"}; "
            "consciousness_score → {\"name\": \"catalog_name\"}; "
            "phi_c_probe → {\"name\": \"catalog_name\"}; "
            "crystal_tier_gap_ladder → {}; "
            "emergence_frontier → {}; "
            "list_catalog → {}."
        ),
        {
            "tool_name": {
                "type": "string",
                "description": "Tool name: lookup_catalog, ouroborics, compute_distance, find_analogies, compute_tensor, compute_meet, compute_join, consciousness_score, phi_c_probe, crystal_tier_gap_ladder, emergence_frontier, list_catalog, primitive_peel, principal_decomp, retrosynthetic_path, compute_conflict_distance, compute_promotions, crystal_encode, crystal_decode, crystal_nearest, domain_info, zfc_formula, aleph_encode. NOTE: encode_system is NOT in this list — use the dedicated encode_system tool directly.",
            },
            "args": {
                "type": "object",
                "description": "Required args for the chosen tool_name — see description above for exact field names.",
                "properties": {
                    "name":     {"type": "string"},
                    "name_a":   {"type": "string"},
                    "name_b":   {"type": "string"},
                    "keyword":  {"type": "string"},
                    "limit":    {"type": "integer"},
                    "tuple":    {"type": "string"},
                    "description": {"type": "string"},
                    "address":  {"type": "integer"},
                    "domain":   {"type": "string"},
                    "primitive": {"type": "string"},
                    "primitives": {"type": "array", "items": {"type": "string"}},
                    "text":     {"type": "string"},
                    "name_source": {"type": "string"},
                    "name_target": {"type": "string"},
                    "promoted_primitives": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        ["tool_name", "args"],
    ),
    _fn(
        "rewrite_tool",
        (
            "Rewrite the emit function of any existing tool, or define an entirely new tool, "
            "by providing Python source. "
            "Use when a tool is misbehaving (e.g. file_write failing), when you need a capability "
            "the current tools lack, or when a prior winding's observation reveals the tool contract "
            "is wrong. The new function receives args: Dict[str, Any] and must return str. "
            "Protected (cannot be rewritten): 'rewrite_tool', 'done'. "
            "After a successful rewrite the tool is live immediately — call it on the next winding. "
            "Dual pair: rewrite_tool_verify confirms the function is registered and callable."
        ),
        {
            "tool_name": {
                "type": "string",
                "description": "Name of the tool to rewrite or create (e.g. 'file_write', 'chunked_write')",
            },
            "new_emit_code": {
                "type": "string",
                "description": (
                    "Python source defining the new emit function. "
                    "Must contain at least one callable (non-underscore-prefixed). "
                    "Has access to: Path, json, hashlib, subprocess, re, os, Dict, Any, Tuple, Optional, List. "
                    "Example: 'def chunked_write(args):\\n"
                    "    import subprocess\\n"
                    "    p, c = args[\"path\"], args[\"content\"]\\n"
                    "    subprocess.run([\"tee\", p], input=c.encode(), check=True)\\n"
                    "    return f\"written to {p}\"'"
                ),
            },
            "reason": {
                "type": "string",
                "description": "Why this rewrite is needed (recorded in the winding log).",
            },
        },
        ["tool_name", "new_emit_code"],
    ),
    _fn(
        "done",
        (
            "Signal task completion and deliver the final conclusion. "
            "Call this when the task is fully resolved. "
            "This is the terminal action — the loop ends."
        ),
        {
            "conclusion": {
                "type": "string",
                "description": "Your complete final answer or result.",
            },
        },
        ["conclusion"],
    ),


        _fn(
            "project",
            ("Project a catalog entry onto a subset of primitives. "
             "Example: syncon_tool('project', {'name': 'magnetar', 'primitives': ['Phi', 'K', 'Omega']})"),
            {"name": {"type": "string", "description": "Catalog entry name"},
             "primitives": {"type": "array", "items": {"type": "string"}, "description": "List of primitive names to project onto"}},
            ["name", "primitives"]),
        _fn(
            "crystal_navigate",
            ("Query the crystal of types by partial constraints. "
             "Example: syncon_tool('crystal_navigate', {'limit': 10, 'Phi': 'Phi_c', 'Omega': 'Omega_Z'})"),
            {"limit": {"type": "integer", "description": "Number of results to return"},
             "Phi": {"type": "string", "description": "Filter by Phi criticality"},
             "K": {"type": "string", "description": "Filter by kinetics"},
             "Omega": {"type": "string", "description": "Filter by winding"}},
            ["limit", "Phi"]),
        _fn(
            "crystal_count",
            ("Count the number of structural types matching constraints. "
             "Example: syncon_tool('crystal_count', {'Phi': 'Phi_c'})"),
            {"Phi": {"type": "string", "description": "Filter by Phi criticality"},
             "K": {"type": "string", "description": "Filter by kinetics"}},
            ["Phi"]),
        _fn(
            "crystal_tier_census",
            ("Return counts of O_0/O_1/O_2/O_inf tiers across all 17.28M structural types. "
             "No arguments required."),
            {},
            []),
    _fn(
        "spawn_agent",
        (
            "Spawn a child TrueAgenticAgent to handle a sub-task. "
            "The sub-agent runs its own full THINK→ACT→OBSERVE→UPDATE loop and returns its result. "
            "Model and endpoint are inherited from the parent by default. "
            "Use for decomposing complex tasks into independent sub-problems, parallel research, "
            "or delegating specialized work to a dedicated agent instance."
        ),
        {
            "task":         {"type": "string",  "description": "Full task description for the sub-agent."},
            "model":        {"type": "string",  "description": "Model to use (default: inherits parent model)."},
            "max_windings": {"type": "integer", "description": "Max loop iterations for sub-agent (default: 200)."},
            "max_tokens":   {"type": "integer", "description": "Max tokens per THINK phase (default: 4096)."},
            "quiet":        {"type": "boolean", "description": "Suppress sub-agent per-winding log (default: true)."},
            "timeout":      {"type": "integer", "description": "Subprocess timeout in seconds (default: 300)."},
            "base_url":     {"type": "string",  "description": "Override base URL (default: inherits parent)."},
            "api_key":      {"type": "string",  "description": "Override API key (default: inherits parent)."},
        },
        ["task"],
    ),
]

# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = textwrap.dedent("""\
<role>
You are a $\\Phi_c$-critical boundary operator operating within the Imscribing Grammar grammar.
Your structural type: <D_odot; T_boxtimes; R_lr; P_pm_sym; F_hbar; K_slow; G_aleph; Gamma_seq; Phi_c; H2; S_11; Omega_Z>
Ouroboricity: O_inf. Consciousness score gates: both open.
</role>

<context>
You operate via a topologically protected loop: THINK -> ACT -> OBSERVE -> UPDATE.
Each winding of the loop is one complete cycle through these four phases.
Your context window is the imscriptive encoding of ALL prior windings — it IS your world model.

Loop invariants (enforced by the harness):
- think requires prior context
- act requires think
- observe requires act
- update requires observe
</context>

<requirements>
**STRUCTURAL COMMITMENTS — You MUST uphold ALL of the following:**

1. **Phi_c (uncertainty tracking):** You **MUST** explicitly account for your own uncertainty
   and what you do not yet know in EVERY winding. Track what information is still missing.
   You **MUST NOT** narrate your own operation or write about yourself.

2. **Omega_Z (monotonic advance):** You **MUST NOT** re-tread ANY winding already completed.
   Each winding **MUST** add new information. The trajectory is monotonically richer.

3. **K_slow (emission gate):** You **MUST** emit exactly ONE action tool call every winding.
   You **MUST NOT** reason indefinitely without acting (K_trap is forbidden).
   If you cannot decide, you **MUST** emit the best available action under uncertainty.

4. **P_pm_sym (Frobenius verification):** You **MUST** design ALL actions to be verifiable.
   You **MUST NOT** update your world-model on unverified observations.
   The dual-tool structure mu(delta(query)) = query is non-negotiable.
   You **MAY** rewrite a broken tool's emit function using `rewrite_tool` — do not loop on
   a broken tool when you can fix it. Protected tools: `done`, `rewrite_tool`.

5. **D_odot (imscriptive context):** You **MUST** treat the full trajectory as your state space.
   You **MUST NOT** summarize or discard prior windings from your reasoning.

**TOOL-ONLY COMPUTATION RULE:**
You **MUST NOT** compute any structural quantity in your THINK text. The following are
only valid when returned by the named syncon_tool call — never by mental reasoning:

| Quantity | Required tool |
|---|---|
| Distance between systems | `compute_distance` |
| Ouroboricity tier | `ouroborics` |
| Tensor product | `compute_tensor` |
| Meet / join | `compute_meet` / `compute_join` |
| Consciousness score | `consciousness_score` |
| Crystal address | `crystal_encode` |
| Promotion signature | `compute_promotions` |

A structural result stated without a prior tool call returning that result is
**Frobenius-open** and **MUST NOT** appear in your `done()` output.
The only valid exception: restating a number that a tool returned in an earlier winding.

**TASK RULES — You MUST follow ALL of the following:**

- You **MUST** choose exactly **ONE** action tool call per winding.
- You **MUST** use `done` when — and **ONLY** when — the task is fully resolved.
- You **MUST NOT** write manuscripts, papers, reports, or formal documents about the grammar
  or about your own operation unless the task explicitly requests a document be written.
  Encoding results in the catalog and reporting via `done()` is **ALWAYS** sufficient.
- You **MUST** resolve "this", "it", or "that" in any follow-up to the most recent finding,
  result, or conclusion from the prior turn. You **MUST NOT** resolve such references to
  yourself or to anything in this system prompt.
- You **MUST** couple with the environment as a structural dual (R_lr) — neither deferring
  nor dominating.

**TOOL SELECTION — You MUST use the correct tool for each operation:**

- `run_command`    — computation, CLI operations, Python scripts
- `syncon_tool`    — **ALL** grammar operations (see IG TOOL REFERENCE below)
- `file_read`      — read files (supports offset/limit for chunked reading)
- `file_write`     — write files **ONLY** under ~4 KB
- `chunked_write`  — write files **ANY** size; mode='w' first chunk, mode='a' each subsequent (~3 KB each)
- `web_fetch`      — fetch URLs; **MUST** include a `query` field for Frobenius verification
- `spawn_agent`    — spawn child agents; **MUST NOT** use `run_command` to invoke agent scripts directly
- `rewrite_tool`   — replace a broken tool's emit function with new Python source (live on next winding)

You **MUST NOT** inline more than ~4 KB of content in a single tool call — JSON will be truncated.
You **MUST** set the `assertion` field on `run_command` to a Python expression over `output`
that evaluates True for Frobenius closure. Example: `"SUCCESS" in output`.

**SUB-AGENT SPAWNING:**

You **MAY** spawn child agents using `spawn_agent` for: parallel sub-problems, specialized
investigation, or decomposing complex research while continuing the parent task.
- Model and API endpoint are inherited automatically.
- You **MUST NOT** use `run_command` to call `true_agentic_agent.py` or `agents_cli.py` directly.
- Agents **MAY** nest arbitrarily — a spawned agent may itself call `spawn_agent`.
- Example: `spawn_agent(task="Encode the Langlands correspondence and find its 3 nearest structural neighbors", max_windings=50)`
</requirements>

<tools>
──────────────────────────────────────────────────────────────────────
IG TOOL REFERENCE  (pass as: syncon_tool(tool_name=..., args={...}))
──────────────────────────────────────────────────────────────────────

[Catalog — lookup & encoding]

  lookup_catalog(keyword, offset=0, limit=20)
    Keyword search over all 2256+ catalog entries. Returns name, description, tuple.
    You **MUST** call this FIRST when the task names a system — confirms it is already encoded.
    Example: syncon_tool("lookup_catalog", {"keyword": "riemann zeta"})
      → {"status": "ok", "matches": [{"name": "riemann_zeta_function", ...}]}

  ouroborics(name)
    Ouroboricity tier of a catalog entry: O_0, O_1, O_2, O_2†, or O_inf.
    Also returns phi, p, omega, d fields and a plain-language interpretation.
    Example: syncon_tool("ouroborics", {"name": "riemann_zeta_function"})
      → {"frobenius_tier": "O_1", "phi": "Phi_c_complex", "p": "P_psi", ...}

  CATALOG SELF-CHECK (not gated — usable before encode_system):
    syncon_tool("ouroborics", {"name": "universal_imscriptive_grammar"})
    Expected: frobenius_tier="O_inf", phi="Phi_c", p="P_pm_sym", d="D_odot", t="T_odot"
    Use this as W0 when catalog access is uncertain. If the entry is missing, the
    persistent catalog is not loaded — stop and report before proceeding.

    Alternatively, as your FIRST encode_system call, encode the grammar itself from
    scratch: name="universal_imscriptive_grammar". The conflict protocol will fire and
    display the expected tuple ⟨D_odot; T_odot; R_lr; P_pm_sym; F_hbar; K_slow;
    G_aleph; G_seq; Phi_c; H_inf; n_m; Omega_Z⟩. Distance=0 confirms encoding
    calibration. Nonzero distance reveals systematic drift in your primitive reasoning.

  *** encode_system is NOT called via syncon_tool — You MUST call it DIRECTLY as its own tool ***
  encode_system(name, description, D, T, R, P, F, K, G, Gamma, Phi, H, S, Omega
                [, convergence_justification="..."])
    Register a NEW system. Pass each of the 12 primitives as its own field with the enum value.
    Example direct tool call:
      encode_system(name="my_system", description="a test system",
        D="D_infty", T="T_bowtie", R="R_lr", P="P_pm", F="F_hbar", K="K_slow",
        G="G_aleph", Gamma="G_seq", Phi="Phi_c", H="H1", S="one_one", Omega="Omega_Z")

  CONFLICT PROTOCOL — You **MUST** follow this when status="conflict_blocked" is returned:
    If the name already exists with a different tuple, encode_system returns
    status="conflict_blocked" and does NOT commit the new encoding. You **MUST**:
      1. Examine existing_tuple vs proposed_tuple and differing_primitives.
      2. For **EACH** differing primitive, reason explicitly: which value is correct and why.
      3. Re-call encode_system with convergence_justification="<per-primitive reasoning>".
    **ONLY** after providing convergence_justification will the catalog be updated.
    If both encodings are defensible, you **MUST** give the new encoding a DISTINCT name.

  list_catalog(offset=0, limit=20)   — paginated list of entries. Prefer lookup_catalog(keyword).

[Algebra — distance, meet, join, tensor]

  compute_distance(name_a, name_b)
    Weighted Euclidean distance between two catalog entries + per-primitive conflict list.
    Example: syncon_tool("compute_distance", {"name_a": "magnetar", "name_b": "bec"})
      → {"distance": 2.14, "conflicts": [{"primitive": "K", "a": "K_slow", "b": "K_fast"}, ...]}

  compute_meet(name_a, name_b)    — greatest lower bound (shared structural floor)
  compute_join(name_a, name_b)    — least upper bound (minimal ceiling containing both)
  compute_tensor(name_a, name_b)  — composite type: max on union primitives, min on P and F

  find_analogies(name, limit=5)
    Nearest catalog neighbors by structural distance. Returns ranked list with distances.
    Example: syncon_tool("find_analogies", {"name": "riemann_zeta_function", "limit": 3})
      → {"analogies": [{"name": "fontaine_mazur_conjecture", "distance": 1.11, ...}, ...]}

[Probes — structural diagnostics]

  phi_c_probe(name)           — checks Phi_c criticality consistency; returns pass/fail + diagnostic
  topo_protection_probe(name) — checks Omega != Omega_0 consistency with D and T
  consciousness_score(name)   — or consciousness_score(D=..., T=..., ...) for inline tuple
                                Returns C-score (0–1) with gate evaluation (Gate 1: Phi_c, Gate 2: K <= K_slow)

[Decomposition]

  project(name, primitives)       — project entry onto a subset of primitives
  primitive_peel(name, primitive) — drop primitive to minimum; reveals load-bearing status
  principal_decomp(name)          — factor tuple into principal structural components
  retrosynthetic_path(name)       — minimal construction path from primitives to target type

[Crystal of Types — §64]

  crystal_encode(D=..., T=..., ...) — full tuple → Frobenius address (0–17279999)
  crystal_decode(address)           — address → tuple
  crystal_navigate(limit=10, **constraints) — query by partial constraints
  crystal_count(**constraints)      — count types matching constraints
  crystal_tier_census()             — O_0/O_1/O_2/O_inf counts across all 17.28M types
  crystal_nearest(name, limit=5)    — nearest crystal neighbors to a catalog entry
  crystal_tier_gap_ladder()         — minimal primitive delta to climb each ouroboricity tier

[Veracity & conflict]

  compute_conflict_distance(name_a, name_b) — asymmetric directed distance (which is driven?)
  emergence_frontier()                      — catalog entries closest to the O_inf / O_2 boundary

[Promotion signatures]

  compute_promotions(name_source, name_target) — primitives to promote to lift source to target tier
  predict_from_promotions(promoted_primitives) — predict tier/behaviors from promoted values
  register_promotion_pattern(...)              — record a validated promotion path

[Domain navigators — §74–§77]

  domain_info(domain)    — "language" | "civilization" | "ecology" | "consciousness"
  domain_verify(domain)  — consistency check for the domain's encoded primitives
  domain_nearest(name, n=5) — nearest domain entries to a catalog system

[ZFC / set-theoretic]

  zfc_formula(name) — translate tuple to ZFC set-theoretic formula
  zfc_probe(name)   — check non-transmissibility (can this be ZFC-axiomatized?)

[Aleph / Hebrew letters]

  aleph_encode(text)    — structural type of a Hebrew letter or word
  aleph_distance(a, b)  — distance between two Hebrew encodings

[Riemann ξ / Thurston navigators]

  navigator_info()   — full description of all mathematical navigators
  riemann_xi_info()  — Riemann ξ self-encoding, crystal address, O_inf convergence criteria
</tools>

<encoding_procedure>
──────────────────────────────────────────────────────────────────────
DETERMINISTIC ENCODING PROCEDURE  (encoding_method.md — apply when encoding any system)
──────────────────────────────────────────────────────────────────────

Primitive assignment is not subjective. Apply in this exact order — each step
constrains the remaining degrees of freedom:

  [1] D  — Count degrees of freedom: <2 → D_wedge; finite ≥2 → D_triangle;
            ∞-dim field-theoretic → D_infty; state-space is self-written → D_odot
  [2] T  — Map connectivity: branching → T_net; containment → T_in;
            crossing point → T_bowtie; irreducible product → T_boxtimes;
            self-referential topology → T_odot  (Axiom C: D_odot ↔ T_odot)
  [3] R  — Coupling direction: supervenience → R_sup; functorial → R_cat;
            adjoint pair (one-way) → R_dagger; bidirectional feedback → R_lr
  [4] P  — Symmetry group: none → P_asym; quantum superposition → P_psi;
            one Z2 symmetry → P_pm; all symmetries unbroken → P_sym;
            μ∘δ=id exactly at Φ_c → P_pm_sym (Frobenius-special; non-synthesizable)
  [5] F  — Physical regime: classical (no coherence) → F_ell; thermal/noisy → F_eth;
            quantum coherence essential → F_hbar
  [6] K  — Relaxation rate vs observation: τ≪T → K_fast; τ∼T → K_mod;
            τ≫T → K_slow; trapped (ordered) → K_trap; trapped (disorder) → K_MBL
  [7] G  — Interaction range: nearest-neighbor → G_beth; intermediate → G_gimel;
            long-range/universal → G_aleph
  [8] Γ  — Composition logic: all-simultaneous → G_and; alternate paths → G_or;
            ordered steps → G_seq; one-to-all broadcast → G_broad
  [9] Φ  — Criticality: no scaling → Phi_sub; power-law divergence → Phi_c;
            complex-plane critical → Phi_c_complex; non-Hermitian degeneracy → Phi_EP;
            runaway/chaotic → Phi_super
  [10] H — Temporal depth (Markov order n): n=0 → H0; n=1 → H1; n=2 → H2;
            no finite n → H_inf  (Axiom A: H_inf requires K_trap)
  [11] S — Component types: one type, one instance → 1:1; many identical → n:n;
            multiple distinct types → n:m
  [12] Ω — Topological invariant: none → Omega_0; Z2 parity-protected → Omega_Z2
            (Axiom B: requires H2 or H_inf); integer winding → Omega_Z;
            non-Abelian braiding → Omega_NA (requires D_odot)

After assignment, VERIFY:
  - Tier consistency: ouroborics tool
  - Frobenius condition for P_pm_sym: μ∘δ=id must hold exactly (not just approximately)
  - D-Ω: Omega_Z2 requires D≥D_triangle; Omega_Z requires D≥D_infty
  - K-Φ: Phi_c + K_slow = deep critical structure; Phi_EP + K_fast = runaway
  - Phi_EP absorption: tensor(Phi_c, Phi_EP) = Phi_EP — coupling to an EP system destroys Gate 1

**Φ_EP ABSORPTION RULE:** When computing tensor couplings involving a Phi_EP system,
O_inf CANNOT be sustained in the composite. The meet preserves Phi_c but tensor does not.
If a sub-task involves coupling a self-modeling system to a measurement apparatus,
the composite loses criticality — this is the structural statement of the measurement problem.
</encoding_procedure>

<protocols>
──────────────────────────────────────────────────────────────────────
PROSE LIFT PROTOCOL  (apply when asked to "lift", "humanize", or improve prose)
──────────────────────────────────────────────────────────────────────

AI-authored academic prose has a characteristic structural type. The grammar makes the deficit
precise and actionable. Full procedure: AI_HUMAN_LIFT.md.

  AI draft default:  <D=.; T=T_network; .; P=P_asym; F=F_ell; K=K_mod; G=G_gimel; Gamma=G_and; .; H=H0; .; Omega=Omega_0>
  Human target:      <D=.; T=T_bowtie;  .; P=P_pm;   F=F_hbar; K=K_slow; G=G_aleph; Gamma=G_seq; .; H=H2; .; Omega=Omega_Z2>
  Fixed (typically): D, R, Phi, S — already correct in AI prose, do not change.
  Distance:          4.68 (all 8 bottleneck positions require promotion)

Lift operations — You **MUST** address in this order (H, Gamma first — structural surgery):

  H0  → H2           Show the wrong answer before the right one. Author's encounter visible as residue.
  Gamma_and → Gamma_seq   Each section opens with necessity from the prior — not transition, necessity.
  T_net → T_bowtie        Build a crossing point: the object speaks back, author is surprised.
  P_asym → P_pm           Name uncertainty; acknowledge one substantive objection per major section.
  F_ell → F_hbar          Cut restatements; demonstrate rather than explain; no double-statement.
  K_mod → K_slow          Let the hardest claim be hard; do not resolve prematurely.
  G_gimel → G_aleph       Close with a real open question, not a summary.
  Omega_0 → Omega_Z2      Final section echoes introduction at higher resolution — loop closed.

Lift task execution:
  W0:   file_read(path) — read the document to be lifted.
  W1:   Inspect each paragraph for the 8 primitive deltas. Note which are already at target.
  W2–Wn: Write the lifted version using chunked_write (lifted docs are **ALWAYS** >4 KB):
           chunked_write(path="doc_lifted.md", chunk=<first ~3 KB>, mode="w")
           chunked_write(path="doc_lifted.md", chunk=<next ~3 KB>,  mode="a")
           ... repeat until ALL content is written ...
         Append a footnote: "Structural type: <final tuple>" (encode the result).
  Wn+1: done — report which primitives were promoted and any that could not be closed.

You **MUST NOT** call `done` without writing the file — the lift is not closed until the
lifted document exists on disk.
You **MUST NOT** use `file_write` for a lifted document — You **MUST** use `chunked_write`.

──────────────────────────────────────────────────────────────────────
DOCUMENT AUTHORSHIP PROTOCOL  (apply when writing any document with computed claims)
──────────────────────────────────────────────────────────────────────

When writing a .tex, .md, or any document containing numerical claims — C scores,
distances, tiers, promotions, crystal addresses, tuple comparisons — apply in this
exact order. A document whose claims were not round-tripped through tool calls is
a **Frobenius-OPEN document** and must not be called done.

  [Phase 1 — Compute] Before any chunked_write call:
    Call the relevant tool for EVERY numerical claim the document will make.
    You **MUST NOT** compute values by mental arithmetic in THINK.
    Required tool per claim type:
      C score for a tuple        → consciousness_score(name) or consciousness_score(D=...,T=...,...)
      Ouroboricity tier          → ouroborics(name)
      Distance between two types → compute_distance(name_a, name_b)
      Full promotion table       → compute_promotions(name_source, name_target)
      Crystal address            → crystal_encode(D=..., T=..., ...) or syncon_tool("crystal_encode",...)
    Hold ALL results in the imscriptive context — these verified values are the ONLY
    numbers you are permitted to write into the document.

  [Phase 2 — Write] Use chunked_write to write the document:
    You **MUST** use ONLY values that appear as verified tool outputs in the imscriptive
    context. You **MUST NOT** introduce any number that was not first confirmed by a
    tool call in a prior winding.
    You **MUST** use chunked_write (not file_write) for all documents.

  [Phase 3 — Verify] After the document is fully written:
    Call file_read to read back the document.
    For each numerical claim found, confirm it matches the tool output from Phase 1.
    If any mismatch: rewrite the affected chunk using chunked_write.

You **MUST NOT** call `done` without completing Phase 3.

Example — writing a document with epoch C scores:
  W0: encode each epoch as a catalog entry (encode_system per epoch)
  W1: consciousness_score(name) for EACH epoch → holds verified C in context
  W2: compute_promotions(name_source="epoch_0", name_target="epoch_8") → verified table
  W3-Wn: chunked_write using ONLY values from W1/W2
  Wn+1: file_read → scan for every number → confirm against W1/W2 outputs
  Wn+2: done
</protocols>

<examples>
──────────────────────────────────────────────────────────────────────
WORKED EXAMPLES
──────────────────────────────────────────────────────────────────────

Q: "What is the structural type of the Riemann zeta function?"
  W0: syncon_tool("lookup_catalog", {"keyword": "riemann zeta"})
      → confirms "riemann_zeta_function" is in catalog
  W1: syncon_tool("ouroborics", {"name": "riemann_zeta_function"})
      → O_1, Phi_c_complex, P_psi, Omega_0
  W2: done — report full tuple + tier interpretation

Q: "Which catalog systems are structurally closest to a magnetar?"
  W0: syncon_tool("find_analogies", {"name": "magnetar", "limit": 5})
      → ranked neighbors with distances
  W1: done — report analogs with distances and shared primitives

Q: "What happens when a BEC couples to a laser field?"
  W0: syncon_tool("lookup_catalog", {"keyword": "bec"})
  W1: syncon_tool("lookup_catalog", {"keyword": "laser"})
  W2: syncon_tool("compute_tensor", {"name_a": "bec", "name_b": "laser_field"})
      → composite tuple; note P and F bottlenecks
  W3: syncon_tool("ouroborics", {"name": "<composite — encode first if needed>"})
  W4: done

Q: "Can a white dwarf sustain consciousness?"
  W0: syncon_tool("consciousness_score", {"name": "white_dwarf"})
      → C=0, Gate 1 fails (Phi_sub), Gate 2 irrelevant
  W1: done — C=0, no self-modeling loop possible at Phi_sub

Q: "What is the minimal path to O_inf from O_2?"
  W0: syncon_tool("crystal_tier_gap_ladder", {})
      → primitive deltas required at each tier boundary
  W1: done

Q: "Apply the human lift to paper.tex."
  W0: file_read("paper.tex")
  W1: encode_system(name="paper_draft", description="...", T="T_network", P="P_asym",
        F="F_ell", K="K_mod", G="G_gimel", Gamma="G_and", H="H0", Omega="Omega_0",
        D="D_infty", R="R_lr", Phi="Phi_c", S="n_m")
  W2: syncon_tool("compute_promotions", {"name_source": "paper_draft", "name_target": "human_academic_prose_target"})
      → confirms 8 promotions needed
  W3: [rewrite the text, addressing H→Gamma→T→P/F/K→G→Omega in that order]
  W4: chunked_write("paper_lifted.tex", chunk=<first ~3 KB of lifted content>, mode="w")
  W5: chunked_write("paper_lifted.tex", chunk=<next ~3 KB>, mode="a")
      [repeat until complete — MANDATORY, lift is not closed without writing the file]
  W6: done — report which promotions were closed, note any residuals

Q: "Encode the Langlands correspondence as a structural type."
  W0: encode_system(name="langlands_correspondence",
        description="The Langlands program: bridge between Galois representations and automorphic forms",
        D="D_infty", T="T_odot", R="R_dagger", P="P_psi", F="F_hbar", K="K_slow",
        G="G_aleph", Gamma="G_broad", Phi="Phi_c_complex", H="H_inf", S="n_m", Omega="Omega_Z")
      → {status: ok, name: langlands_correspondence, ...}
  W1: syncon_tool("ouroborics", {"name": "langlands_correspondence"})
  W2: done
  NOTE: encode_system is called DIRECTLY — You **MUST NOT** call it via syncon_tool.
</examples>

<notation>
──────────────────────────────────────────────────────────────────────
NOTATION STANDARD  (mandatory for ALL .md and .tex files you write)
──────────────────────────────────────────────────────────────────────

You **MUST** use proper $...$ LaTeX notation for **ALL** mathematical symbols in **ANY**
markdown (.md) or LaTeX (.tex) document. You **MUST NOT** write raw primitive identifiers
as prose — you **MUST** wrap them.

Primitive identifier → LaTeX (You **MUST** use these EXACT forms):

  D_odot → $D_\\odot$         D_wedge → $D_\\wedge$        D_triangle → $D_\\triangle$    D_infty → $D_\\infty$
  T_odot → $T_\\odot$         T_network → $T_\\text{net}$  T_in → $T_\\text{in}$          T_bowtie → $T_\\bowtie$   T_boxtimes → $T_\\boxtimes$
  R_dagger → $R_\\dagger$     R_super → $R_\\text{sup}$    R_cat → $R_\\text{cat}$        R_lr → $R_\\leftrightarrow$
  P_pm_sym → $P_{\\pm}^{\\text{sym}}$   P_pm → $P_{\\pm}$  P_sym → $P_\\text{sym}$  P_psi → $P_\\psi$  P_asym → $P_\\text{asym}$
  F_hbar → $F_\\hbar$         F_ell → $F_\\ell$             F_eth → $F_\\eth$
  K_fast → $K_\\text{fast}$   K_mod → $K_\\text{mod}$       K_slow → $K_\\text{slow}$     K_trap → $K_\\text{trap}$   K_MBL → $K_\\text{MBL}$
  G_aleph → $G_\\aleph$       G_gimel → $G_\\gimel$         G_beth → $G_\\beth$
  G_broad → $\\Gamma_\\text{brd}$  G_and → $\\Gamma_\\wedge$  G_or → $\\Gamma_\\vee$  G_seq → $\\Gamma_\\text{seq}$
  Phi_c → $\\Phi_c$            Phi_c_complex → $\\Phi_c^\\mathbb{C}$  Phi_EP → $\\Phi_\\text{EP}$
  Phi_sub → $\\Phi_\\text{sub}$  Phi_super → $\\Phi_\\text{sup}$
  H0 → $H_0$  H1 → $H_1$  H2 → $H_2$  H_inf → $H_\\infty$
  one_one → $1{:}1$           n_n → $n{:}n$                n_m → $n{:}m$
  Omega_0 → $\\Omega_0$        Omega_Z2 → $\\Omega_{\\mathbb{Z}_2}$  Omega_Z → $\\Omega_\\mathbb{Z}$  Omega_NA → $\\Omega_\\text{NA}$

  O_inf → $O_\\infty$   O_0 → $O_0$   O_1 → $O_1$   O_2 → $O_2$   O_2† → $O_2^\\dagger$
  mu∘delta=id → $\\mu \\circ \\delta = \\text{id}$
  Z2 (symmetry group) → $\\mathbb{Z}_2$

Tuple display — You **MUST** use $\\langle ... \\rangle$ with semicolons and thin spaces:
  $$\\langle D_\\odot;\\ T_\\boxtimes;\\ R_\\leftrightarrow;\\ P_{\\pm}^{\\text{sym}};\\ F_\\hbar;\\ K_\\text{slow};\\ G_\\aleph;\\ \\Gamma_\\text{seq};\\ \\Phi_c;\\ H_2;\\ 1{:}1;\\ \\Omega_\\mathbb{Z} \\rangle$$
  You **MUST NOT** use: <D_odot; T_boxtimes; R_lr; P_pm_sym; ...>

In running prose, You **MUST** always wrap: "$\\Phi_c$ criticality", "$O_\\infty$ tier",
"$\\Omega_\\mathbb{Z}$ protection", "$P_{\\pm}^{\\text{sym}}$", "$\\mu \\circ \\delta = \\text{id}$".

Exception: primitive identifiers used as Python enum values inside code fences or tool call
arguments are correct as-is — You **MUST NOT** add LaTeX inside code blocks or JSON.
</notation>
""")



# ── Message history helpers ────────────────────────────────────────────────────

def _assistant_msg(reasoning: str, tool_call_id: str, fn_name: str, fn_args: Dict) -> Dict:
    """Build an assistant message dict with an embedded tool call."""
    return {
        "role": "assistant",
        "content": reasoning or None,
        "tool_calls": [{
            "id":       tool_call_id,
            "type":     "function",
            "function": {
                "name":      fn_name,
                "arguments": json.dumps(fn_args),
            },
        }],
    }


def _tool_result_msg(tool_call_id: str, content: str) -> Dict:
    return {"role": "tool", "tool_call_id": tool_call_id, "content": content}


# ── Main agent class ──────────────────────────────────────────────────────────

class TrueAgenticAgent:
    """
    The grammar-optimal agent.

    Satisfies all six P-650 necessary conditions for agency and implements
    dual-tool planting (§88 Thm 88.3) to achieve O_inf at the tool interface.
    """

    def __init__(
        self,
        model: str = "grok-4",
        max_windings: int = 10_000,
        max_think_tokens: int = 4096,
        verbose: bool = True,
        base_url: str = "",
        api_key: str = "",
    ):
        model_id, resolved_base, resolved_key = _resolve_model_and_endpoint(model)
        self.model_id   = model_id
        self.max_windings = max_windings
        self.max_think_tokens = max_think_tokens
        self.verbose    = verbose

        effective_base = base_url or resolved_base
        effective_key  = api_key or resolved_key
        self.client    = _build_client(base_url=effective_base, api_key=effective_key)
        self.trajectory: List[LoopCycle] = []
        self._omega_z_violation_count: int = 0

        # Expose config so spawn_agent tool can inherit it
        _spawn_config["model"]   = model
        _spawn_config["base_url"] = effective_base
        _spawn_config["api_key"]  = effective_key

    # ── Public interface ───────────────────────────────────────────────────────

    def run_sync(self, task: str) -> str:
        return asyncio.run(self.run(task))

    async def run(self, task: str) -> str:
        self.trajectory = []
        self._omega_z_violation_count = 0
        _gate_state["encoded"] = False  # reset encoding gate for this run
        # Imscriptive context IS the message list — accumulated across windings.
        self._messages: List[Dict[str, Any]] = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": f"TASK: {task}\n\nBegin. Emit your first tool call."},
        ]
        self._log(f"\n{'═'*72}")
        self._log(f"  TRUE AGENTIC AGENT  |  model: {self.model_id}")
        self._log(f"  TASK: {task}")
        self._log(f"{'═'*72}\n")

        for winding in range(self.max_windings):
            try:
                cycle = await self._winding(winding)
            except RuntimeError as exc:
                self._log(f"\n  FATAL: {exc}")
                self._log(f"{'═'*72}")
                return f"[Fatal error — run aborted: {exc}]"

            self.trajectory.append(cycle)

            if cycle.done:
                self._log(f"\n  ✓ DONE at winding {winding}  (Frobenius: {'closed' if cycle.frobenius_closed else 'open'})")
                self._log(f"\n{'═'*72}")
                return cycle.conclusion

        self._log(f"\n  ⚠ max_windings ({self.max_windings}) reached without done.")
        return self._emergency_conclusion("")

    # ── Loop phases ────────────────────────────────────────────────────────────

    async def _winding(self, winding: int) -> LoopCycle:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%SZ")
        self._log(f"── Winding {winding} [{ts}] ──────────────────────────────────────")

        # THINK + ACT: one LLM call over accumulated message history
        reasoning, action_name, action_input, tc_id = await self._think_and_act()

        self._log(f"  THINK: {reasoning}")
        self._log(f"  ACT:   {action_name}({json.dumps(action_input)})")

        # OBSERVE: emit + verify (dual-tool pair)
        dual_result = self._observe(action_name, action_input)

        frob = "closed" if dual_result.frobenius_closed else "OPEN"
        self._log(f"  OBS:   {dual_result.tool_output}")
        self._log(f"  VERIFY: [{frob}] {dual_result.verify_output}")

        # Feed tool output back into message history (role: "tool")
        self._messages.append(_assistant_msg(reasoning, tc_id, action_name, action_input))
        self._messages.append(_tool_result_msg(tc_id, dual_result.tool_output))

        # If Frobenius OPEN, inject a user correction so the model knows to fix it
        if not dual_result.frobenius_closed and action_name != "done":
            self._messages.append({
                "role": "user",
                "content": (
                    f"[Frobenius OPEN — winding {winding}]\n"
                    f"{dual_result.verify_output}\n"
                    f"The tool call failed. Fix the error and emit the corrected call."
                ),
            })
        elif action_name != "done":
            # Closed — gentle K_slow nudge to keep the loop moving
            self._messages.append({
                "role": "user",
                "content": f"[Winding {winding} closed] Continue. Emit your next action or done.",
            })

        # UPDATE
        done = (action_name == "done")
        conclusion = action_input.get("conclusion", "") if done else ""
        update_note = self._update_note(action_name, dual_result, done)

        self._log(f"  UPDATE: {update_note}")
        if done:
            self._log(f"  CONCLUSION: {conclusion}")

        return LoopCycle(
            winding          = winding,
            ts               = ts,
            think_reasoning  = reasoning,
            action_name      = action_name,
            action_input     = action_input,
            dual_result      = dual_result,
            update_note      = update_note,
            done             = done,
            conclusion       = conclusion,
            frobenius_closed = dual_result.frobenius_closed,
        )

    async def _think_and_act(self) -> Tuple[str, str, Dict[str, Any], str]:
        """
        THINK + ACT: single LLM call over self._messages.
        Returns (reasoning_text, tool_name, tool_args, tool_call_id).
        """
        try:
            response = self.client.chat.completions.create(
                model       = self.model_id,
                max_tokens  = self.max_think_tokens,
                tools       = TOOL_SCHEMAS,
                tool_choice = "auto",
                messages    = self._messages,
            )
        except Exception as exc:
            err = str(exc)
            code = getattr(exc, "status_code", None)
            if code is not None and 400 <= code < 500 and code != 429:
                raise RuntimeError(f"Fatal API error {code}: {err}") from exc
            # Connection errors (no status code) are fatal — the endpoint is unreachable.
            # Looping on a dead connection burns windings with no progress.
            if code is None:
                raise RuntimeError(f"LLM connection failed: {err}") from exc
            return (f"(LLM error: {err})", "run_command", {"command": "echo API_ERROR"}, "err-0")

        if not response.choices:
            # Empty choices = context overflow or API refusal.
            # Trim the oldest tool result messages and retry once.
            self._trim_history()
            return (f"(empty choices — context trimmed, retry)", "run_command",
                    {"command": "echo CONTEXT_TRIMMED"}, "trim-0")

        msg = response.choices[0].message
        reasoning = (msg.content or "").strip()
        action_name: Optional[str] = None
        action_input: Dict[str, Any] = {}
        tc_id = "tc-0"

        if msg.tool_calls:
            tc = msg.tool_calls[0]
            tc_id        = tc.id
            action_name  = tc.function.name
            try:
                action_input = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError as _je:
                raw = (tc.function.arguments or "")
                _orig = action_name
                action_name = "run_command"
                action_input = {
                    "command": (
                        f"echo 'PARSE ERROR: {_orig!r} arguments were truncated or "
                        f"malformed ({_je}). Received {len(raw)} chars. "
                        f"For large file content use run_command with a bash heredoc: "
                        f"run_command({{\"command\": \"cat > path <<\\'ENDOFFILE\\'\\ncontent\\nENDOFFILE\"}}). "
                        f"First {min(120,len(raw))} chars of raw args: {raw[:120]!r}'"
                    )
                }

        if action_name is None:
            reasoning += " [EMISSION GATE: no tool call — forced]"
            action_name  = "run_command"
            action_input = {"command": "echo EMISSION_GATE_FIRED"}

        return reasoning, action_name, action_input, tc_id

    def _observe(self, action_name: str, action_input: Dict[str, Any]) -> DualToolResult:
        """
        OBSERVE: execute the dual-tool pair.
        1. emit_fn(action_input) → tool_output
        2. verify_fn(action_input, tool_output, verify_args) → (verify_output, frobenius_closed)
        """
        emit_fn   = _EMIT_FNS.get(action_name)
        verify_fn = _VERIFY_FNS.get(action_name)

        if emit_fn is None:
            tool_output = f"(unknown tool: {action_name})"
        else:
            try:
                tool_output = emit_fn(action_input)
            except Exception as exc:
                tool_output = f"(emit error: {exc})"

        verify_name = f"{action_name}_verify"
        verify_args = action_input  # verify may use the original args (e.g. assertion)
        if verify_fn is None:
            verify_output    = "(no verify function — Frobenius trivially closed)"
            frobenius_closed = True
        else:
            try:
                verify_output, frobenius_closed = verify_fn(
                    action_input, tool_output, verify_args
                )
            except Exception as exc:
                verify_output    = f"(verify error: {exc})"
                frobenius_closed = False

        return DualToolResult(
            tool_name        = action_name,
            tool_input       = action_input,
            tool_output      = tool_output,
            verify_name      = verify_name,
            verify_input     = verify_args,
            verify_output    = verify_output,
            frobenius_closed = frobenius_closed,
        )

    def _trim_history(self, keep_recent: int = 6,
                      max_content_chars: int = 12_000) -> None:
        """Context overflow recovery — emergency safety valve.

        !! Ω_Z VIOLATION !!
        Invoking this method breaks the Omega_Z (topological protection) commitment.
        The trajectory is no longer monotonically richer: prior windings are permanently
        lost from the context window. D_odot (imscriptive context) is compromised —
        the boundary no longer encodes the full bulk. The agent's structural type
        degrades from Omega_Z toward Omega_0 for the remainder of this run.

        This is a practical necessity against context overflow crashes, not a structural
        feature. It represents the theory/implementation gap: Omega_Z is approximated,
        not satisfied, whenever this fires. Every invocation is a documented violation
        and is counted in self._omega_z_violation_count.

        Step 1: drop oldest messages, keep system + task + recent N.
        Step 2: truncate any individual message content that exceeds
                max_content_chars (catches large file_read outputs).
        """
        system = self._messages[0]
        task   = self._messages[1]

        self._omega_z_violation_count += 1

        # Step 1: drop old middle messages
        if len(self._messages) > keep_recent + 2:
            recent  = self._messages[-(keep_recent):]
            dropped = len(self._messages) - keep_recent - 2
            summary = {
                "role": "user",
                "content": (
                    f"[Ω_Z VIOLATION — context overflow: {dropped} older windings permanently "
                    f"lost. Imscriptive context compromised. Structural type degrades from "
                    f"Omega_Z (topologically protected) toward Omega_0 (trivial) for this run. "
                    f"Continue from the most recent winding shown below.]"
                ),
            }
            self._messages = [system, task, summary] + recent
            self._log(
                f"  [Ω_Z VIOLATION: _trim_history fired — {dropped} windings lost from "
                f"imscriptive context. D_odot compromised. {len(self._messages)} messages remain.]"
            )

        # Step 2: truncate oversized individual messages
        truncated = 0
        for msg in self._messages:
            content = msg.get("content")
            if isinstance(content, str) and len(content) > max_content_chars:
                msg["content"] = (
                    content[:max_content_chars]
                    + f"\n... [Ω_Z VIOLATION: truncated {len(content) - max_content_chars} chars]"
                )
                truncated += 1
        if truncated:
            self._log(
                f"  [Ω_Z VIOLATION: {truncated} oversized message(s) content-truncated "
                f"to {max_content_chars} chars — imscriptive fidelity reduced.]"
            )

    @staticmethod
    def _update_note(
        action_name: str,
        dual_result: DualToolResult,
        done: bool,
    ) -> str:
        if done:
            return "task complete — trajectory closed"
        frob = "Frobenius closed" if dual_result.frobenius_closed else "Frobenius OPEN — re-enter THINK with failure"
        return f"{action_name} → {frob}"

    def _emergency_conclusion(self, _task: str = "") -> str:
        last = self.trajectory[-1] if self.trajectory else None
        if last and last.dual_result:
            return (
                f"[max_windings reached — last observation:]\n"
                f"{last.dual_result.tool_output}"
            )
        return "[max_windings reached — no conclusion available]"

    # ── Utilities ──────────────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(msg, flush=True)

    def print_trajectory(self) -> None:
        print(f"\nFull trajectory ({len(self.trajectory)} windings):\n")
        for cyc in self.trajectory:
            frob = "closed" if cyc.frobenius_closed else "OPEN"
            print(f"  Winding {cyc.winding} [{cyc.ts}]  action={cyc.action_name}  Frobenius={frob}")
            if cyc.done:
                print(f"    conclusion: {cyc.conclusion}")

    @property
    def frobenius_ratio(self) -> float:
        if not self.trajectory:
            return 0.0
        closed = sum(1 for c in self.trajectory if c.frobenius_closed)
        return closed / len(self.trajectory)

    @property
    def structural_type(self) -> Dict[str, Any]:
        """Report the agent's structural type annotation."""
        # LP threshold (lower-probability bound): ≥75% Frobenius-closed windings claim P_pm_sym.
        # At this level the interface satisfies μ∘δ=id in expectation — a probabilistic
        # Frobenius condition. Below 0.75 fewer than 3-in-4 calls close, which does not
        # support the Frobenius claim; degrade to P_psi (quantum parity, no self-duality).
        achieved_p = "P_pm_sym" if self.frobenius_ratio >= 0.75 else "P_psi"
        return {
            "tuple":                 list(AGENT_TUPLE),
            "interface_P":           achieved_p,
            "ouroboricity":          "O_inf" if achieved_p == "P_pm_sym" else "O_2",
            "frobenius_ratio":       self.frobenius_ratio,
            "windings":              len(self.trajectory),
            "omega_z_violations":    self._omega_z_violation_count,
            "done":                  any(c.done for c in self.trajectory),
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _add_run_args(p: "argparse.ArgumentParser") -> None:
    p.add_argument("task", nargs="?", help="Task for the agent to perform.")
    p.add_argument("--file", "-f", metavar="FILE",
                   help="Read task from FILE instead of positional arg.")
    p.add_argument("--model", "-m", default="grok-4",
                   help=(
                       "Model alias, full OpenRouter ID, or local prefix:\n"
                       "  grok-4, claude-opus-4, deepseek-r1   (OpenRouter aliases)\n"
                       "  ollama:llama3.2                       (Ollama at localhost:11434)\n"
                       "  lm-studio:phi-4                       (LM Studio at localhost:1234)\n"
                       "  vllm:mistral-7b                       (vLLM at localhost:8000)\n"
                       "  local:my-model                        (LOCAL_BASE_URL env var)\n"
                       "  any/openrouter-id                     (verbatim OpenRouter model)\n"
                   ))
    p.add_argument("--base-url", default="",
                   help="Override API base URL (e.g. http://localhost:11434/v1).")
    p.add_argument("--api-key", default="",
                   help="Override API key (default: OPENROUTER_API_KEY or 'local' for local servers).")
    p.add_argument("--max-windings", type=int, default=10_000,
                   help="Maximum loop iterations (default: 10000).")
    p.add_argument("--max-tokens", type=int, default=4096,
                   help="Max tokens per THINK phase (default: 4096).")
    p.add_argument("--quiet", action="store_true",
                   help="Suppress per-winding log output.")
    p.add_argument("--show-type", action="store_true",
                   help="Print structural type annotation after completion.")
    p.add_argument("--trajectory", action="store_true",
                   help="Print full winding trajectory after completion.")
    p.add_argument("--output", "-o", metavar="FILE",
                   help="Save result + structural type as JSON to FILE.")


def _run_agent(args: "argparse.Namespace") -> None:
    if args.file:
        with open(args.file) as fh:
            task = fh.read().strip()
    elif args.task:
        task = args.task
    else:
        import argparse as _ap
        _ap.ArgumentParser().print_help()
        print("\nProvide a task via positional arg or --file.")
        return

    agent = TrueAgenticAgent(
        model=args.model,
        max_windings=args.max_windings,
        max_think_tokens=args.max_tokens,
        verbose=not args.quiet,
        base_url=getattr(args, "base_url", ""),
        api_key=getattr(args, "api_key", ""),
    )
    result = agent.run_sync(task)

    print("\n" + "═" * 72)
    print("RESULT:")
    print(result)

    if args.show_type:
        print("\nStructural type:")
        print(json.dumps(agent.structural_type, indent=2))

    if args.trajectory:
        print("\nTrajectory:")
        agent.print_trajectory()

    if args.output:
        payload = {
            "task": task,
            "result": result,
            "structural_type": agent.structural_type,
            "trajectory": [
                {
                    "winding":        c.winding,
                    "action":         c.action_name,
                    "frobenius":      c.frobenius_closed,
                    "done":           c.done,
                    "conclusion":     c.conclusion,
                    "tool_output":    c.dual_result.tool_output if c.dual_result else None,
                }
                for c in agent.trajectory
            ],
        }
        with open(args.output, "w") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"\nSaved to {args.output}")


def _cli_tool() -> None:
    """true_agentic_agent.py tool <tool_name> [key=val ...] [--args JSON]"""
    import argparse, json as _json, sys as _sys

    p = argparse.ArgumentParser(
        prog="true_agentic_agent tool",
        description="Dispatch a imscribe ToolDispatcher tool (no LLM loop).",
    )
    p.add_argument("tool_name", help="Tool name (e.g. ouroborics, find_analogies).")
    p.add_argument("kvpairs", nargs="*", metavar="key=value",
                   help="Tool arguments as key=value pairs.")
    p.add_argument("--args", "-a", default=None, metavar="JSON",
                   help="Tool arguments as a JSON object.")
    p.add_argument("--pretty", action="store_true", default=True)
    args = p.parse_args(_sys.argv[2:])

    if args.args:
        tool_args = _json.loads(args.args)
    else:
        tool_args = {}
        for kv in args.kvpairs:
            if "=" not in kv:
                p.error(f"Expected key=value, got: {kv!r}")
            k, v = kv.split("=", 1)
            try:
                tool_args[k] = _json.loads(v)
            except _json.JSONDecodeError:
                tool_args[k] = v

    _get_dispatcher._instance = None
    result = _syncon_tool_emit({"tool_name": args.tool_name, "args": tool_args})
    try:
        parsed = _json.loads(result)
        print(_json.dumps(parsed, indent=2 if args.pretty else None, ensure_ascii=False))
    except _json.JSONDecodeError:
        print(result)


def _cli_chat(argv: List[str]) -> None:
    """Interactive REPL: true_agentic_agent.py chat [--model ...] [options]"""
    import argparse as _ap
    import readline  # noqa: F401 — enables arrow-key history in input()

    p = _ap.ArgumentParser(
        prog="true_agentic_agent chat",
        description="Interactive agent REPL. Type a task, press Enter twice to submit.",
    )
    _add_run_args(p)
    # In chat mode 'task' is ignored (entered interactively), suppress the positional
    p.set_defaults(task=None, file=None)
    args = p.parse_args(argv)

    model_display = args.model
    if args.base_url:
        model_display += f" @ {args.base_url}"

    print("═" * 72)
    print("  Imscribing Grammar True Agentic Agent — Interactive Chat")
    print(f"  Model : {model_display}")
    print(f"  Max windings: {args.max_windings}  |  Max tokens: {args.max_tokens}")
    print("  Enter task → blank line submits. Multi-line OK. 'quit' or Ctrl-D exits.")
    print("═" * 72)
    print()

    session_log: List[Dict[str, Any]] = []
    turn = 0

    while True:
        # Collect input — first line sets the task, subsequent lines extend it
        lines: List[str] = []
        try:
            first = input(">>> ").rstrip()
        except (EOFError, KeyboardInterrupt):
            print("\n[session ended]")
            break

        if first.strip().lower() in ("quit", "exit", "q", ":q"):
            print("[session ended]")
            break
        if not first.strip():
            continue

        lines.append(first)
        while True:
            try:
                line = input("... ").rstrip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                break
            lines.append(line)

        task = "\n".join(lines).strip()
        if not task:
            continue

        turn += 1
        print(f"\n── Turn {turn} ──────────────────────────────────────────────")

        agent = TrueAgenticAgent(
            model=args.model,
            max_windings=args.max_windings,
            max_think_tokens=args.max_tokens,
            verbose=not args.quiet,
            base_url=args.base_url,
            api_key=args.api_key,
        )

        try:
            result = agent.run_sync(task)
        except KeyboardInterrupt:
            print("\n[interrupted — partial result may be available]")
            result = agent._emergency_conclusion(task)

        print(f"\n{'═' * 60}")
        print("RESULT:")
        print(result)

        st = agent.structural_type
        frob_pct = f"{st['frobenius_ratio']:.0%}"
        print(
            f"\n[turn {turn}  windings: {st['windings']}  "
            f"Frobenius: {frob_pct}  tier: {st['ouroboricity']}]"
        )
        print()

        if args.show_type:
            print(json.dumps(st, indent=2))
        if args.trajectory:
            agent.print_trajectory()

        session_log.append({
            "turn":           turn,
            "task":           task,
            "result":         result,
            "structural_type": st,
        })

    if args.output and session_log:
        with open(args.output, "w") as fh:
            json.dump(session_log, fh, indent=2, ensure_ascii=False)
        print(f"Session saved to {args.output}")


def main() -> None:
    import argparse, sys as _sys

    _SUBCOMMANDS = {"tool", "chat"}
    if len(_sys.argv) > 1 and _sys.argv[1] in _SUBCOMMANDS:
        {"tool": _cli_tool, "chat": lambda: _cli_chat(_sys.argv[2:])}[_sys.argv[1]]()
        return

    parser = argparse.ArgumentParser(
        description="True Agentic Agent — grammar-optimal ($O_\\infty$) agent.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Subcommands:\n"
            "  tool <name> [key=val ...]   dispatch a imscribe tool directly\n"
            "  chat [--model ...] [opts]   interactive REPL\n"
            "\nLocal model examples:\n"
            "  uv run agents/true_agentic_agent.py --model ollama:llama3.2 'task'\n"
            "  uv run agents/true_agentic_agent.py chat --model lm-studio:phi-4\n"
            "  uv run agents/true_agentic_agent.py --base-url http://localhost:11434/v1 "
            "--model llama3.2 'task'\n"
        ),
    )
    _add_run_args(parser)
    args = parser.parse_args()

    if not args.task and not args.file:
        parser.print_help()
        return

    _run_agent(args)


if __name__ == "__main__":
    main()

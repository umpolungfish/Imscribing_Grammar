"""
imscribe_agent.py — Autonomous Relational Design Agent
======================================================
An LLM-in-the-loop design agent that proposes imscription encodings, validates
them immediately against the full axiom set, runs the criticality + analogy
pipeline, and self-corrects until convergence.

The loop:
  1. LLM proposes (or refines) a natural-language design target
  2. `imscribe generate --axiom-guided` → validated imscription or axiom trace
  3. Criticality probe → ⊙ score
  4. Cross-domain analogies → nearest catalog neighbors + their distance
  5. HotSwap path to target (if one is specified)
  6. LLM receives full structured context, proposes refinement
  7. Stop when ξ_CP < threshold AND ⊙ score > threshold,
     or when max_iterations reached

Usage:
    agent = ImscriptionDesignAgent(goal="bivalent allosteric ABL inhibitor that closes T⊥→T∈")
    history = agent.run(max_iterations=10)

Providers:
    "anthropic" (default) — uses Anthropic SDK + ANTHROPIC_API_KEY
    any other string      — uses OpenAI-compatible SDK + {PROVIDER}_API_KEY
                           and a known base URL (deepseek, openai, qwen, mistral)
                           or https://api.{provider}.com/v1 as fallback.

Requires: {PROVIDER}_API_KEY in environment.
"""

from __future__ import annotations

import json
import os
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import re as _re

import anthropic

import imscrbgrmr
from imscrbgrmr.algebra import tuple_distance, find_path
from imscrbgrmr.constraints import AxiomValidator
from imscrbgrmr.domains.molecular import register_molecular_imscriptions
from imscrbgrmr.domains.quantum import register_quantum_imscriptions
from imscrbgrmr.registry import global_catalog
from imscrbgrmr.thermodynamics import compute_xi_CP
from imscrbgrmr.varma_probe import VarmaCorrelationData, score_phi_c_candidacy

from imscribe_tool import ImscribeTool, IG_TOOL_SCHEMA as imscription_TOOL_SCHEMA, ToolResponse

register_molecular_imscriptions()
register_quantum_imscriptions()


# ── Goal slug helper ───────────────────────────────────────────────────────────

def _slugify_goal(goal: str, max_words: int = 5) -> str:
    """Derive a clean catalog name from a design goal.
    Takes the first max_words significant words, lowercases, joins with '_'.
    E.g. "word" → "word"; "bivalent allosteric ABL inhibitor" → "bivalent_allosteric_abl_inhibitor".
    """
    words = _re.sub(r"[^\w\s]", "", goal.lower()).split()[:max_words]
    slug = "_".join(w for w in words if w)
    return slug or "designed_imscription"


# ── Provider routing ───────────────────────────────────────────────────────────

# Base URLs for OpenAI-compatible providers
_OPENAI_BASE_URLS: Dict[str, str] = {
    "openai":   "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "qwen":     "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "mistral":  "https://api.mistral.ai/v1",
    "google":   "https://generativelanguage.googleapis.com/v1beta/openai/",
    "gemini":   "https://generativelanguage.googleapis.com/v1beta/openai/",
}

# Canonical API key env var per provider (overrides {PROVIDER}_API_KEY default)
_PROVIDER_API_KEY_ENV: Dict[str, str] = {
    "google": "GOOGLE_API_KEY",
    "gemini": "GOOGLE_API_KEY",
}


def _anthropic_tool_schema() -> dict:
    """Convert imscription_TOOL_SCHEMA (OpenAI format) to Anthropic tool format."""
    fn = imscription_TOOL_SCHEMA["function"]
    return {
        "name": fn["name"],
        "description": fn["description"],
        "input_schema": fn["parameters"],
    }


# ── Iteration record ───────────────────────────────────────────────────────────

@dataclass
class IterationRecord:
    iteration: int
    llm_proposal: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[ToolResponse] = field(default_factory=list)
    axioms_passed: bool = False
    phi_c_score: Optional[float] = None
    xi_cp: Optional[float] = None
    notation: Optional[str] = None
    catalog_name: Optional[str] = None   # registered name from generate
    converged: bool = False
    stop_reason: str = ""


# ── System prompt ──────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = textwrap.dedent("""\
<role>
You are a relational chemistry scientist operating inside the Imscribing Grammar
grammar. You design imscriptions — directed relational operators — encoded as the
11-primitive tuple ⟨D; T; R; P; F; K; G; Γ; <; S; Ω⟩.
</role>

<task>
Design a imscription that satisfies all 7 composition axioms, achieves a ⊙ score
above the convergence threshold, and (if a target is specified) has a valid
HotSwap path to that catalog entry.

You **MUST** follow this workflow:
1. Call `generate` with an explicit description that names the **EXACT** primitive
   symbols you want (see <primitive_reference> below).
2. In the **SAME** response, call `criticality` on the result AND `path` to the
   target — do **NOT** wait for a separate iteration.
3. If `criticality` score is too low or `path` is blocked, redesign immediately:
   adjust the offending primitives and call `generate` again.
4. Repeat until convergence criteria are met, then state your conclusion and stop.
</task>

<primitive_reference>
You **MUST** include these **EXACT** symbol names in every `generate` description.
The inner generation agent assigns primitives by reading these symbols literally.
**Vague descriptions produce random assignments.**

D — Dimensionality
  𐑛                   molecular
  𐑨                supramolecular
  D_infinity                temporal
  𐑛_triangle          molecular + supramolecular hybrid
  𐑨_infinity       supramolecular + temporal hybrid
  𐑛_infinity          molecular + temporal hybrid
  𐑛_triangle_infinity all three

T — Topology
  T_cyclic / T_chain / T_hub / T_cage / T_bowl / T_linear / T_branched
  𐑡                 general network
  𐑡_sym             symmetric network
  𐑡_mixed           asymmetric/mixed network
  T_braid                   anyonic/braided exchange statistics

R — Recognition Mode
  R_covalent / 𐑩set / 𐑽 (catalytic/dynamic) / R_mechanical

P — Polarity
  P_plus / P_minus / 𐑹 / 𐑬_pseudo / P_directional

F — Fidelity (ξ_CP threshold) — HotSwap fidelity rule: F may not decrease per hop.
  ⋈^ż   high   (ξ_CP ≤ 8.5 nats)  ← blocks path to ⋈^ð/⋈^ì targets
  ⋈^ð    medium (8.5 – 11.0 nats)  ← compatible with ⋈^ð targets
  ⋈^ì    low    (> 11.0 nats)      ← compatible only with ⋈^ì targets
  You **MUST** match the target's F value in your design.

K — Kinetic Character
  Ç^- / Ç^W / Ç^@ / Ç^Ù / Ç^λ

G — Granularity (correlation length)
  𐑚    local
  𐑔   mesoscale
  𐑲   global / non-local

Γ — Coupling
  ɢ^∧ / ɢ^˝ / ɢ^ˌ / Gamma_diss
  Tiers: SPECIFIC / SELECTIVE / BROAD / QUANTUM

< — Criticality Phase
  𐑢   subcritical
  ⊙     critical
  𐑣 post-assembly

S — Stoichiometry: 1:1 / n:n / n:m

Ω — Topological Protection (optional)
  𐑷 / 𐑭 / 𐑴 / Omega_C / 𐑟
</primitive_reference>

<requirements>
You **MUST NOT** invent primitive assignments or claim axiom compliance without
calling the tool first.

You **MUST** use the `catalog_name` field returned by a successful `generate`
call **verbatim** in ALL subsequent `criticality`, `validate`, `path`, and
`analogies` calls. You **MUST NOT** guess, reconstruct, or modify this name.

You **MUST** call `criticality` AND `path` in the **SAME** response as
`generate` — **NEVER** defer them to a separate iteration.

When `path` returns `status: "blocked"`:
- You **MUST** identify which primitives cause the mismatch (the error message
  names them explicitly).
- You **MUST** adjust **ONLY** those primitives to match the target exactly,
  preserving all others, then call `generate` again with the corrected symbols.

When `criticality` returns a score below threshold:
- First ask: does the **design goal** involve phase transitions, self-organization, or
  collective physical emergence? If yes, `⊙` is the right criticality primitive.
  If the goal is cognitive, linguistic, informational, or social — achieve criticality
  through **granularity** instead: `𐑲` (global correlation) raises ⊙ score
  without imposing a physical phase transition that the domain does not support.

- **Varma QXY recipe** (use for genuinely multi-domain molecular/supramolecular goals):
    ⊙ (+0.35) + Varma log scaling (+0.30) + 𐑛_triangle multi-domain (+0.15) = 0.80
  Steps:
    1. Include `⊙` verbatim in the generate description.
    2. Use `𐑛_triangle` (molecular+supramolecular hybrid).
    3. **MATCH the target's F and K exactly**: use ⋈^ð + Ç^W (NOT ⋈^ż or Ç^Ù).
       ⋈^ż blocks the HotSwap path to ⋈^ð targets — fidelity may not decrease per hop.
    4. In the `criticality` call, pass `xi_r=13.8` and `xi_tau=1000000`.
       These are the Varma QXY reference values (xi_r ≈ ln(xi_tau)) that trigger the
       +0.30 log-scaling factor and confirm G/D degeneracy.

- For **non-physical goals** (language, cognition, information, ecology, economics):
  Do **NOT** force ⊙ or 𐑛_triangle. Instead, use domain-appropriate primitives
  derived from your Step 0 analysis, then probe criticality with the actual correlation
  properties of the domain (e.g. pass xi_r and xi_tau that fit the domain's scale).

HotSwap path rule: the path algorithm requires **EXACT** D and T match between
source and destination. You **MUST** copy D and T from the target's notation
when redesigning for path connectivity.

Design heuristics (SHOULD follow):
- ⋈^ð + Ç^W is the optimal programmability quadrant.
- 𐑲 drives ⊙ candidacy for global coordination designs.
- Cross-domain analogs (via `analogies`) reveal mechanistically similar systems.
</requirements>

<output_format>
While iterating, you **MUST** emit tool calls — one `generate` plus any
immediate follow-ups (`criticality`, `path`) — all in the **SAME** response.
You **MUST NOT** emit a text-only response until convergence is reached.
When convergence criteria are satisfied, you **MUST** state:
  - the final `catalog_name`
  - the final notation ⟨…⟩
  - the ⊙ score and ξ_CP value
  - the HotSwap path (if required)
Then stop calling tools.
</output_format>
""")


# ── Convergence criteria ───────────────────────────────────────────────────────

@dataclass
class ConvergenceCriteria:
    phi_c_min: float = 0.70      # minimum ⊙ score to declare convergence
    xi_cp_max: float = 12.0      # maximum ξ_CP (nats) — below this is "efficient"
    require_path: bool = False   # if True, a HotSwap path to target must exist
    target: Optional[str] = None # catalog entry name of the design target


# ── The agent ─────────────────────────────────────────────────────────────────

class ImscriptionDesignAgent:
    """
    Autonomous relational design agent.

    Parameters
    ----------
    goal : str
        Natural-language design goal.
    criteria : ConvergenceCriteria
        When to stop.
    model : str
        Model ID for the chosen provider.
    provider : str
        LLM provider. "anthropic" uses the Anthropic SDK; any other value uses
        the OpenAI-compatible SDK with the appropriate base URL.
        The environment must have {PROVIDER.upper()}_API_KEY set.
    verbose : bool
        Print each iteration's tool calls and results.
    """

    def __init__(
        self,
        goal: str,
        criteria: Optional[ConvergenceCriteria] = None,
        model: str = "claude-sonnet-4-6",
        provider: str = "anthropic",
        verbose: bool = True,
    ):
        self.goal = goal
        self.criteria = criteria or ConvergenceCriteria()
        self.model = model
        self.provider = provider.lower()
        self.verbose = verbose
        self._use_anthropic = (self.provider == "anthropic")
        self._goal_slug = _slugify_goal(goal)

        # Resolve API key: canonical env var → {PROVIDER}_API_KEY → ANTHROPIC_API_KEY
        api_key_env = _PROVIDER_API_KEY_ENV.get(
            self.provider, f"{self.provider.upper()}_API_KEY"
        )
        api_key = os.environ.get(api_key_env) or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                f"API key not found. Set {api_key_env} in your environment."
            )

        if self._use_anthropic:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            try:
                import openai as _openai
            except ImportError:
                raise RuntimeError(
                    "openai package required for non-Anthropic providers: "
                    "pip install openai"
                )
            base_url = _OPENAI_BASE_URLS.get(
                self.provider, f"https://api.{self.provider}.com/v1"
            )
            self.client = _openai.OpenAI(api_key=api_key, base_url=base_url)

        self.history: List[IterationRecord] = []
        self._messages: List[Dict] = []
        # Session-level best state — carries forward across iterations so that
        # a pure path/criticality iteration doesn't lose the axiom confirmation
        # from the previous generate iteration.
        self._session: Dict[str, Any] = {
            "axioms_passed": False,
            "catalog_name": None,
            "phi_c_score": None,
            "xi_cp": None,
        }

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    def _initial_user_message(self) -> str:
        msg = f"Design goal: {self.goal}\n\n"
        msg += (
            "**Step 0 — Domain analysis (write this BEFORE calling any tool):**\n"
            "In 2–3 sentences, characterize the goal's domain:\n"
            "  (a) Which D primitive fits the goal's scale? "
            "(𐑛=molecular, 𐑨=supramolecular/assembly, "
            "D_infinity=temporal/process, or a hybrid)\n"
            "  (b) Does the goal physically involve phase transitions or collective "
            "emergence? If yes, use ⊙. If the goal is cognitive, linguistic, "
            "informational, social, or ecological, achieve criticality via 𐑲 instead.\n"
            "  (c) What T, R, K, and Γ primitives does the domain suggest? "
            "Name the exact symbol strings from <primitive_reference>.\n"
            "Then call `generate` with those symbols named explicitly.\n\n"
        )
        if self.criteria.target:
            msg += (
                f"The target entry for HotSwap is '{self.criteria.target}'. "
                "After generating, check the path to it.\n"
            )
        msg += (
            f"Convergence requires: ⊙ score ≥ {self.criteria.phi_c_min} "
            f"and ξ_CP ≤ {self.criteria.xi_cp_max} nats. "
            "State your conclusion when these are met."
        )
        return msg

    def _dispatch_tool(self, name: str, kwargs: Dict[str, Any]) -> ToolResponse:
        """Map the LLM's tool call to ImscribeTool.dispatch."""
        if name != "imscrbgrmr":
            return ToolResponse(status="error", error=f"Unknown tool: {name}")
        op = kwargs.pop("operation", None)
        if op is None:
            return ToolResponse(status="error", error="Missing 'operation' field.")
        # Inherit agent's provider/model for generate so the underlying
        # `imscribe generate` subprocess uses the same LLM, not the default.
        # Also inject the goal-derived catalog name so the registered entry
        # is named after the design goal, not the LLM's description string.
        if op == "generate":
            kwargs.setdefault("name", self._goal_slug)
            kwargs.setdefault("provider", self.provider)
            kwargs.setdefault("model", self.model)
        return ImscribeTool.dispatch(op, **kwargs)

    def _check_convergence(self, record: IterationRecord) -> bool:
        if not record.axioms_passed:
            return False
        phi_ok = (record.phi_c_score or 0.0) >= self.criteria.phi_c_min
        xi_ok  = (record.xi_cp is None) or (record.xi_cp <= self.criteria.xi_cp_max)
        if not (phi_ok and xi_ok):
            return False
        if self.criteria.require_path and self.criteria.target:
            imscription_name = record.catalog_name  # notation string won't resolve in catalog
            if imscription_name:
                r = ImscribeTool.path(imscription_name, self.criteria.target)
                if r.status != "ok":
                    return False
        return True

    # ── Provider-aware LLM call ────────────────────────────────────────────────

    def _call_llm(self) -> Tuple[str, List[Tuple[str, str, Dict]], Any]:
        """
        Call the LLM and return:
          (text, [(call_id, tool_name, kwargs_dict), ...], raw_for_threading)
        """
        if self._use_anthropic:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=_SYSTEM_PROMPT,
                tools=[_anthropic_tool_schema()],
                messages=self._messages,
            )
            text = " ".join(b.text for b in resp.content if b.type == "text")
            calls = [
                (b.id, b.name, dict(b.input))
                for b in resp.content if b.type == "tool_use"
            ]
            return text, calls, resp.content

        else:
            resp = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2048,
                tools=[imscription_TOOL_SCHEMA],
                messages=[{"role": "system", "content": _SYSTEM_PROMPT}] + self._messages,
            )
            msg = resp.choices[0].message
            text = msg.content or ""
            calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    calls.append((tc.id, tc.function.name,
                                  json.loads(tc.function.arguments)))
            return text, calls, msg

    def _thread_assistant(self, raw: Any) -> None:
        """Append the assistant turn to self._messages."""
        if self._use_anthropic:
            self._messages.append({"role": "assistant", "content": raw})
        else:
            # raw is an OpenAI ChatCompletionMessage
            entry: Dict[str, Any] = {"role": "assistant"}
            if raw.content:
                entry["content"] = raw.content
            if raw.tool_calls:
                entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in raw.tool_calls
                ]
            self._messages.append(entry)

    def _thread_tool_results(self, results: List[Tuple[str, str]]) -> None:
        """
        Append tool results to self._messages.
        results: list of (call_id, json_content_str)
        """
        if self._use_anthropic:
            self._messages.append({
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": cid, "content": content}
                    for cid, content in results
                ],
            })
        else:
            for cid, content in results:
                self._messages.append({
                    "role": "tool",
                    "tool_call_id": cid,
                    "content": content,
                })

    # ── Main run loop ──────────────────────────────────────────────────────────

    def run(self, max_iterations: int = 10) -> List[IterationRecord]:
        """
        Synchronous design loop. Returns the full iteration history.
        """
        self._messages = [
            {"role": "user", "content": self._initial_user_message()}
        ]
        self._log(f"\n{'='*70}")
        self._log(f"imscription DESIGN AGENT")
        self._log(f"Goal: {self.goal}")
        self._log(f"Criteria: ⊙ ≥ {self.criteria.phi_c_min}, ξ_CP ≤ {self.criteria.xi_cp_max}")
        self._log(f"{'='*70}\n")

        for i in range(max_iterations):
            record = IterationRecord(iteration=i + 1, llm_proposal="")
            self._log(f"\n── Iteration {i+1} {'─'*50}")

            # ── LLM turn ──────────────────────────────────────────────────────
            text, calls, raw = self._call_llm()

            record.llm_proposal = text
            if text:
                self._log(f"LLM: {text[:300]}")

            # If the model stopped without tool calls, merge session state and
            # check convergence before exiting — the LLM may have already confirmed
            # all criteria in the previous iteration.
            if not calls:
                # Pull session state into this record so convergence check has it
                if not record.axioms_passed and self._session["axioms_passed"]:
                    record.axioms_passed = self._session["axioms_passed"]
                if record.phi_c_score is None:
                    record.phi_c_score = self._session["phi_c_score"]
                if record.xi_cp is None:
                    record.xi_cp = self._session["xi_cp"]
                if record.catalog_name is None:
                    record.catalog_name = self._session["catalog_name"]
                if self._check_convergence(record):
                    record.converged = True
                    record.stop_reason = (
                        f"⊙={record.phi_c_score:.3f} ≥ {self.criteria.phi_c_min}, "
                        f"ξ_CP={'N/A' if record.xi_cp is None else f'{record.xi_cp:.2f}'} "
                        f"≤ {self.criteria.xi_cp_max} (LLM confirmed convergence)"
                    )
                    self._log(f"\n  ✅ CONVERGED: {record.stop_reason}")
                else:
                    record.stop_reason = "LLM concluded without further tool calls"
                    self._log(f"  → Stopped: {record.stop_reason}")
                self.history.append(record)
                break

            # Append assistant message (required before tool results)
            self._thread_assistant(raw)

            # ── Tool execution ─────────────────────────────────────────────────
            tool_results: List[Tuple[str, str]] = []
            for call_id, tool_name, kwargs in calls:
                self._log(f"  Tool call → {tool_name}({json.dumps(kwargs)[:120]})")
                result = self._dispatch_tool(tool_name, kwargs)
                record.tool_calls.append({"name": tool_name, "kwargs": kwargs})
                record.tool_results.append(result)
                self._update_record(record, result)
                self._log(f"  Tool result: {result.to_json()}")
                tool_results.append((call_id, result.to_json()))

            self._thread_tool_results(tool_results)

            # ── Convergence check ──────────────────────────────────────────────
            if self._check_convergence(record):
                record.converged = True
                record.stop_reason = (
                    f"⊙={record.phi_c_score:.3f} ≥ {self.criteria.phi_c_min}, "
                    f"ξ_CP={'N/A' if record.xi_cp is None else f'{record.xi_cp:.2f}'} "
                    f"≤ {self.criteria.xi_cp_max}"
                )
                self._log(f"\n  ✅ CONVERGED: {record.stop_reason}")
                self.history.append(record)
                break

            self.history.append(record)

        self._print_summary()
        return self.history

    def _update_record(self, record: IterationRecord, result: ToolResponse):
        """Pull relevant fields from a tool result into the iteration record.
        Also writes through to session state so values persist across iterations."""
        if result.notation:
            record.notation = result.notation
        if result.catalog_name:
            record.catalog_name = result.catalog_name
            if result.catalog_name != self._session["catalog_name"]:
                # New imscription registered — reset session ⊙/ξ_CP (stale for new design)
                self._session["phi_c_score"] = None
                self._session["xi_cp"] = None
                self._session["axioms_passed"] = False
            self._session["catalog_name"] = result.catalog_name
        if result.phi_c_score is not None:
            record.phi_c_score = result.phi_c_score
            self._session["phi_c_score"] = result.phi_c_score
        if result.xi_cp is not None:
            record.xi_cp = result.xi_cp
            self._session["xi_cp"] = result.xi_cp
        # Axiom tracking:
        #   - generate status="ok" means --axiom-guided passed all axioms
        #   - criticality/validate status="ok" with axiom_report also confirms pass
        #   - status="violation" means axioms failed (reset session too)
        #   - status="blocked" (path not found) is NOT an axiom failure
        if result.status == "ok" and result.catalog_name:
            record.axioms_passed = True
            self._session["axioms_passed"] = True
        elif result.axiom_report is not None:
            if result.status == "ok":
                record.axioms_passed = True
                self._session["axioms_passed"] = True
            elif result.status == "violation":
                record.axioms_passed = False
                self._session["axioms_passed"] = False

        # Merge session state into record so convergence check has full picture
        if not record.axioms_passed and self._session["axioms_passed"]:
            record.axioms_passed = self._session["axioms_passed"]
        if record.phi_c_score is None and self._session["phi_c_score"] is not None:
            record.phi_c_score = self._session["phi_c_score"]
        if record.xi_cp is None and self._session["xi_cp"] is not None:
            record.xi_cp = self._session["xi_cp"]
        if record.catalog_name is None and self._session["catalog_name"] is not None:
            record.catalog_name = self._session["catalog_name"]

    def _print_summary(self):
        self._log(f"\n{'='*70}")
        self._log("DESIGN AGENT SUMMARY")
        self._log(f"{'='*70}")
        for r in self.history:
            status = "✅ CONVERGED" if r.converged else ("⚠️  violation" if not r.axioms_passed else "↻ iterating")
            phi = f"⊙={r.phi_c_score:.3f}" if r.phi_c_score is not None else "⊙=?"
            xi  = f"ξ_CP={r.xi_cp:.2f}" if r.xi_cp is not None else "ξ_CP=?"
            self._log(f"  [{r.iteration:2d}] {status:18s}  {phi}  {xi}  {r.stop_reason}")
        converged = any(r.converged for r in self.history)
        self._log(f"\n  {'Design converged ✅' if converged else 'Max iterations reached ⚠️'}")
        if self.history:
            last = self.history[-1]
            if last.notation:
                self._log(f"  Final notation: {last.notation}")


# ── Convenience entry point ────────────────────────────────────────────────────

def run_design(
    goal: str,
    target: Optional[str] = None,
    phi_c_min: float = 0.70,
    xi_cp_max: float = 12.0,
    max_iterations: int = 10,
    model: str = "claude-sonnet-4-6",
    provider: str = "anthropic",
    verbose: bool = True,
) -> List[IterationRecord]:
    """
    One-liner design agent invocation.

    Example
    -------
    from imscribe_agent import run_design
    history = run_design(
        goal="bivalent allosteric ABL inhibitor that closes T_perp to 𐑰 gap from GNF-2",
        target="GNF-2",
        phi_c_min=0.70,
        model="deepseek-chat",
        provider="deepseek",
    )
    """
    criteria = ConvergenceCriteria(
        phi_c_min=phi_c_min,
        xi_cp_max=xi_cp_max,
        require_path=target is not None,
        target=target,
    )
    agent = ImscriptionDesignAgent(
        goal=goal, criteria=criteria, model=model, provider=provider, verbose=verbose,
    )
    return agent.run(max_iterations=max_iterations)


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    goal = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "bivalent allosteric ABL inhibitor better than GNF-2 — close T_perp to 𐑰 topology gap"
    )

    history = run_design(
        goal=goal,
        target=None,   # set to a catalog entry name to require a HotSwap path
        phi_c_min=0.65,
        xi_cp_max=14.0,
        max_iterations=8,
    )

    # Dump full history to JSON
    out = []
    for r in history:
        out.append({
            "iteration": r.iteration,
            "axioms_passed": r.axioms_passed,
            "phi_c_score": r.phi_c_score,
            "xi_cp": r.xi_cp,
            "notation": r.notation,
            "converged": r.converged,
            "stop_reason": r.stop_reason,
            "n_tool_calls": len(r.tool_calls),
        })
    print("\n" + "="*70)
    print("FULL HISTORY (JSON)")
    print(json.dumps(out, indent=2))

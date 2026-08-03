"""
Translate a proof path (sequence of ProofSteps) into a conventional
mathematical proof sketch, via OpenRouter.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

from .graph import ProofStep, PRIMS
from .ops import OPERATIONS_BY_NAME

_TRANSCRIPT_DIR = Path(__file__).resolve().parent.parent.parent / "proof_transcripts"


def _stream_to_stdout(response) -> str:
    """Iterate a streaming chat completion, write chunks live, return full text."""
    parts: list[str] = []
    for chunk in response:
        delta = chunk.choices[0].delta
        piece = delta.content or getattr(delta, "reasoning_content", None) or ""
        if piece:
            sys.stdout.write(piece)
            sys.stdout.flush()
            parts.append(piece)
    sys.stdout.write("\n")
    sys.stdout.flush()
    content = "".join(parts)
    if not content:
        raise ValueError("Empty streaming response.")
    return content


def _get_client():
    try:
        import openai
    except ImportError:
        sys.exit("openai package required: uv add openai")
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        sys.exit("OPENROUTER_API_KEY not set.")
    return openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": os.environ.get(
                "OPENROUTER_REFERER",
                "https://github.com/umpolungfish/imscrbgrmr",
            ),
            "X-Title": "Imscribing Grammar Proof Path",
        },
    )


def _prim_label(prim: str) -> str:
    return {
        "⊢": "Dimensionality", "⊣": "Topology", ">": "Relational Mode",
        "<": "Parity/Symmetry", "⋈": "Fidelity", "⊤": "Kinetics",
        "∈": "Scope", "∋": "Interaction Grammar", "⊙": "Criticality",
        "⊥": "Chirality", "⊞": "Stoichiometry", "◻": "Topological Invariant",
    }.get(prim, prim)


def _format_step(i: int, step: ProofStep) -> str:
    op = OPERATIONS_BY_NAME.get(step.op_name)
    lines = [f"Step {i}: {step.op_name.replace('_', ' ')}"]
    lines.append(f"  From: {step.from_name}")
    lines.append(f"  To:   {step.to_name}")
    for prim, (old, new) in step.changes.items():
        lines.append(f"  {_prim_label(prim)} ({prim}): {old} → {new}")
    if op:
        lines.append(f"  Operation: {op.description}")
        lines.append(f"  Math: {op.math}")
    return "\n".join(lines)


_SYSTEM = """\
You are a mathematical proof assistant working with the Imscribing Grammar (IG), \
a 12-primitive coordinate system for mathematical and physical objects. \
IG primitives: Ð (Dimensionality), Þ (Topology), Ř (Relational Mode), \
Φ (Parity/Symmetry), ƒ (Fidelity), Ç (Kinetics), Γ (Scope), \
ɢ (Interaction Grammar), ⊙ (Criticality), Ħ (Chirality), \
Σ (Stoichiometry), Ω (Topological Invariant).

A proof path in IG is a sequence of named mathematical operations that transform \
the imscription (primitive tuple) of an open conjecture into the imscription of a \
proven result. Each operation corresponds to a real mathematical technique; \
each primitive change encodes a structural transformation of the mathematical object.

Your task: given the IG proof path below, produce a rigorous conventional \
mathematical proof sketch that follows exactly the same logical structure. \
Each IG step must correspond to a numbered mathematical argument. \
Be precise, use standard notation, and make the mathematical content genuinely \
correct. Do not mention IG terminology in the output — translate it entirely \
into conventional mathematics.

Proof-writing discipline:
- Take the most direct route. For each step, use the minimal exact-sequence or \
kernel/image argument that achieves the stated transition. Do not introduce \
auxiliary objects (e.g., Pic⁰, Néron-Severi group, associated graded pieces) \
unless they are logically necessary for that step — structural descriptions of \
the objects can appear only after the proof is complete.
- When cohomological machinery is invoked on a compact Kähler manifold, state \
the Hodge decomposition H^n(X,ℂ) = ⊕_{p+q=n} H^{p,q}(X) explicitly and \
identify maps to sheaf cohomology via Dolbeault's theorem H^q(X,Ω^p) ≅ H^{p,q}(X). \
Kernel and surjectivity arguments should name the Hodge component being killed, \
not just appeal vaguely to "a diagram chase" or "the ∂∂̄-lemma".
- Keep the proof and the structural commentary separated. A fact that holds \
because of the theorem (e.g., NS(X) injects into integral (1,1)-classes) is a \
corollary, not a proof step.
- Phrasing: describe the conjecture/theorem in terms of its mathematical content \
(e.g., "the Hodge conjecture for p = 1"), not in terms of proof-state metadata \
(e.g., "criticality resolved" or "the critical conjecture-state for k = 1").\
"""


def translate_path(
    steps: list[ProofStep],
    source_name: str,
    source_desc: str,
    target_name: str,
    target_desc: str,
    model: str = "google/gemini-2.5-flash-preview",
) -> str:
    if not steps:
        return "Source and target are identical — no proof path needed."

    step_text = "\n\n".join(_format_step(i + 1, s) for i, s in enumerate(steps))
    total_dist = sum(len(s.changes) for s in steps)

    user_msg = f"""\
PROOF PATH: {source_name} → {target_name}

Source: {source_name}
  {source_desc}

Target: {target_name}
  {target_desc}

Path ({len(steps)} steps, {total_dist} primitive transitions):

{step_text}

Produce a conventional mathematical proof sketch that follows this path exactly. \
Structure the output as:
1. One paragraph: state precisely what is being proved, using standard \
   mathematical terminology (theorem name, objects, and quantifiers).
2. Numbered proof steps, one per operation above. Each step must: \
   (a) identify the mathematical technique being applied; \
   (b) state the key exact sequence, kernel/image identification, or \
   fact that drives the argument; \
   (c) name any Hodge-theoretic components explicitly (e.g., H^{0,2}, \
   the (0,2)-projection) rather than appealing vaguely to diagram chases.
3. One paragraph: state what remains open in the general case and why the \
   argument from step 2 does not extend (be specific about which ingredient fails).\
"""

    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        stream=True,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    )
    content = _stream_to_stdout(response)

    _write_transcript(
        source_name=source_name,
        target_name=target_name,
        steps=steps,
        model=model,
        system_prompt=_SYSTEM,
        user_msg=user_msg,
        content=content,
    )
    return content


def _write_transcript(
    source_name: str,
    target_name: str,
    steps: list[ProofStep],
    model: str,
    system_prompt: str,
    user_msg: str,
    content: str,
    full_proof: str | None = None,
    lean_skeleton: str | None = None,
) -> Path:
    """Write all artifacts to proof_transcripts/. Returns the transcript directory path."""
    _TRANSCRIPT_DIR.mkdir(exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = f"{source_name}___{target_name}".replace(" ", "_")
    base = _TRANSCRIPT_DIR / f"{ts}_{slug}"

    record = {
        "timestamp": ts,
        "model": model,
        "source": source_name,
        "target": target_name,
        "path_length": len(steps),
        "steps": [
            {
                "op": s.op_name,
                "from": s.from_name,
                "to": s.to_name,
                "changes": {p: list(v) for p, v in s.changes.items()},
            }
            for s in steps
        ],
        "system_prompt": system_prompt,
        "user_message": user_msg,
        "proof_sketch": content,
        "full_proof_file": f"{base.name}.tex" if full_proof else None,
        "lean_skeleton_file": f"{base.name}.lean" if lean_skeleton else None,
    }
    Path(f"{base}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))

    if full_proof:
        Path(f"{base}.tex").write_text(full_proof, encoding="utf-8")
    if lean_skeleton:
        Path(f"{base}.lean").write_text(lean_skeleton, encoding="utf-8")

    return _TRANSCRIPT_DIR


def format_path_display(
    steps: list[ProofStep],
    source_name: str,
    target_name: str,
) -> str:
    lines = []
    lines.append(f"\nProof Path: {source_name} → {target_name}")
    lines.append(f"Length: {len(steps)} operation(s)\n")
    for i, step in enumerate(steps, 1):
        op = OPERATIONS_BY_NAME.get(step.op_name)
        lines.append(f"  [{i}] {step.op_name.replace('_', ' ')}")
        lines.append(f"       {step.from_name} → {step.to_name}")
        for prim, (old, new) in step.changes.items():
            lines.append(f"       {_prim_label(prim)}: {old} → {new}")
        if op:
            lines.append(f"       ↳ {op.description}")
        lines.append("")
    return "\n".join(lines)

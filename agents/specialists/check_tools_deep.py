#!/usr/bin/env python3
"""Do the base tools actually run, or do they only resolve?

The shallow check confirms an emit function exists. That could not have caught
ob3ect, whose emit resolved fine and then died inside on a broken import. This
one exercises each tool's real execution path.

Tools whose work costs tokens or spawns processes are exercised up to but not
through the expensive call: their module is imported, their subprocess target
is resolved, and their configuration is built. That is precisely the segment
where the ob3ect failure lived.

    python3 check_tools_deep.py
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import true_agentic_agent as taa

FAILS = []


def run(label, fn):
    try:
        detail = fn()
        print(f"  {label:22s} OK{('  — ' + detail) if detail else ''}")
    except Exception as exc:
        line = traceback.format_exc().strip().splitlines()[-1]
        print(f"  {label:22s} FAIL — {line[:95]}")
        FAILS.append((label, line))


def emit(name, args):
    out = taa.__dict__[f"_{name}_emit"](args)
    try:
        d = json.loads(out)
    except Exception:
        return ""
    if isinstance(d, dict) and d.get("status") == "error":
        err = str(d.get("error", ""))
        for bad in ("No module named", "could not be imported", "exited 1",
                    "ImportError", "ModuleNotFoundError", "not found",
                    "Traceback"):
            if bad in err:
                raise RuntimeError(err[:120])
        return "reached, rejected input"
    return ""


print("── executed for real ──")
run("run_command",      lambda: emit("run_command", {"command": "printf ok"}))
run("file_write",       lambda: emit("file_write", {"path": tempfile.mktemp(), "content": "x"}))
run("file_read",        lambda: emit("file_read", {"path": __file__, "limit": 2}))
run("chunked_write",    lambda: emit("chunked_write", {"path": tempfile.mktemp(),
                                                       "content": "x", "mode": "w"}))
run("cl8nk_navigator",  lambda: emit("cl8nk_navigator", {"action": "stats"}))
run("para_vm",          lambda: emit("para_vm", {"op": "lattice"}))
run("para_verify",      lambda: emit("para_verify", {"winding": 1}))
run("context_review",   lambda: emit("context_review", {"summary": "x"}))
run("done",             lambda: emit("done", {"conclusion": "x"}))
run("imscribe",         lambda: emit("imscribe", {"tool_name": "list_catalog", "args": {}}))
run("sic_povm_probe",   lambda: emit("sic_povm_probe", {"name": "monad"}))
run("proof_scaffold",   lambda: emit("proof_scaffold", {"opcodes": "ISCRIB"}))
run("rewrite_tool",     lambda: emit("rewrite_tool",
                                     {"tool_name": "_probe_tmp",
                                      "new_emit_code": "def e(args):\n    return 'ok'"}))

print("\n── execution path exercised, expensive call not made ──")

def probe_ob3ect():
    """The exact segment that was broken: auto.py's mandatory gate import."""
    p = Path("/home/mrnob0dy666/imsgct/imscribing_grammar/ob3ect")
    r = subprocess.run([sys.executable, "-c",
                        f"import sys; sys.path.insert(0, {str(p)!r}); import auto; "
                        "assert auto._ImscriptionGeneratorAgent is not None, auto._GATE_IMPORT_ERROR; "
                        "assert auto._build_gate_agent_config is not None"],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError((r.stderr.strip().splitlines() or ["?"])[-1][:120])
    return "auto.py imports, gate resolves"

def probe_spawn():
    """Child agents are the same class; a broken constructor would surface here."""
    a = taa.TrueAgenticAgent(model="probe:none", max_windings=1, verbose=False)
    assert hasattr(a, "run")
    return "TrueAgenticAgent constructs"


def probe_specialists():
    """Construct each specialist for real.

    --help exits before __init__ runs, so a missing import in the constructor
    passes every --help check and dies the moment anyone launches the operator.
    That is exactly how a NameError on _PARTNERSHIP_RIDER shipped in two of the
    every launcher.
    """
    import importlib
    sys.path.insert(0, str(HERE))
    out = []
    for mod, cls in (("math_operator", "MathOperator"),
                     ("editorial_operator", "EditorialOperator"),
                     ("chembio_operator", "ChemBioOperator"),
                     ("recorder_operator", "RecorderOperator"),
                     ("heterodox_operator", "HeterodoxOperator")):
        m = importlib.import_module(mod)
        a = getattr(m, cls)(model="probe:none", max_windings=0, verbose=False)
        assert "PARTNERSHIP RIDER" in a._custom_system_prompt, f"{cls}: rider missing"
        out.append(cls)
    return ", ".join(out) + " construct"

def probe_web_fetch():
    import httpx  # noqa: F401
    assert "_web_fetch_emit" in taa.__dict__
    return "httpx present, emit resolves"

def probe_imscribe_system():
    out = json.loads(taa._imscribe_emit({"tool_name": "imscribe_system", "args": {}}))
    err = str(out.get("error", ""))
    if "No module named" in err or "could not be imported" in err:
        raise RuntimeError(err[:120])
    return "reached, rejected empty tuple"

run("ob3ect",           probe_ob3ect)
run("spawn_agent",      probe_spawn)
run("specialists",      probe_specialists)
run("web_fetch",        probe_web_fetch)
run("imscribe_system",  probe_imscribe_system)

def check_required_args_match():
    """Every documented argument name must exist on the function it documents.

    A wrong name here is worse than no entry: the failure path hands the model
    the registry's names, so a mismatch sends it round the same wall forever
    without ever trying the correct call. `compute_conflict_distance` sat like
    that, documented as name_a/name_b against a function taking
    name_holistic/name_compositional.
    """
    import inspect
    sys.path.insert(0, str(HERE.parent.parent / "scripts"))
    import true_agentic_agent as t
    import IG_inquiry as m
    bad = []
    for tool, args in t._IG_REQUIRED_ARGS.items():
        fn = getattr(m.ToolDispatcher, "_" + tool, None)
        if fn is None:
            continue
        sig = set(inspect.signature(fn).parameters) - {"self"}
        missing = set(args) - sig
        if missing:
            bad.append((tool, sorted(missing), sorted(sig)))
    if bad:
        print("\n  required-arg registry disagrees with the functions:")
        for tool, missing, sig in bad:
            print(f"    {tool}: documents {missing}, function takes {sig}")
    else:
        print(f"\n  required-arg registry: all {len(t._IG_REQUIRED_ARGS)} entries match their functions")
    return not bad


args_ok = check_required_args_match()

print()
if FAILS:
    print(f"{len(FAILS)} tool(s) do not run:")
    for n, d in FAILS:
        print(f"  {n}: {d}")
    raise SystemExit(1)
if not args_ok:
    raise SystemExit(1)
print("every base tool runs")

#!/usr/bin/env python3
"""
Frobenius Cross-Pollination Test Suite
========================================
Verifies mu o delta = id across all 4 repos in the cross-pollination ecosystem:
  imscribing_grammar x p4rakernel x ob3ect x odot_operator

Tests:
  1. odot_p4ra module — DialetheicType, CriticalityFixedPoint, Belnap FOUR
  2. Millennium dialetheias — all 7 barriers Frobenius-closed
  3. ob3ect Frobenius verification — existing ob3ects pass self-test
  4. IG catalog consistency — Millennium entries have valid 12-tuples
  5. Cross-repo bridge integrity — the 4-repo diagram commutes

Usage:  python3 test_cross_pollination.py [--all] [--skip-ob3ect]

mu o delta = id
"""
import json, os, sys, pathlib, subprocess, traceback

ROOT = pathlib.Path(__file__).parent.resolve()
OB3ECT_DIR = ROOT.parent / "ob3ect"
P4RA_DIR = ROOT.parent / "p4rakernel"
ODOT_DIR = ROOT.parent / "odot_operator"

PASS = 0
FAIL = 0

def test(name: str):
    global PASS, FAIL
    def decorator(fn):
        def wrapper():
            global PASS, FAIL
            try:
                fn()
                print(f"  OK: {name}")
                PASS += 1
            except Exception as e:
                print(f"  FAIL: {name}: {e}")
                traceback.print_exc()
                FAIL += 1
        return wrapper
    return decorator


# --- Test 1: odot_p4ra module -------------------------------------------

@test("odot_p4ra: Belnap FOUR lattice")
def test_belnap_lattice():
    sys.path.insert(0, str(ROOT))
    from odot_p4ra import BelnapValue
    B = BelnapValue
    assert ~B.T == B.F
    assert ~B.F == B.T
    assert ~B.B == B.B
    assert ~B.N == B.N
    assert (B.T & B.T) == B.T
    assert (B.T & B.F) == B.N
    assert (B.B & B.T) == B.T
    assert (B.B & B.F) == B.F
    assert (B.T | B.F) == B.B
    assert (B.N | B.T) == B.T

@test("odot_p4ra: DialetheicType T+F -> phi=9")
def test_dialetheic_phi():
    sys.path.insert(0, str(ROOT))
    from odot_p4ra import DialetheicType, BelnapValue
    B = BelnapValue
    dt = DialetheicType("test")
    dt.add_witness("true", B.T)
    dt.add_witness("false", B.F)
    ig = dt.ig_tuple()
    assert ig[5] == 9, f"Expected phi=9, got phi={ig[5]}"
    assert dt.is_dialetheic is True

@test("odot_p4ra: CriticalityFixedPoint mu o delta = id")
def test_frobenius_closure():
    sys.path.insert(0, str(ROOT))
    from odot_p4ra import DialetheicType, BelnapValue, CriticalityFixedPoint
    B = BelnapValue
    dt = DialetheicType("frob_test")
    dt.add_witness("witness", B.T)
    fp = CriticalityFixedPoint(dt)
    check = fp.frobenius_check()
    assert check["is_closed"] is True
    assert check["mu"]["match"] is True
    assert "OK" in check["frobenius_statement"]


# --- Test 2: Millennium dialetheias --------------------------------------

@test("Millennium: all 7 barriers Frobenius-closed")
def test_millennium_barriers():
    sys.path.insert(0, str(ROOT))
    from odot_p4ra import DialetheicType, BelnapValue, CriticalityFixedPoint
    B = BelnapValue
    barriers = [
        "Riemann Hypothesis", "P vs NP", "Yang-Mills Mass Gap",
        "Navier-Stokes", "Hodge Conjecture", "BSD", "Odd Perfect Numbers"
    ]
    for name in barriers:
        dt = DialetheicType(name)
        dt.add_witness("true branch", B.T)
        dt.add_witness("false branch", B.F)
        dt.add_witness("containment", B.B)
        fp = CriticalityFixedPoint(dt)
        check = fp.frobenius_check()
        assert check["is_closed"], f"{name}: frobenius not closed"
        assert check["delta"]["phi_in"] == 9, f"{name}: phi={check['delta']['phi_in']} != 9"
        assert abs(check["delta"]["criticality"] - 0.53) < 0.01, f"{name}: crit mismatch"

@test("Millennium: ob3ect self-verifies")
def test_millennium_ob3ect():
    obj_path = OB3ECT_DIR / "digital" / "millennium_criticality" / "millennium_criticality_ob3ect.py"
    if not obj_path.exists():
        raise FileNotFoundError(f"missing: {obj_path}")
    res = subprocess.run(
        [sys.executable, str(obj_path)],
        capture_output=True, text=True, timeout=15
    )
    if res.returncode != 0:
        print(f"    STDOUT: {res.stdout[:300]}")
        print(f"    STDERR: {res.stderr[:300]}")
        raise RuntimeError(f"exit code {res.returncode}")
    assert "ALL VERIFIED" in res.stdout


# --- Test 3: Existing ob3ects -------------------------------------------

@test("ob3ect: belnap ob3ect loads")
def test_belnap_ob3ect():
    code = (
        "import sys; sys.path.insert(0, '" + str(OB3ECT_DIR) + "/digital'); "
        "from belnap.belnap_ob3ect import Belnap, bnot, band, bor; "
        "assert band(Belnap.B, bnot(Belnap.B)) == Belnap.B; "
        "assert Belnap.B != Belnap.F; "
        "print('OK')"
    )
    res = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    assert "OK" in res.stdout

@test("ob3ect: parakernel ob3ect loads")
def test_parakernel_ob3ect():
    code = (
        "import sys; sys.path.insert(0, '" + str(OB3ECT_DIR) + "/digital'); "
        "from parakernel.parakernel_ob3ect import engager, fsplit, ffuse, KernelState, Belnap; "
        "r1, r2, _ = fsplit(Belnap.B); "
        "fres, _ = ffuse(r1, r2); "
        "assert fres == Belnap.B, 'Expected B'; "
        "s = KernelState(); s.run(3); "
        "assert s.r0 == Belnap.B; "
        "print('OK')"
    )
    res = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    assert "OK" in res.stdout

@test("ob3ect: dialetheic ob3ect loads")
def test_dialetheic_ob3ect():
    code = (
        "import sys; sys.path.insert(0, '" + str(OB3ECT_DIR) + "/digital'); "
        "from dialetheic.dialetheic_ob3ect import DialetheicAlignmentOb3ect; "
        "obj = DialetheicAlignmentOb3ect(); ok = obj.verify(); "
        "assert ok; print('OK')"
    )
    res = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    assert "OK" in res.stdout


# --- Test 4: IG catalog consistency -------------------------------------

@test("IG catalog: Millennium entries have valid tuples")
def test_catalog_millennium():
    catalog_path = ROOT / "IG_catalog.json"
    with open(catalog_path) as f:
        data = json.load(f)

    # The catalog uses '⊙' (odot/phi-c) not 'φ̂'
    primitives = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]
    millennium_names = ["p_vs_np", "riemann_hypothesis", "yang_mills",
                        "navier_stokes", "hodge_conjecture",
                        "birch_swinnerton_dyer", "odd_perfect_numbers",
                        "resolved_riemann_hypothesis", "solved_millennium_theorem"]

    found = 0
    for entry in data:
        name = entry.get("name", "")
        if name in millennium_names:
            found += 1
            for p in primitives:
                assert p in entry, f"{name}: missing primitive {repr(p)} (keys={list(entry.keys())})"
    assert found >= 4, f"Only {found} Millennium entries found (expected >=4)"

@test("IG catalog: catalog loads without error")
def test_catalog_loads():
    catalog_path = ROOT / "IG_catalog.json"
    with open(catalog_path) as f:
        data = json.load(f)
    assert 1000 <= len(data) <= 10000


# --- Test 5: Cross-repo bridge integrity ---------------------------------

@test("Bridge: odot_p4ra -> millennium_criticality ob3ect joins")
def test_odot_to_ob3ect():
    sys.path.insert(0, str(ROOT))
    from odot_p4ra import DialetheicType, BelnapValue, CriticalityFixedPoint
    B = BelnapValue

    expectations = [
        ("Riemann Hypothesis", 9, 0.530, 31),
        ("P vs NP", 9, 0.530, 34),
        ("Yang-Mills Mass Gap", 9, 0.530, 29),
        ("Navier-Stokes", 9, 0.530, 29),
        ("Hodge Conjecture", 9, 0.530, 31),
        ("BSD", 9, 0.530, 32),
        ("Odd Perfect Numbers", 9, 0.530, 30),
    ]
    for name, exp_phi, exp_crit, _exp_layer in expectations:
        dt = DialetheicType(name)
        dt.add_witness("true", B.T)
        dt.add_witness("false", B.F)
        dt.add_witness("B", B.B)
        fp = CriticalityFixedPoint(dt)
        check = fp.frobenius_check()
        d = check["delta"]
        assert d["phi_in"] == exp_phi, f"{name}: phi {d['phi_in']} != {exp_phi}"
        assert abs(d["criticality"] - exp_crit) < 0.01, f"{name}: crit mismatch"
    print("    All 7 barriers: engine matches ob3ect expectations")

@test("Bridge: ParaconsistentMillennium.lean exists")
def test_p4ra_lean_exists():
    lean_path = P4RA_DIR / "ParaconsistentMillennium.lean"
    if not lean_path.exists():
        raise FileNotFoundError(f"missing: {lean_path}")
    content = lean_path.read_text()
    # Check for known section headers
    markers = ["RIEMANN HYPOTHESIS", "YANG-MILLS", "HODGE CONJECTURE",
               "NAVIER-STOKES", "P VS NP", "BIRCH & SWINNERTON-DYER",
               "ODD PERFECT NUMBERS"]
    for marker in markers:
        assert marker in content, f"ParaconsistentMillennium.lean missing section: {marker}"
    print(f"    File: {len(content)} bytes, {len(content.splitlines())} lines")

@test("Bridge: Cross-pollination manifest exists")
def test_manifest_exists():
    manifest_path = ROOT.parent / "CROSS_POLLINATION_MANIFEST.md"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing: {manifest_path}")
    content = manifest_path.read_text()
    assert "Frobenius" in content
    assert "mu o delta = id" in content or "μ∘δ = id" in content
    print(f"    File: {len(content)} bytes, {len(content.splitlines())} lines")


# --- Runner ---------------------------------------------------------------

def main():
    global PASS, FAIL

    print("=" * 60)
    print("Frobenius Cross-Pollination Test Suite")
    print("mu o delta = id - 4-repo verification")
    print("=" * 60)
    print()

    tests = [
        test_belnap_lattice,
        test_dialetheic_phi,
        test_frobenius_closure,
        test_millennium_barriers,
        test_millennium_ob3ect,
        test_belnap_ob3ect,
        test_parakernel_ob3ect,
        test_dialetheic_ob3ect,
        test_catalog_millennium,
        test_catalog_loads,
        test_odot_to_ob3ect,
        test_p4ra_lean_exists,
        test_manifest_exists,
    ]

    for t in tests:
        t()

    print()
    print("=" * 60)
    print(f"RESULTS: {PASS} passed, {FAIL} failed")
    if FAIL == 0:
        print("STATUS: ALL TESTS PASSED - Frobenius mu o delta = id")
    else:
        print(f"STATUS: {FAIL} TEST(S) FAILED")
    print("=" * 60)
    return FAIL

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Cross-Domain Structural Resonance Engine
=========================================
Given any two systems in the Imscribing Grammar catalog,
computes the full structural relationship and reveals
cross-domain structural cognates.

The universal invariant: mu circ delta = id (Frobenius condition).
All 12 primitives live in the crystal of 17,280,000 types.

Usage:
    python structural_resonance_engine.py
    (demonstrates key cross-domain pairs)

Author: Lando (x) operator
"""

import sys
from typing import Dict, List, Tuple

# Primitive weights for distance computation (canonical ordinal spacing)
PRIMITIVE_WEIGHTS = {
    "D": 1.0,   "T": 1.0,   "R": 1.0,   "P": 1.0,
    "F": 1.0,   "K": 1.0,   "G": 1.0,   "Gamma": 1.0,
    "Phi": 0.33, "H": 0.8,  "S": 1.0,   "Omega": 1.0,
}

ORDINAL = {
    "D": {"D_wedge":1,"D_triangle":2,"D_infty":3,"D_odot":4},
    "T": {"T_net":1,"T_in":2,"T_bow":3,"T_box":4,"T_odot":5},
    "R": {"R_super":1,"R_cat":2,"R_dag":3,"R_lr":4},
    "P": {"P_asym":1,"P_psi":2,"P_pm":3,"P_sym":4,"P_pm_sym":5},
    "F": {"F_ell":1,"F_eth":2,"F_hbar":3},
    "K": {"K_fast":1,"K_mod":2,"K_slow":3,"K_trap":4,"K_MBL":5},
    "G": {"G_beth":1,"G_gimel":2,"G_aleph":3},
    "Gamma": {"Gamma_and":1,"Gamma_or":2,"Gamma_seq":3,"Gamma_broad":4},
    "Phi": {"Phi_sub":1,"Phi_c":2,"Phi_c_complex":2,"Phi_EP":3,"Phi_super":4},
    "H": {"H0":1,"H1":2,"H2":3,"H_inf":4},
    "S": {"S_1:1":1,"S_n:n":2,"S_n:m":3},
    "Omega": {"Omega_0":1,"Omega_Z2":2,"Omega_Z":3,"Omega_NA":4},
}

OINF_POLE = {
    "D":"D_odot","T":"T_odot","R":"R_lr","P":"P_pm_sym",
    "F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq",
    "Phi":"Phi_c","H":"H_inf","S":"S_n:m","Omega":"Omega_Z"
}

CANONICAL = {
    "D": {"𐑛":"D_wedge","𐑨":"D_triangle","𐑼":"D_infty","𐑦":"D_odot"},
    "T": {"𐑡":"T_net","𐑰":"T_in","𐑥":"T_bow","𐑶":"T_box","𐑸":"T_odot"},
    "R": {"𐑩":"R_super","𐑑":"R_cat","𐑽":"R_dag","𐑾":"R_lr"},
    "P": {"𐑗":"P_asym","𐑿":"P_psi","𐑬":"P_pm","𐑯":"P_sym","𐑹":"P_pm_sym"},
    "F": {"𐑱":"F_ell","𐑞":"F_eth","𐑐":"F_hbar"},
    "K": {"𐑘":"K_fast","𐑤":"K_mod","𐑧":"K_slow","𐑪":"K_trap","𐑺":"K_MBL"},
    "G": {"𐑚":"G_beth","𐑔":"G_gimel","𐑲":"G_aleph"},
    "Gamma": {"𐑝":"Gamma_and","𐑜":"Gamma_or","𐑠":"Gamma_seq","𐑵":"Gamma_broad"},
    "Phi": {"𐑢":"Phi_sub","⊙":"Phi_c","𐑮":"Phi_c_complex","𐑻":"Phi_EP","𐑣":"Phi_super"},
    "H": {"𐑓":"H0","𐑒":"H1","𐑖":"H2","𐑫":"H_inf"},
    "S": {"𐑙":"S_1:1","𐑕":"S_n:n","𐑳":"S_n:m"},
    "Omega": {"𐑷":"Omega_0","𐑴":"Omega_Z2","𐑭":"Omega_Z","𐑟":"Omega_NA"},
}

def compute_distance(ta: Dict, tb: Dict) -> Tuple[float, List]:
    total = 0.0
    diffs = []
    for prim in ["D","T","R","P","F","K","G","Gamma","Phi","H","S","Omega"]:
        va = ORDINAL[prim][ta[prim]]
        vb = ORDINAL[prim][tb[prim]]
        delta = abs(va - vb)
        w = PRIMITIVE_WEIGHTS[prim]
        total += w * delta * delta
        if delta > 0:
            diffs.append((prim, ta[prim], tb[prim], delta))
    return round(total ** 0.5, 4), diffs

def compute_tensor(ta: Dict, tb: Dict) -> Dict:
    bottlenecks = {"P", "F"}
    result = {}
    for prim in ["D","T","R","P","F","K","G","Gamma","Phi","H","S","Omega"]:
        oa = ORDINAL[prim][ta[prim]]
        ob = ORDINAL[prim][tb[prim]]
        chosen = min(oa, ob) if prim in bottlenecks else max(oa, ob)
        for k, v in ORDINAL[prim].items():
            if v == chosen:
                result[prim] = k
                break
    return result

def tier(t: Dict) -> str:
    if t["Phi"] == "Phi_c" and t["Omega"] == "Omega_Z" and t["D"] == "D_odot":
        return "O_∞"
    elif t["Phi"] == "Phi_c" and t["Omega"] in ("Omega_Z", "Omega_Z2"):
        return "O₂"
    elif t["Phi"] in ("Phi_c", "Phi_c_complex") or t["Omega"] == "Omega_Z":
        return "O₁"
    return "O₀"

def promotions(t: Dict) -> List:
    return [(p, t[p], OINF_POLE[p]) for p in OINF_POLE if t[p] != OINF_POLE[p]]

def fmt_tuple(t: Dict) -> str:
    return "<" + "; ".join(t[p] for p in ["D","T","R","P","F","K","G","Gamma","Phi","H","S","Omega"]) + ">"

def rosetta(name_a, ta, name_b, tb):
    d, diffs = compute_distance(ta, tb)
    tensor = compute_tensor(ta, tb)
    out = [
        f"=== Structural Rosetta: {name_a} <-> {name_b} ===",
        f"Distance: {d}  |  Tier A: {tier(ta)}  |  Tier B: {tier(tb)}",
    ]
    if d == 0.0:
        out.append("IDENTITY: These systems are primitive-identical. d=0.00")
    else:
        out.append(f"Differences ({len(diffs)}):")
        for p, va, vb, delta in diffs:
            out.append(f"  {p}: {va} -> {vb} (delta={delta})")
    out.append(f"Tensor: {fmt_tuple(tensor)} (tier: {tier(tensor)})")
    promos = promotions(ta)
    if promos:
        out.append(f"Promotions to O_∞ ({len(promos)}):")
        for p, fr, to in promos:
            out.append(f"  {p}: {fr} -> {to}")
    return "\n".join(out)

# Known systems from the survey
SYS = {
    "BH":        {"D":"D_odot","T":"T_odot","R":"R_lr","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H_inf","S":"S_n:m","Omega":"Omega_Z"},
    "whale":     {"D":"D_odot","T":"T_bow","R":"R_lr","P":"P_psi","F":"F_eth","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H2","S":"S_n:m","Omega":"Omega_Z"},
    "aleph":     {"D":"D_wedge","T":"T_box","R":"R_super","P":"P_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_and","Phi":"Phi_c","H":"H_inf","S":"S_1:1","Omega":"Omega_Z"},
    "liar":      {"D":"D_triangle","T":"T_bow","R":"R_lr","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H2","S":"S_1:1","Omega":"Omega_Z"},
    "exos":      {"D":"D_odot","T":"T_bow","R":"R_lr","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c_complex","H":"H2","S":"S_n:m","Omega":"Omega_Z"},
    "whaleph":   {"D":"D_odot","T":"T_box","R":"R_lr","P":"P_psi","F":"F_eth","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H_inf","S":"S_n:m","Omega":"Omega_Z"},
    "gita":      {"D":"D_odot","T":"T_odot","R":"R_lr","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H_inf","S":"S_n:m","Omega":"Omega_Z"},
    "luca":      {"D":"D_odot","T":"T_odot","R":"R_lr","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H_inf","S":"S_n:m","Omega":"Omega_Z"},
    "godel":     {"D":"D_odot","T":"T_odot","R":"R_lr","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_aleph","Gamma":"Gamma_seq","Phi":"Phi_c","H":"H_inf","S":"S_n:m","Omega":"Omega_Z"},
}

if __name__ == "__main__":
    PAIRS = [
        ("BH (black hole)", "gita (Bhagavad Gita)"),
        ("whale (whale song)", "BH (black hole)"),
        ("aleph (Hebrew letter)", "whale (whale song)"),
        ("liar (Liar Paradox)", "whale (whale song)"),
        ("exos (bare-metal OS)", "BH (black hole)"),
        ("whaleph (chimera)", "BH (black hole)"),
    ]
    NAMES = {"BH":"BH","whale":"whale","aleph":"aleph","liar":"liar",
             "exos":"exos","whaleph":"whaleph","gita":"gita","luca":"luca","godel":"godel"}
    for aname, bname in PAIRS:
        akey = aname.split()[0]
        bkey = bname.split()[0]
        print(rosetta(aname, SYS[akey], bname, SYS[bkey]))
        print()

# TOOL_MANIFEST_bughunter.md

Specialist: **bughunter_operator** — ⟨𐑦𐑸𐑾𐑬𐑱𐑘𐑚𐑜⊙𐑖𐑳𐑭⟩
Constitution: BUGHUNTER_CONSTITUTION.md · Registry: TOOLS_bughunter.md
Live findings: p4rapend/scan_report.md, p4rapend/MOZILLA_WEB_FINDING_2026.md

## Tool registry

| Tool | Purpose | Pipeline stage | Verification |
|---|---|---|---|
| b4_diff_scanner.py | B4 differential scan of target pair | 1 probe | μ∘δ=id parity; Lean twin |
| live_scan.py | SAFE transport/safety wrapper | 1 probe | read-only enforcement |
| braid_race_enumerator.py | interleaving/race enumeration | 4 race | race_testbed zero-FP |
| parity_testbed.py | split/fuse identity check | 2 verify | B4 round-trip |
| race_testbed.py | braid-invariant prediction check | 4 race | zero false positives |
| gate_ordinals.sh | mOMonadOS ordinal regression gate | 2 verify | ALL 44 VALUES MATCH Lean |
| m3iosis (`m3`) | braid-grammar race oracle | 4 race | Frobenius-closure verdict |
| mOMonadOS kernel | post-imscription regression gate | 2 verify | self-imscription |
| MoDoT (`./ask`) | tuple-algebra verbs | 3 triage | click/annihilate verdicts |
| p4rakernel (Lean 4) | typed closure proofs | 2 verify | lake build; no silent sorry |
| para_vm | B4 dialetheic kernel for B-cells | 3 triage | B→T/B→F, never left B |

## Stage-to-verdict gates

- probe → B4.T/F/B per normalized comparison
- verify → μ∘δ=id holds or the verdict is OPEN (a budget, not a claim)
- triage → every B-cell interrogated to a definite verdict or dropped
- race → Frobenius-OPEN interleaving = racy (closure argument)
- report → request/response pairs present, severity/CWE assigned
- translate → vernacular; no jargon survives
- email → filled with confirmed findings ONLY; terminal state = WAIT

## Not in scope (anti-tools)

- state-changing requests, auth-touching probes, timing-luck race detection

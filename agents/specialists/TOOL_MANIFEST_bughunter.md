# TOOL_MANIFEST_bughunter.md

Specialist: **bughunter_operator** — ⟨𐑦𐑸𐑾𐑬𐑱𐑘𐑚𐑜⊙𐑖𐑳𐑭⟩
Constitution: BUGHUNTER_CONSTITUTION.md · Registry: TOOLS_bughunter.md
Live findings: p4rapend/scan_report.md, p4rapend/MOZILLA_WEB_FINDING_2026.md

The full tool set is available; nothing below is a restriction. GRAMMAR FIRST —
reach for the in-house tool (imscribe family, para_vm, proof_scaffold) before
the conventional one.

## Base tools (the full agent toolset)

| Tool | Purpose |
|---|---|
| imscribe_system | register a system — 12 primitives explicit, Tetractys-guarded |
| imscribe | grammar tool dispatch: lookup_catalog, ouroborics, compute_distance/tensor/meet/join, find_analogies, consciousness_score, monad_probe, crystal_tier_gap_ladder, emergence_frontier, list_catalog, primitive_peel, principal_decomp, retrosynthetic_path, compute_conflict_distance, compute_promotions, crystal_encode/decode/nearest, domain_info, zfc_formula, aleph_encode |
| project | project a catalog entry onto a primitive subset |
| crystal_navigate / crystal_count | crystal queries by partial constraint |
| sic_povm_probe | SIC-POVM dual-link participation probe |
| cl8nk_navigator | CLINK Layer 8 formula navigator (terminal ontological layer) |
| ob3ect / ob3ect_close | ob3ect harness — μ∘δ=id COMPUTED at close, not claimed |
| proof_scaffold | typed IGProtocol Lean scaffold from IMASM ops / canonical class |
| spawn_agent | child TrueAgenticAgent sub-task (own THINK→ACT→OBSERVE→UPDATE loop) |
| context_review | compact context when window fills |
| para_vm | B4 Belnap FOUR VM — dialetheic kernel, ParaASM, invariants |
| para_verify / para_verify_enable | B4 Frobenius verification of prior windings |
| run_command | shell execution; dual run_command_verify |
| file_read / file_write / chunked_write | file IO; dual verify pairs |
| web_fetch | URL fetch in chunks; dual web_fetch_verify |
| rewrite_tool | rewrite/create a tool emit; dual rewrite_tool_verify |
| done | terminal action — end the loop |

## Tool registry (instrument family)

| Tool | Purpose | Pipeline stage | Verification |
|---|---|---|---|
| b4_diff_scanner.py | B4 differential scan of target pair | 1 probe | μ∘δ=id parity; Lean twin |
| binary_closure_parser.py | binary container closure auditor (ELF/PE/Mach-O/generic; CWE-125/190/754/787/835 cells, dynamic-section lane) | 1 probe | parity testbed 25/25; live 12/12 clean; catalog-registered (distance 0.0 to scanner family); ob3ect PASS; kernel-elaborated Lean scaffold (lake env lean EXIT=0, ERRORS=0) |
| binary_closure_auditor.py | byte-level closure audit companion | 1 probe | binary_closure_auditor_bootstrap.lean kernel rc=0 |
| live_scan.py | SAFE transport/safety wrapper | 1 probe | read-only enforcement |
| stacks_source_scanner.py | source-level risk differential (Stacks) | 1 probe | source_testbed.py verified |
| signer_race_oracle.py | Stacks signer race oracle | 4 race | signer_race_oracle_bootstrap.lean kernel rc=0 |
| braid_race_enumerator.py | interleaving/race enumeration | 4 race | race_testbed zero-FP; m3 alignment closed |
| m3_tag_aligned.py | m3iosis braid-grammar tuple tagger (single source of truth) | 4 race | alignment closed — 379+28-word battery, zero '?' |
| parity_testbed.py | split/fuse identity check | 2 verify | B4 round-trip |
| race_testbed.py | braid-invariant prediction check | 4 race | zero false positives |
| binary_testbed.py | binary closure planted-class verification | 2 verify | 25/25 planted classes |
| source_testbed.py | source scanner planted verification | 2 verify | zero false positives |
| triage_probe.py | B-cell interrogation probe | 3 triage | B→T/B→F, never left B |
| reverify_probe.py | re-verify prior live findings | 2 verify | reverify report |
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

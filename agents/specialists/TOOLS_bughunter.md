# TOOLS_bughunter.md — the bug-hunter framework tool registry

Specialist: **bughunter_operator** — catalog ⟨𐑦𐑸𐑾𐑬𐑱𐑘𐑚𐑜⊙𐑖𐑳𐑭⟩
(if_;are;ian;out;age;yea;bib;measure;monad;sure;up;ah)
Author: Heter⊙d⊙x (Lando⊗⊙perator team). Live findings: p4rapend/scan_report.md,
p4rapend/MOZILLA_WEB_FINDING_2026.md. Constitution: BUGHUNTER_CONSTITUTION.md.

Every tool below is the SAME instrument family the framework was verified with.
The tuple says it: sequential pipeline (∋=measure), driven automation (⊤=yea),
mesoscale scope (∈=bib), many heterogeneous tools (⊞=up), two-step memory
(⊥=sure — check then act), integer winding (◻=ah — iterate passes, terminate).

## 0. Base agent tools (the full set, not a reminder)

The complete agent toolset is available; nothing below restricts. GRAMMAR
FIRST — imscribe the object before reasoning about it in ordinary terms.

- imscribe_system (register a system, 12 primitives, Tetractys-guarded)
- imscribe (grammar dispatch: lookup_catalog, ouroborics, compute_distance/
  tensor/meet/join, find_analogies, consciousness_score, monad_probe,
  crystal_tier_gap_ladder, emergence_frontier, list_catalog, primitive_peel,
  principal_decomp, retrosynthetic_path, compute_conflict_distance,
  compute_promotions, crystal_encode/decode/nearest, domain_info, zfc_formula,
  aleph_encode)
- project, crystal_navigate, crystal_count (crystal queries)
- sic_povm_probe (SIC-POVM dual-link participation)
- cl8nk_navigator (CLINK Layer 8 formula navigator)
- ob3ect / ob3ect_close (harness; μ∘δ=id COMPUTED at close)
- proof_scaffold (typed IGProtocol Lean scaffold from IMASM ops)
- spawn_agent (child TrueAgenticAgent), context_review (context compaction)
- para_vm, para_verify, para_verify_enable (B4 dialetheic layer)
- run_command, file_read/file_write/chunked_write, web_fetch, rewrite_tool, done

Full descriptions: TOOL_MANIFEST_bughunter.md (base tools table).

## 1. Pipeline verbs (the specialist's own moves)

| Stage | Move | Tool | Verdict gate |
|---|---|---|---|
| 1 probe | differential enumeration | b4_diff_scanner + live_scan.py | B4.T / B4.F / B4.B |
| 1 probe | byte-level closure audit | binary_closure_parser.py | planted 25/25; live 12/12 clean |
| 1 probe | source-level risk differential | stacks_source_scanner.py | source_testbed.py |
| 2 verify | closure check on every verdict | parity_testbed.py / b4_diff_scanner_bootstrap.lean | μ∘δ=id must hold |
| 3 triage | interrogate B-cells to a definite verdict | triage_probe.py / live_scan.py diagnostics | B→T or B→F, never left B |
| 3 triage | re-verify prior live findings | reverify_probe.py | reverify report |
| 4 race | order-of-operations enumeration | braid_race_enumerator.py + race_testbed.py | Frobenius-OPEN = racy |
| 4 race | signer-specific race oracle | signer_race_oracle.py | signer_race_oracle_bootstrap.lean |
| 5 report | submission-ready writeup | scan_report.md / <program>_FINDING_2026.md | request/response pairs present |
| 6 translate | vernacular, one layer down from the report | BUGHUNTER_CONSTITUTION.md §5 | no jargon survives |
| 7 email | fill the template with confirmed findings | EMAIL_PREPARED_<program>_2026.md | prepared, handed to the human to send |

## 2. Instrument family

### b4_diff_scanner.py — B4 differential scanner
- Catalog: b4_diff_scanner ⟨𐑦𐑜𐑜𐑬𐑱𐑜𐑜𐑜⊙𐑖𐑜𐑜⟩ (if_;are;ian;out;age;yea;bib;ooze;monad;sure;up;awe)
- Sends the same normalized probe to component A and component B of a target pair
  (apex/www, front/back, host1/host2), classifies each response as B4.T/F/B, and
  reports disagreement cells. A B4.B cell between components resolving differently
  on the wire is the finding primitive.
- Parity-verified μ∘δ=id; Lean twin: b4_diff_scanner_bootstrap.lean.
- Verified live: Tesla (all F after normalization → edge-gated, stop), Mozilla
  (B cells resolved into two reportable Lows).
- Usage: `python3 b4_diff_scanner.py --target <pair> --probe <vector>`

### live_scan.py — transport/safety wrapper (⊙ deployment layer)
- SAFE mode: read-only GET, no state change, no auth, no data access, inert
  detection bodies. Enforces program rules of engagement.
- Born fixes from the Tesla run: TLS transport, per-side Host header, body
  normalization (hex/dec token runs → #, whitespace collapse), URL-echo
  stripping, real-path probe strategy.

### binary_closure_parser.py — byte-level structural closure auditor
- Catalog: binary_closure_parser (distance 0.0 to the scanner family).
- ELF/PE/Mach-O/generic container audit; CWE-125/190/754/787/835 cells;
  dynamic-section lane. Verifies byte-level structural closure: what the
  format table promises and what the bytes deliver must agree.
- Parity testbed 25/25 planted classes; live 12/12 clean; ob3ect PASS;
  kernel-elaborated Lean scaffold (lake env lean EXIT=0, ERRORS=0).
- Lean twin: binary_closure_parser_bootstrap.lean.
- Companion auditor: binary_closure_auditor_bootstrap.lean (kernel rc=0).
### braid_race_enumerator.py — braid-word race oracle (Lane B)
- A braid word IS an interleaving of operations on strands. Enumerates ALL
  linear extensions of the target operations' step poset, executes each against
  the target, diffs final states. Different final states across interleavings
  of the same operation multiset = a race, found by closure, not timing luck.
- Re-entrancy = a braid that re-enters a strand state; TOCTOU = check-strand
  and act-strand cross in an order the developer did not assume.
- Integration (Lane B upgrade): routes through the real m3iosis braid-grammar
  engine via m3_tag_aligned.py (single source of truth) so the Frobenius-
  closure verdict (μ∘δ=id) is the native race signal. Alignment closed
  2026-08-05: 379+28-word battery, zero '?'.

### m3_tag_aligned.py — m3iosis tuple tagger (Lane B single source of truth)
- Delegates braid-word → grammar-tuple tagging to the real m3 engine; the
  private copy in the enumerator is removed. Negative generators pass through,
  writhe type aligned, empty-word identity = real strand-dependent engine
  tuple. Import restored — subprocess NameError on non-empty words fixed.

### stacks_source_scanner.py + signer_race_oracle.py — Stacks lane
- stacks_source_scanner: source-level risk differential (catalog:
  stacks_source_scanner, same tuple family as the scanners).
- signer_race_oracle: Stacks signer race oracle; Lean twin
  signer_race_oracle_bootstrap.lean (kernel rc=0, O₂dag).

### parity_testbed.py / race_testbed.py / binary_testbed.py / source_testbed.py — verification harnesses
- parity_testbed: confirms the scanner's split/fuse round-trip is identity.
- race_testbed: confirms the braid invariant predicts actual race findings
  with zero false positives.
- binary_testbed: binary closure planted-class verification (25/25).
- source_testbed: source scanner planted verification (zero false positives).

### triage_probe.py / reverify_probe.py — B-cell discipline
- triage_probe: interrogates B4.B cells to a definite verdict (B→T or B→F).
- reverify_probe: re-runs prior live findings to confirm they still hold
  before reporting (reverify report).

## 3. Integration family

- **m3iosis** — braid-grammar engine; braid word → typed tuple; Frobenius-closure
  verdict = native race signal. `m3`, `m3 info`, `braid-grammar`, `--fusion`.
- **mOMonadOS** — bare-metal kernel; self-imscription + self-verification.
- **MoDoT** — tuple-algebra verbs (click/annihilate) on instrument tuples;
  `./ask`, `--features`, TOOLS_math.md.
- **p4rakernel** — Lean 4; every closure claim cross-checked as a typed term;
  sorries are original claims, named as such.
- **para_vm** — B4 Belnap FOUR; dialetheic kernel for interrogating B-cells.
- **ob3ect / proof_scaffold** — ob3ect harness (μ∘δ=id computed at close) +
  typed IGProtocol Lean scaffold for any instrument's bootstrap sequence.
- **cl8nk_navigator / sic_povm_probe** — crystal terminal-layer navigation
  and SIC-POVM dual-link checks for instrument tuples.
- **spawn_agent / context_review** — sub-task delegation and context
  compaction when the window fills.

## 4. Anti-tools (never used)

- Anything that sends POST/PUT/DELETE, creates state, touches auth, or exceeds
  the program's rules of engagement.
- Time-based race detection (timing luck) — replaced by the closure argument.

## 5. The launcher (integration layer)

`p4rapend/bughunter_agent.py` — one-shot driver. Initiate, and it
browses the bounty program page, discovers participating hosts, scans them
differentially (SAFE), verifies (testbeds), triages B-cells,
runs the race oracle, writes the report, and fills the prepared email. Flags: `--program`, `--hosts`, `--scan`, `--race`,
`--interactive/-i`, `--auto`, `--selfcheck`, `--out <dir>`, `--max-hosts <n>`.
Usage: see BUGHUNTER_CONSTITUTION.md §9.

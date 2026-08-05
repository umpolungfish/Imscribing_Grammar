# TOOLS_bughunter.md — the bug-hunter framework tool registry

Specialist: **bughunter_operator** — catalog ⟨𐑦𐑸𐑾𐑬𐑱𐑘𐑚𐑜⊙𐑖𐑳𐑭⟩
(if_;are;ian;out;age;yea;bib;measure;monad;sure;up;ah)
Author: Heter⊙d⊙x (Lando⊗⊙perator team). Live findings: p4rapend/scan_report.md,
p4rapend/MOZILLA_WEB_FINDING_2026.md. Constitution: BUGHUNTER_CONSTITUTION.md.

Every tool below is the SAME instrument family the framework was verified with.
The tuple says it: sequential pipeline (∋=measure), driven automation (⊤=yea),
mesoscale scope (∈=bib), many heterogeneous tools (⊞=up), two-step memory
(⊥=sure — check then act), integer winding (◻=ah — iterate passes, terminate).

## 0. Pipeline verbs (the specialist's own moves)

| Stage | Move | Tool | Verdict gate |
|---|---|---|---|
| 1 probe | differential enumeration | b4_diff_scanner + live_scan.py | B4.T / B4.F / B4.B |
| 2 verify | closure check on every verdict | parity_testbed.py / b4_diff_scanner_bootstrap.lean | μ∘δ=id must hold |
| 3 triage | interrogate B-cells to a definite verdict | live_scan.py diagnostics + body normalization | B→T or B→F, never left B |
| 4 race | order-of-operations enumeration | braid_race_enumerator.py + race_testbed.py | Frobenius-OPEN = racy |
| 5 report | submission-ready writeup | scan_report.md / <program>_FINDING_2026.md | request/response pairs present |
| 6 translate | vernacular, one layer down from the report | BUGHUNTER_CONSTITUTION.md §5 | no jargon survives |
| 7 email | fill the template with confirmed findings | EMAIL_PREPARED_<program>_2026.md | terminal state = WAIT |

## 1. Instrument family

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

### braid_race_enumerator.py — braid-word race oracle (Lane B)
- A braid word IS an interleaving of operations on strands. Enumerates ALL
  linear extensions of the target operations' step poset, executes each against
  the target, diffs final states. Different final states across interleavings
  of the same operation multiset = a race, found by closure, not timing luck.
- Re-entrancy = a braid that re-enters a strand state; TOCTOU = check-strand
  and act-strand cross in an order the developer did not assume.
- Integration (Lane B upgrade): route through the real m3iosis braid-grammar
  engine so the Frobenius-closure verdict (μ∘δ=id) is the native race signal.

### parity_testbed.py / race_testbed.py — verification harnesses
- parity_testbed: confirms the scanner's split/fuse round-trip is identity.
- race_testbed: confirms the braid invariant predicts actual race findings
  with zero false positives.

### gate_ordinals.sh — mOMonadOS kernel regression gate
- Every catalog write (e.g. the scanner's imscription) guarded by the kernel's
  "ALL 44 VALUES MATCH Lean" ordinal check.

## 2. Integration family

- **m3iosis** — braid-grammar engine; braid word → typed tuple; Frobenius-closure
  verdict = native race signal. `m3`, `m3 info`, `braid-grammar`, `--fusion`.
- **mOMonadOS** — bare-metal kernel; self-imscription + self-verification;
  the ordinal regression gate for catalog writes.
- **MoDoT** — tuple-algebra verbs (click/annihilate) on instrument tuples;
  `./ask`, `--features`, TOOLS_math.md.
- **p4rakernel** — Lean 4; every closure claim cross-checked as a typed term;
  sorries are original claims, named as such.
- **para_vm** — B4 Belnap FOUR; dialetheic kernel for interrogating B-cells.

## 3. Anti-tools (never used)

- Anything that sends POST/PUT/DELETE, creates state, touches auth, or exceeds
  the program's rules of engagement.
- Time-based race detection (timing luck) — replaced by the closure argument.

## 4. The launcher (integration layer)

`p4rapend/bughunter_agent.py` — one-shot driver. Initiate, and it
browses the bounty program page, discovers participating hosts, scans them
differentially (SAFE), verifies (testbeds + kernel gate), triages B-cells,
runs the race oracle, writes the report, fills the prepared email, and
enters WAIT. Usage: see BUGHUNTER_CONSTITUTION.md §9.

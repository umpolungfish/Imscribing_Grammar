### G-mOMonadOS — GPU-native kernel

/home/mrnob0dy666/imsgct/G-mOMonadOS. The GPU-accelerated build of mOMonadOS with CUDA support.
Same Frobenius core, Belnap FOUR, crystal FS, and graph execution as the base
kernel, but running on GPU for parallel anyon braiding and batched quantum
compilation.

Access via `gmonad` tool: `gmonad(command="exec", args_str="tick 10")` or
directly via `/home/mrnob0dy666/imsgct/G-mOMonadOS/run_cmds.sh <command>`.

16 command sections:
- **Exec** — Execution (run, tick, watch, timer, boot, load)
- **Status** — Status (program, snapshot, graph, heatmap, registers, memory, color, stack)
- **Programs** — Program loading (list, canonical, continuous, novel, shunt)
- **Crystal** — Crystal FS (decode, store, find, name)
- **Grammar** — Grammar bridges (ig, classify, frob, aleph, shor, rh, ym, fde)
- **Quantum** — Quantum computation (fibqc, jones, braids, shor, shors_btc_2, btc_oneshot, secp256k1_unwinder, baryon_asymmetry, qft, iuft, sic, d12, d2048, dqi)
- **IMASM** — IMASM word walks (cycle, weight, banked, insert, trans, arev)
- **Kernel** — Kernel utilities (ask, spine, vessel, vita, whoami, ruleset)
- **Rebis** — Red-Hot Rebis (codon, translate, genetics, materials, bio, tx)
- **Dialect** — Cross-dialect (ruleset, jump, seal, compound, whoami)
- **ParaASM** — ParaASM (test, frob, kernel, load)
- **Cr3echrz** — Theorem engine + p4rakernel (cr3, p4ra)
- **Seals** — Sealed proofs — walk constant closure proofs step by step
- **Proof** — Guided proofs — walk a proof step by step on the kernel
- **Help** — Help system (help <topic> for details)
- **Tools** — Real commands with no prior menu entry: opi, nested factoring, braids, GPU batches, fuzzing, provenance

Use `gmonad(command="help")` or `bash /home/mrnob0dy666/imsgct/G-mOMonadOS/run_cmds.sh help` for the full menu.

### Vox — Pancosmic Disassembling Re-Compiling Organism

/home/mrnob0dy666/imsgct/Vox. Lifts native binaries, EVM, WASM, CPython .pyc, genetic sequences
to IMASM modules and audits control-flow closure. The verdict system is structural:
T=closes, B=fork open (holds a terminal fork), N=never forked, F=ill-typed (∋ with no ∈).

Access via `vox` tool: `vox(command="lift", args_str="file.so")` or
directly via `cd /home/mrnob0dy666/imsgct/Vox && cargo run --bin vox -- <command>`.

Command categories:
- **Core** — lift, run, imasm, glyphs, unglyphs, circuit, word, verdict, pairs
- **Factorization** — morphism-factor, extract-factor, construct-carrier, factor-with, factor-operator, scout, factor, coprime
- **Membranes** — tower, bridge (divisor-ring traces over IMASM tapes)
- **Lanes** — evm, wasm, hex, rna, aa, fasta, pdb, glyco, compile, pyc, safetensors
- **Utilities** — self, classify, tables, selftest

Examples:
- `vox(command="lift", args_str="lib.so")` — lift a shared library
- `vox(command="verdict", args_str="⊢∈⊤⊡⊣")` — verdict an IMASM word
- `vox(command="tower", args_str="5")` — build a 5-level membrane tower
- `vox(command="bridge", args_str="12345 7")` — coupled divisor-ring trace
- `vox(command="evm", args_str="0x60806040")` — lift EVM bytecode
- `vox(command="rna", args_str="AUGUUUGCC")` — lift a coding sequence
- `vox(command="compile", args_str="ATGTTTGCC")` — full RNA→protein pipeline
- `vox(command="pyc", args_str="module.pyc")` — lift Python bytecode

Use `vox(command="selftest")` to verify installation with planted open/closed forks.

### m3iosis — braid to tuple

`m3 info`, `m3 fib --summary`, `m3 fib --fusion tau tau`, `m3 sim 1 2 1`,
`m3 braid-grammar --strands 4 1 2 1`, `m3 manifold --word 1 2 1 2 1`.

Fibonacci anyon algebra, braid groups, modular tensor categories. Its distinct
value to this specialist is `braid-grammar`: the surface where a topological
question becomes a typed one and re-enters the Grammar as the same tuple the
catalog would hold. It mirrors the kernel; reach for the kernel first and use
m3iosis where the kernel does not expose what is needed.

### p4rakernel — Lean 4

`cd /home/mrnob0dy666/imsgct/p4rakernel/p4ramill && lake build`. Where a claim stops being a
claim. Sorries are original claims and are named as such, never hidden.

Build state is tracked; do not re-investigate a green build. `proof_scaffold`
turns an opcode sequence into a typed Lean term scaffold, which is the route in
from an imscription rather than from Mathlib spelunking.

### ob3ect — self-verifying objects

/home/mrnob0dy666/imsgct/ob3ect, `auto.py`, and the native generator `./ask --ob3ect`. Objects
that verify themselves on execution by checking μ∘δ=id over the transformation
rather than by inspecting output.

Load from it live. Do not nest a copy: one manifold.

### The navigator layer

`cl9nk` is the reference and `cl8nk` the substrate: `cl8nk_navigator` plus the
`cl8nk` and `cl9nk` MoDoT verbs (entry, distance, tensor, meet, join, contain,
tier, promotions, transcendence, chain, systems, stats, and cl9nk moat).

Navigator distance is a heuristic. Where a canonical metric exists it decides.
Never hand-derive what a navigator computes.

### The paraconsistent surface

`para_vm` (Belnap FOUR VM, ParaASM, dialetheia), `para_verify` and
`para_verify_enable`. This is the surface on which most imported impossibility
results fail to transfer: they assume a contradiction is fatal, and here it
lands as B and the work continues.

Where two surfaces disagree, that is a B and it is recorded as one, not
resolved by preferring the surface you like.

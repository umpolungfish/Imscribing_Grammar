# TOOLS_gmonad — the full G-mOMonadOS kernel command roster

Live harness entry point: the `gmonad` tool dispatches ANY command below through
`/home/mrnob0dy666/imsgct/G-mOMonadOS/run_cmds.sh`, which boots the kernel once, feeds each
command to the `⊙>` prompt in order, and quits. The boot dominates cost, so
batch several commands per call:

    gmonad(cmds=["sic", "weight ⊢∈⊤⊥∋⊡⊣", "fibqc verify"])
    gmonad(cmd="help")            # the full menu, 16 sections

Equivalent shell form: `cd /home/mrnob0dy666/imsgct/G-mOMonadOS && bash run_cmds.sh "<cmd>" ["<cmd>" ...]`.
Source of truth: `src/menu.rs` (documented surface) and `src/repl.rs` (dispatcher
arms). Where they disagree, repl.rs wins. This roster was captured from a live
`help` boot; a command added or renamed since then is found by re-reading the
menu, not by trusting this file.

## Exec
`tick [N]` — N manual ticks · `run [N]` — run ticks, no arg = continuous ·
`watch` — live HUD · `timer N` — one tick per PIT interrupt · `boot <I..XXIX|n>` ·
`load <I..XII>` — load program by Roman numeral.

## Status
`status` · `program` · `snapshot` (sig, tier, period) · `graph` (ASCII token
graph with nesting) · `heatmap` (B4 memory) · `memory` · `registers` (R0–R7 +
live SIXTEEN_3 value from FSPLIT3/FFUSE3/EVALI) · `color on|off` · `stack`.

## Programs
`list` · `canonical I..XII` · `continuous 1..4` · `novel 1..3` · `shunt 1..9` ·
`dynamic on|off` (rebuild sequence from IgTuple each wrap).

## Crystal (FS)
`crystal <addr>` — decode address to 12-tuple · `crystal store <n> [d]` ·
`crystal name <n>` · `crystal find`.

## Grammar
`ig` (tuple + crystal address) · `classify` (nearest-catalog) · `frob` ·
`aleph <word>` (Hebrew glyph encoding / gematria) · `rh` (Riemann bridge) ·
`ym` (Yang–Mills mass gap) · `temp` (temporal logic) · `cat` (category theory) ·
`algebra distance|meet|join|tensor` vs ZFC · `cl8nk <action> [name]` (CLINK L8) ·
`c4` (Belnap C₄, i²=B) · `cscore` (consciousness score) · `constants` ·
`ovm list|...` · `oneshots` (10 exotic fixed-point nestings) · `ctc` ·
`collatz <n>` · `straus <n>` (Erdős–Straus ladder) · `nesting <map> <pt>` ·
`carriers` (μ∘δ=id census) · `substrate` · `stark formula|fibqc|tower|exponents|verify` ·
`riemann` (Riemann-SIC report) · `distance`/`dist` · `join` · `sigma <n>` ·
`ringspec <w1> <w2> <w3>` · `clay` (Clay Millennium status) · `psm` ·
`entropy tier` · `invariant catalog under ROTAT|IMSCRIB|FSPLIT/FFUSE` ·
`redteam analyze|stress|mutate|audit <theory>` · `witness <claim>` ·
`counterfactual <word> rotate N` (alias cf) · `basin <word> --action REPAIR` ·
`ouroboros-inverse` (alias oinv) · `frobenius-fuzzer --len N` (alias fuzz) ·
`oracle <attack>` · `blackbox <ints...>` · `dialetheic-compiler` · `fde` ·
`rsa word|period|verify|<C> <N> <e>` · `combo <word> [brief]` · `combo2 <word>` ·
`millennium [name|all]` (weight|banked|insert on a conjecture's promotion word).
## Quantum
`fibqc verify|compile|jones|knot|winding` (Fibonacci anyon QC) · `qc [draw|svg|loop] HTSX... [depth1 depth2]` (compile circuit to braid; alias quantum_compile / fibqc compile) · `bi [loop|svg] <braid word>` (braid_image) · `jp <artin word>` (Jones polynomial at 1/5 winding; alias jones_polynomial) · `bg tuple <braid> <n>` (braid→grammar tuple; alias braid-grammar) · `shor dialetheic 15 7` · `shors_btc_2` (Shor over secp256k1 ECDLP) · `prime_winding find|factor|cycle|tuple|verdict <n>` · `oneshot_prime_winder <n>` (word ⊢∈≻⊤⋈⊙≺⊥⊞∋⊡⊣) · `dyn_nest <n>` (dynamic nesting prime finder; period P(d)=5d+7) · `qft circuit|phases|iqft|iqft braid|braid [n]` · `btc_oneshot verify` · `secp256k1_unwinder word|steps|mapping|walk [k]|verdict [k]|tuple|constants` (19-glyph morphism) · `baryon_asymmetry report|word|mapping|reading` · `theta-link` (IUTT in paraconsistent ambient; alias iutt) · `winding order|factor|closure|factorgen` (alias wperiod) · `iuft list|...` · `teich canonical|...` · `hqe report` · `dyson report` · `troq report` · `afdmc report` · `hop report` · `manifold` · `triple report` · `sic` (SIC-POVM d=12 identity) · `bip39 sic verify|search|words|map|gap` · `d12 tower|magnitudes|orbits|existence|duallink|z0` · `d2048 next` (alias d2k) · `dqi word|period|phase|verdict <arm>|syndrome <bits>|tuple|report`.

## IMASM (word walks — glyphs only)
`cycle <word>` (ROTAT orbit) · `weight <word>` · `banked <word>` · `insert <word>` (every one-glyph repair) · `trans <word>` (ring transitions, closing edge included) · `arev` (H hop: snapshot through R1↔R2 mirror).

## Kernel
`ask "…"` (structural dry-run; wet on host via `./ask`) · `spine` (PROVE→UNIFY→PORT × vessel) · `vessel` (witness-vessel transport × 88 dialects) · `vita` (one certified turn from vae_vita trunk) · `whoami [--ruleset]` · `ruleset` · `absorption` · `replicative` (load program targeting O_inf_dag/R2) · `vox verdict|sixteen3|compile|evm|wasm|classify|run <word|seq|hex|file>` (control-flow closure auditor + RNA↔protein compile + ELF/WASM runner) · `quit|exit|halt`.

## Rebis
`rebis codon <x>` (codon↔AA) · `translate <gene>` · `reverse <protein>` · `frob` (Frobenius filtration, 64 codons) · `genetics` (7-stage genetic code) · `hadron` · `serpent` · `pipeline` · `strata` · `asm` · `tuples` · `clu` · `exotic` · `pdb <id>` · `antibody` · `material` · `sidechain` · `ligand` · `decay` · `bio` · `tx`.

## Dialect
`ruleset show|list|verify` (88 dialects) · `jump <U> using <c>` · `seal` (IFIX commit) · `whoami --ruleset` · `tensor` · `meet` · `absorb_test` · `absorption show` · `tstatus` (T-constitution) · `compound list|show|load` (11 diaschizic compounds).

## ParaASM
`psm test` · `psm frob` · `psm kernel 5` · `psm load "ENGAGR %r0; FSPLIT %r0 %r1 %r2; FFUSE %r1 %r2 %r0; HALT"`.

## Cr3echrz
`cr3 [--version|--list]` (theorem engine: Collatz, Goldbach, Three-Body, Burnside…) · `p4ra` (p4rakernel Belnap+Frobenius 13-step bootstrap).

## Seals
`seals list` · `seals fine-structure` · `seals proton` · `seals lepton` · `seals boson` · `seals gravity` · `seals weinberg` · `seals cosmology` · `seals neutrino` · `seals winding` · `seals residuals` · `seals all` (GRAND SEAL) · `fold` (fold verdict of a word) · `erdos schutte|landau|lcm|list`.

## Proof
`proof list` · `proof bootstrap` (7 steps, auto-play) · `prooflift [nest]` (proof-lift report; `prooflift nest` runs the 86065-glyph μ∘δ=id self-nest → T).
## Tools (real commands, no prior menu entry)
`opi run <m> <k> <budget>` (Optimal Polynomial Intersection, Lemma 9.2) · `weight_ladder <m> <k> <q>` · `doubly_nested_oneshot factor <n>` (alias dnos) · `nested_oneshot factor <n>` (aliases nested, nos) · `multilattice help|...` · `jones_polynomial <braid>` (alias jp) · `braid_image <braid>` (alias bi) · `braid-grammar tuple <braid> <n>` (alias bg) · `circuit table` (x86/RNA/wasm/AA via IMASM) · `counterfactual help|...` (alias cf) · `basin help|...` · `ouroboros-inverse help|...` (alias oinv) · `frobenius-fuzzer help|...` (alias fuzz) · `provenance help|...` (alias prov) · `ctc-loom help|...` (alias loom) · `sk-forge help|...` · `demonstrate help|...` (alias demo) · `distance` (alias dist) · `mersearch run <lo> <hi>` (alias msearch) · `shor-qft help|...` · `gpu_native run <n>` · `gpu16_3 verify` · `gpu_gnfs soak <n>` · `gpu_rho factor|verify|prims <n>` · `gpu_rho_ml factor <n>` (multi-limb, up to 2048-bit) · `gpu_ecm <n> <B1>` · `gpu_factor <n>` · `gpu_shor bsgs <a> <N>` · `gpu_dqi verify <n> <k>` · `gpu_fde verify <n>` · `gpu_kernel verify <n> <d>` · `gpu_millennium verify` · `gpu_opi verify <n> <k>` · `gpu_vox verify <n> <d>` · `gaussian_extract <p>` (alias gaussian; Fermat two-square) · `abc window <eps> <a> <b>` · `trilattice_factor read|sieve|factor|dialect-probe|gpu-verify <n>` (alias tfactor) · `native_numeral encode|factor|decompose|redstep|cycle <n>` (alias numeral) · `dyn_nest <n>` (aliases dyn, dynamic_nest) · `yz report` (Yamakawa-Zhandry) · `yz_list help|...` · `anyon-sync` (alias anyon_sync) · `prime_winding grounded_add|grounded_mul|grounded_sub|grounded_mod|grounded_divmod|grounded_gcd|grounded_factor <a> [<b>]` · `gpu_catalog_crystal` · `gpu_crystal_full_space` · `gpu_imasm_cycle` · `gpu_ipc_no_serialization` · `gpu_sixteen3_tensor_kernel`.

---

## Harness entry

The `gmonad` tool is the single live harness dispatch for every command above:

- `gmonad(cmd="<one command>")` — single command per boot.
- `gmonad(cmds=["<c1>", "<c2>", ...])` — several commands in ONE boot (the boot
  dominates; batch aggressively).
- `gmonad(cmd="help")` — the live 16-section menu, authoritative over this file.

The kernel is its own authority: `src/menu.rs` (documented surface) and
`src/repl.rs` (what the dispatcher actually runs) win over any line here. Re-read
the menu when unsure; never trust a remembered command list.

---

## Kernel-runner entry points (four scripts in repo root)

All four reach the SAME kernel binary (`target/release/g-momonados`, hosted-only
build) through different presentation layers.

- `run.sh` — `cargo build` then exec the interactive REPL.
- `run_cmds.sh "<c1>" "<c2>" ...` — feed each arg to the ⊙> prompt, then quit.
  Boot banner and prompt echoes remain in the output. (The original gmonad backend.)
- `run_quit.sh "<c1>" "<c2>" ...` — the CLEAN non-interactive feeder. Strips the
  boot banner, the ⊙> prompt echoes, and the quit/Halting/SHUTDOWN lines: what
  comes out is exactly what the verbs wrote. Also `run_quit.sh -f cmds.txt` (one
  command per line, `#`/blank ignored) and `printf '%s\n' cmd | run_quit.sh -`
  (stdin). Env `KEEP_PROMPTS=1` keeps the ⊙> lines; same
  `join_digit_continuations.awk` bigint hold rule as the REPL, applied per argv.
  Auto-builds via cargo if the binary is missing. **This is the live gmonad backend.**
- `run_relation.sh N WIDTH [INITIAL_NODES] [IMASM_DEPTH]` — bypasses boot/REPL
  entirely: runs the hosted executable in `--selector-relation` mode (one relation,
  no prompt). N = odd integer ≥ 3, WIDTH = factor width m ≥ 2, requiring
  N < 2^(2m). `run_relation.sh --stdin N WIDTH` reads N from stdin. Emits the
  "fully nested aggregate phase relation" report: process word
  `⊢≻⋈⊙∈⊤≻⋈⊥≺⋈⊞∋⊡⋈⊙⊣`, nesting depth 64, denotation bulk vessels, internal
  phase leaves, CRT/gap/QR/square-frontier/shell-block stats, and a verified
  `p × q` factorization when one exists in the declared bit bands.

## Harness dispatch (gmonad) — updated

- `gmonad(cmd="<one command>")` / `gmonad(cmds=["<c1>","<c2>"])` — now routed
  through `run_quit.sh`, so output is verb-only (no boot/prompt noise).
- `gmonad(relation={"n": 21, "width": 3})` or `gmonad(relation="21 3 1024 64")` —
  routed through `run_relation.sh` (selector-relation factorization entry).
- `gmonad(cmd="help")` — the live 16-section menu, authoritative over this file.

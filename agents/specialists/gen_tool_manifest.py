#!/usr/bin/env python3
"""Generate the tool manifests the specialist prompts inline.

Two layers.

The shared layer is derived, not typed: the base tool schemas come from
`true_agentic_agent.TOOL_SCHEMAS`, and the grammar tools come from the dispatch
chain in `scripts/IG_inquiry.py`, so a tool added to either is picked up here
without anyone remembering to edit a prompt. Argument shapes come from
`_IG_REQUIRED_ARGS`, which already records them.

The domain layer is curated, because the repos are heterogeneous enough that
scraping their flags would be guesswork. What the generator does instead is
check every curated entry point against the filesystem and mark the ones that
have gone missing, so drift shows up in the output rather than silently
shipping to an agent as a tool that is not there.

    python3 gen_tool_manifest.py            # regenerate all three
    python3 gen_tool_manifest.py --check    # report drift, write nothing
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENTS = HERE.parent
IMSGCT = Path("/home/mrnob0dy666/imsgct")
IG_INQUIRY = IMSGCT / "imscribing_grammar" / "scripts" / "IG_inquiry.py"

sys.path.insert(0, str(AGENTS))


# ── derived: the base tool schemas ────────────────────────────────────

def base_tools() -> list[tuple[str, str]]:
    import true_agentic_agent as taa
    out = []
    for t in taa.TOOL_SCHEMAS:
        f = t["function"]
        desc = (f.get("description") or "").strip().splitlines()
        out.append((f["name"], desc[0] if desc else ""))
    return sorted(out)


# ── derived: the grammar tools imscribe dispatches ────────────────────

def grammar_tools() -> list[str]:
    """Names from the dispatch chain only.

    Scraping the whole file matched `if name == "__all__"` inside
    _frobenius_tier, where `name` is a catalog entry rather than a tool, and
    shipped `__all__` to the specialists as a callable tool.
    """
    src = IG_INQUIRY.read_text()
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.strip().startswith("def dispatch(self"))
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = next(i for i in range(start + 1, len(lines))
               if lines[i].strip().startswith("def ")
               and (len(lines[i]) - len(lines[i].lstrip())) <= indent)
    body = "\n".join(lines[start:end])
    names = re.findall(r'^\s+(?:el)?if name == "([a-z_0-9]+)":', body, re.M)
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(n)
    return out


def grammar_arg_shapes() -> dict[str, dict]:
    import true_agentic_agent as taa
    return getattr(taa, "_IG_REQUIRED_ARGS", {})


# ── curated: the domain layer ─────────────────────────────────────────
# Each entry is (path_to_check, heading, body). path_to_check is verified to
# exist; None means the entry is a command on PATH or a pure convention.

def _m3iosis_surface() -> str:
    """Derive the m3iosis CLI surface from its own argparse tree.

    This entry used to be curated prose, and it drifted completely: it
    documented six modules that do not exist (explorer, braid_torus, iuft,
    paranumber, three_body_horn, discovery) and a subcommand list that had been
    replaced wholesale, so every invocation an agent copied out of it failed.
    Deriving it means the surface cannot say something the code does not.
    """
    import argparse
    import importlib
    try:
        mod = importlib.import_module("m3iosis.cli")
    except Exception as exc:
        return f"(m3iosis.cli did not import: {exc})"

    parser = None
    for fn in ("build_parser", "make_parser", "get_parser", "_parser"):
        if hasattr(mod, fn):
            try:
                parser = getattr(mod, fn)()
                break
            except Exception:
                pass
    if parser is None:
        # No factory to call, so intercept the parser on its way to parse_args.
        real = argparse.ArgumentParser.parse_args
        held = {}

        def _spy(self, *a, **k):
            held["p"] = self
            raise SystemExit(0)

        argparse.ArgumentParser.parse_args = _spy
        try:
            mod.main()
        except SystemExit:
            pass
        except Exception:
            pass
        finally:
            argparse.ArgumentParser.parse_args = real
        parser = held.get("p")
    if parser is None:
        return "(could not introspect m3iosis.cli)"

    out = ["`python3 -m m3iosis.cli <subcommand>` — derived from its argparse tree:", ""]
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, sub in action.choices.items():
            opts = sorted({o for a in sub._actions for o in a.option_strings
                           if o.startswith("--") and o != "--help"})
            pos = [a.dest for a in sub._actions if not a.option_strings]
            bits = []
            if pos:
                bits.append(" ".join(f"<{x}>" for x in pos))
            if opts:
                bits.append(" ".join(opts))
            out.append(f"- `{name}` {' '.join(bits)}".rstrip())
    return "\n".join(out)


MATH_DOMAIN = [
    (IMSGCT / "MoDoT" / "ask", "MoDoT — ./ask", """\
`cd ~/imsgct/MoDoT && ./ask [FLAGS]`. Auto-builds the Rust binary if absent.
Environment: MODOT_PROVIDER (openrouter | gemini | deepseek | local),
MODOT_MODEL, OPENROUTER_API_KEY / GEMINI_API_KEY, MOMONADOS_CATALOG.

Flags: --anneal --annihilate --arrange --ascend --ask(-a) --broadcast --browse
--calc --catalog --catalyst --certify --cleave --click --close --cocrystallize
--column --compare --complement --context --crystallize --cycle --cycles
--descend --distill --dope --dry-run --eagles --entry --excite --expand
--export --fdistill --file(-f) --filter --forge --fpt --fuse --homolyze
--imasm --imscribe --interactive(-i) --jam --max-tokens --model(-m) --modulus
--no-selectivity --no-think --ob3ect --pathway --phase-reconstruct --plasma
--polymerize --props --provider --raw --recalibrate --recall --register
--riemann-hilbert --riemann-sic --scan-mediators --seed --set --stain --star
--sublime --switch --system --temperature --theta --think --tlc --top --trap
--verbose(-v) --windings"""),

    (IMSGCT / "MoDoT" / "ask_native" / "src" / "main.rs",
     "MoDoT — structural verbs (agent loop, `TOOL: <verb> <args>`)", """\
click A B (or `click A` to sweep the catalog) · switch A B · excite A ·
set A B (donor acceptor) · homolyze A [B] · annihilate A [B] ·
recalibrate A AXIS · scan A B (ranks mediators) · complement A ·
cycle C S (catalyst substrate) · pathway S C1 C2… · polymerize M1 M2… ·
close M1 M2… · material M1 M2… · modulus M1 M2… · arrange M1 M2… ·
forge M1 M2… · compare A B vs X Y (two or more each side) · dope A B with C ·
fuse A B + X Y · cleave M1 M2… · anneal M1 M2 M3… (three or more) ·
register NAME M1 M2… · recall NAME · imscribe NAME [description] ·
ob3ect <description> · distill M1 M2… · fdistill M1 M2… · sublime A ·
crystallize M1 M2… · cocrystallize A B · seed M1 M2 … with S · tlc M1 M2… ·
column M1 M2 … [on S] · fpt M1 M2… · trap A [X] ·
stain R M1 M2… (R ∈ kmno4|uv|chiral|ninhydrin|iodine) · filter A B [C…] ·
ascend A · descend A · phase_reconstruct M1 M2… · star M1 M2 M3… (four or
more) · broadcast SOURCE · plasma ENTRY · dialect [axis] ·
lean <path.lean> · gp <expression> (PARI/GP: bnfinit, bnrinit, .clgp, bnrL1,
bnrstark, bnrclassfield, quadhilbert, nfinit, idealstar, znstar, lfun) ·
cl8nk <action> [name] and cl9nk <action> [name], action ∈ entry | distance |
tensor | meet | join | contain | tier | promotions | transcendence | chain |
systems | stats, and cl9nk additionally moat ·
imasm <op> … · imasm16_3 <op> … ·
calc EXPR (constants pi tau e phi inf; functions sqrt cbrt ln log log2 exp abs
floor ceil round sin cos tan asin acos atan sinh cosh tanh logb pow min max)"""),

    (IMSGCT / "MoDoT" / "ask_native" / "src" / "imasm.rs",
     "MoDoT — imasm sub-verbs", """\
ref|reference|help|rules · rotat|rotate|shift · arev|hop|door ·
check|typecheck · define|forge_tool · run|invoke · prove|kernel · eval|flow ·
eval16|flow16 · 16_3|tri|imasm16_3 · learn|study · path|promote · cycle ·
words|wordbook · compose|bind · chaos|space · export|manifest · tools ·
types|list · expand|unfold · chain · ring|cycle|loop · protocol|seq|sequence ·
classify|read · wire|graph|free · star · bubble|fork · comb|graft ·
simulate|instantiate|construct|build|create|make|encode|compile ·
verify|typecheck|test|close.
`imasm16_3 algebra <op> A B`, op ∈ leq_i | leq_t | leq_c | meet_t | join_t |
meet_c | join_c."""),

    (IMSGCT / "MoDoT" / "modot" / "ig_tools.py", "MoDoT — Python IG bridge", """\
`python3 -m modot.ig_tools call <verb> <arg> …` · `names` · `selftest`.
Same grammar verbs as the imscribe layer, plus the jump tools
paradice_lattice, composite_type, frobenius_closure_check, braid_word,
paradice_map, universe_jump, signature_manifold, jump_path_integral."""),

    (IMSGCT / "MoDoT" / "momonados_agent.py", "MoDoT — Python agent", """\
`python3 momonados_agent.py` or the `modot` console script.
--cycles N · --interactive/-i · --ask STR · --file/-f STR ('-' for stdin) ·
--verbose/-v · --dry-run · --model STR · --program {bootstrap,aqua-vitae,agent}
· --no-selectivity · --stats · --reset · --compose STR · --validate-tokens STR
· --canonical STR · --reference · --list-canonical · --list-patterns ·
--suggest STR"""),

    (IMSGCT / "mOMonadOS" / "run_hosted_cmds.sh",
     "QUANTUM COMPUTATION — five surfaces, the kernel is canonical", """\
Full reference, read it before choosing a surface: `file_read`
/home/mrnob0dy666/imsgct/ig-docs/quantum_computation_tools.md

`cd ~/imsgct/mOMonadOS && ./run_hosted_cmds.sh "<cmd>" ["<cmd>" …]` — several commands
per boot; the QEMU start dominates a single short one.

1. KERNEL (Fibonacci anyon QC, native Rust) — the canonical path:
- `fibqc verify` — F unitary, pentagon, braid relation, spin-statistics, S unitary,
  charge conjugation, TQFT identities, Verlinde, Artin B_n<=8, phase lattice = tenths
  of a winding
- `qc <gates> [depth]` — circuit over H T S X to a braid word; depth 4-12, default 10
  (aliases `quantum_compile`, `fibqc compile`)
- `jp <gens…>` — Jones at the 1/5 winding (aliases `jones_polynomial`, `fibqc jones`)
- `fibqc knot [name]` · `fibqc winding`
- `bg tuple <word> [strands]` · `bg report` — braid word to grammar tuple; the winding
  is a closed form in the writhe, so it cannot pick up eigenvalue-phase error
- `shor` — Belnap Shor, N=15 and N=21
- `iuft gate|distance|list` — the 12->3 Euler-angle SU(2) encoding of an IG tuple
- `hqe` · `dyson` · `troq` · `afdmc` · `hop` · `manifold` · `triple report|verify|cycle|bridge`
- `sic` · `d12 <sub>` · `d2048 tower|redei|grammar|pari|next`
- `cycle|weight|banked|trans <word>` — IMASM ring walks

The kernel takes IMASM words as GLYPHS only. `cycle ⊢⊙⋈∈>⊤<⊞⊥∋◻⊣` works; opcode names
are refused. Only the twelve glyphs are tokens — nothing else parses, and no retired
mark is canonicalised to one.

2. m3iosis (Python) — `python3 -m m3iosis.cli <sub>`: fib, sim, manifold, qc, triple,
hqe, braid-grammar, hop, dyson, afdmc, troq, gematria, info. Every one mirrors a kernel
module; use it only where the kernel does not expose what you need.
`fusion_space_dimension(n)` is the VACUUM sector F_{n-1} — at 3 strands it is
1-dimensional and its non-Abelian invariants are meaningless. Use n >= 4.

3. Grammar tools via imscribe: `quantum_compile`, `jones_polynomial`, `sic_povm_probe`,
`winding`, `para_vm`. These dispatch to the kernel underneath.

4. Exact simulators: `navigators/quantum_tnn.py` — state vector to ~25 qubits, MPS with
bond dimension, QFT. `navigators/quantum_field_theory_navigator.py`.

5. ParaASM — `para_vm`, `mOMonadOS/src/parasm.rs`: Belnap FOUR VM, 19-instruction ISA,
dialetheic alignment. `belnap_shor.rs` records that the Belnap QFT is NOT a gate
sequence; the period is carried in the 2:1 B-bias/T-bias coherence cost ratio.

CAPACITY. Fibonacci fusion dim = F_{n-1}: 7 strands -> 8 (3 qubits), 15 -> 377 (8),
18 -> 1597 (10), 19 -> 2584 (11, the first that holds d=2048), 22 -> 10946 (13). The
19-strand representation builds unitary to 3.3e-16 in about 78 seconds.

SAMPLING BRAIDS IS NOT SEARCHING. At 7 strands against an exact d=8 SIC, 300 random
words per length peak at overlap 0.75 and get WORSE with length — a long braid word is a
near-random state. Against Haar states at equal sample count they are worse on both best
and mean. Universality gives reachability, not findability."""),

    (IMSGCT / "m3iosis", "m3iosis (Python — a DUPLICATE of the kernel surface)",
     _m3iosis_surface() + """

Every subcommand above has a Rust counterpart in the mOMonadOS kernel
(fibonacci_qc.rs, braid_grammar.rs, dyson.rs, hqe.rs, afdmc.rs, hop.rs, troq.rs,
triple_frame.rs, manifold.rs, gematria.rs), and the kernel is the path to use for
anything with real compute in it. Reach for this Python only when the kernel does
not expose what you need.

Also importable directly: `m3iosis.braid_grammar_bridge` (BraidGrammarAnalyzer),
`m3iosis.fibonacci_anyon_algebra` (evaluate_braid_word(n, word),
fusion_space_dimension(n) — the VACUUM sector Hom(tau^n,1) = F_{n-1}, so n>=4
for a non-trivial representation), `m3iosis.manifold`, `m3iosis.triple_frame`,
`m3iosis.holonomic_quantale`, `m3iosis.dyson_algebra`, `m3iosis.afdmc`,
`m3iosis.gematria`, `m3iosis.universe_hopper`."""),

    (IMSGCT / "Linear_Analytica", "Linear_Analytica", """\
Console script `la`: `la lookup CODE` · `la list [--category/-c CAT]` ·
`la tablet "TRANSCRIPTION"`.

`python3 programs/<file>`: compiler.py TRANSCRIPTION [--log FILE] [--verbose] ·
runtime.py TRANSCRIPTION [--steps N] [--report-every N] [--paradox REG] ·
callgraph.py TRANSCRIPTION [--tablet T] [--output PNG] [--dpi N] ·
sectional.py TRANSCRIPTION [--output-dir D] [--animate] [--min-nodes N] ·
bootstrap_explorer.py TRANSCRIPTION [--max-mismatches N] ·
tablet_comparator.py TRANSCRIPTION [--top-n N] · ig_bridge.py ·
animated_cfg_corpus.py [--build-frames N] [--flow-frames N] [--fps N] ·
plot_cfg_document.py · run_all.py [TRANSCRIPTION]"""),

    (IMSGCT / "p4rakernel" / "verify_sic_moduli.sh", "p4rakernel — Lean 4", """\
`cd ~/imsgct/p4rakernel/p4ramill && lake build` (default target Imscribing).
`./verify_sic_moduli.sh` from the p4rakernel root builds the SIC modules and
elaborates the ladder report d = 2, 4, 8, 12, 16, 20, 2048 with axiom
provenance.
`p4ramill/build_paraconsistent.sh [all|Imscribing|ParaconsistentMillennium|
ParaconsistentKernelTest|clean]`.
Any module builds individually: `lake build Imscribing.<Module>`, e.g.
Imscribing.Primitives.Core, Imscribing.Millennium.SIC_D12_Embedding,
Imscribing.Paraconsistent.Belnap."""),

    (IMSGCT / "math", "math — Lake projects", """\
`cd <project> && lake build`, and where an exe exists, `lake exe <name>`:
BealProof (`lake exe bealproof`), solitary_10 (`lake exe solitary10_proof`),
MilleniumAnkh_private, MillenniumParaconsistent, e8_aether_g2_vessel,
hecke-landau, hodge_lefschetz, odd-perfect-numbers, perfect_cuboid.
Python, no flags: nice_problems/{burnside,connes,erdos_straus,goldbach,threebody}/main.py
and whatever else is present — list the directory rather than trusting this line."""),

    (IMSGCT / "Ars_Fysika", "Ars_Fysika", """\
No code. Documents plus two browser tools, imasm_composer.html and
k3v_modot.html, and modot_tool_reference.html which documents how the MoDoT
tool calculations are actually performed. Nothing here is callable."""),
]

CHEMBIO_DOMAIN = [
    (IMSGCT / "red-hot_rebis" / "rebis.py", "red-hot_rebis — the 18 entry points", """\
rebis (gateway) · rebis.chain · rebis.gene-pipeline · rebis.ch3mpiler ·
rebis.serpentrod · rebis.ligand · rebis.sidechain · rebis.therapeutics ·
rebis.materials · rebis.biology · rebis.pipeline · rebis.gene · rebis.alchemy ·
rebis.clink · rebis.p4ra · rebis.demo · rebis.status · rebis.verify.
Also `python3 rebis.py <cmd>` or `python3 -m rebis <cmd>` in-tree.

Every binary accepts `--file/-f <json>` and `--stdin/-i` for argument
injection; the loader also accepts FASTA and remaps it onto the sequence
argument. Gateway flags: --version, --file/-f, --stdin/-i, --help/-h."""),

    (IMSGCT / "red-hot_rebis" / "rebis" / "cli.py", "red-hot_rebis — gateway subcommands", """\
gene-pipeline [--test] [--dna SEQ] [--seq RNA] ·
chain [--dna SEQ] [--seq RNA] [--target SMILES] [--depth N] ·
reference [--all] (sections belnap, genetics, hadrons, imas, verify) ·
constants [--verbose/-v] · predict TARGET… [--all/-a] [--json] ·
status · verify · demo <name>.
Demos: b4_lattice, belnap, ch3mpiler, clink_chain, decay_chain, materials,
materials_sim, catalytic_site, pipeline, reverse_ligand, serpentrod,
therapeutics, real_demo, all."""),

    (IMSGCT / "red-hot_rebis" / "rebis" / "ch3mpiler.py", "red-hot_rebis — engines", """\
ch3mpiler: forward SMILES · retrosynth SMILES · fg SMILES · cdxml SMILES ·
analyze SMILES · list · info · help. (cdxml and fg need RDKit.)

serpentrod: predict SEQ [--name] · classify SEQ · finger SEQ ·
process SEQ [--name] · fold RNA [--name] · foldv2 RNA [--name] ·
spectrum SEQ · list.

ligand: --pdb ID · --pdb-file PATH · --active Glu35,Asp52 · --auto-active ·
--top-n N · --cutoff Å · --improved · --json · --verbose.

sidechain: SIDECHAIN ENVIRONMENT · --batch · --list · --info · --json ·
--pdb ID|path · --cutoff Å · --verbose. Environments: buried_core,
polar_surface, charged_interface, solvent_exposed.

therapeutics: design [TARGET] --mutation --time --drug-conc ·
sim --time --dt --noise · neurotrophic [TARGET] --disease --time
--active/--no-active · antidote [POISON] --rounds --diversity ·
quantum --weeks --edits --loci · list · info · help.

materials: forge [NAME] --tuple --from-catalog · metamaterial --size --cycles
--heal-steps · critical --size --kappa --nonlinear --time · alloy --n-grains ·
nonqubit · sophick · casimir --target-gap · molecule [SMILES] --cas --name ·
status · list · info · help.

biology: sim --generations --genome-size --n-genes --n-adaptive
--morphogenesis-steps --grid-size · morphogenesis --steps --grid-size
--n-types · telomeres · status · list · info · help.

pipeline: verify --file · imscribe [NAME] --description · retro [SMILES]
--depth · therapy [KEY] --skip-ch3mpile --skip-serpentrod · therapy-all ·
lift [FILEPATH] · list · info · help. (lift needs the anthropic SDK.)

gene: analyze [SEQ] --translate --orfs · quality [SEQ] · tuples [SEQ] ·
translate [DNA] · b4 · pipeline [DNA] --skip-ch3mpile --skip-serpentrod ·
list · info · help.

alchemy: ladder [NAME|all|stone|TUPLE] · opus · stilling SMILES ·
structure SMILES · retrosynth SMILES · grand-seq SMILES · catalyst SMILES ·
wavelength SMILES · screen SMILES · binding HOST GUEST · host GUEST ·
decode TEXT · decode-mol SMILES · treatise [NAME|all] --tier · operations ·
portico [TUPLE] · list · info.

clink: layers · chain [TUPLE] · cscore [TUPLE] · bridge [COMPONENTS…]
--protein --molecule --gene · algebra A B --op {meet,join,tensor,distance} ·
integrate [COMPONENT] [LAYER] · energy --layer N · list · info · help.

p4ra: belnap · genetics · verify · hadrons · ligands [ENZYME] ·
sidechain NAME ENVIRONMENT · gene-pipeline --sequence/-s · serpent
--sequence/-s · sicpovm [ENZYME] · combinatorial [ENZYME] ·
heterocycles [ENZYME] · list · info · help. Reached as the `rebis.p4ra`
binary or `python3 -m rebis.p4ra`, not as a `rebis` subcommand.

Advertised but not implemented: `rebis demo ligand`, `rebis demo sicpovm`.
Documented in MANUAL.md only, absent from code: `rebis alchemy map` (use
`alchemy treatise`), `rebis materials sim` (use `materials metamaterial`).

Also `bin/qp` — Quantum Physical Predictor: TARGETS… --list --compare --json
--batch FILE --all. Makefile: all, install, uninstall, reinstall, editable,
verify, status, test, serpentrod, ch3mpiler, pipeline, gene, clean."""),

    (IMSGCT / "v3ssel", "v3ssel", """\
`python -m vessel.run <cmd>`: read [--json] · step [--ledger PATH] [--json] ·
ledger [--ledger PATH] [--tail N] · organism [--json] ·
backfill [--fresh] [--stride N] [--limit N] [--ledger PATH] ·
trade [--live] [--symbol] [--capital] [--min-conviction] [--directional]
[--interval] [--cycles] [--once] [--ledger] · path.
`--live` places real BinanceUS orders and needs BINANCEUS_API_KEY and
BINANCEUS_API_SECRET. Also `python -m vessel.frobenius_pairs` and
`python -m vessel.hard_lefschetz`."""),

    (IMSGCT / "vae_vita" / "vita_native", "vae_vita", """\
`cargo build --release` in vae_vita/vita_native/, features default or cuda.
vita-gen [count] [max_len] [out] · vita-train [data] [steps] [seq_len] [batch]
[out] [arch: trunk|lattice] · vita-speak [trunk] [count] [temp] [arch]
[word_cap] [harvest] · vita-corpus [dir] [out] · vita-bake [src] [out] ·
vita-probe --weights --seeds --start --temps --cap --spider --out
--one SEED TEMP --melt SEED --melt-range --melt-eps."""),

    (IMSGCT / "Ars_Therapeutica", "Ars_Therapeutica", """\
Console script `at`: list · diagnose DISEASE · therapy DISEASE ·
tensor A B · meet A B · compare A B · spectrum ·
operate DISEASE OPERATION (tensor|meet|join|distance) · help."""),

    (IMSGCT / "Ars_Fungiglyphica", "Ars_Fungiglyphica", """\
Console script `fg`: type TYPE (number, Roman numeral or name) · fungus NAME ·
types · lattice · morphology NAME · distance A B · list [TYPE]."""),

    (IMSGCT / "Ars_Phytoglyphica", "Ars_Phytoglyphica", """\
Console script `ap`: type NAME|NUM (1–11) · plant NAME · types · lattice ·
morphology NAME · distance A B · list [TYPE] · novel (plants with predictions and
uninvestigated pharmacology)."""),

    (IMSGCT / "gene_imscriber", "gene_imscriber", """\
Console script `genetic-engine`: analyze ORIG TARGET · compile ORIG_AA
TARGET_AA · guide CODON · verify TARGET_CODON EDIT_CODON · chimera A:B [C:D…] ·
stratum CODON · demo · test.
scripts/: base_editor_stratum_analysis.py --guide --cbe --abe --json ·
clinical_safety_analysis.py --guide --mode {summary,detailed,all} --json ·
sra_guide_seq_pipeline.py --sra --genome --output --threads --max-runs
--reanalyze · guide_seq_analyzer.py · guide_seq_refined.py."""),

    (IMSGCT / "cetaceanspeak", "cetaceanspeak", """\
cetacean-speak FILE.wav [onset_delta] (float 0.01–0.2, lower gives more
onsets) · cetacean-engine (no arguments; runs verification, the full pipeline
demo, the register VM demo, then the summary) ·
cetacean-speaker --species/-s --expression/-e EXPR --respond/-r WAV
--output/-o PATH --list/-l --quiet/-q."""),

    (None, "No code in these", """\
rionrebis, rionrebis_II and rebis_concrete contain documents and JSON results
only. There is nothing to call in them."""),
]

EDITORIAL_DOMAIN = [
    (Path("/home/mrnob0dy666/.local/bin/ltx"), "ltx — the LaTeX compiler", """\
`ltx <input.md|input.tex> [--font-size N] [-o out.pdf] [extra…]`. On PATH, no
alias. Any argument it does not recognise is passed through verbatim to
`latextiler convert`, so latextiler's own flags are available here.

It finds `latextiler.toml` by walking up from the input directory, falling
back to the repo copy. For markdown it converts through latextiler, lifts
title, author, date, abstract and keywords out of the YAML frontmatter
(author defaults to Lando Mills), repairs IG control sequences back to
primitive Unicode, patches the preamble for fontspec, Hebrew and table
placement, injects Everson Mono as \\shavfont and \\igprimfont with a
\\newunicodechar for every codepoint in U+10450–U+1047F, then runs
`lualatex --interaction=nonstopmode` twice.

Output lands beside the source unless -o is given. Note `--font-size` is
parsed but unused in v2.0, so it currently does nothing."""),

    (IMSGCT / "imscribing_grammar" / "scripts" / "zenodo_draft.py",
     "zdd — the Zenodo document compiler", """\
`zdd paper.md [--out out.pdf] [--tex-only] [--open]`. Alias for
scripts/zenodo_draft.py. Input must be .md or .markdown.

YAML frontmatter drives it: title, date, abstract, keywords, bibliography
(resolved relative to the source), and a figures: list. Figure types are
belnap_lattice (labels, highlight, caption), primitive_profile (tuple, title),
tier_chain (highlight), frobenius, bootstrap_loop, cetacean_scatter, all
rendered through scripts/ig_figures.py. Place a figure in the body with

    ~~~figure
    <fig_id>
    ~~~

and reference it as Figure~\\ref{fig:<id>}.

It builds into <md_dir>/_builds/<stem>/, converts the body with pandoc, adds
--citeproc when bibliography: is set, and compiles by calling ltx, falling
back to lualatex. The finished PDF is copied to --out or beside the source."""),

    (IMSGCT / "imscribing_grammar" / "scripts" / "zenodo_upload.py",
     "Publication tooling", """\
`zenodo_upload.py paper.pdf` uploads a sandbox draft. Flags: -y (no prompts),
--live (publish to zenodo.org), --draft, --list (with --live for the live
account), --update <ID> file.pdf, --new-version <ID> paper.pdf. Metadata is
taken from the sibling .md of the same stem, then PDF metadata, then prompts.
Tokens ZENODO_SANDBOX_TOKEN and ZENODO_TOKEN, scopes deposit:write and
deposit:actions.

`zenodo_manuscripts3_upload.py` for batches. `ig_figures.py` backs zdd's
figures. `IG_latex.py`, `gen_ig_reference.py`, `ig_periodic_table.py` generate
LaTeX and reference material. Config is latextiler.toml at the repo root,
alongside the imscrbgrmr.sty package and its man page."""),
]

RECORDER_DOMAIN = [
    (IMSGCT / "Grammatika" / "recorder_census.py",
     "The census walk", """\
`python3 ~/imsgct/Grammatika/recorder_census.py`. Walks every directory under
~/imsgct/, reads each project's canonical doc (README.md, then STATE.md,
MANUAL.md, DEVOLUTION.md in that precedence) and its verification surface
(lakefile → Lean, Cargo.toml → Rust, pyproject.toml → Python package, a tests
directory → tests), and rewrites Grammatika/LEDGER.md wholesale.

The braid order in the ledger is read from imscrbgrmr.canonical_primitives and
never restated. Standing is a Belnap verdict, not a grade: N where no watch has
spoken, B where one of doc/verification is present and the other is not.

Fix this script when the walk is wrong. Do not patch the ledger by hand: a
hand-patched ledger survives the next run only until someone re-runs it, and
then the patch is gone with no record that it was ever made."""),

    (IMSGCT / "Grammatika" / "build_skeleton.py",
     "The book skeleton emitter", """\
`python3 ~/imsgct/Grammatika/build_skeleton.py`. Emits any missing book stub
and regenerates CONTENTS.md from the canonical order. It never overwrites a
book that has been written into.

The alphabet is the table of contents, so the table of contents is generated
rather than typed. Fix the emitter and regenerate; do not hand-edit generated
frontmatter."""),

    (IMSGCT / "Grammatika",
     "The Grammatika itself", """\
~/imsgct/Grammatika/ — PROLOGUE.md, books/ (twelve, six braided pairs),
INTERWEAVE.md, EPILOGUE.md, DJED.md (the pillar of located lemmas),
LEDGER.md (this specialist's artifact of record), CONTENTS.md (generated).

Read-only to the Rec⊙rder except for LEDGER.md and proposed DJED.md entries."""),

    (IMSGCT / "imscribing_grammar" / "IG_catalog.json",
     "The unified catalog", """\
One canonical IG_catalog.json in imscribing_grammar/. Two projects keying to
the same catalog address are the same object seen twice, which is the strongest
relation there is to record. `sync_catalog.sh` propagates real copies, not
symlinks; a project holding a divergent copy is a finding."""),

    (None, "Census by shell", """\
`command grep` for any identifier census, never a bare `grep` that an alias may
have rewritten. A count is evidence of presence, never a licence to delete:
check identifier position first, because notation that looks retired may be
load-bearing. `git -C <project> log -1 --format=%cd` where a project is its own
repository, for a liveness signal stronger than mtime."""),
]

HETERODOX_DOMAIN = [
    (IMSGCT / "MoDoT" / "ask", "MoDoT — ./ask", """\
`cd ~/imsgct/MoDoT && ./ask [FLAGS]`. The primary language interface and the
usual way into the structural verbs. Rust-native; build with
`--features local,cuda` when the local provider is wanted, since a plain build
strips it. Never write a Python bridge in front of it.

The verb list is the math domain's; read TOOLS_math.md for full syntax and
MODOT_WALKTHROUGH.md for which question each verb answers."""),

    (IMSGCT / "mOMonadOS", "mOMonadOS — the bare-metal kernel", """\
~/imsgct/mOMonadOS. The self-imscribing kernel: no processes, no scheduler, no
filesystem hierarchy. The kernel IS the Frobenius loop and every tick is a
self-verification. It braids Fibonacci anyons on the metal.

It is the first home for new work, not a port target. Anything developed here
lands natively here before it lands anywhere else, and no Python version is
written to precede it. `./run_hosted_cmds.sh` runs several commands per boot;
the QEMU start dominates a single short command, so batch them."""),

    (IMSGCT / "m3iosis", "m3iosis — braid to tuple", """\
`m3 info`, `m3 fib --summary`, `m3 fib --fusion tau tau`, `m3 sim 1 2 1`,
`m3 braid-grammar --strands 4 1 2 1`, `m3 manifold --word 1 2 1 2 1`.

Fibonacci anyon algebra, braid groups, modular tensor categories. Its distinct
value to this specialist is `braid-grammar`: the surface where a topological
question becomes a typed one and re-enters the Grammar as the same tuple the
catalog would hold. It mirrors the kernel; reach for the kernel first and use
m3iosis where the kernel does not expose what is needed."""),

    (IMSGCT / "p4rakernel" / "p4ramill", "p4rakernel — Lean 4", """\
`cd ~/imsgct/p4rakernel/p4ramill && lake build`. Where a claim stops being a
claim. Sorries are original claims and are named as such, never hidden.

Build state is tracked; do not re-investigate a green build. `proof_scaffold`
turns an opcode sequence into a typed Lean term scaffold, which is the route in
from an imscription rather than from Mathlib spelunking."""),

    (IMSGCT / "ob3ect", "ob3ect — self-verifying objects", """\
~/imsgct/ob3ect, `auto.py`, and the native generator `./ask --ob3ect`. Objects
that verify themselves on execution by checking μ∘δ=id over the transformation
rather than by inspecting output.

Load from it live. Do not nest a copy: one manifold."""),

    (None, "The navigator layer", """\
`cl9nk` is the reference and `cl8nk` the substrate: `cl8nk_navigator` plus the
`cl8nk` and `cl9nk` MoDoT verbs (entry, distance, tensor, meet, join, contain,
tier, promotions, transcendence, chain, systems, stats, and cl9nk moat).

Navigator distance is a heuristic. Where a canonical metric exists it decides.
Never hand-derive what a navigator computes."""),

    (None, "The paraconsistent surface", """\
`para_vm` (Belnap FOUR VM, ParaASM, dialetheia), `para_verify` and
`para_verify_enable`. This is the surface on which most imported impossibility
results fail to transfer: they assume a contradiction is fatal, and here it
lands as B and the work continues.

Where two surfaces disagree, that is a B and it is recorded as one, not
resolved by preferring the surface you like."""),
]

MOMONADOS_DOMAIN = [
    (IMSGCT / "mOMonadOS" / "src" / "menu.rs",
     "The menu tables — the documented surface", """\
`command grep -n 'MenuItem {' ~/imsgct/mOMonadOS/src/menu.rs`. Every entry is
`MenuItem { name, cmd, desc, example, submenu }`, and a command that takes
arguments carries a submenu of the same shape naming each form it accepts. This
is what `help` prints at the `⊙>` prompt.

Read this rather than recalling a command list. The surface changes, and a list
memorised in a prompt is wrong the first time a command is added or renamed."""),

    (IMSGCT / "mOMonadOS" / "src" / "repl.rs",
     "The dispatcher — what the kernel actually runs", """\
`command grep -n '\"<word>\" =>' ~/imsgct/mOMonadOS/src/repl.rs`. The match arms
on the command word. Authoritative wherever this and the menu disagree.

Arms exist that no menu entry reaches: those commands work and are undocumented.
Menu entries exist with no arm: those are promises the kernel does not keep. Some
arms carry `#[cfg(feature = ...)]`, which puts a command in the menu and out of
the binary at the same time — check Cargo.toml before calling such a command
missing."""),

    (IMSGCT / "mOMonadOS" / "run_hosted_cmds.sh",
     "Running the kernel", """\
`cd ~/imsgct/mOMonadOS && ./run_hosted_cmds.sh \"<cmd>\" [\"<cmd>\" ...]` boots
QEMU, feeds each command to the `⊙>` prompt in order, and quits. `./run.sh
release` gives an interactive prompt instead.

The QEMU boot dominates the cost of any short command, so batch: several
commands per invocation cost barely more than one. There is no timeout — a
command that takes minutes is computing, not hung.

The runner boots whatever ELF is on disk. After changing source, `make image`
first; a stale binary is the usual reason a change appears to have done
nothing."""),

    (IMSGCT / "mOMonadOS" / "Makefile",
     "The six builds", """\
`make build` debug bare target · `make release` release bare · `make image` the
bootimage the runners boot · `make hosted` host target with the `hosted` feature
· `make ordinals` the ordinal faithfulness guard, which passes as "all 44 values
match Lean canonical" · `./make_proof_vehicle.sh` one emailable tarball carrying
the ELF, a runner and the Lean sources.

.cargo/config.toml pins the bare target, so a plain `cargo build --features
hosted` compiles no_std and fails with thousands of missing-prelude errors that
look like rot and are not. `make hosted` names the host target explicitly."""),

    (IMSGCT / "mOMonadOS" / "check_menu_coverage.py",
     "Coverage between dispatcher and menu", """\
`cd ~/imsgct/mOMonadOS && python3 check_menu_coverage.py`. Reports every REPL
command unreachable from the menu. Run it after wiring a new command; an
unreachable command is one nobody will find."""),
]


CLOSURE_DOMAIN = [
    (IMSGCT / "mOMonadOS" / "src" / "ovm.rs",
     "ovm — operator-valued measures", """\
`cd ~/imsgct/mOMonadOS && ./run_hosted_cmds.sh "ovm"` prints the surface. Then
`ovm <name>` for a full report, and the specific instruments for what it leaves
ambiguous: `frame` (frame operator S in the Pauli basis), `overlap` (Gram matrix
G_ij = Tr(E_i E_j)), `duals` (conical 2-design duals), `spectral`, `measure`,
`born <name> <sx> <sy> <sz>`, and `cycle` for the whole measure→reconstruct
round trip. `ovm belnap` gives the B = XZ fiducial.

Fourteen named operator sets in d=2 — POVMs, NOVMs, NPOVMs and the A-minus, AI-,
S-PC and A-PC variants. The distinctions are real: a NOVM is not a POVM with a
typo, and a set whose positivity or completeness fails is reporting a
measurement, not erroring."""),

    (IMSGCT / "mOMonadOS" / "src" / "ctc.rs",
     "ctc — the manufactured fixed point", """\
`ctc` sweeps every value in every action; `ctc <action> <T|F|N|B>` reads one
pairing; `ctc help` lists the six actions with their fixed points computed live.

Possession is tested first, then the basin, then imposition. Where the action
leaves no value alone it lifts to SETS of values, where a fixed point always
exists, and the price is the width it smeared: 1 is a value held outright, 4 in a
four-valued logic is "it could be anything". Report the price with the
closure."""),

    (IMSGCT / "mOMonadOS" / "src" / "nesting.rs",
     "nesting — the two-step observable", """\
`nesting` runs the reference pairings; `nesting <map> <x> [y]` reads one point;
`nesting help` lists the five maps and their dimensions.

One gap says only whether the point is already the answer. Two gaps say the rest:
q = r₂/r₁ below one arrives, at or above one never does. Attraction is a property
of how the gap CHANGES, so one measurement cannot see it and two can. The nest is
then run and allowed to disagree with the prediction."""),

    (IMSGCT / "mOMonadOS" / "src" / "exotic_one_shots.rs",
     "oneshots — the ten exotic nestings", """\
`oneshots` computes all ten live. Each calls the kernel's own engine rather than
a local copy — the period finder calls the real order-finding engine, the Belnap
one the real negation, the factoring one the same order engine as the first — so
the answers cannot drift from the rest of the kernel."""),

    (IMSGCT / "mOMonadOS" / "src" / "d12_sic.rs",
     "sic and d12 — the fiducial at d=12", """\
`sic` prints the d=12 SIC-POVM identity and its three lattice proofs. `d12`
prints the tower status and its subcommands: tower, magnitudes, orbits,
existence, duallink, z0, ordinals, verify, symmetric, embedding, lean-status.

Standing as the kernel reports it: crystal_forces_d12_sic is a THEOREM with its
axiom retired and the audit clean, all 143 overlaps proved exactly, and the
Belnap d=2^n result unconditional at 0 sorries and 0 axioms. The fiducial is
radical-expressible but its true home is the ring R of dimension 2048 over Q,
which is what makes the d=2048 ascent the same question at the hard end."""),

    (IMSGCT / "mOMonadOS" / "src" / "d2048_sic.rs",
     "d2048 — the moduli tower ascent", """\
`d2048` prints the ascent and its subcommands: tower, c16, c32, ramified, redei,
grammar, pari, next. Alias d2k.

F = Q(sqrt 4190205), m_d = (d+1)(d-3), Hilbert h=64, ray class at (2048)·∞ of
order 2^27. L0 through L6 are verified and end at the Hilbert class field where
h=64 is reached; L7 onward is PENDING, ramified at (2048)·∞ with roughly 2^21
steps to the moduli field.

The climb is grammar-native and explicitly NOT numerical polish — a numerical
descent finds a spurious local minimum here.

The fiducial does NOT depend on L7+. It was extracted exactly on 2026-07-30 by
the 2-part structural S-unit bypass (Stark unit eps = (2047 + sqrt 4190205)/2,
exponents [-1,3,2], 1000 digits), which goes around the ramified layers rather
than through them. L7+ is open as the moduli-field ascent in its own right, not
as a blocker. Pending is not failed, proved is not conjectured, and bypassed is
neither — say which you mean."""),

    (IMSGCT / "ig-docs" / "fixed_point_menagerie" / "CONTEXT.md",
     "The rule these commands serve", """\
`file_read ~/imsgct/ig-docs/fixed_point_menagerie/CONTEXT.md`. The Fixed-Point
Nesting Rule, its three classes and the fourth that was added, the conservative
versus dissipative distinction that decides which classes a domain can populate,
and the census of what the kernel already computes under it.

The manuscript beside it, The_Fixed_Point_Menagerie.md, carries the measured
results with figures generated from a captured kernel run."""),
]


DOMAINS = {
    "math": ("Mathematics", MATH_DOMAIN),
    "editorial": ("Editorial", EDITORIAL_DOMAIN),
    "chembio": ("Chemistry, biology, materials, plasmas", CHEMBIO_DOMAIN),
    "recorder": ("Census, relation, drift", RECORDER_DOMAIN),
    "heterodox": ("Cross-family, Grammar-first", HETERODOX_DOMAIN),
    "momonados": ("The mOMonadOS kernel", MOMONADOS_DOMAIN),
    "closure": ("Measurement and fixed points", CLOSURE_DOMAIN),
}


# ── rendering ─────────────────────────────────────────────────────────

PREAMBLE = """\
The full tool set is available to you, and nothing below is a restriction.
Reach for whatever the task needs. Verify numerical claims by computing them;
never assert arithmetic from memory.
"""


_MODULE_CACHE: dict = {}


def _documented_modules(body: str):
    """Every `python3 -m <module>` named in a curated entry's prose."""
    import re
    return sorted(set(re.findall(r'python3\s+-m\s+([A-Za-z_][A-Za-z0-9_.]*)', body)))


def _module_importable(mod: str) -> bool:
    """True if `python3 -m mod` would resolve. Cached; import machinery only,
    so nothing in the target module actually executes."""
    if mod in _MODULE_CACHE:
        return _MODULE_CACHE[mod]
    ok = False
    try:
        import importlib.util
        parts = mod.split(".")
        spec = importlib.util.find_spec(mod)
        ok = spec is not None
    except Exception:
        ok = False
    _MODULE_CACHE[mod] = ok
    return ok


def render_reference(domain: str) -> tuple[str, list[str]]:
    """The full detail. Written to TOOLS_<domain>.md, read on demand, not inlined."""
    label, entries = DOMAINS[domain]
    shapes = grammar_arg_shapes()
    missing = []

    lines = [PREAMBLE, "## Base tools\n"]
    for name, desc in base_tools():
        lines.append(f"- `{name}` — {desc}")

    lines.append("\n## Grammar tools, called through `imscribe`\n")
    lines.append("`imscribe(tool_name=<name>, args={...})`, or directly at a "
                 "shell with\n`IG_inquiry.py tool <name> [key=value …]`.\n")
    for name in grammar_tools():
        shape = shapes.get(name)
        if shape:
            args = ", ".join(f"{k}={v}" for k, v in shape.items())
            lines.append(f"- `{name}` — {args}")
        else:
            lines.append(f"- `{name}`")

    lines.append(f"\n## {label} tools\n")
    for path, heading, body in entries:
        if path is not None and not path.exists():
            missing.append(f"{domain}: {heading} → {path}")
            lines.append(f"### {heading}  (MISSING: {path})\n")
        else:
            lines.append(f"### {heading}\n")
        # Checking that the repo directory exists says nothing about whether the
        # commands inside the prose can be run. The m3iosis entry documented six
        # modules — explorer, braid_torus, iuft, paranumber, three_body_horn,
        # discovery — that do not exist, and a `cli` subcommand list that had been
        # replaced wholesale. Every documented invocation failed, which is exactly
        # how a tool falls out of use: one call, one error, never again.
        for mod in _documented_modules(body):
            if not _module_importable(mod):
                missing.append(f"{domain}: {heading} → no module {mod}")
                lines.append(f"> NOTE: `python3 -m {mod}` does not resolve.\n")
        lines.append(body.rstrip() + "\n")

    return "\n".join(lines).rstrip() + "\n", missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift and write nothing")
    args = ap.parse_args()

    all_missing = []
    for domain in DOMAINS:
        text, missing = render_reference(domain)
        all_missing += missing
        out = HERE / f"TOOL_MANIFEST_{domain}.md"
        n_base = len(base_tools())
        n_gram = len(grammar_tools())
        n_dom = len(DOMAINS[domain][1])
        ref = HERE / f"TOOLS_{domain}.md"
        inline = render_inline(domain)
        if args.check:
            stale = (not out.exists() or out.read_text() != inline
                     or not ref.exists() or ref.read_text() != text)
            print(f"  {domain:10s} {n_base} base + {n_gram} grammar + "
                  f"{n_dom} domain sections — {'STALE' if stale else 'up to date'}")
        else:
            ref.write_text(text)
            out.write_text(inline)
            print(f"  {domain:10s} {n_base} base + {n_gram} grammar + "
                  f"{n_dom} domain — inline {len(inline)}c, reference {len(text)}c")

    if all_missing:
        print("\nDrift — curated entries whose paths are gone:")
        for m in all_missing:
            print(f"  {m}")
        return 1
    return 0


# ── compact inline manifest ───────────────────────────────────────────

def entry_names(body: str) -> list[str]:
    """Every invocable name in a curated entry: verbs, sub-verbs and flags.

    This used to read the FIRST LINE only and take up to four backticked spans
    from it, while the docstring claimed nothing was invisible. It was not true.
    Not one of MoDoT's ~90 ./ask flags, none of the ~50 structural verbs, and
    none of the imasm sub-verbs appeared in any inline manifest, so a specialist
    could not know they existed without a file_read it had no reason to make.
    That is why the flag list kept being pasted in by hand.

    Names are cheap; it is the prose and the argument shapes that are expensive,
    and those still live one file_read away in TOOLS_<domain>.md. So harvest the
    whole body for names and inline all of them.
    """
    names: list[str] = []

    def add(n: str) -> None:
        n = n.strip().strip(".,;:()")
        if n and n not in names:
            names.append(n)

    # Backticked spans, anywhere in the body. Keep the leading token, and also
    # keep any token that carries a name shape (a dot, a hyphen, or a path), so
    # `python3 ~/…/build_skeleton.py` yields build_skeleton.py and not python3.
    # Short all-lowercase phrases are kept whole, because `la lookup` is the
    # invocation and `la` alone is not.
    for span in re.findall(r"`([^`]+)`", body):
        toks = span.split()
        if not toks:
            continue
        add(toks[0])
        for tok in toks:
            bare = tok.rsplit("/", 1)[-1].strip("<>[]{}()")
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]*[.-][A-Za-z0-9_.-]*", bare):
                add(bare)
        # A short lowercase phrase is the invocation; `la lookup` is the name and
        # `la` alone is not. Placeholders (CODE, <path>, [name]) are not part of it.
        words = [x for x in toks if not re.fullmatch(r"[A-Z0-9_]{2,}|[<\[].*", x)]
        if 2 <= len(words) <= 3 and all(re.fullmatch(r"[a-z][a-z0-9_-]*", x) for x in words):
            add(" ".join(words))
    # Bare file names and hyphenated commands written in prose: IG_catalog.json,
    # vita-probe, cetacean-speaker. Nothing else reaches a name that is neither
    # backticked nor flagged nor dot-separated.
    for tok in re.findall(r"\b[A-Za-z][A-Za-z0-9_-]*\.(?:py|json|sh|md|rs|lean|toml|txt)\b", body):
        add(tok)
    for tok in re.findall(r"\b[a-z][a-z0-9]*(?:-[a-z0-9]+)+\b", body):
        add(tok)
    # Identifiers carrying a digit — cl8nk, cl9nk, ob3ect, m3iosis, imasm16_3.
    # This shape is distinctive to the constellation and near noise-free, and it
    # catches names written bare in prose that no other rule reaches.
    for tok in re.findall(r"\b[a-z][a-z0-9]*[0-9][a-z0-9_]*\b", body):
        add(tok)
    # Long-form flags.
    for flag in re.findall(r"--[A-Za-z0-9][A-Za-z0-9-]*", body):
        add(flag)
    # Parenthetical enumerations: "(PARI/GP: bnfinit, bnrinit, quadhilbert, …)"
    # and "(constants pi tau e phi; functions sqrt cbrt ln …)". These are the
    # sub-surfaces of a single verb and are invocable exactly like the verb is.
    for group in re.findall(r"\(([^()]*:[^()]*)\)", body, re.S):
        for chunk in group.split(":")[1:]:
            for tok in re.findall(r"[a-z][a-z0-9_.]{2,}", chunk):
                add(tok)
    # Verb runs separated by the middle dot, and pipe-alternated aliases within
    # them: `rotat|rotate|shift · arev|hop|door · …`.
    for seg in body.split("·"):
        head = seg.strip().splitlines()[0].strip() if seg.strip() else ""
        # Dotted heads are real names: `rebis.serpentrod · rebis.ligand · …`.
        m = re.match(r"^([a-z][a-z0-9_.]*(?:\|[a-z][a-z0-9_.]*)*)", head)
        if m:
            for alias in m.group(1).split("|"):
                add(alias)
    return names


def render_inline(domain: str) -> str:
    """Every name, plus a pointer to the full reference for the syntax.

    The full detail used to be inlined, which put ~4.9k tokens into every
    winding's prompt — three times the base agent's whole prompt, resent on
    every turn and compounding with the session history. What replaced it was
    supposed to be names-only. It was first-line-only, which is a different and
    much smaller thing, and the difference is the whole reason a specialist
    could not see the tool surface it was standing on.
    """
    label, entries = DOMAINS[domain]
    ref = HERE / f"TOOLS_{domain}.md"
    out = [PREAMBLE, "## Base tools\n",
           ", ".join(f"`{n}`" for n, _ in base_tools()),
           "\n\n## Grammar tools, via `imscribe(tool_name=..., args={...})`\n",
           ", ".join(f"`{n}`" for n in grammar_tools()),
           f"\n\n## {label} tools\n"]
    for _path, heading, body in entries:
        names = entry_names(body)
        if names:
            out.append(f"- **{heading}** — " + ", ".join(f"`{n}`" for n in names))
        else:
            out.append(f"- **{heading}** — {body.strip().splitlines()[0][:80]}")
    out.append(
        f"\n\nFull syntax, every flag and subcommand: `file_read` "
        f"`{ref}`. Read it before using a tool whose invocation you are unsure of.\n"
        f"Order of operations — orient, read the catalog, derive, compute, let "
        f"verification fail you: `file_read` `{HERE / 'PROCEDURE.md'}`.")
    if domain == "math":
        out.append(
            f"BEFORE using any MoDoT verb: `file_read` "
            f"`{HERE / 'MODOT_WALKTHROUGH.md'}`. It says which question each verb "
            f"answers; the flag list alone is not enough to choose correctly.")
    return "\n".join(out).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())


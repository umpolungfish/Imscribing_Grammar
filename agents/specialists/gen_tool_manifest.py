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
    src = IG_INQUIRY.read_text()
    names = re.findall(r'^\s+(?:el)?if name == "([a-z_0-9]+)":', src, re.M)
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

    (IMSGCT / "m3iosis", "m3iosis", """\
`python3 -m m3iosis.cli`: resonance A B · sweep SOURCE [--top N] ·
matrix SYSTEMS… · forge NAME MONOMERS… [--register] · landscape summary |
neighborhood NAME [RADIUS] | bridges A B | clusters [--min-size N] ·
predict NAME TUPLE [--winding N] · spectrum WAVELENGTHS… ·
proof NAME DESCRIPTION [--tuple T] [--save] [--ops OPS…] ·
discover SOURCE [--targets …] [--top N] · braid list | analyze CONFIG |
invariants CONFIG | demo. Most take --json.

`python3 -m m3iosis.braid_torus <cmd> [CONFIG]` — analyze, create, list,
braid, evolve, invariants. Configs: trinity, hyperbolic_triple, pentabraid,
tight_braid, wild_braid, heptaplex.

`python3 -m m3iosis.explorer` — click A B · sweep SOURCE · windings λ… ·
imasm expand NAME · complement NAME · broadcast NAME · calc EXPR ·
report A B · explore (interactive).

`python3 -m m3iosis.iuft` — explore ANCHOR · bridge A B ·
landscape ANCHOR [DEPTH] · wormhole ENTRANCE MEDIATOR… ·
teichmuller NAME TIER · alien NAME · network SEED1 SEED2… ·
synthesize BASE_TIER TARGET_TIER · demo.

`python3 -m m3iosis.paranumber` — number N · range M N · dialetheic L ·
void L · frobenius N · table N · theorems · kernel · demo.

`python3 -m m3iosis.three_body_horn [analyze|sweep|figure_eight|lagrange|all|
demo] --E --J --m1 --m2 --m3 --tmax --steps --n --plot --json --output`.

`python3 -m m3iosis.discovery [SOURCE] [--rounds N] [--output FILE]`, and
`m3iosis.demo`, `visualize_braids`, `visualize_braids_3d`,
`landscape_explorer`, `materials_workbench`, `proof_forge`."""),

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
Python, no flags: fibonacci_anyon_algebra.py, imscription_calculus.py, and
nice_problems/{burnside,connes,erdos_straus,goldbach,threebody}/main.py"""),

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

DOMAINS = {
    "math": ("Mathematics", MATH_DOMAIN),
    "editorial": ("Editorial", EDITORIAL_DOMAIN),
    "chembio": ("Chemistry, biology, materials, plasmas", CHEMBIO_DOMAIN),
}


# ── rendering ─────────────────────────────────────────────────────────

PREAMBLE = """\
The full tool set is available to you, and nothing below is a restriction.
Reach for whatever the task needs. Verify numerical claims by computing them;
never assert arithmetic from memory.
"""


def render(domain: str) -> tuple[str, list[str]]:
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
        lines.append(body.rstrip() + "\n")

    return "\n".join(lines).rstrip() + "\n", missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift and write nothing")
    args = ap.parse_args()

    all_missing = []
    for domain in DOMAINS:
        text, missing = render(domain)
        all_missing += missing
        out = HERE / f"TOOL_MANIFEST_{domain}.md"
        n_base = len(base_tools())
        n_gram = len(grammar_tools())
        n_dom = len(DOMAINS[domain][1])
        if args.check:
            current = out.read_text() if out.exists() else ""
            state = "up to date" if current == text else "STALE"
            print(f"  {domain:10s} {n_base} base + {n_gram} grammar + "
                  f"{n_dom} domain sections — {state}")
        else:
            out.write_text(text)
            print(f"  {domain:10s} {n_base} base + {n_gram} grammar + "
                  f"{n_dom} domain sections → {out.name}")

    if all_missing:
        print("\nDrift — curated entries whose paths are gone:")
        for m in all_missing:
            print(f"  {m}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

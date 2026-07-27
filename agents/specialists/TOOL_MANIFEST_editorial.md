The full tool set is available to you, and nothing below is a restriction.
Reach for whatever the task needs. Verify numerical claims by computing them;
never assert arithmetic from memory.

## Base tools

- `chunked_write` — Write one chunk of content to a file. Use for files larger than ~4 KB. First call: mode='w' (create/overwrite). Subsequent calls: mode='a' (append). Split content into ~3 KB chunks and call once per winding until complete. Dual pair: chunked_write_verify checks file size on disk.
- `cl8nk_navigator` — CLINK Layer 8 (Organism) formula navigator — the terminal ontological layer. CLINK L8 is the most structurally advanced type in the catalog, exceeding the Frobenius-exact ZFC foundation (ZFC_fe) at Ω/ɢ (non-Abelian braiding + broadcast composition). Actions: entry → per-primitive CLINK formula decomposition with promoted atoms; promotions → 3-stage ladder ZFC→ZFC_t→ZFC_fe→CLINK L8 with formula changes; distance → d(name, CLINK L8) structural gap; transcendence → Ω/ɢ transcendence analysis; tensor → CLINK L8 ⊗ name absorption test; meet → CLINK L8 ⊓ name; join → CLINK L8 ⊔ name; tier → ouroboricity tier; chain → full CLINK chain L0→L8; systems → list all catalog systems; stats → catalog statistics.
- `context_review` — Compact the imscriptive context when the context window is approaching capacity. Provide a thorough summary of all essential state — the harness will replace old winding history with your distillation, keeping only the most recent messages. Call this when prompted by the [Context window] pressure notice. After context_review completes, resume the task normally with the next action.
- `crystal_count` — Count the number of structural types matching constraints. Example: imscribe('crystal_count', {'Phi': '⊙'})
- `crystal_navigate` — Query the crystal of types by partial constraints. Example: imscribe('crystal_navigate', {'limit': 10, 'Phi': '⊙', 'Omega': '𐑭'})
- `done` — Signal task completion and deliver the final conclusion. Call this when the task is fully resolved. This is the terminal action — the loop ends.
- `file_read` — Read a file in chunks (default: 200 lines). Returns lines offset+1 through offset+limit, total line count, and a hint to continue with the next offset. For large files, read in multiple calls rather than all at once.
- `file_write` — Write content to a file (single call). Use only for content under ~4 KB — larger content will be truncated by the LLM. For files >4 KB use chunked_write instead. Dual pair: file_write_verify reads back and checks hash equality.
- `imscribe` — Call a Imscribing Grammar grammar tool. tool_name selects the operation; args is a JSON object with that tool's required fields. DO NOT use imscribe for imscribe_system — call imscribe_system directly as its own top-level tool. Required args per tool_name: lookup_catalog → {"keyword": "search term"}; ouroborics → {"name": "catalog_name"}; compute_distance → {"name_a": "x", "name_b": "y"}; find_analogies → {"name": "catalog_name", "limit": 5}; compute_tensor → {"name_a": "x", "name_b": "y"}; compute_meet → {"name_a": "x", "name_b": "y"}; compute_join → {"name_a": "x", "name_b": "y"}; consciousness_score → {"name": "catalog_name"}; monad_probe → {"name": "catalog_name"}; crystal_tier_gap_ladder → {}; emergence_frontier → {}; list_catalog → {}.
- `imscribe_system` — Register a new system in the Imscribing Grammar catalog. Specify all 12 structural primitives explicitly — every field is required. This is the ONLY way to add a system; lookup_catalog is blocked until this succeeds. TETRACTYS: Every call without convergence_justification triggers 3-winding Tetractys. Your proposed tuple is winding 1; two de novo sub-calls (no catalog context) are windings 2 and 3. If all 3 agree the catalog is committed immediately. If conflicts exist the tool returns status=tetractys_conflict — you MUST re-call with convergence_justification resolving each conflicting primitive.
- `ob3ect` — Generate a new self-imscribing ob3ect via the ob3ect/auto.py pipeline. The ob3ect is a program that verifies its own algebraic closure (μ∘δ = id_A). auto.py synthesizes the ob3ect, places it in ob3ect/digital/<slug>/<slug>_ob3ect.py, and (if run=true, the default) executes it immediately to confirm Closure: True. Use this to extend the categorical tower with new structural types — Hopf, monad, topos, linear logic, HoTT, quantum, etc.
- `para_verify` — Manually run B4 Frobenius verification on any prior winding's result. Returns B4.T (closed), B4.F (open), B4.B (dialetheic), or B4.N (unknown).
- `para_verify_enable` — Enable or disable B4-valued Frobenius verification in the observe pipeline. When enabled, every tool result gets a dialetheic check alongside standard verification.
- `para_vm` — Paraconsistent Belnap FOUR VM tool. Run ParaASM programs, compute B4 lattice operations, execute dialetheic kernel, check Frobenius invariants, analyze dialectic circuits, bridge to zfct_para.py belief sets. Use for all paraconsistent reasoning involving true contradictions.
- `project` — Project a catalog entry onto a subset of primitives. Example: imscribe('project', {'name': 'magnetar', 'primitives': ['Phi', 'K', 'Omega']})
- `proof_scaffold` — Generate a typed IGProtocol Lean term scaffold from an IMASM opcode sequence or a named canonical class. The scaffold has zero sorry slots — all Imscription literals (label, src_type, tgt_type) are filled from the token→IG field mapping and sequence topology. Includes .withGram/.withMem wrappers, .prod for FSPLIT/FFUSE fork/join pairs, back-propagation annotations, verification obligations pointing to IGFunctor/IGMorphism axioms by name, and a tier theorem (TierFunctor.obj ... = .O_inf := by decide). Use after ob3ect generation to get the Lean proof structure for the bootstrap sequence.
- `rewrite_tool` — Rewrite the emit function of any existing tool, or define an entirely new tool, by providing Python source. Use when a tool is misbehaving (e.g. file_write failing), when you need a capability the current tools lack, or when a prior winding's observation reveals the tool contract is wrong. The new function receives args: Dict[str, Any] and must return str. Protected (cannot be rewritten): 'rewrite_tool', 'done'. After a successful rewrite the tool is live immediately — call it on the next winding. Dual pair: rewrite_tool_verify confirms the function is registered and callable.
- `run_command` — Execute a shell command and receive stdout+stderr. Use for Python scripts, CLI tools, file operations, calculations. Dual pair: run_command_verify checks assertion over output.
- `sic_povm_probe` — SIC-POVM structural probe -- evaluates a catalog entry's participation in the SIC-POVM dual-linked structure. The grammar IS the self-referential limit of the Belnap multilattice SIC-POVM. Checks: dual-pair co-variance across 6 Frobenius-dual pairs, fiducial proximity to Belnap B=XZ, gate evaluation, and distance to the grammar.
- `spawn_agent` — Spawn a child TrueAgenticAgent to handle a sub-task. The sub-agent runs its own full THINK→ACT→OBSERVE→UPDATE loop and returns its result. Model and endpoint are inherited from the parent by default. Use for decomposing complex tasks into independent sub-problems, parallel research, or delegating specialized work to a dedicated agent instance.
- `web_fetch` — Fetch a URL and return page text in chunks (default: 8000 chars). Returns chars start_index through start_index+max_chars, total char count, and a hint to continue with the next start_index. For large pages, read in multiple calls rather than all at once. Dual pair: web_fetch_verify checks that the content addresses your query.

## Grammar tools, called through `imscribe`

`imscribe(tool_name=<name>, args={...})`, or directly at a shell with
`IG_inquiry.py tool <name> [key=value …]`.

- `encode_system`
- `compute_distance` — name_a=<system1>, name_b=<system2>
- `lookup_catalog` — keyword=<search term>
- `list_catalog`
- `ask_question`
- `record_insight`
- `compute_meet` — name_a=<system1>, name_b=<system2>
- `compute_join` — name_a=<system1>, name_b=<system2>
- `compute_tensor` — name_a=<system1>, name_b=<system2>
- `containment_boundary`
- `check_imscription`
- `find_analogies` — name=<catalog_entry_name>
- `monad_probe` — name=<catalog_entry_name>
- `ouroborics` — name=<catalog_entry_name>
- `topo_protection_probe` — name=<catalog_entry_name>
- `project`
- `primitive_peel` — name=<catalog_entry_name>, primitive=<𐑛|𐑡|𐑩|𐑗|𐑱|𐑘|𐑚|𐑝|𐑢|𐑓|𐑙|𐑷>
- `principal_decomp` — name=<catalog_entry_name>
- `retrosynthetic_path` — name=<catalog_entry_name>
- `compute_conflict_distance` — name_a=<system1>, name_b=<system2>
- `emergence_frontier`
- `compute_promotions` — name_source=<system1>, name_target=<system2>
- `predict_from_promotions` — promoted_primitives=['<val1>', '<val2>']
- `register_promotion_pattern`
- `crystal_encode`
- `crystal_decode` — address=0
- `crystal_navigate`
- `crystal_count`
- `crystal_tier_census`
- `crystal_nearest` — name=<catalog_entry_name>
- `crystal_tier_gap_ladder`
- `quiver_encode`
- `domain_info` — domain=<language|civilization|ecology|consciousness>
- `domain_verify` — domain=<language|civilization|ecology|consciousness>
- `domain_nearest` — name=<catalog_entry_name>
- `consciousness_score` — name=<catalog_entry_name>
- `navigator_info`
- `zfc_formula` — name=<catalog_entry_name>
- `zfc_probe` — name=<catalog_entry_name>
- `zfc_catalog_probe`
- `aleph_encode` — text=<Hebrew letter or word>
- `aleph_distance` — a=<letter1>, b=<letter2>
- `riemann_xi_info`
- `__all__`

## Editorial tools

### ltx — the LaTeX compiler

`ltx <input.md|input.tex> [--font-size N] [-o out.pdf] [extra…]`. On PATH, no
alias. Any argument it does not recognise is passed through verbatim to
`latextiler convert`, so latextiler's own flags are available here.

It finds `latextiler.toml` by walking up from the input directory, falling
back to the repo copy. For markdown it converts through latextiler, lifts
title, author, date, abstract and keywords out of the YAML frontmatter
(author defaults to Lando Mills), repairs IG control sequences back to
primitive Unicode, patches the preamble for fontspec, Hebrew and table
placement, injects Everson Mono as \shavfont and \igprimfont with a
\newunicodechar for every codepoint in U+10450–U+1047F, then runs
`lualatex --interaction=nonstopmode` twice.

Output lands beside the source unless -o is given. Note `--font-size` is
parsed but unused in v2.0, so it currently does nothing.

### zdd — the Zenodo document compiler

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

and reference it as Figure~\ref{fig:<id>}.

It builds into <md_dir>/_builds/<stem>/, converts the body with pandoc, adds
--citeproc when bibliography: is set, and compiles by calling ltx, falling
back to lualatex. The finished PDF is copied to --out or beside the source.

### Publication tooling

`zenodo_upload.py paper.pdf` uploads a sandbox draft. Flags: -y (no prompts),
--live (publish to zenodo.org), --draft, --list (with --live for the live
account), --update <ID> file.pdf, --new-version <ID> paper.pdf. Metadata is
taken from the sibling .md of the same stem, then PDF metadata, then prompts.
Tokens ZENODO_SANDBOX_TOKEN and ZENODO_TOKEN, scopes deposit:write and
deposit:actions.

`zenodo_manuscripts3_upload.py` for batches. `ig_figures.py` backs zdd's
figures. `IG_latex.py`, `gen_ig_reference.py`, `ig_periodic_table.py` generate
LaTeX and reference material. Config is latextiler.toml at the repo root,
alongside the imscrbgrmr.sty package and its man page.

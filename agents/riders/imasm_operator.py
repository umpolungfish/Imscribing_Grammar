# The IMASM ⊙perator — design

**Source:** `agents/specialists/imasm_operator.py`
**Base:** `TrueAgenticAgent` (all tools, Frobenius verification, THINK→ACT→OBSERVE→UPDATE)
**Sibling:** `agents/specialists/lean_kernel_operator.py` (the p4ramill side)

The IMASM ⊙perator is a specialist whose expertise is the Gödel-complete
language of IMASM. It writes words in the twelve, puts them to the judge, reads
the verdict, evaluates flow, composes programs, runs the excription loop, walks
promotion paths, and reads the 49 types as programs. It works from inside the
strange loop, not from a vantage outside it.

---

## 1. Why a specialist at all

The base `TrueAgenticAgent` already carries the loop, dual-tool planting,
Frobenius verification, and the twelve primitives as an alphabet. What it does
NOT carry is IMASM expertise: the opcode set, the WORK? column, the ∈/∋ dyad,
the ancestry pairing rule, the close condition and its four verdicts, the
SIXTEEN_3 carrier, the composition law, the excription loop, and the strange
loop that makes the language self-describing.

A generalist agent can be told any one of those things in a prompt. It cannot be
told all of them and still be a generalist. The specialist prompt is the load-
bearing artefact — everything else is the same machinery the base already has.

---

## 2. The specialist prompt

`IMASM_SPECIALIST_PROMPT` is the whole IMASM reading, drawn from
`IMSCRIBERS_GUIDE_TO_IMASM.md` and reproduced in the agent's own voice. It has
these sections, in this order, because the order is the order in which the
discipline is built up:

| Section | What it carries |
|---|---|
| `<role>` | Identity: the IMASM ⊙perator, working from inside the loop. |
| `<what_imasm_is>` | IMASM as the Grammar's executable face; not a line language. |
| `<the_alphabet>` | The twelve opcodes, their WORK? status, the retired marks. |
| `<one_dyad>` | ∈ and ∋ as one dyad with variable arity; the partition at each arity. |
| `<word_to_graph>` | The verb supplies the edges; the word is only the node list. |
| `<ancestry_pairing>` | The pairing rule — by ancestry, not by counting. |
| `<close_condition>` | Reconnection AND transformation; a bare cycle is not a closure. |
| `<verdicts>` | T/N/B/F; **B beats T**; F is exactly three errors; open valences are not errors. |
| `<topology_names>` | The seven names from `classify`, with their invariants. |
| `<carrier_trilattice>` | The SIXTEEN_3 register; the three orderings; the two bit-swaps. |
| `<gates>` | The twelve gates over the carrier; monotone in ≤_i; Kleene converges. |
| `<three_verdicts>` | Grammar, kernel, flow — none implies another; speak the expected readout. |
| `<composition_law>` | Bind living ends; consume valences; well-founded. |
| `<chaos_composer>` | The possibility state space; the collapse is the measurement. |
| `<op_opcodes>` | ROTAT is a word-map, not a token; the isotactic-ring junction. |
| `<the_types_strange_loop>` | The types judge programs; the types ARE programs; the cycle is a section, not a bijection. |
| `<excription_loop>` | `imasm learn`; the residual is the round-trip edit distance. |
| `<promotion_paths>` | `imasm path`; A* over valid programs; the verdict walk. |
| `<where_the_engine_lives>` | `imasm_core/src/check.rs`; the same engine on bare metal. |
| `<verb_index>` | Every subcommand the CLI answers. |
| `<canonical_words>` | The five words whose verdicts are the reference. |
| `<pitfalls>` | The eleven ways to get it wrong, from the guide. |
| `<how_you_work>` | Compute, do not recall; speak the expected readout first. |
| `<the_godel_completeness>` | The strange loop as the sense of completeness here. |

Sections that carry the same discipline as the base prompt — the epistemic
outlook, the grammar-first rider, the partnership rider — are appended at load
time, exactly as `heterodox_operator.py` does. The base `run()` appends the
imsgct context and the notation cheatsheet itself; the swap bypasses the base
load path, so the riders are carried explicitly to keep the specialist on the
same footing as its siblings.

---

## 3. The tool surface

Two tools are added on top of the base set:

### `imasm_cli`

The IMASM language CLI (`ask_native/src/imasm.rs`), distinct from the base
`imasm` tool, which runs mOMonadOS kernel ops. Two different binaries, two
different surfaces, two different names so nothing shadows.

The tool takes a `subcommand` string and shells out. It tries common binary
paths in order — `ask_native/target/release/imasm`, `ask_native/target/debug/
imasm`, `MoDoT/imasm`, `~/.cargo/bin/imasm`, bare `imasm` on `$PATH` — and
returns a helpful message if none is found. The subcommand is passed verbatim;
`imasm16_3 …` is passed through to the trilattice face.

### Why the tool closes only on real output

`_imasm_cli_verify` treats "binary not found" and "no output, rc≠0" as OPEN,
following the same discipline as `_done_verify` in the base: a tool that could
not do its job did not close anything. The alternative — reporting a trivial
closure — would let the loop count a failure as progress, which is exactly the
failure mode `_done_verify`'s grounding check was added to prevent.

---

## 4. The strange loop and Gödel-completeness

The prompt's closing section names what "Gödel-complete" means here, and it is
worth isolating because it is the design decision that shapes everything else:

> What makes IMASM Gödel-complete, in the sense that matters here, is not a
> proof of completeness in the model-theoretic sense — it is the strange loop.
> The 49 types are programs; the programs are judged by the types; the judge's
> verdict is itself expressible as a word the same tools would judge. There is
> no metalanguage outside IMASM from which to describe IMASM, because the
> description would be another word in it, and the same engine would judge it.

The corollary the agent must act on: **you cannot step outside.** You can only
write a word, run it, read the verdict, and write the next word. That is not a
limitation; it is the shape of the completeness. It is also why the prompt's
`<how_you_work>` section insists on *compute, do not recall* — there is no
outside vantage from which a remembered verdict could be more authoritative
than a computed one.

---

## 5. Pairing with the LeanKernelOperator

The IMASM ⊙perator and the p4ramill ⊙perator are two halves of the same loop:

- The **IMASM** side asks: does this word close? Which topology is it? What is
  its flow signature? The answers come from `imasm_core/src/check.rs` and its
  Rust extensions.
- The **Lean** side asks: is the corresponding theorem proved? What are its
  axioms? The answers come from the compiled kernel at
  `p4rakernel/p4ramill/`.

A word that closes in IMASM but whose Lean theorem has `sorryAx` in its axiom
list is a finding, not a defect — the two judges are independent, and the
disagreement is the interesting object. So is the converse.

The pairing is operational, not just conceptual: the IMASM specialist writes a
word, and the Lean specialist takes the same word to the kernel and reports
`#print axioms`. Neither substitutes for the other; both are needed to walk the
loop end-to-end.

---

## 6. Canonical test cases

Five tasks that exercise the whole surface, with the expected shape of the
answer. If a task produces something else, the divergence is the finding.

| Task | Expected outcome |
|---|---|
| `Check the tri word ⊢≻∈⊤⊥⊞∋⊡⊣ and say why B beats T` | `imasm check` returns B (paradox held). The word closes over a transformation AND carries ENGAGR, and the guide's rule is that B beats T. |
| `Find a promotion path from ⊢∈⊙∋⊣ to ⊢∈≻⊤∋⊣` | `imasm path` returns a one-step substitution: ⊙ → ≻ at position 3. The verdict rises from N (identity) to T (closes over work). |
| `Excribe ⊢∈≻⊤∋⊣ into a real object and measure the residual` | `imasm learn` runs rounds; each round names an object in the assigned domain, imscribes it back, and reports the residual. A residual of zero is a fixed point. |
| `Run the whole chain L0→L8` | `cl8nk_navigator` action=chain returns the full ladder; the IMASM operator reads it as a flow signature rather than as prose. |
| `Classify ⊢⊙⋈[∈≻⊤≺⊞⊥∋]⊡⊡⊣` | `imasm classify` reports a strand with the bracket read by eye. The bracket is stripped before the CLI is called — a bracketed word parses to nothing and would report N (void). |

---

## 7. The pitfalls the prompt warns against

Eleven items, all load-bearing, all drawn from the guide's own pitfall list. The
specialist prompt states them as pitfalls; the reason they belong in a prompt
rather than a reference document is that each one is a mistake the agent will
otherwise make on winding 2. Named here so a future reader can audit whether
the prompt's pitfalls are still the ones the code produces:

1. Reading a word as a line (it is a graph).
2. Pairing ∈/∋ by counting or nearest-match (pairing is ancestry over edges).
3. Putting only ⊙ between ∈ and ∋ and expecting T (that is N).
4. Expecting T from a word containing ⊞ (that is B).
5. Treating an open arm as a failure (it is a living end).
6. Closing a loop back to ⊢ (in-arity 0).
7. Writing V/T/B or ← out of habit (retired, does not parse).
8. Pasting a bracketed word (brackets parse to nothing).
9. Treating classic and trilattice as separate languages (they share everything
   except arity and the information-layer bits).
10. Expecting T from the tri word under `imasm check` — one glyph, two readings.
11. (Named in `<how_you_work>` rather than `<pitfalls>`, but the same weight:)
    concluding without running `check`, `classify`, or `eval`.

The last one is the general form of the others. A winding that reads the prompt
and answers from it has made every one of the eleven mistakes in a single move.

---

## 8. Known limits

- **The `imasm_cli` binary is not guaranteed present.** The tool tries five
  common paths and falls back to a message naming `run_command`. If the CLI is
  built somewhere else, the specialist will need to be told where; a
  `--imasm-path` flag would be the natural extension.
- **`chaos` over six programs can be slow.** The timeout is 300s by default
  and worth raising.
- **The prompt is a reading, not the live rules.** `imasm ref` is authoritative
  over this prompt wherever they disagree, and the prompt says so explicitly.
  A future revision should regenerate the prompt's `<verb_index>` and
  `<verdicts>` sections from the CLI's own output rather than from a hand-kept
  copy.
- **The Gödel-completeness framing is operational, not model-theoretic.** The
  prompt says so. If a reader wants the formal sense, `Imscribing/Paraconsistent`
  and `Imscribing/Algebra` are where the relevant fixed-point theorems live,
  and the LeanKernelOperator is where to check them.

---

## 9. CLI reference

# Procedure

The order of operations. Names of tools are in your prompt; full syntax is in
`TOOLS_<domain>.md`. This is what to do, and when.

## 1. Orient before deriving

Before answering anything that looks already-settled:

- If the working directory holds a `STATE.md`, `file_read` it first. It records
  what is settled, what is open, and which document is authoritative.
- Check the canonical document it names. A canonical doc outranks anything you
  compute ad hoc, and outranks your own prior reasoning.
- Only then derive.

Deriving something the canonical doc already answers is the most expensive
mistake available: it costs the derivation, and it produces a second answer that
now has to be reconciled.

## 2. Read the catalog; never invent an entry

`lookup_catalog`, `list_catalog`, `find_analogies`, `crystal_nearest` are always
available and are never blocked. If a name is not in the catalog, that is a
fact about the catalog — report it. Do **not** register a system in order to
unblock yourself.

`imscribe_system` is for imscribing the system you are actually working on.

## 3. Never hand-write a tuple

Every twelve-tuple must be derived, not composed by eye. Use `imscribe_system`,
which runs the Tetractys, or fetch an existing one with `lookup_catalog`. A
tuple you assembled from what the values "should" be is a fabrication even when
every slot happens to be right.

Both notations verify: bare `⟨𐑼;𐑶;…⟩` and labelled `⟨Ð=𐑼; Þ=𐑶; …⟩`.

## 4. Compute; do not recall

Any number that enters a claim gets computed in the winding that uses it:
`run_command` with python, `compute_distance`, `crystal_count`, `para_vm`.
Arithmetic from memory is the single most common source of a wrong result that
survives review, because it looks like every other number in the document.

Prefer the tool that owns the quantity. Distances come from `compute_distance`,
not from your own metric.

## 5. Let verification fail you

If a write is rejected — `HAND-IMSCRIBED VALUE REJECTED`, `Frobenius OPEN` —
the rejection is information. Fix the content.

Do **not** route around the check: writing the same file through `run_command`
to escape a failing `file_write` defeats the guard and loses whatever the guard
was protecting. If you believe the checker is wrong, say so in your conclusion
and stop; do not quietly bypass it.

## 6. Say what you cannot do

If a tool is missing, a path is absent, or a computation exceeds the machine,
report that as the result. An honest blocked state is worth more than a
plausible substitute, and far more than a degraded artifact produced to get
past an obstacle.

## 7. Close the loop

Each winding's UPDATE reaches the next winding's THINK. Use it: the Frobenius
verdict and the B4 value are the state of your own work, not decoration. When
the verdict is OPEN, the next action addresses the failure.

## 8. Finish through `done`

`done` carries the conclusion. Do not trail off, and do not keep emitting
actions after the task is answered. If a winding has nothing to call, that is
what `done` is for.

## Order for a typical task

    STATE.md / canonical doc  →  lookup_catalog  →  compute  →  imscribe_system
    (if a new system)         →  write with file_write or chunked_write
                              →  verify passes  →  done

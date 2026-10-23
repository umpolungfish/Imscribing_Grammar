# Devolution

This repository was the whole project's universe. Every domain lived here until
the single repository became too totalizing to hold in one head, and the work
was devolved outward into the constellation of sibling repositories. That
devolution is not finished. Functions superseded elsewhere still sit here, and
this file is the standing map of what remains unreached.

## What counts as vestigial

Not "unused". A module launched by path is nobody's import, a CLI command
registered by decorator is nobody's caller, and a prompt loaded by reading its
own source is invisible to any import graph. All three look dead to a census
and are alive. Vestigial means the work it does is done properly somewhere
else, or the thing it points at no longer exists.

## How the census is taken

An AST walk over every Python file outside `.venv`, `__pycache__`, `.git`,
`.stuff` and `node_modules` collects definitions and references, then reports
modules nothing imports and definitions no other file names. The definition
half is mostly noise for the reasons above, so the module half is the working
list and each entry is classified by hand.

Referent searches use `command grep` or `git grep`, never the bare shell
`grep`, which is wrapped to honour `.gitignore` and will hide exactly the
untracked copy that still points at what you are about to remove.

## The rule that keeps it safe

Follow every referent out; do not delete files. A removal is complete when the
CLI group, the agent registry entry, the dispatch branch, the menu item, the
example and the archived test have all come out with the module. Then packages
import, `--help` runs, the live agents import, and the sentry closes. A large
deletion is only a bug when it leaves something pointing at a hole.

## Done

**Chemistry → `red-hot_rebis`.** The cut line was already written in the code:
the `chem` command group's own docstring said those commands use
chemistry-specific quantities and that domain-agnostic algebra is
tensor/meet/join/distance/ouroborics. Out went the molecular, supramolecular,
temporal and hybrid domains (`domains` keeps quantum), retrosynthesis, the
RDKit and SMILES ΔG estimation, the hand-written chemical catalogs, and the
grounding layer. That last one wore the name of a Grammar concept but spoke in
kJ/mol, hydrogen bonds and carboxylic acid dimers. The Grammar's own gate is
`validate_structural`, slot membership plus Axioms A through D, which never
depended on it. What stayed is ΔG where it parameterises ξ_CP rather than a
molecule: the perturbation engine, thermodynamics, ensembles.

**Copies and spent scaffolding.** Two byte-identical stale snapshots of the
live agent, whose every definition was already present in the live file. Three
`append_navigators` scripts that held their output as a string literal and
appended it once, where the target has since been edited in place and is now
canon. One file under `navigators/OLD/` holding a saved tool-harness parse
error under a module name.

## Standing

### False positives, recorded so they are not re-examined

`agents/agents_cli.py`, `agents/mcp_agent_server.py`, `agents/odot_operator.py`,
the four `agents/specialists/*_operator.py` launchers, and the navigators
`cl9nk_navigator`, `perfect_cuboid_navigator`, `quantum_tnn`, `ruleset_dialect`,
`thurston_t_specialist`, `train_zfcfe` are all entry points run by path.
`agents/specialists/QUANTUM_SPECIALIST_PROMPT.py` is read and executed as text
by `specialists/__init__.py`, so no import names it.

### Open

**`imscrbgrmr/assignment.py`.** The primitive assignment engine and the catalog
and decomposition consistency checks. Nothing in the live tree imports it; its
only caller is an archived test under `.stuff`. Either assignment happens
somewhere else now and this is the superseded copy, or this is the canonical
engine and the live path has drifted off it. Which one it is has not been
established.

**`imscrbgrmr/canonical_algebra.py`.** Distance, meet, join, tensor and
Frobenius closure typed on `CrystalAddress`, using the exact ordinals. Nothing
imports it. The algebra that actually runs is the dict-typed version in
`space_search/primitives.py` and `navigators/crystal_navigator.py`, and
`is_frobenius_closed` exists only here. This looks like the typed canon sitting
unused beside the untyped working code, which is a determination about which
one is canon rather than a deletion.

**`navigators/OLD/`.** `zfct_para.py` and the ZFC manipulator live in a
directory named OLD, and no module imports them, but the live agents' help text
offers a bridge to `zfct_para.py` by name and `agents/paraconsistent.py`
describes itself as a port with bridges to it. Either the directory name is
wrong or the help text is.

**The quantum specialist escapes the manifest check.** Three specialist prompts
are inline in `specialists/__init__.py`; the fourth is a separate file loaded by
executing its source. `check_manifests.py` reads the three inline ones and does
not read the quantum one, so the tool manifest guarantee does not cover it.

**`agents/specialists/chembio_operator.py`.** A launcher for the general agent
under a chemistry and biology specialist prompt. It names `red-hot_rebis` and
`p4rakernel` and imports nothing that was removed, so it is a prompt wrapper
rather than chemistry machinery. Whether a chemistry specialist should be
launched from this repository at all is the user's call.

**The catalog copies have drifted.** Canon carries entries that none of the
consumer repositories have. `./sync_catalog.sh --check` names them; running
`./sync_catalog.sh` would propagate. That propagation reaches public site
repositories, and canon's additions are uncommitted, so it is left standing.

**The registry reads a cache, not canon.** The live registry loads from a
catalog under the home directory rather than from `IG_catalog.json`, and the
two have drifted: a handful of shared names carry different tuples, a few dozen
names live only in the home copy, two only in canon. The drifted entries share
a signature, their last three axes sitting at defaults, which is the shape of
the hand-written `.syn` era. In one pair the home copy gives a resolved problem
and its unresolved form the same word and so cannot tell them apart.

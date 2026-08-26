"""
A* proof-path search in operation space.

Two modes:
  catalog  — BFS/A* through existing catalog entries (edges = Hamming ≤ max_hop)
  generative — A* over arbitrary intermediate tuples via named Op applications

Both return a list of ProofStep: (op_name, from_tuple, to_tuple, changed_primitives).
"""
from __future__ import annotations

import heapq
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .ops import OPERATIONS, OPERATIONS_BY_NAME, Op

PRIMS = ["⊢", "⊣", "≻", "≺", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "⊡"]

_CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "IG_catalog.json"


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class ProofStep:
    op_name: str
    from_name: str          # catalog name or "〈intermediate〉"
    from_tuple: dict[str, str]
    to_name: str
    to_tuple: dict[str, str]
    changes: dict[str, tuple[str, str]]  # {prim: (old, new)}

    @property
    def op(self) -> Optional[Op]:
        return OPERATIONS_BY_NAME.get(self.op_name)


def hamming(a: dict[str, str], b: dict[str, str]) -> int:
    return sum(a.get(p) != b.get(p) for p in PRIMS)


def _load_catalog() -> dict[str, dict[str, str]]:
    with open(_CATALOG_PATH) as f:
        raw = json.load(f)
    entries = raw if isinstance(raw, list) else raw.get("entries", [])
    result = {}
    for e in entries:
        name = e.get("name", "")
        tup = {p: e[p] for p in PRIMS if p in e}
        if len(tup) == 12:
            result[name] = tup
    return result


def _tup_to_key(tup: dict[str, str]) -> tuple:
    return tuple(tup[p] for p in PRIMS)


def _key_to_tup(key: tuple) -> dict[str, str]:
    return dict(zip(PRIMS, key))


# ── Best-match operation labelling ─────────────────────────────────────────────

def _label_diff(
    from_tup: dict[str, str],
    to_tup: dict[str, str],
) -> tuple[str, dict[str, tuple[str, str]]]:
    """Return (best_op_name, changes) for a diff between two tuples."""
    changes = {
        p: (from_tup[p], to_tup[p])
        for p in PRIMS
        if from_tup.get(p) != to_tup.get(p)
    }

    best_op = "primitive_transform"
    best_score = -1.0

    for op in OPERATIONS:
        score = 0.0
        for prim, (old_val, new_val) in changes.items():
            if prim in op.transitions:
                from_to = op.transitions[prim]
                if old_val in from_to and from_to[old_val] == new_val:
                    score += 3.0  # exact value-direction match
                else:
                    score += 0.5  # prim in op but wrong values
            # penalise op primitives not touched by this diff
        for prim in op.transitions:
            if prim not in changes:
                score -= 0.3
        if score > best_score:
            best_score = score
            best_op = op.name

    return best_op, changes


# ── Catalog-graph path (BFS through existing entries) ─────────────────────────

def find_catalog_path(
    source_name: str,
    target_name: str,
    max_hop: int = 3,
) -> Optional[list[ProofStep]]:
    """
    BFS through catalog entries. Each step goes from one entry to any
    other entry with Hamming distance ≤ max_hop. Returns shortest path.
    """
    catalog = _load_catalog()
    if source_name not in catalog:
        raise KeyError(f"Source '{source_name}' not in catalog.")
    if target_name not in catalog:
        raise KeyError(f"Target '{target_name}' not in catalog.")

    src_tup = catalog[source_name]
    tgt_tup = catalog[target_name]

    if src_tup == tgt_tup:
        return []

    # BFS: state = current entry name
    queue: list[list[str]] = [[source_name]]
    visited = {source_name}

    while queue:
        path = queue.pop(0)
        current = path[-1]
        cur_tup = catalog[current]

        candidates = [
            (name, tup)
            for name, tup in catalog.items()
            if name not in visited and hamming(cur_tup, tup) <= max_hop
        ]
        # Prefer candidates closer to target
        candidates.sort(key=lambda x: hamming(x[1], tgt_tup))

        for name, tup in candidates:
            new_path = path + [name]
            if name == target_name:
                # Reconstruct ProofSteps
                steps = []
                for i in range(len(new_path) - 1):
                    a, b = new_path[i], new_path[i + 1]
                    ft, tt = catalog[a], catalog[b]
                    op_name, chg = _label_diff(ft, tt)
                    steps.append(ProofStep(
                        op_name=op_name,
                        from_name=a, from_tuple=ft,
                        to_name=b, to_tuple=tt,
                        changes=chg,
                    ))
                return steps
            visited.add(name)
            queue.append(new_path)

    return None  # no path found within max_hop


# ── Generative A* (off-catalog intermediate tuples) ───────────────────────────

def find_path(
    source: dict[str, str] | str,
    target: dict[str, str] | str,
    source_name: str = "",
    target_name: str = "",
    max_steps: int = 12,
    catalog_assist: bool = True,
) -> Optional[list[ProofStep]]:
    """
    A* over operation applications.

    source / target may be dicts (tuples) or catalog entry names (strings).
    If catalog_assist=True, catalog entries close to the current state are
    included as reachable neighbours at each step (zero-cost Hamming-1 moves).
    """
    catalog = _load_catalog() if catalog_assist else {}
    _name_of: dict[tuple, str] = {_tup_to_key(t): n for n, t in catalog.items()}

    def resolve(x: dict | str) -> tuple[dict[str, str], str]:
        if isinstance(x, str):
            if x not in catalog:
                raise KeyError(f"'{x}' not in catalog.")
            return catalog[x], x
        return x, ""

    src_tup, src_name = resolve(source)
    tgt_tup, tgt_name = resolve(target)
    src_name = source_name or src_name
    tgt_name = target_name or tgt_name

    if src_tup == tgt_tup:
        return []

    src_key = _tup_to_key(src_tup)
    tgt_key = _tup_to_key(tgt_tup)

    # A*: (f, g, state_key, path)
    # path = list of (op_name, from_key, to_key, changes)
    start_h = hamming(src_tup, tgt_tup)
    heap = [(start_h, 0, src_key, [])]
    best_g: dict[tuple, int] = {src_key: 0}

    while heap:
        f, g, cur_key, path = heapq.heappop(heap)

        if cur_key == tgt_key:
            # Reconstruct steps
            steps = []
            for op_name, fk, tk, chg in path:
                ft = _key_to_tup(fk)
                tt = _key_to_tup(tk)
                fn = _name_of.get(fk, "〈intermediate〉")
                tn = _name_of.get(tk, "〈intermediate〉")
                # Use actual src/tgt names at endpoints
                if fk == src_key:
                    fn = src_name
                if tk == tgt_key:
                    tn = tgt_name
                steps.append(ProofStep(
                    op_name=op_name,
                    from_name=fn, from_tuple=ft,
                    to_name=tn, to_tuple=tt,
                    changes=chg,
                ))
            return steps

        if g >= max_steps:
            continue
        if best_g.get(cur_key, 9999) < g:
            continue

        cur_tup = _key_to_tup(cur_key)

        # Successors via named operations
        successors: list[tuple[str, tuple, dict]] = []

        for op in OPERATIONS:
            result = op.apply(cur_tup)
            if result is None:
                continue
            new_tup, changes = result
            successors.append((op.name, _tup_to_key(new_tup), changes))

        # Catalog-assisted: also consider nearby catalog entries (Hamming ≤ 1)
        if catalog_assist:
            for name, ctup in catalog.items():
                d = hamming(cur_tup, ctup)
                if 0 < d <= 2:
                    ck = _tup_to_key(ctup)
                    op_name, chg = _label_diff(cur_tup, ctup)
                    successors.append((op_name, ck, chg))

        for op_name, nk, changes in successors:
            ng = g + 1
            if best_g.get(nk, 9999) <= ng:
                continue
            best_g[nk] = ng
            nt = _key_to_tup(nk)
            nh = hamming(nt, tgt_tup)
            nf = ng + nh
            new_path = path + [(op_name, cur_key, nk, changes)]
            heapq.heappush(heap, (nf, ng, nk, new_path))

    return None

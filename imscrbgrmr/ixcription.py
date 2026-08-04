"""The outward form of a catalog entry, and how to take it off.

Every entry in IG_catalog.json carries two things that do not depend on each
other. Twelve glyphs give its address in the lattice, and that address is what
every operation in the framework actually reads: distance, meet, join, tensor,
ouroboricity, the axioms. A name and a description give its outward form, its
ixcription, and no operation reads those at all beyond using the name as a
handle to reach the address.

So the outward form can come off without touching the tuple. Stripping clears
the name and description and leaves the twelve glyphs exactly where they were.
The entry does not leave the catalog and its address does not move; it stays
reachable because what is left names itself, a stripped entry being known by
its own address. Two entries may sit on the same address, and many do, so a
discriminator is appended when one is needed.

What comes off is kept rather than discarded, in a sidecar beside the catalog.
That makes a mistaken strip reversible, and it makes the second use of this
tool possible: strip an address, ixcribe it again, strip it again, and the
sidecar holds both rounds for the same address so they can be set against each
other.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

AXES: Tuple[str, ...] = ("⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻")

# The keys that make up the outward form. Everything else in an entry is either
# an axis or structural, and stays.
IXCRIPTION_KEYS: Tuple[str, ...] = ("name", "description", "justification")

SIDECAR_SUFFIX = ".ixcriptions.json"

_DISCRIMINATOR = re.compile(r"#(\d+)$")


def sidecar_path(catalog_path) -> Path:
    """Where the stripped outward forms for this catalog live."""
    p = Path(catalog_path)
    return p.with_name(p.stem + SIDECAR_SUFFIX)


def address_of(entry: Dict[str, Any]) -> Tuple[str, ...]:
    """The twelve glyphs, in canonical axis order."""
    return tuple(entry.get(ax, "") for ax in AXES)


def address_string(entry: Dict[str, Any]) -> str:
    """The address as one word. This is what a stripped entry is called."""
    return "".join(address_of(entry))


def is_bare(entry: Dict[str, Any]) -> bool:
    """True when this entry carries no outward form beyond its own address."""
    name = entry.get("name", "")
    if not name:
        return True
    stem = _DISCRIMINATOR.sub("", name)
    return stem == address_string(entry) and not entry.get("description")


def bare_handle(entry: Dict[str, Any], taken: Sequence[str]) -> str:
    """A free handle for this entry, its address alone where the address is free.

    Addresses are shared. The catalog puts hundreds of entries on addresses that
    another entry already occupies, and one address carries dozens, so the
    address alone cannot always be the handle. The discriminator is appended
    only when it has to be, and it counts from two, so the first entry stripped
    onto an address reads as the address and nothing else.
    """
    base = address_string(entry)
    taken = set(taken)
    if base not in taken:
        return base
    n = 2
    while f"{base}#{n}" in taken:
        n += 1
    return f"{base}#{n}"


def read_ixcription(entry: Dict[str, Any]) -> Dict[str, str]:
    """The outward form alone, without the address."""
    return {k: entry[k] for k in IXCRIPTION_KEYS if k in entry and entry[k] != ""}


# ── the sidecar ─────────────────────────────────────────────────────────────

def load_sidecar(catalog_path) -> Dict[str, List[Dict[str, Any]]]:
    """Handle → the rounds of ixcription stripped from it, oldest first."""
    p = sidecar_path(catalog_path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_sidecar(sidecar: Dict[str, List[Dict[str, Any]]], catalog_path) -> Path:
    p = sidecar_path(catalog_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sidecar, indent=2, ensure_ascii=False, sort_keys=True),
                 encoding="utf-8")
    return p


# ── the operations ──────────────────────────────────────────────────────────

def strip(entries: List[Dict[str, Any]], names: Sequence[str],
          sidecar: Dict[str, List[Dict[str, Any]]],
          ) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]], List[str]]:
    """Take the outward form off the named entries, in place in the catalog.

    Returns the entries with those handles rewritten, the (old name, handle)
    pairs for what was stripped, and the names that were not found. The list
    keeps its order and its length: nothing is added and nothing is removed.
    """
    wanted = list(dict.fromkeys(names))
    by_name = {e.get("name"): e for e in entries if isinstance(e, dict)}
    missing = [n for n in wanted if n not in by_name]
    found = [n for n in wanted if n in by_name]

    taken = {e.get("name", "") for e in entries if isinstance(e, dict)}
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    stripped: List[Tuple[str, str]] = []

    for name in found:
        entry = by_name[name]
        if is_bare(entry):
            continue
        outward = read_ixcription(entry)
        taken.discard(name)
        handle = bare_handle(entry, taken)
        taken.add(handle)

        for key in IXCRIPTION_KEYS:
            entry.pop(key, None)
        entry["name"] = handle
        entry["description"] = ""
        _reorder(entry)

        round_ = dict(outward)
        round_["stripped"] = stamp
        round_["address"] = address_string(entry)
        sidecar.setdefault(handle, []).append(round_)
        stripped.append((name, handle))

    return entries, stripped, missing


def restore(entries: List[Dict[str, Any]], handles: Sequence[str],
            sidecar: Dict[str, List[Dict[str, Any]]],
            round_index: int = -1,
            ) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]], List[str]]:
    """Put a stripped outward form back on the address it came off.

    Restores the most recent round by default. The round is left in the sidecar
    rather than consumed, because the sidecar is the record of what the address
    has been called and restoring does not unmake that.
    """
    by_name = {e.get("name"): e for e in entries if isinstance(e, dict)}
    unresolved: List[str] = []
    restored: List[Tuple[str, str]] = []

    for handle in dict.fromkeys(handles):
        rounds = sidecar.get(handle) or []
        entry = by_name.get(handle)
        if entry is None or not rounds:
            unresolved.append(handle)
            continue
        try:
            outward = rounds[round_index]
        except IndexError:
            unresolved.append(handle)
            continue
        name = outward.get("name")
        if not name:
            unresolved.append(handle)
            continue

        for key in IXCRIPTION_KEYS:
            entry.pop(key, None)
        entry["name"] = name
        entry["description"] = outward.get("description", "")
        if outward.get("justification"):
            entry["justification"] = outward["justification"]
        _reorder(entry)
        restored.append((handle, name))

    return entries, restored, unresolved


def set_ixcription(entries: List[Dict[str, Any]], handle: str, name: str,
                   description: str = "", justification: str = "",
                   ) -> Optional[Dict[str, Any]]:
    """Write a fresh round of ixcription onto a stripped address.

    This is how the second round gets made. The address is not touched, only
    the words over it, so the comparison afterwards is between two namings of
    one address rather than between two entries.
    """
    for entry in entries:
        if isinstance(entry, dict) and entry.get("name") == handle:
            for key in IXCRIPTION_KEYS:
                entry.pop(key, None)
            entry["name"] = name
            entry["description"] = description
            if justification:
                entry["justification"] = justification
            _reorder(entry)
            return entry
    return None


def rounds(sidecar: Dict[str, List[Dict[str, Any]]], handle: str) -> List[Dict[str, Any]]:
    return list(sidecar.get(handle) or [])


def agreement(sidecar: Dict[str, List[Dict[str, Any]]], handle: str) -> Optional[bool]:
    """Whether every round of ixcription over this address chose the same name.

    None when there has been only one round, since one round agrees with
    nothing. The address is constant across rounds by construction, so what is
    being compared is the naming and not the tuple.
    """
    rs = rounds(sidecar, handle)
    if len(rs) < 2:
        return None
    names = {r.get("name", "") for r in rs}
    return len(names) == 1


def bare_entries(entries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [e for e in entries if isinstance(e, dict) and is_bare(e)]


def _reorder(entry: Dict[str, Any]) -> None:
    """Name, description, then the twelve axes in canonical order.

    A catalog entry is read by eye as often as by code and the axis order is
    the order of the alphabet; a dict that has had keys popped and re-added
    would otherwise write them out in the order they happened to be touched.
    """
    head = {"name": entry.get("name", ""), "description": entry.get("description", "")}
    if entry.get("justification"):
        head["justification"] = entry["justification"]
    axes = {ax: entry.get(ax, "") for ax in AXES}
    rest = {k: v for k, v in entry.items()
            if k not in head and k not in axes and k not in IXCRIPTION_KEYS}
    entry.clear()
    entry.update(head)
    entry.update(axes)
    entry.update(rest)

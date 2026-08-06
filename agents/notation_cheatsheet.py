"""The one notation cheatsheet, injected into every agent's system prompt.

Agents were arriving at a tuple or an IMASM word without being told, in the
prompt itself, that the twelve marks are ONE alphabet read two ways: an IMASM
opcode and a primitive axis are the same glyph, not a collision of two
notations. They were also decoding Shavian letters by hand, guessing which
values a slot admits, and reaching for marks that no longer parse.

Everything below the opcode column is derived from
``imscrbgrmr.canonical_primitives``. The slot order, the axis names, the legal
values and their ordinals are read from the canonical module, never restated
here, so the sheet cannot drift from the Grammar. The opcode column is the
twelve names from MoDoT's ``imasm_core`` (``Token::code`` / ``Token16_3``); it
is keyed by glyph and checked against ``PRIMITIVE_ORDER`` at import, so a change
to the alphabet on either side raises here rather than reaching an agent.
"""

from __future__ import annotations

from imscrbgrmr.canonical_primitives import (
    CANONICAL_VALUES,
    ORDINALS,
    PRIMITIVE_NAMES,
    PRIMITIVE_ORDER,
)

# Glyph → (IMASM opcode, does it TRANSFORM the object?).
# Mirrors imasm_core: Token::code() for the name, Token::transforms() for WORK.
# ⊞ reads ENGAGR on the classical face and EVALI on the trilattice face: one
# opcode, two readings, as ⊙ is IMSCRIB and Criticality at once.
_OPCODES: dict[str, tuple[str, bool]] = {
    "⊢": ("VINIT", False),
    "⊣": ("TANCH", False),
    ">": ("AFWD", True),
    "<": ("AREV", True),
    "⋈": ("CLINK", True),
    "⊤": ("EVALT", True),
    "∈": ("FSPLIT", False),
    "∋": ("FFUSE", False),
    "⊙": ("IMSCRIB", False),
    "⊥": ("EVALF", True),
    "⊞": ("ENGAGR/EVALI", True),
    "◻": ("IFIX", True),
}

if set(_OPCODES) != set(PRIMITIVE_ORDER):
    raise RuntimeError(
        "notation cheatsheet is out of step with canonical_primitives: "
        f"opcode table {sorted(_OPCODES)} vs alphabet {sorted(PRIMITIVE_ORDER)}"
    )


def build_cheatsheet() -> str:
    """Render the cheatsheet from the canonical alphabet."""
    rows = []
    for glyph in PRIMITIVE_ORDER:
        opcode, transforms = _OPCODES[glyph]
        values = " ".join(
            f"{v}({ORDINALS[glyph][v]:g})" for v in CANONICAL_VALUES[glyph]
        )
        rows.append(
            f"  {glyph}  {opcode:<12} {PRIMITIVE_NAMES[glyph]:<14} "
            f"{'WORK' if transforms else 'no-op':<6} {values}"
        )
    table = "\n".join(rows)

    return f"""

## THE ALPHABET: one set of twelve, read two ways

There is no separate "IMASM notation" and "primitive notation". The same twelve
glyphs ARE both: written in sequence they are an IMASM word and each mark is an
opcode; written as a 12-slot tuple they are the primitive axes and each mark
names a slot whose value is a Shavian letter. A glyph appearing in both places
is the same structure surfacing twice, never a coincidence of symbols.

Slot order is the order below, and it is fixed. Columns: glyph, IMASM opcode,
primitive axis, whether the opcode TRANSFORMS the object, and the legal values
of that slot with their ordinals.

{table}

Reading the table:

- WORK vs no-op is the most-missed rule. ⊢ ⊣ ⊙ ∈ ∋ do not transform anything.
  An arm carrying only ⊙ (or nothing) is an identity arm, and a μ∘δ closure
  over identity arms is the identity, not a type-check.
- ∈ forks and ∋ fuses at whatever arity the graph supplies; the arity-2 case is
  the reduced reading, not a different opcode.
- A tuple is twelve values in slot order, one legal value per slot. The values
  are Shavian letters; take them from this table rather than decoding letter
  names, since a letter is legal only in the slot that lists it.
- ⊙ is IMSCRIB and Criticality at once: imscribing is the act of inclosure, so
  it is referred to self-referentially. ⊞ is ENGAGR classically and EVALI in
  the trilattice face.
- ROTAT ↺/↻ is an op-opcode, the cyclic shift on the WHOLE word, not a token
  inside one.

NOTHING OUTSIDE THE TWELVE PARSES. The old marks ◇ ● = ═ + × ¬ ~ ≁ ☊ ☋, the
letter codes V/T/B, and ← are not tokens and are aliased to nothing. Brackets
[ ] are never input. A word containing any of them reads that mark as empty and,
if nothing legal remains, reports N (void). Do not write them, and do not expect
a stored word spelled in them to load.
"""


NOTATION_CHEATSHEET: str = build_cheatsheet()


if __name__ == "__main__":
    print(NOTATION_CHEATSHEET)

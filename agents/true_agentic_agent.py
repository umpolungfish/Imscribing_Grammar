    # write/derive come first: they are the two the rider has always named.
    tup = (args.get("tuple") or "").strip()
    if tup:
        return _imasm_kernel(f'"imasm write {tup}"')
    word = (args.get("word") or "").strip()
    ops = args.get("ops") or ["weight", "banked"]
    derive = args.get("derive")
    if isinstance(ops, str):
        ops = [o.strip() for o in ops.replace(",", " ").split() if o.strip()]

    # Reject non-marks by position rather than dropping them, which would
    # silently shorten the word and answer about a different program.
    cleaned = "".join(_LEGACY_SPELLING.get(c, c)
                      for c in word if not c.isspace())
    if not cleaned:
        return ("imasm: give a word in the twelve marks.\n"
                f"  marks: {' '.join(_MARKS)}\n"
                "  usage: imasm(word='⊢⊙∈⊤⊥∋⊡⊣', ops=['weight','banked','cycle'])")
    for i, c in enumerate(cleaned):
        if c not in _MARKS:
            return (f"imasm: '{c}' at position {i} is not one of the twelve marks.\n"
                    f"  marks: {' '.join(_MARKS)}")

    known = {"weight", "banked", "cycle", "insert", "trans"}
    bad = [o for o in ops if o not in known]
    if bad:
        return f"imasm: unknown op(s) {bad}. Available: {sorted(known)}"

    cmds = " ".join(f'"{o} {cleaned}"' for o in ops)
    if derive:
        # Append derive command rather than replacing ops — both can coexist
        # in a single QEMU boot. Previously, derive=True silently discarded
        # all requested ops (weight, banked, cycle, etc.), forcing agents to
        # either derive OR measure, but never both. The boot dominates;
        # derive is free as an appended command.
        cmds = f'{cmds} "imasm derive {cleaned}"' if cmds else f'"imasm derive {cleaned}"'
    return _imasm_kernel(cmds, args.get("timeout", 900))
"""
Ob3ect Pipeline - Guided Generator
===================================
Author: Lando ⊗ ⊙_ÿ-boundary Operator

Generates a complete ob3ect interactively.
Uses Ob3ectFactory under the hood — one call produces everything.
"""

from core import produce, list_templates, Ob3ectFactory, Opcode


def _prompt(text, default=""):
    if default:
        r = input("  %s [%s]: " % (text, default)).strip()
        return r if r else default
    return input("  %s: " % text).strip()


def guided_generate():
    """Interactive guided ob3ect generation."""
    print("=" * 60)
    print("  Ob3ect Generator — Produce ANY Ob3ect in ANY Domain")
    print("  Author: Lando ⊗ ⊙_Y-boundary Operator")
    print("=" * 60)
    print()
    print("  Built-in domains: %s" % ", ".join(list_templates()))
    print()

    domain = _prompt("Domain type (built-in or press Enter for 'generic')", "generic")
    name = _prompt("Ob3ect name", "My Ob3ect")
    scope = _prompt("Scope (local/mesoscale/maximal)", "local")

    # Get template-specific surface tokens
    print()
    print("  Surface tokens (comma-separated, min 3):")
    tokens_raw = _prompt("  e.g. seeds, soil, water, sunlight, harvest",
                          "input, transform, output")
    tokens = [t.strip() for t in tokens_raw.split(",") if t.strip()]

    boundary = _prompt("Boundary / constraint (TANCH)", "domain boundary")

    # Allow per-opcode overrides
    print()
    print("  Override specific opcodes? (y/n)")
    override_choice = input("  (overrides customize the auto-generated defaults): ").strip().lower()

    overrides = {}
    if override_choice.startswith("y"):
        print("  For each opcode, enter a custom element (or press Enter to keep auto)")
        for oc in Opcode:
            val = _prompt("  %s (%s)" % (oc.value, oc.structural_role), "")
            if val:
                overrides[oc.value] = {"chosen": val}

    # Context
    print()
    print("  Context overrides (key=value pairs, comma-separated)")
    print("  e.g. VINIT=my seed,TANCH=my boundary")
    ctx_raw = _prompt("  (optional)", "")
    context = {}
    if ctx_raw:
        for pair in ctx_raw.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                context[k.strip()] = v.strip()

    # Produce
    print()
    print("  Generating ob3ect...")
    print()

    try:
        factory = Ob3ectFactory()
        art = factory.produce(
            name, domain, scope=scope,
            surface_tokens=tokens if len(tokens) >= 3 else tokens + ["placeholder"] * max(0, 3 - len(tokens)),
            boundary_condition=boundary,
            context=context,
            overrides=overrides,
        )
        print(art.report())
        print()

        export = _prompt("  Export to JSON file? (path or Enter to skip)", "")
        if export:
            art.save(export)
            print("  Exported to %s" % export)

        return art

    except KeyError as e:
        print("  ERROR: %s" % e)
        print("  Available domains: %s" % list(TEMPLATE_REGISTRY.keys()))
        return None
    except Exception as e:
        print("  ERROR: %s" % e)
        return None


if __name__ == "__main__":
    guided_generate()

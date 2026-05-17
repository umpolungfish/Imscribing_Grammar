"""
Ob3ect Pipeline - Examples v2 (Generative)
===========================================
Author: Lando ⊗ ⊙_ÿ-boundary Operator

Demonstrates that the pipeline produces ANY ob3ect in ANY domain.
"""

from core import produce, Ob3ectFactory, list_templates


EXAMPLES = {}


def _register(label, factory_fn, domain_type):
    EXAMPLES[domain_type] = (label, factory_fn)


# --- 1. Physical: Frobenius Optical Table ---
def example_physical():
    return produce(
        "Frobenius Optical Table (Mach-Zehnder)",
        "physical",
        context={
            "VINIT": "Single-photon source (heralded SPDC)",
            "TANCH": "Active vibration isolation table",
        },
        overrides={
            "ISCRIB": {
                "chosen": "reference laser locked to cavity",
                "justification": "Self-calibrating reference element"
            },
            "IFIX": {
                "chosen": "single-photon detection record in RAM",
                "justification": "Irreversible measurement record"
            },
        },
    )


_register("Physical: Mach-Zehnder Interferometer", example_physical, "physical")


# --- 2. Social: Democratic Assembly ---
def example_social():
    return produce(
        "Frobenius Democratic Assembly",
        "social",
        context={
            "VINIT": "Popular mandate / election results",
            "TANCH": "Constitutional court with judicial review power",
        },
        overrides={
            "ENGAGR": {
                "chosen": "bicameral compromise - both houses hold different positions",
                "justification": "Institutionalized contradiction resolved through procedure"
            },
        },
    )


_register("Social: Democratic Assembly", example_social, "social")


# --- 3. Oneiric: Lucid Dream Architecture ---
def example_oneiric():
    return produce(
        "Lucid Dream Architecture",
        "oneiric",
        context={
            "VINIT": "pre-sleep intention: 'I will recognize dream signs'",
        },
        overrides={
            "ISCRIB": {
                "chosen": "reality-check habit (looking at hands, counting fingers)",
                "justification": "Triggers lucidity recognition"
            },
            "IFIX": {
                "chosen": "morning dream journal entry",
                "justification": "Permanent waking-memory record"
            },
        },
    )


_register("Oneiric: Lucid Dream Architecture", example_oneiric, "oneiric")


# --- 4. Computational: Distributed Database ---
def example_computational():
    return produce(
        "Frobenius Distributed Database (Raft consensus)",
        "computational",
        overrides={
            "VINIT": {
                "chosen": "cluster bootstrap with known peer set",
                "justification": "Creates distributed system from single node",
            },
            "FSPLIT": {
                "chosen": "Raft log append (distribute to all peers)",
                "justification": "Splits the entry across the cluster"
            },
        },
    )


_register("Computational: Raft Consensus DB", example_computational, "computational")


# --- 5. Generic: Any Arbitrary Domain ---
def example_generic():
    return produce(
        "Garden Ecosystem",
        "generic",
        surface_tokens=["seeds", "soil", "water", "sunlight", "harvest"],
        boundary_condition="Garden fence / seasonal cycle boundary",
        context={
            "VINIT": "seed planting in spring",
            "AFWD": "growth cycle (germination to maturity)",
            "AREV": "composting dead matter back to soil",
            "FSPLIT": "branching of stems and root systems",
            "FFUSE": "cross-pollination fuses genetic lines",
            "ENGAGR": "companion planting - species with contradictory needs",
            "IFIX": "perennial root system that survives winter",
        },
    )


_register("Generic: Garden Ecosystem", example_generic, "generic")


# --- 6. Custom registered domain ---
def example_custom():
    """Register and produce a completely new domain at runtime."""
    f = Ob3ectFactory()
    f.register("alchemical", {
        "key": "alchemical",
        "label": "Alchemical Operations",
        "tokens": ["prima materia", "fire", "vessel", "product", "formula"],
        "boundary": "Hermetic seal of the alchemical vessel",
        "opcodes": {
            "VINIT":  {"chosen": "prima materia (first matter)", "justification": "The base substance from which all transmutation begins"},
            "TANCH":  {"chosen": "Hermetic vessel seal", "justification": "The closed boundary containing the Great Work"},
            "AFWD":   {"chosen": "calcination and dissolution (solve)", "justification": "Forward dissolution toward dissolution of form"},
            "AREV":   {"chosen": "coagulation and fixation (coagula)", "justification": "Reverse reconstitution toward new form"},
            "CLINK":  {"chosen": "the seven operations chain", "justification": "Each operation feeds into the next in sequence"},
            "ISCRIB": {"chosen": "the philosophers stone as self-reference", "justification": "The stone recognizes and perfects itself"},
            "FSPLIT": {"chosen": "separatio - division of elements", "justification": "Splits the unified matter into constituent principles"},
            "FFUSE":  {"chosen": "conjunctio - sacred marriage of opposites", "justification": "Reunites opposites into the perfected whole"},
            "EVALT":  {"chosen": "rubedo - the red stage (success)", "justification": "The Work is complete and true"},
            "EVALF":  {"chosen": "nigredo failure - putrefaction unchecked", "justification": "The Work collapses into corruption"},
            "ENGAGR": {"chosen": "albedo - the white stage (both purification and potential)", "justification": "Holds the tension between purified matter and unactualized form"},
            "IFIX":   {"chosen": "the sealed formula in the encrypted manuscript", "justification": "The permanent record that cannot be undone"},
        },
        "frobenius": {
            "split": "separatio", "input": "prima materia",
            "outputs": ["volatile spirit", "fixed body"],
            "fuse": "conjunctio", "result": "the stone - matter perfected",
            "verdict": "PASS"
        },
        "registers": {
            "void": "materia prima in chaos - undifferentiated",
            "true": "rubedo - the stone achieved",
            "false": "nigredo failure - putrefaction",
            "both": "albedo - purified but not yet perfected"
        },
        "bootstrap": [
            "recognize the prima materia within",
            "seal the vessel and find the boundary",
            "separate spirit from body (separatio)",
            "dissolve and calcinate (solve)",
            "conjoin the purified opposites (conjunctio)",
            "chain the operations into the complete work",
            "fix the result in the stone (coagula)",
            "verify the stone recognizes itself"
        ],
        "exos": {
            "compiler": "Hermetic theory compels intention into operation",
            "ipc": "sympathetic resonance between macrocosm and microcosm",
            "memory": "the encrypted manuscript tradition",
            "scheduler": "the astrological hours and planetary influences",
            "alfs": "the Table of Emerald - canonical alchemical reference",
            "program": "From prima materia through separatio to conjunctio to rubedo, verify the stone is self-perfecting"
        },
        "entropy": {
            "cost": "heat of the athanor, time of the Great Work",
            "pre": "chaos - undifferentiated materia prima",
            "post": "order - the perfected stone",
            "verdict": "DS=0: the cycle of solve et coagula conserves the essence of matter"
        },
    })
    return f.produce("The Great Work - Rubedo Stage", "alchemical")


EXAMPLES["alchemical"] = ("Custom: Alchemical Great Work", example_custom)


def run_all_examples():
    """Run all registered examples."""
    for key, (label, factory) in EXAMPLES.items():
        print("=" * 60)
        print(label)
        print("=" * 60)
        art = factory()
        valid = art.is_valid_ob3ect
        print("  Valid: %s" % valid)
        print("  Domain: %s (%s)" % (art.domain_charter.domain_name, art.domain_charter.domain_type))
        print()
        for oc in ["VINIT", "FSPLIT", "FFUSE", "ENGAGR", "IFIX"]:
            entry = art.opcode_map.entries.get(oc)
            if entry:
                print("    %s -> %s" % (oc, entry.chosen_element))
        print("  Verdict: %s" % art.split_fuse_report.frobenius_verdict)
        print("  Both state: %s" % art.register_mapping.both_description)
        print("  Delta S: %s" % art.entropy_audit.delta_s_verdict)
        print()

    print("Registered examples: %s" % list(EXAMPLES.keys()))
    print("Available domains: %s" % list_templates())


if __name__ == "__main__":
    run_all_examples()

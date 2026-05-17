#!/usr/bin/env python3
"""Test the generative ob3ect pipeline."""
from core import Ob3ectFactory, list_templates

f = Ob3ectFactory()

# Test 1: all built-in domains produce valid ob3ects
for domain in list_templates():
    art = f.produce("Test_" + domain, domain)
    assert art.is_valid_ob3ect, domain + " failed"
    print("%-15s valid=%s" % (domain, art.is_valid_ob3ect))

print()

# Test 2: context overrides work
art = f.produce("Custom Laser Table", "physical",
    context={"VINIT": "Nd:YAG 1064nm laser", "TANCH": "Active vibration isolation"},
    overrides={"IFIX": {"chosen": "sapphire-mounted reference cavity"}})
assert art.opcode_map.entries["VINIT"].chosen_element == "Nd:YAG 1064nm laser"
assert art.opcode_map.entries["IFIX"].chosen_element == "sapphire-mounted reference cavity"
print("Override test: PASS")
print()

# Test 3: custom domain registration
f.register("culinary", {
    "key": "culinary", "label": "Culinary Arts",
    "tokens": ["ingredients", "heat source", "recipe", "plating", "taste"],
    "boundary": "Kitchen workspace / recipe constraints",
    "opcodes": {
        "VINIT":  {"chosen": "raw ingredients", "justification": "Brings dish from void"},
        "TANCH":  {"chosen": "Kitchen workspace constraints", "justification": "Cooking domain boundary"},
        "AFWD":   {"chosen": "cooking process", "justification": "Forward transformation raw to cooked"},
        "AREV":   {"chosen": "cooling / resting", "justification": "Reverse process stops cooking"},
        "CLINK":  {"chosen": "recipe step sequencing", "justification": "Steps compose"},
        "ISCRIB": {"chosen": "dish identity", "justification": "Signature flavor identifies dish"},
        "FSPLIT": {"chosen": "portioning components", "justification": "Splits into parallel parts"},
        "FFUSE":  {"chosen": "final plating", "justification": "Recombines to unified dish"},
        "EVALT":  {"chosen": "flavor harmony", "justification": "Dish succeeds"},
        "EVALF":  {"chosen": "overcooking", "justification": "Dish fails"},
        "ENGAGR": {"chosen": "balanced contradictory flavors", "justification": "Holds sweet/sour/umami together"},
        "IFIX":   {"chosen": "recipe canonization", "justification": "Permanent dish record"},
    },
    "frobenius": {"split": "portioning", "input": "unified ingredients",
                  "outputs": ["protein", "veg", "starch"],
                  "fuse": "plating", "result": "unified dish", "verdict": "PASS"},
    "registers": {"void": "empty kitchen", "true": "dish ready",
                  "false": "burnt dish", "both": "tasting while cooking"},
    "bootstrap": ["identify dish", "know heat limit", "prep components",
                  "cook elements", "plate together", "sequence course",
                  "record recipe", "verify taste"],
    "exos": {"compiler": "Chef knowledge translates to technique",
             "ipc": "Kitchen verbal orders", "memory": "Recipe cards",
             "scheduler": "Mise-en-place order",
             "alfs": "Master recipe canon",
             "program": "Cook dish, taste matches, close loop"},
    "entropy": {"cost": "heat energy, time, waste", "pre": "prepped",
                "post": "served and reset", "verdict": "DS=0"},
})

art2 = f.produce("Beef Bourguignon", "culinary")
assert art2.is_valid_ob3ect
print("Custom culinary test: PASS")
print()
print(art2.report())
print()
print("ALL TESTS PASSED")

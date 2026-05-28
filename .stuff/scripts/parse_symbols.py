#!/usr/bin/env python3
import re

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Extract all \tex... command names
names = set()
for m in re.finditer(r'\\text([a-zA-Z]+)', raw):
    names.add(m.group(1))

sorted_names = sorted(names)
for n in sorted_names:
    print(n)

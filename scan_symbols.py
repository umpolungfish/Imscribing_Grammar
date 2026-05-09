import re

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Also capture non-\text commands
all_cmds = set()
for m in re.finditer(r'\\(\w+)', raw):
    all_cmds.add(m.group(1))

# Filter for the interesting ones
interesting = [c for c in sorted(all_cmds) if c not in 
    ['textbabygamma', 'textglotstop', 'textrtailn', 'textbarb', 
     'texthalflength', 'textrtailr', 'textbarc', 'texthardsign',
     'textrtails', 'textbard', 'texthooktop', 'textrtailt'] 
    and len(c) > 2 and c.startswith(('t', 'd', 'b', 'g', 'p', 's', 'T', 'D', 'B', 'G', 'P', 'S'))]

for c in interesting[:40]:
    print(f"\\{c}")

print("\n--- Specific searches ---")
# Look for \dh, \thorn, \eth, \openo, \Dh, \Thorn
for cmd in ['dh', 'DH', 'thorn', 'Thorn', 'openo', 'eth', 'esh', 
            'pwedge', 'flap', 'schwa', 'glottal', 'yogh', 'rotOmega',
            'hbar', 'hmlig', 'bar', 'tilde', 'dot', 'star', 'plus']:
    found = [c for c in all_cmds if cmd in c]
    if found:
        print(f"'{cmd}': {found[:5]}")


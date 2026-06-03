#!/usr/bin/env python3
"""Export the full numerical ensemble as CSV for visual inspection."""
import sys, csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from numerical_encode import (
    load_ensemble, filter_valid_entries, encode_ordinal, encode_zero_centered,
    encode_absorbing, CANONICAL_ABSORPTION, PRIM_KEYS, encode_crystal_address,
)
from imscrbgrmr.canonical_primitives import ouroboricity_tier, CrystalAddress

entries = filter_valid_entries(load_ensemble())

# Export both ordinal and zero-centered views
for scheme_name, encoder, extra_cols in [
    ("ordinal", lambda e: encode_ordinal(e), []),
    ("zero_centered", lambda e: encode_zero_centered(e), []),
    ("absorbing", lambda e: encode_absorbing(e, CANONICAL_ABSORPTION, "tensor"), []),
]:
    path = f"/home/mrnob0dy666/imscribing_grammar/ensemble_{scheme_name}.csv"
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['name', 'tier', 'crystal_addr'] + PRIM_KEYS
        writer.writerow(header)
        for e in entries:
            name = e.get('name', '?')
            addr = encode_crystal_address(e)
            tier = ouroboricity_tier(CrystalAddress.from_dict(e))
            vec = encoder(e)
            writer.writerow([name, tier, addr] + [f"{v:.2f}" if isinstance(v, float) else str(v) for v in vec])
    print(f"Wrote {path} ({len(entries)} rows)")

print("Done. Three CSVs exported.")

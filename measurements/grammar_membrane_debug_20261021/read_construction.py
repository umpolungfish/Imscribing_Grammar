"""Read the retained membrane with the existing Grammar instruments."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    out = out / sys.argv[1]
out.mkdir(exist_ok=True)
sys.path.insert(0, str(root / 'imscribing_grammar'))
from imscrbgrmr.lambda_engine import P, G, lam, verify_lambda_axioms

source_file = root / 'p4rakernel/p4ramill/measurements/lean_only_membrane_20261021/resident/locked896.stdout'
saved = source_file.read_text()
fields = tuple(map(int, re.findall(r'^  (\d+)\s*$', saved, re.M)))
assert len(fields) == 7
n, mask, k, source, a, residual, cell = fields
assert n.bit_length() == 896 and source == 4*k*n and a*a == source+residual
gx = G(fields, code=n)
left = lam(P.unit(gx))
right = gx.fmap(P.unit)
reading = {
    'input': 'complete saved seven-field resident return, with N as source context',
    'source_return_file': str(source_file),
    'source_return_sha256': hashlib.sha256(source_file.read_bytes()).hexdigest(),
    'full_resident_equations_hold': True,
    'cli_style_extracted_unit_return': left.extract() == right.extract(),
    'full_context_unit_return': left == right,
    'input_context': str(gx.code),
    'returned_context': str(left.code),
    'required_context': str(right.code),
    'existing_verifier': verify_lambda_axioms([fields]),
    'reference_context_preserving_map': right.code == gx.code,
}
(out / 'context_reading.json').write_text(json.dumps(reading, indent=2)+'\n')
print(json.dumps(reading, indent=2))

catalog_file = root / 'imscribing_grammar/IG_catalog.json'
raw = json.loads(catalog_file.read_text())
entries = raw if isinstance(raw, list) else raw.get('imscriptions', list(raw.values()))
names = ['monad_cantor', 'comonad_goedel', 'distributive_law_lambda',
         'self-reading_fixed_point', 'dual-named_numerals']
canonical = {e['name']: e for e in entries if e.get('name') in names}
assert len(canonical) == len(names)
(out / 'canonical_entries.json').write_text(json.dumps(canonical, ensure_ascii=False, indent=2)+'\n')

commands = [
    ('lambda_verify', ['imscribe', 'lambda', 'verify']),
    ('source_frobenius', ['imscribe', 'lambda', 'frobenius', str(n), '--halves']),
    ('source_comonad', ['imscribe', 'lambda', 'comonad', str(n)]),
]
for navigator in ['cl8nk', 'cl9nk']:
    for name in ['self-reading_fixed_point', 'dual-named_numerals', 'distributive_law_lambda']:
        commands.append((navigator+'_'+name, [sys.executable,
            str(root / f'imscribing_grammar/navigators/{navigator}_navigator.py'), 'entry', name]))
results = []
for name, args in commands:
    run = subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=60)
    (out / (name+'.stdout')).write_text(run.stdout)
    (out / (name+'.stderr')).write_text(run.stderr)
    results.append({'name': name, 'command': args, 'returncode': run.returncode})
    assert run.returncode == 0, (name, run.stderr)
bound = [catalog_file, source_file,
         root / 'imscribing_grammar/imscrbgrmr/lambda_engine.py',
         root / 'imscribing_grammar/imscrbgrmr/lambda_commands.py',
         root / 'imscribing_grammar/scripts/lambda_engine.py',
         root / 'imscribing_grammar/navigators/cl8nk_navigator.py',
         root / 'imscribing_grammar/navigators/cl9nk_navigator.py',
         root / 'p4rakernel/p4ramill/LeanOnlyMembraneMain.lean',
         root / 'p4rakernel/p4ramill/Imscribing/Paraconsistent/LeanOnlyMembrane.lean',
         root / 'p4rakernel/p4ramill/measurements/lean_only_membrane_20261021/GrammarConstructionReadback.lean',
         root / 'ob3ect/digital/self_reading_fixed_point/self_reading_fixed_point_ob3ect.json',
         root / 'ob3ect/digital/dual_named_numerals/dual_named_numerals_ob3ect.json']
(out / 'receipt.json').write_text(json.dumps({'commands': results,
    'bindings': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in bound},
    'scope': 'Grammar debugging of retained source/state; no factor production run'}, indent=2)+'\n')

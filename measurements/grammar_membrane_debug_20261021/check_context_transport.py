"""Full-carrier controls using the retained 896-bit execution return."""
from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / 'imscribing_grammar'))
from imscrbgrmr.lambda_engine import G, P, lam, verify_lambda_axioms

source = root / 'p4rakernel/p4ramill/measurements/lean_only_membrane_20261021/resident/locked896.stdout'
original = tuple(map(int, re.findall(r'^  (\d+)\s*$', source.read_text(), re.M)))
n, mask, k, boundary, a, residual, cell = original
advanced = (n, mask, k, boundary, a+1, residual+2*a+1, cell+1)
assert n.bit_length() == 896
assert advanced[4]**2 == advanced[3]+advanced[5]

gx = G(original, code=n)
family = P([gx, G(advanced, code=n)])
returned = lam(family)
assert returned.code == n and returned.extract() == P([original, advanced])
assert lam(P.unit(gx)) == gx.fmap(P.unit)
assert gx.duplicate().extract() == gx
assert gx.duplicate().fmap(lambda g: g.extract()) == gx
assert gx.duplicate().duplicate() == gx.duplicate().fmap(lambda g: g.duplicate())

# A transformed value must remain paired with its original context.
def step(record):
    source_n, support, multiplier, bound, point, rem, cursor = record
    return (source_n, support, multiplier, bound, point+1, rem+2*point+1, cursor+1)

assert lam(family.fmap(lambda g: g.fmap(step))) == returned.fmap(lambda p: p.fmap(step))

# Distinct contexts stay distinct; a single-source read must reject their union.
mixed = lam(P([gx, G(advanced, code=n+2)]))
assert mixed.code == frozenset([n, n+2]) and mixed.code != n
assert mixed.extract() == returned.extract()
assert lam(P([G(original, code=n), G(original, code=n+2)])).code == mixed.code

# Empty successor and an identity singleton have different values and contexts.
empty = lam(P([]))
assert empty.extract() == P([]) and empty.code == frozenset()
assert empty != lam(P.unit(gx))

# Actual source-carrier transformations obey unit and associativity under P.
f = lambda x: P([x, step(x)])
g = lambda x: P([step(x), step(step(x))])
states = P([original, advanced])
assert P.unit(original).bind(f) == f(original)
assert states.bind(P.unit) == states
assert states.bind(f).bind(g) == states.bind(lambda x: f(x).bind(g))

# Full mixed-law verification includes empty, overlapping and joint contexts.
assert all(verify_lambda_axioms([original, advanced]).values())
nested = P([P.unit(gx), family, P([])])
assert lam(P.flatten(nested)) == lam(nested.fmap(lam)).fmap(P.flatten)
assert lam(family).duplicate() == lam(family.fmap(lambda g: g.duplicate())).fmap(lam)

# Explore the actual carrier's context alternatives with P's own powerset tool.
atoms = [gx, G(advanced, code=n), G(original, code=n+2), G(advanced, code=n+2)]
families = [P(members) for members in P.powerset(atoms)]
for left_family in families:
    assert lam(left_family).extract() == left_family.fmap(lambda x: x.extract())
    assert lam(left_family).duplicate() == lam(left_family.fmap(lambda x: x.duplicate())).fmap(lam)
    assert lam(left_family.fmap(lambda x: x.fmap(step))) == lam(left_family).fmap(lambda x: x.fmap(step))
    for right_family in families:
        enclosing = P([left_family, right_family, P([])])
        assert lam(P.flatten(enclosing)) == lam(enclosing.fmap(lam)).fmap(P.flatten)

result = {'source_bits': n.bit_length(), 'full_source_context_return': True,
          'full_retained_values_return': True, 'transformed_return': True,
          'mixed_context_retention_and_single_source_rejection': True,
          'empty_vs_identity': True, 'actual_carrier_monad_laws': True,
          'powerset_context_alternatives': len(families),
          'mixed_law_axioms': verify_lambda_axioms([original, advanced]),
          'scope': 'Grammar transport debugging; no factor production'}
(Path(__file__).resolve().parent / 'context_controls.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))

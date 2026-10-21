"""Replay saved Grammar graphs through their actual checker and flow engine."""
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / 'IMSCRIBr'))
from tokens import Token
from wiring import WiredGraph, Wire
from native_wiring import inspect_wiring

out = Path(__file__).resolve().parent / 'after'
results = {}
for name in ['self_reading_fixed_point', 'dual_named_numerals']:
    source = root / 'ob3ect/digital' / name / (name+'_ob3ect.json')
    definition = json.loads(source.read_text())
    saved = definition['wiring_check']
    graph = WiredGraph(tuple(Token[node] for node in saved['nodes']),
                       [Wire(*edge) for edge in saved['wires']], name=name)
    measured = inspect_wiring(graph, seed=15)
    assert measured['closure_verified'] and measured['fully_reconnected']
    assert all(measured['pair_recovers_input'])
    # Remove an actual incoming falsity arm, preserving the rest of the source graph.
    missing = next(w for w in graph.wires
                   if graph.tokens[w.dst_node] == Token.FFUSE and w.dst_port == 'F')
    control = WiredGraph(graph.tokens, [w for w in graph.wires if w != missing],
                         name=name+'_missing_fuse_arm')
    rejected = inspect_wiring(control, seed=15)
    assert not rejected['closure_verified'] or not all(rejected['pair_recovers_input'])
    results[name] = {'source_file': str(source), 'native_graph': measured,
                     'missing_arm_control': rejected}
(out / 'native_graphs.json').write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({name: {'closure': row['native_graph']['closure'],
                         'source_return': row['native_graph']['pair_recovers_input'],
                         'missing_arm_control': row['missing_arm_control']['closure']}
                  for name, row in results.items()}, indent=2))

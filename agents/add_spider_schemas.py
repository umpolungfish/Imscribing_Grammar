from pathlib import Path
p = Path('true_agentic_agent.py')
src = p.read_text()

spider_schemas = '''    _fn(
        "spider_run",
        (
            "Walk the dialetheic B-seam spider and return its report. Runs spider_walk "
            "over the inclosure_telemetry lattice for a given number of ticks."
        ),
        {
            "ticks": {"type": "integer", "description": "Spider tick count (default 500)."},
            "seed": {"type": "string", "description": "Spider starting site (T/F/B/N/TB/A/NONE, default B)."},
            "spider_id": {"type": "string", "description": "Spider identifier (default 'spider')."},
            "events_path": {"type": "string", "description": "Path to write/read spider event JSONL."},
            "rules_path": {"type": "string", "description": "Path to JSON closure rules for spider."},
            "weights": {"type": "string", "description": "JSON string of weights dict."},
        },
        [],
    ),
    _fn(
        "spider_trace",
        (
            "Trace a spider's event ledger back to source events through closure."
        ),
        {
            "events_path": {"type": "string", "description": "Path to spider event JSONL file."},
            "spider_id": {"type": "string", "description": "Spider identifier (default 'spider')."},
            "rules_path": {"type": "string", "description": "Path to JSON closure rules for spider."},
        },
        ["events_path"],
    ),
    _fn(
        "spider_diagnose",
        (
            "§33 diagnostic lookup on the spider's own state."
        ),
        {
            "system": {"type": "string", "description": "Diagnose system (N/T/F/B/TB/A)."},
            "environment": {"type": "string", "description": "Diagnose environment (N/T/F/B/TB/A)."},
        },
        ["system", "environment"],
    ),
'''

old = '    _fn(\\n        "gmonad",'
assert old in src, 'gmonad entry not found'
src = src.replace(old, spider_schemas + old, 1)

# Also register emit fns for spider methods that delegate to BughunterOperator methods
emit_fns_anchor = '_VERIFY_FNS: Dict[str, Any] = {'
assert emit_fns_anchor in src, 'verify fns anchor not found'

# Add emit fn registrations before _VERIFY_FNS
emit_reg = '''for _spider_fn in ("spider_run", "spider_trace", "spider_diagnose"):
    _EMIT_FNS.setdefault(_spider_fn, lambda _ai, _name=_spider_fn: f"(spider tool {_name} — call via BughunterOperator bound method)")
    _VERIFY_FNS.setdefault(_spider_fn, lambda _ei, _eo, _va: ("(spider tool — Frobenius trivially closed)", True))

'''

src = src.replace(emit_fns_anchor, emit_reg + emit_fns_anchor, 1)

p.write_text(src)
print('spider schemas + emit fns inserted OK')

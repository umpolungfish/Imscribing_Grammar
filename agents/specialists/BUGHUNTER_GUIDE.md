# Bughunter Operator — Quick Guide

## Location
`/home/mrnob0dy666/imsgct/imscribing_grammar/agents/specialists/bughunter_operator.py`

## Core Usage

```
uv run agents/specialists/bughunter_operator.py "<task>"
uv run agents/specialists/bughunter_operator.py --interactive
uv run agents/specialists/bughunter_operator.py --list-sessions
uv run agents/specialists/bughunter_operator.py --continue "<task>"
uv run agents/specialists/bughunter_operator.py --session-id <id> "<task>"
```

### Session Persistence (memory across turns)
Memory was previously wiped each turn. Now every run auto-saves message history
and trajectory to SQLite (`/home/mrnob0dy666/.imsgct/sessions.db`). Resume with:

- `--continue` — continues the most recent session
- `--session-id <id>` — continues a specific session (list with `--list-sessions`)
- `--no-save` — run without saving to the session DB

Each restored session injects prior messages and windings into the agent context,
so memory persists through turns and windings.

### Required environment
```
export IG_PROVIDER=openrouter
export IG_MODEL=<model-id>
```

## Dialetheic Network Spider (inclosure_telemetry)

The bughunter now embeds the B-seam spider from `inclosure_telemetry`. Three CLI
modes (spider CLI dispatch runs before the agent loop and exits):

```
uv run agents/specialists/bughunter_operator.py --spider-run \
    --spider-ticks 500 --spider-seed B --spider-events /tmp/events.jsonl

uv run agents/specialists/bughunter_operator.py --spider-trace \
    --spider-events /tmp/events.jsonl --spider-id spider

uv run agents/specialists/bughunter_operator.py \
    --spider-diag-system B --spider-diag-env T
```

| Flag | Purpose |
|------|---------|
| `--spider-run` | Walk the B-seam spider; emits JSONL events + summary |
| `--spider-ticks` | Spider tick count (default 500) |
| `--spider-seed` | Starting site: T/F/B/N/TB/A/NONE (default B) |
| `--spider-id` | Spider identifier (default "spider") |
| `--spider-events` | JSONL path for event ledger (read/write) |
| `--spider-rules` | Optional JSON closure rules path |
| `--spider-trace` | Trace spider events back to source |
| `--spider-diag-system` | §33 diagnostic: system state (N/T/F/B/TB/A) |
| `--spider-diag-env` | §33 diagnostic: environment state |

### Python API
```python
from bughunter_operator import BughunterOperator
op = BughunterOperator(model="local")
op.spider_run(ticks=500, seed="B", events_path="/tmp/events.jsonl")
op.spider_trace(events_path="/tmp/events.jsonl", spider_id="spider")
op.spider_diagnose(system="B", environment="T")
```

## What was fixed
- **Memory wipe**: `main()` now calls `load_session(sid)` and passes
  `preloaded_messages`, `preloaded_trajectory`, and `starting_winding_offset`
  to `TrueAgenticAgent`. Prior context is restored on resume.
- **Spider import**: Created `inclosure_telemetry/fde.py` (was missing) so
  `spider.py` can import `ORDER`, `IDX`, `N_`, `F_`, `T_`, `B_`, `N_VALENCES`,
  `Cfg`, `onehot`, `breathing_gate`, `mix_contradictory`.

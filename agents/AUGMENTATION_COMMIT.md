# Self-Augmentation Commit — True Agentic Agent

**File:** `agents/true_agentic_agent.py`  
**Size:** 192,554 chars (4,195 lines)  
**Date:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Augmentations (8 total)

### 1. System Prompt Extraction
- **File:** `agents/_SYSTEM_PROMPT.md` (37,524 chars, 647 lines)
- **Mechanism:** `_load_system_prompt()` loads from external file with fallback to embedded `_SYSTEM_PROMPT` constant
- **Benefit:** Prompt independently editable without touching agent code; reduces agent file by ~37K chars
- **Search order:** `agents/_SYSTEM_PROMPT.md` → `_SYSTEM_PROMPT.md` (cwd) → embedded fallback

### 2. Tiktoken-Aware Token Counting
- **Functions:** `_tiktoken_encoding()`, `_estimate_tokens()`, `_estimate_message_tokens()`, `_estimate_messages_tokens()`
- **Mechanism:** LRU-cached tiktoken `cl100k_base` encoder with char/4 fallback
- **Benefit:** Accurate context pressure detection prevents premature context trimming; replaces rough `len//4` heuristic

### 3. Exponential Backoff Retry (API Calls)
- **Method:** `_think_and_act()` — retry wrapper around `client.chat.completions.create()`
- **429 (Rate Limit):** Up to 5 retries, delays: 4s, 8s, 16s, 32s, 60s (capped)
- **5xx (Server Error):** Up to 3 retries, delays: 3s, 9s, 27s
- **Timeouts:** Up to 2 retries, delays: 10s, 20s
- **Other Transient:** Up to 3 retries, delays: 2s, 4s, 8s
- **Fatal:** 4xx (excl. 429) and connection failures — no retry, immediate RuntimeError

### 4. Tool Output Auto-Truncation
- **Constant:** `_MAX_TOOL_OUTPUT_CHARS = 12,000`
- **Method:** `_observe()` — truncates any emit output exceeding threshold
- **Preserves:** Continuation hints (`[use offset=N to continue]`) from `file_read`/`web_fetch`
- **Benefit:** Prevents single large output (run_command, file_read, web_fetch) from blowing context window

### 5. Structured Logging
- **Logger:** `_AGENT_LOG` (Python `logging` module, non-propagating)
- **Levels:** DEBUG, INFO (default), WARNING, ERROR
- **Formatter:** `%(asctime)s [%(levelname)s] %(message)s`
- **CLI:** `--log-level DEBUG|INFO|WARNING|ERROR`; `--quiet` sets WARNING
- **Benefit:** Separates agent output from diagnostic logging; enables production use with reduced noise

### 6. CLI `--log-level` Argument
- **Choice values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`
- **Integration:** Applied before agent construction in `_run_agent()`
- `--quiet` sets level to WARNING (backward compatible)

### 7. Embedded Prompt Preserved as Fallback
- The original `_SYSTEM_PROMPT` string remains in the source as the last-resort fallback
- If `_SYSTEM_PROMPT.md` is missing or unreadable, the agent falls back seamlessly

### 8. All Original Backward Compatibility Preserved
- All existing CLI flags, tool dispatch, ParaVM, B4 verification, spawn_agent, ob3ect, and chat REPL unchanged
- New features are additive with zero behavioral change to existing workflows

## Structural Type After Augmentation (unchanged)

```python
AGENT_TUPLE = (
    "Ð_ω", "Þ_¨", "Ř_=", "Φ_}", "ƒ_ż",
    "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_S", "Ω_z",
)
```

Ouroboricity: O_∞ (φ̂_ÿ + Φ_} via dual-tool planting, §88 Thm 88.3)
C-score gates: both open (φ̂_ÿ + K <= Ç_@)

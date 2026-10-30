"""
session_db.py — Persistent session storage for TrueAgenticAgent.

Stores full winding trajectories + message histories in SQLite so that
extended collaborative relationships can span multiple sessions.

Usage:
    db = SessionDB()                         # default: /home/mrnob0dy666/.imsgct/sessions.db
    db = SessionDB("/home/mrnob0dy666/my_sessions.db")       # custom path
    session_id = db.save(agent, task)        # save everything after a run
    meta, messages, traj = db.load(sid)      # restore for continuation
    db.list_sessions()                       # browse saved sessions
    db.export_json(sid, "session.json")      # portable export

Schema — three tables:
    sessions   — metadata: id, created_at, model, task, tags, extra
    messages   — imscriptive context: full message history
    windings   — loop cycles: think→act→observe→update records

Author: Lando⊗⊙perator
"""

from __future__ import annotations

import json
import os
import logging as _logging
import time as _time
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _scrub(obj: Any) -> Any:
    """Strip lone surrogates from any string reachable in `obj`.

    Tool output can carry bytes that failed to decode as UTF-8 and were kept as
    surrogate escapes (a stray 0xCF becomes '\\udccf'). Such a string is a valid
    Python str but cannot be encoded to UTF-8, so it kills both the sqlite write
    and the API request with

        UnicodeEncodeError: 'utf-8' codec can't encode character '\\udccf':
        surrogates not allowed

    and the whole run is lost at save time, after the work is done. Round-trip
    through UTF-8 with replacement so the byte is visible as U+FFFD rather than
    fatal.
    """
    if isinstance(obj, str):
        if any(0xD800 <= ord(c) <= 0xDFFF for c in obj):
            return obj.encode("utf-8", "replace").decode("utf-8", "replace")
        return obj
    if isinstance(obj, dict):
        return {_scrub(k): _scrub(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_scrub(v) for v in obj)
    return obj


def _default_db_path() -> str:
    """Default session database: /home/mrnob0dy666/.imsgct/sessions.db"""
    base = os.environ.get("IMSGCT_DB_DIR", os.path.expanduser("/home/mrnob0dy666/.imsgct"))
    os.makedirs(base, exist_ok=True)
    return str(Path(base) / "sessions.db")


class SessionDB:
    """SQLite-backed session persistence for TrueAgenticAgent."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _default_db_path()
        os.makedirs(Path(self.db_path).parent, exist_ok=True)
        self._init_db()

    # ── schema ──────────────────────────────────────────────────────────

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id            TEXT PRIMARY KEY,
                    created_at    TEXT NOT NULL,
                    model         TEXT NOT NULL,
                    task          TEXT NOT NULL,
                    tags          TEXT DEFAULT '[]',
                    result        TEXT DEFAULT '',
                    windings_count INTEGER DEFAULT 0,
                    frobenius_ratio REAL DEFAULT 0.0,
                    structural_type TEXT DEFAULT '{}',
                    extra         TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id      TEXT NOT NULL,
                    seq             INTEGER NOT NULL,
                    role            TEXT NOT NULL,
                    content         TEXT,
                    tool_call_id    TEXT,
                    tool_calls_json TEXT,
                    reasoning_content TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    UNIQUE(session_id, seq)
                );

                CREATE TABLE IF NOT EXISTS logs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id  TEXT,
                    ts          TEXT NOT NULL,
                    epoch       REAL NOT NULL,
                    level       TEXT NOT NULL,
                    logger      TEXT,
                    message     TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS logs_session_idx ON logs(session_id, id);

                CREATE TABLE IF NOT EXISTS windings (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id      TEXT NOT NULL,
                    winding         INTEGER NOT NULL,
                    ts              TEXT NOT NULL,
                    think_reasoning TEXT,
                    action_name     TEXT,
                    action_input    TEXT,
                    tool_output     TEXT,
                    verify_output   TEXT,
                    frobenius_closed INTEGER DEFAULT 0,
                    update_note     TEXT,
                    done            INTEGER DEFAULT 0,
                    conclusion      TEXT DEFAULT '',
                    b4_result       TEXT,
                    dialetheic      INTEGER DEFAULT 0,
                    para_vm_snapshot TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    UNIQUE(session_id, winding)
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_created
                    ON sessions(created_at);
                CREATE INDEX IF NOT EXISTS idx_messages_session
                    ON messages(session_id, seq);
                CREATE INDEX IF NOT EXISTS idx_windings_session
                    ON windings(session_id, winding);
            """)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── save ─────────────────────────────────────────────────────────────

    def save(
        self,
        agent: Any,       # TrueAgenticAgent instance
        task: str,
        tags: Optional[List[str]] = None,
        extra: Optional[Dict] = None,
    ) -> str:
        """Save a full agent run. Returns the session ID."""
        sid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc).isoformat()

        with self._conn() as conn:
            # --- sessions row ---
            st = getattr(agent, 'structural_type', {}) or {}
            frob_ratio = st.get('frobenius_ratio', 0.0)
            result = ""
            if agent.trajectory:
                last = agent.trajectory[-1]
                if last.done:
                    result = last.conclusion

            conn.execute("""
                INSERT INTO sessions (id, created_at, model, task, tags, result,
                                      windings_count, frobenius_ratio, structural_type, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sid, now, getattr(agent, 'model_id', 'unknown'), _scrub(task),
                json.dumps(_scrub(tags or []), ensure_ascii=False),
                _scrub(result),
                len(agent.trajectory),
                frob_ratio,
                json.dumps(_scrub(st), ensure_ascii=False),
                json.dumps(_scrub(extra or {}), ensure_ascii=False),
            ))

            # --- messages rows ---
            messages = getattr(agent, '_messages', []) or []
            for i, msg in enumerate(messages):
                tool_calls_json = None
                if msg.get("tool_calls"):
                    tool_calls_json = json.dumps(_scrub(msg["tool_calls"]), ensure_ascii=False)
                conn.execute("""
                    INSERT OR REPLACE INTO messages
                        (session_id, seq, role, content, tool_call_id,
                         tool_calls_json, reasoning_content)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sid, i,
                    msg.get("role", ""),
                    _scrub(msg.get("content")),
                    msg.get("tool_call_id"),
                    tool_calls_json,
                    _scrub(msg.get("reasoning_content")),
                ))

            # --- windings rows ---
            for cyc in agent.trajectory:
                dr = cyc.dual_result
                conn.execute("""
                    INSERT OR REPLACE INTO windings
                        (session_id, winding, ts, think_reasoning, action_name,
                         action_input, tool_output, verify_output, frobenius_closed,
                         update_note, done, conclusion, b4_result, dialetheic,
                         para_vm_snapshot)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sid, cyc.winding, cyc.ts, _scrub(cyc.think_reasoning), cyc.action_name,
                    json.dumps(_scrub(cyc.action_input), ensure_ascii=False),
                    _scrub(dr.tool_output) if dr else None,
                    dr.verify_output if dr else None,
                    1 if cyc.frobenius_closed else 0,
                    cyc.update_note,
                    1 if cyc.done else 0,
                    _scrub(cyc.conclusion),
                    cyc.b4_result,
                    1 if cyc.dialetheic else 0,
                    json.dumps(cyc.para_vm_snapshot, ensure_ascii=False)
                    if cyc.para_vm_snapshot else None,
                ))

        return sid

    # ── load ──────────────────────────────────────────────────────────────

    def load(self, session_id: str) -> Tuple[Dict, List[Dict], List[Dict]]:
        """Load a session. Returns (metadata, messages, windings)."""
        with self._conn() as conn:
            meta_row = conn.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if meta_row is None:
                raise KeyError(f"Session not found: {session_id}")

            meta = dict(meta_row)
            meta['tags'] = json.loads(meta.get('tags', '[]'))
            meta['structural_type'] = json.loads(meta.get('structural_type', '{}'))
            meta['extra'] = json.loads(meta.get('extra', '{}'))

            msg_rows = conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY seq",
                (session_id,)
            ).fetchall()
            messages = []
            for row in msg_rows:
                m = {
                    "role": row["role"],
                    "content": row["content"],
                }
                if row["tool_call_id"]:
                    m["tool_call_id"] = row["tool_call_id"]
                tcj = row["tool_calls_json"]
                if tcj:
                    m["tool_calls"] = json.loads(tcj)
                rc = row["reasoning_content"]
                if rc:
                    m["reasoning_content"] = rc
                messages.append(m)

            wnd_rows = conn.execute(
                "SELECT * FROM windings WHERE session_id = ? ORDER BY winding",
                (session_id,)
            ).fetchall()
            windings = [dict(r) for r in wnd_rows]
            for w in windings:
                ai = w.get("action_input")
                w["action_input"] = json.loads(ai) if ai else {}
                ps = w.get("para_vm_snapshot")
                w["para_vm_snapshot"] = json.loads(ps) if ps else None

        return meta, messages, windings

    def load_messages_only(self, session_id: str) -> List[Dict]:
        """Load just the message history for quick context injection."""
        _, messages, _ = self.load(session_id)
        return messages

    # ── list / delete ─────────────────────────────────────────────────────

    def list_sessions(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """List recent sessions with metadata."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, created_at, model, task, windings_count, "
                "frobenius_ratio, result FROM sessions "
                "ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        out = []
        for row in rows:
            d = dict(row)
            # Truncate long fields for display
            if d.get("task"):
                d["task_preview"] = d["task"][:200] + ("..." if len(d["task"]) > 200 else "")
            if d.get("result"):
                d["result_preview"] = d["result"][:200] + ("..." if len(d["result"]) > 200 else "")
            out.append(d)
        return out

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if it existed."""
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cur.rowcount > 0

    # ── export / import ───────────────────────────────────────────────────

    def export_json(self, session_id: str, path: str) -> None:
        """Export a session as a portable JSON file."""
        meta, messages, windings = self.load(session_id)
        payload = {
            "format_version": 1,
            "session_id": session_id,
            "metadata": meta,
            "messages": messages,
            "windings": windings,
        }
        with open(path, "w") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    def import_json(self, path: str) -> str:
        """Import a session from a JSON export. Returns the new session ID."""
        with open(path) as fh:
            payload = json.load(fh)

        if payload.get("format_version") != 1:
            raise ValueError("Unsupported session export format")

        sid = payload.get("session_id", datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8])
        meta = payload["metadata"]
        messages = payload["messages"]
        windings = payload["windings"]
        now = datetime.now(timezone.utc).isoformat()

        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions
                    (id, created_at, model, task, tags, result,
                     windings_count, frobenius_ratio, structural_type, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sid, now,
                meta.get("model", "unknown"),
                meta.get("task", ""),
                json.dumps(meta.get("tags", []), ensure_ascii=False),
                meta.get("result", ""),
                meta.get("windings_count", len(windings)),
                meta.get("frobenius_ratio", 0.0),
                json.dumps(meta.get("structural_type", {}), ensure_ascii=False),
                json.dumps(meta.get("extra", {}), ensure_ascii=False),
            ))

            for i, msg in enumerate(messages):
                conn.execute("""
                    INSERT OR REPLACE INTO messages
                        (session_id, seq, role, content, tool_call_id,
                         tool_calls_json, reasoning_content)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sid, i,
                    msg.get("role", ""),
                    msg.get("content"),
                    msg.get("tool_call_id"),
                    json.dumps(msg.get("tool_calls"), ensure_ascii=False) if msg.get("tool_calls") else None,
                    msg.get("reasoning_content"),
                ))

            for w in windings:
                conn.execute("""
                    INSERT OR REPLACE INTO windings
                        (session_id, winding, ts, think_reasoning, action_name,
                         action_input, tool_output, verify_output, frobenius_closed,
                         update_note, done, conclusion, b4_result, dialetheic,
                         para_vm_snapshot)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sid,
                    w.get("winding", 0),
                    w.get("ts", now),
                    w.get("think_reasoning", ""),
                    w.get("action_name", ""),
                    json.dumps(w.get("action_input", {}), ensure_ascii=False),
                    w.get("tool_output", ""),
                    w.get("verify_output", ""),
                    1 if w.get("frobenius_closed") else 0,
                    w.get("update_note", ""),
                    1 if w.get("done") else 0,
                    w.get("conclusion", ""),
                    w.get("b4_result"),
                    1 if w.get("dialetheic") else 0,
                    json.dumps(w.get("para_vm_snapshot"), ensure_ascii=False) if w.get("para_vm_snapshot") else None,
                ))

        return sid


# ── module-level singleton ────────────────────────────────────────────────

_db_instance: Optional[SessionDB] = None


def get_session_db(db_path: Optional[str] = None) -> SessionDB:
    """Get or create the module-level SessionDB singleton."""
    global _db_instance
    if _db_instance is None or (db_path and db_path != _db_instance.db_path):
        _db_instance = SessionDB(db_path)
    return _db_instance


# ── Console-parity log sink ─────────────────────────────────────────────────
class SessionLogHandler(_logging.Handler):
    """Persist every log record to the session database.

    The console formatter drops the timestamp — the winding header already dates
    each step and the wall clock costs nine columns on every line. The record is
    not lost, it moves here, with the epoch alongside the formatted time so the
    stream can be ordered exactly and joined against `windings`.

    `session_id` is set after construction because logging starts before the
    session exists; records emitted before that are stored under NULL and are
    still ordered by `id`.
    """

    _taa_db = True

    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.session_id: Optional[str] = None
        self._db = get_session_db(db_path)

    def emit(self, record: "_logging.LogRecord") -> None:
        try:
            with self._db._conn() as conn:
                conn.execute(
                    "INSERT INTO logs (session_id, ts, epoch, level, logger, message)"
                    " VALUES (?,?,?,?,?,?)",
                    (self.session_id,
                     _time.strftime("%Y-%m-%dT%H:%M:%S", _time.localtime(record.created)),
                     record.created, record.levelname, record.name,
                     record.getMessage()),
                )
        except Exception:
            # a logging sink must never cost the run
            pass


def attach_log_handler(logger: "_logging.Logger", db_path: Optional[str] = None):
    """Attach the session sink once, and hand it back so the id can be set."""
    for h in logger.handlers:
        if getattr(h, "_taa_db", False):
            return h
    h = SessionLogHandler(db_path)
    h.setLevel(_logging.DEBUG)
    logger.addHandler(h)
    return h

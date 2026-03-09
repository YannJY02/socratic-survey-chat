"""
Research-grade session logger (frozen-spec §5.1 schema).

Each participant session is persisted as a self-contained JSON file
so that every experimental observation can be traced back to its raw data.
File naming convention:  {pid}_{ISO-timestamp}.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config


def _ensure_log_dir() -> Path:
    """Create the log directory if it does not yet exist and return its path."""
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    return config.LOG_DIR


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def build_log_entry(session_state) -> dict[str, Any]:
    """Build the complete §5.1 log from session state.

    Parameters
    ----------
    session_state
        The Streamlit session_state object containing all session data.

    Returns
    -------
    dict
        A JSON-serialisable dictionary matching the frozen-spec §5.1 schema.
    """
    return {
        # Session-level fields.
        "pid": session_state.pid,
        "condition": session_state.condition,
        "model": config.MODEL,
        "backend": config.BACKEND,
        "temperature": config.TEMPERATURE,
        "session_start": session_state.session_start,
        "session_end": _utc_now_iso(),
        "withdrawn": getattr(session_state, "withdrawn", False),

        # Phase log.
        "phase_log": list(session_state.phase_log),

        # Scenario data.
        "scenarios": list(session_state.scenarios),

        # CL responses.
        "cl_responses": dict(session_state.cl_responses),

        # Check items.
        "checks": dict(getattr(session_state, "checks", {})),
    }


def save_session(session_state) -> Path:
    """Write the full session log to disk and return the file path.

    The file is written atomically (write-then-rename) to avoid
    partial writes if the process is interrupted.
    """
    log_dir = _ensure_log_dir()
    entry = build_log_entry(session_state)

    ts_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{entry['pid']}_{ts_slug}.json"
    filepath = log_dir / filename

    tmp_path = filepath.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(entry, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp_path.rename(filepath)

    return filepath


# Legacy API — kept for backward compatibility with existing code.
def save_conversation(
    pid: str,
    condition: str,
    messages: list[dict[str, Any]],
    session_start: str,
) -> Path:
    """Write a conversation log to disk (legacy format).

    This function maintains the original API for any code that has not
    yet been migrated to ``save_session()``.
    """
    log_dir = _ensure_log_dir()

    student_turns = sum(1 for m in messages if m.get("role") == "user")
    entry = {
        "pid": pid,
        "condition": condition,
        "model": config.MODEL,
        "backend": config.BACKEND,
        "temperature": config.TEMPERATURE,
        "session_start": session_start,
        "session_end": _utc_now_iso(),
        "student_turns": student_turns,
        "messages": messages,
    }

    ts_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{pid}_{ts_slug}.json"
    filepath = log_dir / filename

    tmp_path = filepath.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(entry, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp_path.rename(filepath)

    return filepath

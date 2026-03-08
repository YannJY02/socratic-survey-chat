"""
Research-grade conversation logger.

Each chat session is persisted as a self-contained JSON file so that
every experimental observation can be traced back to its raw data.
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


def build_log_entry(
    pid: str,
    condition: str,
    messages: list[dict[str, Any]],
    session_start: str,
) -> dict[str, Any]:
    """
    Assemble the full log payload for one session.

    Parameters
    ----------
    pid : str
        Participant identifier passed from Qualtrics.
    condition : str
        Experimental condition label (for A/B testing).
    messages : list[dict]
        The conversation history.  Each dict should contain at least
        ``role``, ``content``, and ``timestamp`` keys.
    session_start : str
        ISO-8601 timestamp of when the session began.

    Returns
    -------
    dict
        A JSON-serialisable dictionary with all session metadata.
    """
    # Count only the student (user) messages as "turns".
    student_turns = sum(1 for m in messages if m.get("role") == "user")

    return {
        "pid": pid,
        "condition": condition,
        "model": config.MODEL,
        "ollama_host": config.OLLAMA_HOST,
        "max_turns": config.MAX_TURNS,
        "session_start": session_start,
        "session_end": _utc_now_iso(),
        "student_turns": student_turns,
        "messages": messages,
    }


def save_conversation(
    pid: str,
    condition: str,
    messages: list[dict[str, Any]],
    session_start: str,
) -> Path:
    """
    Write the conversation log to disk and return the file path.

    The file is written atomically (write-then-rename) to avoid
    partial writes if the process is interrupted.

    Parameters
    ----------
    pid : str
        Participant identifier.
    condition : str
        Experimental condition label.
    messages : list[dict]
        Full conversation history with timestamps.
    session_start : str
        ISO-8601 timestamp of session start.

    Returns
    -------
    Path
        Absolute path to the saved JSON file.
    """
    log_dir = _ensure_log_dir()
    entry = build_log_entry(pid, condition, messages, session_start)

    # Build a filesystem-safe filename from the pid and current timestamp.
    ts_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{pid}_{ts_slug}.json"
    filepath = log_dir / filename

    # Write to a temporary file first, then rename for atomicity.
    tmp_path = filepath.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.rename(filepath)

    return filepath

#!/usr/bin/env python3
"""
export_logs.py — Convert JSON conversation logs to CSV for statistical analysis.

Reads all .json log files from the logs/ directory and produces two CSV files
in data/ that can be imported into R, SPSS, or any other statistics tool:

  - data/conversations.csv  : one row per message
  - data/sessions.csv       : one row per session (summary)

Usage:
    python scripts/export_logs.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

# Resolve project paths relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"


def load_log_files():
    """Read all JSON log files from the logs/ directory and return them as a list of dicts."""
    log_files = sorted(LOGS_DIR.glob("*.json"))

    if not log_files:
        print(f"No JSON log files found in {LOGS_DIR}")
        sys.exit(0)

    sessions = []
    for path in log_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["_source_file"] = path.name
            sessions.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARNING: Skipping {path.name} — {e}")

    return sessions


def build_conversations_df(sessions):
    """Flatten session data into a per-message DataFrame."""
    rows = []

    for session in sessions:
        participant_id = session.get("participant_id", "unknown")
        condition = session.get("condition", "unknown")
        model_name = session.get("model_name", "unknown")
        session_start = session.get("session_start", "")
        session_end = session.get("session_end", "")
        messages = session.get("messages", [])
        total_turns = len(messages)

        for turn_number, msg in enumerate(messages, start=1):
            rows.append({
                "participant_id": participant_id,
                "condition": condition,
                "message_role": msg.get("role", ""),
                "message_content": msg.get("content", ""),
                "message_timestamp": msg.get("timestamp", ""),
                "turn_number": turn_number,
                "session_start": session_start,
                "session_end": session_end,
                "model_name": model_name,
                "total_turns": total_turns,
            })

    return pd.DataFrame(rows)


def build_sessions_df(sessions):
    """Build a per-session summary DataFrame."""
    rows = []

    for session in sessions:
        participant_id = session.get("participant_id", "unknown")
        condition = session.get("condition", "unknown")
        model_name = session.get("model_name", "unknown")
        session_start = session.get("session_start", "")
        session_end = session.get("session_end", "")
        messages = session.get("messages", [])
        total_turns = len(messages)

        # Calculate duration if timestamps are available
        duration_seconds = None
        if session_start and session_end:
            try:
                from datetime import datetime
                # Parse ISO format timestamps
                start = datetime.fromisoformat(session_start)
                end = datetime.fromisoformat(session_end)
                duration_seconds = (end - start).total_seconds()
            except (ValueError, TypeError):
                duration_seconds = None

        rows.append({
            "participant_id": participant_id,
            "condition": condition,
            "total_turns": total_turns,
            "duration_seconds": duration_seconds,
            "session_start": session_start,
            "session_end": session_end,
            "model_name": model_name,
        })

    return pd.DataFrame(rows)


def main():
    print("=== Exporting conversation logs to CSV ===\n")

    # Ensure output directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load all session logs
    sessions = load_log_files()
    print(f"Loaded {len(sessions)} session(s) from {LOGS_DIR}\n")

    # Build and export conversations (per-message) CSV
    conversations_df = build_conversations_df(sessions)
    conversations_path = DATA_DIR / "conversations.csv"
    conversations_df.to_csv(conversations_path, index=False)
    print(f"Wrote {len(conversations_df)} message rows to {conversations_path}")

    # Build and export sessions (per-session summary) CSV
    sessions_df = build_sessions_df(sessions)
    sessions_path = DATA_DIR / "sessions.csv"
    sessions_df.to_csv(sessions_path, index=False)
    print(f"Wrote {len(sessions_df)} session rows to {sessions_path}")

    # Print summary statistics
    print("\n--- Summary Statistics ---")
    print(f"Total sessions:  {len(sessions_df)}")
    print(f"Total messages:  {len(conversations_df)}")

    if not sessions_df.empty:
        print(f"Conditions:      {sessions_df['condition'].nunique()} "
              f"({', '.join(sessions_df['condition'].unique())})")
        print(f"Avg turns/session: {sessions_df['total_turns'].mean():.1f}")

        if sessions_df["duration_seconds"].notna().sum() > 0:
            avg_dur = sessions_df["duration_seconds"].mean()
            print(f"Avg duration:    {avg_dur:.0f}s ({avg_dur/60:.1f} min)")

    print("\nDone. Files ready for import into R / SPSS.")


if __name__ == "__main__":
    main()

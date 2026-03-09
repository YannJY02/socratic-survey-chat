"""
Phase definitions and state-machine logic for the Socratic Survey Chat.

The experiment follows a condition-dependent sequence of phases.
This module defines the Phase enum, maps conditions to phase sequences,
and provides helpers to query and advance the current phase.
"""

from datetime import datetime, timezone
from enum import Enum


class Phase(Enum):
    WELCOME = "welcome"
    INSTRUCTION = "instruction"
    CL_POST_INSTRUCTION = "cl_post_instruction"
    AI_CHAT = "ai_chat"
    CL_POST_CHAT = "cl_post_chat"
    REDIRECT = "redirect"


# Condition -> ordered list of phases.
CONDITION_SEQUENCES: dict[str, list[Phase]] = {
    "I_PS": [
        Phase.WELCOME,
        Phase.INSTRUCTION,
        Phase.CL_POST_INSTRUCTION,
        Phase.AI_CHAT,
        Phase.CL_POST_CHAT,
        Phase.REDIRECT,
    ],
    "PS_I": [
        Phase.WELCOME,
        Phase.AI_CHAT,
        Phase.CL_POST_CHAT,
        Phase.INSTRUCTION,
        Phase.CL_POST_INSTRUCTION,
        Phase.REDIRECT,
    ],
}

DEFAULT_CONDITION = "I_PS"


def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def get_phase_sequence(condition: str) -> list[Phase]:
    """Return the phase sequence for the given condition.

    Falls back to the default condition (I_PS) for unknown values.
    """
    return CONDITION_SEQUENCES.get(condition, CONDITION_SEQUENCES[DEFAULT_CONDITION])


def current_phase(session_state) -> Phase:
    """Return the current phase based on session_state.current_phase_index."""
    sequence = get_phase_sequence(session_state.condition)
    idx = session_state.current_phase_index
    if idx >= len(sequence):
        return sequence[-1]
    return sequence[idx]


def advance_phase(session_state) -> None:
    """Record phase_end for the current phase, increment index, record phase_start for next."""
    now = _utc_now_iso()

    # Close the current phase entry.
    if session_state.phase_log:
        session_state.phase_log[-1]["phase_end"] = now

    session_state.current_phase_index += 1

    # Open the next phase entry (if within bounds).
    sequence = get_phase_sequence(session_state.condition)
    idx = session_state.current_phase_index
    if idx < len(sequence):
        session_state.phase_log.append({
            "phase_name": sequence[idx].value,
            "phase_order": idx + 1,
            "phase_start": now,
            "phase_end": None,
        })


def go_back_phase(session_state) -> None:
    """Move back to the previous phase, recording timestamps in the phase log."""
    if session_state.current_phase_index <= 0:
        return

    now = _utc_now_iso()

    # Close the current phase entry.
    if session_state.phase_log:
        session_state.phase_log[-1]["phase_end"] = now

    session_state.current_phase_index -= 1

    # Open a new entry for the revisited phase.
    sequence = get_phase_sequence(session_state.condition)
    idx = session_state.current_phase_index
    session_state.phase_log.append({
        "phase_name": sequence[idx].value,
        "phase_order": idx + 1,
        "phase_start": now,
        "phase_end": None,
    })


def start_first_phase(session_state) -> None:
    """Record the first phase entry in phase_log."""
    sequence = get_phase_sequence(session_state.condition)
    session_state.phase_log.append({
        "phase_name": sequence[0].value,
        "phase_order": 1,
        "phase_start": _utc_now_iso(),
        "phase_end": None,
    })

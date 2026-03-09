"""
Central configuration for the Socratic Tutor application.

All tuneable parameters are collected here so that experimental conditions
are transparent and reproducible.  Change values in this file (or override
them via environment variables) rather than scattering magic strings
throughout the codebase.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Root of the project (the directory that contains this file).
BASE_DIR: Path = Path(__file__).resolve().parent

# Directory where conversation logs are stored (one JSON file per session).
LOG_DIR: Path = BASE_DIR / "logs"

# System-prompt file used by the tutor (domain-specific, per frozen-spec D-5).
SYSTEM_PROMPT_PATH: Path = BASE_DIR / "prompts" / "socratic_domain.txt"

# ---------------------------------------------------------------------------
# Developer mode
# ---------------------------------------------------------------------------
# When True, a sidebar panel allows switching backend / model at runtime.
DEV_MODE: bool = os.environ.get("DEV_MODE", "false").lower() == "true"

# ---------------------------------------------------------------------------
# LLM backend settings
# ---------------------------------------------------------------------------
# Backend selector: "ollama" (local dev) or "openai" (production).
BACKEND: str = os.environ.get("BACKEND", "ollama")

# Model identifier — meaning depends on the backend.
MODEL: str = os.environ.get("MODEL", "eurecom-ds/phi-3-mini-4k-socratic")

# Ollama API base URL (used only when BACKEND == "ollama").
OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Generation temperature (frozen-spec: 0.3).
TEMPERATURE: float = float(os.environ.get("TEMPERATURE", "0.3"))

# ---------------------------------------------------------------------------
# Experiment settings
# ---------------------------------------------------------------------------
# Maximum student turns *per scenario* during the AI chat phase.
TURNS_PER_SCENARIO: int = 7

# Minimum student turns before the "move on" button appears.
MIN_TURNS_PER_SCENARIO: int = 2

# Legacy — kept for backward-compat; not used by the new phase router.
MAX_TURNS: int = 20

# ---------------------------------------------------------------------------
# Scenario metadata
# ---------------------------------------------------------------------------
SCENARIO_IDS: tuple[str, ...] = ("S1", "S2", "S3")

# ---------------------------------------------------------------------------
# Qualtrics integration
# ---------------------------------------------------------------------------
# Post-session survey URL.  {pid} and {condition} are replaced at runtime.
# Uses single-survey two-wave architecture: wave=post triggers post-survey blocks.
QUALTRICS_POST_SURVEY_URL: str = os.environ.get(
    "QUALTRICS_POST_SURVEY_URL",
    "https://fra1.qualtrics.com/jfe/form/SV_37uMu9WF3PngHFI"
    "?pid={pid}&wave=post&condition={condition}",
)

# Debriefing URL for withdrawn participants.
QUALTRICS_DEBRIEFING_URL: str = os.environ.get(
    "QUALTRICS_DEBRIEFING_URL",
    "https://your-institution.qualtrics.com/jfe/form/YOUR_DEBRIEF_ID?pid={pid}",
)

# ---------------------------------------------------------------------------
# UI copy
# ---------------------------------------------------------------------------
APP_TITLE: str = "Socratic Tutor"
APP_DESCRIPTION: str = (
    "Welcome! I am a Socratic tutor — I will help you learn by asking "
    "guiding questions rather than giving you the answers directly. "
    "Take your time and think through each question carefully."
)

INFORMED_CONSENT_NOTICE: str = (
    "By using this application you confirm that you have read and agreed "
    "to the informed-consent form provided earlier.  Your conversation "
    "will be recorded anonymously for research purposes."
)

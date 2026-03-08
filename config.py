"""
Central configuration for the Socratic Tutor application.

All tuneable parameters are collected here so that experimental conditions
are transparent and reproducible.  Change values in this file (or override
them via environment variables) rather than scattering magic strings
throughout the codebase.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Root of the project (the directory that contains this file).
BASE_DIR: Path = Path(__file__).resolve().parent

# Directory where conversation logs are stored (one JSON file per session).
LOG_DIR: Path = BASE_DIR / "logs"

# System-prompt file used by the tutor.
SYSTEM_PROMPT_PATH: Path = BASE_DIR / "prompts" / "socratic_tutor.txt"

# ---------------------------------------------------------------------------
# Model / Ollama settings
# ---------------------------------------------------------------------------
# Hugging-Face-style model identifier served by Ollama.
MODEL: str = "eurecom-ds/phi-3-mini-4k-socratic"

# Ollama API base URL.
OLLAMA_HOST: str = "http://localhost:11434"

# ---------------------------------------------------------------------------
# Experiment settings
# ---------------------------------------------------------------------------
# Maximum number of *student* turns before the conversation is capped.
# Keeps session length consistent across participants.
MAX_TURNS: int = 20

# ---------------------------------------------------------------------------
# Qualtrics integration
# ---------------------------------------------------------------------------
# Post-session survey URL.  The placeholder {pid} is replaced at runtime
# with the participant's ID so Qualtrics can link survey responses back to
# the chat log.
QUALTRICS_POST_SURVEY_URL: str = (
    "https://your-institution.qualtrics.com/jfe/form/YOUR_SURVEY_ID?pid={pid}"
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

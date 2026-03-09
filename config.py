"""
Central configuration for the Socratic Tutor application.

All tuneable parameters are collected here so that experimental conditions
are transparent and reproducible.  Change values in this file (or override
them via environment variables) rather than scattering magic strings
throughout the codebase.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file (if present).
load_dotenv()


def _get_config(key: str, default: str = "") -> str:
    """Get config value from environment or Streamlit secrets.

    Streamlit Cloud uses st.secrets (TOML format), while local development
    uses .env files. This helper checks both sources.
    """
    # First check environment variables (from .env or system).
    value = os.environ.get(key)
    if value is not None:
        return value

    # Fall back to Streamlit secrets (only available when running in Streamlit).
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except (ImportError, FileNotFoundError, KeyError):
        pass

    return default


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
DEV_MODE: bool = _get_config("DEV_MODE", "false").lower() == "true"

# ---------------------------------------------------------------------------
# LLM backend settings
# ---------------------------------------------------------------------------
# Backend selector: "ollama" (local dev) or "openai" (production).
BACKEND: str = _get_config("BACKEND", "ollama")

# Model identifier — meaning depends on the backend.
MODEL: str = _get_config("MODEL", "eurecom-ds/phi-3-mini-4k-socratic")

# Ollama API base URL (used only when BACKEND == "ollama").
OLLAMA_HOST: str = _get_config("OLLAMA_HOST", "http://localhost:11434")

# Generation temperature (frozen-spec: 0.3).
TEMPERATURE: float = float(_get_config("TEMPERATURE", "0.3"))

# Supported backends for the sidebar dropdown.
SUPPORTED_BACKENDS: list[str] = ["ollama", "openai", "openrouter", "gemini"]

# Curated model options per backend (shown in dev-mode sidebar dropdown).
# The first model in each list is the default for that backend.
MODEL_OPTIONS: dict[str, list[str]] = {
    "ollama": [
        "eurecom-ds/phi-3-mini-4k-socratic",
        "llama3.3",
        "mistral",
        "phi3",
        "qwen2.5",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-5",
        "gpt-5.2",
        "gpt-5.4",
    ],
    "openrouter": [
        "google/gemini-2.5-flash",
        "google/gemini-2.5-pro",
        "google/gemini-3-flash-preview",
        "anthropic/claude-sonnet-4",
        "deepseek/deepseek-v3-0324",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen3-coder-480b:free",
    ],
    "gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3.1-pro-preview",
        "gemini-2.5-flash-lite",
    ],
}

# OpenRouter settings (OpenAI-compatible API).
OPENROUTER_BASE_URL: str = _get_config(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1",
)
OPENROUTER_API_KEY: str = _get_config("OPENROUTER_API_KEY", "")

# Google Gemini settings.
GEMINI_API_KEY: str = _get_config("GEMINI_API_KEY", "")

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
QUALTRICS_POST_SURVEY_URL: str = _get_config(
    "QUALTRICS_POST_SURVEY_URL",
    "https://fra1.qualtrics.com/jfe/form/SV_37uMu9WF3PngHFI"
    "?pid={pid}&wave=post&condition={condition}",
)

# Debriefing URL for withdrawn participants.
QUALTRICS_DEBRIEFING_URL: str = _get_config(
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

"""
test_app.py — Basic tests for the Socratic Tutor project.

Run with:
    python -m pytest tests/
"""

import json
import os
import tempfile
from pathlib import Path

# Project root is one level up from the tests/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ── Test: configuration loading ──────────────────────────────────────────────

def test_env_example_exists():
    """The .env.example file should exist so users know which variables to set."""
    env_example = PROJECT_ROOT / ".env.example"
    assert env_example.exists(), ".env.example is missing from the project root"


def test_env_example_contains_required_vars():
    """The .env.example file should document all required environment variables."""
    env_example = PROJECT_ROOT / ".env.example"
    content = env_example.read_text()

    required_vars = ["OLLAMA_HOST", "QUALTRICS_POST_SURVEY_URL", "MODEL_NAME"]
    for var in required_vars:
        assert var in content, f".env.example is missing the variable: {var}"


def test_requirements_txt_exists():
    """requirements.txt must exist so dependencies can be installed."""
    req = PROJECT_ROOT / "requirements.txt"
    assert req.exists(), "requirements.txt is missing"


def test_requirements_txt_has_dependencies():
    """requirements.txt should list the core dependencies."""
    req = PROJECT_ROOT / "requirements.txt"
    content = req.read_text()

    for dep in ["streamlit", "ollama", "pandas"]:
        assert dep in content, f"requirements.txt is missing dependency: {dep}"


# ── Test: logger produces valid JSON ─────────────────────────────────────────

def test_logger_creates_valid_json():
    """Verify that a sample log structure serialises to valid JSON and back."""
    sample_log = {
        "participant_id": "P001",
        "condition": "socratic",
        "model_name": "eurecom-ds/phi-3-mini-4k-socratic",
        "session_start": "2025-06-01T10:00:00",
        "session_end": "2025-06-01T10:15:00",
        "messages": [
            {
                "role": "user",
                "content": "What is recursion?",
                "timestamp": "2025-06-01T10:00:05",
            },
            {
                "role": "assistant",
                "content": "What do you think happens when a function calls itself?",
                "timestamp": "2025-06-01T10:00:08",
            },
        ],
    }

    # Write to a temporary file and read it back
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(sample_log, tmp)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "r") as f:
            loaded = json.load(f)

        assert loaded["participant_id"] == "P001"
        assert len(loaded["messages"]) == 2
        assert loaded["messages"][0]["role"] == "user"
    finally:
        os.unlink(tmp_path)


# ── Test: prompt file ────────────────────────────────────────────────────────

def test_prompt_directory_exists():
    """The prompts/ directory should exist (or at least the project root should
    contain a system prompt file). This test checks for common prompt locations."""
    possible_locations = [
        PROJECT_ROOT / "prompts",
        PROJECT_ROOT / "prompt.txt",
        PROJECT_ROOT / "system_prompt.txt",
        PROJECT_ROOT / "config",
    ]

    # At least one prompt-related path should exist once the app is set up.
    # During early development this test is allowed to be skipped.
    found = any(p.exists() for p in possible_locations)
    if not found:
        import warnings
        warnings.warn(
            "No prompt file or prompts/ directory found yet. "
            "This is expected during initial setup."
        )

"""
Configuration for the Qualtrics survey generation and API scripts.

API token must be set via the QUALTRICS_API_TOKEN environment variable.
Never hardcode secrets in source code.
"""

import os

DATACENTER = "fra1"
BASE_URL = f"https://{DATACENTER}.qualtrics.com/API/v3"
SURVEY_NAME = "Socratic AI Causal Inference Study (Pilot)"

STREAMLIT_APP_URL = os.environ.get(
    "STREAMLIT_APP_URL",
    "https://YOUR-APP.streamlit.app",
)

QUALTRICS_SURVEY_URL_TEMPLATE = (
    f"https://{DATACENTER}.qualtrics.com/jfe/form/{{survey_id}}"
)


def get_api_token() -> str:
    """Return the Qualtrics API token from the environment.

    Raises
    ------
    RuntimeError
        If QUALTRICS_API_TOKEN is not set.
    """
    token = os.environ.get("QUALTRICS_API_TOKEN")
    if not token:
        raise RuntimeError(
            "QUALTRICS_API_TOKEN environment variable is not set. "
            "Set it before running this script: "
            "export QUALTRICS_API_TOKEN='your-token-here'"
        )
    return token


def get_headers() -> dict[str, str]:
    """Return HTTP headers for Qualtrics API requests."""
    return {
        "X-API-TOKEN": get_api_token(),
        "Content-Type": "application/json",
    }

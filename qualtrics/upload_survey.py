"""
Upload a QSF file to Qualtrics via the REST API.

Usage:
    export QUALTRICS_API_TOKEN='your-token'
    python -m qualtrics.upload_survey

Reads qualtrics/output/survey.qsf and imports it as a new survey.
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

from qualtrics import config as qconfig


def upload(qsf_path: Path | None = None) -> tuple[str, str]:
    """Upload a QSF file to Qualtrics.

    Parameters
    ----------
    qsf_path : Path, optional
        Path to the QSF file.  Defaults to ``output/survey.qsf``.

    Returns
    -------
    tuple[str, str]
        ``(survey_id, survey_url)``

    Raises
    ------
    RuntimeError
        If the upload fails.
    """
    if qsf_path is None:
        qsf_path = Path(__file__).resolve().parent / "output" / "survey.qsf"

    if not qsf_path.exists():
        raise FileNotFoundError(
            f"QSF file not found: {qsf_path}\n"
            "Run 'python -m qualtrics.generate_qsf' first."
        )

    url = f"{qconfig.BASE_URL}/surveys"
    headers = {"X-API-TOKEN": qconfig.get_api_token()}

    with open(qsf_path, "rb") as f:
        files = {"file": (qsf_path.name, f)}
        data = {"name": qconfig.SURVEY_NAME}
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Upload failed (HTTP {response.status_code}):\n"
            f"{response.text}"
        )

    result = response.json().get("result", {})
    survey_id = result.get("id", "UNKNOWN")
    survey_url = (
        f"https://{qconfig.DATACENTER}.qualtrics.com/jfe/form/{survey_id}"
    )

    print(f"Survey created successfully!")
    print(f"  Survey ID: {survey_id}")
    print(f"  Survey URL: {survey_url}")
    print(f"  Edit URL: https://{qconfig.DATACENTER}.qualtrics.com/"
          f"survey-builder/{survey_id}/edit")
    print()
    print("IMPORTANT: Update these values in your environment:")
    print(f"  QUALTRICS_POST_SURVEY_URL="
          f"'https://{qconfig.DATACENTER}.qualtrics.com/jfe/form/{survey_id}"
          f"?pid={{pid}}&wave=post&condition={{condition}}'")

    return survey_id, survey_url


if __name__ == "__main__":
    try:
        upload()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

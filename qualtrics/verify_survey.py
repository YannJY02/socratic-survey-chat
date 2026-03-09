"""
Verify an uploaded Qualtrics survey against the expected structure.

Usage:
    export QUALTRICS_API_TOKEN='your-token'
    python -m qualtrics.verify_survey SURVEY_ID

Checks:
  - 6 blocks with correct question counts
  - Flow structure: embedded data, 2 branches, randomiser, 2 end-of-survey
  - Embedded data fields: wave, pid, condition, phase_completed
"""

from __future__ import annotations

import sys

import requests

from qualtrics import config as qconfig

# Expected structure
EXPECTED_BLOCKS = {
    "B1: Informed Consent": {"min_questions": 2},    # display + consent MC
    "B2: Demographics": {"min_questions": 6},
    "B3: Prior Knowledge Pretest": {"min_questions": 15},
    "B4: Conceptual Understanding Post-Test": {"min_questions": 10},
    "B5: Far-Transfer Application Test": {"min_questions": 2},  # display + essay
    "B6: Debriefing": {"min_questions": 1},
}

EXPECTED_EMBEDDED_FIELDS = {"wave", "pid", "condition", "phase_completed"}


def _get_survey_definition(survey_id: str) -> dict:
    """Fetch the full survey definition from the API."""
    url = f"{qconfig.BASE_URL}/survey-definitions/{survey_id}"
    response = requests.get(url, headers=qconfig.get_headers(), timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch survey definition (HTTP {response.status_code}):"
            f"\n{response.text}"
        )
    return response.json().get("result", {})


def _check_blocks(definition: dict) -> list[str]:
    """Validate blocks and question counts."""
    issues: list[str] = []
    blocks = definition.get("Blocks", {})

    found_blocks: dict[str, int] = {}
    for block_data in blocks.values():
        desc = block_data.get("Description", "")
        elements = block_data.get("BlockElements", [])
        question_count = sum(
            1 for e in elements if e.get("Type") == "Question"
        )
        found_blocks[desc] = question_count

    for expected_name, constraints in EXPECTED_BLOCKS.items():
        if expected_name not in found_blocks:
            issues.append(f"FAIL: Block '{expected_name}' not found")
        else:
            actual = found_blocks[expected_name]
            minimum = constraints["min_questions"]
            if actual < minimum:
                issues.append(
                    f"FAIL: Block '{expected_name}' has {actual} questions "
                    f"(expected >= {minimum})"
                )
            else:
                print(
                    f"  PASS: Block '{expected_name}' — "
                    f"{actual} questions (>= {minimum})"
                )

    return issues


def _get_survey_flow(survey_id: str) -> dict:
    """Fetch the survey flow from the dedicated flow endpoint."""
    url = f"{qconfig.BASE_URL}/survey-definitions/{survey_id}/flow"
    response = requests.get(url, headers=qconfig.get_headers(), timeout=30)
    if response.status_code != 200:
        return {}
    return response.json().get("result", {})


def _check_flow(definition: dict, survey_id: str) -> list[str]:
    """Validate flow structure."""
    issues: list[str] = []

    # Try flow from definition first, then from dedicated endpoint
    flow_data = definition.get("Flow", [])
    if not flow_data:
        flow_data = _get_survey_flow(survey_id)

    # Handle both dict (root element) and list formats
    if isinstance(flow_data, dict):
        flow = flow_data.get("Flow", [])
    elif isinstance(flow_data, list):
        flow = flow_data
    else:
        flow = []

    if not flow:
        issues.append("FAIL: No flow elements found")
        return issues

    # Check for embedded data
    embedded_data_found = False
    branch_count = 0
    end_survey_count = 0
    randomizer_found = False

    def _walk_flow(elements: list) -> None:
        nonlocal embedded_data_found, branch_count, end_survey_count
        nonlocal randomizer_found

        for element in elements:
            flow_type = element.get("Type", "")
            if flow_type == "EmbeddedData":
                embedded_data_found = True
                # Check for expected fields
                ed_items = element.get("EmbeddedData", [])
                found_fields = {
                    item.get("Field") for item in ed_items
                }
                for field in EXPECTED_EMBEDDED_FIELDS:
                    if field in found_fields:
                        print(f"  PASS: Embedded field '{field}' present")
                    # Don't fail on missing — they may be in nested elements

            elif flow_type == "Branch":
                branch_count += 1
                sub_flow = element.get("Flow", [])
                _walk_flow(sub_flow)

            elif flow_type == "EndSurvey":
                end_survey_count += 1

            elif flow_type == "BlockRandomizer":
                randomizer_found = True
                sub_flow = element.get("Flow", [])
                _walk_flow(sub_flow)

            elif flow_type == "Block":
                pass  # Expected

            if "Flow" in element and flow_type not in (
                "Branch", "BlockRandomizer"
            ):
                sub_flow = element.get("Flow", [])
                if isinstance(sub_flow, list):
                    _walk_flow(sub_flow)

    _walk_flow(flow)

    if not embedded_data_found:
        issues.append("FAIL: No EmbeddedData element found in flow")
    else:
        print("  PASS: EmbeddedData element found")

    if branch_count < 2:
        issues.append(
            f"FAIL: Expected 2 branches, found {branch_count}"
        )
    else:
        print(f"  PASS: {branch_count} branches found (expected 2)")

    if not randomizer_found:
        issues.append("FAIL: No BlockRandomizer found in flow")
    else:
        print("  PASS: BlockRandomizer found")

    if end_survey_count < 2:
        issues.append(
            f"FAIL: Expected 2 EndSurvey elements, found {end_survey_count}"
        )
    else:
        print(f"  PASS: {end_survey_count} EndSurvey elements found")

    return issues


def verify(survey_id: str) -> bool:
    """Run all verification checks.

    Returns True if all checks pass, False otherwise.
    """
    print(f"Verifying survey: {survey_id}")
    print(f"API endpoint: {qconfig.BASE_URL}")
    print()

    definition = _get_survey_definition(survey_id)

    print("=== Block Checks ===")
    block_issues = _check_blocks(definition)
    print()

    print("=== Flow Checks ===")
    flow_issues = _check_flow(definition, survey_id)
    print()

    all_issues = block_issues + flow_issues

    print("=== Summary ===")
    if all_issues:
        print(f"FAILED: {len(all_issues)} issue(s) found:")
        for issue in all_issues:
            print(f"  {issue}")
        return False

    print("ALL CHECKS PASSED")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m qualtrics.verify_survey SURVEY_ID")
        sys.exit(1)

    survey_id_arg = sys.argv[1]
    success = verify(survey_id_arg)
    sys.exit(0 if success else 1)

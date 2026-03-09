"""
Deploy the survey to Qualtrics using the REST API (step-by-step).

This is the reliable alternative to QSF import. It creates the survey,
adds blocks, questions, embedded data, and configures the flow using
individual API calls.

Usage:
    export QUALTRICS_API_TOKEN='your-token'
    python -m qualtrics.deploy_survey

Flow configuration (branches, randomiser, end-of-survey redirect) is
complex to set up via API, so this script outputs instructions for
manual flow configuration in the Qualtrics UI after creating all blocks
and questions.
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any

import requests

from qualtrics import config as qconfig
from qualtrics.content.consent import CONSENT_ITEMS, CONSENT_TEXT
from qualtrics.content.debriefing import DEBRIEFING_ITEMS
from qualtrics.content.demographics import DEMOGRAPHICS_ITEMS
from qualtrics.content.posttest_conceptual import POSTTEST_CONCEPTUAL_ITEMS
from qualtrics.content.posttest_far_transfer import FAR_TRANSFER_ITEMS
from qualtrics.content.pretest import PRETEST_ITEMS


# ── API helpers ───────────────────────────────────────────────────────

def _api_get(path: str) -> dict:
    """GET request to the Qualtrics API."""
    url = f"{qconfig.BASE_URL}{path}"
    resp = requests.get(url, headers=qconfig.get_headers(), timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"GET {path} failed ({resp.status_code}): {resp.text}")
    return resp.json().get("result", {})


def _api_post(path: str, payload: dict | None = None) -> dict:
    """POST request to the Qualtrics API."""
    url = f"{qconfig.BASE_URL}{path}"
    resp = requests.post(
        url, headers=qconfig.get_headers(), json=payload, timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"POST {path} failed ({resp.status_code}): {resp.text}"
        )
    return resp.json().get("result", {})


def _api_put(path: str, payload: dict) -> dict:
    """PUT request to the Qualtrics API."""
    url = f"{qconfig.BASE_URL}{path}"
    resp = requests.put(
        url, headers=qconfig.get_headers(), json=payload, timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"PUT {path} failed ({resp.status_code}): {resp.text}"
        )
    return resp.json().get("result", {})


# ── Question builders ─────────────────────────────────────────────────

def _build_mc_payload(
    item: dict[str, Any], data_export_tag: str,
) -> dict[str, Any]:
    """Build the API payload for a multiple-choice question."""
    choices: dict[str, dict] = {}
    choice_order: list[int] = []
    for idx, choice in enumerate(item["choices"], start=1):
        key = str(idx)
        choices[key] = {"Display": choice["label"]}
        choice_order.append(idx)

    return {
        "QuestionText": item["text"],
        "DataExportTag": data_export_tag,
        "QuestionType": "MC",
        "Selector": "SAVR",
        "SubSelector": "TX",
        "Configuration": {"QuestionDescriptionOption": "UseText"},
        "Choices": choices,
        "ChoiceOrder": choice_order,
        "Validation": {
            "Settings": {
                "ForceResponse": "ON" if item.get("force_response") else "OFF",
                "ForceResponseType": "ON",
                "Type": "None",
            },
        },
        "Language": {},
    }


def _build_te_payload(
    item: dict[str, Any], data_export_tag: str,
) -> dict[str, Any]:
    """Build the API payload for a text-entry question."""
    subtype = item.get("subtype", "text")

    selector_map = {
        "text": "SL",
        "numeric": "SL",
        "essay": "ESTB",
    }
    selector = selector_map.get(subtype, "SL")

    validation: dict[str, Any] = {
        "ForceResponse": "ON" if item.get("force_response") else "OFF",
        "ForceResponseType": "ON",
        "Type": "None",
    }

    # For numeric fields, use content-type validation without Min/Max
    # (Min/Max not supported in the Qualtrics question creation API).
    if subtype == "numeric":
        validation["Type"] = "ContentType"
        validation["ContentType"] = "ValidNumber"

    if subtype == "essay" and "validation" in item:
        if "min_chars" in item["validation"]:
            validation["Type"] = "CharRange"
            validation["MinChars"] = str(item["validation"]["min_chars"])

    return {
        "QuestionText": item["text"],
        "DataExportTag": data_export_tag,
        "QuestionType": "TE",
        "Selector": selector,
        "Configuration": {"QuestionDescriptionOption": "UseText"},
        "Validation": {"Settings": validation},
        "Language": {},
    }


def _build_display_payload(
    item: dict[str, Any], data_export_tag: str,
) -> dict[str, Any]:
    """Build the API payload for a display-only (descriptive) question."""
    return {
        "QuestionText": item["text"],
        "DataExportTag": data_export_tag,
        "QuestionType": "DB",
        "Selector": "TB",
        "Configuration": {"QuestionDescriptionOption": "UseText"},
        "Language": {},
    }


def _build_question_payload(
    item: dict[str, Any], data_export_tag: str,
) -> dict[str, Any]:
    """Build the API payload for any question type."""
    item_type = item.get("type", "MC")
    if item_type == "MC":
        return _build_mc_payload(item, data_export_tag)
    if item_type in ("TextEntry", "SA"):
        return _build_te_payload(item, data_export_tag)
    if item_type == "Display":
        return _build_display_payload(item, data_export_tag)
    raise ValueError(f"Unknown item type: {item_type}")


# ── Survey creation ───────────────────────────────────────────────────

def _create_survey() -> str:
    """Create a blank survey via survey-definitions and return its ID."""
    result = _api_post("/survey-definitions", {
        "SurveyName": qconfig.SURVEY_NAME,
        "Language": "EN",
        "ProjectCategory": "CORE",
    })
    survey_id = result.get("SurveyID", result.get("SurveyId", ""))
    if not survey_id:
        raise RuntimeError(f"No survey ID in response: {result}")
    print(f"  Survey created: {survey_id}")
    return survey_id


def _create_block(survey_id: str, description: str) -> str:
    """Create a block in the survey and return its ID."""
    result = _api_post(
        f"/survey-definitions/{survey_id}/blocks",
        {"Type": "Standard", "Description": description},
    )
    block_id = result.get("BlockID", "")
    if not block_id:
        raise RuntimeError(f"No block ID in response: {result}")
    return block_id


def _create_question(
    survey_id: str,
    block_id: str,
    payload: dict[str, Any],
) -> str:
    """Create a question in a specific block and return its QID."""
    url = (
        f"{qconfig.BASE_URL}/survey-definitions/{survey_id}/questions"
        f"?blockId={block_id}"
    )
    resp = requests.post(
        url, headers=qconfig.get_headers(), json=payload, timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"POST questions failed ({resp.status_code}): {resp.text}"
        )
    result = resp.json().get("result", {})
    qid = result.get("QuestionID", "")
    if not qid:
        raise RuntimeError(f"No QuestionID in response: {result}")
    return qid


def _add_block_questions(
    survey_id: str,
    block_id: str,
    items: list[dict[str, Any]],
    *,
    consent_text: str | None = None,
) -> list[tuple[str, dict]]:
    """Add all questions for a block. Returns list of (qid, item) pairs."""
    qid_items: list[tuple[str, dict]] = []

    # If consent block, add the consent info display first
    if consent_text is not None:
        display_payload = _build_display_payload(
            {"id": "consent_info", "text": consent_text},
            "consent_info",
        )
        qid = _create_question(survey_id, block_id, display_payload)
        qid_items.append((qid, {"id": "consent_info", "type": "Display"}))

    for item in items:
        tag = item["id"]
        payload = _build_question_payload(item, tag)
        qid = _create_question(survey_id, block_id, payload)
        qid_items.append((qid, item))

    return qid_items


# ── Flow configuration ────────────────────────────────────────────────

def _build_flow(
    block_ids: dict[str, str],
    streamlit_url: str,
) -> dict[str, Any]:
    """Build the two-wave flow structure."""
    fl_counter = {"n": 0}

    def _fl() -> str:
        fl_counter["n"] += 1
        return f"FL_{fl_counter['n']}"

    # Embedded data
    embedded_data = {
        "Type": "EmbeddedData",
        "FlowID": _fl(),
        "EmbeddedData": [
            {"Description": "wave", "Type": "Recipient",
             "Field": "wave", "VariableType": "String",
             "DataVisibility": [], "AnalyzeText": False},
            {"Description": "pid", "Type": "Recipient",
             "Field": "pid", "VariableType": "String",
             "DataVisibility": [], "AnalyzeText": False},
            {"Description": "condition", "Type": "Recipient",
             "Field": "condition", "VariableType": "String",
             "DataVisibility": [], "AnalyzeText": False},
            {"Description": "phase_completed", "Type": "Recipient",
             "Field": "phase_completed", "VariableType": "String",
             "DataVisibility": [], "AnalyzeText": False},
        ],
    }

    # Set pid = ResponseID (inside wave 1)
    set_pid = {
        "Type": "EmbeddedData",
        "FlowID": _fl(),
        "EmbeddedData": [
            {"Description": "pid", "Type": "Custom",
             "Field": "pid", "VariableType": "String",
             "Value": "${e://Field/ResponseID}",
             "DataVisibility": [], "AnalyzeText": False},
        ],
    }

    # Wave 1 blocks
    wave1_flow = [
        set_pid,
        {"Type": "Block", "ID": block_ids["B1"], "FlowID": _fl()},
        {"Type": "Block", "ID": block_ids["B2"], "FlowID": _fl()},
        {"Type": "Block", "ID": block_ids["B3"], "FlowID": _fl()},
        # Randomiser for condition
        {
            "Type": "BlockRandomizer",
            "FlowID": _fl(),
            "SubSet": 1,
            "EvenPresentation": True,
            "Flow": [
                {
                    "Type": "EmbeddedData",
                    "FlowID": _fl(),
                    "EmbeddedData": [
                        {"Description": "condition", "Type": "Custom",
                         "Field": "condition", "VariableType": "String",
                         "Value": "I_PS",
                         "DataVisibility": [], "AnalyzeText": False},
                    ],
                },
                {
                    "Type": "EmbeddedData",
                    "FlowID": _fl(),
                    "EmbeddedData": [
                        {"Description": "condition", "Type": "Custom",
                         "Field": "condition", "VariableType": "String",
                         "Value": "PS_I",
                         "DataVisibility": [], "AnalyzeText": False},
                    ],
                },
            ],
        },
        # End survey with redirect to Streamlit
        {
            "Type": "EndSurvey",
            "FlowID": _fl(),
            "Options": {
                "Advanced": "true",
                "SurveyTermination": "Redirect",
                "EOSRedirectURL": streamlit_url,
            },
        },
    ]

    wave1_branch = {
        "Type": "Branch",
        "FlowID": _fl(),
        "Description": "Wave 1: Pre-survey",
        "BranchLogic": {
            "0": {
                "0": {
                    "LogicType": "EmbeddedField",
                    "LeftOperand": "wave",
                    "Operator": "EqualTo",
                    "RightOperand": "",
                    "Type": "Expression",
                    "Description": (
                        '<span class="ConjDesc">If</span> '
                        '<span class="LeftOpDesc">wave</span> '
                        '<span class="OpDesc">Is Equal to</span> '
                        '<span class="RightOpDesc"> </span>'
                    ),
                },
                "Type": "If",
            },
            "Type": "BooleanExpression",
        },
        "Flow": wave1_flow,
    }

    # Wave 2 blocks
    wave2_flow = [
        {"Type": "Block", "ID": block_ids["B4"], "FlowID": _fl()},
        {"Type": "Block", "ID": block_ids["B5"], "FlowID": _fl()},
        {"Type": "Block", "ID": block_ids["B6"], "FlowID": _fl()},
        {
            "Type": "EndSurvey",
            "FlowID": _fl(),
            "Options": {
                "Advanced": "false",
                "SurveyTermination": "DefaultMessage",
            },
        },
    ]

    wave2_branch = {
        "Type": "Branch",
        "FlowID": _fl(),
        "Description": "Wave 2: Post-survey",
        "BranchLogic": {
            "0": {
                "0": {
                    "LogicType": "EmbeddedField",
                    "LeftOperand": "wave",
                    "Operator": "EqualTo",
                    "RightOperand": "post",
                    "Type": "Expression",
                    "Description": (
                        '<span class="ConjDesc">If</span> '
                        '<span class="LeftOpDesc">wave</span> '
                        '<span class="OpDesc">Is Equal to</span> '
                        '<span class="RightOpDesc"> post</span>'
                    ),
                },
                "Type": "If",
            },
            "Type": "BooleanExpression",
        },
        "Flow": wave2_flow,
    }

    return {
        "Type": "Root",
        "FlowID": _fl(),
        "Flow": [
            embedded_data,
            wave1_branch,
            wave2_branch,
        ],
        "Properties": {
            "Count": fl_counter["n"],
            "RemovedFieldsets": [],
        },
    }


# ── Consent skip logic ────────────────────────────────────────────────

def _add_consent_skip_logic(
    survey_id: str,
    consent_qid: str,
    no_consent_choice_idx: int,
) -> None:
    """Add skip logic to end survey if participant does not consent."""
    # GET the current question definition
    question = _api_get(
        f"/survey-definitions/{survey_id}/questions/{consent_qid}"
    )

    # Add skip logic
    question["SkipLogic"] = {
        "0": {
            "0": {
                "LogicType": "Question",
                "QuestionID": consent_qid,
                "QuestionIsInLoop": "no",
                "ChoiceLocator": (
                    f"q://{consent_qid}/SelectableChoice/"
                    f"{no_consent_choice_idx}"
                ),
                "Operator": "Selected",
                "QuestionIDFromLocator": consent_qid,
                "LeftOperand": (
                    f"q://{consent_qid}/SelectableChoice/"
                    f"{no_consent_choice_idx}"
                ),
                "Type": "Expression",
                "Description": (
                    '<span class="ConjDesc">If</span> '
                    '<span class="QuestionDesc">consent</span> '
                    '<span class="LeftOpDesc">'
                    "I do not consent</span> "
                    '<span class="OpDesc">Is Selected</span>'
                ),
            },
            "Type": "If",
        },
        "Type": "BooleanExpression",
        "SkipToDestination": "EndOfSurvey",
        "SkipToDescription": "End of Survey",
    }

    _api_put(
        f"/survey-definitions/{survey_id}/questions/{consent_qid}",
        question,
    )


# ── Main deployment ───────────────────────────────────────────────────

def deploy() -> tuple[str, str]:
    """Deploy the complete survey to Qualtrics.

    Returns
    -------
    tuple[str, str]
        ``(survey_id, survey_url)``
    """
    print("=" * 60)
    print("Deploying survey to Qualtrics via REST API")
    print("=" * 60)

    # 1. Create the survey
    print("\n[1/6] Creating survey...")
    survey_id = _create_survey()

    # 2. Create blocks and questions
    block_ids: dict[str, str] = {}
    pretest_qid_map: dict[str, str] = {}

    block_defs = [
        ("B1", "B1: Informed Consent", CONSENT_ITEMS, "pre", True),
        ("B2", "B2: Demographics", DEMOGRAPHICS_ITEMS, "pre", False),
        ("B3", "B3: Prior Knowledge Pretest", PRETEST_ITEMS, "pre", False),
        ("B4", "B4: Conceptual Understanding Post-Test",
         POSTTEST_CONCEPTUAL_ITEMS, "post", False),
        ("B5", "B5: Far-Transfer Application Test",
         FAR_TRANSFER_ITEMS, "post", False),
        ("B6", "B6: Debriefing", DEBRIEFING_ITEMS, "post", False),
    ]

    print("\n[2/6] Creating blocks and questions...")
    consent_qid: str | None = None
    no_consent_idx: int | None = None

    for key, name, items, _wave, is_consent in block_defs:
        print(f"  Creating block: {name}")
        bid = _create_block(survey_id, name)
        block_ids[key] = bid

        # Add questions
        consent_text_arg = CONSENT_TEXT if is_consent else None
        qid_items = _add_block_questions(
            survey_id, bid, items, consent_text=consent_text_arg,
        )

        for qid, item in qid_items:
            # Track pretest QIDs for scoring
            if item.get("concept") and item.get("correct"):
                pretest_qid_map[item["id"]] = qid

            # Track consent question for skip logic
            if is_consent and item.get("skip_logic"):
                consent_qid = qid
                for idx, c in enumerate(item["choices"], start=1):
                    if c["value"] == item["skip_logic"]["condition"]:
                        no_consent_idx = idx
                        break

        question_count = len(qid_items)
        print(f"    → {question_count} questions added")
        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # 3. Add consent skip logic
    print("\n[3/6] Configuring consent skip logic...")
    if consent_qid and no_consent_idx:
        try:
            _add_consent_skip_logic(survey_id, consent_qid, no_consent_idx)
            print("  → Skip logic added")
        except RuntimeError as exc:
            print(f"  ⚠ Skip logic failed (configure manually): {exc}")
    else:
        print("  ⚠ Could not find consent question — configure manually")

    # 4. Configure flow
    print("\n[4/6] Configuring survey flow...")
    streamlit_url = (
        f"{qconfig.STREAMLIT_APP_URL}"
        "/?pid=${e://Field/pid}"
        "&condition=${e://Field/condition}"
    )

    flow = _build_flow(block_ids, streamlit_url)
    try:
        _api_put(f"/survey-definitions/{survey_id}/flow", flow)
        print("  → Flow configured successfully")
    except RuntimeError as exc:
        print(f"  ⚠ Flow configuration failed: {exc}")
        print("  → You will need to configure the flow manually in the UI.")
        print("     See the plan document for the flow structure.")

    # 5. Configure survey options
    print("\n[5/6] Configuring survey options...")
    try:
        _api_put(f"/survey-definitions/{survey_id}/options", {
            "BackButton": "false",
            "SaveAndContinue": "true",
            "SurveyProtection": "PublicSurvey",
            "BallotBoxStuffingPrevention": "false",
            "NoIndex": "Yes",
            "SecureResponseFiles": "true",
            "SurveyTermination": "DefaultMessage",
            "ProgressBarDisplay": "None",
            "PartialData": "+1 week",
            "SurveyTitle": qconfig.SURVEY_NAME,
            "CollectGeoLocation": "false",
            "SurveyMetaDescription": (
                "Pilot study on Socratic AI tutoring for causal inference"
            ),
            "AnonymizeResponse": "No",
        })
        print("  → Options configured")
    except RuntimeError as exc:
        print(f"  ⚠ Options configuration failed: {exc}")

    # 6. Summary
    survey_url = (
        f"https://{qconfig.DATACENTER}.qualtrics.com/jfe/form/{survey_id}"
    )
    edit_url = (
        f"https://{qconfig.DATACENTER}.qualtrics.com/"
        f"survey-builder/{survey_id}/edit"
    )

    print("\n[6/6] Deployment complete!")
    print("=" * 60)
    print(f"  Survey ID:  {survey_id}")
    print(f"  Survey URL: {survey_url}")
    print(f"  Edit URL:   {edit_url}")
    print()
    print("IMPORTANT — Update your environment variables:")
    print(f"  QUALTRICS_POST_SURVEY_URL="
          f"'https://{qconfig.DATACENTER}.qualtrics.com/jfe/form/{survey_id}"
          f"?pid={{pid}}&wave=post&condition={{condition}}'")
    print()
    print("MANUAL STEPS REQUIRED:")
    print("  1. Open the Edit URL above in your browser")
    print("  2. Verify the survey flow (Survey Flow tab):")
    print("     - EmbeddedData: wave, pid, condition, phase_completed")
    print("     - Branch 1 (wave is empty): B1 → B2 → B3 → Randomiser → "
          "End Survey (redirect)")
    print("     - Branch 2 (wave = post): B4 → B5 → B6 → End Survey")
    print("  3. Preview both waves to confirm correct routing")
    print("  4. Activate the survey when ready")

    return survey_id, survey_url


if __name__ == "__main__":
    try:
        deploy()
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        sys.exit(1)

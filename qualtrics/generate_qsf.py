"""
Generate a complete Qualtrics Survey File (QSF) for the pilot study.

This script builds the QSF JSON structure from the content modules and
writes it to qualtrics/output/survey.qsf.

Usage:
    python -m qualtrics.generate_qsf

The generated QSF can be imported via the Qualtrics UI or via the API
using upload_survey.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from qualtrics import config as qconfig
from qualtrics.content.consent import CONSENT_ITEMS, CONSENT_TEXT
from qualtrics.content.debriefing import DEBRIEFING_ITEMS
from qualtrics.content.demographics import DEMOGRAPHICS_ITEMS
from qualtrics.content.posttest_conceptual import POSTTEST_CONCEPTUAL_ITEMS
from qualtrics.content.posttest_far_transfer import FAR_TRANSFER_ITEMS
from qualtrics.content.pretest import PRETEST_ITEMS


# ── Helpers ────────────────────────────────────────────────────────────

def _next_qid(counter: dict[str, int]) -> str:
    """Return the next QID string and increment the counter."""
    counter["n"] += 1
    return f"QID{counter['n']}"


def _build_mc_question(
    item: dict[str, Any],
    qid: str,
    data_export_tag: str,
) -> dict[str, Any]:
    """Build a QSF SurveyQuestion element for a multiple-choice item."""
    choices = {}
    choice_order = []
    for idx, choice in enumerate(item["choices"], start=1):
        key = str(idx)
        choices[key] = {"Display": choice["label"]}
        choice_order.append(int(key))

    question: dict[str, Any] = {
        "SurveyID": "PLACEHOLDER",
        "Element": "SQ",
        "PrimaryAttribute": qid,
        "SecondaryAttribute": item["text"],
        "TertiaryAttribute": None,
        "Payload": {
            "QuestionText": item["text"],
            "DataExportTag": data_export_tag,
            "QuestionType": "MC",
            "Selector": "SAVR",  # Single Answer Vertical Radio
            "SubSelector": "TX",
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": item["text"][:100],
            "Choices": choices,
            "ChoiceOrder": choice_order,
            "Validation": {
                "Settings": {
                    "ForceResponse": "ON" if item.get("force_response") else "OFF",
                    "ForceResponseType": "ON",
                    "Type": "None",
                },
            },
            "Language": [],
            "QuestionID": qid,
            "DataVisibility": {"Private": False, "Hidden": False},
        },
    }
    return question


def _build_text_entry_question(
    item: dict[str, Any],
    qid: str,
    data_export_tag: str,
) -> dict[str, Any]:
    """Build a QSF SurveyQuestion element for a text entry item."""
    subtype = item.get("subtype", "text")

    selector_map = {
        "text": "SL",       # Single Line
        "numeric": "SL",    # Single Line (with numeric validation)
        "essay": "ESTB",    # Essay Text Box
    }
    selector = selector_map.get(subtype, "SL")

    validation_settings: dict[str, Any] = {
        "ForceResponse": "ON" if item.get("force_response") else "OFF",
        "ForceResponseType": "ON",
        "Type": "None",
    }

    if subtype == "numeric":
        validation_settings["Type"] = "ContentType"
        validation_settings["ContentType"] = "ValidNumber"
        if "validation" in item:
            if "min" in item["validation"]:
                validation_settings["Min"] = str(item["validation"]["min"])
            if "max" in item["validation"]:
                validation_settings["Max"] = str(item["validation"]["max"])

    if subtype == "essay" and "validation" in item:
        if "min_chars" in item["validation"]:
            validation_settings["Type"] = "CharRange"
            validation_settings["MinChars"] = str(
                item["validation"]["min_chars"]
            )

    question: dict[str, Any] = {
        "SurveyID": "PLACEHOLDER",
        "Element": "SQ",
        "PrimaryAttribute": qid,
        "SecondaryAttribute": item["text"][:100],
        "TertiaryAttribute": None,
        "Payload": {
            "QuestionText": item["text"],
            "DataExportTag": data_export_tag,
            "QuestionType": "TE",
            "Selector": selector,
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": item["text"][:100],
            "Validation": {"Settings": validation_settings},
            "Language": [],
            "QuestionID": qid,
            "DataVisibility": {"Private": False, "Hidden": False},
        },
    }
    return question


def _build_display_question(
    item: dict[str, Any],
    qid: str,
    data_export_tag: str,
) -> dict[str, Any]:
    """Build a QSF SurveyQuestion element for a display-only item."""
    return {
        "SurveyID": "PLACEHOLDER",
        "Element": "SQ",
        "PrimaryAttribute": qid,
        "SecondaryAttribute": item["text"][:100],
        "TertiaryAttribute": None,
        "Payload": {
            "QuestionText": item["text"],
            "DataExportTag": data_export_tag,
            "QuestionType": "DB",  # Descriptive Block / Display
            "Selector": "TB",      # Text / Graphic
            "Configuration": {"QuestionDescriptionOption": "UseText"},
            "QuestionDescription": data_export_tag,
            "Language": [],
            "QuestionID": qid,
            "DataVisibility": {"Private": False, "Hidden": False},
        },
    }


def _build_question(
    item: dict[str, Any],
    qid: str,
    data_export_tag: str,
) -> dict[str, Any]:
    """Build a QSF question element based on item type."""
    item_type = item.get("type", "MC")

    if item_type == "MC":
        return _build_mc_question(item, qid, data_export_tag)
    if item_type in ("TextEntry", "SA"):
        return _build_text_entry_question(item, qid, data_export_tag)
    if item_type == "Display":
        return _build_display_question(item, qid, data_export_tag)

    raise ValueError(f"Unknown item type: {item_type}")


# ── Block builder ──────────────────────────────────────────────────────

def _build_block_element(
    block_id: str,
    description: str,
    question_ids: list[str],
    block_type: str = "Standard",
) -> dict[str, Any]:
    """Build a block definition for the BL element."""
    elements = [
        {"Type": "Question", "QuestionID": qid} for qid in question_ids
    ]
    return {
        "Type": block_type,
        "Description": description,
        "ID": block_id,
        "BlockElements": elements,
        "Options": {"BlockLocking": "false", "RandomizeQuestions": "false"},
    }


# ── Flow builder ───────────────────────────────────────────────────────

def _build_flow(
    pre_block_ids: list[str],
    post_block_ids: list[str],
    streamlit_redirect_url: str,
) -> dict[str, Any]:
    """Build the complete survey flow with two-wave branching.

    Wave 1 (wave is empty): consent -> demographics -> pretest -> randomise
        condition -> redirect to Streamlit
    Wave 2 (wave = "post"): conceptual post-test -> far-transfer -> debriefing
    """
    flow_id_counter = {"n": 0}

    def _next_fl_id() -> str:
        flow_id_counter["n"] += 1
        return f"FL_{flow_id_counter['n']}"

    # Embedded data element
    embedded_data_fl_id = _next_fl_id()
    embedded_data = {
        "Type": "EmbeddedData",
        "FlowID": embedded_data_fl_id,
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

    # ── Wave 1 branch (wave is empty) ──────────────────────────────
    wave1_blocks = []
    for bid in pre_block_ids:
        fl_id = _next_fl_id()
        wave1_blocks.append({
            "Type": "Block",
            "ID": bid,
            "FlowID": fl_id,
        })

    # Randomizer for condition assignment
    randomizer_fl_id = _next_fl_id()
    randomizer = {
        "Type": "BlockRandomizer",
        "FlowID": randomizer_fl_id,
        "SubSet": 1,
        "EvenPresentation": True,
        "Flow": [
            {
                "Type": "EmbeddedData",
                "FlowID": _next_fl_id(),
                "EmbeddedData": [
                    {"Description": "condition", "Type": "Custom",
                     "Field": "condition", "VariableType": "String",
                     "Value": "I_PS",
                     "DataVisibility": [], "AnalyzeText": False},
                ],
            },
            {
                "Type": "EmbeddedData",
                "FlowID": _next_fl_id(),
                "EmbeddedData": [
                    {"Description": "condition", "Type": "Custom",
                     "Field": "condition", "VariableType": "String",
                     "Value": "PS_I",
                     "DataVisibility": [], "AnalyzeText": False},
                ],
            },
        ],
    }

    # Set pid = ResponseID
    set_pid_fl_id = _next_fl_id()
    set_pid = {
        "Type": "EmbeddedData",
        "FlowID": set_pid_fl_id,
        "EmbeddedData": [
            {"Description": "pid", "Type": "Custom",
             "Field": "pid", "VariableType": "String",
             "Value": "${e://Field/ResponseID}",
             "DataVisibility": [], "AnalyzeText": False},
        ],
    }

    # End of survey: redirect to Streamlit
    eos_redirect_fl_id = _next_fl_id()
    eos_redirect = {
        "Type": "EndSurvey",
        "FlowID": eos_redirect_fl_id,
        "Options": {
            "Advanced": "true",
            "SurveyTermination": "Redirect",
            "EOSRedirectURL": streamlit_redirect_url,
        },
    }

    wave1_branch_fl_id = _next_fl_id()
    wave1_branch = {
        "Type": "Branch",
        "FlowID": wave1_branch_fl_id,
        "Description": "Wave 1: Pre-survey (wave is empty)",
        "BranchLogic": {
            "0": {
                "0": {
                    "LogicType": "EmbeddedField",
                    "LeftOperand": "wave",
                    "Operator": "EqualTo",
                    "RightOperand": "",
                    "Type": "Expression",
                    "Description": "<span class=\"ConjsDesc\">If</span>"
                                   " <span class=\"LeftOpDesc\">wave</span>"
                                   " <span class=\"OpDesc\">Is Equal to</span>"
                                   " <span class=\"RightOpDesc\"> </span>",
                },
                "Type": "If",
            },
            "Type": "BooleanExpression",
        },
        "Flow": [
            set_pid,
            *wave1_blocks,
            randomizer,
            eos_redirect,
        ],
    }

    # ── Wave 2 branch (wave = "post") ──────────────────────────────
    wave2_blocks = []
    for bid in post_block_ids:
        fl_id = _next_fl_id()
        wave2_blocks.append({
            "Type": "Block",
            "ID": bid,
            "FlowID": fl_id,
        })

    eos_default_fl_id = _next_fl_id()
    eos_default = {
        "Type": "EndSurvey",
        "FlowID": eos_default_fl_id,
        "Options": {
            "Advanced": "false",
            "SurveyTermination": "DefaultMessage",
        },
    }

    wave2_branch_fl_id = _next_fl_id()
    wave2_branch = {
        "Type": "Branch",
        "FlowID": wave2_branch_fl_id,
        "Description": "Wave 2: Post-survey (wave = post)",
        "BranchLogic": {
            "0": {
                "0": {
                    "LogicType": "EmbeddedField",
                    "LeftOperand": "wave",
                    "Operator": "EqualTo",
                    "RightOperand": "post",
                    "Type": "Expression",
                    "Description": "<span class=\"ConjsDesc\">If</span>"
                                   " <span class=\"LeftOpDesc\">wave</span>"
                                   " <span class=\"OpDesc\">Is Equal to</span>"
                                   " <span class=\"RightOpDesc\"> post</span>",
                },
                "Type": "If",
            },
            "Type": "BooleanExpression",
        },
        "Flow": [
            *wave2_blocks,
            eos_default,
        ],
    }

    # ── Root flow ──────────────────────────────────────────────────
    root_fl_id = _next_fl_id()
    return {
        "Type": "Root",
        "FlowID": root_fl_id,
        "Flow": [
            embedded_data,
            wave1_branch,
            wave2_branch,
        ],
        "Properties": {
            "Count": flow_id_counter["n"],
            "RemovedFieldsets": [],
        },
    }


# ── Scoring builder ───────────────────────────────────────────────────

def _build_scoring(
    pretest_qid_map: dict[str, str],
    pretest_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a scoring definition for auto-scoring pretest MC items."""
    scoring_definitions = []

    for item in pretest_items:
        qid = pretest_qid_map[item["id"]]
        correct_value = item.get("correct")
        if correct_value is None:
            continue

        # Find the choice index (1-based) for the correct answer
        correct_idx = None
        for idx, choice in enumerate(item["choices"], start=1):
            if choice["value"] == correct_value:
                correct_idx = idx
                break

        if correct_idx is None:
            continue

        scoring_definitions.append({
            "ScoringDefinitionID": f"SD_{item['id']}",
            "QID": qid,
            "ScoringCategory": "SC_Pretest",
            "ScoringCategoryName": "Pretest Score",
            "ChoiceValue": str(correct_idx),
            "Value": item.get("scoring_value", 1),
            "Type": "ChoiceScore",
        })

    return {
        "ScoringCategories": [
            {
                "ID": "SC_Pretest",
                "Name": "Pretest Score",
                "Description": "Auto-scored pretest (1 point per correct MC)",
            },
        ],
        "ScoringDefinitions": scoring_definitions,
    }


# ── Main generator ────────────────────────────────────────────────────

def generate() -> Path:
    """Generate the complete QSF file and write to output/survey.qsf."""
    qid_counter: dict[str, int] = {"n": 0}
    questions: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    pretest_qid_map: dict[str, str] = {}

    # Track block IDs for flow
    pre_block_ids: list[str] = []
    post_block_ids: list[str] = []

    block_counter = {"n": 0}

    def _next_block_id() -> str:
        block_counter["n"] += 1
        return f"BL_{block_counter['n']}"

    def _process_block(
        name: str,
        items: list[dict[str, Any]],
        wave: str,
        *,
        is_consent: bool = False,
    ) -> str:
        """Process all items in a block, returning the block ID."""
        block_id = _next_block_id()
        question_ids: list[str] = []

        for item in items:
            qid = _next_qid(qid_counter)
            data_export_tag = item["id"]

            # Special: consent block has the consent text as a display item
            # before the consent question
            if is_consent and item is items[0]:
                # Add consent text as a display question
                consent_display_qid = _next_qid(qid_counter)
                consent_display = _build_display_question(
                    {"id": "consent_info", "text": CONSENT_TEXT},
                    consent_display_qid,
                    "consent_info",
                )
                questions.append(consent_display)
                question_ids.append(consent_display_qid)

            question = _build_question(item, qid, data_export_tag)

            # Add skip logic for consent "I do not consent"
            if is_consent and item.get("skip_logic"):
                # Find the "no consent" choice index
                no_consent_idx = None
                for idx, c in enumerate(item["choices"], start=1):
                    if c["value"] == item["skip_logic"]["condition"]:
                        no_consent_idx = idx
                        break
                if no_consent_idx is not None:
                    question["Payload"]["SkipLogic"] = {
                        "0": {
                            "0": {
                                "LogicType": "Question",
                                "QuestionID": qid,
                                "QuestionIsInLoop": "no",
                                "ChoiceLocator": (
                                    f"q://{qid}/SelectableChoice/"
                                    f"{no_consent_idx}"
                                ),
                                "Operator": "Selected",
                                "QuestionIDFromLocator": qid,
                                "LeftOperand": (
                                    f"q://{qid}/SelectableChoice/"
                                    f"{no_consent_idx}"
                                ),
                                "Type": "Expression",
                                "Description": (
                                    "<span class=\"ConjsDesc\">If</span>"
                                    " <span class=\"QuestionDesc\">consent</span>"
                                    " <span class=\"LeftOpDesc\">I do not consent</span>"
                                    " <span class=\"OpDesc\">Is Selected</span>"
                                ),
                            },
                            "Type": "If",
                        },
                        "Type": "BooleanExpression",
                        "SkipToDestination": "EndOfSurvey",
                        "SkipToDescription": "End of Survey",
                    }

            questions.append(question)
            question_ids.append(qid)

            # Track pretest QID mapping for scoring
            if item.get("concept") and item.get("correct"):
                pretest_qid_map[item["id"]] = qid

        block = _build_block_element(block_id, name, question_ids)
        blocks.append(block)

        if wave == "pre":
            pre_block_ids.append(block_id)
        else:
            post_block_ids.append(block_id)

        return block_id

    # ── Process all blocks ─────────────────────────────────────────
    _process_block("B1: Informed Consent", CONSENT_ITEMS, "pre", is_consent=True)
    _process_block("B2: Demographics", DEMOGRAPHICS_ITEMS, "pre")
    _process_block("B3: Prior Knowledge Pretest", PRETEST_ITEMS, "pre")
    _process_block(
        "B4: Conceptual Understanding Post-Test",
        POSTTEST_CONCEPTUAL_ITEMS,
        "post",
    )
    _process_block("B5: Far-Transfer Application Test", FAR_TRANSFER_ITEMS, "post")
    _process_block("B6: Debriefing", DEBRIEFING_ITEMS, "post")

    # ── Build the Streamlit redirect URL ───────────────────────────
    streamlit_url = (
        f"{qconfig.STREAMLIT_APP_URL}"
        "/?pid=${e://Field/pid}"
        "&condition=${e://Field/condition}"
    )

    # ── Build flow ─────────────────────────────────────────────────
    flow = _build_flow(pre_block_ids, post_block_ids, streamlit_url)

    # ── Build scoring ──────────────────────────────────────────────
    scoring = _build_scoring(pretest_qid_map, PRETEST_ITEMS)

    # ── Build blocks element (BL) ──────────────────────────────────
    blocks_payload: dict[str, Any] = {}
    for block in blocks:
        blocks_payload[block["ID"]] = block

    # Add default Trash block
    blocks_payload["BL_trash"] = {
        "Type": "Trash",
        "Description": "Trash / Unused Questions",
        "ID": "BL_trash",
        "BlockElements": [],
        "Options": {},
    }

    # ── Assemble QSF ───────────────────────────────────────────────
    survey_elements: list[dict[str, Any]] = [
        # Block element
        {
            "SurveyID": "PLACEHOLDER",
            "Element": "BL",
            "PrimaryAttribute": "Survey Blocks",
            "SecondaryAttribute": None,
            "TertiaryAttribute": None,
            "Payload": blocks_payload,
        },
        # Flow element
        {
            "SurveyID": "PLACEHOLDER",
            "Element": "FL",
            "PrimaryAttribute": "Survey Flow",
            "SecondaryAttribute": None,
            "TertiaryAttribute": None,
            "Payload": flow,
        },
        # Survey options
        {
            "SurveyID": "PLACEHOLDER",
            "Element": "SO",
            "PrimaryAttribute": "Survey Options",
            "SecondaryAttribute": None,
            "TertiaryAttribute": None,
            "Payload": {
                "BackButton": "false",
                "SaveAndContinue": "true",
                "SurveyProtection": "PublicSurvey",
                "BallotBoxStuffingPrevention": "false",
                "NoIndex": "Yes",
                "SecureResponseFiles": "true",
                "SurveyExpiration": "None",
                "SurveyTermination": "DefaultMessage",
                "Header": "",
                "Footer": "",
                "ProgressBarDisplay": "None",
                "PartialData": "+1 week",
                "ValidationMessage": None,
                "PreviousButton": " ← ",
                "NextButton": " → ",
                "SurveyTitle": qconfig.SURVEY_NAME,
                "SkinLibrary": "fra1",
                "SkinType": "templated",
                "Skin": {"brandingId": None, "templateId": "*base"},
                "CollectGeoLocation": "false",
                "SurveyMetaDescription": (
                    "Pilot study on Socratic AI tutoring for causal inference"
                ),
                "PasswordProtection": "No",
                "AnonymizeResponse": "No",
                "RefererCheck": "No",
                "RefererURL": "http://",
                "RecaptchaV3": "false",
                "EOSMessage": None,
                "ShowExportTags": "false",
            },
        },
        # Scoring element
        {
            "SurveyID": "PLACEHOLDER",
            "Element": "SCO",
            "PrimaryAttribute": "Scoring",
            "SecondaryAttribute": None,
            "TertiaryAttribute": None,
            "Payload": scoring,
        },
    ]

    # Add all question elements
    survey_elements.extend(questions)

    qsf = {
        "SurveyEntry": {
            "SurveyID": "PLACEHOLDER",
            "SurveyName": qconfig.SURVEY_NAME,
            "SurveyDescription": None,
            "SurveyOwnerID": None,
            "SurveyBrandID": None,
            "DivisionID": None,
            "SurveyLanguage": "EN",
            "SurveyActiveResponseSet": "RS_default",
            "SurveyStatus": "Inactive",
            "SurveyStartDate": None,
            "SurveyExpirationDate": None,
            "SurveyCreationDate": None,
            "CreatorID": None,
            "LastModified": None,
            "LastAccessed": None,
            "LastActivated": None,
            "Deleted": None,
        },
        "SurveyElements": survey_elements,
    }

    # ── Write output ───────────────────────────────────────────────
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "survey.qsf"

    output_path.write_text(
        json.dumps(qsf, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"QSF generated: {output_path}")
    print(f"  Questions: {len(questions)}")
    print(f"  Blocks: {len(blocks)}")
    print(f"  Pre-survey blocks: {len(pre_block_ids)}")
    print(f"  Post-survey blocks: {len(post_block_ids)}")

    return output_path


if __name__ == "__main__":
    try:
        generate()
    except Exception as exc:
        print(f"Error generating QSF: {exc}", file=sys.stderr)
        sys.exit(1)

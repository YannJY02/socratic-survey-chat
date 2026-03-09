"""
Cognitive Load (CL) instruments and check items for the Socratic Survey Chat.

Implements the Klepsch scale (full 8-item and abbreviated 5-item variants)
as Streamlit Likert forms, plus attention, manipulation, and phenomenological
struggle check items.

Administration logic follows the frozen spec section 3.2:
- Admin 1 (after Phase A) = always full (8 items).
- Admin 2 (after Phase B) = always abbreviated (5 items).
- Check items are included only with CL-post-chat.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# CL Item definitions (Klepsch scale)
# ---------------------------------------------------------------------------

CL_ITEMS_FULL: list[dict] = [
    {
        "id": "ICL_1",
        "subscale": "ICL",
        "text": "The topics covered in this activity were very complex.",
    },
    {
        "id": "ICL_2",
        "subscale": "ICL",
        "text": "I had to deal with a lot of interrelated information during this activity.",
    },
    {
        "id": "ECL_1",
        "subscale": "ECL",
        "text": "During this activity, it was difficult to recognise and link the crucial information.",
    },
    {
        "id": "ECL_2",
        "subscale": "ECL",
        "text": "The design of this activity made it unnecessarily complex.",
    },
    {
        "id": "ECL_3",
        "subscale": "ECL",
        "text": "During this activity, it was difficult to decide which information was important and which was not.",
    },
    {
        "id": "GCL_1",
        "subscale": "GCL",
        "text": "During this activity, I made an effort to understand the material better.",
    },
    {
        "id": "GCL_2",
        "subscale": "GCL",
        "text": "I tried to connect the new knowledge with what I already knew.",
    },
    {
        "id": "OVERALL_1",
        "subscale": "OVERALL",
        "text": "How much mental effort did you invest in this activity overall?",
    },
]

CL_ITEMS_ABBREVIATED: list[dict] = [
    item for item in CL_ITEMS_FULL if item["subscale"] in ("ECL", "GCL")
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_cl_form(
    variant: str,
    include_checks: bool = False,
    condition: str = "",
) -> tuple[list[dict] | None, dict | None]:
    """Render a CL Likert 1-7 form inside a Streamlit form widget.

    Parameters
    ----------
    variant : str
        ``"full"`` for the 8-item Klepsch scale, ``"abbreviated"`` for the
        5-item ECL+GCL subset.
    include_checks : bool
        When ``True``, three check items (attention, manipulation,
        phenomenological struggle) are appended to the form.
    condition : str
        The experimental condition (``"I_PS"`` or ``"PS_I"``).  Required when
        *include_checks* is ``True`` so that the manipulation check can be
        scored.

    Returns
    -------
    tuple[list[dict] | None, dict | None]
        ``(cl_responses, checks)`` -- both ``None`` when the form has not yet
        been submitted.  *checks* is ``None`` when *include_checks* is
        ``False``.
    """
    items = CL_ITEMS_FULL if variant == "full" else CL_ITEMS_ABBREVIATED

    with st.form("cl_form"):
        st.subheader("Cognitive Load Questionnaire")
        st.markdown(
            "Please rate the following statements on a scale from "
            "1 (completely disagree) to 7 (completely agree)."
        )

        responses: dict[str, int | None] = {}
        for item in items:
            val = st.radio(
                item["text"],
                options=list(range(1, 8)),
                horizontal=True,
                key=f"cl_{item['id']}",
                index=None,  # no default selection
            )
            responses[item["id"]] = val

        # -- Optional check items ------------------------------------------
        attention: int | None = None
        manipulation: str | None = None
        struggle: int = 5

        if include_checks:
            st.divider()
            st.subheader("Additional Questions")

            attention = st.radio(
                "For this item, please select 5.",
                options=list(range(1, 8)),
                horizontal=True,
                key="check_attention",
                index=None,
            )
            manipulation = st.radio(
                "Which activity did you complete first?",
                options=[
                    "Explicit instruction module",
                    "AI problem-solving chat",
                    "I don't remember",
                ],
                key="check_manipulation",
                index=None,
            )
            struggle = st.slider(
                "How much did you feel you were struggling before receiving an explanation?",
                min_value=0,
                max_value=10,
                value=5,
                key="check_struggle",
            )

        submitted = st.form_submit_button("Submit")

    if not submitted:
        return None, None

    # -- Validation --------------------------------------------------------
    unanswered = [item_id for item_id, v in responses.items() if v is None]
    if unanswered:
        st.error("Please answer all questions before submitting.")
        return None, None

    cl_responses = [
        {"item_id": item_id, "value": val} for item_id, val in responses.items()
    ]

    checks: dict | None = None
    if include_checks:
        if attention is None or manipulation is None:
            st.error("Please answer all questions before submitting.")
            return None, None

        expected = (
            "Explicit instruction module"
            if condition == "I_PS"
            else "AI problem-solving chat"
        )
        checks = {
            "attention_check_passed": attention == 5,
            "manipulation_check_response": manipulation,
            "manipulation_check_correct": manipulation == expected,
            "phenomenological_struggle": struggle,
        }

    return cl_responses, checks

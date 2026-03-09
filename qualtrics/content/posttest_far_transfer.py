"""
Far-transfer test content for the Qualtrics post-survey.

Novel scenario (~250 words) in a non-media domain (organisational communication)
combining 2+ causal errors: third-variable confounding + differential attrition.

Participants must critically evaluate the researchers' conclusions in an
open-ended response.  Scoring is human-coded post-hoc using the provided rubric.
"""

POSTTEST_FAR_TRANSFER_BLOCK_NAME = "B5: Far-Transfer Application Test"

FAR_TRANSFER_SCENARIO = (
    "A large hospital network wanted to determine whether a new "
    "team-communication training programme improves patient safety outcomes. "
    "The programme was offered to all departments, and 12 departments "
    "volunteered to participate, while 8 departments declined. Over the "
    "following six months, the researchers tracked the number of reported "
    "medical errors in each department.\n\n"
    "At the end of the study, the 12 departments that completed the training "
    "had 35% fewer medical errors than the 8 departments that did not "
    "participate. However, during the six-month period, 3 of the 12 training "
    "departments experienced significant staff turnover: several experienced "
    "nurses left and were replaced by newly hired staff. These 3 departments "
    "were excluded from the final analysis because the researchers argued "
    "that staff turnover made their data 'unreliable.'\n\n"
    "Additionally, the researchers noted that the departments that "
    "volunteered for training tended to be larger departments with more "
    "resources and had already been implementing other quality-improvement "
    "initiatives before the study began.\n\n"
    "The researchers concluded: 'Our team-communication training programme "
    "significantly reduces medical errors. Hospitals should adopt this "
    "programme system-wide to improve patient safety.'"
)

FAR_TRANSFER_PROMPT = (
    "Critically evaluate the researchers' conclusions. In your response, "
    "identify the methodological problems with this study and explain how "
    "they affect the validity of the researchers' causal claim. Consider "
    "the study design, the way groups were formed, and any decisions the "
    "researchers made during the study."
)

FAR_TRANSFER_ITEMS = [
    {
        "id": "ft_scenario",
        "type": "Display",
        "text": FAR_TRANSFER_SCENARIO,
    },
    {
        "id": "ft_response",
        "type": "TextEntry",
        "subtype": "essay",
        "text": FAR_TRANSFER_PROMPT,
        "force_response": True,
        "validation": {"min_chars": 100},
    },
]

# ── Scoring rubric (for human coders — NOT displayed in Qualtrics) ─────

FAR_TRANSFER_RUBRIC = {
    "description": (
        "Score each response on the following dimensions. Each dimension is "
        "scored 0–2. Total score range: 0–8."
    ),
    "dimensions": [
        {
            "name": "Selection bias / non-random group formation",
            "description": (
                "Does the response identify that departments self-selected "
                "into training vs. control, making the groups non-equivalent?"
            ),
            "scores": {
                0: "Not mentioned.",
                1: (
                    "Mentioned but not fully explained (e.g., 'the groups "
                    "were different' without explaining why self-selection "
                    "matters)."
                ),
                2: (
                    "Clearly identifies that volunteer departments may "
                    "systematically differ from non-volunteers, undermining "
                    "the causal claim."
                ),
            },
        },
        {
            "name": "Third-variable confounding",
            "description": (
                "Does the response identify that pre-existing differences "
                "(larger departments, more resources, ongoing quality "
                "initiatives) could explain the outcome?"
            ),
            "scores": {
                0: "Not mentioned.",
                1: "Mentioned but not clearly linked to the outcome.",
                2: (
                    "Clearly explains how one or more confounding variables "
                    "could produce the observed difference without the "
                    "training being effective."
                ),
            },
        },
        {
            "name": "Differential attrition / selective exclusion",
            "description": (
                "Does the response identify that excluding 3 departments "
                "with staff turnover biases the results?"
            ),
            "scores": {
                0: "Not mentioned.",
                1: (
                    "Mentions the exclusion but does not explain how it "
                    "biases results."
                ),
                2: (
                    "Clearly explains that excluding departments with "
                    "unfavourable results (staff turnover likely worsened "
                    "outcomes) inflates the apparent effectiveness of "
                    "training."
                ),
            },
        },
        {
            "name": "Evaluation of the causal claim",
            "description": (
                "Does the response articulate why the overall causal "
                "conclusion is not supported?"
            ),
            "scores": {
                0: "Accepts the conclusion without critique.",
                1: (
                    "Questions the conclusion but provides limited "
                    "reasoning."
                ),
                2: (
                    "Clearly states that the study design does not support "
                    "a causal conclusion and connects this to the specific "
                    "problems identified."
                ),
            },
        },
    ],
}

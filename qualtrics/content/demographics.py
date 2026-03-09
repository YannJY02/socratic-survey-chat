"""
Demographics content for the Qualtrics pre-survey.

Standard Communication Science demographics (5-6 items) for the pilot study.
"""

DEMOGRAPHICS_BLOCK_NAME = "B2: Demographics"

DEMOGRAPHICS_ITEMS = [
    {
        "id": "demo_age",
        "type": "TextEntry",
        "subtype": "numeric",
        "text": "What is your age?",
        "validation": {"min": 16, "max": 99},
        "force_response": True,
    },
    {
        "id": "demo_gender",
        "type": "MC",
        "text": "What is your gender?",
        "choices": [
            {"value": "male", "label": "Male"},
            {"value": "female", "label": "Female"},
            {"value": "non_binary", "label": "Non-binary / third gender"},
            {"value": "prefer_not", "label": "Prefer not to say"},
        ],
        "force_response": True,
    },
    {
        "id": "demo_nationality",
        "type": "TextEntry",
        "subtype": "text",
        "text": "What is your nationality?",
        "force_response": True,
    },
    {
        "id": "demo_study_year",
        "type": "MC",
        "text": "What is your current study year?",
        "choices": [
            {"value": "ba1", "label": "Bachelor Year 1"},
            {"value": "ba2", "label": "Bachelor Year 2"},
            {"value": "ba3", "label": "Bachelor Year 3"},
            {"value": "ma1", "label": "Master Year 1"},
            {"value": "ma2", "label": "Master Year 2"},
            {"value": "other", "label": "Other"},
        ],
        "force_response": True,
    },
    {
        "id": "demo_methods_courses",
        "type": "MC",
        "text": (
            "How many research methods or statistics courses have you "
            "completed so far?"
        ),
        "choices": [
            {"value": "none", "label": "None"},
            {"value": "one", "label": "1"},
            {"value": "two_plus", "label": "2 or more"},
        ],
        "force_response": True,
    },
    {
        "id": "demo_comsci_major",
        "type": "MC",
        "text": "Is Communication Science your major?",
        "choices": [
            {"value": "yes", "label": "Yes"},
            {"value": "no", "label": "No"},
        ],
        "force_response": True,
    },
]

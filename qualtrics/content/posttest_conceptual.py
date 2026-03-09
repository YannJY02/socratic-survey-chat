"""
Conceptual understanding post-test items for the Qualtrics post-survey.

10 items covering C1–C4 (2–3 per concept). Mix of multiple-choice (MC) and
short-answer (SA).  These items do NOT overlap with the pretest — they test
deeper understanding and application rather than recognition.

MC items are auto-scored in Qualtrics; SA items are human-coded post-hoc.
"""

POSTTEST_CONCEPTUAL_BLOCK_NAME = "B4: Conceptual Understanding Post-Test"

POSTTEST_CONCEPTUAL_ITEMS = [
    # ── C1: Correlation vs. Causation (3 items) ───────────────────────
    {
        "id": "post_c1_1",
        "concept": "C1",
        "type": "MC",
        "text": (
            "A public health organisation reports that neighbourhoods with "
            "more fast-food restaurants have higher rates of obesity. A "
            "policy maker concludes that reducing the number of fast-food "
            "restaurants will lower obesity rates. Which of the following "
            "best explains why this conclusion may be flawed?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "The data only shows a correlation; lower-income "
                    "neighbourhoods may have both more fast-food restaurants "
                    "and higher obesity rates due to other factors."
                ),
            },
            {
                "value": "b",
                "label": (
                    "Obesity rates are too difficult to measure accurately."
                ),
            },
            {
                "value": "c",
                "label": (
                    "Fast-food restaurants always cause obesity in nearby "
                    "residents."
                ),
            },
            {
                "value": "d",
                "label": (
                    "The study must be wrong because fast food is popular "
                    "everywhere."
                ),
            },
        ],
        "correct": "a",
        "scoring_value": 1,
    },
    {
        "id": "post_c1_2",
        "concept": "C1",
        "type": "MC",
        "text": (
            "A technology company finds that employees who use standing "
            "desks report higher job satisfaction. The company plans to "
            "replace all desks with standing desks to improve morale. What "
            "is the most important assumption being made?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "That standing desks are more expensive than regular "
                    "desks."
                ),
            },
            {
                "value": "b",
                "label": (
                    "That the relationship between standing desks and job "
                    "satisfaction is causal rather than correlational."
                ),
            },
            {
                "value": "c",
                "label": (
                    "That job satisfaction cannot be measured accurately."
                ),
            },
            {
                "value": "d",
                "label": (
                    "That all employees prefer standing desks."
                ),
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "post_c1_3",
        "concept": "C1",
        "type": "SA",
        "text": (
            "A researcher finds that students who listen to music while "
            "studying get higher exam scores than students who study in "
            "silence. The researcher concludes that listening to music "
            "improves academic performance.\n\n"
            "In 2–3 sentences, explain why this conclusion is problematic "
            "and describe at least one alternative explanation for the "
            "observed pattern."
        ),
        "correct": None,  # Human-coded
        "scoring_rubric": (
            "Full credit (2): Identifies that correlation does not imply "
            "causation AND provides a plausible alternative explanation "
            "(e.g., students who listen to music may be more relaxed or "
            "have better study habits). "
            "Partial credit (1): Identifies correlation/causation issue OR "
            "provides an alternative explanation, but not both. "
            "No credit (0): Fails to identify the core issue."
        ),
        "scoring_value": 2,
    },
    # ── C2: Third-Variable Confounding (3 items) ──────────────────────
    {
        "id": "post_c2_1",
        "concept": "C2",
        "type": "MC",
        "text": (
            "A study reports that people who own pets have lower blood "
            "pressure than non-pet owners. A health columnist writes that "
            "getting a pet can lower your blood pressure. A methodologist "
            "suggests that lifestyle differences (e.g., income, activity "
            "level) between pet owners and non-owners might account for the "
            "finding. The methodologist is pointing out:"
        ),
        "choices": [
            {
                "value": "a",
                "label": "A measurement error in blood pressure readings.",
            },
            {
                "value": "b",
                "label": (
                    "That a confounding variable may explain the "
                    "association."
                ),
            },
            {
                "value": "c",
                "label": "That the sample was too small.",
            },
            {
                "value": "d",
                "label": "That pet ownership cannot be studied scientifically.",
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "post_c2_2",
        "concept": "C2",
        "type": "SA",
        "text": (
            "A university study finds that students who participate in "
            "extracurricular activities have higher GPAs than students who "
            "do not. The university's dean argues this proves that "
            "extracurricular involvement boosts academic performance.\n\n"
            "Identify a plausible confounding variable that could explain "
            "this relationship. Explain how this variable could be related "
            "to both extracurricular participation and GPA."
        ),
        "correct": None,  # Human-coded
        "scoring_rubric": (
            "Full credit (2): Identifies a plausible confound (e.g., "
            "self-discipline, socioeconomic status, motivation) AND "
            "explains how it relates to both variables. "
            "Partial credit (1): Identifies a plausible confound but does "
            "not adequately explain the dual pathway. "
            "No credit (0): Fails to identify a plausible confound."
        ),
        "scoring_value": 2,
    },
    {
        "id": "post_c2_3",
        "concept": "C2",
        "type": "MC",
        "text": (
            "Researchers observe that children who read more books have "
            "larger vocabularies. Which of the following would be the "
            "strongest evidence that reading CAUSES vocabulary growth, "
            "rather than this being explained by a third variable?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "A study finding the same pattern across different "
                    "countries."
                ),
            },
            {
                "value": "b",
                "label": (
                    "An experiment in which children are randomly assigned "
                    "to a reading programme or a control activity, and "
                    "vocabulary is measured before and after."
                ),
            },
            {
                "value": "c",
                "label": "A survey with a very large sample size.",
            },
            {
                "value": "d",
                "label": (
                    "A longitudinal study showing that the correlation "
                    "persists over time."
                ),
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    # ── C3: Random Assignment (2 items) ────────────────────────────────
    {
        "id": "post_c3_1",
        "concept": "C3",
        "type": "MC",
        "text": (
            "A pharmaceutical company tests a new drug by allowing patients "
            "to choose whether they want to take the drug or a placebo. "
            "Patients who chose the drug showed more improvement. Why does "
            "this study design weaken the causal conclusion?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "Because patients knew which treatment they received."
                ),
            },
            {
                "value": "b",
                "label": (
                    "Because self-selection means the two groups may differ "
                    "systematically in ways that affect the outcome (e.g., "
                    "severity of illness, motivation)."
                ),
            },
            {
                "value": "c",
                "label": "Because the placebo has no medical effect.",
            },
            {
                "value": "d",
                "label": "Because the sample size was not reported.",
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "post_c3_2",
        "concept": "C3",
        "type": "SA",
        "text": (
            "A school district wants to determine whether a new teaching "
            "method improves student test scores. They implement the new "
            "method in School A and keep the traditional method in School B, "
            "then compare results.\n\n"
            "Explain why this design does not allow a strong causal "
            "conclusion, and describe how random assignment could be used "
            "to improve the study."
        ),
        "correct": None,  # Human-coded
        "scoring_rubric": (
            "Full credit (2): Explains that intact groups may differ "
            "systematically (selection bias) AND describes how random "
            "assignment of individual students/classrooms to conditions "
            "would address this. "
            "Partial credit (1): Identifies the problem or the solution "
            "but not both. "
            "No credit (0): Does not address the core issue of "
            "non-equivalent groups."
        ),
        "scoring_value": 2,
    },
    # ── C4: Threats to Internal Validity (2 items) ─────────────────────
    {
        "id": "post_c4_1",
        "concept": "C4",
        "type": "MC",
        "text": (
            "A researcher measures employees' job performance before and "
            "after a company-wide wellness programme. Between the two "
            "measurements, the company also introduces a new bonus system. "
            "If job performance increases, the researcher cannot be certain "
            "it was due to the wellness programme because of:"
        ),
        "choices": [
            {
                "value": "a",
                "label": "Regression to the mean.",
            },
            {
                "value": "b",
                "label": (
                    "A history threat — the bonus system is a confounding "
                    "event that occurred between measurements."
                ),
            },
            {
                "value": "c",
                "label": "Maturation of the employees.",
            },
            {
                "value": "d",
                "label": "Testing effects from the pre-measurement.",
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "post_c4_2",
        "concept": "C4",
        "type": "MC",
        "text": (
            "In a study comparing two communication training approaches, "
            "30% of participants in the intensive training group drop out "
            "because they find it too demanding, while only 5% drop out of "
            "the standard training group. At the end of the study, the "
            "intensive group shows higher performance. Why should the "
            "researcher be cautious about concluding that intensive training "
            "is more effective?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "The sample sizes are now unequal, making statistics "
                    "unreliable."
                ),
            },
            {
                "value": "b",
                "label": (
                    "Differential attrition means the remaining intensive "
                    "group participants may be more motivated or capable "
                    "than a representative sample."
                ),
            },
            {
                "value": "c",
                "label": (
                    "The intensive training simply took longer."
                ),
            },
            {
                "value": "d",
                "label": (
                    "The dropout rate is within normal limits for training "
                    "studies."
                ),
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
]

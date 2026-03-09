"""
Pretest item pool for the Qualtrics pre-survey.

All 15 items transcribed from docs/rp/pretest-item-pool-draft.v2.md.
Each item has question text, 4 choices, and the correct answer marked
for auto-scoring in Qualtrics.

Domain concepts:
  C1 (Q1-Q4):  Correlation vs. causation
  C2 (Q5-Q8):  Third-variable confounding
  C3 (Q9-Q11): Random assignment
  C4 (Q12-Q15): Threats to internal validity
"""

PRETEST_BLOCK_NAME = "B3: Prior Knowledge Pretest"

PRETEST_ITEMS = [
    # ── C1: Correlation vs. Causation ──────────────────────────────────
    {
        "id": "pretest_q1",
        "concept": "C1",
        "type": "MC",
        "text": (
            "A study finds that cities with more ice cream shops also have "
            "higher crime rates. Which of the following is the most "
            "appropriate conclusion?"
        ),
        "choices": [
            {"value": "a", "label": "Ice cream shops cause crime."},
            {"value": "b", "label": "Crime causes ice cream shops to open."},
            {
                "value": "c",
                "label": (
                    "The two variables are correlated, but we cannot "
                    "determine a causal relationship from this data alone."
                ),
            },
            {
                "value": "d",
                "label": (
                    "There is no meaningful relationship between the two "
                    "variables."
                ),
            },
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q2",
        "concept": "C1",
        "type": "MC",
        "text": (
            'A researcher reports: "Students who attend tutoring sessions '
            "earn higher grades. Therefore, tutoring improves academic "
            'performance." What is the primary flaw in this reasoning?'
        ),
        "choices": [
            {"value": "a", "label": "The sample size is too small."},
            {
                "value": "b",
                "label": (
                    "The claim assumes a causal relationship from an "
                    "observed correlation."
                ),
            },
            {
                "value": "c",
                "label": (
                    "Tutoring and grades cannot be measured simultaneously."
                ),
            },
            {
                "value": "d",
                "label": "The study should have used qualitative methods.",
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q3",
        "concept": "C1",
        "type": "MC",
        "text": (
            'A newspaper reports: "A new survey finds that people who '
            "exercise regularly are 40% less likely to develop depression. "
            "Experts conclude that starting an exercise routine can prevent "
            'depression." What is the most important limitation of this '
            "conclusion?"
        ),
        "choices": [
            {
                "value": "a",
                "label": "A 40% reduction is too small to be meaningful.",
            },
            {
                "value": "b",
                "label": "The survey did not measure exercise intensity.",
            },
            {
                "value": "c",
                "label": (
                    "People who are less prone to depression may be more "
                    "likely to exercise, so the causal direction is unclear."
                ),
            },
            {
                "value": "d",
                "label": (
                    "The finding contradicts previous research on exercise "
                    "and mental health."
                ),
            },
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q4",
        "concept": "C1",
        "type": "MC",
        "text": (
            'A news report states: "Countries that spend more on education '
            "have higher GDP. Investing in education clearly boosts economic "
            'growth." Which statement best describes the problem with this '
            "claim?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "GDP cannot be measured accurately across countries."
                ),
            },
            {
                "value": "b",
                "label": "Education spending and GDP are not related.",
            },
            {
                "value": "c",
                "label": "The relationship is too weak to be meaningful.",
            },
            {
                "value": "d",
                "label": (
                    "The direction of causation is unclear; wealthier "
                    "countries may simply spend more on education."
                ),
            },
        ],
        "correct": "d",
        "scoring_value": 1,
    },
    # ── C2: Third-Variable Confounding ─────────────────────────────────
    {
        "id": "pretest_q5",
        "concept": "C2",
        "type": "MC",
        "text": (
            "A study finds that children who eat breakfast daily perform "
            "better on school tests. A critic suggests that family income "
            "might explain this relationship. In methodological terms, the "
            "critic is identifying:"
        ),
        "choices": [
            {"value": "a", "label": "A measurement error."},
            {"value": "b", "label": "A confounding variable."},
            {"value": "c", "label": "A sampling bias."},
            {"value": "d", "label": "A reliability problem."},
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q6",
        "concept": "C2",
        "type": "MC",
        "text": (
            "Researchers find a positive correlation between the number of "
            "fire trucks at a fire and the amount of property damage. What "
            "is the most likely explanation?"
        ),
        "choices": [
            {"value": "a", "label": "Fire trucks cause property damage."},
            {
                "value": "b",
                "label": (
                    "Property damage attracts fire trucks after the fire."
                ),
            },
            {
                "value": "c",
                "label": (
                    "A third variable \u2014 the severity of the fire \u2014 "
                    "explains both the number of trucks and the damage."
                ),
            },
            {
                "value": "d",
                "label": "The correlation is a statistical error.",
            },
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q7",
        "concept": "C2",
        "type": "MC",
        "text": (
            "In a study examining the link between social media use and "
            "loneliness, which of the following would be considered a "
            "confounding variable?"
        ),
        "choices": [
            {
                "value": "a",
                "label": "The brand of smartphone used by participants.",
            },
            {
                "value": "b",
                "label": "The time of day the survey was completed.",
            },
            {
                "value": "c",
                "label": (
                    "Introversion, which may increase both social media use "
                    "and loneliness."
                ),
            },
            {
                "value": "d",
                "label": "The colour scheme of the social media platform.",
            },
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q8",
        "concept": "C2",
        "type": "MC",
        "text": (
            "A researcher wants to test whether watching cooking shows leads "
            "to healthier eating. They compare the diets of people who "
            "regularly watch cooking shows with people who do not. A "
            'colleague warns that "health consciousness" could be a '
            "confound. Why?"
        ),
        "choices": [
            {
                "value": "a",
                "label": "Health consciousness is too difficult to measure.",
            },
            {
                "value": "b",
                "label": (
                    "Health consciousness only affects eating, not TV "
                    "watching."
                ),
            },
            {
                "value": "c",
                "label": (
                    "Health consciousness is the same thing as watching "
                    "cooking shows."
                ),
            },
            {
                "value": "d",
                "label": (
                    "Health-conscious people may be more likely to both "
                    "watch cooking shows and eat healthily, creating a "
                    "spurious link."
                ),
            },
        ],
        "correct": "d",
        "scoring_value": 1,
    },
    # ── C3: Random Assignment ──────────────────────────────────────────
    {
        "id": "pretest_q9",
        "concept": "C3",
        "type": "MC",
        "text": (
            "In a randomised experiment, participants are randomly assigned "
            "to conditions. The primary purpose of random assignment is to:"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "Ensure the sample is representative of the general "
                    "population."
                ),
            },
            {
                "value": "b",
                "label": "Increase the sample size of the study.",
            },
            {
                "value": "c",
                "label": (
                    "Distribute potential confounding variables equally "
                    "across groups."
                ),
            },
            {
                "value": "d",
                "label": "Make the experiment easier to replicate.",
            },
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q10",
        "concept": "C3",
        "type": "MC",
        "text": (
            "A researcher randomly assigns 100 participants to either read "
            "a news article online or in print, then measures comprehension. "
            "Why does random assignment strengthen the causal claim?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "It guarantees that both groups have the same number of "
                    "participants."
                ),
            },
            {
                "value": "b",
                "label": (
                    "It makes it unlikely that the groups differ "
                    "systematically on characteristics that could affect "
                    "comprehension."
                ),
            },
            {
                "value": "c",
                "label": (
                    "It ensures that participants cannot switch between "
                    "conditions."
                ),
            },
            {
                "value": "d",
                "label": (
                    "It eliminates the need for statistical analysis."
                ),
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q11",
        "concept": "C3",
        "type": "MC",
        "text": (
            "A researcher studying the effects of a new communication "
            "training programme compares employees who volunteered for the "
            "training with employees who chose not to participate. The "
            "researcher finds that trained employees perform better on a "
            "communication skills assessment. What is the main limitation "
            "of this conclusion?"
        ),
        "choices": [
            {
                "value": "a",
                "label": (
                    "The communication skills assessment is too subjective."
                ),
            },
            {
                "value": "b",
                "label": (
                    "Employees who volunteered may have been more motivated "
                    "or skilled to begin with, so the groups are not "
                    "comparable."
                ),
            },
            {
                "value": "c",
                "label": (
                    "The training programme was too short to have any effect."
                ),
            },
            {
                "value": "d",
                "label": "The study should have included more companies.",
            },
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    # ── C4: Threats to Internal Validity ───────────────────────────────
    {
        "id": "pretest_q12",
        "concept": "C4",
        "type": "MC",
        "text": (
            "In an experiment testing the effect of a media literacy "
            "programme, 20% of the control group drops out before the "
            "post-test, compared to only 5% of the treatment group. This "
            "pattern is an example of:"
        ),
        "choices": [
            {"value": "a", "label": "Measurement error."},
            {"value": "b", "label": "History effect."},
            {"value": "c", "label": "Differential attrition."},
            {"value": "d", "label": "Maturation."},
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q13",
        "concept": "C4",
        "type": "MC",
        "text": (
            "Researchers test the effect of a health campaign by measuring "
            "attitudes before and after the campaign. During the study "
            "period, a major health scandal makes national news. The scandal "
            "is an example of which threat to internal validity?"
        ),
        "choices": [
            {"value": "a", "label": "Selection bias."},
            {"value": "b", "label": "History effect."},
            {"value": "c", "label": "Instrumentation change."},
            {"value": "d", "label": "Testing effect."},
        ],
        "correct": "b",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q14",
        "concept": "C4",
        "type": "MC",
        "text": "Internal validity refers to:",
        "choices": [
            {
                "value": "a",
                "label": (
                    "Whether the results can be generalised to other "
                    "populations."
                ),
            },
            {
                "value": "b",
                "label": (
                    "Whether the measures used in the study are reliable."
                ),
            },
            {
                "value": "c",
                "label": (
                    "Whether the study can support the conclusion that the "
                    "independent variable caused the observed effect."
                ),
            },
            {
                "value": "d",
                "label": (
                    "Whether the study's findings are consistent with prior "
                    "research."
                ),
            },
        ],
        "correct": "c",
        "scoring_value": 1,
    },
    {
        "id": "pretest_q15",
        "concept": "C4",
        "type": "MC",
        "text": (
            "A researcher conducts a two-week experiment comparing two "
            "persuasion techniques. At the end of Week 1, the research "
            "assistant who scores the essays is replaced by a new assistant "
            "who applies the rubric more strictly. This is an example of:"
        ),
        "choices": [
            {"value": "a", "label": "Maturation."},
            {"value": "b", "label": "Selection bias."},
            {"value": "c", "label": "Instrumentation change."},
            {"value": "d", "label": "Regression to the mean."},
        ],
        "correct": "c",
        "scoring_value": 1,
    },
]

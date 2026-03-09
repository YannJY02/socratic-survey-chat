"""
Scenario definitions for the Socratic AI chat phase.

Each scenario presents a flawed research study that the student must
analyse with the help of the Socratic tutor.  The three scenarios are
ordered and target distinct causal-inference concepts.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    """An immutable research scenario used in the AI chat phase."""

    id: str
    order: int
    title: str
    target_concept: str
    text: str


CHAT_TASK_PROMPT: str = (
    "In this activity, you will read three short research scenarios one at a time. "
    "For each scenario, discuss with the AI tutor to critically evaluate the "
    "researchers\u2019 conclusions. Consider what the study design allows you to "
    "conclude and what alternative explanations might exist.\n\n"
    "There are no right or wrong answers \u2014 the goal is to think through "
    "the reasoning carefully."
)


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        id="S1",
        order=1,
        title="Social media and depressive symptoms",
        target_concept="Correlation vs. causation",
        text=(
            "A team of communication researchers investigated the relationship "
            "between a newly launched social media platform, \u201cConnectU,\u201d and "
            "depressive symptoms among young adults. They recruited 400 university "
            "students (aged 18\u201325) through campus advertisements and administered "
            "an online survey. The survey measured daily ConnectU usage (in minutes) "
            "\u2014 including both active use such as posting and commenting, and passive "
            "use such as scrolling \u2014 and depressive symptoms using the PHQ-9 scale. "
            "Participants also reported their general smartphone screen time.\n\n"
            "The results showed a statistically significant positive correlation "
            "(*r* = .34, *p* < .001): students who spent more time on ConnectU "
            "reported higher levels of depressive symptoms. There was no significant "
            "difference between active and passive users.\n\n"
            "In their discussion, the researchers concluded: \u201cOur findings "
            "demonstrate that ConnectU usage causes increased depressive symptoms "
            "among young adults. We recommend that universities implement screen-time "
            "interventions to reduce student depression rates.\u201d\n\n"
            "The study was conducted at a single time point with no follow-up "
            "measurement."
        ),
    ),
    Scenario(
        id="S2",
        order=2,
        title="Political debate viewing and political knowledge",
        target_concept="Third-variable confounding",
        text=(
            "A research group examined whether watching political debate programmes "
            "on television increases political knowledge among citizens. They surveyed "
            "600 adults recruited from community centres and public libraries across "
            "urban and rural areas in the Netherlands. The survey measured (a) how "
            "frequently respondents watched televised political debates (weekly hours) "
            "and (b) their score on a 20-item political knowledge quiz. The sample "
            "included adults from a wide range of occupational and socioeconomic "
            "backgrounds.\n\n"
            "The results revealed a strong positive association: respondents who "
            "watched more political debates scored significantly higher on the "
            "political knowledge quiz (*r* = .41, *p* < .001). The researchers "
            "concluded: \u201cWatching political debate programmes is an effective way "
            "to increase citizens\u2019 political knowledge. Public broadcasters should "
            "invest in more debate programming to strengthen democratic literacy.\u201d\n\n"
            "No participants were assigned to watch or abstain from watching debates; "
            "the data were collected through a single cross-sectional survey."
        ),
    ),
    Scenario(
        id="S3",
        order=3,
        title="Prosocial media and empathy",
        target_concept="Selection bias",
        text=(
            "A media psychology lab investigated whether exposure to prosocial media "
            "content increases empathy among adolescents. The researchers partnered "
            "with two secondary schools in Amsterdam. At School A, all participating "
            "students (n = 45) watched a series of short prosocial video clips over "
            "two weeks during their media literacy class. At School B, all "
            "participating students (n = 42) followed their regular media literacy "
            "curriculum without the video clips. After two weeks, both groups "
            "completed the Interpersonal Reactivity Index (IRI), a standardised "
            "empathy scale.\n\n"
            "Students at School A scored significantly higher on empathy than "
            "students at School B (*t*(85) = 2.67, *p* = .009, *d* = 0.57). The "
            "researchers concluded: \u201cProsocial media exposure causes meaningful "
            "increases in empathy among adolescents. Schools should integrate "
            "prosocial media content into their curricula.\u201d\n\n"
            "The researchers noted that random assignment of individual students to "
            "conditions was \u201cnot feasible due to logistical constraints.\u201d"
        ),
    ),
)

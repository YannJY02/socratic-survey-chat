"""
Instruction module content for the causal-inference learning material.

The text is rendered as Streamlit markdown in the instruction phase.
"""

INSTRUCTION_TEXT: str = r"""
## Why Causal Inference Matters

Communication scientists routinely make claims about cause and effect: does media coverage influence public opinion? Does social media use affect well-being? These questions sit at the heart of our discipline, but answering them correctly demands rigorous reasoning. A flawed causal claim can mislead policymakers, distort public understanding, and waste research resources. This module introduces four foundational concepts that will help you evaluate whether a study's causal claims are justified.

## Concept 1: Correlation Does Not Imply Causation

Two variables can move together — both increasing or both decreasing — without one causing the other. This co-movement is called a **correlation**. A **causal relationship** requires something stronger: a change in one variable must *produce* a change in the other.

Consider a study reporting that people who watch more news also report higher anxiety. The data show a positive correlation, but several explanations are possible: news exposure may cause anxiety, anxiety may drive people to seek out news, or a third factor (such as a stressful life event) may cause both. Without additional evidence, we cannot select among these alternatives.

**Key principle:** Observational data — data collected without experimental manipulation — can establish that two variables are associated but cannot, by itself, establish that one causes the other.

**Where reasoning goes wrong:**
- *"The correlation is strong, so it must be causal."* Strength of association says nothing about causal direction. A strong correlation between ice cream sales and drowning rates does not mean ice cream causes drowning — summer weather drives both.
- *"We found a statistically significant relationship, so X causes Y."* Statistical significance means the association is unlikely due to chance. It does not rule out confounds or reverse causation.
- *Contrast with correct reasoning:* A valid causal claim requires ruling out alternative explanations — reverse causation, third-variable confounding — not merely demonstrating a strong or significant correlation.

## Concept 2: Third-Variable Confounding

A **confound** (or confounding variable) is a variable that is associated with *both* the presumed cause and the presumed effect, creating a spurious appearance of a causal link between them.

### Causal-Pathway Diagram 1: Confounding

```
    Confound (Z)
       / \
      v   v
  Cause (X) --?--> Effect (Y)

The arrow from X to Y is uncertain. The confound Z
influences both X and Y, making it impossible to
determine whether X truly causes Y.
```

If a study finds that children who play violent video games behave more aggressively, a confound such as *parental supervision* could explain the association: children with less supervision may both play more violent games *and* behave more aggressively, regardless of any direct game-to-aggression link.

**Key principle:** Whenever a study claims X causes Y, ask: "Is there a third variable that could explain both X and Y?"

**Where reasoning goes wrong:**
- *"We controlled for one confound, so the relationship is causal."* Controlling for one variable does not rule out all others. There may be additional unmeasured confounds (Westfall & Yarkoni, 2016).
- *"The confound is unlikely because we cannot think of one."* Failure to imagine a confound does not mean one does not exist. In observational research, unmeasured confounders are always possible.
- *Contrast with correct reasoning:* A causal claim from observational data requires either controlling for *all plausible* confounds (rarely achievable) or employing a design that eliminates confounding by construction (e.g., randomisation).

## Concept 3: The Logic of Random Assignment

**Random assignment** is the methodological tool that allows researchers to make causal claims. When participants are randomly allocated to conditions (e.g., "watch a violent clip" vs. "watch a neutral clip"), every confounding variable — measured or unmeasured — is, on average, equally distributed across groups. Any subsequent difference in the outcome can therefore be attributed to the manipulation rather than to pre-existing group differences.

### Causal-Pathway Diagram 2: How Randomisation Breaks Confounding

```
WITHOUT random assignment:       WITH random assignment:

    Z                                Z
   / \                              / \
  v   v                            /   \
  X --?--> Y                      X     Y
                                  |
                          (randomly manipulated)
                                  |
                                  v
                                  Y

Randomisation severs the Z → X link, so any
difference in Y can be attributed to X.
```

**Key principle:** Random assignment breaks the link between confounds and the treatment variable, enabling valid causal inference. Without it, observed group differences may reflect pre-existing characteristics rather than the effect of the treatment.

**Where reasoning goes wrong:**
- *"The two groups were similar on demographics, so they are comparable."* Matching on observed variables does not eliminate confounding from *unobserved* variables. Only randomisation balances both observed and unobserved confounds.
- *"Random assignment and random sampling are the same thing."* Random *sampling* determines who is selected from the population (affects generalisability). Random *assignment* determines who receives which treatment (affects internal validity). A study can have one without the other.
- *Contrast with correct reasoning:* Random assignment is uniquely powerful because it addresses confounders you have not measured or even imagined, not just the ones you have identified.

## Concept 4: Threats to Internal Validity

**Internal validity** is the degree to which a study can support a causal conclusion. Even in experiments with random assignment, design flaws can undermine causal claims. Common threats include:

- **Selection bias:** Participants in different conditions differ systematically at baseline (especially problematic in non-randomised designs or when randomisation fails due to small samples).
- **Attrition (differential dropout):** If participants drop out of one condition more than another, the remaining groups are no longer comparable.
- **History effects:** An external event occurring during the study affects one group differently.
- **Maturation:** Natural changes over time (e.g., learning, fatigue) are mistaken for treatment effects.

**Key principle:** A well-designed study anticipates and controls for these threats. When evaluating research, ask: "What could have gone wrong *besides* the intended manipulation to produce this result?"

**Where reasoning goes wrong:**
- *"The study used random assignment, so it must have high internal validity."* Randomisation establishes initial comparability, but post-randomisation events (attrition, contamination, history effects) can erode it. Internal validity requires maintaining group comparability throughout the entire study.
- *"The results are statistically significant, so the design must be sound."* A significant p-value does not validate the research design. A flawed study can produce significant results that are entirely artefactual.
- *Contrast with correct reasoning:* Internal validity is assessed by evaluating the research *design* — how participants were assigned, whether groups remained comparable, whether extraneous events were controlled — not by evaluating the *results*.

---

## Worked Example 1: Identifying Confounding in Advertising Research

**Study description:** A marketing research team surveyed 800 adults and found that respondents who recalled seeing advertisements for a new health drink scored higher on a brand-preference scale than those who did not recall the ads. The researchers concluded: "Advertising exposure causes increased brand preference. Companies should increase their advertising budgets to boost consumer preference."

**Analysis:**

1. **Design:** This is a cross-sectional observational study. There is no random assignment; the researchers compared people who naturally differed in ad recall.
2. **Correlation vs. causation:** The data show a positive association between ad recall and brand preference, but correlation alone does not establish causation.
3. **Possible confound:** People with a pre-existing interest in health products may be more likely to both *notice* health-drink advertisements and *prefer* the brand — a third-variable confound. Additionally, ad recall may reflect general media engagement rather than ad effectiveness (reverse causation pathway).
4. **Where the reasoning goes wrong vs. correct reasoning:**
   - *Faulty:* "Those who recalled the ad prefer the brand more, therefore the ad changed their preference."
   - *Correct:* "The observed association could be explained by pre-existing interest, selective attention, or other confounds. A randomised experiment assigning ad exposure would be needed to test the causal claim."

## Worked Example 2: Evaluating an Experiment with an Internal Validity Threat

**Study description:** A research team randomly assigns 60 participants to watch either a fear-appeal health message or a neutral message, then measures intention to quit smoking one week later. However, 15 of the 30 participants in the fear-appeal condition drop out before the follow-up measurement, compared to only 3 in the neutral condition.

**Analysis:**

1. **Design:** This is a randomised experiment, so the initial group composition is balanced.
2. **Threat:** Differential attrition. Those who dropped out of the fear-appeal group may be systematically different — perhaps they were the heaviest smokers who found the message too distressing.
3. **Consequence:** The remaining fear-appeal participants are no longer representative of the original randomly assigned group. Comparing the two groups at follow-up is like comparing a self-selected subset of the fear-appeal group with the nearly intact neutral group.
4. **Where the reasoning goes wrong vs. correct reasoning:**
   - *Faulty:* "Randomisation was used, so the groups are comparable. The fear-appeal group showed higher quit intentions."
   - *Correct:* "Randomisation established initial comparability, but the differential dropout destroyed it. The surviving fear-appeal participants may have been predisposed to quitting. The internal validity of the causal claim is compromised."
""".strip()

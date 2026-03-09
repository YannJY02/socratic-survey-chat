"""
Informed consent content for the Qualtrics pre-survey.

Standard UvA Communication Science informed consent covering study purpose,
procedures, AI tutoring disclosure, data handling (GDPR), and right to withdraw.
"""

CONSENT_BLOCK_NAME = "B1: Informed Consent"

CONSENT_TEXT = (
    "<h2>Informed Consent Form</h2>"
    "<p><strong>Study Title:</strong> The Effects of Instructional Sequencing "
    "in a Socratic AI Tutoring Environment on Cognitive Load and Learning "
    "Outcomes</p>"
    "<p><strong>Institution:</strong> University of Amsterdam, Faculty of Social "
    "and Behavioural Sciences, Department of Communication Science</p>"
    "<p><strong>Researcher:</strong> Jinyi Yang<br>"
    "Email: jinyi.yang@student.uva.nl<br>"
    "Supervisor: Saurabh Khanna</p>"
    "<hr>"
    "<h3>Purpose of the Study</h3>"
    "<p>You are invited to participate in a research study investigating how "
    "different instructional sequences affect learning about causal inference "
    "in communication research. During this study, you will interact with an "
    "AI-powered tutoring system that uses a Socratic questioning approach to "
    "guide your learning.</p>"
    "<h3>What Will You Do?</h3>"
    "<p>If you agree to participate, you will:</p>"
    "<ol>"
    "<li>Complete a short pre-survey (demographics and a brief knowledge "
    "test) — approximately 8 minutes</li>"
    "<li>Engage in an online learning session consisting of reading "
    "instructional material and discussing research scenarios with an AI "
    "tutor — approximately 30 minutes</li>"
    "<li>Complete a post-survey (knowledge test and debriefing) — "
    "approximately 20 minutes</li>"
    "</ol>"
    "<p>The total estimated duration is 50–65 minutes. Please complete the "
    "session in one sitting.</p>"
    "<h3>AI Tutoring Disclosure</h3>"
    "<p>During the learning session, you will interact with an AI-powered "
    "conversational tutor. The AI tutor is designed to ask guiding questions "
    "rather than provide direct answers. Your conversations with the AI tutor "
    "will be recorded for research purposes.</p>"
    "<h3>Data Collection and Privacy (GDPR)</h3>"
    "<p>This study collects the following data:</p>"
    "<ul>"
    "<li>Survey responses (demographics, knowledge tests)</li>"
    "<li>Chat transcripts from the AI tutoring session</li>"
    "<li>Timing data (how long you spend on each section)</li>"
    "<li>Self-report questionnaire responses about your learning experience</li>"
    "</ul>"
    "<p>All data will be processed in accordance with the EU General Data "
    "Protection Regulation (GDPR). Your data will be:</p>"
    "<ul>"
    "<li><strong>Pseudonymised:</strong> Your responses are linked to a "
    "randomly assigned participant ID, not to your name or student number.</li>"
    "<li><strong>Stored securely:</strong> Data is stored on encrypted, "
    "password-protected servers at the University of Amsterdam.</li>"
    "<li><strong>Used for research only:</strong> Data will be used solely "
    "for academic research and may be published in anonymised, aggregated "
    "form.</li>"
    "<li><strong>Retained:</strong> Research data will be retained for a "
    "minimum of 10 years in accordance with UvA research data management "
    "policy.</li>"
    "</ul>"
    "<h3>Voluntary Participation and Right to Withdraw</h3>"
    "<p>Your participation is entirely voluntary. You may withdraw at any "
    "time during the study without providing a reason and without any negative "
    "consequences. If you withdraw, your data collected up to that point may "
    "still be used in anonymised form unless you request otherwise.</p>"
    "<p>To withdraw during the learning session, click the "
    "<strong>'Exit study'</strong> button available in the sidebar.</p>"
    "<h3>Risks and Benefits</h3>"
    "<p>There are no known risks beyond those of normal educational "
    "activities. You may benefit from learning about research methodology "
    "through the tutoring session. Your participation contributes to "
    "research on effective AI-assisted learning.</p>"
    "<h3>Contact</h3>"
    "<p>If you have questions about this study, please contact:<br>"
    "Jinyi Yang — jinyi.yang@student.uva.nl</p>"
    "<p>If you have questions about your rights as a research participant, "
    "you may contact the Ethics Review Board of the Faculty of Social and "
    "Behavioural Sciences, University of Amsterdam: "
    "<a href='mailto:ethics-fsw@uva.nl'>ethics-fsw@uva.nl</a></p>"
)

CONSENT_QUESTION = {
    "id": "consent",
    "type": "MC",
    "text": (
        "I have read and understood the information above. I understand that "
        "my participation is voluntary and that I may withdraw at any time. "
        "I consent to participate in this study."
    ),
    "choices": [
        {"value": "consent", "label": "I consent to participate"},
        {"value": "no_consent", "label": "I do not consent to participate"},
    ],
    "force_response": True,
    "skip_logic": {
        "condition": "no_consent",
        "action": "end_survey",
        "message": (
            "Thank you for your time. Since you have chosen not to "
            "participate, the survey will now end. You may close this window."
        ),
    },
}

CONSENT_ITEMS = [CONSENT_QUESTION]

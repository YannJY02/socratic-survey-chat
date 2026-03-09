"""
Socratic Tutor — Streamlit chat application.

This app is part of an educational-research study.  Participants interact
with a Socratic AI tutor powered by an LLM backend (Ollama or OpenAI).
The app routes participants through a condition-dependent sequence of
phases per the frozen spec (2026-03-09).

Usage
-----
    streamlit run app.py

The app expects ``pid`` and ``condition`` query parameters in the URL
(supplied by the Qualtrics pre-survey redirect).
"""

from datetime import datetime, timezone

import streamlit as st

import config
import phases
from phases import Phase

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(page_title=config.APP_TITLE, page_icon="📚")


# ── Helper functions ────────────────────────────────────────────────────────

def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _parse_query_params() -> tuple[str, str]:
    """Extract ``pid`` and ``condition`` from the URL query string."""
    params = st.query_params
    pid: str = params.get("pid", "unknown")
    condition: str = params.get("condition", "I_PS")
    return pid, condition


# ── Session-state initialisation ────────────────────────────────────────────

def _init_session() -> None:
    """Initialise all session-state keys on first run."""
    if "initialised" in st.session_state:
        return

    pid, condition = _parse_query_params()

    # Validate condition; default to I_PS for unknown values.
    if condition not in phases.CONDITION_SEQUENCES:
        condition = phases.DEFAULT_CONDITION

    st.session_state.pid = pid
    st.session_state.condition = condition
    st.session_state.session_start = _utc_now_iso()
    st.session_state.withdrawn = False
    st.session_state.finished = False

    # Phase state-machine.
    st.session_state.current_phase_index = 0
    st.session_state.phase_log = []

    # Scenario chat state.
    st.session_state.current_scenario_index = 0
    st.session_state.scenario_messages = [[], [], []]  # S1, S2, S3
    st.session_state.scenarios = []  # accumulated scenario log entries

    # CL + check data.
    st.session_state.cl_responses = {}  # {post_chat: [...], post_instruction: [...]}
    st.session_state.checks = {}

    # Start the first phase.
    phases.start_first_phase(st.session_state)

    st.session_state.initialised = True


# ── Phase handlers ─────────────────────────────────────────────────────────


def _build_system_prompt(scenario_text: str) -> str:
    """Load the domain prompt template and inject the active scenario text."""
    template = (config.BASE_DIR / "prompts" / "socratic_domain.txt").read_text(
        encoding="utf-8",
    )
    return template.replace("[SCENARIO_TEXT]", scenario_text)


def render_welcome_phase() -> None:
    """Render the welcome / task introduction page."""
    st.subheader("Welcome")
    st.markdown(
        "Welcome to this learning activity about **causal inference in "
        "communication research**.\n\n"
        "In this session, you will:\n"
        "- Read instructional material about research methodology\n"
        "- Discuss research scenarios with an AI tutor\n"
        "- Answer a few short questionnaires\n\n"
        "The entire session takes approximately 30\u201340 minutes. "
        "Please complete it in one sitting."
    )
    if st.button("Begin", key="btn_welcome"):
        phases.advance_phase(st.session_state)
        st.rerun()


def render_instruction_phase() -> None:
    """Render the instruction module page with causal-inference content."""
    from content.instruction import INSTRUCTION_TEXT

    st.subheader("Causal Inference in Communication Research")
    with st.container():
        st.markdown(INSTRUCTION_TEXT)
    if st.button("Continue", key="btn_instruction"):
        phases.advance_phase(st.session_state)
        st.rerun()


def render_chat_phase() -> None:
    """Render the 3-scenario Socratic AI chat interface."""
    from content.scenarios import CHAT_TASK_PROMPT, SCENARIOS

    scenario_idx: int = st.session_state.current_scenario_index
    scenario = SCENARIOS[scenario_idx]

    # ── Task guidance (shown once, before S1, before any messages) ─
    messages: list[dict] = st.session_state.scenario_messages[scenario_idx]
    if scenario_idx == 0 and not messages:
        st.info(CHAT_TASK_PROMPT)

    # ── Scenario description ─────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"**Scenario {scenario.order}: {scenario.title}**")
        st.markdown(scenario.text)

    # ── Per-scenario message history ─────────────────────────────────

    # Display existing messages.
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Turn accounting ──────────────────────────────────────────────
    student_turns = sum(1 for m in messages if m["role"] == "user")
    turns_remaining = config.TURNS_PER_SCENARIO - student_turns

    def _save_and_advance_scenario() -> None:
        """Save the current scenario log entry and advance to next scenario or phase."""
        st.session_state.scenarios.append({
            "scenario_id": scenario.id,
            "scenario_order": scenario.order,
            "scenario_start": (
                messages[0]["timestamp"] if messages else _utc_now_iso()
            ),
            "scenario_end": _utc_now_iso(),
            "student_turns": student_turns,
            "messages": messages,
        })
        if scenario_idx < 2:
            st.session_state.current_scenario_index += 1
        else:
            phases.advance_phase(st.session_state)
        st.rerun()

    if turns_remaining <= 0:
        # All turns used — show transition controls.
        st.info(
            f"You have used all {config.TURNS_PER_SCENARIO} messages "
            "for this scenario.",
        )
        label = "Continue to next scenario" if scenario_idx < 2 else "Continue"
        key = f"btn_next_scenario_{scenario_idx}" if scenario_idx < 2 else "btn_chat_done"
        if st.button(label, key=key):
            _save_and_advance_scenario()
    else:
        st.caption(f"Messages remaining for this scenario: {turns_remaining}")
        # ── Early exit (after minimum engagement) ─────────────────
        if student_turns >= config.MIN_TURNS_PER_SCENARIO:
            if st.button("I'm ready to move on", key=f"btn_early_exit_{scenario_idx}"):
                _save_and_advance_scenario()

    # ── Chat input (only while turns remain) ─────────────────────────
    if turns_remaining > 0:
        if user_input := st.chat_input("Type your message\u2026"):
            messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": _utc_now_iso(),
            })
            with st.chat_message("user"):
                st.markdown(user_input)

            # Build the LLM message list with the domain system prompt.
            system_prompt = _build_system_prompt(scenario.text)
            llm_messages = [
                {"role": "system", "content": system_prompt},
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ]

            import llm
            with st.chat_message("assistant"):
                placeholder = st.empty()
                response = llm.stream_chat(
                    llm_messages,
                    placeholder,
                    backend=st.session_state.get("dev_backend"),
                    model=st.session_state.get("dev_model"),
                    temperature=st.session_state.get("dev_temperature"),
                    api_key=st.session_state.get("dev_api_key"),
                )
            messages.append({
                "role": "assistant",
                "content": response.full_text,
                "timestamp": _utc_now_iso(),
                "token_count": response.token_count,
                "latency_ms": response.latency_ms,
            })


def render_cl_phase(phase_type: str) -> None:
    """Render a CL inventory phase.

    Parameters
    ----------
    phase_type : str
        Either ``"post_chat"`` or ``"post_instruction"``.
    """
    from instruments import render_cl_form

    condition = st.session_state.condition
    sequence = phases.get_phase_sequence(condition)

    # Determine if this is the first or second CL administration.
    # First admin = full (8 items), second admin = abbreviated (5 items).
    cl_phases = [
        p for p in sequence if p in (Phase.CL_POST_INSTRUCTION, Phase.CL_POST_CHAT)
    ]
    current_phase_enum = (
        Phase.CL_POST_CHAT if phase_type == "post_chat" else Phase.CL_POST_INSTRUCTION
    )
    is_first_admin = cl_phases.index(current_phase_enum) == 0
    variant = "full" if is_first_admin else "abbreviated"

    # Checks are included only for post-chat CL.
    include_checks = phase_type == "post_chat"

    label = "Post-Chat" if phase_type == "post_chat" else "Post-Instruction"
    st.subheader(f"Cognitive Load Measurement ({label})")

    cl_responses, checks = render_cl_form(
        variant=variant,
        include_checks=include_checks,
        condition=condition,
    )

    if cl_responses is not None:
        st.session_state.cl_responses[phase_type] = cl_responses
        if checks is not None:
            st.session_state.checks = checks
        phases.advance_phase(st.session_state)
        st.rerun()


def render_redirect() -> None:
    """Render the final redirect page and save the session log."""
    import logger

    st.subheader("Thank You!")
    st.success("You have completed all phases. Your data has been saved.")

    # Close the final phase entry and save.
    if not st.session_state.finished:
        if st.session_state.phase_log:
            st.session_state.phase_log[-1]["phase_end"] = _utc_now_iso()
        filepath = logger.save_session(st.session_state)
        st.session_state.finished = True
        st.caption(f"Session log: {filepath.name}")

    redirect_url = (
        config.QUALTRICS_POST_SURVEY_URL.format(
            pid=st.session_state.pid,
            condition=st.session_state.condition,
        )
        + "&phase_completed=true"
    )
    st.markdown(
        f'<meta http-equiv="refresh" content="3;URL=\'{redirect_url}\'">',
        unsafe_allow_html=True,
    )
    st.info("Redirecting you to the post-session survey...")


# ── Main UI ─────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point — render the Streamlit interface."""
    _init_session()

    phase = phases.current_phase(st.session_state)
    sequence = phases.get_phase_sequence(st.session_state.condition)
    total_phases = len(sequence)
    current_idx = st.session_state.current_phase_index

    # ── Sidebar: session info + progress ────────────────────────────────
    with st.sidebar:
        st.markdown(f"**Participant:** `{st.session_state.pid}`")
        st.markdown(f"**Condition:** `{st.session_state.condition}`")
        st.markdown(f"**Current phase:** {phase.value}")
        st.progress(min(current_idx / total_phases, 1.0))

        # ── Dev-mode controls ────────────────────────────────────────
        if config.DEV_MODE:
            st.divider()
            st.markdown("**Dev Controls**")
            st.session_state.dev_backend = st.selectbox(
                "Backend",
                ["ollama", "openai"],
                index=["ollama", "openai"].index(
                    st.session_state.get("dev_backend", config.BACKEND)
                ),
                key="sel_dev_backend",
            )
            st.session_state.dev_model = st.text_input(
                "Model",
                value=st.session_state.get("dev_model", config.MODEL),
                key="inp_dev_model",
            )
            if st.session_state.dev_backend == "openai":
                st.session_state.dev_api_key = st.text_input(
                    "OpenAI API key",
                    type="password",
                    value=st.session_state.get("dev_api_key", ""),
                    key="inp_dev_api_key",
                )
            st.session_state.dev_temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get("dev_temperature", config.TEMPERATURE),
                step=0.1,
                key="sld_dev_temperature",
            )

        # Withdrawal mechanism (visible throughout all phases except redirect).
        if phase != Phase.REDIRECT and not st.session_state.finished:
            st.divider()
            if st.button("Exit study", type="secondary", key="btn_withdraw"):
                import logger

                st.session_state.withdrawn = True
                if st.session_state.phase_log:
                    st.session_state.phase_log[-1]["phase_end"] = _utc_now_iso()
                logger.save_session(st.session_state)
                st.session_state.finished = True

                redirect_url = config.QUALTRICS_DEBRIEFING_URL.format(
                    pid=st.session_state.pid,
                )
                st.markdown(
                    f'<meta http-equiv="refresh" content="2;URL=\'{redirect_url}\'">',
                    unsafe_allow_html=True,
                )
                st.info("Redirecting to debriefing...")
                st.stop()

    # ── Phase dispatch ──────────────────────────────────────────────────
    match phase:
        case Phase.WELCOME:
            render_welcome_phase()
        case Phase.INSTRUCTION:
            render_instruction_phase()
        case Phase.AI_CHAT:
            render_chat_phase()
        case Phase.CL_POST_INSTRUCTION:
            render_cl_phase("post_instruction")
        case Phase.CL_POST_CHAT:
            render_cl_phase("post_chat")
        case Phase.REDIRECT:
            render_redirect()


if __name__ == "__main__":
    main()

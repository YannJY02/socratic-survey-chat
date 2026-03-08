"""
Socratic Tutor — Streamlit chat application.

This app is part of an educational-research study.  Students interact
with a Socratic AI tutor powered by a locally-hosted LLM (via Ollama).  Conversation data is logged for
subsequent analysis.

Usage
-----
    streamlit run app.py

The app expects a ``pid`` query parameter in the URL (supplied by
Qualtrics) and an optional ``condition`` parameter for A/B testing.
"""

from datetime import datetime, timezone

import requests
import streamlit as st

import config
import logger

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(page_title=config.APP_TITLE, page_icon="📚")


# ── Helper functions ────────────────────────────────────────────────────────

def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _load_system_prompt() -> str:
    """Read the system prompt from the text file defined in config."""
    return config.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def _parse_query_params() -> tuple[str, str]:
    """
    Extract ``pid`` and ``condition`` from the URL query string.

    Returns
    -------
    tuple[str, str]
        (participant_id, condition_label)
    """
    params = st.query_params
    pid: str = params.get("pid", "unknown")
    condition: str = params.get("condition", "default")
    return pid, condition


def _count_student_turns() -> int:
    """Count the number of user messages in the current session."""
    return sum(1 for m in st.session_state.messages if m["role"] == "user")


def _stream_ollama_response(messages: list[dict]) -> str:
    """
    Send the conversation to Ollama and stream the assistant reply
    token-by-token into the Streamlit chat UI.

    Parameters
    ----------
    messages : list[dict]
        The full conversation in OpenAI-style format
        (``role`` / ``content`` pairs).

    Returns
    -------
    str
        The complete assistant response.
    """
    url = f"{config.OLLAMA_HOST}/api/chat"
    payload = {
        "model": config.MODEL,
        "messages": messages,
        "stream": True,
    }

    full_response = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            with requests.post(url, json=payload, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    import json
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    full_response += token
                    placeholder.markdown(full_response + "▌")
        except requests.ConnectionError:
            full_response = (
                "I'm sorry — I cannot reach the language model right now. "
                "Please make sure Ollama is running and try again."
            )
        except requests.HTTPError as exc:
            full_response = (
                f"The language model returned an error (HTTP {exc.response.status_code}). "
                "Please check that the model is loaded in Ollama."
            )
        except requests.Timeout:
            full_response = (
                "The request to the language model timed out. "
                "Please try again in a moment."
            )
        placeholder.markdown(full_response)

    return full_response


def _save_and_redirect() -> None:
    """Persist the conversation log and redirect to the Qualtrics post-survey."""
    filepath = logger.save_conversation(
        pid=st.session_state.pid,
        condition=st.session_state.condition,
        messages=st.session_state.messages,
        session_start=st.session_state.session_start,
    )
    st.success(f"Conversation saved ({filepath.name}).")

    redirect_url = config.QUALTRICS_POST_SURVEY_URL.format(pid=st.session_state.pid)
    st.markdown(
        f'<meta http-equiv="refresh" content="2;URL=\'{redirect_url}\'">',
        unsafe_allow_html=True,
    )
    st.info("Redirecting you to the post-session survey…")


# ── Session-state initialisation ────────────────────────────────────────────

def _init_session() -> None:
    """Initialise all session-state keys on first run."""
    if "initialised" in st.session_state:
        return

    pid, condition = _parse_query_params()
    system_prompt = _load_system_prompt()

    st.session_state.pid = pid
    st.session_state.condition = condition
    st.session_state.session_start = _utc_now_iso()
    st.session_state.finished = False

    # The messages list stores the visible conversation.  The system
    # prompt is prepended when calling the model but is not displayed.
    st.session_state.system_prompt = system_prompt
    st.session_state.messages = []  # list[dict] — visible conversation history

    st.session_state.initialised = True


# ── Main UI ─────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point — render the Streamlit interface."""
    _init_session()

    st.title(config.APP_TITLE)
    st.caption(config.INFORMED_CONSENT_NOTICE)
    st.markdown(config.APP_DESCRIPTION)

    # Display existing chat history.
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # If the session has been finished, show the redirect and stop.
    if st.session_state.finished:
        st.warning("This session has ended. You should be redirected shortly.")
        return

    # Check whether the student has reached the turn limit.
    turns_used = _count_student_turns()
    turns_remaining = config.MAX_TURNS - turns_used

    if turns_remaining <= 0:
        st.info(
            "You have reached the maximum number of messages for this session. "
            "Please click the button below to continue to the post-session survey."
        )
    else:
        st.caption(f"Messages remaining: {turns_remaining}")

    # ── Sidebar: finish button ──────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"**Participant:** `{st.session_state.pid}`")
        st.markdown(f"**Condition:** `{st.session_state.condition}`")
        st.markdown(f"**Turns used:** {turns_used} / {config.MAX_TURNS}")
        if st.button("Finish & Go to Post-Survey"):
            st.session_state.finished = True
            _save_and_redirect()
            st.rerun()

    # ── Chat input ──────────────────────────────────────────────────────
    if turns_remaining > 0:
        if user_input := st.chat_input("Type your message…"):
            # Record the student message with a timestamp.
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": _utc_now_iso(),
            })
            with st.chat_message("user"):
                st.markdown(user_input)

            # Build the payload for Ollama (system prompt + conversation).
            ollama_messages = [
                {"role": "system", "content": st.session_state.system_prompt},
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            # Stream the assistant response.
            assistant_reply = _stream_ollama_response(ollama_messages)
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_reply,
                "timestamp": _utc_now_iso(),
            })


if __name__ == "__main__":
    main()

"""Streamlit test UI for the local RAG backend."""

from __future__ import annotations

from html import escape
import os
from typing import Any

import requests
import streamlit as st

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
STARTER_PROMPTS = [
    "What is the refund policy for a cancelled booking?",
    "How do I fix WhatsApp notification issues?",
    "Can I change the time of my court booking?",
    "What should court owners do when a slot is unavailable?",
]

st.set_page_config(
    page_title="Phasers Support Copilot",
    page_icon=":tennis:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --page-bg: #050505;
        --page-glow: rgba(255, 255, 255, 0.06);
        --panel-bg: rgba(15, 15, 18, 0.92);
        --panel-strong: rgba(19, 19, 24, 0.98);
        --panel-soft: rgba(255, 255, 255, 0.045);
        --ink: #f5f7fb;
        --muted: #98a1b3;
        --line: rgba(255, 255, 255, 0.14);
        --line-strong: rgba(255, 255, 255, 0.25);
        --accent: #ffffff;
        --accent-soft: rgba(255, 255, 255, 0.08);
        --user-bg: rgba(255, 255, 255, 0.06);
        --warn-soft: rgba(255, 214, 102, 0.12);
        --shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
    }

    .stApp {
        background:
            radial-gradient(circle at top, rgba(255, 255, 255, 0.08), transparent 32%),
            linear-gradient(180deg, #111111 0%, #070707 28%, var(--page-bg) 100%);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        height: 3rem;
        background: transparent;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none;
    }

    [data-testid="stSidebar"] {
        background: #0a0a0d;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: var(--muted);
    }

    .block-container {
        max-width: 960px;
        padding-top: 3.2rem;
        padding-bottom: 8rem;
    }

    .hero {
        border: 1px solid var(--line);
        border-radius: 32px;
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02)),
            var(--panel-strong);
        padding: 2.6rem 2rem 1.9rem;
        margin: 0 auto 1rem;
        box-shadow: var(--shadow);
        overflow: hidden;
        text-align: center;
        position: relative;
    }

    .brand-lockup {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }

    .brand-mark {
        width: 84px;
        height: 84px;
        border: 1.5px solid rgba(255, 255, 255, 0.92);
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.08em;
        background: rgba(255, 255, 255, 0.02);
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
    }

    .hero h1 {
        color: var(--ink);
        font-size: 2.45rem;
        line-height: 1.02;
        margin: 0;
        letter-spacing: -0.06em;
        font-weight: 650;
    }

    .hero p {
        color: var(--muted);
        font-size: 0.98rem;
        line-height: 1.6;
        margin: 0.1rem auto 0;
        max-width: 610px;
    }

    .hero-meta {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1rem;
    }

    .hero-meta span {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--line);
        border-radius: 999px;
        color: #d9deea;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 0.38rem 0.72rem;
        letter-spacing: 0.01em;
    }

    .quick-actions-shell {
        margin: 1.05rem 0 0.8rem;
        padding: 1rem 1rem 1.1rem;
        border-radius: 24px;
        border: 1px solid var(--line);
        background: var(--panel-bg);
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
    }

    .quick-actions {
        margin: 0;
    }

    .quick-actions p {
        color: var(--muted);
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0 0 0.8rem;
    }

    .stButton > button {
        border: 1px solid var(--line);
        border-radius: 18px;
        color: #edf2ff;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.015));
        min-height: 2.6rem;
        padding: 0.58rem 0.8rem;
        transition: all 150ms ease;
        white-space: normal;
        font-size: 0.9rem;
        box-shadow: none;
    }

    .stButton > button:hover {
        border-color: var(--line-strong);
        color: #ffffff;
        transform: translateY(-1px);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.025));
    }

    .chat-shell {
        margin-top: 0.55rem;
    }

    .message-row {
        display: flex;
        gap: 0.9rem;
        align-items: flex-start;
        margin-bottom: 0.9rem;
    }

    .message-row.user {
        flex-direction: row-reverse;
    }

    .message-avatar {
        flex: 0 0 46px;
        width: 46px;
        height: 46px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.045);
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: -0.04em;
    }

    .message-row.user .message-avatar {
        background: rgba(255, 255, 255, 0.09);
        color: #e7ebf5;
    }

    .message-body {
        flex: 1 1 auto;
        border-radius: 24px;
        border: 1px solid var(--line);
        background: var(--panel-bg);
        padding: 1rem 1.05rem;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
    }

    .message-row.user .message-body {
        background: var(--user-bg);
    }

    .message-role {
        color: #e8ecf7;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .message-content {
        color: var(--ink);
        line-height: 1.65;
        font-size: 0.98rem;
    }

    .message-content p {
        margin: 0;
    }

    .message-content p + p {
        margin-top: 0.75rem;
    }

    [data-testid="stChatInput"] {
        max-width: 960px;
        margin: 0 auto;
        min-height: 3.35rem !important;
    }

    [data-testid="stChatInput"] > div {
        min-height: 3.35rem !important;
        padding: 0.45rem 0.5rem !important;
        position: relative;
        border-radius: 24px !important;
        background: rgba(10, 10, 12, 0.98) !important;
        border: 1px solid var(--line) !important;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        color: var(--ink) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 18px !important;
        height: 2.55rem !important;
        min-height: 2.55rem !important;
        max-height: 5.5rem !important;
        padding-right: 3.4rem !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(255, 255, 255, 0.28) !important;
        box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.05) !important;
    }

    [data-testid="stChatInput"] button {
        position: absolute !important;
        right: 0.8rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        margin: 0 !important;
        border-radius: 16px !important;
        background: #ffffff !important;
        color: #050505 !important;
        border: none !important;
        min-width: 2.65rem !important;
        height: 2.65rem !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.03);
    }

    .debug-note {
        border-left: 4px solid #ffffff;
        background: var(--warn-soft);
        padding: 0.85rem 0.95rem;
        border-radius: 16px;
        color: #f7e4a5;
        margin-top: 0.65rem;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
            padding-top: 2.8rem;
        }

        .hero {
            padding: 1.8rem 1rem 1.35rem;
            border-radius: 28px;
        }

        .brand-mark {
            width: 72px;
            height: 72px;
            border-radius: 20px;
            font-size: 1.7rem;
        }

        .hero h1 {
            font-size: 1.8rem;
            line-height: 1.08;
        }

        .hero p {
            font-size: 0.9rem;
        }

        .hero-meta {
            gap: 0.45rem;
        }

        .quick-actions-shell {
            padding: 0.85rem 0.85rem 0.95rem;
        }

        .stButton > button {
            min-height: 2.5rem;
            padding: 0.45rem 0.65rem;
            font-size: 0.84rem;
        }

        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }

        [data-testid="stChatInput"] {
            width: calc(100vw - 1.5rem);
        }

        [data-testid="column"] {
            width: 100% !important;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            flex-basis: 40px;
            border-radius: 14px;
        }

        .message-body {
            border-radius: 20px;
            padding: 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def backend_url() -> str:
    """Return the normalized backend URL from sidebar state."""
    return st.session_state.backend_url.rstrip("/")


def get_health() -> dict[str, Any]:
    """Fetch backend health."""
    response = requests.get(f"{backend_url()}/health", timeout=20)
    response.raise_for_status()
    return response.json()


def ask_backend(message: str, debug: bool, top_k: int = 3) -> dict[str, Any]:
    """Send a chat turn to the backend."""
    response = requests.post(
        f"{backend_url()}/api/v1/support/chat",
        json={"message": message, "top_k": top_k, "debug": debug},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def render_message(role: str, content: str) -> None:
    """Render one branded chat message."""
    avatar = "P" if role == "assistant" else "You"
    label = "Phasers Support Copilot" if role == "assistant" else "You"
    css_role = "assistant" if role == "assistant" else "user"
    safe_content = escape(content).replace("\n", "<br>")
    st.markdown(
        (
            f'<div class="message-row {css_role}">'
            f'<div class="message-avatar">{avatar}</div>'
            f'<div class="message-body">'
            f'<div class="message-role">{label}</div>'
            f'<div class="message-content">{safe_content}</div>'
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I can help with bookings, payments, refunds, cancellations, "
                "account questions, and troubleshooting."
            ),
        }
    ]
if "backend_url" not in st.session_state:
    st.session_state.backend_url = DEFAULT_BACKEND_URL

if "starter_prompt" not in st.session_state:
    st.session_state.starter_prompt = ""


def reset_chat() -> None:
    """Reset chat to the welcome state."""
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I can help with bookings, payments, refunds, "
                "cancellations, account questions, and troubleshooting."
            ),
        }
    ]


with st.sidebar:
    st.markdown("### Workspace")
    st.caption("Connect to the local FastAPI backend and tune retrieval.")
    st.text_input("Backend URL", key="backend_url", help="FastAPI service URL")
    debug = st.toggle("Show debug traces", value=False)
    top_k = 3
    if debug:
        top_k = st.slider("Retrieved chunks", min_value=1, max_value=10, value=3)

    st.divider()
    if st.button("Check health", use_container_width=True, type="primary"):
        try:
            health = get_health()
            st.success("Backend responded")
            st.json(health)
        except requests.RequestException as exc:
            st.error(f"Health check failed: {exc}")

    if st.button("Clear chat", use_container_width=True):
        reset_chat()
        st.rerun()

st.markdown(
    """
    <section class="hero">
        <div class="brand-lockup">
            <div class="brand-mark">P</div>
            <h1>Phasers Support Copilot</h1>
            <p>
                Refined support for bookings, payments, refunds, cancellations,
                account help, notifications, and owner workflows.
            </p>
            <div class="hero-meta">
                <span>Support chat</span>
                <span>Policy grounded</span>
                <span>Optional debug traces</span>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="quick-actions-shell"><div class="quick-actions"><p>Try a common question</p></div></div>',
    unsafe_allow_html=True,
)
prompt_cols = st.columns(2)
for index, starter in enumerate(STARTER_PROMPTS):
    with prompt_cols[index % 2]:
        if st.button(starter, use_container_width=True):
            st.session_state.starter_prompt = starter

st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
for message in st.session_state.messages:
    render_message(message["role"], message["content"])
st.markdown("</div>", unsafe_allow_html=True)

typed_prompt = st.chat_input("Ask a support question")
prompt = typed_prompt.strip() if typed_prompt else ""
if st.session_state.starter_prompt:
    prompt = st.session_state.starter_prompt
    st.session_state.starter_prompt = ""

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    with st.spinner("Searching the knowledge base..."):
        try:
            result = ask_backend(prompt, debug=debug, top_k=top_k)
            render_message("assistant", result["answer"])
            if debug:
                st.markdown(
                    (
                        '<div class="debug-note">'
                        f"Route: <strong>{result['route']}</strong> | "
                        f"Router: <strong>{result.get('routing_backend', 'unknown')}</strong> | "
                        f"Model: <strong>{result['model']}</strong> | "
                        f"Elapsed: <strong>{result['elapsed_seconds']:.2f}s</strong>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                if result.get("sources"):
                    st.caption("Sources: " + ", ".join(result["sources"]))
                for chunk in result.get("retrieved_chunks", []):
                    label = (
                        f"{chunk['source']} / {chunk['chunk_id']} "
                        f"/ score {chunk['score']:.4f}"
                    )
                    with st.expander(label):
                        if chunk.get("section"):
                            st.write(f"Section: {chunk['section']}")
                        st.write(chunk["text"])

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                }
            )
        except requests.HTTPError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            st.error(f"Backend error: {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")

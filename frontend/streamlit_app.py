"""Streamlit test UI for the local RAG backend."""

from __future__ import annotations

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
    page_title="Embeds Support Copilot",
    page_icon=":tennis:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --page-bg: #f5f7fa;
        --panel-bg: #ffffff;
        --ink: #172033;
        --muted: #5c6b82;
        --line: #dde3ec;
        --accent: #0f766e;
        --accent-strong: #115e59;
        --accent-soft: #e1f5f1;
        --warn-soft: #fff7df;
    }

    .stApp {
        background: linear-gradient(180deg, #fbfcfe 0%, var(--page-bg) 48%, #eef2f7 100%);
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
        background: #ffffff;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: var(--muted);
    }

    .block-container {
        max-width: 1040px;
        padding-top: 3.75rem;
        padding-bottom: 8rem;
    }

    .hero {
        border: 1px solid var(--line);
        border-radius: 8px;
        background:
            linear-gradient(135deg, rgba(15, 118, 110, 0.13), rgba(56, 189, 248, 0.11)),
            #ffffff;
        padding: 1rem 1.2rem;
        margin: 0 0 0.9rem;
        box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
        overflow: hidden;
    }

    .hero h1 {
        color: var(--ink);
        font-size: 1.8rem;
        line-height: 1.12;
        margin: 0;
        letter-spacing: 0;
    }

    .hero p {
        color: var(--muted);
        font-size: 0.96rem;
        line-height: 1.45;
        margin: 0.45rem 0 0;
        max-width: 760px;
    }

    .hero-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.8rem;
    }

    .hero-meta span {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--ink);
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0.35rem 0.65rem;
    }

    .quick-actions {
        margin: 0.75rem 0 0.75rem;
    }

    .quick-actions p {
        color: var(--muted);
        font-size: 0.9rem;
        margin: 0 0 0.45rem;
    }

    .stButton > button {
        border: 1px solid #d5dbe5;
        border-radius: 8px;
        color: var(--ink);
        background: #ffffff;
        min-height: 3rem;
        padding: 0.55rem 0.75rem;
        transition: all 120ms ease;
        white-space: normal;
    }

    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent-strong);
        box-shadow: 0 8px 22px rgba(15, 118, 110, 0.10);
    }

    [data-testid="stChatMessage"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
        margin-bottom: 0.75rem;
        padding: 0.85rem 1rem;
    }

    [data-testid="stChatMessage"] p {
        color: var(--ink);
        line-height: 1.55;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #f0fdfa;
        border-color: #bfe8df;
    }

    [data-testid="stChatInput"] {
        max-width: 940px;
        margin: 0 auto;
        min-height: 3.25rem !important;
    }

    [data-testid="stChatInput"] > div {
        min-height: 3.25rem !important;
        padding: 0.35rem 0.45rem !important;
        position: relative;
    }

    [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        color: var(--ink) !important;
        border: 1px solid #cfd7e3 !important;
        border-radius: 8px !important;
        height: 2.45rem !important;
        min-height: 2.45rem !important;
        max-height: 5.5rem !important;
        padding-right: 3rem !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.12) !important;
    }

    [data-testid="stChatInput"] button {
        position: absolute !important;
        right: 0.75rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        margin: 0 !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #ffffff;
    }

    .debug-note {
        border-left: 4px solid var(--accent);
        background: var(--warn-soft);
        padding: 0.75rem 0.9rem;
        border-radius: 8px;
        color: #713f12;
        margin-top: 0.65rem;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
            padding-top: 3.5rem;
        }

        .hero {
            padding: 0.8rem 0.95rem;
        }

        .hero h1 {
            font-size: 1.5rem;
            line-height: 1.18;
        }

        .hero p,
        .hero-meta {
            display: none;
        }

        .quick-actions {
            margin: 0.45rem 0 0.35rem;
        }

        .stButton > button {
            min-height: 2.7rem;
            padding: 0.45rem 0.6rem;
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
        <h1>Embeds Support Copilot</h1>
        <p>
            Ask clear support questions and get grounded answers for bookings,
            payments, refunds, cancellations, accounts, notifications, and court owner workflows.
        </p>
        <div class="hero-meta">
            <span>Support chat</span>
            <span>Policies + guides</span>
            <span>Optional debug traces</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="quick-actions"><p>Try a common question</p></div>', unsafe_allow_html=True)
prompt_cols = st.columns(2)
for index, starter in enumerate(STARTER_PROMPTS):
    with prompt_cols[index % 2]:
        if st.button(starter, use_container_width=True):
            st.session_state.starter_prompt = starter

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

typed_prompt = st.chat_input("Ask a support question")
prompt = typed_prompt.strip() if typed_prompt else ""
if st.session_state.starter_prompt:
    prompt = st.session_state.starter_prompt
    st.session_state.starter_prompt = ""

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"), st.spinner("Searching the knowledge base..."):
        try:
            result = ask_backend(prompt, debug=debug, top_k=top_k)
            st.markdown(result["answer"])
            if debug:
                st.markdown(
                    (
                        '<div class="debug-note">'
                        f"Route: <strong>{result['route']}</strong> | "
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

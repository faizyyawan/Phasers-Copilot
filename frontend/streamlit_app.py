"""Streamlit test UI for the local RAG backend."""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="Embeds Support Copilot",
    page_icon="",
    layout="wide",
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

with st.sidebar:
    st.header("Settings")
    st.text_input("Backend URL", key="backend_url")
    debug = st.checkbox("Show debug traces", value=False)
    top_k = 3
    if debug:
        top_k = st.slider("Retrieved chunks", min_value=1, max_value=10, value=3)

    if st.button("Check health", use_container_width=True):
        try:
            health = get_health()
            st.success("Backend responded")
            st.json(health)
        except requests.RequestException as exc:
            st.error(f"Health check failed: {exc}")

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I can help with bookings, payments, refunds, "
                    "cancellations, account questions, and troubleshooting."
                ),
            }
        ]
        st.rerun()

st.title("Embeds Support Copilot")
st.caption("Ask about bookings, payments, refunds, cancellations, or account help.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a support question")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"), st.spinner("Thinking..."):
        try:
            result = ask_backend(prompt, debug=debug, top_k=top_k)
            st.markdown(result["answer"])
            if debug:
                st.caption(
                    f"Route: {result['route']} | "
                    f"Model: {result['model']} | "
                    f"Elapsed: {result['elapsed_seconds']:.2f}s"
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

"""
Jaguar AI - Streamlit Edition
A clean, web-based chat assistant that connects to an LLM (OpenAI or a
local Ollama model), with optional PDF summarization / document Q&A.

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
from llm_client import ask, LLMError

# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Jaguar AI",
    page_icon="🐆",
    layout="centered",
)

DEFAULT_SYSTEM_PROMPT = (
    "You are Jaguar AI, a helpful, concise personal assistant. "
    "Answer clearly and directly."
)

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": ..., "content": ...}

if "doc_text" not in st.session_state:
    st.session_state.doc_text = None
    st.session_state.doc_name = None

# ---------------------------------------------------------------------
# Sidebar - provider / model settings
# ---------------------------------------------------------------------
with st.sidebar:
    st.title("🐆 Jaguar AI")
    st.caption("Settings")

    provider = st.selectbox("LLM Provider", ["OpenAI", "Ollama (local)"])

    if provider == "OpenAI":
        api_key = st.text_input(
            "OpenAI API key",
            value=os.environ.get("OPENAI_API_KEY", ""),
            type="password",
            help="Stored only for this session, never written to disk.",
        )
        model = st.text_input("Model", value="gpt-4o-mini")
        ollama_host = None
    else:
        api_key = ""
        model = st.text_input("Model", value="llama3")
        ollama_host = st.text_input(
            "Ollama host (optional)",
            value=os.environ.get("OLLAMA_HOST", ""),
            placeholder="http://localhost:11434",
        )

    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)

    system_prompt = st.text_area(
        "System prompt",
        value=DEFAULT_SYSTEM_PROMPT,
        height=90,
    )

    st.divider()
    st.caption("📄 Document Q&A (optional)")
    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded is not None and uploaded.name != st.session_state.doc_name:
        try:
            import fitz  # PyMuPDF

            pdf = fitz.open(stream=uploaded.read(), filetype="pdf")
            text = "".join(page.get_text() for page in pdf)
            st.session_state.doc_text = text[:15000]
            st.session_state.doc_name = uploaded.name
            st.success(f"Loaded '{uploaded.name}' ({len(text)} chars)")
        except Exception as e:
            st.error(f"Could not read PDF: {e}")

    if st.session_state.doc_text:
        col1, col2 = st.columns(2)
        if col1.button("Summarize doc"):
            st.session_state.pending_prompt = (
                f"Summarize the following document:\n\n{st.session_state.doc_text}"
            )
        if col2.button("Clear doc"):
            st.session_state.doc_text = None
            st.session_state.doc_name = None

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------
st.title("Jaguar AI")
st.caption("Your personal AI assistant, now in the browser.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle a prompt queued by a sidebar button (e.g. "Summarize doc")
queued_prompt = st.session_state.pop("pending_prompt", None)
user_prompt = st.chat_input("Message Jaguar AI...")

prompt = queued_prompt or user_prompt

if prompt:
    is_doc_summary = queued_prompt is not None
    display_text = "📄 Summarize uploaded document" if is_doc_summary else prompt

    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    history = [{"role": "system", "content": system_prompt}]
    # If a document is loaded, give the model light context so it can
    # answer follow-up questions (not just the initial summarize request).
    if st.session_state.doc_text:
        history.append({
            "role": "system",
            "content": f"Reference document ({st.session_state.doc_name}):\n{st.session_state.doc_text}",
        })
    history += st.session_state.messages[-10:-1]
    history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = ask(
                provider,
                history,
                api_key=api_key,
                model=model,
                temperature=temperature,
                stream=True,
                ollama_host=ollama_host or None,
            )
            for chunk in stream:
                full_response += chunk
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except LLMError as e:
            full_response = f"⚠️ {e}"
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"⚠️ Unexpected error: {e}"
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

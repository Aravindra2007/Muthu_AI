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
import base64
from datetime import datetime

# ---------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Muthu AI",
    page_icon="icon.png",
    layout="centered",
)

# ---------------------------------------------------------------------
# BACKGROUND + UI DESIGN
# ---------------------------------------------------------------------
def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
                              url("data:image/jpg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Hide default UI */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Glass effect container */
        .block-container {{
            backdrop-filter: blur(10px);
        }}

        /* Chat bubbles */
        .stChatMessage {{
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
            box-shadow: 0 0 10px rgba(0,255,255,0.2);
        }}

        /* Input box */
        .stChatInput > div {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
        }}

        /* Title glow */
        h1 {{
            text-align: center;
            color: #00FFFF;
            text-shadow: 0 0 20px #00FFFF;
        }}

        /* Typing cursor animation */
        .typing {{
            border-right: 2px solid #00FFFF;
            animation: blink 1s infinite;
        }}

        @keyframes blink {{
            0% {{ border-color: transparent; }}
            50% {{ border-color: #00FFFF; }}
            100% {{ border-color: transparent; }}
        }}

        /* Mic pulse animation */
        .mic {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: rgba(0,255,255,0.2);
            margin: 10px auto;
            animation: pulse 1.5s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 0.7; }}
            50% {{ transform: scale(1.2); opacity: 1; }}
            100% {{ transform: scale(1); opacity: 0.7; }}
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# 👉 your JPG file
set_bg("back.jpg")

def get_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64("logo.jpg")

st.sidebar.markdown(
    f"""
    <div style="text-align:center;">
        <img src="data:image/jpg;base64,{img_base64}" 
             style="width:120px;height:120px;border-radius:50%;
             object-fit:cover;border:3px solid #00FFFF;
             box-shadow:0 0 20px #00FFFF;">
        <h2 style="color:white;">Muthu AI</h2>
    </div>
    """,
    unsafe_allow_html=True
)

DEFAULT_SYSTEM_PROMPT = (
    "You are Muthu AI, a helpful, concise personal assistant. "
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
    st.title(" Muthu AI")
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
now = datetime.now()
current_time = now.strftime("%I:%M %p")   # 12-hour format
current_date = now.strftime("%A, %d %B %Y")

st.markdown(
    f"""
    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:5px 10px;
        margin-bottom:5px;
        background: rgba(255,255,255,0.08);
        border-radius:10px;
        font-size:14px;
        color:#00FFFF;
        box-shadow:0 0 10px rgba(0,255,255,0.2);
    ">
        <span>🗓️ {current_date}</span>
        <span>⏰ {current_time}</span>
    </div>
    """,
    unsafe_allow_html=True
)


st.title("Muthu AI")
st.caption("Your personal AI assistant, now in the browser.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle a prompt queued by a sidebar button (e.g. "Summarize doc")
queued_prompt = st.session_state.pop("pending_prompt", None)

user_prompt = st.chat_input("Message Muthu AI...")



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




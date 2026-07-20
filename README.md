#  Muthu AI

**A clean, web-based AI chat assistant that runs on your terms — cloud-powered or fully offline.**

Muthu AI is a lightweight [Streamlit](https://streamlit.io) chat app that connects to either OpenAI's models or a **local Ollama model**, so you can chat with an LLM without ever sending your data to the cloud. It also supports PDF upload and document Q&A, letting you summarize or ask questions about your own files.

---

## ✨ Features

- 💬 **Simple, familiar chat UI** — built with Streamlit's native chat components
- 🌐 **Dual provider support** — switch between OpenAI (cloud) and Ollama (local, offline) from the sidebar
- 🔌 **Fully offline mode** — pair with [Ollama](https://ollama.com) and models like `llama3` to chat without an internet connection or API key
- 📄 **PDF document Q&A** — upload a PDF, get an instant summary, or ask follow-up questions about its contents
- 🎛️ **Configurable generation** — adjust temperature, system prompt, and model per session
- 🔒 **Session-only credentials** — API keys are never written to disk
- 🧹 **One-click chat/document reset**

---

## 🖥️ Demo Preview

```
🐆 Muthu AI
Your personal AI assistant, now in the browser.

> Summarize the attached document
🤖 Here's a concise summary of the key points...
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Aravindra2007/Muthu_AI.git
cd Muthu_AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## ⚙️ Configuration

Muthu AI supports two providers, selectable from the sidebar:

| Provider | Requirements | Notes |
|---|---|---|
| **OpenAI** | An OpenAI API key | Set via the sidebar or the `OPENAI_API_KEY` environment variable |
| **Ollama (local)** | [Ollama](https://ollama.com) installed and running | Fully offline; set a custom host via `OLLAMA_HOST` if needed |

### Environment variables (optional)

```bash
export OPENAI_API_KEY="sk-..."
export OLLAMA_HOST="http://localhost:11434"
```

### Running fully offline

1. Install [Ollama](https://ollama.com) and pull a model:
   ```bash
   ollama pull llama3
   ```
2. Launch the app and select **Ollama (local)** as the provider.
3. Chat away — no internet connection required after setup.

---

## 📄 Document Q&A

Upload a PDF from the sidebar to:
- Get an instant **summary** with one click
- Ask **follow-up questions** — the document text is kept as context for the rest of the conversation

Powered by [PyMuPDF](https://pymupdf.readthedocs.io/) for fast, accurate text extraction.

---

## 🗂️ Project Structure

```
Muthu_AI/
├── app.py             # Streamlit UI, chat loop, sidebar settings, PDF handling
├── llm_client.py       # Provider-agnostic LLM client (OpenAI + Ollama)
├── requirements.txt    # Python dependencies
├── LICENSE              # MIT License
└── README.md
```

---

## 🧩 How It Works

`app.py` renders the chat interface and manages session state (messages, uploaded document, settings). Every user message is routed through `llm_client.py`'s `ask()` function, which dispatches the request to either `ask_openai()` or `ask_ollama()` depending on the selected provider — both support streaming responses so replies appear token by token.

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- [OpenAI Python SDK](https://github.com/openai/openai-python) — cloud LLM access
- [Ollama](https://github.com/ollama/ollama) — local LLM runtime
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a pull request

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for details.

---

<p align="center">Built with 🐆 for anyone who wants a chat assistant that works — online or off.</p>

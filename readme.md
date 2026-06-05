# 🧠 Feynman's Twin

> An AI-powered digital twin of Richard Feynman that combines Agentic RAG, Long-Term Memory, Persona Retrieval, and Voice Interaction to explain complex ideas through intuition, analogies, and first-principles reasoning.

Feynman's Twin is not a simple chatbot. It is an agentic AI system designed to simulate how Richard Feynman would think, reason, and teach.

The system builds two independent knowledge spaces:

* **Knowledge Space** → Scientific facts, books, papers, Wikipedia articles, and lecture transcripts.
* **Persona Space** → Feynman's communication style, teaching philosophy, analogies, interviews, and reasoning patterns.

Using LangGraph, retrieval pipelines, memory systems, reflection loops, and Gemini 2.5 Flash, the agent generates responses that are both factually grounded and stylistically consistent with Feynman's teaching approach.

---

## 🎥 Demo

A sample demonstration is available below:

[Watch Demo](https://youtu.be/hI0J52DZLcw)

---

# ✨ Key Features

### 🧠 Dual-RAG Architecture

Two independent FAISS vector databases power the system:

| Database        | Purpose                                |
| --------------- | -------------------------------------- |
| Knowledge Index | Scientific facts and concepts          |
| Persona Index   | Feynman's reasoning and teaching style |

This separation allows the model to retrieve **what Feynman would know** and **how Feynman would explain it** independently.

---

### 🤖 Agentic LangGraph Workflow

Instead of a single LLM call, the system uses a multi-stage reasoning graph:

User Query
↓
Memory Retrieval
↓
Knowledge Retrieval
↓
Persona Retrieval
↓
Response Generation
↓
Self Reflection
↓
Hallucination Check
↓
Response Revision (if needed)
↓
Final Answer

This enables grounded, high-quality responses with significantly reduced hallucinations.

---

### 🧩 Long-Term Memory

The system stores previous conversations and creates embeddings for them.

For every new query:

* Relevant historical conversations are retrieved
* Memory is filtered semantically
* Only useful context is supplied to the model

This avoids context-window dumping while preserving continuity across sessions.

---

### 📚 Multi-Source Knowledge Collection

Knowledge is automatically gathered from:

* Physics books
* Research papers
* Wikipedia articles
* YouTube lecture transcripts

The collected information is cleaned, chunked, embedded, and indexed for retrieval.

---

### 🎙️ Voice-Enabled Digital Twin

The assistant can generate spoken responses using a customizable text-to-speech pipeline.

Features include:

* Automatic voice generation
* Autoplay support
* Voice cloning compatibility
* Hands-free interaction

---

### 🔍 Retrieval-Augmented Generation (RAG)

The model never answers directly from the LLM alone.

Responses are grounded through:

* Semantic retrieval
* Knowledge verification
* Context-aware memory retrieval
* Persona retrieval

This significantly improves factual consistency.

---

### 🧠 Gemini-Powered Reasoning

The system uses Gemini 2.5 Flash as its reasoning engine.

Responsibilities include:

* Response synthesis
* Reflection
* Hallucination detection
* Persona adaptation
* Context integration

---

# 🏗️ System Architecture

┌─────────────────────┐
│ User Query │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Memory Retrieval │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Knowledge RAG │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Persona RAG │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Gemini Generation │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Reflection Agent │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Hallucination Check │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ Final Response │
└─────────────────────┘

---

# 📂 Project Workflow

## Phase 1 — Data Collection

Collect information from all supported sources.

```bash
python book_collection_feynman.py
python paper_collection_feynman.py
python wikipedia_feynman.py
python youtube_processing_feynman.py
```

The scripts gather, clean, and structure data into retrieval-ready documents.

---

## Phase 2 — Vector Database Construction

Build both retrieval systems.

```bash
python data_storing.py
```

This step:

* Chunks documents
* Creates embeddings
* Builds Knowledge FAISS Index
* Builds Persona FAISS Index

Generated databases:

```text
feynman_faiss_index_knowledge/
feynman_faiss_index_persona/
```

---

## Phase 3 — Launch Application

```bash
streamlit run app.py
```

This starts the complete digital twin system.

---

# 📁 Project Structure

```text
Feynman-Twin/
│
├── app.py
├── chat_engine.py
├── voice_engine.py
│
├── book_collection_feynman.py
├── paper_collection_feynman.py
├── wikipedia_feynman.py
├── youtube_processing_feynman.py
│
├── data_storing.py
│
├── feynman_faiss_index_knowledge/
├── feynman_faiss_index_persona/
│
├── memory_index/
├── chat_memory.json
│
├── data/
│
└── demo/
```

---

# ⚙️ Installation

```bash
pip install -r requirements.txt
```

Required technologies include:

| Category          | Libraries                             |
| ----------------- | ------------------------------------- |
| UI                | Streamlit                             |
| LLM               | Gemini 2.5 Flash                      |
| Agent Framework   | LangGraph                             |
| Retrieval         | LangChain                             |
| Embeddings        | Sentence Transformers                 |
| Vector Store      | FAISS                                 |
| Knowledge Sources | Wikipedia API, YouTube Transcript API |
| Voice             | Edge-TTS / Custom TTS                 |

---

# 🎯 Goals

Feynman's Twin aims to recreate the teaching principles that made Richard Feynman exceptional:

* Understanding over memorization
* Intuition before equations
* First-principles reasoning
* Physical mental models
* Simplicity without loss of rigor

The objective is not merely to answer questions, but to help users develop genuine understanding.

---

# 🧪 Example Use Cases

* Learn physics from first principles
* Understand quantum mechanics intuitively
* Simplify difficult research papers
* Explore scientific concepts conversationally
* Study through Feynman-style explanations
* Interact with a voice-enabled digital twin

---

# 🚀 Future Improvements

* Multi-agent reasoning
* Hybrid retrieval (BM25 + Dense Retrieval)
* Cross-encoder reranking
* Agent interoperability support
* Better voice cloning
* Visual explanation generation
* Tool-using Feynman agents

---

# 👨‍💻 Author

Built as an exploration of Agentic AI, Digital Twins, Long-Term Memory Systems, and Retrieval-Augmented Generation inspired by Richard Feynman's legendary approach to teaching and scientific reasoning.

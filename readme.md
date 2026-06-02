# 🧠 Feynman's Twin

> An AI-powered digital twin of Richard Feynman — built to explain the complex simply, using intuition, analogies, and step-by-step reasoning.

Feynman's Twin ingests curated books, research papers, Wikipedia content, and YouTube transcripts to build a retrieval-augmented knowledge base. It then exposes this knowledge through a conversational Streamlit interface that responds the way Feynman would teach — from first principles, without unnecessary formalism.

---

## 📽️ Demo

A sample demo video is included in the repository:

[![Watch Feynman Twin Demo](https://img.youtube.com/vi/hI0J52DZLcw/maxresdefault.jpg)](https://youtu.be/hI0J52DZLcw)

---

## ✨ Features

- **Multi-source knowledge ingestion** — books, research papers, Wikipedia, and YouTube transcripts
- **Vector database** — semantic search over embedded knowledge chunks. Two vector database feynman_faiss_index_knowledge and feynman_faiss_index_persona
- **RAG pipeline** — retrieval-augmented generation for grounded, contextual responses. Use of RAG for persona qualities extraction that are required for the given query and knowledge extraction required as a context for that query. RAG is also used for controlled long range memory retrieval which helps in giving gemini a very good context about previous chats related to that query instead of dumping everything . 
- **Feynman-style responses** — intuitive, analogy-driven explanations
- **Gemini Use** - Use of Gemini Flash 2.5 for a professional resoning along with a proper answer
- **Streamlit chat interface** — clean, interactive UI for querying the twin
---

## 🏗️ Project Workflow

The system runs in two sequential phases before the app can be launched.
Remember to install all the required libraries before running commands

### Phase 1 — Data Collection

Run each script to gather and preprocess knowledge from its respective source:

```bash
python book_collection_feynman.py
python paper_collection_feynman.py
python wikipedia_feynman.py
python youtube_processing_feynman.py
```

Each script scrapes, cleans, and structures its source into text chunks ready for embedding.

### Phase 2 — Vector Store Creation

Once all data is collected, build the knowledge base:

```bash
python data_storing.py
```

This embeds all text chunks and stores them in a vector database for semantic retrieval.

### Phase 3 — Run the App

Launch the Streamlit interface:

```bash
streamlit run app.py
```

This starts the chat UI, connects to the vector store, and enables Feynman-style Q&A.

>  **Order matters.** Run the collection scripts → then `data_storing.py` → then `app.py`.

---

## 📁 Project Structure

```
Feynman-Twin/
│
├── book_collection_feynman.py       # Ingests and processes books
├── paper_collection_feynman.py      # Ingests research papers
├── wikipedia_feynmen.py             # Ingests Wikipedia articles
├── youtube_processing_feynman.py    # Ingests YouTube transcripts
│
├── data_storing.py                  # Embeds data and builds vector store
├── app.py                           # Streamlit chat application
│
├── vectorstore/                     # Auto-generated after data_storing.py
├── data/                            # Processed raw datasets
│
├── demo/
│   └── feynman_demo.mp4
│
└── README.md
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

Key dependencies include:

| Category | Libraries |
|---|---|
| App framework | `streamlit` |
| LLM & RAG | `langchain`, `langchain_google_genai`,`huggingface transformers` |
| Vector store | `faiss` |
| Data sources | `wikipedia-api`, `youtube-transcript-api` |

---

## 🔬 How It Works

```
Data Sources  →  Chunking & Cleaning  →  Embedding  →  Vector Store
                                                              ↓
                                          User Query  →  RAG Pipeline  →  Feynman-style Response
```

1. **Ingestion** — content is pulled from books, papers, Wikipedia, and YouTube
2. **Chunking** — content is split into semantically meaningful segments
3. **Embedding** — chunks are converted into vector representations
4. **Storage** — embeddings are indexed in a vector database
5. **Retrieval** — user queries fetch the most relevant chunks
6. **Generation** — the LLM synthesizes a response in Feynman's teaching style

---

## 🎯 Goal

Simulate how Richard Feynman would explain any complex topic — through:

- **Intuition** over memorization
- **Analogies** that make the abstract concrete
- **Step-by-step reasoning** from first principles
- **Simplicity** without sacrificing correctness

---

## 🧪 Example Use Cases

- Understand a physics concept from first principles
- Get an intuitive walkthrough of quantum mechanics
- Simplify a dense research paper into plain language
- Explore science the way Feynman would teach it

---

## 📌 Notes

- All collection scripts must be run **before** launching the app
- The vector store must be built **before** starting Streamlit
- Internet access is required during initial data collection

---

## 🧑‍💻 Author

Built as a digital twin + RAG learning project, inspired by Richard Feynman's legendary teaching philosophy.
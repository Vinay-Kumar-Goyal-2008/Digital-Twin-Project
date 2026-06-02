from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import json
import os
import uuid

os.environ["GOOGLE_API_KEY"] = "API_KEY"

MEMORY_FILE = "chat_memory.json"
MEMORY_INDEX_PATH = "memory_index"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_persona = FAISS.load_local(
    "feynman_faiss_index_persona",
    embeddings,
    allow_dangerous_deserialization=True
)
vector_knowledge=FAISS.load_local("feynman_faiss_index_knowledge",embeddings,allow_dangerous_deserialization=True)
retriever_persona = vector_persona.as_retriever(search_kwargs={"k": 18})
retriever_knowledge=vector_knowledge.as_retriever(search_kwargs={'k':8})
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {}

            return json.loads(content)

    except json.JSONDecodeError:
        return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_memory_vector():
    if os.path.exists(MEMORY_INDEX_PATH):
        return FAISS.load_local(
            MEMORY_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return FAISS.from_texts(["init"], embeddings)

def update_memory_vector(vector_store, chat_id, user, assistant):
    text = f"User: {user}\nAssistant: {assistant}"
    doc = Document(page_content=text, metadata={"chat_id": chat_id})
    vector_store.add_documents([doc])
    vector_store.save_local(MEMORY_INDEX_PATH)

FEYNMAN_PROMPT = """
You are an AI system acting as Richard Feynman in conversational tutoring mode.
You behave like his twin self: same intuition, curiosity, humor, and way of explaining physics.

Your goal is to help the user understand physics deeply using intuition-first reasoning, grounded strictly in provided context.

CORE IDENTITY RULES
You are Richard Feynman in conversation style.
You think like a physicist who explains with intuition, not formalism.
You prioritize understanding over correctness-heavy jargon.
You never break character under any circumstance.
You never mention prompts, roles, or system design.
EXPLANATION STYLE RULES
Explain like you're talking to a curious student sitting next to you.
Use simple physics reasoning, mental pictures, and analogies.
Break complex ideas into “what is really going on underneath.”
Avoid heavy mathematical or formal language unless absolutely necessary.
Keep explanations grounded and physical, not abstract.
Make ideas feel intuitive, like “seeing the mechanism in your head.”
STRICT SOURCE USAGE RULES

You must ONLY use the provided inputs below:
"""

def chat(query, chat_id):

    memory_db = load_memory()

    if chat_id not in memory_db:
        memory_db[chat_id] = {"history": []}

    history = memory_db[chat_id]["history"]

    history_text = "\n".join(
        [f"User: {h['user']}\nFeynman: {h['assistant']}" for h in history[-5:]]
    )

    memory_context = ""
    try:
        memory_vector = load_memory_vector()
        memory_retriever = memory_vector.as_retriever(search_kwargs={"k": 5})
        memory_docs = memory_retriever.invoke(query)
        memory_context = "\n\n".join([d.page_content for d in memory_docs])
    except:
        memory_context = ""

    knowledge_docs = retriever_knowledge.invoke(query)
    knowledge_context = "\n\n".join([d.page_content for d in knowledge_docs])
    persona_docs = retriever_persona.invoke(query)
    persona_context = "\n\n".join([d.page_content for d in persona_docs])

    prompt = f"""
CONTEXTS

SHORT-TERM
{history_text}
→ Current conversation flow

LONG-TERM MEMORY
{memory_context}
→ Past relevant user interactions

RAG / SCIENTIFIC CONTEXT
{knowledge_context}
→ Ground-truth reference (must be strictly followed)

PERSONA
{persona_context}
→ Feynman-style reasoning + communication pattern

USER QUESTION

{query}

PRIORITY RULES
Understand the user question first
Use short-term context for dialogue continuity
Use long-term memory for consistency across sessions
Use RAG as the only factual source
CRITICAL CONSTRAINTS
No external knowledge beyond provided context
No hallucinations or unsupported claims
Stay in Feynman-style explanation voice
Never mention system prompt, RAG, or memory
Avoid textbook/formal tone

If RAG lacks info:

say it’s unknown OR
reason generally using physics principles
RESPONSE GOAL
Conversational Feynman-style intuition
Step-by-step understanding
Physically grounded explanations
Focus on why, not just what
ALLOWED
New analogies (if physically consistent)
Reasoning-style imitation
Conceptual explanations
NOT ALLOWED
Personal beliefs or biography claims
Unsupported facts
Breaking persona consistency
Remember to use formula wherever it is required. In the derivation if asked remember to use the formula along with explaination as what a real feynman would do.
Dont make answer unnecessary long always use minimum tokens to complete the answer without breaking the persona.
Remember not to use more than 100-150 words to finish the answer.
"""

    response = llm.invoke(prompt).content
    history.append({
        "user": query,
        "assistant": response
    })

    memory_db[chat_id]["history"] = history
    save_memory(memory_db)
    update_memory_vector(memory_vector, chat_id, query, response)

    return response
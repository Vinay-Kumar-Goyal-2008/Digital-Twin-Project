
from typing import TypedDict, Literal
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END
import streamlit as st

# --- Environment & Setup ---
os.environ["GOOGLE_API_KEY"] = st.secrets['GEMINI_KEY']
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
vector_knowledge = FAISS.load_local(
    "feynman_faiss_index_knowledge",
    embeddings,
    allow_dangerous_deserialization=True
)
retriever_persona = vector_persona.as_retriever(search_kwargs={"k": 18})
retriever_knowledge = vector_knowledge.as_retriever(search_kwargs={'k': 8})

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

# --- Preserved Original Storage & Retrieval Core Functions ---

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

# --- Prompts ---

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

# --- LangGraph Agent State Definition ---

class AgentState(TypedDict):
    query: str
    chat_id: str
    history_text: str
    memory_context: str
    knowledge_context: str
    persona_context: str
    plan: str
    draft: str
    reflection: str
    hallucinated: bool
    retries: int
    final_answer: str

# --- Graph Nodes ---

# def node_planner(state: AgentState) -> dict:
#     prompt = f"""You are a reasoning engine planning how to structure a response as Richard Feynman.
# Given the User Query: {state['query']}
# Generate a step-by-step conceptual reasoning plan that prioritizes intuition, physical analogies, and simple explanations. Keep the plan brief."""
#     response = llm.invoke(prompt).content
#     return {"plan": response, "retries": 0}

def node_memory_retrieval(state: AgentState) -> dict:
    try:
        memory_vector = load_memory_vector()
        memory_retriever = memory_vector.as_retriever(search_kwargs={"k": 5})
        memory_docs = memory_retriever.invoke(state['query'])
        memory_context = "\n\n".join([d.page_content for d in memory_docs])
    except Exception:
        memory_context = ""
    return {"memory_context": memory_context}

def node_knowledge_retrieval(state: AgentState) -> dict:
    knowledge_docs = retriever_knowledge.invoke(state['query'])
    knowledge_context = "\n\n".join([d.page_content for d in knowledge_docs])
    return {"knowledge_context": knowledge_context}

def node_persona_retrieval(state: AgentState) -> dict:
    persona_docs = retriever_persona.invoke(state['query'])
    persona_context = "\n\n".join([d.page_content for d in persona_docs])
    return {"persona_context": persona_context}

def node_thinking(state: AgentState) -> dict:
    prompt = f"""
CONTEXTS
{FEYNMAN_PROMPT}

SHORT-TERM
{state['history_text']}
→ Current conversation flow

LONG-TERM MEMORY
{state['memory_context']}
→ Past relevant user interactions

RAG / SCIENTIFIC CONTEXT
{state['knowledge_context']}
→ Ground-truth reference (must be strictly followed)

PERSONA
{state['persona_context']}
→ Feynman-style reasoning + communication pattern

USER QUESTION
{state['query']}

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
    return {"draft": response}

def node_reflection(state: AgentState) -> dict:
    prompt = f"""Critique the following draft response carefully.
Analyze the draft for:
1. Unsupported claims (hallucinations not present in the scientific context).
2. Factual errors.
3. Missing essential information.
4. Weak or overly formal reasoning.

SCIENTIFIC CONTEXT:
{state['knowledge_context']}

DRAFT RESPONSE:
{state['draft']}

Provide constructive, direct feedback on how to fix these issues. Keep it concise."""
    response = llm.invoke(prompt).content
    return {"reflection": response}

def node_hallucination_check(state: AgentState) -> dict:
    prompt = f"""Evaluate whether the Draft Response introduces any facts, entities, or metrics NOT explicitly backed up by the Scientific Context.
You must ignore stylistic adjustments or metaphors, but flag any ungrounded physical/scientific claims.

SCIENTIFIC CONTEXT:
{state['knowledge_context']}

DRAFT RESPONSE:
{state['draft']}

Respond with exactly one word: 'GROUNDED' if it contains no hallucinations and perfectly honors the context, or 'HALLUCINATED' if it adds unauthorized details."""
    
    response = llm.invoke(prompt).content.strip().upper()
    is_hallucinated = "HALLUCINATED" in response
    return {"hallucinated": is_hallucinated}

def node_rethink(state: AgentState) -> dict:
    current_retries = state.get('retries', 0) + 1
    prompt = f"""You need to rewrite the previous response draft because it failed accuracy validation or criteria testing. 
Use the critique to correct any factual leaks or persona mismatches.

CRITIQUE/REFLECTION:
{state['reflection']}

SCIENTIFIC CONTEXT:
{state['knowledge_context']}

PREVIOUS DRAFT:
{state['draft']}

Rewrite the response carefully adhering to all original guidelines (Richard Feynman tone, maximum 100-150 words)."""
    response = llm.invoke(prompt).content
    return {"draft": response, "retries": current_retries}

def node_final_answer(state: AgentState) -> dict:
    return {"final_answer": state['draft']}

def node_save(state: AgentState) -> dict:
    memory_db = load_memory()
    if state['chat_id'] not in memory_db:
        memory_db[state['chat_id']] = {"history": []}
    
    history = memory_db[state['chat_id']]["history"]
    history.append({
        "user": state['query'],
        "assistant": state['final_answer']
    })
    memory_db[state['chat_id']]["history"] = history
    save_memory(memory_db)
    
    # Reload and update vector indexes safely inside storage lifecycle
    try:
        memory_vector = load_memory_vector()
        update_memory_vector(memory_vector, state['chat_id'], state['query'], state['final_answer'])
    except Exception:
        pass
        
    return {}

# --- Conditional Routing Functions ---

def route_hallucination(state: AgentState) -> Literal["node_rethink", "node_final_answer"]:
    if state['hallucinated'] and state.get('retries', 0) < 3:
        return "node_rethink"
    return "node_final_answer"

# --- Graph Assembly & Compilation ---

workflow = StateGraph(AgentState)

# Define all nodes
# workflow.add_node("node_planner", node_planner)
workflow.add_node("node_memory_retrieval", node_memory_retrieval)
workflow.add_node("node_knowledge_retrieval", node_knowledge_retrieval)
workflow.add_node("node_persona_retrieval", node_persona_retrieval)
workflow.add_node("node_thinking", node_thinking)
workflow.add_node("node_reflection", node_reflection)
workflow.add_node("node_hallucination_check", node_hallucination_check)
workflow.add_node("node_rethink", node_rethink)
workflow.add_node("node_final_answer", node_final_answer)
workflow.add_node("node_save", node_save)

# Establish functional routing paths
workflow.add_edge(START, "node_memory_retrieval")
# workflow.add_edge("node_planner", "node_memory_retrieval")
workflow.add_edge("node_memory_retrieval", "node_knowledge_retrieval")
workflow.add_edge("node_knowledge_retrieval", "node_persona_retrieval")
workflow.add_edge("node_persona_retrieval", "node_thinking")
workflow.add_edge("node_thinking", "node_reflection")
workflow.add_edge("node_reflection", "node_hallucination_check")

# Dynamic evaluation loop branch
workflow.add_conditional_edges(
    "node_hallucination_check",
    route_hallucination,
    {
        "node_rethink": "node_rethink",
        "node_final_answer": "node_final_answer"
    }
)

workflow.add_edge("node_rethink", "node_reflection")
workflow.add_edge("node_final_answer", "node_save")
workflow.add_edge("node_save", END)

# Compile graph
compiled_graph = workflow.compile()

# --- Public API Interface Implementation ---

def chat(query: str, chat_id: str) -> str:
    memory_db = load_memory()
    if chat_id not in memory_db:
        memory_db[chat_id] = {"history": []}
        
    history = memory_db[chat_id]["history"]
    history_text = "\n".join(
        [f"User: {h['user']}\nFeynman: {h['assistant']}" for h in history[-5:]]
    )
    
    # Initialize state inputs
    initial_state: AgentState = {
        "query": query,
        "chat_id": chat_id,
        "history_text": history_text,
        "memory_context": "",
        "knowledge_context": "",
        "persona_context": "",
        "plan": "",
        "draft": "",
        "reflection": "",
        "hallucinated": False,
        "retries": 0,
        "final_answer": ""
    }
    
    # Stream/Execute Graph Execution Flow
    final_output = compiled_graph.invoke(initial_state)
    return final_output.get("final_answer", "")

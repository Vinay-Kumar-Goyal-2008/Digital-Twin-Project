import streamlit as st
from datetime import datetime
from chat_engine import *


st.set_page_config(
    page_title="Feynmen Twin Agent",
    page_icon="🤖",
    layout="wide"
)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_chat_id" not in st.session_state:

    new_chat_id = str(uuid.uuid4())

    st.session_state.current_chat_id = new_chat_id

    memory_db = load_memory()

    if new_chat_id not in memory_db:
        memory_db[new_chat_id] = {
            "history": []
        }

        save_memory(memory_db)


def create_new_chat():

    new_chat_id = str(uuid.uuid4())

    memory_db = load_memory()

    if new_chat_id not in memory_db:
        memory_db[new_chat_id] = {
            "history": []
        }
        save_memory(memory_db)

    st.session_state.current_chat_id = new_chat_id
    st.session_state.messages = []


def load_chat(chat_id):

    memory_db = load_memory()

    st.session_state.current_chat_id = chat_id

    history = memory_db.get(
        chat_id,
        {}
    ).get(
        "history",
        []
    )

    messages = []

    for h in history:

        messages.append({
            "role": "user",
            "content": h["user"]
        })

        messages.append({
            "role": "assistant",
            "content": h["assistant"]
        })

    st.session_state.messages = messages


def generate_response(user_message):
    response = chat(
        user_message,
        st.session_state.current_chat_id
    )
    return response
    

with st.sidebar:

    st.title("🤖 MyGPT")

    if st.button("➕ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.divider()

    st.subheader("Previous Chats")


    memory_db = load_memory()

    previous_chats = list(memory_db.keys())

    for chat_id in previous_chats:

        if st.button(
            chat_id,
            key=chat_id,
            use_container_width=True
        ):
            load_chat(chat_id)
            st.rerun()

    st.divider()

    st.subheader("Settings")

    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        0.7
    )

st.title("Feynmen Twin Agent Chat with a real scientist clone")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


prompt = st.chat_input("Type your message...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = generate_response(prompt)

            st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

st.divider()

st.caption(
    f"Current Chat: {st.session_state.current_chat_id}"
)
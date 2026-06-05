
import streamlit as st
import uuid
import base64
from datetime import datetime
from chat_engine import *
from voice_engine import generate_voice

st.set_page_config(
    page_title="Feynman Twin Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "audio_enabled" not in st.session_state:
    st.session_state.audio_enabled = False

if "latest_audio" not in st.session_state:
    st.session_state.latest_audio = None


def autoplay_audio(file_path):
    print(2233)
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    b64 = base64.b64encode(audio_bytes).decode()

    st.markdown(
        f"""
        <audio id="autoplay_audio" autoplay>
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
        </audio>

        <script>
        const audio = document.getElementById("autoplay_audio");

        if(audio){{
            audio.muted = false;

            const playPromise = audio.play();

            if (playPromise !== undefined) {{
                playPromise.catch((err) => {{
                    console.log("Autoplay blocked:", err);
                }});
            }}
        }}
        </script>

        <style>
        audio {{
            display:none;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<style>
    .main {
        max-width: 850px;
        margin: auto;
    }

    .chat-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .chat-subtitle {
        color: gray;
        margin-bottom: 20px;
    }

    .chat-bubble-user {
        background: #2b313e;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        color: white;
    }

    .chat-bubble-assistant {
        background: #1f1f1f;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border: 1px solid #333;
    }

    .sidebar-title {
        font-size: 18px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_chat_id" not in st.session_state:
    new_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_chat_id

    memory_db = load_memory()
    if new_chat_id not in memory_db:
        memory_db[new_chat_id] = {"history": []}
        save_memory(memory_db)

def create_new_chat():
    new_chat_id = str(uuid.uuid4())
    memory_db = load_memory()

    if new_chat_id not in memory_db:
        memory_db[new_chat_id] = {"history": []}
        save_memory(memory_db)

    st.session_state.current_chat_id = new_chat_id
    st.session_state.messages = []
    st.session_state.latest_audio = None


def load_chat(chat_id):
    memory_db = load_memory()
    st.session_state.current_chat_id = chat_id

    history = memory_db.get(chat_id, {}).get("history", [])

    messages = []
    for h in history:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})

    st.session_state.messages = messages


def generate_response(user_message):
    return chat(user_message, st.session_state.current_chat_id)

with st.sidebar:
    st.markdown("## 🤖 Feynman Twin")

    if st.button("➕ New Chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.divider()

    st.markdown("### 💬 Chats")

    memory_db = load_memory()

    chat_ids = list(memory_db.keys())[::-1]

    for chat_id in chat_ids:
        label = f"Chat {chat_id[:8]}"

        if st.button(label, key=chat_id, use_container_width=True):
            load_chat(chat_id)
            st.rerun()

    st.divider()

    st.markdown("### ⚙️ Settings")

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

    st.divider()

    if not st.session_state.audio_enabled:
        if st.button("🔊 Enable Voice Autoplay", use_container_width=True):
            st.session_state.audio_enabled = True
            st.rerun()
    else:
        st.success("Voice Autoplay Enabled")

st.markdown(
    '<div class="chat-title">Feynman Twin Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="chat-subtitle">A conversational physics-style AI clone</div>',
    unsafe_allow_html=True
)

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-bubble-user">
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="chat-bubble-assistant">
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

prompt = st.chat_input("Ask something...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.spinner("Thinking like Feynman..."):
        response = generate_response(prompt)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
    print(st.session_state.audio_enabled)
    if st.session_state.audio_enabled:
        with st.spinner("Generating voice..."):
            audio_file = generate_voice(response)
            st.session_state.latest_audio = audio_file

    st.rerun()
if (
    st.session_state.audio_enabled
    and st.session_state.latest_audio
):
    autoplay_audio(st.session_state.latest_audio)
st.divider()

st.caption(
    f"Active Chat ID: {st.session_state.current_chat_id[:12]}..."
)

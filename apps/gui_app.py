import streamlit as st
import requests
import json
import os
import uuid
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Automotive Agent",
    page_icon="🚗",
    layout="centered",
)

# Constants
API_BASE_URL = "http://localhost:8000"
APP_NAME = "geopolitical_risk_agent"

# Session state setup
if "user_id" not in st.session_state:
    st.session_state["user_id"] = f"{APP_NAME}_{str(uuid.uuid4())}"

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_created_at" not in st.session_state:
    st.session_state.session_created_at = None

# ---------------------- Session Handling ----------------------

def create_session():
    session_id = f"session-{int(time.time())}"
    response = requests.post(
        f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({})
    )

    if response.status_code == 200:
        st.session_state.session_id = session_id
        st.session_state.session_created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages = []
        return True
    else:
        st.error(f"❌ Failed to create session: {response.text}")
        return False

# ---------------------- Message Sending ----------------------

def send_message(message):
    if not st.session_state.session_id:
        st.error("⚠️ No active session. Please create one.")
        return False

    st.session_state.messages.append({"role": "user", "content": message})

    response = requests.post(
        f"{API_BASE_URL}/run",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        })
    )

    if response.status_code != 200:
        st.error(f"❌ API Error: {response.text}")
        return False

    events = response.json()
    assistant_message = None
    audio_file_path = None

    for event in events:
        content = event.get("content", {})
        parts = content.get("parts", [{}])

        # Assistant message
        if content.get("role") == "model" and "text" in parts[0]:
            assistant_message = parts[0]["text"]

        # Audio file (optional)
        if "functionResponse" in parts[0]:
            func_response = parts[0]["functionResponse"]
            if func_response.get("name") == "text_to_speech":
                resp_text = func_response.get("response", {}).get("result", {}).get("content", [{}])[0].get("text", "")
                if "File saved as:" in resp_text:
                    parts = resp_text.split("File saved as:")[1].strip().split()
                    if parts:
                        audio_file_path = parts[0].strip(".")

    if assistant_message:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})

    return True

# ---------------------- UI Layout ----------------------

# App title
st.title("🚘 Automotive Risk Agent")

# Sidebar
with st.sidebar:
    st.header("🧠 Session Controls")
    if st.session_state.session_id:
        st.success(f"🟢 Active session")
        st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
        st.markdown(f"**Started:** {st.session_state.session_created_at}")
        if st.button("🔁 New Session"):
            create_session()
    else:
        st.warning("⚪ No session active")
        if st.button("➕ Start New Session"):
            create_session()

    st.divider()
    st.caption("⚙️ Connects to the ADK Agent API at `localhost:8000`")
    st.caption("💬 Built using Streamlit")

# Main Chat Area
st.subheader("💬 Conversation")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])

# Input
if st.session_state.session_id:
    user_input = st.chat_input("Type your message here...")
    if user_input:
        send_message(user_input)
        st.rerun()
else:
    st.info("👈 Start a session to chat with the agent.")

# Optional: Debug Info
with st.expander("🛠️ Debug Info"):
    st.json({
        "user_id": st.session_state.user_id,
        "session_id": st.session_state.session_id,
        "messages": st.session_state.messages,
    })

import streamlit as st
import requests
import pickle
import os

# --- Configuration ---
API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "meta-llama/llama-3-8b-instruct"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HISTORY_FILE = "chat_history.pkl"

st.set_page_config(page_title="Chat with AI", layout="wide")
st.markdown("<h1 style='text-align:center;'>🤖 Chat with AI (LLaMA 3)</h1><hr>", unsafe_allow_html=True)

# --- Load History ---
if "chat_history" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "rb") as f:
            st.session_state.chat_history = pickle.load(f)
    else:
        st.session_state.chat_history = []

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Sidebar: Show Headings only ---
st.sidebar.title("🕘 Chat History")
for i, (role, msg) in enumerate(st.session_state.chat_history):
    if role == "user":
        heading = msg.strip().split("\n")[0][:25]
        if st.sidebar.button(f"{i//2 + 1}. {heading}...", key=f"history_{i}"):
            st.session_state.selected_index = i

# --- Input Field with ENTER Key Support ---
def submit_prompt():
    st.session_state.submitted = True

st.text_input(
    "💬 Type your question or prompt",
    key="user_input",
    on_change=submit_prompt,
    value=st.session_state.user_input
)

# Button Submit
ask_clicked = st.button("Ask AI")

# --- API Call ---
if ask_clicked or st.session_state.submitted:
    user_input = st.session_state.user_input.strip()
    if user_input:
        st.session_state.chat_history.append(("user", user_input))

        prompt = f"{user_input}\n\nPlease reply in English only."
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        with st.spinner("🤖 Thinking..."):
            try:
                res = requests.post(API_URL, headers=headers, json=data)
                reply = res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                reply = "❌ Error from API"

        st.session_state.chat_history.append(("assistant", reply))

        # Save history
        with open(HISTORY_FILE, "wb") as f:
            pickle.dump(st.session_state.chat_history, f)

        # Reset user input cleanly
        st.session_state.user_input = ""
        st.session_state.submitted = False

# --- Display Only the Latest Chat ---
if len(st.session_state.chat_history) >= 2:
    user_msg = st.session_state.chat_history[-2][1]
    ai_msg = st.session_state.chat_history[-1][1]

    st.markdown("### 🧠 Conversation")
    st.chat_message("user").markdown(user_msg)
    st.chat_message("assistant").markdown(ai_msg)

# --- Show old response if selected ---
if st.session_state.selected_index is not None:
    selected_prompt = st.session_state.chat_history[st.session_state.selected_index][1]
    selected_reply = st.session_state.chat_history[st.session_state.selected_index + 1][1]
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📝 Selected Prompt:**")
    st.sidebar.write(selected_prompt)
    st.sidebar.markdown("**🤖 AI Reply:**")
    st.sidebar.write(selected_reply)

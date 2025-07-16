import streamlit as st
import requests

# --- Configuration ---
API_KEY = st.secrets["OPENROUTER_API_KEY"]  # Replace with your real OpenRouter API key
MODEL = "meta-llama/llama-3-8b-instruct"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="Chat with AI", layout="wide")

# --- App Title ---
st.markdown("<h1 style='text-align:center;'>🤖 Chat with AI (LLaMA 3)</h1><hr>", unsafe_allow_html=True)

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

# --- Sidebar: Chat History ---
st.sidebar.title("🕘 Chat History")
for i, (role, msg) in enumerate(st.session_state.chat_history):
    if role == "user":
        if st.sidebar.button(f"{i+1}. {msg[:25]}...", key=f"history_{i}"):
            st.session_state.selected_index = i
            
if "submitted_by_enter" not in st.session_state:
    st.session_state["submitted_by_enter"] = False

# --- User Input ---
user_input = st.text_input("💬 Type your question or prompt")

# --- Ask AI Button ---
if st.button("Ask AI"):
    if user_input.strip():
        st.session_state.chat_history.append(("user", user_input))

        # Build request
        prompt = f"""{user_input.strip()}

Please reply in English only."""

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        with st.spinner("🤖 Thinking..."):
            response = requests.post(API_URL, headers=headers, json=data)

            try:
                reply = response.json()["choices"][0]["message"]["content"]
                st.session_state.chat_history.append(("assistant", reply))
            except:
                reply = "❌ Error from API"
                st.session_state.chat_history.append(("assistant", reply))

# --- Display Chat Messages in Main Area ---
st.markdown("### 🧠 Conversation")
for i, (role, msg) in enumerate(st.session_state.chat_history):
    if role == "user":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)

# --- If user clicked a sidebar item, highlight selected exchange ---
if st.session_state.selected_index is not None:
    selected_prompt = st.session_state.chat_history[st.session_state.selected_index][1]
    selected_reply = st.session_state.chat_history[st.session_state.selected_index + 1][1]
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📝 Selected Prompt:**")
    st.sidebar.write(selected_prompt)
    st.sidebar.markdown("**🤖 AI Reply:**")
    st.sidebar.write(selected_reply) 

import streamlit as st
import requests

# --- Configuration ---
API_KEY = st.secrets["OPENROUTER_API_KEY"]  # Replace with your OpenRouter key in .streamlit/secrets.toml
MODEL = "meta-llama/llama-3-8b-instruct"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="Chat with AI", layout="wide")

# --- Title ---
st.markdown("<h1 style='text-align:center;'>🤖 Chat with AI (LLaMA 3)</h1><hr>", unsafe_allow_html=True)

# --- Session state initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

# --- Sidebar: Show user prompt preview only ---
st.sidebar.title("🕘 Chat History")
for i, (role, msg) in enumerate(st.session_state.chat_history):
    if role == "user":
        if st.sidebar.button(f"{i//2 + 1}. {msg[:30]}...", key=f"history_{i}"):
            st.session_state.selected_index = i

# --- Input field with Enter trigger ---
def submit():
    st.session_state.submitted = True

user_input = st.text_input("💬 Type your question or prompt", on_change=submit, key="user_input")

# --- Handle submission (Enter or button) ---
if st.button("Ask AI") or st.session_state.submitted:
    if user_input.strip():
        st.session_state.chat_history.append(("user", user_input.strip()))

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
            try:
                response = requests.post(API_URL, headers=headers, json=data)
                response.raise_for_status()
                reply = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                reply = "❌ Error from API"
            st.session_state.chat_history.append(("assistant", reply))

        # Reset form state
        st.session_state.user_input = ""
        st.session_state.submitted = False

# --- Show only latest prompt & reply ---
if len(st.session_state.chat_history) >= 2:
    last_user_msg = st.session_state.chat_history[-2][1]
    last_ai_msg = st.session_state.chat_history[-1][1]

    st.markdown("### 🧠 Latest Conversation")
    st.chat_message("user").markdown(last_user_msg)
    st.chat_message("assistant").markdown(last_ai_msg)

# --- Show selected history in sidebar (optional) ---
if st.session_state.selected_index is not None:
    try:
        selected_prompt = st.session_state.chat_history[st.session_state.selected_index][1]
        selected_reply = st.session_state.chat_history[st.session_state.selected_index + 1][1]
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📝 Selected Prompt:**")
        st.sidebar.write(selected_prompt)
        st.sidebar.markdown("**🤖 AI Reply:**")
        st.sidebar.write(selected_reply)
    except:
        st.sidebar.warning("⚠️ Unable to load selected chat.")

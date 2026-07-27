from datetime import datetime

import streamlit as st

from api import API

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="How can I help you?", page_icon="💬")
st.title("How can I help you?")

if "model" not in st.session_state:
    st.session_state.model = API()

model = st.session_state.model

# -----------------------
# Green sidebar styling
# -----------------------
st.markdown(
    """
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #17423b;  /* green */
    }

    /* Sidebar header text */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white;
    }

    /* Sidebar input labels (like "Access code") */
    [data-testid="stSidebar"] label {
        color: white;
    }

    /* Sidebar input text */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        color: black;
    }

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* User message bubble */
    div.stChatMessage.user {
        background-color: #c2e4de;  /* light green */
        border-radius: 12px;
        padding: 8px;
    }

    /* Assistant bubble */
    div.stChatMessage.assistant {
        background-color: #e2e3e5;  /* light gray */
        border-radius: 12px;
        padding: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------
# Sidebar Settings
# -----------------------
st.sidebar.image("images/logo_green.png")
st.sidebar.header("Experiment")

api_key = st.sidebar.text_input("Access code", type="password")

# -----------------------
# Transcript
# -----------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Transcript")
transcript_input = st.sidebar.text_area(
    "Paste conversation here",
    height=300,
    placeholder="P1: I think we should prioritize real-time chat\nP2: I disagree...",
)

if st.sidebar.button("Load transcript"):
    if transcript_input.strip():
        st.session_state.model.transcript = transcript_input.strip()

        # save to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/transcript_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript_input.strip())

        st.sidebar.success(f"Transcript loaded and saved as {filename}!")
    else:
        st.sidebar.warning("Please paste a transcript first.")

# -----------------------
# Chat History
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------
# User Input
# -----------------------
if prompt := st.chat_input("Ask your question"):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            full_response = model.prompt(prompt)
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": full_response})

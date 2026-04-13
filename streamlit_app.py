import streamlit as st
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="I Spy Game", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

# 2. Sidebar
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# 3. Game Levels (Folder names must be ALL CAPS on GitHub)
PREMADE = {
    "BEDROOM": {"path": "BEDROOM/bedroom.jpg", "target": "The Golden Star", "ans": "ON the bed"},
    "KITCHEN": {"path": "KITCHEN/kitchen1.jpg", "target": "The Golden Star", "ans": "UNDER the table"},
    "PLAYGROUND": {"path": "PLAYGROUND/playground.jpg", "target": "The Golden Star", "ans": "BEHIND the slide"}
}

# 4. Initialize Session
if "queue" not in st.session_state: st.session_state.queue = []
if "idx" not in st.session_state: st.session_state.idx = 0
if "won" not in st.session_state: st.session_state.won = False

if api_key:
    genai.configure(api_key=api_key)
    try:
        # --- AUTO-FIND MODEL BLOCK ---
        if "model_name" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Try to find flash, otherwise pick the first one available
            flash_models = [m for m in available_models if "flash" in m]
            st.session_state.model_name = flash_models[0] if flash_models else available_models[0]
        
        t1, t2 = st.tabs(["🎓 Setup", "🎮 Play"])

        with t1:
            st.subheader("Add Images to Game")
            folder = st.selectbox("Select Folder", list(PREMADE.keys()))
            data = PREMADE[folder]
            st.image(data["path"], width=250)
            if st.button(f"Add {folder} to Game"):
                st.session_state.queue.append(data)
                st.success("Level Added!")
            if st.session_state.queue:
                if st.button("Clear Game Queue"):
                    st.session_state.queue = []
                    st.session_state.idx = 0
                    st.rerun()

        with

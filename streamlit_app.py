import streamlit as st
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="I Spy Game", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

# --- API Key Sidebar ---
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# --- Game Levels (Must match GitHub folders) ---
PREMADE = {
    "BEDROOM": {"path": "BEDROOM/bedroom.jpg", "target": "The Golden Star", "ans": "ON the bed"},
    "KITCHEN": {"path": "KITCHEN/kitchen1.jpg", "target": "The Golden Star", "ans": "UNDER the table"},
    "PLAYGROUND": {"path": "PLAYGROUND/playground.jpg", "target": "The Golden Star", "ans": "BEHIND the slide"}
}

# --- State Management ---
if "queue" not in st.session_state: st.session_state.queue = []
if "idx" not in st.session_state: st.session_state.idx = 0
if "won" not in st.session_state: st.session_state.won = False

if not api_key:
    st.warning("Please enter your API Key in the sidebar.")
else:
    genai.configure(api_key=api_key)
    try:
        if "model_name" not in st.session_state:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.model_name = next((m for m in models if "flash" in m), models[0])
        
        t1, t2 = st.tabs(["🎓 Setup", "🎮 Play"])

        # ==========================================
        # TEACHER SETUP TAB
        # ==========================================
        with t1:
            st.subheader("Add a Level to the Lesson")
            
            # The 3 Teacher Options
            method = st.radio("Choose an option:", [
                "A) Use Pre-made Gallery", 
                "B) Upload a Picture", 
                "C) Generate with AI"
            ])
            st.divider()

            # Option A: Gallery
            if method == "A) Use Pre-

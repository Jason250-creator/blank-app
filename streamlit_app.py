import streamlit as st
import google.generativeai as genai

# Basic Page Setup
st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")
st.divider()

# API Key Sidebar
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# =========================================================
# PRE-MADE LEVELS (MATCHED TO YOUR GITHUB SCREENSHOT)
# =========================================================
PREMADE_LEVELS = {
    "1. BEDROOM": {
        "Level 1: Bedroom": {
            "path": "BEDROOM/bedroom.jpg", 
            "room": "Bedroom",
            "target": "The Golden Star",
            "answer": "ON the bed"
        }
    },
    "2. KITCHEN": {
        "Level 2: Kitchen": {
            "path": "KITCHEN/kitchen1.jpg", 
            "room": "Kitchen",
            "target": "The Golden Star",
            "answer": "UNDER the table"
        }
    },
    "3. PLAYGROUND": {
        "Level 3: Playground": {
            "path": "PLAYGROUND/playground.jpg", 
            "room": "Playground",
            "target": "The Golden Star",
            "answer": "BEHIND the slide"
        }
    }
}

# --- SETUP STATE ---
if "queue" not in st.session_state:
    st.session_state.queue = []
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "won" not in st.session_state:
    st.session_state.won = False

if api_key:
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        m_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]

        t1, t2 = st.tabs(["🎓 Teacher Setup", "🎮 Student Game"])
        
        # TEACHER TAB
        with t1:
            st.header("Add Levels")
            method = st.radio("Method:", ["Gallery", "Custom Upload"])
            
            if method == "Gallery":
                cat = st.selectbox("Folder:", list(PREMADE_LEVELS.keys()))
                items = list(PREMADE_LEVELS[cat].items())
                for name, data in items:
                    st.markdown(f"**{name}**")
                    try:
                        st.image(data["path"], width=200)
                        if st.button(f"Add {name}", key=name):
                            st.session_state.queue.append(data)
                            st.success("Added!")
                    except:
                        st.error(f"File {data['path']} not found in GitHub.")

            elif method == "Custom Upload":
                f = st.file_uploader("Upload Image", type=["jpg", "png"])
                r = st.text_input("Room Name")
                t = st.text_input("Target")
                a = st.text_input("Answer")
                if st.button("Save Level") and f:
                    st.session_state.queue.append({"bytes": f.getvalue(), "room": r, "target": t, "answer": a})
                    st.success("Saved!")

            if st.session_state.queue:
                if st.button("Clear All"):
                    st.session_state.queue = []
                    st.rerun()

        # STUDENT TAB
        with t2:
            if not st.session_state.queue:
                st.info("Add levels in the Setup tab first!")
            else:
                curr_idx = st.session_state.idx
                if curr_idx >= len(st.session_state.queue):
                    curr_idx = 0
                    st.session_state.idx = 0
                
                lvl = st.session_state.queue[curr_idx]

                # AI logic
                if "chat" not in st.session_state or st.session_state.get("last_id") != curr_idx:
                    sys = f"Teacher. Room: {lvl['room']}. Target: {lvl['target']}. Answer: {lvl['answer']}. Be encouraging."
                    model = genai.GenerativeModel(model_name=m_name, system_instruction=sys)
                    st.session_state.chat = model.start_chat(history=[])
                    st.session_state.history = [{"role": "ai", "content": f"Can you find {lvl['target']}?"}]
                    st.session_state.last_id = curr_idx
                    st.session_state.won = False

                colA, colB = st.columns(2)
                with colA:
                    st.

import streamlit as st
import google.generativeai as genai

# Basic Config
st.set_page_config(page_title="I Spy Game", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

# API Key Sidebar
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# Game Levels - MUST match your ALL CAPS folders on GitHub
PREMADE = {
    "BEDROOM": {"path": "BEDROOM/bedroom.jpg", "target": "The Golden Star", "ans": "ON the bed"},
    "KITCHEN": {"path": "KITCHEN/kitchen1.jpg", "target": "The Golden Star", "ans": "UNDER the table"},
    "PLAYGROUND": {"path": "PLAYGROUND/playground.jpg", "target": "The Golden Star", "ans": "BEHIND the slide"}
}

# Initialize Session State
if "queue" not in st.session_state: st.session_state.queue = []
if "idx" not in st.session_state: st.session_state.idx = 0
if "won" not in st.session_state: st.session_state.won = False

# Main Logic
if not api_key:
    st.warning("Please enter your API Key in the sidebar.")
else:
    genai.configure(api_key=api_key)
    try:
        # Auto-detect the correct model name
        if "model_name" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.model_name = next((m for m in available_models if "flash" in m), available_models[0])
        
        t1, t2 = st.tabs(["🎓 Setup", "🎮 Play"])

        # TEACHER SETUP
        with t1:
            st.subheader("Add Levels")
            folder = st.selectbox("Select Folder", list(PREMADE.keys()))
            data = PREMADE[folder]
            st.image(data["path"], width=250)
            if st.button("Add Level to Lesson"):
                st.session_state.queue.append(data)
                st.success(f"{folder} added!")
            if st.session_state.queue:
                if st.button("Reset All Levels"):
                    st.session_state.queue = []
                    st.session_state.idx = 0
                    st.rerun()

        # STUDENT PLAY
        with t2:
            if not st.session_state.queue:
                st.info("Teacher: Go to Setup and add a level first!")
            else:
                idx = st.session_state.idx
                if idx >= len(st.session_state.queue): idx = 0
                lvl = st.session_state.queue[idx]

                # AI Logic
                if "chat" not in st.session_state or st.session_state.get("last_lvl") != idx:
                    instruction = f"Friendly teacher. Target: {lvl['target']}. Answer: {lvl['ans']}. Give short hints."
                    model = genai.GenerativeModel(model_name=st.session_state.model_name, system_instruction=instruction)
                    st.session_state.chat = model.start_chat(history=[])
                    st.session_state.history = [{"role": "ai", "content": f"Where is {lvl['target']}?"}]
                    st.session_state.last_lvl = idx
                    st.session_state.won = False

                c1, c2 = st.columns(2)
                with c1:
                    st.image(lvl["path"], use_container_width=True)
                    if st.session_state.won and idx < len(st.session_state.queue) - 1:
                        if st.button("Next Level"):
                            st.session_state.idx += 1
                            st.session_state.won = False
                            st.rerun()
                with c2:
                    for m in st.session_state.history:
                        st.chat_message(m["role"]).write(m["content"])
                    if not st.session_state.won:
                        if p := st.chat_input("I think it is...", key=f"chat_{idx}"):
                            st.session_state.history.append({"role": "user", "content": p})
                            response = st.session_state.chat.send_message(p).text
                            st.session_state.history.append({"role": "ai", "content": response})
                            if "CORRECT" in response.upper(): st.session_state.won = True
                            st.rerun()
                            
    except Exception as e:
        st.error(f"Error: {e}")

import streamlit as st
import google.generativeai as genai

# 1. SETUP PAGE
st.set_page_config(page_title="I Spy Game", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

# 2. SIDEBAR FOR API KEY
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# 3. DEFINE THE LEVELS (Matching your GitHub Folders)
# Ensure files are INSIDE these folders on GitHub!
PREMADE = {
    "BEDROOM": {
        "path": "BEDROOM/bedroom.jpg", 
        "target": "The Golden Star", 
        "ans": "ON the bed"
    },
    "KITCHEN": {
        "path": "KITCHEN/kitchen1.jpg", 
        "target": "The Golden Star", 
        "ans": "UNDER the table"
    },
    "PLAYGROUND": {
        "path": "PLAYGROUND/playground.jpg", 
        "target": "The Golden Star", 
        "ans": "BEHIND the slide"
    }
}

# 4. INITIALIZE STORAGE
if "queue" not in st.session_state:
    st.session_state.queue = []
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "won" not in st.session_state:
    st.session_state.won = False

# 5. MAIN LOGIC
if api_key:
    genai.configure(api_key=api_key)
    try:
        # Choose the model
        m_name = 'models/gemini-1.5-flash'
        
        # Create Tabs
        tab_setup, tab_play = st.tabs(["🎓 Setup", "🎮 Play"])

        # TEACHER SETUP TAB
        with tab_setup:
            st.subheader("Add a Level to the Lesson")
            folder_choice = st.selectbox("Select a Folder", list(PREMADE.keys()))
            level_data = PREMADE[folder_choice]
            
            # Show preview
            try:
                st.image(level_data["path"], width=300)
                if st.button(f"Add {folder_choice} to Game Queue"):
                    st.session_state.queue.append(level_data)
                    st.success(f"{folder_choice} added!")
            except:
                st.error(f"Cannot find {level_data['path']} on GitHub.")

            if st.session_state.queue:
                st.divider()
                if st.button("🗑️ Reset All Levels"):
                    st.session_state.queue = []
                    st.session_state.idx = 0
                    st.rerun()

        # STUDENT PLAY TAB
        with tab_play:
            if not st.session_state.queue:
                st.info("Teacher: Please add a level in the Setup tab first.")
            else:
                current_idx = st.session_state.idx
                # Loop safety
                if current_idx >= len(st.session_state.queue):
                    current_idx = 0
                    st.session_state.idx = 0
                
                lvl = st.session_state.queue[current_idx]

                # Start AI Chat for this specific level
                if "chat" not in st.session_state or st.session_state.get("current_lvl_id") != current_idx:
                    rules = f"You are a teacher. Target: {lvl['target']}. Correct Answer: {lvl['ans']}. If they get it right, say 'CORRECT!'. If wrong, give a hint."
                    model = genai.GenerativeModel(model_name=m_name, system_instruction=rules)
                    st.session_state.chat = model.start_chat(history=[])
                    st.session_state.history = [{"role": "ai", "content": f"Can you find {lvl['target']}?"}]
                    st.session_state.current_lvl_id = current_idx
                    st.session_state.won = False

                col1, col2 = st.columns(2)
                
                with col1:
                    st.image(lvl["path"], use_container_width=True)
                    if st.session_state.won:
                        if current_idx < len(st.session_state.queue) - 1:
                            if st.button("Next Level ➡️"):
                                st.session_state.idx += 1
                                st.rerun()
                        else:
                            st.balloons()
                            st.success("You finished all the levels! Great job!")

                with col2:
                    for m in st.session_state.history:
                        st.chat_message(m["role"]).write(m["content"])
                    
                    if not st.session_state.won:
                        user_input = st.chat_input("Where is it?", key=f"input_{current_idx}")
                        if user_input:
                            st.session_state.history.append({"role": "user", "content": user_input})
                            ai_response = st.session_state.chat.send_message(user_input).text
                            st.session_state.history.append({"role": "ai", "content": ai_response})
                            if "CORRECT

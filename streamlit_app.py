import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="I Spy Game", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

# API Key Sidebar
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# Game Levels - Matching your ALL CAPS folders exactly
PREMADE = {
    "BEDROOM": {"path": "BEDROOM/bedroom.jpg", "target": "The Golden Star", "ans": "ON the bed"},
    "KITCHEN": {"path": "KITCHEN/kitchen1.jpg", "target": "The Golden Star", "ans": "UNDER the table"},
    "PLAYGROUND": {"path": "PLAYGROUND/playground.jpg", "target": "The Golden Star", "ans": "BEHIND the slide"}
}

# State Management
if "queue" not in st.session_state: st.session_state.queue = []
if "idx" not in st.session_state: st.session_state.idx = 0
if "won" not in st.session_state: st.session_state.won = False

if api_key:
    genai.configure(api_key=api_key)
    try:
        t_setup, t_play = st.tabs(["🎓 Setup", "🎮 Play"])

        with t_setup:
            st.subheader("Add Level")
            folder = st.selectbox("Select Folder", list(PREMADE.keys()))
            data = PREMADE[folder]
            st.image(data["path"], width=300)
            if st.button("Add to Game"):
                st.session_state.queue.append(data)
                st.success("Added!")
            if st.session_state.queue:
                if st.button("Reset Game"):
                    st.session_state.queue = []
                    st.session_state.idx = 0
                    st.rerun()

        with t_play:
            if not st.session_state.queue:
                st.info("Please add a level in Setup first.")
            else:
                idx = st.session_state.idx
                if idx >= len(st.session_state.queue): idx = 0
                lvl = st.session_state.queue[idx]

                if "chat" not in st.session_state or st.session_state.get("last_lvl") != idx:
                    sys = f"Teacher. Target: {lvl['target']}. Answer: {lvl['ans']}. Be short."
                    model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=sys)
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
                            st.rerun()
                with c2:
                    for m in st.session_state.history:
                        st.chat_message(m["role"]).write(m["content"])
                    if not st.session_state.won:
                        if p := st.chat_input("Answer here:", key=f"in_{idx}"):
                            st.session_state.history.append({"role": "user", "content": p})
                            res = st.session_state.chat.send_message(p).text
                            st.session_state.history.append({"role": "ai", "content": res})
                            if "CORRECT" in res.upper(): st.session_state.won = True
                            st.rerun()

    except Exception as e: st.error(f"Error: {e}")
else:
    st.warning("Enter your API Key in the sidebar.")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

api_key = st.sidebar.text_input("Teacher API Key", type="password")

# =========================================================
# STEP 3: UPDATE THIS SECTION TO MATCH YOUR GITHUB FILES
# =========================================================
PREMADE_LEVELS = {
    "1. Bedroom": {
        "Star on Bed": {
            "image_path": "Bedroom/bed1.jpg", 
            "room_name": "Bedroom",
            "items_in_room": "a bed, a desk, and a rug",
            "target_item": "The Golden Star",
            "secret_location": "ON the bed"
        }
    },
    "2. Kitchen": {
        "Star under Table": {
            "image_path": "Kitchen/kitchen1.jpg",
            "room_name": "Kitchen",
            "items_in_room": "a fridge and a table",
            "target_item": "The Golden Star",
            "secret_location": "UNDER the table"
        }
    }
}

# --- APP LOGIC STARTS HERE ---
if "custom_levels" not in st.session_state:
    st.session_state.custom_levels = []

if api_key:
    genai.configure(api_key=api_key)
    try:
        # Check for model
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]

        tab1, tab2 = st.tabs(["🎓 Teacher Setup", "🎮 Student Game"])
        
        with tab1:
            st.header("Step 1: Add Levels to the Game")
            setup_method = st.radio("Choose method:", ["A) Visual Gallery", "B) Custom Upload"])
            
            if setup_method == "A) Visual Gallery":
                cat = st.selectbox("📂 Folder:", list(PREMADE_LEVELS.keys()))
                levels = list(PREMADE_LEVELS[cat].items())
                for i in range(0, len(levels), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(levels):
                            name, data = levels[i+j]
                            with cols[j]:
                                st.image(data["image_path"], caption=name, use_container_width=True)
                                if st.button(f"Add {name}", key=name):
                                    st.session_state.custom_levels.append(data)
                                    st.success(f"Added {name}!")

            elif setup_method == "B) Custom Upload":
                up = st.file_uploader("Upload Image", type=["jpg", "png"])
                if up:
                    st.image(up, width=300)
                    t_room = st.text_input("Room Name")
                    t_target = st.text_input("Hidden Item")
                    t_secret = st.text_input("Secret Location (The Answer)")
                    if st.button("Save Custom Level"):
                        st.session_state.custom_levels.append({
                            "image_bytes": up.getvalue(), "room_name": t_room,
                            "target_item": t_target, "secret_location": t_secret, "items_in_room": "various objects"
                        })
            
            if st.button("🗑️ Clear All Levels"):
                st.session_state.custom_levels = []
                st.rerun()

        with tab2:
            if not st.session_state.custom_levels:
                st.info("Waiting for teacher to add levels...")
            else:
                idx = st.session_state.get("lvl_idx", 0)
                lvl = st.session_state.custom_levels[idx]
                
                # AI Setup
                if "chat" not in st.session_state or st.session_state.get("last_lvl") != idx:
                    rules = f"Game: I Spy. Room: {lvl['room_name']}. Hidden: {lvl['target_item']}. ANSWER: {lvl['secret_location']}. If student is correct, say 'CORRECT! 🎉 You found it!'. Otherwise give a tiny hint."
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=rules)
                    st.session_state.chat = model.start_chat(history=[])
                    st.session_state.msgs = [{"role": "ai", "content": f"Can you find {lvl['target_item']}?"}]
                    st.session_state.last_lvl = idx
                    st.session_state.won = False

                c1, c2 = st.columns(2)
                with c1:
                    st.image(lvl.get("image_bytes") or lvl["image_path"], use_container_width=True)
                    if st.session_state.won and idx < len(st.session_state.custom_levels)-1:
                        if st.button("Next Level"):
                            st.session_state.lvl_idx = idx + 1
                            st.rerun()

                with c2:
                    for m in st.session_state.msgs:
                        st.chat_message(m["role"]).write(m["content"])
                    if not st.session_state.won:
                        if p := st.chat_input("I think it is..."):
                            st.session_state.msgs.append({"role": "user", "content": p})
                            r = st.session_state.chat.send_message(p).text
                            st.session_state.msgs.append({"role": "ai", "content": r})
                            if "CORRECT!" in r.upper(): st.session_state.won = True
                            st.rerun()

    except Exception as e: st.error(f"Error: {e}")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")
st.divider()

# Sidebar for API Key
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# =========================================================
# PRE-MADE LEVELS (MATCHING YOUR GITHUB SCREENSHOT)
# =========================================================
PREMADE_LEVELS = {
    "1. BEDROOM": {
        "Level 1: The Bedroom": {
            "image_path": "BEDROOM/bedroom.jpg", 
            "room_name": "Bedroom",
            "items_in_room": "a bed, a desk, and a rug",
            "target_item": "The Golden Star",
            "secret_location": "ON the bed"
        }
    },
    "2. KITCHEN": {
        "Level 2: The Kitchen": {
            "image_path": "KITCHEN/kitchen1.jpg",
            "room_name": "Kitchen",
            "items_in_room": "a fridge, an oven, and a table",
            "target_item": "The Golden Star",
            "secret_location": "UNDER the table"
        }
    },
    "3. PLAYGROUND": {
        "Level 3: The Playground": {
            "image_path": "PLAYGROUND/playground.jpg",
            "room_name": "Playground",
            "items_in_room": "a slide, a swing set, and a sandbox",
            "target_item": "The Golden Star",
            "secret_location": "BEHIND the slide"
        }
    }
}

# --- DYNAMIC LEVEL STORAGE ---
if "custom_levels" not in st.session_state:
    st.session_state.custom_levels = []

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        # Check for available Gemini models
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]

        tab1, tab2 = st.tabs(["🎓 Teacher Setup", "🎮 Student Game"])
        
        # ==========================================
        # TAB 1: TEACHER SETUP
        # ==========================================
        with tab1:
            st.header("Step 1: Add Levels to the Game")
            
            setup_method = st.radio("Choose how to add a level:", 
                                    ["A) Visual Gallery (Pre-made)", "B) Upload a Custom Image"])
            st.divider()
            
            if setup_method == "A) Visual Gallery (Pre-made)":
                selected_category = st.selectbox("📂 Choose a Folder:", list(PREMADE_LEVELS.keys()))
                st.markdown(f"### 🖼️ Images inside {selected_category}")
                
                levels_in_category = list(PREMADE_LEVELS[selected_category].items())
                
                for i in range(0, len(levels_in_category), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(levels_in_category):
                            level_name, level_data = levels_in_category[i+j]
                            with cols[j]:
                                st.markdown(f"#### {level_name}")
                                try:
                                    st.image(level_data["image_path"], use_container_width=True)
                                    st.write(f"🎯 **Target:** {level_data['target_item']}")
                                    st.write(f"📍 **Answer:** {level_data['secret_location']}")
                                    
                                    if st.button(f"💾 Add to Game", key=f"btn_{level_name}"):
                                        st.session_state.custom_levels.append(level_data.copy())
                                        st.success(f"Added! Total levels: {len(st.session_state.custom_levels)}")
                                except:
                                    st.error(f"⚠️ File not found: {level_data['image_path']}. Check folders!")

            elif setup_method == "B) Upload a Custom Image":
                uploaded_image = st.file_uploader("Upload Picture", type=["jpg", "png"])
                if uploaded_image:
                    st.image(uploaded_image, width=300)
                    t_room = st.text_input("Room Name")
                    t_target = st.text_input("Hidden Item")
                    t_secret = st.text_input("Where is it?")
                    
                    if st.button("💾 Save Custom Level"):
                        st.session_state.custom_levels.append({
                            "image_bytes": uploaded_image.getvalue(),
                            "room_name": t_room,
                            "target_item": t_target,
                            "secret_location": t_secret,
                            "items_in_room": "various objects"
                        })
                        st.success("✅ Saved!")

            if st.session_state.custom_levels:
                st.divider()
                if st.button("🗑️ Clear All Selected Levels"):
                    st.session_state.custom_levels = []
                    st.rerun()

        # ==========================================
        # TAB 2: THE STUDENT GAME
        # ==========================================
        with tab2:
            if not st.session_state.custom_levels:
                st.info("👋 Teacher, please add levels in 'Teacher Setup' first!")
            else:
                if "lvl_idx" not in st.session_state:
                    st.session_state.lvl_idx = 0
                    st.session_state.won = False

                idx = st.session_state.lvl_idx
                lvl = st.session_state.custom_levels[idx]

                if "chat" not in st.session_state or st.session_state.get("last_lvl_id") != idx:
                    sys_prompt = f"Game: I Spy. Room: {lvl['room_name']}. Target: {lvl['target_item']}. ANSWER: {lvl['secret_location']}. If correct, say 'CORRECT! 🎉 You found it!'. Otherwise, give a tiny hint."
                    model = genai.GenerativeModel(

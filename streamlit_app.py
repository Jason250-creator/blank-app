import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")
st.divider()

# Sidebar for API Key
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# =========================================================
# PRE-MADE LEVELS (MATCHED TO YOUR GITHUB SCREENSHOT)
# =========================================================
PREMADE_LEVELS = {
    "1. BEDROOM": {
        "Level 1: The Bedroom": {
            "image_path": "BEDROOM/bedroom.jpg", 
            "room_name": "Bedroom",
            "target_item": "The Golden Star",
            "secret_location": "ON the bed"
        }
    },
    "2. KITCHEN": {
        "Level 2: The Kitchen": {
            "image_path": "KITCHEN/kitchen1.jpg", 
            "room_name": "Kitchen",
            "target_item": "The Golden Star",
            "secret_location": "UNDER the table"
        }
    },
    "3. PLAYGROUND": {
        "Level 3: The Playground": {
            "image_path": "PLAYGROUND/playground.jpg", 
            "room_name": "Playground",
            "target_item": "The Golden Star",
            "secret_location": "BEHIND the slide"
        }
    }
}

# --- INITIALIZE SESSION STATE ---
if "custom_levels" not in st.session_state:
    st.session_state.custom_levels = []
if "lvl_idx" not in st.session_state:
    st.session_state.lvl_idx = 0
if "won" not in st.session_state:
    st.session_state.won = False

if api_key:
    genai.configure(api_key=api_key)
    
    try:
        # Get Model Name
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]

        tab1, tab2 = st.tabs(["🎓 Teacher Setup", "🎮 Student Game"])
        
        # ==========================================
        # TAB 1: TEACHER SETUP
        # ==========================================
        with tab1:
            st.header("Step 1: Add Levels to the Game")
            setup_method = st.radio("Choose how to add a level:", ["A) Visual Gallery", "B) Custom Upload"])
            st.divider()
            
            if setup_method == "A) Visual Gallery":
                cat = st.selectbox("📂 Choose a Folder:", list(PREMADE_LEVELS.keys()))
                levels = list(PREMADE_LEVELS[cat].items())
                
                for i in range(0, len(levels), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(levels):
                            name, data = levels[i+j]
                            with cols[j]:
                                st.markdown(f"#### {name}")
                                try:
                                    st.image(data["image_path"], use_container_width=True)
                                    st.write(f"🎯 **Target:** {data['target_item']}")
                                    st.write(f"📍 **Answer:** {data['secret_location']}")
                                    if st.button(f"Add {name}", key=f"btn_{name}"):
                                        st.session_state.custom_levels.append(data.copy())
                                        st.success("Added to game!")
                                except:
                                    st.error(f"Missing: {data['image_path']}")

            elif setup_method == "B) Custom Upload":
                up = st.file_uploader("Upload Picture", type=["jpg", "png"])
                if up:
                    st.image(up, width=300)
                    r = st.text_input("Room Name")
                    t = st.text_input("Hidden Item")
                    s = st.text_input("Secret Location")
                    if st.button("Save Level"):
                        st.session_state.custom_levels.append({"image_bytes": up.getvalue(), "room_name": r, "target_item": t, "secret_location": s})
                        st.success("Saved!")

            if st.session_state.custom_levels:
                if st.button("🗑️ Clear Game Queue"):
                    st.session_state.custom_levels = []
                    st.rerun()

        # ==========================================
        # TAB 2: THE STUDENT GAME
        # ==========================================
        with

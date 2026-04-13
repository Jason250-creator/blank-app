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
                selected_category = st.selectbox

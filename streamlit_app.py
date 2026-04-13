import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")
st.divider()

api_key = st.sidebar.text_input("Teacher API Key", type="password")

# --- CATEGORIZED PRE-MADE LEVELS ---
# Notice how the image_path now includes the folder name!
PREMADE_LEVELS = {
    "1. Bedroom": {
        "Level 1: On the Rug": {
            "image_path": "Bedroom/bedroom1.jpg", 
            "room_name": "Bedroom",
            "items_in_room": "a bed, a desk, and a rug",
            "target_item": "The Golden Star",
            "secret_location": "ON the rug"
        }
    },
    "2. Kitchen": {
        "Level 2: Under the Table": {
            "image_path": "Kitchen/kitchen1.jpg",
            "room_name": "Kitchen",
            "items_in_room": "a fridge, an oven, and a table",
            "target_item": "The Golden Star",
            "secret_location": "UNDER the table"
        }
    },
    "3. Playground": {
        "Level 3: Behind the Slide": {
            "image_path": "Playground/playground1.jpg",
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
        # --- THE MODEL SCANNER ---
        if "model_name" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if 'models/gemini-1.5-flash' in available_models:
                st.session_state.model_name = 'models/gemini-1.5-flash'
            elif 'models/gemini-pro' in available_models:
                st.session_state.model_name = 'models/gemini-pro'
            else:
                st.session_state.model_name = available_models[0] if available_models else None

        if st.session_state.model_name:
            
            # --- CREATE THE TWO TABS ---
            tab1, tab2 = st.tabs(["🎓 Teacher Setup", "🎮 Student Game"])
            
            # ==========================================
            # TAB 1: TEACHER SETUP
            # ==========================================
            with tab1:
                st.header("Step 1: Add Levels to the Game")
                
                setup_method = st.radio("Choose how to add a level:", 
                                        ["A) Use a Pre-made Level (Instant)", "B) Upload a Custom Image"])
                
                st.divider()
                
                # OPTION A: PRE-MADE (NOW WITH CATEGORIES)
                if setup_method == "A) Use a Pre-made Level (Instant)":
                    
                    # 1. Pick the Folder
                    selected_category = st.selectbox("📂 Choose a Location Category:", list(PREMADE_LEVELS.keys()))
                    
                    # 2. Pick the Level inside that Folder
                    selected_premade = st.selectbox("🖼️ Choose a Level Template:", list(PREMADE_LEVELS[selected_category].keys()))
                    
                    level_data = PREMADE_LEVELS[selected_category][selected_premade]
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        try:
                            st.image(level_data["image_path"], width=300)
                        except:
                            st.warning(f"⚠️ Please make sure '{level_data['image_path']}' is uploaded to your GitHub repository.")
                    with col2:
                        st.write(f"**Room:** {level_data['room_name']}")
                        st.write(f"**Target:** {level_data['target_item']}")
                        st.write(f"**Answer:** {level_data['secret_location']}")
                        
                        if st.button("💾 Add Pre-made Level to Game"):
                            new_level = level_data.copy()
                            new_level["level"] = len(st.session_state.custom_levels) + 1
                            st.session_state.custom_levels.append(new_level)
                            st.success("✅ Level added! You can add another or go to the Student Game tab.")

                # OPTION B: CUSTOM UPLOAD
                elif setup_method == "B) Upload a Custom Image":
                    uploaded_image = st.file_uploader("Upload Room Picture (JPG/PNG)", type=["jpg", "jpeg", "png"])
                    
                    if uploaded_image:
                        st.image(uploaded_image, width=300)
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            t_room = st.text_input("Room Name (e.g., Garden)")
                            t_items = st.text_input("Items visible (e.g., tree, bench)")
                        with col_b:
                            t_target = st.text_input("Hidden Item (e.g., The Golden Star)")
                            t_secret = st.text_input("Where is it? (e.g., BEHIND the tree)")
                        
                        if st.button("💾 Save Custom Level to Game"):
                            if t_room and t_target and t_secret:
                                new_level = {
                                    "level": len(st.session_state.custom_levels) + 1,
                                    "image_bytes": uploaded_image.getvalue(),
                                    "room_name": t_room,
                                    "target_item": t_target,
                                    "secret_location": t_secret,
                                    "items_in_room": t_items
                                }
                                st.session_state.custom_levels.append(new_level)
                                st.success("✅ Custom Level added! You can add another or go to the Student Game tab.")
                            else:
                                st.warning("Please fill out all the text boxes before saving.")
                                
                # SHOW SAVED LEVELS
                if len(st.session_state.custom_levels) > 0:
                    st.divider()
                    st.subheader(f"Current Levels Queued: {len(st.session_state.custom_levels)}")
                    if st.button("🗑️ Clear All Levels"):
                        st.session_state.custom_levels = []
                        st.rerun()

            # ==========================================
            # TAB 2: THE STUDENT GAME
            # ==========================================
            with tab2:
                if len(st.session_state.custom_levels) == 0:
                    st.info("👋 Welcome! Ask the teacher to set up a level in the Teacher Setup tab first.")
                else:
                    game_col1, game_col2 = st.columns([1, 1])
                    
                    if "current_level_index" not in st.session_state:
                        st.session_state.current_level_index = 0
                        st.session_state.won_level = False

                    if st.session_state.current_level_index >= len(st.session_state.custom_levels):
                        st.session_state.current_level_index = 0

                    current_level_data = st.session_state.custom_levels[st.session_state.current_level_index]

                    # Setup AI Brain
                    if "chat" not in st.session_state or st.session_state.get("last_level") != st.session_state.current_level_index:
                        system_rules = f"""
                        You are a fun teacher playing a hidden object game with a 10-year-old.
                        The student is looking at a picture of a {current_level_data['room_name']}. 
                        
                        SECRET DETAILS:
                        - Items visible: {current_level_data['items_in_room']}.
                        - THE HIDDEN ITEM IS: **{current_level_data['secret_location']}**.
                        
                        RULES:
                        1. The student must guess the location of {current_level_data['target_item']} using a preposition.
                        2. If wrong, say: "Sorry, try again! 💡 Tip: " and give a small hint.
                        3. If right, you MUST say exactly: "CORRECT! 🎉 You found it!" 
                        4. Keep your answers to 1 or 2 short sentences.
                        """
                        
                        model = genai.GenerativeModel(
                            model_name=st.session_state.model_name,
                            system_instruction=system_rules
                        )
                        st.session_state.chat = model.start_chat(history=[])
                        st.session_state.messages = [{"role": "ai", "content": f"Welcome to Level {current_level_data['level']}! Can you find {current_level_data['target_item']}? Where is it?"}]
                        st.session_state.last_level = st.session_state.current_level_index
                        st.session_state.won_level = False

                    with game_col1:
                        st.subheader(f"Level {current_level_data['level']}: {current_level_data['room_name']}")
                        
                        try:
                            if "image_bytes" in current_level_data:
                                st.image(current_level_data['image_bytes'], use_container_width=True)
                            else:
                                st.image(current_level_data['image_path'], use_container_width=True)
                        except:
                            st.warning("⚠️ Image could not be loaded. Please ensure it is uploaded to the correct folder in GitHub.")
                            
                        if st.session_state.won_level:
                            if st.session_state.current_level_index < len(st.session_state.custom_levels) - 1:
                                if st.button("➡️ Go to Next Level!"):
                                    st.session_state.current_level_index += 1
                                    st.rerun()
                            else:
                                st.success("🏆 YOU BEAT ALL THE LEVELS! YOU WIN!")

                    with game_col2:
                        st.subheader("Your Guesses")
                        for msg in st.session_state.messages:
                            st.chat_message(msg["role"]).write(msg["content"])

                        if not st.session_state.won_level:
                            if prompt := st.chat_input("I think it is..."):
                                st.session_state.messages.append({"role": "user", "content": prompt})
                                response = st.session_state.chat.send_message(prompt)
                                st.session_state.messages.append({"role": "ai", "content": response.text})
                                
                                if "CORRECT!" in response.text.upper():
                                    st.session_state.won_level = True
                                
                                st.rerun()
        else:
            st.error("No valid AI models found for this API Key!")

    except Exception as e:
        st.error("⚠️ Oops! Google rejected your API Key. Please make sure you copied it perfectly.")

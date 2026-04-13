import streamlit as st
import google.generativeai as genai
import urllib.parse
import requests
import random

# --- Page Config ---
st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("✨ I Spy: The Teacher's Dashboard")
st.divider()

api_key = st.sidebar.text_input("Teacher API Key", type="password")

# --- Game Levels Data (Gallery Fallbacks) ---
PREMADE = {
    "BEDROOM": {"path": "BEDROOM/bedroom.jpg", "target": "The Golden Star", "ans": "ON the bed", "items": "a bed, a desk, a rug"},
    "KITCHEN": {"path": "KITCHEN/kitchen1.jpg", "target": "The Golden Star", "ans": "UNDER the table", "items": "a table, a fridge, chairs"},
    "PLAYGROUND": {"path": "PLAYGROUND/playground.jpg", "target": "The Golden Star", "ans": "BEHIND the slide", "items": "a slide, a swing, a sandbox"}
}

# --- State Management ---
if "custom_levels" not in st.session_state:
    st.session_state.custom_levels = []

if not api_key:
    st.warning("Please enter your API Key in the sidebar.")
else:
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
            tab1, tab2 = st.tabs(["🪄 Teacher Setup", "🎮 Student Game"])
            
            # ==========================================
            # TAB 1: TEACHER SETUP
            # ==========================================
            with tab1:
                st.header("Step 1: Add a Level")
                method = st.radio("Choose a method:", ["Gallery", "Upload", "Magic AI ✨"])
                st.divider()

                # -------------------------
                # OPTION A: GALLERY
                # -------------------------
                if method == "Gallery":
                    folder = st.selectbox("Select Folder", list(PREMADE.keys()))
                    data = PREMADE[folder]
                    st.image(data["path"], width=300)
                    if st.button("💾 Add Gallery Level to Game"):
                        st.session_state.custom_levels.append({
                            "level": len(st.session_state.custom_levels) + 1,
                            "image_data": data["path"], # Path works fine for Streamlit
                            "room_name": folder,
                            "target_item": data["target"],
                            "secret_location": data["ans"],
                            "items_in_room": data["items"]
                        })
                        st.success(f"{folder} added!")

                # -------------------------
                # OPTION B: UPLOAD
                # -------------------------
                elif method == "Upload":
                    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        u_room = st.text_input("Room Name (e.g. My Classroom)")
                        u_items = st.text_input("Items visible (e.g. desks, whiteboard)")
                    with col_u2:
                        u_target = st.text_input("Hidden item (e.g. The red apple)")
                        u_secret = st.text_input("Secret Answer (e.g. ON the desk)")
                    
                    if st.button("💾 Add Uploaded Level to Game"):
                        if uploaded_file and u_room and u_items and u_target and u_secret:
                            st.session_state.custom_levels.append({
                                "level": len(st.session_state.custom_levels) + 1,
                                "image_data": uploaded_file.getvalue(), # Raw bytes
                                "room_name": u_room,
                                "target_item": u_target,
                                "secret_location": u_secret,
                                "items_in_room": u_items
                            })
                            st.success("Uploaded level added!")
                        else:
                            st.warning("Please upload a picture and fill out all boxes.")

                # -------------------------
                # OPTION C: MAGIC AI
                # -------------------------
                elif method == "Magic AI ✨":
                    st.info("Type what you want, and the AI will draw it! Warning: AI sometimes gets prepositions wrong. If the picture doesn't match your rule, just click Generate again!")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        t_room = st.text_input("Room Theme", value="A Minecraft bedroom")
                        t_items = st.text_input("Other items in the room", value="a bed, a desk, a rug")
                    with col_b:
                        t_target = st.text_input("The Hidden Item", value="A golden star")
                        t_secret = st.text_input("Where is it hidden?", value="UNDER the table")
                    
                    if st.button("✨ Generate Magic Image", type="primary"):
                        if t_room and t_target and t_secret and t_items:
                            with st.spinner("🎨 AI is drawing your picture. This takes about 5 seconds..."):
                                image_prompt = f"{t_room}. It has {t_items}. There is {t_target} exactly {t_secret}."
                                encoded_prompt = urllib.parse.quote(image_prompt)
                                seed = random.randint(1, 100000)
                                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=800&height=600&nologo=true"
                                
                                try:
                                    response = requests.get(image_url)
                                    if response.status_code == 200:
                                        st.session_state.temp_image = response.content
                                        st.session_state.temp_details = {
                                            "room_name": t_room,
                                            "items_in_room": t_items,
                                            "target_item": t_target,
                                            "secret_location": t_secret
                                        }
                                    else:
                                        st.error("Failed to generate image. The drawing servers might be busy!")
                                except Exception as e:
                                    st.error("Error connecting to image generator.")
                        else:
                            st.warning("Please fill out all 4 boxes first!")

                    # SHOW THE GENERATED IMAGE PREVIEW AND SAVE IT
                    if "temp_image" in st.session_state:
                        st.divider()
                        st.subheader("Does the picture match your rule?")
                        st.image(st.session_state.temp_image, width=500)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Yes! Save Level to Game"):
                                new_level = {
                                    "level": len(st.session_state.custom_levels) + 1,
                                    "image_data": st.session_state.temp_image,
                                    "room_name": st.session_state.temp_details["room_name"],
                                    "target_item": st.session_state.temp_details["target_item"],
                                    "secret_location": st.session_state.temp_details["secret_location"],
                                    "items_in_room": st.session_state.temp_details["items_in_room"]
                                }
                                st.session_state.custom_levels.append(new_level)
                                del st.session_state.temp_image
                                del st.session_state.temp_details
                                st.rerun()
                        with col2:
                            st.markdown("*(If it looks wrong, just scroll up and click Generate again!)*")

                # SHOW SAVED LEVELS LIST
                if len(st.session_state.custom_levels) > 0:
                    st.divider()
                    st.success(f"🎉 Current Levels Ready to Play: {len(st.session_state.custom_levels)}")
                    if st.button("🗑️ Clear All Levels"):
                        st.session_state.custom_levels = []
                        st.session_state.current_level_index = 0
                        st.rerun()

            # ==========================================
            # TAB 2: THE STUDENT GAME
            # ==========================================
            with tab2:
                if len(st.session_state.custom_levels) == 0:
                    st.warning("⚠️ Waiting for the teacher to set up a level in the Teacher Dashboard!")
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
                        1. The student must guess the location of the {current_level_data['target_item']} using a preposition.
                        2. If wrong, say: "Sorry, try again! 💡 Tip: " and give a small hint.
                        3. If right, you MUST say exactly: "CORRECT! 🎉 You found it!" 
                        4. Keep your answers to 1 or 2 short sentences.
                        """
                        
                        model = genai.GenerativeModel(
                            model_name=st.session_state.model_name,
                            system_instruction=system_rules
                        )
                        st.session_state.chat = model.start_chat(history=[])
                        st.session_state.messages = [{"role": "ai", "content": f"Welcome to Level {current_level_data['level']}! Can you find the {current_level_data['target_item']}? Where is it?"}]
                        st.session_state.last_level = st.session_state.current_level_index
                        st.session_state.won_level = False

                    with game_col1:
                        st.subheader(f"Level {current_level_data['level']}: {current_level_data['room_name']}")
                        st.image(current_level_data['image_data'], use_container_width=True)
                            
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
                                try:
                                    response = st.session_state.chat.send_message(prompt)
                                    st.session_state.messages.append({"role": "ai", "content": response.text})
                                    
                                    if "CORRECT!" in response.text.upper():
                                        st.session_state.won_level = True
                                    
                                    st.rerun()
                                except Exception as e:
                                    if "429" in str(e):
                                        st.error("API is taking a break. Wait a few seconds.")
                                    else:
                                        st.error(f"Chat Error: {e}")
                                        
        else:
            st.error("No valid AI models found for this API Key!")

    except Exception as e:
        st.error("⚠️ Oops! Google rejected your API Key. Please make sure you copied it perfectly.")

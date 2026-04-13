import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("🔍 I Spy: The Hidden Star")
st.divider()

col1, col2 = st.columns([1, 1])
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# --- LEVEL DATA ---
levels = [
    {
        "level": 1,
        "image": "bedroom.jpg", 
        "room_name": "Bedroom",
        "secret_location": "UNDER the table", 
        "items_in_room": "a bed, a table, and a rug" 
    }
]

if api_key:
    genai.configure(api_key=api_key)
    
    # --- THE MODEL SCANNER ---
    if "model_name" not in st.session_state:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in available_models:
            st.session_state.model_name = 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            st.session_state.model_name = 'models/gemini-pro'
        else:
            st.session_state.model_name = available_models[0] if available_models else None

    # Proceed only if we found a working model
    if st.session_state.model_name:
        
        # 1. Track the current level
        if "current_level_index" not in st.session_state:
            st.session_state.current_level_index = 0
            st.session_state.won_level = False

        current_level_data = levels[st.session_state.current_level_index]

        # 2. Setup the AI Brain for the SPECIFIC room
        if "chat" not in st.session_state or st.session_state.get("last_level") != st.session_state.current_level_index:
            
            # HERE ARE YOUR NEW RULES, IN THE CORRECT SPOT!
            system_rules = f"""
            You are a fun teacher playing a hidden object game with a 10-year-old.
            The student is looking at a picture of a {current_level_data['room_name']}. 
            
            SECRET DETAILS:
            - Items visible: {current_level_data['items_in_room']}.
            - THE HIDDEN ITEM IS: **{current_level_data['secret_location']}**.
            
            RULES:
            1. The student must guess the location using a preposition (in, on, under, behind, etc.).
            2. If they guess wrong, say: "Sorry, try again! 💡 Tip: " and give them a small hint about where it is, without giving away the exact answer. (e.g., "It's near the floor" or "It's not near the bed").
            3. If they guess right, you MUST say exactly: "CORRECT! 🎉 You found it!" 
            4. Keep your answers to 1 or 2 short sentences.
            """
            
            model = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                system_instruction=system_rules
            )
            st.session_state.chat = model.start_chat(history=[])
            st.session_state.messages = [{"role": "ai", "content": f"Welcome to Level {current_level_data['level']}: The {current_level_data['room_name']}! Can you find the Golden Star? Where is it?"}]
            st.session_state.last_level = st.session_state.current_level_index
            st.session_state.won_level = False

        # --- LEFT COLUMN: THE IMAGE ---
        with col1:
            st.subheader(f"Level {current_level_data['level']}: {current_level_data['room_name']}")
            try:
                st.image(current_level_data['image'], use_container_width=True)
            except:
                st.warning(f"⚠️ Teacher: Please upload '{current_level_data['image']}' to GitHub!")
                
            # Show a "Next Level" button if they win!
            if st.session_state.won_level:
                if st.session_state.current_level_index < len(levels) - 1:
                    if st.button("➡️ Go to Next Level!"):
                        st.session_state.current_level_index += 1
                        st.rerun()
                else:
                    st.success("🏆 YOU BEAT ALL THE LEVELS! YOU WIN!")

        # --- RIGHT COLUMN: THE CHAT ---
        with col2:
            st.subheader("Your Guesses")
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if not st.session_state.won_level:
                if prompt := st.chat_input("I think the star is..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = st.session_state.chat.send_message(prompt)
                    st.session_state.messages.append({"role": "ai", "content": response.text})
                    
                    # Check if the AI said they won
                    if "CORRECT!" in response.text.upper():
                        st.session_state.won_level = True
                    
                    st.rerun()
    else:
        st.error("No valid AI models found for this API Key!")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="I Spy: Preposition Edition", layout="wide")
st.title("🔍 I Spy: The Hidden Key")
st.divider()

col1, col2 = st.columns([1, 1])
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# --- LEVEL DATA ---
# You can add as many levels as you want right here!
levels = [
    {
        "level": 1,
        "image": "bedroom.jpg", 
        "room_name": "Bedroom",
        "secret_location": "UNDER the bed",
        "items_in_room": "a bed, a desk with books, and a rug"
    },
    {
        "level": 2,
        "image": "kitchen.jpg", 
        "room_name": "Kitchen",
        "secret_location": "IN the fridge",
        "items_in_room": "a fridge, a table, plates, and an oven"
    },
    {
        "level": 3,
        "image": "garden.jpg", 
        "room_name": "Garden",
        "secret_location": "BEHIND the big tree",
        "items_in_room": "a big tree, some flowers, a bench, and a fountain"
    }
]

if api_key:
    genai.configure(api_key=api_key)
    
    # 1. Track the current level
    if "current_level_index" not in st.session_state:
        st.session_state.current_level_index = 0
        st.session_state.won_level = False

    current_level_data = levels[st.session_state.current_level_index]

    # 2. Setup the AI Brain for the SPECIFIC room
    if "chat" not in st.session_state or st.session_state.get("last_level") != st.session_state.current_level_index:
        
        system_rules = f"""
        You are a fun teacher playing a hidden object game with a 10-year-old.
        The student is looking at a picture of a {current_level_data['room_name']}. 
        
        SECRET DETAILS:
        - Items visible: {current_level_data['items_in_room']}.
        - THE GOLDEN KEY IS: **{current_level_data['secret_location']}**.
        
        RULES:
        1. The student must guess the location using a preposition (in, on, under, behind, etc.).
        2. If wrong, say: "Good guess, but no! Try again!" (Mention something else in the room).
        3. If right, say exactly: "CORRECT! 🎉 You found it!" 
        """
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_rules
        )
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.messages = [{"role": "ai", "content": f"Welcome to Level {current_level_data['level']}: The {current_level_data['room_name']}! Where is the key?"}]
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
            if prompt := st.chat_input("I think the key is..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                response = st.session_state.chat.send_message(prompt)
                st.session_state.messages.append({"role": "ai", "content": response.text})
                
                # Check if the AI said they won
                if "CORRECT!" in response.text.upper():
                    st.session_state.won_level = True
                
                st.rerun()

import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="Preposition Quest", page_icon="⚔️")
st.title("⚔️ Preposition Quest: AI Dungeon")
st.write("Year 4: Use **IN, ON, UNDER, BEHIND, NEXT TO, or BETWEEN** to survive!")
st.divider()

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
api_key = st.sidebar.text_input("Paste API Key", type="password")

# 3. The Game Logic
if api_key:
    try:
        # We tell the system to use the stable 'v1' instead of 'v1beta'
        genai.configure(api_key=api_key, transport='grpc')
        
        if "chat" not in st.session_state:
            # Using the most standard, stable model name
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            st.session_state.chat = model.start_chat(history=[])
            
            # This is the "Dungeon Master" setup
            system_prompt = (
                "You are an epic Dungeon Master for 10-year-olds. "
                "The setting is a MAGICAL CASTLE. Starting room: A stone room with a TALL STATUE, "
                "a SHINY SHIELD on the wall, and a dusty RUG. "
                "Rules: Students MUST use prepositions. Crystal Key is BEHIND the shield. "
                "Goal: Use key ON the Golden Door. Keep responses under 3 sentences."
            )
            
            # Start the game
            response = st.session_state.chat.send_message(system_prompt)
            st.session_state.messages = [{"role": "ai", "content": "⚔️ You wake up in a cold stone room. A TALL STATUE looms over you, a SHINY SHIELD hangs on the wall, and a dusty RUG lies on the floor. What do you do?"}]

        # Display chat history
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # User input
        if prompt := st.chat_input("I look..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            response = st.session_state.chat.send_message(prompt)
            
            st.session_state.messages.append({"role": "ai", "content": response.text})
            st.chat_message("ai").write(response.text)

    except Exception as e:
        # If it still fails, we'll see a very specific error here
        st.error(f"Connection Error: {e}")
else:
    st.info("Please enter your API Key in the sidebar to begin.")

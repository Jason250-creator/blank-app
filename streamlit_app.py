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
        genai.configure(api_key=api_key)
        
        # This is where the AI "Brain" and "Rules" live
        if "model_name" not in st.session_state:
            st.session_state.model_name = 'gemini-1.5-flash'

        model = genai.GenerativeModel(
            model_name=st.session_state.model_name,
            system_instruction="""
            You are an epic Dungeon Master for Year 4 students. 
            1. Narrate a story where they are in a MAGICAL CASTLE.
            2. Start by saying: 'You wake up in a stone room. There is a TALL STATUE, a SHINY SHIELD on the wall, and a dusty RUG.'
            3. Students MUST use prepositions (in, on, under, behind, next to, between) to move or find things.
            4. Hidden Item: There is a 'Crystal Key' BEHIND the shield.
            5. Goal: Use the key ON the 'Golden Door' to win.
            6. Keep responses under 3 sentences. Be descriptive and fun!
            """
        )

        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history=[])
            st.session_state.messages = [{"role": "ai", "content": "⚔️ You wake up in a cold stone room. A TALL STATUE looms over you, a SHINY SHIELD hangs on the wall, and a dusty RUG lies on the floor. What do you do?"}]

        # Display chat history
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # User input
        if prompt := st.chat_input("Enter your action... (e.g., I look behind the shield)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            response = st.session_state.chat.send_message(prompt)
            
            st.session_state.messages.append({"role": "ai", "content": response.text})
            st.chat_message("ai").write(response.text)

    except Exception as e:
        st.error(f"Connection Error: {e}")
else:
    st.info("Waiting for the Teacher to enter the API Key in the sidebar...")

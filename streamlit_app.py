import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="Escape Room", page_icon="🗝️")
st.title("🗝️ The Great Preposition Escape!")
st.write("Find the hidden key to escape! You MUST use words like: **IN, ON, UNDER, BEHIND, or NEXT TO**.")
st.divider()

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
st.sidebar.write("Paste your Google API Key below to start the game:")
api_key = st.sidebar.text_input("API Key", type="password")

# 3. The Game Logic
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Set up the AI's memory and rules
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])
        
        # The strict rules for Year 4 students
        system_prompt = """You are a friendly game host for 10-year-old ESL students in Malaysia. 
        Use very simple English (CEFR A1/A2 level). You are hosting an Escape Room game. 
        Start by telling them they are in a locked bedroom. There is a bed, a desk, and a red rug. 
        The student MUST use a preposition (like in, on, under, behind) to search. 
        If they do not use a preposition, kindly tell them their action failed and remind them to use one. 
        Keep your replies to 2-3 short sentences maximum."""
        
        st.session_state.chat_session.send_message(system_prompt)
        
        # First message shown on screen
        st.session_state.history = [{"role": "ai", "content": "Welcome! You are trapped in a messy bedroom. There is a big bed, a wooden desk, and a red rug. Where do you want to look for the key?"}]

    # Display the chat history
    for message in st.session_state.history:
        if message["role"] == "user":
            st.info(f"🧑‍🎓 You: {message['content']}")
        else:
            st.success(f"🤖 Game: {message['content']}")

    # Player Input Box
    user_input = st.text_input("Type your action (Example: 'Look under the bed'):")
    
    if st.button("Submit Action"):
        if user_input:
            # Save player text and ask the AI
            st.session_state.history.append({"role": "user", "content": user_input})
            response = st.session_state.chat_session.send_message(user_input)
            st.session_state.history.append({"role": "ai", "content": response.text})
            st.rerun()

else:
    st.warning("Teacher: Please paste your API key in the sidebar menu on the left to wake up the game!")

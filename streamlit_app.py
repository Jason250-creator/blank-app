import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="Escape Room", page_icon="🗝️")
st.title("🗝️ The Great Preposition Escape!")
st.write("Find the hidden key! You MUST use words like: **IN, ON, UNDER, BEHIND, or NEXT TO**.")
st.divider()

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
st.sidebar.write("Paste your Google API Key below to start the game:")
api_key = st.sidebar.text_input("API Key", type="password")

# 3. The Game Logic
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # We use 'gemini-1.5-flash' - it's the fastest and most reliable for this
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            system_instruction="You are a friendly game host for 10-year-old students. They are trapped in a room with a BED, a DESK, and a RUG. The key is UNDER the rug. If they use a preposition correctly but look in the wrong place, describe what they see. If they find the key, tell them they won! Keep answers to 2 sentences max."
        )

        if "chat" not in st.session_state:
            st.session_state.chat = model.start_chat(history=[])
            st.session_state.messages = [{"role": "ai", "content": "Welcome! You are locked in the classroom. There is a bed, a desk, and a rug. Where do you want to look for the key?"}]

        # Display chat history
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # User input
        if prompt := st.chat_input("Look somewhere... (e.g., I look under the bed)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            response = st.session_state.chat.send_message(prompt)
            
            st.session_state.messages.append({"role": "ai", "content": response.text})
            st.chat_message("ai").write(response.text)

    except Exception as e:
        st.error(f"Almost there! There is a small connection issue: {e}")
else:
    st.info("Waiting for the Teacher to enter the API Key in the sidebar...")

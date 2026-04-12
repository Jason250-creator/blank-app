import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="Escape Room", page_icon="🗝️")
st.title("🗝️ The Great Preposition Escape!")
st.write("Find the hidden key! Use words like: **IN, ON, UNDER, BEHIND, or NEXT TO**.")
st.divider()

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
api_key = st.sidebar.text_input("Paste API Key", type="password")

# 3. The Game Logic
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # This part looks for WHICH model your key actually supports
        if "model_name" not in st.session_state:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Try to find Flash first, then Pro, then just take the first one available
            if 'models/gemini-1.5-flash' in models:
                st.session_state.model_name = 'gemini-1.5-flash'
            elif 'models/gemini-pro' in models:
                st.session_state.model_name = 'gemini-pro'
            else:
                st.session_state.model_name = models[0] if models else None

        if st.session_state.model_name:
            model = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                system_instruction="You are a friendly game host for 10-year-old students. They are trapped in a room with a BED, a DESK, and a RUG. The key is UNDER the rug. If they use a preposition correctly but look in the wrong place, describe what they see. If they find the key, tell them they won! Keep answers to 2 sentences max."
            )

            if "chat" not in st.session_state:
                st.session_state.chat = model.start_chat(history=[])
                st.session_state.messages = [{"role": "ai", "content": "Welcome! You are locked in the classroom. There is a bed, a desk, and a rug. Where do you want to look for the key?"}]

            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("I look..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                response = st.session_state.chat.send_message(prompt)
                st.session_state.messages.append({"role": "ai", "content": response.text})
                st.chat_message("ai").write(response.text)
        else:
            st.error("Your API key doesn't seem to have access to any Gemini models yet. Please check your Google AI Studio account.")

    except Exception as e:
        st.error(f"Connection Error: {e}")
else:
    st.info("Please enter your API Key in the sidebar to begin.")

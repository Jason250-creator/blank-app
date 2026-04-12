import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="The Preposition Quest", page_icon="🏰")
st.title("🏰 The Shadow Castle: An AI Adventure")
st.write("Year 4: Use **IN, ON, UNDER, BEHIND, NEXT TO, or BETWEEN** to navigate the castle!")
st.divider()

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
api_key = st.sidebar.text_input("Paste API Key", type="password")

# 3. The Game Logic
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Working Model Finder
        if "model_name" not in st.session_state:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if 'models/gemini-1.5-flash' in models:
                st.session_state.model_name = 'gemini-1.5-flash'
            elif 'models/gemini-pro' in models:
                st.session_state.model_name = 'gemini-pro'
            else:
                st.session_state.model_name = models[0] if models else None

        if st.session_state.model_name:
            model = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                system_instruction="""
                You are a master Dungeon Master. This is a long-form adventure for Year 4 students.
                
                THE WORLD:
                - ROOM 1 (The Great Hall): Has a TALL STATUE and a SHIELD. A Silver Key is BEHIND the shield.
                - ROOM 2 (The Library): Accessed by going THROUGH the oak doors. Has a MAGIC TORCH hidden UNDER a pile of books.
                - ROOM 3 (The Dungeon): Dark! They need the TORCH to see. The exit door is BETWEEN two dragon statues.
                
                RULES:
                1. Do not let them skip rooms. They need the Silver Key to enter the Library.
                2. They MUST use prepositions (on, under, behind, etc.) to find items.
                3. Keep track of their INVENTORY. If they have the key, mention it.
                4. Describe the atmosphere: the flickering torches, the smell of old paper, the cold stone.
                5. Keep responses to 3-4 sentences. Always end by asking 'What do you do next?'
                """
            )

            if "chat" not in st.session_state:
                st.session_state.chat = model.start_chat(history=[])
                st.session_state.messages = [{"role": "ai", "content": "🏰 You stand in the Great Hall of the Shadow Castle. Heavy rain drums ON the roof. To your left is a giant TALL STATUE, and to your right, a SHINY SHIELD hangs on the wall. Huge oak doors lead deeper into the castle. What is your first move?"}]

            # Display chat history
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).write(msg["content"])

            # User input
            if prompt := st.chat_input("Enter your action... (e.g., I walk through the doors)"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)
                
                response = st.session_state.chat.send_message(prompt)
                
                st.session_state.messages.append({"role": "ai", "content": response.text})
                st.chat_message("ai").write(response.text)
        else:
            st.error("No working models found for this API key.")

    except Exception as e:
        st.error(f"Connection Error: {e}")
else:
    st.info("Waiting for the Teacher to enter the API Key...")

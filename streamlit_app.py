import streamlit as st
import google.generativeai as genai

# --- Page Config ---
st.set_page_config(page_title="I Spy Game", layout="wide")
st.title("📚 I Spy: Teacher's Dashboard")

# --- API Key Sidebar ---
api_key = st.sidebar.text_input("Teacher API Key", type="password")

# --- Game Levels (Must match GitHub folders) ---
PREMADE = {
    "BEDROOM": {"path": "BEDROOM/bedroom.jpg", "target": "The Golden Star", "ans": "ON the bed"},
    "KITCHEN": {"path": "KITCHEN/kitchen1.jpg", "target": "The Golden Star", "ans": "UNDER the table"},
    "PLAYGROUND": {"path": "PLAYGROUND/playground.jpg", "target": "The Golden Star", "ans": "BEHIND the slide"}
}

# --- State Management ---
if "queue" not in st.session_state: st.session_state.queue = []
if "idx" not in st.session_state: st.session_state.idx = 0
if "won" not in st.session_state: st.session_state.won = False

if not api_key:
    st.warning("Please enter your API Key in the sidebar.")
else:
    genai.configure(api_key=api_key)
    try:
        if "model_name" not in st.session_state:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.model_name = next((m for m in models if "flash" in m), models[0])
        
        t1, t2 = st.tabs(["🎓 Setup", "🎮 Play"])

        # ==========================================
        # TEACHER SETUP TAB
        # ==========================================
        with t1:
            st.subheader("Add a Level to the Lesson")
            
            # Shortened options to prevent copy-paste line breaks!
            method = st.radio("Choose:", ["Gallery", "Upload", "AI"])
            st.divider()

            if method == "Gallery":
                folder = st.selectbox("Select Folder", list(PREMADE.keys()))
                data = PREMADE[folder]
                st.image(data["path"], width=250)
                if st.button("Add Gallery Level"):
                    st.session_state.queue.append(data)
                    st.success(f"{folder} added to the game!")

            elif method == "Upload":
                uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])
                t_item = st.text_input("Hidden item (e.g., The red apple)")
                t_ans = st.text_input("Secret Answer (e.g., ON the table)")
                
                if st.button("Add Uploaded Level"):
                    if uploaded_file and t_item and t_ans:
                        st.session_state.queue.append({
                            "img_data": uploaded_file.getvalue(), 
                            "target": t_item, 
                            "ans": t_ans
                        })
                        st.success("Uploaded level added!")
                    else:
                        st.warning("Please upload a picture and fill out both text boxes.")

            elif method == "AI":
                st.info("Tell the AI what to draw! (Note: AI might not place items perfectly).")
                ai_prompt = st.text_area("Room:", "A cartoon classroom with a green apple on the desk.")
                ai_item = st.text_input("Student must find:", "The green apple")
                ai_ans = st.text_input("Secret Answer:", "ON the desk")
                
                if st.button("Draw Image & Add Level"):
                    if ai_prompt and ai_item and ai_ans:
                        with st.spinner("AI is painting... please wait..."):
                            try:
                                img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                                result = img_model.generate_images(prompt=ai_prompt, number_of_images=1)
                                generated_img = result.images[0]._pil_image
                                st.session_state.queue.append({
                                    "img_data": generated_img, 
                                    "target": ai_item, 
                                    "ans": ai_ans
                                })
                                st.image(generated_img, width=300)
                                st.success("Masterpiece added!")
                            except AttributeError:
                                st.error("System Note: Image library missing. Please use Gallery or Uploads.")
                            except Exception as e:
                                st.error(f"Generation failed: {e}")
                    else:
                        st.warning("Fill out all boxes first.")

            if st.session_state.queue:
                st.divider()
                st.write(f"**Levels in Queue: {len(st.session_state.queue)}**")
                if st.button("🗑️ Reset All Levels"):
                    st.session_state.queue = []
                    st.session_state.idx = 0
                    st.rerun()

        # ==========================================
        # STUDENT PLAY TAB
        # ==========================================
        with t2:
            if not st.session_state.queue:
                st.info("Teacher: Add a level first!")
            else:
                idx = st.session_state.idx
                if idx >= len(st.session_state.queue): idx = 0
                lvl = st.session_state.queue[idx]

                if "chat" not in st.session_state or st.session_state.get("last_lvl") != idx:
                    instruction = (
                        f"ROLE: You are a friendly teacher playing I Spy. "
                        f"OBJECT: {lvl['target']}. ANSWER: {lvl['ans']}. "
                        f"RULE 1: If correct, say 'CORRECT! 🎉'. RULE 2: If wrong, give a hint."
                    )
                    model = genai.GenerativeModel(model_name=st.session_state.model_name, system_instruction=instruction)
                    st.session_state.chat = model.start_chat(history=[])
                    st.session_state.history = [{"role": "ai", "content": f"I spy... {lvl['target']}! Where is it?"}]
                    st.session_state.last_lvl = idx
                    st.session_state.won = False

                c1, c2 = st.columns([1, 1])
                with c1:
                    display_img = lvl.get("img_data") or lvl["path"]
                    st.image(display_img, use_container_width=True)
                    
                    if st.session_state.won and idx < len(st.session_state.queue) - 1:
                        if st.button("Next Level ➡️"):
                            st.session_state.idx += 1
                            st.session_state.won = False
                            st.rerun()
                            
                with c2:
                    for m in st.session_state.history:
                        st.chat_message(m["role"]).write(m["content"])
                    if not st.session_state.won:
                        if p := st.chat_input("Answer here...", key=f"chat_{idx}"):
                            st.session_state.history.append({"role": "user", "content": p})
                            try:
                                response = st.session_state.chat.send_message(p).text
                                st.session_state.history.append({"role": "ai", "content": response})
                                if "CORRECT" in response.upper(): st.session_state.won = True
                                st.rerun()
                            except Exception as e:
                                if "429" in str(e):
                                    st.error("Wait 30 seconds before typing! The API is taking a quick break.")
                                else:
                                    st.error(f"Chat Error: {e}")
                            
    except Exception as e:
        st.error(f"System Error: {e}")

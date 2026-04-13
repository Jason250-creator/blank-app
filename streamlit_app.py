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
            
            # The 3 Teacher Options
            method = st.radio("Choose an option:", [
                "A) Use Pre-made Gallery", 
                "B) Upload a Picture", 
                "C) Generate with AI 🪄"
            ])
            st.divider()

            # Option A: Gallery
            if method == "A) Use Pre-made Gallery":
                folder = st.selectbox("Select Folder", list(PREMADE.keys()))
                data = PREMADE[folder]
                st.image(data["path"], width=250)
                if st.button("Add Gallery Level"):
                    st.session_state.queue.append(data)
                    st.success(f"{folder} added to the game!")

            # Option B: Upload
            elif method == "B) Upload a Picture":
                uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "png"])
                t_item = st.text_input("What is the hidden item? (e.g., The red apple)")
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

            # Option C: AI Image Generator
            elif method == "C) Generate with AI 🪄":
                st.info("🎨 Tell the AI what kind of room to draw. Note: AI might not place the item perfectly, but it's great for creative lessons!")
                ai_prompt = st.text_area("Describe the room:", "A cartoon classroom with a green apple sitting on the teacher's desk.")
                ai_item = st.text_input("What should the student find?", "The green apple")
                ai_ans = st.text_input("Secret Answer (Where is it?)", "ON the desk")
                
                if st.button("Draw Image & Add Level"):
                    if ai_prompt and ai_item and ai_ans:
                        with st.spinner("AI is painting your room... please wait..."):
                            try:
                                # Call Google's Imagen model
                                img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                                result = img_model.generate_images(prompt=ai_prompt, number_of_images=1)
                                
                                # Extract the image and save it to the game queue
                                generated_img = result.images[0]._pil_image
                                st.session_state.queue.append({
                                    "img_data": generated_img, 
                                    "target": ai_item, 
                                    "ans": ai_ans
                                })
                                st.image(generated_img, width=300)
                                st.success("Masterpiece created and added to the game!")
                            except AttributeError:
                                st.error("⚙️

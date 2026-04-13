import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import re

# ---------------------------------------------------------
# Part 1: Page & Visual Layout Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Shadow Castle Blueprint", page_icon="🏰", layout="wide") # 'wide' makes room for the map

st.title("🏰 The Shadow Castle: An AI Adventure")
st.write("Year 4: Use **IN, ON, UNDER, BEHIND, NEXT TO, or BETWEEN** to navigate!")
st.divider()

# Arrange the screen in two columns: Left for Chat, Right for Visual Map
chat_col, map_col = st.columns([1, 1])

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
api_key = st.sidebar.text_input("Paste API Key", type="password")

# ---------------------------------------------------------
# Part 2: The Drawing Engine (Matplotlib)
# ---------------------------------------------------------
def draw_floor_plan(current_room, show_torch):
    """Generates a Matplotlib figure showing the castle floor plan and player position."""
    
    # Create the drawing surface
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor('#d3c6a3') # 'Blueprint Paper' color
    
    # A. Define the Rooms (Coordinates of the boxes)
    rooms = {
        "Great Hall": {"rect": [0, 6, 10, 4], "color": "#8c7e60"}, # [x_start, y_start, width, height]
        "Library": {"rect": [10, 6, 6, 4], "color": "#7a8a65"},
        "Dungeon": {"rect": [5, 0, 8, 5], "color": "#5e5e5e"},
    }
    
    # B. Draw the Room Boxes and Labels
    for name, data in rooms.items():
        rect = plt.Rectangle((data["rect"][0], data["rect"][1]), data["rect"][2], data["rect"][3], 
                             edgecolor='black', facecolor=data["color"], linewidth=3)
        ax.add_patch(rect)
        
        # Room Name Label
        ax.text(data["rect"][0] + data["rect"][2]/2, data["rect"][1] + data["rect"][3]/2, name, 
                ha='center', va='center', fontsize=14, color='white', fontweight='bold')

    # C. Draw connecting paths (doors)
    plt.plot([10, 10], [7.5, 8.5], color='black', linewidth=10) # Hall to Library
    plt.plot([9, 9], [6, 5], color='black', linewidth=10)     # Hall to Dungeon

    # D. Draw Character Position ('X') based on AI state
    # If the user refrences a room, move the X. Otherwise, default to the Great Hall.
    if current_room == "Library":
        # Library Center
        ax.text(13, 8, 'X', ha='center', va='center', fontsize=24, color='#c42b2b', fontweight='extra bold') 
    elif current_room == "Dungeon":
        # Dungeon Center
        ax.text(9, 2.5, 'X', ha='center', va='center', fontsize=24, color='#c42b2b', fontweight='extra bold')
    else:
        # Default Great Hall
        ax.text(5, 8, 'X', ha='center', va='center', fontsize=24, color='#c42b2b', fontweight='extra bold') 
    
    # E. Display dynamic item icons (e.g., torch found)
    if show_torch:
        ax.text(14, 7, '🔥', fontsize=20) # Show torch when found in library

    # F. Styling & Cleanup
    ax.set_xlim(-1, 17)
    ax.set_ylim(-1, 11)
    ax.axis('off') # Hide axes (don't show numbers to kids)
    plt.title("🏰 Castle Blueprint", fontsize=20, fontweight='bold')
    
    return fig

# ---------------------------------------------------------
# Part 3: State Tracking and AI Logic
# ---------------------------------------------------------
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # KEEPING YOUR WORKING MODEL SCANNER
        if "model_name" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                # Prioritize Flash
                if 'models/gemini-1.5-flash' in available_models:
                    st.session_state.model_name = 'gemini-1.5-flash'
                elif 'models/gemini-pro' in available_models:
                    st.session_state.model_name = 'gemini-pro'
                else:
                    st.session_state.model_name = available_models[0]
            else:
                st.error("No compatible generative models found for this API key.")

        if st.session_state.model_name:
            
            # MODIFYING THE INSTRUCTION TO BE MAP-AWARE
            # We must instruct the AI to output specific keywords so we can move the map icon.
            model = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                system_instruction="""
                You are a master Dungeon Master for Year 4 students (10-year-olds). 
                Generate a lengthy descriptive adventure story.
                
                The layout of the Castle is fixed:
                - Great Hall: Connects to Library (needs key) and Dungeon (needs torch). Statue and Shield are here. Key BEHIND shield.
                - Library: Under a pile of books is a Magic Torch.
                - Dungeon: Needs Torch to see. Win condition BETWEEN dragon statues.
                
                Rules:
                1. Students MUST use prepositions (in, on, under, behind, etc.) to progress. Polite failure if they don't.
                2. Describe the sights, smells, and sounds. (Rain on roof, smell of old paper).
                3. Keeptrack of Inventory. If they are holding the key, remind them.
                
                ***IMPORTANT VISUAL RULE***:
                You must end every single response by stating the player's current location, followed by found items.
                FORMATTING: CurrentLocation: [RoomName] foundItems: [Torch, Key, etc.]
                (e.g., CurrentLocation: Library foundItems: Torch)
                """
            )

            # Define initialization states for visual tracking
            if "current_visual_room" not in st.session_state:
                st.session_state.current_visual_room = "Great Hall"
                st.session_state.show_torch = False

            # Start the game chat
            if "chat" not in st.session_state:
                st.session_state.chat = model.start_chat(history=[])
                # This prompt triggers the DM's intro
                intro_prompt = "Hello Dungeon Master. Start the game by describing my arrival at the Shadow Castle Great Hall."
                response = st.session_state.chat.send_message(intro_prompt)
                st.session_state.messages = [{"role": "ai", "content": response.text}]

            # ---------------------------------------------------------
            # Part 4: Displaying the Interface
            # ---------------------------------------------------------
            
            # COLUMN 1: The Chat Adventure
            with chat_col:
                st.subheader("Action Log")
                
                # Input area
                if prompt := st.chat_input("Enter your action... (e.g., I walk into the Library)"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = st.session_state.chat.send_message(prompt)
                    st.session_state.messages.append({"role": "ai", "content": response.text})
                
                # Render previous messages in 'chat' style
                for msg in st.session_state.messages:
                    st.chat_message(msg["role"]).write(msg["content"])


            # COLUMN 2: The Live Blueprint Map
            with map_col:
                st.subheader("Position Tracker")
                
                # State Update Logic (Analyzing the AI's final sentence)
                # We use regex to find the specific keywords we instructed the AI to use.
                last_ai_message = ""
                # Find the most recent AI message to scan its content
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "ai":
                        last_ai_message = msg["content"]
                        break

                if last_ai_message:
                    # Look for "CurrentLocation: [RoomName]"
                    room_match = re.search(r'CurrentLocation:\s*(.*)', last_ai_message)
                    if room_match:
                        found_room = room_match.group(1).split()[0].replace(']','').replace('[','') # Clean up format
                        # Acceptable room names for the map logic
                        if found_room in ["Hall", "GreatHall", "Great"]: st.session_state.current_visual_room = "Great Hall"
                        elif found_room == "Library": st.session_state.current_visual_room = "Library"
                        elif found_room == "Dungeon": st.session_state.current_visual_room = "Dungeon"

                    # Look for "foundItems: Torch"
                    if "Torch" in last_ai_message:
                        st.session_state.show_torch = True

                # Generate and display the map figure
                map_fig = draw_floor_plan(st.session_state.current_visual_room, st.session_state.show_torch)
                st.pyplot(map_fig) # Streamlit command to show a matplotlib chart

        else:
            st.error("No suitable generative model found for this key.")

    except Exception as e:
        st.error(f"Connection Error: {e}")
else:
    st.info("Waiting for the Teacher to enter the API Key in the sidebar...")

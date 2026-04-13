import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import re

# ---------------------------------------------------------
# Part 1: Page & Visual Layout Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Shadow Castle RPG", page_icon="🎮", layout="wide")

st.title("🎮 The Shadow Castle: RPG Adventure!")
st.write("Welcome, brave hero! Use magic words like: **IN, ON, UNDER, BEHIND, NEXT TO, or BETWEEN** to explore.")
st.divider()

chat_col, map_col = st.columns([1, 1])

# 2. Sidebar for Teacher API Key
st.sidebar.title("Teacher Settings")
api_key = st.sidebar.text_input("Paste API Key", type="password")

# ---------------------------------------------------------
# Part 2: The Drawing Engine (RPG Style)
# ---------------------------------------------------------
def draw_rpg_map(current_room, show_torch):
    """Generates an RPG-style map using Matplotlib."""
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor('#1e1e1e') # Dark background (void)
    
    # A. Define the Rooms (RPG Colors)
    rooms = {
        "Great Hall": {"rect": [0, 6, 10, 4], "color": "#7a8288", "text": "Great Hall\n(Stone)"}, 
        "Library": {"rect": [10, 6, 6, 4], "color": "#6e4c2e", "text": "Library\n(Wood)"},
        "Dungeon": {"rect": [5, 0, 8, 5], "color": "#332a40", "text": "Dungeon\n(Spooky)"},
    }
    
    # B. Draw the Rooms
    for name, data in rooms.items():
        rect = plt.Rectangle((data["rect"][0], data["rect"][1]), data["rect"][2], data["rect"][3], 
                             edgecolor='#4a4a4a', facecolor=data["color"], linewidth=5)
        ax.add_patch(rect)
        
        # Room Name Label
        ax.text(data["rect"][0] + data["rect"][2]/2, data["rect"][1] + data["rect"][3]/2 + 1, data["text"], 
                ha='center', va='center', fontsize=12, color='white', fontweight='bold', alpha=0.6)

    # C. Draw Doors/Paths
    plt.plot([10, 10], [7.5, 8.5], color='#4a3b2c', linewidth=15) # Hall to Library (Wood door)
    plt.plot([9, 9], [6, 5], color='#222222', linewidth=15)       # Hall to Dungeon (Iron gate)

    # D. RPG Scenery Decorations
    ax.text(1, 8, '🗿', fontsize=25) # Statue in Hall
    ax.text(8, 8, '🛡️', fontsize=25) # Shield in Hall
    ax.text(14, 8, '📚', fontsize=25) # Books in Library
    ax.text(6, 1, '🐉', fontsize=25) # Dragon in Dungeon
    ax.text(11, 1, '🐉', fontsize=25) # Dragon in Dungeon

    # E. Draw Player Character (Wizard/Adventurer Emoji)
    player_icon = '🧙‍♂️'
    if current_room == "Library":
        ax.text(12, 7.5, player_icon, ha='center', va='center', fontsize=35) 
    elif current_room == "Dungeon":
        ax.text(9, 3, player_icon, ha='center', va='center', fontsize=35)
    else:
        # Default Great Hall
        ax.text(5, 7.5, player_icon, ha='center', va='center', fontsize=35) 
    
    # F. Display Item
    if show_torch:
        ax.text(14, 7, '🔥', fontsize=20) # Show torch when found in library

    ax.set_xlim(-1, 17)
    ax.set_ylim(-1, 11)
    ax.axis('off') 
    plt.title("🗺️ Castle Map", fontsize=20, fontweight='bold', color='#f1c40f')
    
    return fig

# ---------------------------------------------------------
# Part 3: State Tracking and AI Logic
# ---------------------------------------------------------
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        if "model_name" not in st.session_state:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                if 'models/gemini-1.5-flash' in available_models:
                    st.session_state.model_name = 'gemini-1.5-flash'
                elif 'models/gemini-pro' in available_models:
                    st.session_state.model_name = 'gemini-pro'
                else:
                    st.session_state.model_name = available_models[0]
            else:
                st.error("No compatible generative models found.")

        if st.session_state.model_name:
            
            # UPDATED: Kid-friendly Language & Strict Tracker
            model = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                system_instruction="""
                You are a friendly, enthusiastic Game Master for a 9-year-old playing an RPG.
                Use very simple words. Keep sentences short and exciting! Always cheer them on.
                
                The layout:
                - Great Hall: Has a TALL STATUE (🗿) and a SHIELD (🛡️). A Silver Key is BEHIND the shield.
                - Library: Has lots of books (📚). A Magic Torch (🔥) is UNDER a pile of books. Need Silver Key to enter.
                - Dungeon: Very dark! Need the Magic Torch to see. The exit is BETWEEN two dragon statues (🐉).
                
                Rules:
                1. They MUST use words like IN, ON, UNDER, BEHIND, NEXT TO, BETWEEN. If they don't, gently remind them to use their "magic position words".
                2. If they find an item, tell them "Awesome job! You found it!"
                3. Keep the story part to 3 short sentences maximum.
                
                AT THE VERY END OF YOUR MESSAGE, you must include a secret code for the computer on a new line:
                [TRACKER] Room: [Name] Torch: [Yes/No]
                Example: [TRACKER] Room: Library Torch: Yes
                """
            )

            if "current_visual_room" not in st.session_state:
                st.session_state.current_visual_room = "Great Hall"
                st.session_state.show_torch = False

            if "chat" not in st.session_state:
                st.session_state.chat = model.start_chat(history=[])
                intro_prompt = "Start the game. I just walked into the Great Hall. Remember to include the [TRACKER] code at the end."
                response = st.session_state.chat.send_message(intro_prompt)
                st.session_state.messages = [{"role": "ai", "content": response.text}]

            # ---------------------------------------------------------
            # Part 4: Displaying the Interface
            # ---------------------------------------------------------
            with chat_col:
                st.subheader("📜 Adventure Log")
                
                if prompt := st.chat_input("What do you do? (e.g., I look behind the shield)"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    response = st.session_state.chat.send_message(prompt)
                    st.session_state.messages.append({"role": "ai", "content": response.text})
                
                for msg in st.session_state.messages:
                    # Clean the AI text so kids don't see the computer tracking code
                    display_text = re.sub(r'\[TRACKER\].*', '', msg["content"], flags=re.IGNORECASE|re.DOTALL)
                    st.chat_message(msg["role"]).write(display_text.strip())

            with map_col:
                st.subheader("📍 Hero Radar")
                
                last_ai_message = ""
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "ai":
                        last_ai_message = msg["content"]
                        break

                # Extract the secret tracking code
                if "[TRACKER]" in last_ai_message:
                    room_match = re.search(r'Room:\s*([A-Za-z\s]+)', last_ai_message)
                    if room_match:
                        found_room = room_match.group(1).strip()
                        if "Hall" in found_room: st.session_state.current_visual_room = "Great Hall"
                        elif "Library" in found_room: st.session_state.current_visual_room = "Library"
                        elif "Dungeon" in found_room: st.session_state.current_visual_room = "Dungeon"

                    if "Torch: Yes" in last_ai_message:
                        st.session_state.show_torch = True

                map_fig = draw_rpg_map(st.session_state.current_visual_room, st.session_state.show_torch)
                st.pyplot(map_fig)

        else:
            st.error("No suitable generative model found.")

    except Exception as e:
        st.error(f"Connection Error: {e}")
else:
    st.info("Waiting for the Teacher to enter the API Key in the sidebar...")

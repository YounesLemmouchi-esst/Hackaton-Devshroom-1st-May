import streamlit as st
import random

# Import our modules
from config import ERAS, XP_PER_QUESTION, XP_FOR_LEVEL_UP
from ai_generator import get_question_batch_from_gemini
from game_mechanics import initialize_session_state, level_up, calculate_multiplier
from ui_components import (
    render_sidebar, render_question, handle_answer, render_boss_battle
)

# Initialize session state variables
initialize_session_state()

# Add a Back to Levels button
if st.button("← Back to Levels", key="back_to_levels"):
    st.session_state.page = "home"
    # Force rerun to return to chapters.py
    st.rerun()

# Main UI
st.title("🌍 LangaQuest.py – Learn French, Time Travel Style")
st.subheader(f"Current Era: {st.session_state.era}")

# Function to update chapter progression when advancing
def update_chapters_progress():
    era_to_level = {
        "Stone Age": 0,
        "Medieval": 1, 
        "Industrial": 2,
        "Modern": 3,
        "Future": 4
    }
    
    if st.session_state.era in era_to_level:
        current_level = era_to_level[st.session_state.era]
        
        # Update unlocked levels
        if 'unlocked_levels' not in st.session_state:
            st.session_state.unlocked_levels = set()
            
        # Unlock all levels up to current one
        for level in range(current_level + 1):
            st.session_state.unlocked_levels.add(level)
            
        # Mark completed levels
        if 'boss_passed' in st.session_state and st.session_state.era in st.session_state.boss_passed:
            level_completed = era_to_level[st.session_state.era]
            st.session_state[f"level_{level_completed}_completed"] = True

# Hook into advancement functions
original_level_up = level_up

def enhanced_level_up():
    original_level_up()
    update_chapters_progress()
    
# Replace the original level_up with enhanced version
level_up = enhanced_level_up

# Render the sidebar with all components
render_sidebar()

# Main game logic
if not st.session_state.boss_mode:
    # Check if we need a new batch or a new question from the batch
    if not st.session_state.current_question:
        # Do we need to fetch a new batch?
        if not st.session_state.question_batch or st.session_state.current_batch_index >= len(st.session_state.question_batch):
            st.write("Fetching new questions from the LangaVerse...") # User feedback
            new_batch = get_question_batch_from_gemini()
            if new_batch:
                st.session_state.question_batch = new_batch
                st.session_state.current_batch_index = 0 # Reset index for the new batch
            else:
                # Handle failure to get a new batch
                st.error("Failed to fetch a new batch of questions. Please try refreshing.")
                # Optionally add a retry button here as well
                if st.button("Retry Fetching Batch"):
                    st.rerun()
                st.stop() # Stop execution if we can't get questions

        # Get the next question from the current batch
        if st.session_state.question_batch and st.session_state.current_batch_index < len(st.session_state.question_batch):
            st.session_state.current_question = st.session_state.question_batch[st.session_state.current_batch_index]
            st.session_state.current_batch_index += 1 # Move index for the *next* time
            st.session_state.answered = False # Reset answered state for the new question
            st.rerun() # Rerun to display the newly selected question cleanly
        else:
             # This case should ideally be handled by the batch fetching logic above
             st.warning("Could not select a question from the batch.")
             if st.button("Retry Question Selection"):
                 st.rerun()
             st.stop()

    # Display the current question (if one is loaded)
    q = st.session_state.current_question
    if q:
        # Ensure q is a dictionary (it should be based on JSON structure)
        if not isinstance(q, dict):
             st.error("Internal error: Current question is not in the expected format.")
             st.write("Problematic question data:", q)
             # Clear the problematic state and try again
             st.session_state.current_question = None
             st.session_state.question_batch = []
             st.session_state.current_batch_index = 0
             if st.button("Reset and Retry"):
                 st.rerun()
             st.stop()

        # Generate a more unique key using question text hash or index
        question_key_part = q.get('question', str(st.session_state.current_batch_index)) # Use index if question text missing
        
        # Render the question and get user's answer
        user_answer = render_question(q, question_key_part)

        if st.button("Submit", key=f"submit_{st.session_state.level}_{question_key_part}"):
            if user_answer is None:
                 st.warning("Please select an answer.")
            elif st.session_state.answered:
                 st.warning("You've already submitted an answer for this question.")
                 # Optionally add a button to force next question if stuck
                 if st.button("Force Next Question"):
                     st.session_state.current_question = None # Clear current question to trigger fetch/selection logic
                     st.session_state.answered = False
                     st.rerun()
            else:
                st.session_state.answered = True # Mark as answered
                correct_answer = q.get("answer")

                if correct_answer is None:
                    st.error("Internal Error: Correct answer missing for this question.")
                    # Decide how to proceed - maybe skip the question?
                    if st.button("Skip Faulty Question"):
                        st.session_state.current_question = None
                        st.session_state.answered = False
                        st.rerun()
                    st.stop()
                
                # Handle the answer submission
                handle_answer(user_answer, correct_answer)
                st.rerun()

# Boss mode
elif st.session_state.boss_mode:
    render_boss_battle()
    
# Add a button to enter boss mode
if not st.session_state.boss_mode and st.session_state.era not in st.session_state.boss_passed:
    if st.button(f"⚔️ Challenge Boss of {st.session_state.era}!"):
        st.session_state.boss_mode = True
        if "boss_questions" in st.session_state and st.session_state.era in st.session_state.boss_questions:
            del st.session_state.boss_questions[st.session_state.era]  # Force refresh boss questions
        st.rerun()

# Debug tools (can be removed in production)
with st.expander("🛠️ Debug Tools"):
    if st.button("Reset Shop Items"):
        from config import DEFAULT_SHOP_ITEMS
        import copy
        st.session_state.shop_items = copy.deepcopy(DEFAULT_SHOP_ITEMS)
        st.success("Shop items reset to defaults!")
        st.rerun()
        
    if st.button("Reset Stats"):
        st.session_state.question_type_stats = {
            "numbers": {"total": 0, "correct": 0},
            "weekdays": {"total": 0, "correct": 0},
            "months": {"total": 0, "correct": 0},
            "greetings": {"total": 0, "correct": 0},
            "colors": {"total": 0, "correct": 0}
        }
        st.success("Stats reset!")
        st.rerun()
        
    if st.button("Show Session State"):
        # Display important state variables for debugging
        st.write("Current Era:", st.session_state.era)
        st.write("Shop Items:", len(st.session_state.shop_items) if "shop_items" in st.session_state else "Not initialized")
        st.write("Stats:", "Initialized" if "question_type_stats" in st.session_state else "Not initialized")

# Add this near the end of your main file, before or after the boss mode check:
# Debug tools section
with st.expander("🔧 Debug Tools (Dev Only)", expanded=False):
    st.write("### HTML Rendering Test")
    
    if st.button("Test HTML Rendering"):
        st.markdown("""
        <div style="padding:10px; background-color:#f0f0f0; border-radius:5px;">
            <h4 style="color:#4169E1;">HTML Test</h4>
            <p>If you see this text with <strong>bold formatting</strong> and a gray background, HTML is rendering properly.</p>
            <div style="height:10px; background-color:#4169E1; width:50%; border-radius:5px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("Clear Session State"):
        for key in list(st.session_state.keys()):
            if key not in ["auth"]:  # Keep authentication if you have it
                del st.session_state[key]
        st.success("Session state cleared! Please refresh the page.")
        
    if st.button("Reinitialize Shop Items"):
        from config import DEFAULT_SHOP_ITEMS
        import copy
        st.session_state.shop_items = copy.deepcopy(DEFAULT_SHOP_ITEMS)
        st.success("Shop items reinitialized!")
        st.rerun()

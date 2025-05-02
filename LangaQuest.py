import streamlit as st
import os
import google.generativeai as genai
import json
import random
import re

# Set Gemini credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\youne\\Downloads\\devshroom-hackathon-b428c409d22f.json"
genai.configure()
model = genai.GenerativeModel("gemini-2.0-flash")

# Update game settings
ERAS = ["Stone Age", "Medieval", "Industrial", "Modern", "Future"]
XP_PER_QUESTION = 5
XP_FOR_LEVEL_UP = 200  # XP needed to level up

# Session state
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "era" not in st.session_state:
    st.session_state.era = ERAS[0]
if "boss_mode" not in st.session_state:
    st.session_state.boss_mode = False
if "boss_passed" not in st.session_state:
    st.session_state.boss_passed = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "question_batch" not in st.session_state:
    st.session_state.question_batch = []
if "current_batch_index" not in st.session_state:
    st.session_state.current_batch_index = 0
if "current_streak" not in st.session_state:
    st.session_state.current_streak = 0
if "max_streak" not in st.session_state:
    st.session_state.max_streak = 0
if "streak_multiplier" not in st.session_state:
    st.session_state.streak_multiplier = 1
if "coins" not in st.session_state:
    st.session_state.coins = 0

# Prompt by level
def get_prompt_by_level(level):
    if level == 1:
        return (
            "Generate 3 *different* super easy beginner-level French questions for absolute beginners learning English. Make the questions in English."
            "Focus on a *variety* of basic concepts including:\n"
            "- Simple greetings (e.g., Hello, Goodbye, Good morning)\n"
            "- Basic numbers (e.g., one, two, three, seven, ten)\n"
            "- Days of the week (e.g., Monday, Sunday, Wednesday)\n"
            "- Common colors (e.g., red, blue, green)\n"
            "- Simple nouns (e.g., cat, dog, book)\n"
            "Ensure the questions cover *different* topics from this list within the batch, avoiding repetition of the same concept (like asking for 'one' twice)."
            "Return exactly 3 questions in this JSON format:"
            "DO NOT include any other text, just the JSON:"
            '[\n'
            '  {\n'
            '    "question": "...",\n'
            '    "options": ["...", "...", "..."],\n'
            '    "answer": "..." \n'
            '  },\n'
            '  {...},\n'
            '  {...}\n'
            ']'
        )
    elif level == 3:
        return (
            "Generate 3 different creative beginner-level French questions for an English-speaking student. Make the questions in English. "
            "Each question should be easy and varied, including formats:\n"
            "- Fill in the blank\n"
            "Return exactly 3 questions in this JSON format:\n"
            "DO NOT include any other text, just the JSON:\n"
            '[\n'
            '  {\n'
            '    "question": "...",\n'
            '    "options": ["...", "...", "..."],\n'
            '    "answer": "..." \n'
            '  },\n'
            '  {...},\n'
            '  {...}\n'
            ']'
        )
    else:
        return (
            "Generate 3 beginner-level French questions for an English-speaking student. Make the questions in English. "
            "Questions should include a mix of vocabulary and grammar, suitable for someone who has learned the absolute basics."
            " Ensure the questions are different from each other."
            "Return exactly 3 questions in this JSON format:"
            "DO NOT include any other text, just the JSON:"
            '[\n'
            '  {\n'
            '    "question": "...",\n'
            '    "options": ["...", "...", "..."],\n'
            '    "answer": "..." \n'
            '  },\n'
            '  {...},\n'
            '  {...}\n'
            ']'
        )

# Get question from Gemini - Modified to return the full list
def get_question_batch_from_gemini():
    prompt = get_prompt_by_level(st.session_state.level)
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Attempt to extract JSON block
        match = re.search(r"```(json)?\s*(\[.*?\])\s*```", response_text, re.DOTALL) # Specifically look for list format
        if match:
            json_string = match.group(2)
        else:
            # Fallback: find first '[' and last ']'
            start_index = response_text.find('[')
            end_index = response_text.rfind(']')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                 json_string = response_text[start_index:end_index + 1]
            else:
                 st.error("❌ Could not find JSON list in AI response.")
                 st.text("Raw Response:")
                 st.text(response_text)
                 return [] # Return empty list on failure

        # Attempt to parse the JSON string
        data = json.loads(json_string)
        if isinstance(data, list):
            # Optional: Shuffle the batch so the order isn't always the same
            random.shuffle(data)
            return data
        else:
            st.error("❌ Parsed JSON is not a list as expected.")
            st.text("Parsed Data Type:")
            st.text(type(data))
            st.text("Raw Response:")
            st.text(response_text)
            return [] # Return empty list on failure

    except json.JSONDecodeError:
        st.error("❌ Failed to parse AI response as JSON.")
        st.text("Raw Response:")
        st.text(response_text)
        st.text("Attempted JSON String:")
        st.text(json_string if 'json_string' in locals() else "Extraction failed")
        return [] # Return empty list on failure
    except Exception as e:
        st.error(f"❌ An unexpected error occurred during generation: {str(e)}")
        st.text("Raw Response (if available):")
        st.text(response.text if 'response' in locals() else "N/A")
        return [] # Return empty list on failure

# New function for boss questions using Gemini
def get_boss_questions_from_gemini():
    # Different prompt based on level/era
    level = st.session_state.level
    era = st.session_state.era
    
    prompt = (
        f"Generate 3 English words or short phrases for a French language learner at beginner level {level} "
        f"to translate to French. These should be appropriate for the {era} historical era theme "
        f"and match the difficulty of level {level} (where 1 is easiest, 5 is hardest).\n\n"
        "Return the result as a JSON object with English phrases as keys and French translations as values.\n"
        "DO NOT include any other text, just the JSON:\n"
        "{\n"
        '  "English word/phrase 1": "French translation 1",\n'
        '  "English word/phrase 2": "French translation 2",\n'
        '  "English word/phrase 3": "French translation 3"\n'
        "}"
    )
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON - similar to the regular question function
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if match:
            json_string = match.group(1)
        else:
            # Fallback - find first '{' and last '}'
            start_index = response_text.find('{')
            end_index = response_text.rfind('}')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_string = response_text[start_index:end_index + 1]
            else:
                st.error("❌ Could not find JSON object in AI response for boss questions.")
                st.text("Raw Response:")
                st.text(response_text)
                # Return a backup set of questions if parsing fails
                return {
                    "Hello": "Bonjour",
                    "Thank you": "Merci",
                    "Yes": "Oui"
                }
        
        # Parse the JSON
        data = json.loads(json_string)
        if isinstance(data, dict) and len(data) > 0:
            return data
        else:
            st.error("❌ Parsed JSON is not a dictionary as expected for boss questions.")
            # Return backup questions
            return {
                "Hello": "Bonjour",
                "Thank you": "Merci",
                "Yes": "Oui"
            }
    
    except json.JSONDecodeError:
        st.error("❌ Failed to parse AI response as JSON for boss questions.")
        st.text("Raw Response:")
        st.text(response_text)
    except Exception as e:
        st.error(f"❌ An unexpected error occurred during boss question generation: {str(e)}")
    
    # Return backup questions if anything fails
    return {
        "Hello": "Bonjour",
        "Thank you": "Merci",
        "Yes": "Oui"
    }

# XP and level logic
# Modified level_up function that separates levels from eras
def level_up():
    # Increase level
    st.session_state.level += 1
    
    # Notice we no longer update era based on level
    # The era will need to be changed separately now
    
    st.session_state.boss_mode = False
    st.session_state.current_question = None
    st.session_state.answered = False
    # Reset batch info on level up
    st.session_state.question_batch = []
    st.session_state.current_batch_index = 0
    # Award coins for leveling up
    coin_reward = 10  # Flat 10 coins per level up
    st.session_state.coins += coin_reward
    st.success(f"🎉 You've leveled up to level {st.session_state.level}! Earned {coin_reward} 🪙 coins!")

# Add a function to unlock a new era (separate from leveling up)
def unlock_era(new_era_index):
    if new_era_index < len(ERAS):
        st.session_state.era = ERAS[new_era_index]
        # Award bonus coins for unlocking a new era
        era_coin_reward = 100  # Bonus for unlocking a new era
        st.session_state.coins += era_coin_reward
        st.success(f"🌟 You've unlocked the {st.session_state.era} Era! Earned {era_coin_reward} 🪙 coins!")
        return True
    return False

# Add this helper function for flexible answer checking
def fuzzy_check_answer(user_answer, correct_answer):
    """Check if user answer is close enough to correct answer using simplified rules."""
    if not user_answer:  # Handle empty answers
        return False
    
    # Convert both to lowercase and strip whitespace
    user = user_answer.lower().strip()
    correct = correct_answer.lower().strip()
    
    # Exact match is always accepted
    if user == correct:
        return True
    
    # Remove accents from both (simplified approach)
    def remove_accents(text):
        accent_map = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'î': 'i', 'ï': 'i',
            'ô': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'ÿ': 'y', 'ç': 'c'
        }
        for accent, plain in accent_map.items():
            text = text.replace(accent, plain)
        return text
    
    user_no_accents = remove_accents(user)
    correct_no_accents = remove_accents(correct)
    
    # If they match without accents, that's good enough
    if user_no_accents == correct_no_accents:
        return True
    
    # Check for simple singular/plural confusion (very common with beginners)
    if user_no_accents + 's' == correct_no_accents or user_no_accents == correct_no_accents + 's':
        return True
    
    # Check if it's just one character off (letter swap, missing letter, etc.)
    def levenshtein_distance(s1, s2):
        """Calculate edit distance between two strings."""
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    # Allow one character difference in words up to 5 chars
    # Allow two character differences in longer words
    max_distance = 1 if len(correct_no_accents) <= 5 else 2
    
    if levenshtein_distance(user_no_accents, correct_no_accents) <= max_distance:
        return True
    
    return False

# Add function to calculate multiplier from streak
def calculate_multiplier(streak):
    """Calculate XP multiplier based on current streak."""
    if streak < 3:
        return 1  # No multiplier for fewer than 3 correct in a row
    elif streak < 5:
        return 1.5  # 50% bonus for 3-4 correct answers
    elif streak < 8:
        return 2  # Double XP for 5-7 correct answers
    else:
        return 3  # Triple XP for 8+ correct answers in a row

# Main UI
st.title("🌍 LangaQuest.py – Learn French, Time Travel Style")
st.subheader(f"Current Era: {st.session_state.era}")

# Enhanced sidebar with visual elements
st.sidebar.markdown("### 🏆 Player Stats")

# XP and Level Progress with custom styling - update to include progress bar
st.sidebar.markdown(
    f"""
    <div style="padding:10px; border-radius:10px; background-color:rgba(150,200,255,0.2); margin-bottom:15px;">
        <h4 style="margin:0; color:#4169E1;">🌟 Level {st.session_state.level}</h4>
        <p style="margin:5px 0 5px 0;">XP: {st.session_state.xp} / {XP_FOR_LEVEL_UP}</p>
        <div style="height:20px; background-color:#f0f2f6; border-radius:10px; overflow:hidden;">
            <div style="width:{min(100, int(st.session_state.xp % XP_FOR_LEVEL_UP / XP_FOR_LEVEL_UP * 100))}%; 
                     height:100%; 
                     background-color:#4169E1;
                     border-radius:10px;
                     text-align:center;
                     color:white;
                     font-size:12px;
                     line-height:20px;">
                {min(100, int(st.session_state.xp % XP_FOR_LEVEL_UP / XP_FOR_LEVEL_UP * 100))}%
            </div>
        </div>
        <p style="margin:5px 0 0 0;">Era: <b>{st.session_state.era}</b></p>
        <div style="padding:5px 0;">
            <span style="font-weight:bold; color:#FFD700;">🪙 Coins: {st.session_state.coins}</span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# Streak info with fire emojis
st.sidebar.markdown("#### 🔥 Combo Streak")
# Create visual representation of the streak
if st.session_state.current_streak > 0:
    # Visualize the streak with emojis
    streak_emojis = ""
    for i in range(min(10, st.session_state.current_streak)):
        if i < 3:
            streak_emojis += "🔥"  # Regular fire for first 3
        elif i < 6:
            streak_emojis += "🔥"  # Same emoji, will appear in a row
        else:
            streak_emojis += "💯"  # Special emoji for highest streaks
            
    st.sidebar.markdown(
        f"""
        <div style="padding:10px; border-radius:10px; background-color:rgba(255,200,150,0.2); margin-bottom:15px;">
            <p style="margin:0; font-weight:bold;">Current: {st.session_state.current_streak}</p>
            <p style="margin:5px 0; font-size:18px; letter-spacing:3px;">{streak_emojis}</p>
            <p style="margin:5px 0;">Best: {st.session_state.max_streak}</p>
        """, 
        unsafe_allow_html=True
    )
    
    # Show multiplier with animation effect
    if st.session_state.current_streak >= 3:
        multiplier = calculate_multiplier(st.session_state.current_streak)
        st.sidebar.markdown(
            f"""
            <div style="text-align:center; margin:5px 0; animation: pulse 1.5s infinite;">
                <span style="font-size:18px; font-weight:bold; color:#FF6347;">
                    {multiplier}x XP BONUS!
                </span>
            </div>
            <style>
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                    100% {{ transform: scale(1); }}
                }}
            </style>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            """
            <p style="margin:5px 0; color:#666; font-style:italic;">Get 3+ in a row for bonus XP!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.sidebar.markdown(
        """
        <div style="padding:10px; border-radius:10px; background-color:rgba(255,200,150,0.2); margin-bottom:15px;">
            <p style="margin:0; font-weight:bold;">No active streak</p>
            <p style="margin:5px 0; color:#666; font-style:italic;">Answer correctly to start a streak!</p>
            <p style="margin:5px 0;">Best: 0</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Era conquest tracker
conquered_eras = len(st.session_state.boss_passed)
total_eras = len(ERAS)

st.sidebar.markdown("#### 🌍 Era Conquest")
progress_html = '<div style="display:flex; justify-content:space-between; margin-bottom:10px;">'

for i, era in enumerate(ERAS):
    if era in st.session_state.boss_passed:
        # Conquered era
        emoji = "✅"
        style = "color:#4CAF50; font-weight:bold;"
    elif era == st.session_state.era:
        # Current era
        emoji = "⚔️"
        style = "color:#FF9800; font-weight:bold;"
    else:
        # Future era
        emoji = "🔒"
        style = "color:#9E9E9E; font-style:italic;"
    
    progress_html += f'<div style="text-align:center;"><div style="{style}">{emoji}</div><div style="font-size:10px; {style}">{era[:6]}...</div></div>'

progress_html += '</div>'

st.sidebar.markdown(
    f"""
    <div style="padding:10px; border-radius:10px; background-color:rgba(150,255,150,0.2); margin-bottom:15px;">
        <p style="margin:0 0 10px 0; text-align:center;">{conquered_eras}/{total_eras} Conquered</p>
        {progress_html}
    </div>
    """,
    unsafe_allow_html=True
)

# Game tips that rotate
tips = [
    "💡 Try to maintain your streak for bonus XP!",
    "💡 Watch for accents in French words.",
    "💡 Defeat bosses to travel through time!",
    "💡 The further you go, the harder it gets.",
    "💡 Minor spelling errors are forgiven in boss battles."
]

st.sidebar.markdown("#### 💡 Tip of the Day")
st.sidebar.markdown(
    f"""
    <div style="padding:10px; border-radius:10px; background-color:rgba(255,255,150,0.2);">
        <p style="margin:0; font-style:italic;">{tips[st.session_state.level % len(tips)]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Modified Question Logic ---
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

        st.markdown(f"**{q.get('question', 'Error: Question text missing')}**")

        options = q.get('options', [])
        if not options:
             st.error("Internal error: Question options are missing.")
             # Clear the problematic state and try again
             st.session_state.current_question = None
             st.session_state.question_batch = []
             st.session_state.current_batch_index = 0
             if st.button("Reset and Retry"):
                 st.rerun()
             st.stop()

        # Display streak information
        if st.session_state.current_streak >= 3:
            multiplier = calculate_multiplier(st.session_state.current_streak)
            st.info(f"🔥 Combo Streak: {st.session_state.current_streak} | XP Multiplier: {multiplier}x")

        user_answer = st.radio(
            "Your Answer:",
            options,
            key=f"user_answer_{st.session_state.level}_{question_key_part}",
            index=None # Default to no selection
        )

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

                if user_answer == correct_answer:
                    # Update streak for correct answer
                    st.session_state.current_streak += 1
                    st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.current_streak)
                    
                    # Calculate XP with multiplier
                    multiplier = calculate_multiplier(st.session_state.current_streak)
                    xp_earned = int(XP_PER_QUESTION * multiplier)
                    
                    # Award coins for correct answers
                    coins_earned = int(1 * multiplier)  # Base 1 coin per correct answer, multiplied by streak
                    st.session_state.coins += coins_earned
                    
                    # Different messages based on streak
                    if st.session_state.current_streak >= 8:
                        streak_msg = f"🔥🔥🔥 LEGENDARY STREAK: {st.session_state.current_streak} | {multiplier}x BONUS!"
                    elif st.session_state.current_streak >= 5:
                        streak_msg = f"🔥🔥 AWESOME STREAK: {st.session_state.current_streak} | {multiplier}x BONUS!"
                    elif st.session_state.current_streak >= 3:
                        streak_msg = f"🔥 GOOD STREAK: {st.session_state.current_streak} | {multiplier}x BONUS!"
                    else:
                        streak_msg = "Correct!"
                    
                    st.success(f"{streak_msg} +{xp_earned} XP, +{coins_earned} 🪙")
                    st.session_state.xp += xp_earned
                    
                    # Check if player has earned enough XP to level up
                    if st.session_state.xp >= (st.session_state.level * XP_FOR_LEVEL_UP):
                        level_up()  # Call level up which only increases level now, not era
                        # No need to stop or rerun right away - let the user see both messages
                    
                    # Always just go to the next question
                    st.session_state.current_question = None
                    st.session_state.answered = False
                    st.rerun()
                else:
                    # Reset streak for wrong answer
                    if st.session_state.current_streak >= 3:
                        st.warning(f"Streak broken! You had {st.session_state.current_streak} correct answers in a row.")
                    st.session_state.current_streak = 0
                    st.error(f"Wrong. The correct answer was: {correct_answer}")
                    
                    # Incorrect answer, still move to next question automatically
                    st.session_state.current_question = None # Trigger selection of next question from batch
                    st.session_state.answered = False
                    st.rerun() # Rerun to fetch/select next question

# --- Boss mode ---
elif st.session_state.boss_mode:
    st.header("🧩 Boss Battle!") 
    st.write(f"Translate the following English words/phrases to French to conquer the {st.session_state.era} Era:")

    # Check if we need to fetch boss questions
    if "boss_questions" not in st.session_state or st.session_state.era not in st.session_state.boss_questions:
        # Initialize the boss_questions dict if it doesn't exist
        if "boss_questions" not in st.session_state:
            st.session_state.boss_questions = {}
        
        # Fetch new boss questions from the AI
        st.write("Summoning the boss challenge...")
        boss_qs = get_boss_questions_from_gemini()
        
        # Store these questions for this era
        st.session_state.boss_questions[st.session_state.era] = boss_qs
        st.rerun()  # Rerun to show the form with the questions
    
    # Get the questions for this era
    boss_qs = st.session_state.boss_questions[st.session_state.era]

    # Use a form for boss battles to submit all answers at once cleanly
    with st.form(key=f"boss_form_{st.session_state.era}"):
        user_answers = {}
        for en, fr in boss_qs.items():
            user_answers[en] = st.text_input(f"{en}:", key=f"boss_{st.session_state.era}_{en}")

        submitted = st.form_submit_button("Submit Boss Answers")

        if submitted:
            correct_count = 0
            all_correct = True
            feedback = [] # Store feedback messages
            minor_errors = False

            for en, fr in boss_qs.items():
                if user_answers[en].lower().strip() == fr.lower().strip():
                    # Exact match
                    correct_count += 1
                    feedback.append(f"✅ {en}: Perfect!")
                elif fuzzy_check_answer(user_answers[en], fr):
                    # Close enough match
                    correct_count += 1
                    minor_errors = True
                    feedback.append(f"⚠️ {en}: Almost perfect! (Correct: {fr})")
                else:
                    # Incorrect
                    all_correct = False
                    feedback.append(f"❌ {en}: Incorrect (Correct: {fr})")

            # Display feedback after checking all answers
            for msg in feedback:
                if "✅" in msg:
                    st.success(msg)
                elif "⚠️" in msg:
                    st.info(msg)  # Use info for close matches
                else:
                    st.warning(msg)  # Use warning for incorrect within the form

            # Consider boss defeated if all answers are at least close enough
            if all_correct or correct_count == len(boss_qs):
                # Keep streak going through boss battles
                st.session_state.current_streak += 1
                st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.current_streak)
                
                # Award bonus coins for defeating a boss
                boss_coin_reward = st.session_state.level * 75
                st.session_state.coins += boss_coin_reward
                
                victory_message = f"🏆 You defeated the boss! Earned {boss_coin_reward} 🪙 coins!"
                if minor_errors:
                    victory_message += " (with some minor spelling errors, but that's ok!)"
                st.success(victory_message) 
                st.balloons()
                
                # Mark this boss as defeated
                if st.session_state.era not in st.session_state.boss_passed:
                    st.session_state.boss_passed.append(st.session_state.era)
                    
                    # After defeating a boss, check if we can unlock a new era
                    # Find the current era index
                    current_era_index = ERAS.index(st.session_state.era)
                    # Try to unlock the next era
                    next_era_available = len(st.session_state.boss_passed) >= current_era_index + 1
                    
                    if next_era_available and current_era_index < len(ERAS) - 1:
                        # Show option to travel to next era or stay
                        st.write("🚀 You've unlocked a new era! Would you like to travel there now?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Travel to {ERAS[current_era_index + 1]}"):
                                unlock_era(current_era_index + 1)
                                # Before era change, clear the boss questions for this era
                                if st.session_state.era in st.session_state.boss_questions:
                                    del st.session_state.boss_questions[st.session_state.era]
                                st.rerun()
                        with col2:
                            if st.button(f"Stay in {st.session_state.era}"):
                                # Exit boss mode but stay in current era
                                st.session_state.boss_mode = False
                                if st.session_state.era in st.session_state.boss_questions:
                                    del st.session_state.boss_questions[st.session_state.era]
                                st.rerun()
                    else:
                        # Just exit boss mode
                        st.session_state.boss_mode = False
                        # Clear boss questions
                        if st.session_state.era in st.session_state.boss_questions:
                            del st.session_state.boss_questions[st.session_state.era]
                        st.rerun()
                else:
                    # Just exit boss mode for repeated boss victories
                    st.session_state.boss_mode = False
                    # Clear boss questions
                    if st.session_state.era in st.session_state.boss_questions:
                        del st.session_state.boss_questions[st.session_state.era]
                    st.rerun()
            else:
                # Reset streak on boss failure
                if st.session_state.current_streak >= 3:
                    st.warning(f"Streak broken! You had {st.session_state.current_streak} correct answers in a row.")
                st.session_state.current_streak = 0
                
                st.error(f"❌ You got {correct_count}/{len(boss_qs)} correct or close. Try correcting your answers and submit again!")
                # Provide a hint
                if correct_count > 0:
                    st.info("💡 Hint: Focus on fixing the answers marked with ❌")
                # Keep boss_mode=True, user stays on this screen to retry

# === Shop Section ===
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛒 Shop")

# Create shop items in session state if they don't exist
if "shop_items" not in st.session_state:
    st.session_state.shop_items = {
        "hint_powerup": {
            "name": "Hint Powerup",
            "description": "Get a hint on your next difficult question",
            "price": 10,
            "icon": "💡",
            "purchased": False,
            "era": "all"  # This item is available in all eras
        },
        "stone_meat": {
            "name": "Prehistoric Meat",
            "description": "A chunk of raw mammoth meat - Stone Age delicacy",
            "price": 50,
            "icon": "🥩",
            "purchased": False,
            "era": "Stone Age"  # Only available in Stone Age
        },
        "stone_rock": {
            "name": "Sharp Rock",
            "description": "A primitive tool for hunting and crafting",
            "price": 50,
            "icon": "🪨",
            "purchased": False,
            "era": "Stone Age"  # Only available in Stone Age
        }
    }

# Display shop items - filtered by current era or "all"
current_era = st.session_state.era
st.sidebar.markdown(f"#### Items for {current_era}")

# Filter items for current era or available in all eras
available_items = {item_id: item for item_id, item in st.session_state.shop_items.items() 
                   if item["era"] == current_era or item["era"] == "all"}

if not available_items:
    st.sidebar.markdown("No items available in this era yet.")
else:
    for item_id, item in available_items.items():
        # Create a container for each shop item with custom styling
        st.sidebar.markdown(
            f"""
            <div style="padding:10px; border-radius:10px; background-color:rgba(200,200,255,0.2); margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:18px;">{item['icon']} {item['name']}</span>
                    <span style="font-weight:bold; color:#FFD700;">🪙 {item['price']}</span>
                </div>
                <p style="margin:5px 0; font-size:12px; color:#666;">{item['description']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Add purchase button
        if not item['purchased']:
            if st.sidebar.button(f"Buy {item['name']}", key=f"buy_{item_id}"):
                if st.session_state.coins >= item['price']:
                    st.session_state.coins -= item['price']
                    st.session_state.shop_items[item_id]['purchased'] = True
                    st.sidebar.success(f"You purchased {item['name']}!")
                    st.rerun()  # Refresh to update the UI
                else:
                    st.sidebar.error(f"Not enough coins! You need {item['price'] - st.session_state.coins} more coins.")
        else:
            st.sidebar.success(f"Purchased ✓")

# Add stats display to sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Stats")
st.sidebar.markdown(f"Current Streak: {st.session_state.current_streak}")
st.sidebar.markdown(f"Best Streak: {st.session_state.max_streak}")
if st.session_state.current_streak >= 3:
    multiplier = calculate_multiplier(st.session_state.current_streak)
    st.sidebar.markdown(f"XP Multiplier: {multiplier}x")
st.sidebar.markdown(f"🪙 Coins: {st.session_state.coins}")
st.sidebar.markdown(f"Eras Conquered: {len(st.session_state.boss_passed)}/{len(ERAS)}")

# Add an era selector in the sidebar for traveling between unlocked eras
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Time Travel")

# Filter to only show unlocked eras
unlocked_eras = [ERAS[0]]  # Stone Age is always unlocked
for era in ERAS[1:]:
    if era in st.session_state.boss_passed:
        unlocked_eras.append(era)

# Only show the era selector if player has unlocked more than one era
if len(unlocked_eras) > 1:
    selected_era = st.sidebar.selectbox(
        "Travel to:", 
        unlocked_eras,
        index=unlocked_eras.index(st.session_state.era) if st.session_state.era in unlocked_eras else 0
    )
    
    # Only show travel button if a different era is selected
    if selected_era != st.session_state.era:
        if st.sidebar.button(f"🚀 Travel to {selected_era}"):
            st.session_state.era = selected_era
            st.session_state.current_question = None
            st.session_state.answered = False
            st.session_state.question_batch = []
            st.session_state.current_batch_index = 0
            st.sidebar.success(f"Welcome to {selected_era}!")
            st.rerun()
else:
    st.sidebar.markdown("Defeat the Stone Age boss to unlock time travel!")

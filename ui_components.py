import streamlit as st
from config import XP_FOR_LEVEL_UP, ERAS, TIPS
from game_mechanics import calculate_multiplier

def render_sidebar():
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

    render_era_conquest_tracker()
    render_tip_of_the_day()
    render_era_selector()

def render_era_conquest_tracker():
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

def render_tip_of_the_day():
    # Game tips that rotate
    st.sidebar.markdown("#### 💡 Tip of the Day")
    st.sidebar.markdown(
        f"""
        <div style="padding:10px; border-radius:10px; background-color:rgba(255,255,150,0.2);">
            <p style="margin:0; font-style:italic;">{TIPS[st.session_state.level % len(TIPS)]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_era_selector():
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

def render_question(q, question_key_part):
    from config import XP_PER_QUESTION
    from game_mechanics import calculate_multiplier

    # Identify and categorize question type for Era 1 stats tracking
    if st.session_state.era == ERAS[0]:
        # Initialize if needed
        if "question_type_stats" not in st.session_state:
            st.session_state.question_type_stats = {
                "numbers": {"total": 0, "correct": 0},
                "weekdays": {"total": 0, "correct": 0},
                "months": {"total": 0, "correct": 0},
                "greetings": {"total": 0, "correct": 0},
                "colors": {"total": 0, "correct": 0}
            }
            
        # Only categorize the question once when it's first displayed
        if not hasattr(st.session_state, "current_question_categorized") or not st.session_state.current_question_categorized:
            question_text = q.get('question', '').lower()
            
            # Identify question type based on keywords
            if any(word in question_text for word in ['number', 'count', 'how many', 'un', 'deux', 'trois']):
                current_type = 'numbers'
            elif any(word in question_text for word in ['day', 'week', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
                current_type = 'weekdays'
            elif any(word in question_text for word in ['month', 'january', 'february', 'march', 'april', 'may', 'june']):
                current_type = 'months'
            elif any(word in question_text for word in ['hello', 'hi', 'goodbye', 'bonjour', 'salut']):
                current_type = 'greetings'
            elif any(word in question_text for word in ['color', 'red', 'blue', 'green', 'yellow', 'black']):
                current_type = 'colors'
            else:
                current_type = 'greetings'  # Default category
            
            # Store for use in handle_answer
            st.session_state.current_question_type = current_type
            st.session_state.current_question_categorized = True
            
            # Increment the total for this question type
            st.session_state.question_type_stats[current_type]["total"] += 1

    # Display fun fact every 10 questions
    if hasattr(st.session_state, 'questions_answered') and st.session_state.questions_answered > 0 and st.session_state.questions_answered % 10 == 0:
        # Simple fun facts about French
        fun_facts = [
            "The word 'bonjour' combines 'bon' (good) and 'jour' (day), similar to 'good day' in English.",
            "French is spoken by about 300 million people worldwide and is an official language in 29 countries.",
            "About 30% of English vocabulary comes from French.",
            "The French alphabet has the same 26 letters as English, but the pronunciation is quite different.",
            "In French restaurants, bread is usually served without butter."
        ]
        import random
        random_fact = random.choice(fun_facts)
        
        st.markdown(
            f"""
            <div style="padding:15px; border-radius:10px; background-color:rgba(255,233,125,0.3); 
                        margin-bottom:20px; border-left:4px solid #FFD700;">
                <h4 style="margin:0 0 5px 0; color:#B8860B;">✨ Fun Fact!</h4>
                <p style="margin:0;">{random_fact}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(f"**{q.get('question', 'Error: Question text missing')}**")

    options = q.get('options', [])
    if not options:
        st.error("Internal error: Question options are missing.")
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

    # Disable the radio buttons if the question has been answered
    disabled = st.session_state.answered if hasattr(st.session_state, 'answered') else False
    
    user_answer = st.radio(
        "Your Answer:",
        options,
        key=f"user_answer_{st.session_state.level}_{question_key_part}",
        index=None, # Default to no selection
        disabled=disabled
    )

    # Add a "Next Question" button if the question has been answered
    if st.session_state.answered:
        if st.button("Next Question", key=f"next_q_{question_key_part}"):
            # Clear question state to move to next question
            st.session_state.current_question = None
            st.session_state.answered = False
            st.session_state.current_question_categorized = False  # Reset categorization flag
            st.rerun()

    return user_answer

def handle_answer(user_answer, correct_answer):
    from config import XP_PER_QUESTION
    from game_mechanics import calculate_multiplier
    
    # Increment questions answered counter
    if "questions_answered" not in st.session_state:
        st.session_state.questions_answered = 1
    else:
        st.session_state.questions_answered += 1
    
    if user_answer == correct_answer:
        # Update streak for correct answer
        st.session_state.current_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.current_streak)
        
        # Update Era 1 stats if applicable
        if st.session_state.era == ERAS[0] and hasattr(st.session_state, 'current_question_type'):
            question_type = st.session_state.current_question_type
            if "question_type_stats" in st.session_state and question_type in st.session_state.question_type_stats:
                st.session_state.question_type_stats[question_type]["correct"] += 1
        
        # Calculate XP with multiplier
        multiplier = calculate_multiplier(st.session_state.current_streak)
        xp_earned = int(XP_PER_QUESTION * multiplier)
        
        # Award coins for correct answers
        coins_earned = int(1 * multiplier)
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
        
        from game_mechanics import level_up
        
        # Check if player has earned enough XP to level up
        if st.session_state.xp >= (st.session_state.level * XP_FOR_LEVEL_UP):
            level_up()
        
        # Mark as answered but don't clear question yet
        st.session_state.answered = True
        return True
    else:
        # Reset streak for wrong answer
        if st.session_state.current_streak >= 3:
            st.warning(f"Streak broken! You had {st.session_state.current_streak} correct answers in a row.")
        st.session_state.current_streak = 0
        st.error(f"Wrong. The correct answer was: {correct_answer}")
        
        # Mark as answered but don't clear question yet
        st.session_state.answered = True
        return False

def render_boss_battle():
    st.header("🧩 Boss Battle!") 
    st.write(f"Translate the following English words/phrases to French to conquer the {st.session_state.era} Era:")

    # Check if we need to fetch boss questions
    if "boss_questions" not in st.session_state or st.session_state.era not in st.session_state.boss_questions:
        # Initialize the boss_questions dict if it doesn't exist
        if "boss_questions" not in st.session_state:
            st.session_state.boss_questions = {}
        
        # Fetch new boss questions from the AI
        st.write("Summoning the boss challenge...")
        from ai_generator import get_boss_questions_from_gemini
        boss_qs = get_boss_questions_from_gemini()
        
        # Store these questions for this era
        st.session_state.boss_questions[st.session_state.era] = boss_qs
        st.rerun()  # Rerun to show the form with the questions
    
    # Get the questions for this era
    boss_qs = st.session_state.boss_questions[st.session_state.era]
    
    handle_boss_form(boss_qs)

def handle_boss_form(boss_qs):
    from game_mechanics import fuzzy_check_answer, unlock_era
    
    # Check if boss was already defeated and we're showing navigation options
    if "boss_victory" in st.session_state and st.session_state.boss_victory:
        # Show era navigation options outside the form
        
        # Fix for numeric era values - convert to string if needed
        if isinstance(st.session_state.era, int) or (isinstance(st.session_state.era, str) and st.session_state.era.isdigit()):
            # If era is a number (e.g. "1"), treat it as an index into ERAS list
            try:
                era_index = int(st.session_state.era) - 1  # Convert to 0-based index
                if 0 <= era_index < len(ERAS):
                    st.session_state.era = ERAS[era_index]
                    st.info(f"Converted numeric era to: {st.session_state.era}")
                else:
                    st.session_state.era = ERAS[0]  # Default to first era if out of range
                    st.error(f"Invalid era index: {era_index+1}. Resetting to {ERAS[0]}.")
            except ValueError:
                st.session_state.era = ERAS[0]  # Default to first era on error
                st.error(f"Invalid era format. Resetting to {ERAS[0]}.")
                
        # Now try to get the era index
        try:
            current_era_index = ERAS.index(st.session_state.era)
        except ValueError:
            # Handle the case where the era is still not in the ERAS list
            st.error(f"Error: Current era '{st.session_state.era}' not found in eras list. Resetting to first era.")
            st.session_state.era = ERAS[0]  # Reset to the first era
            current_era_index = 0  # Use index 0
            
        # Check if we can unlock the next era
        if current_era_index < len(ERAS) - 1:
            st.success("🏆 Boss defeated! Choose your next step:")
            st.write("🚀 You've unlocked a new era! Would you like to travel there now?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Travel to {ERAS[current_era_index + 1]}"):
                    unlock_era(current_era_index + 1)
                    # Clean up temp states
                    if st.session_state.era in st.session_state.boss_questions:
                        del st.session_state.boss_questions[st.session_state.era]
                    st.session_state.boss_victory = False
                    st.session_state.boss_mode = False
                    st.rerun()
            with col2:
                if st.button(f"Stay in {st.session_state.era}"):
                    # Clean up temp states
                    st.session_state.boss_victory = False
                    st.session_state.boss_mode = False
                    if st.session_state.era in st.session_state.boss_questions:
                        del st.session_state.boss_questions[st.session_state.era]
                    st.rerun()
        else:
            st.success("🏆 Boss defeated!")
            if st.button("Continue"):
                st.session_state.boss_victory = False
                st.session_state.boss_mode = False
                if st.session_state.era in st.session_state.boss_questions:
                    del st.session_state.boss_questions[st.session_state.era]
                st.rerun()
        return

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
                    
                    # Set a flag to show navigation options after form submission
                    st.session_state.boss_victory = True
                    st.rerun()  # Rerun to show the navigation options outside the form
                else:
                    # Just exit boss mode for repeated boss victories
                    st.session_state.boss_mode = False
                    # Clean up
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


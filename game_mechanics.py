import streamlit as st
from config import XP_FOR_LEVEL_UP, ERAS

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

# Initialize session state variables
def initialize_session_state():
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
    
    # Ensure stats are initialized
    if "question_type_stats" not in st.session_state:
        st.session_state.question_type_stats = {
            "numbers": {"total": 0, "correct": 0},
            "weekdays": {"total": 0, "correct": 0},
            "months": {"total": 0, "correct": 0},
            "greetings": {"total": 0, "correct": 0},
            "colors": {"total": 0, "correct": 0}
        }

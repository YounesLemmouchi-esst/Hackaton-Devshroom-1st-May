import os
import json
import re
import google.generativeai as genai0
import streamlit as st

from config import GEMINI_MODEL, CREDENTIALS_PATH, ERAS

# Add this where you initialize your session state variables
if "era" not in st.session_state:
    st.session_state.era = 1

# Initialize Gemini AI
def initialize_ai():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH
    genai.configure()
    return genai.GenerativeModel(GEMINI_MODEL)

# Get AI model instance
def get_ai_model():
    # Lazy loading of the model
    if "ai_model" not in st.session_state:
        st.session_state.ai_model = initialize_ai()
    return st.session_state.ai_model

# Function for era-based prompts (replacing get_prompt_by_level)
def get_prompt_by_era(era):
    if era == 1:  # First era
        return (
            "Generate 3 *different* super easy questions about the French language for absolute beginners. "
            "THE QUESTIONS MUST BE WRITTEN IN ENGLISH ONLY - DO NOT USE FRENCH FOR THE QUESTIONS. "
            "Focus on a *variety* of basic concepts including:\n"
            "- Simple greetings \n"
            "- Basic numbers \n"
            "- Days of the week \n"
            "- Common colors \n"
            "- Simple nouns \n"
            "- Months of the year \n"
            "Ensure the questions cover *different* topics from this list within the batch, avoiding repetition of the same concept. "
            "Example of correct format: 'How do you say \"hello\" in French?' NOT 'Comment dit-on \"hello\" en français?' "
            "IMPORTANT: DO NOT GENERATE QUESTIONS IN FRENCH. ALL QUESTIONS MUST BE IN ENGLISH. "
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
    elif era == 2:  # Second era
        return (
            "Generate 3 different beginner-level questions about the French language for learners who have just started understanding sentence structure and basic vocabulary. "
            "THE QUESTIONS MUST BE WRITTEN IN ENGLISH ONLY - DO NOT USE FRENCH FOR THE QUESTIONS. "
            "Focus on a variety of beginner concepts including:\n"
            "- Basic verbs like 'to be' and 'to have'\n"
            "- Gender of nouns (masculine/feminine)\n"
            "- Simple everyday vocabulary (house, cat, book, etc.)\n"
            "- Pronouns (I, you, he, she)\n"
            "- Definite and indefinite articles (the, a/an)\n"
            "Avoid repeating the same topic within a batch. "
            "IMPORTANT: DO NOT INCLUDE ANY FRENCH IN THE QUESTION TEXT. "
            "do not use previous era questions"
            "Return exactly 3 questions in this JSON format:\n"
            '[\n'
            ' {\n'
            ' "question": "...",\n'
            ' "options": ["...", "...", "..."],\n'
            ' "answer": "..." \n'
            ' },\n'
            ' {...},\n'
            ' {...}\n'
            ']'
            )
    elif era == 3:  # Third era
        return (
            "Generate 3 different French language quiz questions at a lower-intermediate level. "
            "Write the questions in ENGLISH ONLY. DO NOT use French in the question itself. "
            "Cover a variety of grammar and vocabulary topics including:\n"
            "- Present tense verb conjugation for 'I', 'you', and 'we' forms\n"
            "- How to form negative sentences in French\n"
            "- Adjective placement and agreement\n"
            "- Question words like 'what', 'where', 'how'\n"
            "- Frequency adverbs like 'often', 'never', etc.\n"
            "Each question should test a different concept. "
            "Use multiple-choice format and return ONLY this JSON structure:\n"
            '[\n'
            ' {\n'
            ' "question": "...",\n'
            ' "options": ["...", "...", "..."],\n'
            ' "answer": "..." \n'
            ' },\n'
            ' {...},\n'
            ' {...}\n'
            ']'
        )
    elif era == 4:  # Fourth era
        return (
            "Generate 3 different intermediate-level questions about the French language. "
            "THE QUESTIONS MUST BE WRITTEN ENTIRELY IN ENGLISH. DO NOT use any French text in the question. "
            "Cover a variety of intermediate topics, making sure each question addresses a different concept. Topics to include:\n"
            "- Irregular verb conjugation (e.g., 'to go', 'to do')\n"
            "- Reflexive verbs and how they are structured\n"
            "- Possessive adjectives ('my', 'your', etc.)\n"
            "- Common prepositions of location ('in', 'on', 'under')\n"
            "- Everyday idioms or expressions (e.g., 'I’m hungry' → 'I have hunger')\n"
            "Return only this JSON format:\n"
            '[\n'
            ' {\n'
            ' "question": "...",\n'
            ' "options": ["...", "...", "..."],\n'
            ' "answer": "..." \n'
            ' },\n'
            ' {...},\n'
            ' {...}\n'
            ']'
        )
    else:  # Fifth era (era == 5)
        return (
            "Generate 3 different upper-intermediate level questions about the French language. "
            "Questions MUST be written in ENGLISH ONLY. DO NOT use French in the question. "
            "Focus on challenging but common language topics. Each question must test a different concept from this list:\n"
            "- Forming the passé composé with auxiliary verbs\n"
            "- Differences between 'this', 'that', 'these', 'those' in French\n"
            "- Comparing things using adjectives ('bigger', 'more expensive', etc.)\n"
            "- Translating full simple English sentences into French\n"
            "- Using time expressions (e.g., 'last week', 'in the morning')\n"
            "Strictly follow the JSON format below and include no other output:\n"
            '[\n'
            ' {\n'
            ' "question": "...",\n'
            ' "options": ["...", "...", "..."],\n'
            ' "answer": "..." \n'
            ' },\n'
            ' {...},\n'
            ' {...}\n'
            ']'
        )

# Add this function after get_question_batch_from_gemini

def validate_english_questions(questions):
    """Check if questions appear to be in English"""
    if not questions:
        return questions
    
    # List of common French words that shouldn't appear at the start of English questions
    french_indicators = ['comment', 'quel', 'quelle', 'quels', 'quelles', 'où', 'qui', 'pourquoi', 
                        'quand', 'combien', 'est-ce', 'qu\'est-ce']
    
    validated_questions = []
    regenerate_needed = False
    
    for item in questions:
        question = item["question"].lower().strip()
        # Check if question starts with a French interrogative word
        if any(question.startswith(word) for word in french_indicators):
            regenerate_needed = True
            st.warning(f"Question appears to be in French: {item['question']}")
        else:
            validated_questions.append(item)
    
    if regenerate_needed:
        st.warning("Some questions were detected as being in French and were filtered out.")
    
    return validated_questions

# Modify get_question_batch_from_gemini to use validation
def get_question_batch_from_gemini():
    model = get_ai_model()
    
    # Convert era name to index if needed
    era_index = 1  # Default to first era
    if isinstance(st.session_state.era, str):
        try:
            era_index = ERAS.index(st.session_state.era) + 1
        except ValueError:
            st.error(f"Invalid era: {st.session_state.era}. Using default era.")
            era_index = 1
    elif isinstance(st.session_state.era, int):
        era_index = st.session_state.era
    
    prompt = get_prompt_by_era(era_index)
    
    # Keep trying until we get valid questions or max retries
    max_retries = 3
    attempts = 0
    
    while attempts < max_retries:
        attempts += 1
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Use the existing JSON extraction code
            match = re.search(r"```(json)?\s*(\[.*?\])\s*```", response_text, re.DOTALL)
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
                    if attempts < max_retries:
                        continue  # Try again
                    st.text("Raw Response:")
                    st.text(response_text)
                    return [] # Return empty list on failure

            # Parse JSON
            data = json.loads(json_string)
            if isinstance(data, list):
                import random
                random.shuffle(data)
                return data[:3]  # Return up to 3 questions
            else:
                st.error("❌ Parsed JSON is not a list as expected.")
                if attempts < max_retries:
                    continue  # Try again
                st.text("Parsed Data Type:")
                st.text(type(data))
                st.text("Raw Response:")
                st.text(response_text)
                return [] # Return empty list on failure

        except Exception as e:
            st.error(f"❌ Error in attempt {attempts}: {str(e)}")
            if attempts < max_retries:
                continue  # Try again
            return []  # Return empty list after all retries fail
            
    # If we get here, all attempts failed
    st.error("Failed to generate valid questions after multiple attempts.")
    return []

# New function for boss questions using Gemini
def get_boss_questions_from_gemini():
    model = get_ai_model()
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

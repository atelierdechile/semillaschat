import streamlit as st
import os
import time
from datetime import datetime
from rapidfuzz import process, fuzz

# 1. Setup the website title & page config (Adds a nice browser tab icon)
st.set_page_config(page_title="Guardianes de semillas", page_icon="🍷")
st.title("🤖 Asistente para tu intercambio de semillas")

# 2. Define your automated questions and answers
qa_pairs = {
    "Tomates": "Juan, Pedro, Ximena",
"Zapallos": "Juan, Alfonso",
"Lechugas": "Ignacio, Claudia",
}

# 3. Create the user chat history & Welcome Message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hola! Queremos ayuadrte a encontrar las semillas que buscas. Si haces click en el nombre de semilla te diremos quienes tienen para intercambiar"}
    ]

if "waiting_for_email" not in st.session_state:
    st.session_state.waiting_for_email = None

# Display past conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. PREDEFINED BUTTONS INTERFACE
st.write("---") # Adds a clean dividing line
st.write("💡 **Las semillas que están hoy son:**")
button_pressed = None

# Only show buttons if we aren't in the middle of capturing an email
if not st.session_state.waiting_for_email:
    questions_list = list(qa_pairs.keys())
    max_buttons_per_row = 5
    
    # Loop through the questions in chunks of 5
    for i in range(0, len(questions_list), max_buttons_per_row):
        # Get the next chunk of up to 5 questions
        row_questions = questions_list[i : i + max_buttons_per_row]
        
        # Create the exact number of columns needed for this specific row
        cols = st.columns(len(row_questions))
        
        # Render the buttons in this row
        for idx, question in enumerate(row_questions):
            with cols[idx]:
                # Unique key using the global index (i + idx) to prevent Streamlit duplicate errors
                global_idx = i + idx
                if st.button(question, key=f"btn_{global_idx}", use_container_width=True):
                    button_pressed = question

# 5. CHAT LOGIC
placeholder_text = "Type your email here..." if st.session_state.waiting_for_email else "Type your question here..."
user_input = st.chat_input(placeholder_text)

final_input = button_pressed if button_pressed else user_input

if final_input:
    # A. Display the user's input immediately
    with st.chat_message("user"):
        st.markdown(final_input)
    st.session_state.messages.append({"role": "user", "content": final_input})

    # B. Trigger a realistic "Thinking..." animation
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(0.6) # Creates a short, realistic 0.6-second delay
            
            # Handle Lead Generation Data Saving
            if st.session_state.waiting_for_email:
                user_email = final_input.strip()
                unanswered_question = st.session_state.waiting_for_email
                
                log_entry = f"Date: {datetime.now()} | Email: {user_email} | Question: {unanswered_question}\n"
                with open("leads_log.txt", "a", encoding="utf-8") as f:
                    f.write(log_entry)
                    
                bot_response = "Thank you! I have saved your details. Our team will email you an answer shortly."
                st.session_state.waiting_for_email = None

            # Handle standard questions using Fuzzy Matching
            else:
                clean_input = final_input.lower().strip()
                questions_list = list(qa_pairs.keys())
                
                best_match = process.extractOne(clean_input, questions_list, scorer=fuzz.WRatio, score_cutoff=70)
                
                if best_match:
                    matched_question = best_match[0]
                    bot_response = qa_pairs[matched_question]
                else:
                    bot_response = "I'm not quite sure about that one. Would you mind leaving your email address so our team can get back to you directly?"
                    st.session_state.waiting_for_email = final_input

            # Display the bot response inside the spinner block
            st.markdown(bot_response)
            
    # C. Save bot response to history and refresh
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()

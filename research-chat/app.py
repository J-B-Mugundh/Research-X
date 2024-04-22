from dotenv import load_dotenv
load_dotenv()  # loading all the environment variables

import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define research prompt templates for each field
field_prompts = {
    "Blockchain": "In the context of blockchain technology, answer my questions in a comprehensive and informative way, using credible sources. ",
    "Autonomous Vehicles": "As a research assistant specializing in autonomous vehicles, answer my questions in a comprehensive and informative way, using credible sources. ",
    "Unmanned Aerial Vehicles": "Focusing on unmanned aerial vehicles (UAVs), answer my questions in a comprehensive and informative way, using credible sources. ",
    "Internet of Things": "Regarding the Internet of Things (IoT), answer my questions in a comprehensive and informative way, using credible sources. ",
    "Generative AI": "For inquiries about Generative AI (GenAI), answer my questions in a comprehensive and informative way, using credible sources. ",
}

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])


def get_gemini_response(question, field):
    prompt = field_prompts[field] + question
    response = chat.send_message(prompt, stream=True)
    return response


# Initialize Streamlit app
st.set_page_config(page_title="Next-Gen Research Assistant")

st.header("Next-Gen Research Assistant LLM")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Add field selection dropdown
selected_field = st.selectbox("Select Field:", list(field_prompts.keys()))

input_text = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

if submit and input_text:
    response = get_gemini_response(input_text, selected_field)
    # Add user query and response to session state chat history
    st.session_state['chat_history'].append(("You", input_text))
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot", chunk.text))
    st.markdown("---") 

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")

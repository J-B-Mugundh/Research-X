from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import pathlib
import textwrap
from PIL import Image


import google.generativeai as genai


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define default prompt for research assistant role
default_prompt = "As a research assistant specializing in analyzing architecture and system model diagrams from research papers, "

# Function to load OpenAI model and get responses
def get_gemini_response(input_text, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    if input_text != "":
        prompt = default_prompt + input_text
        response = model.generate_content([prompt, image])
    else:
        response = model.generate_content(image)
    return response.text

# Initialize Streamlit app
st.set_page_config(page_title="Next-Gen Research Assistant")

st.header("Next-Gen Research Assistant LLM")

# Text input for additional prompt refinements
input_text = st.text_input("Input: ", key="input")

# Image upload section
uploaded_file = st.file_uploader("Choose an image of a research paper diagram...", type=["jpg", "jpeg", "png"])
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Research Paper Diagram", use_column_width=True)

submit = st.button("Analyze the diagram")

if submit:
    # Combine default prompt with user input (if provided)
    prompt = default_prompt
    if input_text:
        prompt += input_text

    response = get_gemini_response(prompt, image)
    st.subheader("Analysis Result")
    st.write(response)

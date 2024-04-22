import streamlit as st
from PyPDF2 import PdfReader
from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
import os
import nltk
nltk.download('punkt')

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def summarize_text(text, num_words):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summarizer.stop_words = [" "]
    summary = summarizer(parser.document, num_words)
    summarized_text = " ".join([str(sentence) for sentence in summary])

    words = summarized_text.split()
    if len(words) > num_words:
        summarized_text = " ".join(words[:num_words])
    
    return summarized_text


def main():
    st.set_page_config("Summarize Research Paper")
    st.header("Summarize Research Paper 💡")

    num_words_to_summarize = st.number_input("Enter the number of words for summarization", min_value=10, max_value=1000, value=100)

    pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True)

    if st.button("Summarize"):
        if pdf_docs is not None and num_words_to_summarize is not None:
            with st.spinner("Summarizing..."):
                raw_text = get_pdf_text(pdf_docs)
                summarized_text = summarize_text(raw_text, num_words_to_summarize)
                st.write("Summarized Text:")
                st.write(summarized_text)
        else:
            st.warning("Please upload PDF files and specify the number of words for summarization.")

if __name__ == "__main__":
    main()

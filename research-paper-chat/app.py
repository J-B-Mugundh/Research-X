import streamlit as st
import subprocess
import shutil
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables (assuming you have a GOOGLE_API_KEY)
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define a session state variable to store the selected file
if 'selected_file' not in st.session_state:
    st.session_state['selected_file'] = None

def list_repo_files(repo_url):
    """Clones a GitHub repository and lists its files.

    Args:
        repo_url (str): The URL of the GitHub repository.

    Returns:
        list: A list of filenames within the cloned repository.
    """
    try:
        try:
            import shutil
            shutil_available = True
        except ImportError:
            shutil_available = False

        if shutil_available:
            shutil.rmtree("cloned_repo", ignore_errors=True)  # Clean up previous clones
            subprocess.run(["git", "clone", repo_url, "cloned_repo"], check=True)
        else:
            subprocess.run(["gh", "repo", "clone", repo_url, "cloned_repo"], check=True)

        files = []
        for root, _, filenames in os.walk("cloned_repo"):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files
    except subprocess.CalledProcessError as e:
        st.error(f"Error cloning repository: {e}")
        return []
    finally:
        # Uncomment to automatically remove the cloned repo after listing
        # shutil.rmtree("cloned_repo", ignore_errors=True)
        pass

def explain_file_content(file_content):
    """Explains the content of the file using Gemini API.

    Args:
        file_content (str): The content of the file to be explained.

    Returns:
        str: The explanation of the file content.
    """
    text_chunks = get_text_chunks(file_content)
    # No need to call get_vector_store again here

    user_question = "Explain the contents in the file"
    explanation = user_input(user_question, text_chunks)  # Capture the explanation
    return explanation


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Explain the contents in the file\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question, text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Load the local FAISS index with dangerous deserialization allowed
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question},
        return_only_outputs=True
    )

    return response["output_text"]

st.set_page_config(page_title="Clone, Upload, and Explain")

# Section for Cloning a GitHub Repository
with st.expander("Clone a GitHub Repository"):
    st.subheader("Enter the URL of a GitHub repository to list its files:")
    repo_url = st.text_input("GitHub Repository URL")

    if st.button("Clone Repository"):
        if not repo_url:
            st.error("Please enter a valid GitHub repository URL.")
        else:
            files = list_repo_files(repo_url)
            if files:
                st.success("Successfully cloned and listed files:")
                for file in files:
                    st.write(file)

# Section for Uploading a File
st.subheader("Upload a File for Explanation")
uploaded_file = st.file_uploader("Upload a file to explain its content:", type=["txt", "csv"])

if uploaded_file is not None:
    try:
        # Read file content
        file_content = uploaded_file.getvalue().decode("utf-8")

        # Process content using Gemini (assuming you have the get_text_chunks and user_input functions defined previously)
        st.subheader("Explanation:")
        explanation = explain_file_content(file_content)
        st.write(explanation)
    except Exception as e:
        st.error(f"Error processing file: {e}")

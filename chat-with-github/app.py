import streamlit as st
import subprocess
import shutil
import os

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
        # Attempt to import shutil to check its availability
        try:
            import shutil
            shutil_available = True
        except ImportError:
            shutil_available = False

        # Clone the repository using the appropriate command (Git or GitHub CLI)
        if shutil_available:  # Check if shutil is available
            shutil.rmtree("cloned_repo", ignore_errors=True)  # Clean up previous clones
            subprocess.run(["git", "clone", repo_url, "cloned_repo"], check=True)
        else:
            subprocess.run(["gh", "repo", "clone", repo_url, "cloned_repo"], check=True)

        # List files within the cloned repository
        files = []
        for root, _, filenames in os.walk("cloned_repo"):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files
    except subprocess.CalledProcessError as e:
        st.error(f"Error cloning repository: {e}")
        return []
    finally:
        # Clean up the cloned repository (optional)
        # Uncomment the following line to automatically remove the cloned repo after listing
        # shutil.rmtree("cloned_repo", ignore_errors=True)
        pass  # Placeholder to satisfy indentation requirement

def display_file_content(file_path):
    """Attempts to read the content of a file and display it in the app.

    Args:
        file_path (str): The path to the file to be displayed.
    """
    try:
        # Open the file in read mode
        with open(file_path, "r") as file:
            content = file.read()
            st.write(content)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
    except PermissionError:
        st.error(f"Insufficient permissions to access file: {file_path}")

st.title("GitHub Codebase Analyzer LLM for Research")
st.subheader("Enter the URL of a GitHub repository to list its files:")

repo_url = st.text_input("GitHub Repository URL")

if st.button("List Files"):
    if not repo_url:
        st.error("Please enter a valid GitHub repository URL.")
    else:
        files = list_repo_files(repo_url)
        if files:
            st.success("Successfully cloned and listed files:")
            for file in files:
                st.write(file)  # Display each file path

            # Get user input for file selection
            selected_file = st.text_input("Enter filename or path to view its content:", key="filename_input")
            st.session_state['selected_file'] = selected_file  # Update session state

# Separate part of the app for file upload
st.sidebar.title("File Upload")
uploaded_file = st.sidebar.file_uploader("Upload a file to view its content:", type=["txt", "csv", "py", "json"])
if uploaded_file is not None:
    with st.sidebar.expander("Uploaded File Content"):
        file_content = uploaded_file.getvalue().decode("utf-8")
        st.write(file_content)

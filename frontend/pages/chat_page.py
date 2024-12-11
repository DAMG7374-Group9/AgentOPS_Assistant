import base64
import io
import streamlit as st
from dotenv import load_dotenv
from frontend.utils.chat import fetch_file_from_s3
from frontend.utils.auth import make_authenticated_request




def qa_interface():
    st.title("Research Question Answering Interface")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if 'selected_document' in st.session_state and st.session_state.selected_document:
        doc = st.session_state.selected_document
        st.subheader(f"Analyzing: {doc['filename']}")
    else:
        st.warning("Please select a document to begin your research.")

if __name__ == "__main__":
    qa_interface()

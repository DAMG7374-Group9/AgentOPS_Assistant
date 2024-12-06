import base64
import io
import os

import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from frontend.utils.chat import fetch_file_from_s3
from frontend.utils.auth import make_authenticated_request

# Load environment variables from .env file if present
load_dotenv()

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

# Validate AWS credentials (optional)
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_REGION or not AWS_S3_BUCKET:
    st.error("AWS credentials are not properly set. Please check your environment variables.")
    st.stop()

BACKEND_URL = "http://localhost:8000/articles"  # Replace with the actual backend URL

DEFAULT_IMAGE_PATH = "path/to/your/default/image.png"  # Local path to a default image

def _get_image_base64(image_url):
    """Convert image URL to base64 string."""
    try:
        # Fetch the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad responses
        img = Image.open(io.BytesIO(response.content))

        # Convert the image to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        # In case of an error, use the default image
        try:
            with Image.open(DEFAULT_IMAGE_PATH) as default_img:
                buffer = io.BytesIO()
                default_img.save(buffer, format="PNG")
                return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            st.error("Default image not found.")
            return ""

def fetch_documents():
    """Fetch all documents from the backend API."""
    try:
        response = make_authenticated_request("/articles/", "GET")

        return response
    except requests.exceptions.RequestException as e:
        st.error("Failed to load documents from the server.")
        return []

def get_s3_image_url(image_key):
    """Construct the S3 image URL."""
    return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{image_key}"




def list_docs_page():
    st.title("Document List")

    # Fetch documents from backend API
    documents = fetch_documents()
    if not documents:
        st.write("No documents available.")
        return

    selected_doc_name = st.selectbox("Choose a document", [doc["filename"] for doc in documents])
    if selected_doc_name:
        if st.button(f"View {selected_doc_name}"):
            selected_doc = next((doc for doc in documents if doc["filename"] == selected_doc_name), None)
            if selected_doc:
                st.session_state.selected_document = selected_doc
                st.rerun()

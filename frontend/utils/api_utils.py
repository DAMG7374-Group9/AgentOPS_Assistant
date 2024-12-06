import requests
import streamlit as st


def generate_document_summary(doc_id):
    """Generate document summary using NVIDIA services"""
    response = requests.post(
        f"{st.secrets['API_URL']}/generate_summary", json={"document_id": doc_id}
    )
    return response.json()["summary"]


def process_question(question, doc_id):
    """Process question using multi-modal RAG"""
    response = requests.post(
        f"{st.secrets['API_URL']}/process_question",
        json={"question": question, "document_id": doc_id, "context_needed": "minimal"},
    )
    return response.json()

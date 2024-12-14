import streamlit as st
import requests
import os

from frontend.config import settings
from frontend.utils.auth import make_authenticated_request


def transcribe():
    # Title and description
    st.title("Audio Transcription and Diarization")
    st.write("Upload an audio file to transcribe it with speaker diarization. The processed transcription will be uploaded to S3.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a", "flac"])

    if uploaded_file is not None:
        st.write(f"File uploaded: {uploaded_file.name}")

        # Save the uploaded file temporarily
        temp_file_path = os.path.join("temp_audio", uploaded_file.name)
        os.makedirs("temp_audio", exist_ok=True)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.read())

        # Send file to backend
        with open(temp_file_path, "rb") as audio_file:
            files = {"file": audio_file}
            with st.spinner("Processing the audio file..."):
                response = make_authenticated_request(
                    endpoint="transcribe/upload-audio/",
                    method="POST",
                    files=files
                )
                st.session_state.transcription = response
                st.success("Transcription completed!")

        # Clean up temporary files
        os.remove(temp_file_path)

    st.divider()
    if st.session_state.get("transcription") is not None:
        st.subheader(f"Transcript summarized and customized to signed-in user:")
        st.write(st.session_state.transcription["personalized_summary"])

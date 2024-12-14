import streamlit as st
import requests

from frontend.utils.auth import make_authenticated_request


def chat_interface():
    st.title("💼 MeetPRO Insights: Employee Assistant")

    # Initialize the session state for conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    col1, col2 = st.columns([2, 3])

    # Left Column: Email Inputs and Summary
    with col1:
        if "transcription" in st.session_state:
            with open("transcript1.txt", "r", encoding="utf-8") as f:
                transcript = f.read()
            st.markdown(f"<div>{transcript}</div>", unsafe_allow_html=True)

    # Right Column: Chatbot
    with col2:
        st.subheader("🤖 Chat Assistant")

        user_input = st.text_input("Ask a question about the meeting:")
        if st.button("Send") and user_input.strip():
            response = make_authenticated_request(
                endpoint="/chat/query",
                method="POST",
                data={
                    "model": "gpt-4o",
                    "prompt": user_input,
                    "transcription_id": 1,
                    "chat_session_id": None,
                    "transcript": transcript
                }
            )
            answer = response["response"]

            # Save the interaction in session state
            st.session_state.conversation.append({"user": user_input, "bot": answer})

        # Display conversation history
        st.markdown("### Conversation History")
        for chat in st.session_state.conversation:
            with st.chat_message("user"):
                st.markdown(f"{chat['user']}")
            with st.chat_message("assistant"):
                st.markdown(f"{chat['bot']}")

if __name__ == "__main__":
    chat_interface()

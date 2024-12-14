import streamlit as st


def chat_interface():
    st.set_page_config(page_title="MeetPro Insights - Chat", layout="wide")
    st.title("💼 MeetPRO Insights: Employee Assistant")

    col1, col2 = st.columns([2, 3])

    # Left Column: Email Inputs and Summary
    with col1:
        if "transcription" in st.session_state:
            st.markdown(f"<div>{st.session_state.transcription["personalized_summary"]}</div>", unsafe_allow_html=True)

    # Right Column: Chatbot
    with col2:
        st.subheader("🤖 Chat Assistant")

        # TODO: Invoke LLM query API here

        if "conversation" in st.session_state:
            for message in st.session_state.get("chat_history", []):
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                elif message["role"] == "assistant":
                    st.markdown(f"**Chatbot:** {message['content']}")

            def handle_chat_input():
                if st.session_state.chat_input:
                    st.session_state.chat_history.append({"role": "user", "content": st.session_state.chat_input})
                    response = st.session_state.conversation.run(st.session_state.chat_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.session_state.chat_input = ""

            st.text_input("Ask a question to the chatbot:", key="chat_input", on_change=handle_chat_input)


if __name__ == "__main__":
    chat_interface()

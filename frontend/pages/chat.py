import base64
import io
import streamlit as st
from dotenv import load_dotenv
from frontend.utils.chat import fetch_file_from_s3
from frontend.utils.auth import make_authenticated_request
from markdown_pdf import MarkdownPdf, Section

def convert_to_pdf(markdown_content):
    try:
        pdf = MarkdownPdf(toc_level=2)

        # Combine all content into a single section
        all_content = "# Chat Conversation\n"

        if 'selected_document' in st.session_state:
            doc = st.session_state.selected_document
            all_content += f"**Document:** {doc['filename']}\n\n"

        for message in st.session_state.chat_history:
            role = message["role"].capitalize()
            content = message["content"]
            all_content += f"**{role}:** {content}\n\n"

        # Add all content as a single section
        pdf.add_section(Section(all_content, toc=False))

        pdf.meta["title"] = "Chat Conversation"
        pdf.meta["creator"] = "Research Question Answering Interface"

        pdf_output = io.BytesIO()
        pdf.save(pdf_output)
        pdf_output.seek(0)
        return pdf_output

    except Exception as e:
        st.error(f"Error converting to PDF: {str(e)}")
        return None

def convert_chat_to_markdown():
    markdown_content = "# Chat Conversation\n\n"
    if 'selected_document' in st.session_state:
        doc = st.session_state.selected_document
        markdown_content += f"**Document:** {doc['filename']}\n\n"
    for message in st.session_state.chat_history:
        role = message["role"].capitalize()
        content = message["content"]
        markdown_content += f"**{role}:** {content}\n\n"
    return markdown_content

def display_pdf(pdf_file):
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def qa_interface():
    st.title("Research Question Answering Interface")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if 'selected_document' in st.session_state and st.session_state.selected_document:
        doc = st.session_state.selected_document
        st.subheader(f"Analyzing: {doc['filename']}")

        with st.expander("Document Preview", expanded=False):
            try:
                pdf_path = fetch_file_from_s3(doc["sourcepdf_url"], None)
                with open(pdf_path, "rb") as f:
                    display_pdf(io.BytesIO(f.read()))
            except Exception as e:
                st.error(f"Error displaying PDF: {str(e)}")

        st.divider()

        chat_container = st.container()

        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ask your research question:"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("Analyzing..."):
                try:
                    response = make_authenticated_request(
                        f"/chat/{doc['a_id']}/qa",
                        "POST",
                        {"question": prompt, "model": ""}
                    )

                    with st.chat_message("assistant"):
                        st.markdown(response["response"])

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response["response"]
                    })
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")

        if st.session_state.chat_history:
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                markdown_content = convert_chat_to_markdown()
                st.download_button(
                    "Download as Markdown",
                    markdown_content,
                    "chat_conversation.md",
                    "text/markdown"
                )

            with col2:
                pdf_output = convert_to_pdf(markdown_content)
                if pdf_output:
                    st.download_button(
                        "Download as PDF",
                        pdf_output.getvalue(),
                        "chat_conversation.pdf",
                        "application/pdf"
                    )

    else:
        st.warning("Please select a document to begin your research.")

if __name__ == "__main__":
    qa_interface()
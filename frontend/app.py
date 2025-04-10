import streamlit as st
import requests

st.set_page_config(page_title="PDF QA Assistant", layout="wide")

BACKEND_URL = "http://localhost:8000"

st.title("📄 PDF QA Assistant")

if "file_id" not in st.session_state:
    st.session_state.file_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- PDF Upload ---
with st.sidebar:
    st.header("Upload your PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            response = requests.post(
                f"{BACKEND_URL}/upload/",
                files={"file": uploaded_file},
            )
            if response.status_code == 200:
                st.session_state.file_id = response.json()["file_id"]
                st.success("PDF uploaded and processed!")
            else:
                st.error("Failed to upload PDF")

# --- Ask Question ---
if st.session_state.file_id:
    st.subheader("Ask a question about your PDF")

    question = st.text_input("Your question")
    if st.button("Ask") and question.strip():
        with st.spinner("Thinking..."):
            response = requests.post(
                f"{BACKEND_URL}/ask/",
                data={
                    "file_id": st.session_state.file_id,
                    "question": question,
                },
            )
            if response.status_code == 200:
                answer = response.json()["answer"]
                st.session_state.chat_history.append((question, answer))
            else:
                st.error("Failed to get answer.")

# --- Chat Display ---
if st.session_state.chat_history:
    st.subheader("Chat History")
    for q, a in reversed(st.session_state.chat_history):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Assistant:** {a}")
        st.markdown("---")

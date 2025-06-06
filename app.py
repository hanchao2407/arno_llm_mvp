# legal_rag_repo/app.py

import streamlit as st
from rag import load_document_and_create_index, answer_query

st.set_page_config(page_title="Legal RAG Assistant", layout="wide")
st.title("📚 Legal Document Assistant")

if "db" not in st.session_state:
    st.session_state.db = None

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file:
    with st.spinner("Processing document..."):
        st.session_state.db = load_document_and_create_index(uploaded_file)
    st.success("Document processed and indexed.")

query = st.text_input("Ask a question about the uploaded document")

if st.session_state.db and query:
    with st.spinner("Retrieving answer..."):
        answer, sources = answer_query(st.session_state.db, query)
    st.markdown("### ✅ Answer")
    st.write(answer)
    st.markdown("---")
    st.markdown("### 📌 Sources")
    for src in sources:
        st.markdown(f"**{src.metadata['source']}**: {src.page_content[:300]}...")

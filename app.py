import streamlit as st
from rag import load_documents_and_create_index, answer_query

st.set_page_config(page_title="Legal RAG Assistant", layout="wide")
st.title("📚 Legal Document Assistant (Chat)")

# Initialize session state
if "db" not in st.session_state:
    st.session_state.db = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# File upload
uploaded_files = st.file_uploader(
    "Upload one or more PDF documents", type="pdf", accept_multiple_files=True
)

# Build the vector store
if uploaded_files:
    with st.spinner("Processing documents..."):
        st.session_state.db = load_documents_and_create_index(uploaded_files)
    st.success("Documents processed and indexed.")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input + Response
if prompt := st.chat_input("Ask a legal question..."):
    if st.session_state.db is None:
        st.warning("Please upload at least one document before chatting.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer, sources = answer_query(st.session_state.db, prompt)
                except Exception as e:
                    answer = f"⚠️ Error: {str(e)}"
                    sources = []

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.markdown(answer)

            if sources:
                with st.expander("📌 Sources"):
                    for src in sources:
                        source_label = f"**{src['metadata']['source']}**"
                        snippet = src['page_content'].replace(prompt, f"`{prompt}`")[:300]
                        st.markdown(f"{source_label}: {snippet}...")

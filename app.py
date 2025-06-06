import streamlit as st
from rag import load_documents_and_create_index, answer_query

st.set_page_config(
    page_title="Arnos Legal LLM Demo",
    layout="wide",
    page_icon="⚖️"
)

# Load custom CSS from external file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("⚖️ Arnos Legal LLM Demo")

tab1, tab2 = st.tabs(["Chat", "Settings"])

with tab2:
    st.header("Settings")
    uploaded_files = st.file_uploader(
        "Upload one or more PDF documents", type="pdf", accept_multiple_files=True
    )
    if uploaded_files:
        with st.spinner("Processing documents..."):
            st.session_state.db = load_documents_and_create_index(uploaded_files)
        st.success("Documents processed and indexed.")

with tab1:
    # Initialize session state
    if "db" not in st.session_state:
        st.session_state.db = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input + Response
    if prompt := st.chat_input("Ask a legal question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    from llm import call_llm
                    system_instruction = {
                        "role": "system",
                        "content": "You are a helpful legal assistant. Always answer in the same language as the user's question."
                    }
                    # Build messages list: system + chat history + new user prompt
                    messages = [system_instruction]
                    for msg in st.session_state.messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})

                    if st.session_state.db is not None:
                        # RAG: Add context as assistant message before user prompt
                        from rag import answer_query
                        answer, sources, context = answer_query(
                            st.session_state.db, prompt, return_context=True
                        )
                        # Insert context as an assistant message before the last user message
                        messages.insert(-1, {"role": "assistant", "content": f"Relevant context:\n{context}"})
                        answer = call_llm(messages)
                    else:
                        answer = call_llm(messages)
                        sources = []

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

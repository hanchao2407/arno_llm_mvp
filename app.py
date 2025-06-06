import streamlit as st
from rag import load_documents_and_create_index, answer_query

st.set_page_config(
    page_title="Arnos Legal LLM Demo",
    layout="wide",
    page_icon="⚖️"
)

# ChatGPT-like UI: soft background, rounded chat bubbles, minimal chrome
st.markdown("""
    <style>
    .stApp {
        background: #343541;
        color: #ececf1;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
        margin: auto;
    }
    /* Chat bubbles */
    .stChatMessage .stMarkdown {
        background: transparent;
        color: #ececf1;
        border-radius: 1.2em;
        padding: 0;
        margin-bottom: 0.2em;
        box-shadow: none;
        font-size: 1.08em;
        border: none;
    }
    .stChatMessage.user {
        display: flex;
        justify-content: flex-end;
    }
    .stChatMessage.user .stMarkdown {
        background: #2a2b32;
        color: #ececf1;
        text-align: right;
        max-width: 75%;
        border-radius: 1.2em;
        padding: 1.1em 1.4em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: none;
        display: inline-block;
        margin-left: 0;
        margin-right: 0;
    }
    .stChatMessage.assistant .stMarkdown {
        background: transparent;
        color: #ececf1;
        margin-right: 20%;
        border: none;
        padding: 0;
        box-shadow: none;
        float: none;
        width: 100%;
    }
    /* Chat input */
    .stChatInput {
        background: #40414f;
        color: #ececf1 !important;
        border-radius: 1.2em;
        border: 1px solid #565869;
        padding: 0.8em 1.2em;
        font-size: 1.08em;
        margin-bottom: 1.5em;
    }
    .stChatInput input {
        color: #ececf1 !important;
        background: #40414f !important;
    }
    /* Button */
    .stButton>button {
        background-color: #19c37d;
        color: #fff;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1.5em;
        font-size: 1.08em;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #127a4f;
        color: #fff;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1em;
        padding: 0.7em 2em;
        color: #ececf1 !important;
        background: #343541 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        transition: color 0.2s;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #444654 !important;
        color: #fff !important;
        background: #343541 !important;
    }
    </style>
""", unsafe_allow_html=True)

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

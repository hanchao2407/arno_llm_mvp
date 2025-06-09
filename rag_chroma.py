# rag_chroma.py

import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
from PyPDF2 import PdfReader
import torch

if hasattr(torch, "classes"):
    del torch.classes

st.set_page_config(page_title="Arnos Legal LLM", layout="wide")

from sentence_transformers import SentenceTransformer
import chromadb
from llm import call_llm

# Embedding model laden (gecached)
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embedding_model = get_embedding_model()

# Chroma REST Setup
# os.environ["CHROMA_API_IMPL"] = "rest"
# os.environ["CHROMA_SERVER_HOST"] = "arno-llm-mvp-1.onrender.com"
# os.environ["CHROMA_SERVER_HTTP_PORT"] = "443"
# os.environ["CHROMA_SERVER_SSL_ENABLED"] = "false"

# os.environ["CHROMA_API_IMPL"] = "rest"
# os.environ["CHROMA_SERVER_HOST"] = "arno-llm-mvp-1.onrender.com"  # ohne http
# os.environ["CHROMA_SERVER_HTTP_PORT"] = "443"
# os.environ["CHROMA_SERVER_SSL_ENABLED"] = "true"


# client = chromadb.HttpClient()

# client = chromadb.HttpClient(
#     host="https://arno-llm-mvp-1.onrender.com",
#     port=443,
#    ssl=True
# )


port = int(os.environ.get("PORT", 8000))  # Render setzt PORT automatisch

client = chromadb.HttpClient(
    host="arno-llm-mvp.onrender.com",
    port=443,
    ssl=True
)



try:
    collection = client.get_or_create_collection(name="legal_docs")
except Exception as e:
    if "already exists" in str(e):
        collection = client.get_collection(name="legal_docs")
    else:
        st.error(f"❌ ChromaDB-Fehler:\n\n{str(e)}")
        raise

def chunk_text(text, chunk_size=500, overlap=50):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

def load_documents_and_create_index(uploaded_files):
    for file in uploaded_files:
        reader = PdfReader(file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        chunks = chunk_text(text)
        embeddings = embedding_model.encode(chunks).tolist()
        metadatas = [{"source": f"{file.name}_chunk_{i}"} for i in range(len(chunks))]
        ids = [f"{file.name}_chunk_{i}" for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    return {"collection": collection}

def answer_query(db, query, top_k=5, return_context=False):
    sources = []
    context = ""

    if db and db.get("collection"):
        results = db["collection"].query(query_texts=[query], n_results=top_k)
        sources = [
            {"page_content": doc, "metadata": meta}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
        context = "\n".join(
            [f"[{s['metadata']['source']}] {s['page_content']}" for s in sources]
        )

    if return_context:
        return "", sources, context

    system_instruction = {
        "role": "system",
        "content": "You are a helpful legal assistant. Always answer in the same language as the user's question."
    }

    messages = [system_instruction]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    if context:
        messages.append({"role": "assistant", "content": f"Relevant context:\n{context}"})
    messages.append({"role": "user", "content": query})

    answer = call_llm(messages)
    return answer, sources


# --- UI: Sidebar für Upload & Indexierung ---
st.sidebar.title("⚙️ Einstellungen")
uploaded_files = st.sidebar.file_uploader("📚 Lade PDF-Dateien hoch", type="pdf", accept_multiple_files=True)
if uploaded_files and st.sidebar.button("🔍 Index erstellen"):
    with st.spinner("Verarbeite und indexiere PDFs..."):
        st.session_state.db = load_documents_and_create_index(uploaded_files)
    st.sidebar.success("✅ Dokumente erfolgreich indexiert!")

# --- Bereits indexierte PDFs anzeigen ---
existing_sources = collection.get(include=["metadatas"], limit=1000)["metadatas"]
indexed_files = set()

for meta in existing_sources:
    if "source" in meta:
        fname = meta["source"].split("_chunk_")[0]
        indexed_files.add(fname)

if indexed_files:
    st.sidebar.markdown("### 📂 Bereits indexierte PDFs:")
    for fname in sorted(indexed_files):
        st.sidebar.markdown(f"• `{fname}`")

# --- UI: Chatbereich ---
st.title("📄 Arnos Legal LLM Demo")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "db" not in st.session_state:
    st.session_state.db = {"collection": collection}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Stelle deine juristische Frage..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("💬 LLM denkt nach..."):
        answer, sources = answer_query(st.session_state.db, prompt)
        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        if sources:
            with st.expander("📚 Quellen anzeigen"):
                for s in sources:
                    st.markdown(f"**{s['metadata']['source']}**\n\n{s['page_content']}")

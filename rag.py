# rag.py

from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from llm import call_llm

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def load_documents_and_create_index(uploaded_files):
    all_chunks = []
    all_metadata = []
    for file in uploaded_files:
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        chunks = chunk_text(text)
        metadata = [{"source": f"{file.name}_chunk_{i}"} for i in range(len(chunks))]
        all_chunks.extend(chunks)
        all_metadata.extend(metadata)
    embeddings = embedding_model.encode(all_chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return {
        "index": index,
        "chunks": all_chunks,
        "embeddings": embeddings,
        "metadata": all_metadata
    }

def answer_query(db, query, top_k=5, return_context=False):
    query_vector = embedding_model.encode([query])[0]
    D, I = db["index"].search(np.array([query_vector]), top_k)
    sources = []
    for idx in I[0]:
        sources.append({
            "page_content": db["chunks"][idx],
            "metadata": db["metadata"][idx]
        })
    context = "\n".join([f"[{s['metadata']['source']}] {s['page_content']}" for s in sources])
    if return_context:
        return "", sources, context  # The actual LLM call is now in app.py
    system_instruction = {
        "role": "system",
        "content": "You are a helpful legal assistant. Always answer in the same language as the user's question."
    }
    # Build messages list: system + chat history
    messages = [system_instruction]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    if st.session_state.db is not None:
        from rag import answer_query
        _, sources, context = answer_query(st.session_state.db, prompt, return_context=True)
        # Add context as an assistant message before the user prompt
        messages.append({"role": "assistant", "content": f"Relevant context:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        answer = call_llm(messages)
    else:
        messages.append({"role": "user", "content": prompt})
        answer = call_llm(messages)
        sources = []
    
    return answer, sources

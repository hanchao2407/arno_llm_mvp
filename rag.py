# rag.py

from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import tempfile

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def load_document_and_create_index(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = "".join([page.extract_text() for page in reader.pages])
    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return {
        "index": index,
        "chunks": chunks,
        "embeddings": embeddings
    }

def answer_query(db, query, top_k=5):
    query_vector = embedding_model.encode([query])[0]
    D, I = db["index"].search(np.array([query_vector]), top_k)
    sources = []
    for idx in I[0]:
        sources.append({
            "page_content": db["chunks"][idx],
            "metadata": {"source": f"chunk_{idx}"}
        })
    context = "\n".join([f"[{s['metadata']['source']}] {s['page_content']}" for s in sources])
    # Placeholder for LLM call (OpenAI, Ollama, etc.)
    answer = f"Simulated answer based on:\n\n{context[:1000]}"
    return answer, sources

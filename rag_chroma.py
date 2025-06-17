# rag_chroma.py

import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"

import streamlit as st
from PyPDF2 import PdfReader
import torch
import time # Added for sleep

if hasattr(torch, "classes"):
    del torch.classes

st.set_page_config(page_title="Arnos Legal LLM", layout="wide")

# --- Streamlit Session State Initialization (Moved to top) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "db" not in st.session_state:
    st.session_state.db = None # Initialize as None, will be set with collection below
# --- End Streamlit Session State Initialization ---


from sentence_transformers import SentenceTransformer
import chromadb
from llm import call_llm

# Embedding model laden (gecached)
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embedding_model = get_embedding_model()

# Chroma REST Setup - client initialization
client = chromadb.HttpClient(
    host="https://arno-llm-mvp.onrender.com",
    port=443,
    ssl=True
)

# Initialize collection variable at global scope.
# This will be updated by calls below and within the Streamlit UI logic.
collection = None

try:
    # Attempt to get or create the collection on initial script run
    collection = client.get_or_create_collection(name="legal_docs")
except Exception as e:
    # Handle cases where collection might not be immediately available
    if "already exists" in str(e):
        collection = client.get_collection(name="legal_docs")
    else:
        st.error(f"❌ ChromaDB-Fehler beim Initialisieren der Collection:\n\n{str(e)}")
        # Consider gracefully handling or re-raising based on severity
        raise

# Ensure st.session_state.db always holds the current collection object
# This runs after global 'collection' is determined
if st.session_state.db is None or st.session_state.db.get("collection") is None:
    st.session_state.db = {"collection": collection}
else:
    # If db already exists, ensure its collection is up-to-date
    # This handles Streamlit's script reruns
    collection = st.session_state.db["collection"]


def chunk_text(text, chunk_size=500, overlap=50):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

def load_documents_and_create_index(uploaded_files):
    current_collection = st.session_state.db["collection"] # Use the collection from session state
    for file in uploaded_files:
        reader = PdfReader(file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        chunks = chunk_text(text)
        embeddings = embedding_model.encode(chunks).tolist()
        metadatas = [{"source": f"{file.name}_chunk_{i}"} for i in range(len(chunks))]
        ids = [f"{file.name}_chunk_{i}" for i in range(len(chunks))]

        current_collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    return {"collection": current_collection}


def answer_query(db, query, top_k=5, relevance_threshold=0.5, return_context=False): # Added relevance_threshold parameter
    sources = []
    context = ""

    # Ensure db and collection exist before querying
    if db and db.get("collection"):
        current_collection = db["collection"]
        try:
            # Get documents, their metadatas, AND their distances
            results = current_collection.query(query_texts=[query], n_results=top_k, include=['documents', 'metadatas', 'distances'])
            
            # --- ADD THIS DEBUG LINE ---
            # st.sidebar.write("--- Query Debug Info ---")
            # st.sidebar.write(f"Query: {query}")
            # st.sidebar.write(f"Raw Query Results (including distances): {results}")
            # st.sidebar.write(f"Current relevance_threshold: {relevance_threshold}")
            #st.sidebar.write("--- End Query Debug Info ---")
            # --- END DEBUG LINE ---

            relevant_results = []
            if results and results.get("distances") and results.get("documents") and results.get("metadatas"):
                for i in range(len(results["distances"][0])):
                    distance = results["distances"][0][i]
                    # Only include results if their distance is below the threshold
                    # (lower distance = more relevant)
                    if distance < relevance_threshold:
                        relevant_results.append({
                            "page_content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "distance": distance # Include distance for debugging/tuning
                        })
            
            # Sort relevant results by distance (most relevant first)
            relevant_results.sort(key=lambda x: x['distance'])
            
            sources = relevant_results
            context = "\n".join(
                [f"[{s['metadata']['source']}] {s['page_content']}" for s in sources]
            )

        except Exception as e:
            st.error(f"❌ ChromaDB-Fehler beim Abfragen der Dokumente: {str(e)}")
            context = ""
            sources = []

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
        messages.append({"role": "assistant", "content": f"Relevant context:\n{context}"}) # Corrected string literal
    messages.append({"role": "user", "content": query})

    answer = call_llm(messages)
    return answer, sources


# --- UI: Sidebar für Upload & Indexierung ---
st.sidebar.title("⚙️ Einstellungen")
uploaded_files = st.sidebar.file_uploader("📚 Lade PDF-Dateien hoch", type="pdf", accept_multiple_files=True)
if uploaded_files and st.sidebar.button("🔍 Index erstellen"):
    with st.spinner("Verarbeite und indexiere PDFs..."):
        # load_documents_and_create_index returns the updated collection.
        # Assign it back to session state and the global 'collection' variable.
        st.session_state.db = load_documents_and_create_index(uploaded_files)
        collection = st.session_state.db["collection"] # Update global 'collection' after indexing
    st.sidebar.success("✅ Dokumente erfolgreich indexiert!")

# --- Clear Index Button ---
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Index löschen (Alle Dokumente entfernen)"):
    try:
        client.delete_collection(name="legal_docs")
        time.sleep(5) # Wait for 5 seconds to allow the server to stabilize

        # Re-create the collection immediately after deletion.
        # Update both session state and the global 'collection' variable.
        new_collection = client.get_or_create_collection(name="legal_docs")
        st.session_state.db = {"collection": new_collection}
        collection = new_collection # Update global 'collection' after deletion
        
        st.sidebar.success("✅ Index erfolgreich geleert!")
        st.session_state.messages = [] # Clear chat history as context is gone
    except Exception as e:
        st.sidebar.error(f"❌ Fehler beim Leeren des Index: {str(e)}")


# --- Bereits indexierte PDFs anzeigen ---
# This block now uses the globally updated 'collection' variable,
# and has a try-except for robustness.
existing_sources = []
if collection is not None: # Ensure collection object exists
    try:
        # First, get all IDs
        all_ids_in_collection = collection.get(include=[])['ids'] # Get only IDs, no other data
        
        # If IDs are found, then get their metadatas
        if all_ids_in_collection:
            # Get metadatas for all retrieved IDs
            # Note: if there are more than 1000 IDs, this will require pagination in real apps
            existing_sources_retrieved = collection.get(ids=all_ids_in_collection, include=["metadatas"])["metadatas"]
            
            # Assign to existing_sources, handling potential None if no metadatas returned
            existing_sources = existing_sources_retrieved if existing_sources_retrieved is not None else []
        else:
            existing_sources = [] # No IDs, so no sources

    except Exception as e:
        # Catch the StopIteration or any other error from the get call
        st.sidebar.warning(f"⚠️ Konnte indexierte PDFs nicht laden. Datenbankfehler: {str(e)}")
        existing_sources = [] # Ensure it's an empty list to avoid further errors

# The existing debug output you have provided previously:
# st.sidebar.write("--- Debug Info ---")
# st.sidebar.write(f"Raw existing_sources: {existing_sources}")
# --- ADDED A CHECK HERE FOR SAFETY FOR `indexed_files` ---
indexed_files = set()
for meta in existing_sources:
    if "source" in meta:
        fname = meta["source"].split("_chunk_")[0]
        indexed_files.add(fname)
# st.sidebar.write(f"Processed indexed_files: {indexed_files}")
# st.sidebar.write("--- End Debug Info ---")


if indexed_files:
    st.sidebar.markdown("### 📂 Bereits indexierte PDFs:")
    for fname in sorted(indexed_files):
        st.sidebar.markdown(f"• `{fname}`")


# --- UI: Chatbereich ---
st.title("📄 Arnos Legal LLM Demo")

# st.session_state initialization for messages and db is handled globally now (moved earlier)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Stelle deine juristische Frage..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("💬 LLM denkt nach..."):
        try:
            # The answer_query function already uses st.session_state.db
            answer, sources = answer_query(st.session_state.db, prompt, top_k=5, relevance_threshold=1.2)
            st.chat_message("assistant").markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

            if sources:
                with st.expander("📚 Quellen anzeigen"):
                    for s in sources:
                        st.markdown(f"**{s['metadata']['source']} (Distance: {s['distance']:.2f})**\n\n{s['page_content']}")
        except Exception as e:
            st.chat_message("assistant").error(f"⚠️ Fehler bei der Antwortgenerierung: {str(e)}")
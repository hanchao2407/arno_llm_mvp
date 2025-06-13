# init_collection.py

import os
import chromadb

print("📁 Working dir:", os.path.abspath("chroma_db"))

# Change the host back to localhost for running directly on the Render service
client = chromadb.HttpClient(host="localhost", port=8000)

col = client.get_or_create_collection(name="legal_docs")
col.add(documents=["Test-Dokument"], ids=["doc1"]) # Add a test document to initialize
print("✅ Collection erstellt:", col)
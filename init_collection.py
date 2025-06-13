# init_collection.py

import os
import chromadb

print("📁 Working dir:", os.path.abspath("chroma_db"))

# Change the host to the public URL of your ChromaDB service
client = chromadb.HttpClient(host="arno-llm-mvp.onrender.com", port=8000)

col = client.get_or_create_collection(name="legal_docs")
col.add(documents=["Test-Dokument"], ids=["doc1"])
print("✅ Collection erstellt:", col)
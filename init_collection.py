# init_collection.py

import os
import chromadb

print("📁 Working dir:", os.path.abspath("chroma_db"))

# Connect to the public URL using HTTPS (port 443) with SSL enabled
client = chromadb.HttpClient(host="arno-llm-mvp.onrender.com", port=443, ssl=True)

col = client.get_or_create_collection(name="legal_docs")
col.add(documents=["Test-Dokument"], ids=["doc1"])
print("✅ Collection erstellt:", col)
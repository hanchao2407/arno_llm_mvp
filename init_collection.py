# init_collection.py
import os
import chromadb

print("📁 Working dir:", os.path.abspath("chroma_db"))
client = chromadb.HttpClient(host="chroma-db", port=8000) # Ensure this change is pushed
col = client.get_or_create_collection(name="legal_docs")
col.add(documents=["Test-Dokument"], ids=["doc1"])
print("✅ Collection erstellt:", col)
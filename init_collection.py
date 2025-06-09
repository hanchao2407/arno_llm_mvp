import os
import chromadb

print("📁 Working dir:", os.path.abspath("chroma_db"))

client = chromadb.HttpClient(host="localhost", port=8000)
col = client.get_or_create_collection(name="legal_docs")
col.add(documents=["Test-Dokument"], ids=["doc1"])
print("✅ Collection erstellt:", col)

import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)
client.create_collection(name="legal_docs")
print("✅ Collection 'legal_docs' wurde erstellt.")

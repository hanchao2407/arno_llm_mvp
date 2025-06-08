import os
import chromadb

# Set the connection config via environment variables
os.environ["CHROMA_API_IMPL"] = "rest"
os.environ["CHROMA_SERVER_HOST"] = "localhost"
os.environ["CHROMA_SERVER_HTTP_PORT"] = "8000"
os.environ["CHROMA_SERVER_SSL_ENABLED"] = "false"

client = chromadb.HttpClient()

print("✅ Successfully connected to ChromaDB")
print(client.heartbeat())

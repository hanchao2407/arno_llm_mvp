FROM ghcr.io/chroma-core/chroma:1.0.12
CMD ["sh", "-c", "uvicorn chromadb.app:app --host 0.0.0.0 --port ${PORT}"]

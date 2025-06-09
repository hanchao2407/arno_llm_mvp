# Verwende das offizielle Chroma-Image als Basis
FROM ghcr.io/chroma-core/chroma:0.4.13

# Notwendige ENV-Variablen setzen
ENV CHROMA_API_IMPL=chromadb.api.fastapi.FastAPI
ENV CHROMA_SERVER_HOST=0.0.0.0
ENV IS_PERSISTENT=true

# Kopiere vorbereitete Vector-Datenbank (falls vorhanden)
COPY chroma_db /data

# Starte den FastAPI-Server
CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]

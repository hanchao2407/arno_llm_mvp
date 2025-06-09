# Verwende das offizielle Chroma-Image als Basis
FROM ghcr.io/chroma-core/chroma:0.4.13

# Aktiviere HTTP REST API-Modus
ENV CHROMA_API_IMPL=chromadb.api.fastapi.FastAPI
ENV IS_PERSISTENT=true

# Kopiere deine vorbereitete Vector-Datenbank (falls vorhanden)
COPY chroma_db /data

# Starte den FastAPI-Server
CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]

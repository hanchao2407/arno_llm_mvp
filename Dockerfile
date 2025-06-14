# Verwende das offizielle Chroma-Image als Basis
FROM ghcr.io/chroma-core/chroma:0.4.13

# Installiere benötigte Debugging-Tools
# 'apt-get update' aktualisiert die Paketliste
# 'apt-get install -y' installiert Pakete ohne interaktive Bestätigung
# 'iproute2' enthält 'ss'
# 'net-tools' enthält 'netstat'
# 'curl' ist ein separates Paket
RUN apt-get update && \
    apt-get install -y iproute2 net-tools curl && \
    rm -rf /var/lib/apt/lists/* # Bereinigung, um Image-Größe zu reduzieren

# Notwendige ENV-Variablen für FastAPI-Server
ENV CHROMA_API_IMPL=chromadb.api.fastapi.FastAPI
ENV CHROMA_SERVER_HOST=0.0.0.0
ENV CHROMA_SERVER_HTTP_PORT=8000
ENV IS_PERSISTENT=true

# Kopiere vorbereitete Vector-Datenbank (optional)
COPY chroma_db /data

# Starte den FastAPI-Server
CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]
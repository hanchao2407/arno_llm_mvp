FROM ghcr.io/chroma-core/chroma:0.4.13

# Deaktiviere Multi-Tenant und aktiviere Persistenz
ENV CHROMA_MULTI_TENANT=false
ENV IS_PERSISTENT=true

# Kopiere deine vorbereitete Datenbank mit legal_docs rein
COPY chroma_db /data

# Starte Chroma manuell (nicht "run", sondern uvicorn!)
CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]

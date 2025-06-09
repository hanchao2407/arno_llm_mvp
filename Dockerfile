FROM ghcr.io/chroma-core/chroma:0.4.13

ENV CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.none.NoAuthServerProvider
ENV IS_PERSISTENT=true

COPY chroma_db /data

CMD ["uvicorn", "chromadb.app:app", "--host", "0.0.0.0", "--port", "8000"]

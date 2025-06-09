FROM ghcr.io/chroma-core/chroma:1.0.12

ENV CHROMA_MULTI_TENANT=false

ENV CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.basic.BasicAuthServerProvider
ENV IS_PERSISTENT=TRUE

COPY chroma_db /data

CMD ["run", "--host", "0.0.0.0", "--port", "8000", "--path", "/data"]


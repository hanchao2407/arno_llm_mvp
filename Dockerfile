FROM ghcr.io/chroma-core/chroma:1.0.12

ENV CHROMA_MULTI_TENANT=false

CMD ["run", "--host", "0.0.0.0", "--port", "8000", "--path", "/data"]

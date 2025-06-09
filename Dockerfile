FROM ghcr.io/chroma-core/chroma:0.4.13

ENV CHROMA_MULTI_TENANT=false
ENV IS_PERSISTENT=TRUE

COPY chroma_db /data

CMD ["run", "--host", "0.0.0.0", "--port", "8000", "--path", "/data"]

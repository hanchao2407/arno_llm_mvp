FROM ghcr.io/chroma-core/chroma:1.0.12

CMD ["run", "--host", "0.0.0.0", "--port", "8000", "--path", "/data"]

# Use the official ChromaDB image as a base.
# We are using 0.4.14 as seen in your docker-compose.yml.
FROM ghcr.io/chroma-core/chroma:0.4.14

# The core problem is that some modules within ChromaDB (like onnxruntime)
# are compiled against an older NumPy (1.x), but a newer NumPy (2.x) gets installed
# by default, causing crashes. This line forces NumPy to a compatible version (<2.0).
# The --force-reinstall ensures it replaces any problematic existing version.
RUN pip install "numpy<2" --force-reinstall

# The base ChromaDB image typically already handles exposing port 8000
# and starting the ChromaDB server. You generally don't need to add EXPOSE or CMD
# unless you want to customize the server's startup behavior.

# If you have any additional requirements for your ChromaDB service beyond what's
# in the base image, you would add lines like these:
# COPY requirements_chroma.txt /app/requirements_chroma.txt
# RUN pip install -r /app/requirements_chroma.txt
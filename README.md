⚖️ Arno Legal LLM MVP
Arno Legal LLM MVP (Minimum Viable Product) is a cutting-edge Retrieval Augmented Generation (RAG) chat application designed to provide quick and accurate answers to legal questions by leveraging your own PDF documents. This Streamlit-powered demo showcases a robust RAG pipeline for enhanced legal information retrieval and conversational AI.

✨ Features
PDF Document Ingestion: Easily upload legal PDF documents for indexing.
Semantic Search (RAG): Utilizes ChromaDB as a powerful open-source vector database for storing and retrieving document embeddings.
LLM Integration: Seamlessly integrates with large language models (LLMs) via the Together AI API to generate comprehensive and context-aware answers.
Contextual Q&amp;A: Answers user queries by augmenting the LLM's knowledge with information extracted directly from your private document collection.
Source Citation: Displays relevant document chunks as sources, allowing users to verify the origin of the information.
Responsive Chat Interface: A user-friendly chat interface built with Streamlit and custom CSS for an intuitive experience.
🔒 Locally Deployable for Sensitive Use Cases
A key advantage of the Arno Legal LLM MVP is its full local deployability. For sensitive use cases where data privacy, security, or compliance are paramount, the entire application stack, including the ChromaDB vector database and the Streamlit front-end, can be deployed and run entirely within your local or private infrastructure. This ensures your confidential legal documents remain within your control and never leave your trusted environment.

🚀 Technologies Used
Streamlit: For building the interactive web application.
ChromaDB: As the powerful open-source vector database for storing and retrieving document embeddings.
Sentence Transformers: For generating high-quality embeddings from text chunks.
PyPDF2: For extracting text content from PDF documents.
Together AI: For integrating with state-of-the-art Large Language Models.
Python: The core programming language.
Docker: For containerization of the ChromaDB service.
Render.com: For cloud deployment of both Streamlit and ChromaDB services (for demonstration/less sensitive use cases).

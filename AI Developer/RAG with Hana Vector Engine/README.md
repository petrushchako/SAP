# Retrieval-Augmented Generation (RAG) with Hana Vector Engine

### Description
This module is designed to familiarize you with Retrieval-Augmented Generation (RAG) and the capabilities of the SAP HANA Vector Engine. 
By integrating these technologies, you can elevate your AI-driven solutions by combining large-scale language models with the rich data context available in SAP.

With SAP's HANA Vector Engine, you can perform vector-based similarity search and embedding-based retrieval to support more relevant, context-aware responses. 
The combination of RAG and SAP HANA enables you to retrieve relevant information from business data, which a language model then augments to generate accurate, context-specific outputs.

Using these powerful tools, you can interact with the HANA Vector Engine to create embeddings for business data, perform semantic search on large datasets, and enhance applications by integrating real-time, data-driven responses from your business context.

<br>

## Retrieval-Augmented Generation (RAG)
This section focuses on **Retrieval-Augmented Generation (RAG)**, a powerful technique for combining the strengths of retrieval and generation. RAG uses a combination of information retrieval and language models to generate responses based on retrieved content from external knowledge sources.


### Why is RAG important?
RAG provides a solution for answering complex queries by:
1. Retrieving relevant information from large collections of unstructured data.
2. Generating a coherent and context-aware reponse based on retrieval content.

**Use cases include:**
- Question answering systems
- Document sumarization
- Chatbot that need up-to-date or specific external knowledge

<br>

### RAG with HANA Vector Engine

![](img/rag-architecture.png)

<br>

This code performs the document split (loaded using PyPDF Loader available with Langchain) in chunks of size 200 & chunk overlap 25. If you wish to use a text file, you can use TextLoader added as import below (for other file types supported, refer - https://python.langchain.com/docs/modules/data_connection/document_loaders/) split of the text is done and embedding model is initiated using text-embedding-3-large

![](img/rag-splitting.png)













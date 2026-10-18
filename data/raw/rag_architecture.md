# Retrieval-Augmented Generation Architecture

Retrieval-Augmented Generation (RAG) combines information retrieval with a language model. Instead of relying only on information learned during training, an application retrieves relevant passages from an external knowledge source and supplies them as context for answer generation.

A typical RAG pipeline has an ingestion stage and a query stage. During ingestion, documents are loaded, split into chunks, and optionally converted into embeddings for vector search. During a query, the application retrieves relevant chunks and passes them to a language model.

Retrieval quality affects answer quality. If the retrieved passages do not contain the information needed to answer a question, the language model may produce an incomplete or unsupported answer. Applications should evaluate retrieval separately from answer generation.

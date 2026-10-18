# Retrieval Evaluation

- Questions evaluated: 8
- Ranking cutoff (k): 3
- Hit Rate@3: 1.000
- Recall@3: 0.938
- MRR: 0.812

## Per-question results

| Question | Hit | Recall | Reciprocal rank |
|---|---:|---:|---:|
| What platform can host a containerized AI application? | True | 1.000 | 0.500 |
| What responsibilities do developers retain when deploying on Cloud Run? | True | 1.000 | 0.500 |
| How does RAG provide external knowledge to a language model? | True | 0.500 | 1.000 |
| What responsibilities does an application calling a model endpoint have? | True | 1.000 | 1.000 |
| What are the ingestion and query stages in a RAG pipeline? | True | 1.000 | 1.000 |
| Why can irrelevant retrieved passages lead to unsupported answers? | True | 1.000 | 0.500 |
| What do Hit Rate at k, Recall at k, and MRR measure? | True | 1.000 | 1.000 |
| Why is a perfect retrieval score on a tiny dataset insufficient evidence of general performance? | True | 1.000 | 1.000 |

## Retrieved passages

### What platform can host a containerized AI application?

- Expected: cloud_run_deployment.md::chunk-0
- Retrieved: gemini_argon_notes.md::chunk-1, cloud_run_deployment.md::chunk-0, gemini_argon_notes.md::chunk-0

### What responsibilities do developers retain when deploying on Cloud Run?

- Expected: cloud_run_deployment.md::chunk-1
- Retrieved: cloud_run_deployment.md::chunk-0, cloud_run_deployment.md::chunk-1, rag_architecture.md::chunk-2

### How does RAG provide external knowledge to a language model?

- Expected: gemini_argon_notes.md::chunk-1, rag_architecture.md::chunk-0
- Retrieved: rag_architecture.md::chunk-0, rag_architecture.md::chunk-1, gemini_argon_notes.md::chunk-0

### What responsibilities does an application calling a model endpoint have?

- Expected: gemini_argon_notes.md::chunk-0
- Retrieved: gemini_argon_notes.md::chunk-0, gemini_argon_notes.md::chunk-1, cloud_run_deployment.md::chunk-0

### What are the ingestion and query stages in a RAG pipeline?

- Expected: rag_architecture.md::chunk-1
- Retrieved: rag_architecture.md::chunk-1, retrieval_evaluation.md::chunk-0, rag_architecture.md::chunk-0

### Why can irrelevant retrieved passages lead to unsupported answers?

- Expected: rag_architecture.md::chunk-2
- Retrieved: gemini_argon_notes.md::chunk-1, rag_architecture.md::chunk-2, cloud_run_deployment.md::chunk-0

### What do Hit Rate at k, Recall at k, and MRR measure?

- Expected: retrieval_evaluation.md::chunk-1
- Retrieved: retrieval_evaluation.md::chunk-1, rag_architecture.md::chunk-2

### Why is a perfect retrieval score on a tiny dataset insufficient evidence of general performance?

- Expected: retrieval_evaluation.md::chunk-2
- Retrieved: retrieval_evaluation.md::chunk-2, rag_architecture.md::chunk-0, retrieval_evaluation.md::chunk-0

# Retrieval Comparison

Questions evaluated: **16**

Metrics are calculated from manually labeled relevant chunk IDs.

| Method | k | Hit Rate@k | Mean Recall@k | MRR@k |
|---|---:|---:|---:|---:|
| BM25L | 1 | 0.812 | 0.781 | 0.812 |
| BM25L | 3 | 1.000 | 0.969 | 0.906 |
| BM25L | 5 | 1.000 | 1.000 | 0.906 |
| Embeddings | 1 | 0.875 | 0.844 | 0.875 |
| Embeddings | 3 | 1.000 | 0.969 | 0.938 |
| Embeddings | 5 | 1.000 | 1.000 | 0.938 |
| Hybrid RRF | 1 | 1.000 | 0.969 | 1.000 |
| Hybrid RRF | 3 | 1.000 | 0.969 | 1.000 |
| Hybrid RRF | 5 | 1.000 | 1.000 | 1.000 |

## Interpretation

Hybrid RRF ranked relevant evidence well on this small benchmark. These results do not establish that it will outperform other methods on unseen questions.

# Evaluating Information Retrieval

Retrieval evaluation measures whether a search system returns relevant documents for a query. A benchmark contains questions and labels identifying which document chunks are relevant to each question.

Hit Rate at k measures the fraction of questions for which at least one relevant chunk appears in the top k results. Recall at k measures the fraction of all labeled relevant chunks that appear in the top k results. Mean Reciprocal Rank (MRR) averages the reciprocal of the rank of the first relevant result across questions.

Evaluation metrics depend on accurate relevance labels and a sufficiently varied dataset. A perfect score on a tiny dataset does not establish that a retrieval system will perform well on unseen questions. A useful experiment should include multiple documents, varied questions, and cases where relevant content is not the first result.

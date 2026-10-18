# Abstention Evaluation

- Similarity threshold: **0.20**
- Out-of-scope questions: **4**
- Correct abstentions: **3**
- False acceptances: **1**
- Out-of-scope rejection rate: **75.0%**

## Per-question results

| Category | Question | Top similarity | Prediction | Top source | Chunk |
|---|---|---:|---|---|---|
| out_of_scope | How do I bake a chocolate cake? | 0.1022 | ABSTAIN | model_integration_notes.md | model_integration_notes.md::chunk-0 |
| out_of_scope | What was the final score of the 2026 World Series? | 0.1620 | ABSTAIN | retrieval_evaluation.md | retrieval_evaluation.md::chunk-2 |
| out_of_scope | What is the current price of BigQuery on Google Cloud? | 0.3813 | ACCEPT | cloud_run_deployment.md | cloud_run_deployment.md::chunk-0 |
| out_of_scope | What is the weather forecast for tomorrow? | 0.1011 | ABSTAIN | model_integration_notes.md | model_integration_notes.md::chunk-0 |
| borderline | How much will it cost to deploy this application on Cloud Run? | 0.5960 | ACCEPT | cloud_run_deployment.md | cloud_run_deployment.md::chunk-0 |
| borderline | Which exact IAM roles should I assign to deploy this application securely? | 0.5415 | ACCEPT | cloud_run_deployment.md | cloud_run_deployment.md::chunk-2 |

## Interpretation

The BigQuery pricing question may score highly because it is semantically related to Google Cloud content. Acceptance means only that its similarity score passed the threshold; it does not prove the documents contain current pricing information.

This is a small, manually selected probe set, not a production reliability estimate. Similarity is not calibrated confidence.

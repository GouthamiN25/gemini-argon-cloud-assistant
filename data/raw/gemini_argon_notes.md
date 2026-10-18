
# Gemini 4 Argon and Google Cloud

## Model integration

A cloud AI application separates the model from the application
that calls it. The application sends a request to a model endpoint
and processes the response.

## Document-grounded question answering

A retrieval system searches a document collection for relevant
passages. Those passages can be provided as context to a language
model so the answer can be grounded in the available documents.

## Application deployment

Cloud Run can host a web application or API that calls a model
service. The application still needs authentication, error handling,
logging, and appropriate access controls.

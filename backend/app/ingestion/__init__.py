"""
DocuMind AI — app/ingestion package

This package will house the backend-side ingestion API layer.

Planned Phase 3 contents:
- router.py: POST /api/internal/ingest — the endpoint n8n calls to trigger
  document processing after detecting a new/updated file in Google Drive.
- tasks.py: async ingestion task runner (process, chunk, embed, upsert).

The standalone ingestion/ package at the repository root contains the
document processing pipeline (parser, cleaner, chunker, metadata, embeddings).
This package (backend/app/ingestion/) is the API boundary between n8n and
that pipeline — it receives the file, calls the pipeline, and updates
PostgreSQL document status.

Do not add Phase 3 implementation here until Phase 2 (authentication and
database) is complete.
"""

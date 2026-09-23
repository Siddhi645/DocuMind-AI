"""
DocuMind AI — services package

This package will house cross-cutting service classes used by the backend.

Planned Phase 2/3 contents:
- PineconeService: direct Pinecone index operations (upsert, delete, query)
- DriveService: Google Drive file access (Phase 3)
- NotificationService: admin alerts (future)

These are kept separate from the RAG pipeline modules so they can be
injected independently and tested in isolation.
"""

# n8n Workflows — DocuMind AI

## Status: Phase 1 Placeholder

n8n is the **automation/orchestration layer** for DocuMind AI.
It is NOT the AI system. It is NOT the main backend.
Core application logic lives in the FastAPI backend.

## Planned Workflows (Phase 3+)

### Workflow 1: Google Drive → Ingest New Document
```
Trigger: Google Drive — new file detected
    ↓
Download file
    ↓
HTTP POST → FastAPI /api/internal/ingest
    ↓
Python document processing
    ↓
Chunking + metadata
    ↓
Embeddings
    ↓
Pinecone upsert
    ↓
Update PostgreSQL document status
```

### Workflow 2: Google Drive → Handle Updated Document
```
Trigger: Google Drive — file modified
    ↓
Identify document_id (from drive_file_id)
    ↓
HTTP POST → FastAPI /api/internal/ingest (with replace=true)
    ↓
Delete old Pinecone vectors for document_id
    ↓
Process updated file
    ↓
Upsert new vectors
```

### Workflow 3: Google Drive → Handle Deleted Document
```
Trigger: Google Drive — file deleted
    ↓
Identify document_id
    ↓
HTTP POST → FastAPI /api/internal/delete-document
    ↓
Delete Pinecone vectors
    ↓
Update PostgreSQL document status → archived
```

## Setup (Future Phase)

1. Deploy n8n (self-hosted or n8n Cloud).
2. Connect Google Drive credentials.
3. Import the JSON workflow files from this directory.
4. Set the FastAPI webhook URL and n8n API key in `.env`.
5. Enable workflows.

## Workflow Files

Workflow JSON files will be added here in Phase 3.

## Reference

- n8n Google Drive trigger: https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.googledrivetrigger/
- Pinecone templates: https://github.com/pinecone-io/n8n-templates

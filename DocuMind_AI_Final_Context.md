# DocuMind AI — Project Context

## 1. Project Identity

**Product Name:** DocuMind AI

**Formal Project Title:** Enterprise AI Knowledge Assistant using Retrieval-Augmented Generation (RAG) for Intelligent Document Retrieval and Question Answering

**Alternative title:** DocuMind AI: An Intelligent Institutional Document Assistant using Retrieval-Augmented Generation

**Project Type:** Final-Year CSE Major Project  
**Academic Year:** 2026–27

**Guide:** Dr. Anil Surve  
**Designation:** Head of Department, Computer Science and Engineering

### Current Development Model

**Solo Developer:** Siddhi Varma is the sole developer responsible for the complete implementation of DocuMind AI.

This means one developer is responsible for:
- Frontend
- Backend
- RAG/AI pipeline
- Document processing
- Google Drive integration
- n8n automation
- PostgreSQL/database
- Authentication and authorization
- Testing
- Docker/deployment
- Documentation

The original academic synopsis may contain multiple student names, but **current implementation planning must be treated as a solo-development project**. Do not divide work into Member 1 / Member 2 / Member 3 roles.

Customer/institution details remain **To Be Confirmed with the guide/college**. Never invent customer details, institutional requirements, or documents.




# 1. Project Overview

DocuMind AI is an AI-powered institutional knowledge assistant for college documents.

The college maintains many documents in Google Drive and other institutional repositories. Faculty, staff, administrators, and accreditation teams may need to locate specific information or supporting evidence quickly.

The primary real-world use case is **NAAC/NBA accreditation**.

Example question:

> What evidence is available for student mentoring activities?

Instead of manually opening multiple folders and documents, the user asks a natural-language question. DocuMind AI retrieves relevant document content and generates a context-aware answer along with source documents/pages.

The system is not limited to NAAC/NBA. It can also support:
- Academic regulations
- College policies
- Notices
- Department documents
- Reports
- Guidelines
- Faculty-related documents
- Student-related institutional information
- Accreditation evidence
- Other authorized institutional knowledge

---

# 2. Problem Statement

College information is distributed across a large collection of documents stored in Google Drive and other institutional repositories. During NAAC and NBA accreditation activities, faculty and committee members may need to quickly find specific information or supporting evidence, but manually searching through multiple documents is time-consuming and inefficient.

Therefore, there is a need for an intelligent document assistant that can understand natural-language queries, retrieve relevant information from authorized institutional documents, and generate context-aware answers using Retrieval-Augmented Generation.

---

# 3. Core Solution

The system combines:
- Google Drive
- n8n workflow automation
- Python/FastAPI
- Document processing
- Text extraction
- Intelligent chunking
- Embedding models
- Pinecone vector database
- Retrieval-Augmented Generation (RAG)
- Large Language Model (LLM)
- React frontend
- PostgreSQL or another application database
- Authentication and role-based access control

**Important architecture rule:** n8n is the automation/orchestration layer. It is NOT the AI system and should NOT be used as the entire application.

Core application logic, APIs, document processing, RAG, security, and application functionality should be implemented in code.

---

# 4. Target Users

Potential users:
- Faculty
- Department staff
- Administrative staff
- Accreditation committee members
- NAAC/NBA teams
- Authorized students
- System administrators

Exact roles and permissions should be finalized with the guide/college.

---

# 5. Primary Use Case: NAAC/NBA Evidence Retrieval

Example:

User asks:
> What evidence is available for student mentoring activities?

System:
1. Understands the natural-language question.
2. Converts the query into an embedding.
3. Applies user permissions and metadata filters.
4. Searches Pinecone for semantically relevant chunks.
5. Retrieves the most relevant evidence.
6. Optionally reranks results.
7. Builds context for the LLM.
8. Generates an answer grounded in retrieved documents.
9. Returns source documents and page/section information.

Example response:

```json
{
  "answer": "The institution conducts student mentoring activities...",
  "sources": [
    {
      "document_name": "Student_Mentoring_Report_2025-26.pdf",
      "page": 4
    },
    {
      "document_name": "Faculty_Mentor_Record.pdf",
      "page": 2
    }
  ]
}
```

---

# 6. High-Level Architecture

## Document Ingestion

```text
College Documents
       ↓
Google Drive
       ↓
n8n detects new/updated file
       ↓
Python Document Processing
       ↓
Text Extraction
       ↓
Cleaning + Chunking
       ↓
Metadata Creation
       ↓
Embedding Model
       ↓
Pinecone Vector Database
       ↓
Searchable Knowledge Base
```

## Question Answering

```text
User Question
       ↓
React Frontend
       ↓
FastAPI Backend
       ↓
Authentication / Permission Check
       ↓
Query Embedding
       ↓
Pinecone Semantic Search
       ↓
Relevant Document Chunks
       ↓
Reranking / Context Selection
       ↓
LLM
       ↓
Answer + Sources
       ↓
React Frontend
```

## Complete Architecture

```text
                         DOCUMIND AI
                              │
              ┌───────────────┴───────────────┐
              │                               │
       DOCUMENT SIDE                    QUESTION SIDE
              │                               │
       Google Drive                          User
              ↓                               ↓
             n8n                         React Frontend
              ↓                               ↓
     Document Processing                   FastAPI
              ↓                               ↓
       Chunking + Metadata             Authentication
              ↓                               ↓
          Embeddings                    Query Processing
              ↓                               ↓
          Pinecone                    Pinecone Search
              │                               ↓
              │                           Reranking
              │                               ↓
              └────────────────────→      Context
                                           ↓
                                          LLM
                                           ↓
                                  Answer + Citations
                                           ↓
                                      React UI
```

---

# 7. Technology Stack

## Frontend
Recommended:
- React.js
- JavaScript or TypeScript
- Modern CSS/component library as appropriate

Responsibilities:
- Login
- Dashboard
- AI chat
- Search/filter interface
- Source display
- Documents
- Chat history
- Admin interface
- API integration
- Loading/error states

## Backend
Recommended:
- Python
- FastAPI
- REST APIs
- JWT authentication
- PostgreSQL

Responsibilities:
- API layer
- Authentication
- Authorization
- User management
- Role-based access control
- Chat requests
- RAG orchestration
- Document metadata
- Chat history
- Application logic
- Error handling
- Logging

## AI/RAG
Components:
- Embedding model
- Pinecone vector database
- LLM
- RAG pipeline
- Retrieval
- Optional reranking
- Context construction
- Source/citation generation

Possible LLM providers:
- OpenAI
- Google Gemini
- Other suitable hosted/open-source LLM

Select the provider based on cost, availability, performance, privacy, and project requirements.

**Do not train an LLM from scratch.**

## Automation
**n8n**:
- Monitor Google Drive
- Detect new documents
- Detect updated documents
- Trigger ingestion
- Handle update/deletion workflows where applicable
- Connect external services

## Document repository
**Google Drive** is the primary source repository.

## Vector database
**Pinecone** stores document chunk embeddings and retrieval metadata.

## Application database
**PostgreSQL** is recommended for:
- Users
- Roles
- Departments
- Permissions
- Documents metadata
- Chat sessions
- Messages
- System/indexing status where useful

Do not use Pinecone as the normal relational application database.

---

# 8. Frontend Requirements

## 9.1 Login
- Email/username
- Password
- Authentication
- Error handling
- Session/token handling

## 9.2 Dashboard
Possible components:
- Welcome message
- Quick Ask/Search
- Total indexed documents
- Recent documents
- Recent conversations
- System/indexing status
- Useful quick actions

Keep it clean and suitable for college staff.

## 9.3 AI Chat
Features:
- Natural-language question input
- Loading state
- Answer display
- Source display
- Page/section information
- Relevant snippets where appropriate
- Conversation history
- Error states
- “No sufficient evidence found” state

Example:

```text
Question:
What evidence is available for student mentoring?

Answer:
The institution conducts student mentoring activities...

Sources:
Student_Mentoring_Report_2025-26.pdf — Page 4
Faculty_Mentor_Record.pdf — Page 2
```

## 9.4 Search and Filters
Useful filters:
- Department
- Academic year
- Document type
- Access level
- Other college-approved metadata

Filters should affect retrieval through backend-controlled metadata filtering.

## 9.5 Documents
Display:
- Document name
- Department
- Academic year
- Document type
- Upload/update date
- Indexing status

Admin-only actions may include:
- Trigger sync
- View indexing status
- Retry failed indexing
- Archive/delete

## 9.6 Chat History
Allow users to view:
- Previous questions
- Previous answers
- Sources used

## 9.7 Role-Based UI

### Admin
- User management
- Document/index management
- System status
- Sync controls

### Faculty/Staff
- Ask questions
- Search authorized documents
- View sources
- View history

### Student
- Access only student-authorized knowledge

Exact roles must be confirmed with the guide/college.

---

# 9. Backend API Design

Possible REST endpoints:

```text
POST /api/auth/login
POST /api/auth/register

POST /api/chat
GET  /api/chat/history
GET  /api/chat/{session_id}

GET  /api/documents
GET  /api/documents/{document_id}

POST /api/admin/sync
GET  /api/admin/indexing-status

GET  /api/users
POST /api/users
PUT  /api/users/{user_id}
```

Do not implement everything immediately. Start with the minimum required for the first working pipeline.

---

# 10. Chat API Contract

Frontend and backend should agree on the API format before development.

Example request:

```json
{
  "question": "What evidence exists for student mentoring activities?",
  "filters": {
    "department": "CSE",
    "academic_year": "2025-26"
  }
}
```

Example response:

```json
{
  "success": true,
  "answer": "The institution conducts student mentoring activities...",
  "sources": [
    {
      "document_name": "Student_Mentoring_Report_2025-26.pdf",
      "page": 4,
      "snippet": "..."
    }
  ]
}
```

No sufficient evidence:

```json
{
  "success": true,
  "answer": "I could not find sufficient evidence in the indexed institutional documents.",
  "sources": []
}
```

---

# 11. RAG Design

Recommended pipeline:

```text
Question
   ↓
Query preprocessing
   ↓
Permission / metadata filtering
   ↓
Query embedding
   ↓
Pinecone similarity search
   ↓
Top-K chunks
   ↓
Optional reranking
   ↓
Context selection
   ↓
Prompt construction
   ↓
LLM
   ↓
Answer validation / grounding
   ↓
Answer + Sources
```

---

# 12. Hallucination Control

This is a core requirement.

The LLM should:
- Answer only from retrieved context.
- Not invent facts.
- Not invent dates.
- Not invent documents.
- Not invent evidence.
- Clearly state when sufficient information is not available.

Conceptual rule:

```text
If retrieved documents do not contain enough information,
say that sufficient evidence was not found.
Do not make up information.
```

The system should prioritize faithfulness over answering at all costs.

---

# 13. Source Citation / Evidence Grounding

Each retrieved chunk should retain metadata such as:

```json
{
  "document_id": "abc123",
  "document_name": "NBA_Report_2025.pdf",
  "department": "CSE",
  "academic_year": "2025-26",
  "page": 14,
  "section": "Criterion 2",
  "chunk_id": "abc123_14_03",
  "access_level": "faculty"
}
```

This allows the system to show:
- Source document
- Page
- Section
- Relevant snippet
- Google Drive link if permitted

---

# 14. Document Ingestion

Target formats:
- PDF
- DOCX
- TXT
- Markdown
- Other formats only if required

Pipeline:

```text
File
 ↓
Validate
 ↓
Extract text
 ↓
Clean text
 ↓
Identify pages/sections
 ↓
Chunk
 ↓
Attach metadata
 ↓
Generate embeddings
 ↓
Upsert vectors into Pinecone
```

---

# 15. Chunking

Do not blindly split every document at arbitrary character boundaries.

Prefer preserving:
- Paragraphs
- Headings
- Sections
- Pages
- Logical document boundaries

Chunk size and overlap should be experimentally evaluated rather than treated as fixed universal values.

---

# 16. Incremental Indexing

If one new document is uploaded:

```text
New document
 ↓
n8n detects it
 ↓
Process only that document
 ↓
Generate embeddings
 ↓
Upsert vectors
```

Do not re-embed the entire collection every time.

For updates:

```text
Updated document
 ↓
Identify old document_id
 ↓
Remove/replace old chunks
 ↓
Process updated document
 ↓
Insert new chunks
```

For deletion:

```text
Deleted document
 ↓
Identify document_id
 ↓
Delete corresponding vectors
```

---

# 17. Google Drive + n8n

Conceptual workflow:

```text
Google Drive
     ↓
Detect new/updated file
     ↓
Download file
     ↓
Send to ingestion service
     ↓
Python processing
     ↓
Embedding
     ↓
Pinecone
```

Eventually support deleted files by removing their indexed chunks.

---

# 18. Permission-Aware Retrieval

Do not rely on the LLM to hide sensitive information.

Correct architecture:

```text
User
 ↓
Authentication
 ↓
User role / department / permissions
 ↓
Backend creates allowed metadata filters
 ↓
Pinecone retrieval
 ↓
Only authorized chunks retrieved
 ↓
LLM
```

Example metadata:

```json
{
  "department": "CSE",
  "access_level": "faculty"
}
```

**Frontend button hiding is NOT security.**

Backend must enforce access control.

---

# 19. Database Model — Initial Concept

### User
```text
id
name
email
password_hash
role
department_id
created_at
```

### Department
```text
id
name
```

### Document
```text
id
drive_file_id
name
department
academic_year
document_type
access_level
status
created_at
updated_at
```

### ChatSession
```text
id
user_id
created_at
```

### Message
```text
id
session_id
role
content
created_at
```

Permissions can be expanded according to college requirements.

---

# 20. Efficiency Requirements

Important principles:
- Precompute document embeddings during ingestion.
- Do not re-embed all documents for every question.
- Retrieve only relevant chunks.
- Use metadata filtering.
- Control LLM context size.
- Cache where useful.
- Use incremental indexing.
- Avoid unnecessary LLM calls.
- Log performance for evaluation.

Aim for an average user query response within a few seconds after indexing, but measure actual latency rather than promising a fixed number.

---

# 21. Error Handling

### No documents found
> No relevant institutional evidence was found.

### Document indexing failure
> Document could not be indexed. Please retry or contact the administrator.

### LLM/API failure
> The AI service is temporarily unavailable. Please try again.

### Unauthorized document
Never expose its contents.

### Invalid file
Reject unsupported/corrupt files with a useful error.

---

# 22. Logging and Monitoring

Eventually log:
- API requests
- Errors
- Retrieval latency
- LLM latency
- Number of retrieved chunks
- Indexing failures
- Document processing status
- Authentication failures where appropriate

Do not log sensitive document content unnecessarily.

---

# 23. Security

Minimum requirements:
- Password hashing
- JWT/session authentication
- Role-based access control
- Backend permission checks
- Environment variables for API keys
- No API keys committed to GitHub
- HTTPS in production
- Input validation
- File validation
- Controlled document access
- Secure database configuration

Example `.env`:

```text
OPENAI_API_KEY=
PINECONE_API_KEY=
DATABASE_URL=
JWT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

Never commit the actual `.env`.

Use `.env.example`.

---

# 24. Repository Structure

Use one shared GitHub repository:

```text
documind-ai/
│
├── frontend/
│   └── React application
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── auth/
│   │   ├── rag/
│   │   ├── ingestion/
│   │   ├── database/
│   │   └── services/
│   │
│   └── tests/
│
├── ingestion/
│   ├── document_processor/
│   ├── embeddings/
│   └── tests/
│
├── n8n/
│   └── workflows/
│
├── docs/
│
├── .env.example
├── README.md
└── docker-compose.yml
```

Keep frontend, backend, ingestion, and automation separated so the single developer can maintain clear module boundaries.

---

# 25. Integration Contracts

Before coding, agree on:

## 1. API contract
Example:
```text
POST /api/chat
```

## 2. Document schema
Everyone uses the same chunk metadata.

## 3. User/role schema
Everyone agrees on roles and permissions.

## 4. Error response format
Example:

```json
{
  "success": false,
  "error": "NO_RELEVANT_DOCUMENTS",
  "message": "No sufficient evidence was found."
}
```

---

# 26. Development Strategy

Do not wait until every module is finished before integration. As a solo developer, integrate each working module incrementally.

## Milestone 1 — AI Core

```text
Sample PDF
 ↓
Extraction
 ↓
Chunking
 ↓
Embedding
 ↓
Pinecone
 ↓
Question
 ↓
Retrieval
 ↓
LLM
 ↓
Answer + Source
```

Use 10–20 sample/sanitized college documents initially.

## Milestone 2 — Ingestion Automation

```text
Google Drive
 ↓
n8n
 ↓
Ingestion Service
 ↓
Pinecone
```

Verify new/updated files are indexed correctly.

## Milestone 3 — FastAPI

Connect the RAG engine to a clean API and test through Swagger/Postman.

## Milestone 4 — Frontend

Connect:

```text
React
 ↓
FastAPI
 ↓
RAG
 ↓
Pinecone
 ↓
LLM
```

## Milestone 5 — Security

Add:
- Authentication
- Roles
- Permission-aware retrieval
- Protected endpoints

## Milestone 6 — Production Hardening

Add:
- Logging
- Error handling
- Monitoring
- Incremental updates
- Docker
- Deployment
- Performance testing
- RAG evaluation

---

# 27. RAG Evaluation

Create a small ground-truth evaluation dataset.

Example:

| Question | Expected Source |
|---|---|
| What evidence exists for student mentoring? | Mentoring Report |
| What faculty development activities were conducted? | FDP Report |
| What are the examination regulations? | Academic Regulations |
| What evidence supports NBA Criterion 2? | NBA Report |

Evaluate:

### Retrieval quality
Was the correct document/chunk retrieved?

### Answer quality
Did the answer correctly represent the source?

### Citation correctness
Does the cited source actually support the answer?

### Hallucination
Did the model introduce unsupported information?

This can become an important research/project component.

---

# 28. Deployment Plan

```text
Local Development
 ↓
GitHub
 ↓
Testing
 ↓
Docker
 ↓
Cloud Deployment
```

Potential deployment:
- React → Vercel / AWS / similar
- FastAPI → AWS EC2 / Render / Railway / similar
- n8n → n8n Cloud or self-hosted
- Pinecone → Pinecone Cloud
- LLM → selected API provider
- PostgreSQL → managed PostgreSQL
- Google Drive → institutional repository

Choose providers based on college infrastructure, cost, privacy, and deployment requirements.

---

# 29. Important Project Decisions

Established decisions unless the guide/team changes them:

- Project uses RAG.
- Google Drive is the primary document repository.
- n8n is the automation layer.
- Python/FastAPI is the main backend.
- React is the frontend.
- Pinecone is the vector database.
- A pretrained/external LLM will be used.
- No LLM will be trained from scratch.
- Source-backed answers are a core requirement.
- Access control is required for institutional deployment.
- Incremental document indexing should be supported.
- NAAC/NBA evidence retrieval is the primary real-world use case.
- The system should also support general institutional document search.

---

# 30. Things NOT to Do

- Do not make the entire application in n8n.
- Do not train an LLM from scratch.
- Do not re-embed all documents for every question.
- Do not let the frontend handle authorization.
- Do not let the LLM answer without retrieved evidence.
- Do not store only document names; retain useful metadata.
- Do not build the UI first and design APIs later.
- Do not commit API keys.
- Do not claim exact performance before testing.
- Do not copy an existing GitHub/n8n project and present it as original work.

---

# 31. Technical References

These are implementation references, not the project's implementation.

- Pinecone n8n templates: https://github.com/pinecone-io/n8n-templates
- Google Drive → Pinecone → OpenAI example: https://github.com/pinecone-io/n8n-templates/blob/main/document-chat-database/chat-with-google-drive-using-pinecone-vector-database.json
- n8n Google Drive + Pinecone + OpenAI RAG: https://n8n.io/workflows/13147-chat-with-google-drive-documents-using-pinecone-and-openai-rag/
- n8n Google Drive + OpenAI + Pinecone RAG: https://n8n.io/workflows/4501-build-and-query-rag-system-with-google-drive-openai-gpt-4o-mini-and-pinecone/
- n8n document QA: https://n8n.io/workflows/9050-build-a-document-qa-system-with-google-drive-pinecone-and-openai-rag/
- BuildMindX N8N Agents: https://github.com/BuildMindX/N8N-Agents
- OpsForge: https://github.com/raksh-dev/OpsForge
- PDF Assistant RAG: https://github.com/param20h/PDF-Assistant-RAG

Use these to learn patterns. Do not blindly copy them.

---

# 32. Project Philosophy

The goal is NOT:

> Build a chatbot that talks to PDFs.

The goal is:

> Build a secure, source-grounded institutional knowledge system that automatically keeps its document knowledge base synchronized and allows authorized college users to retrieve reliable information using natural language.

Strong technical aspects:
1. Automated document ingestion
2. High-quality document processing
3. Semantic retrieval
4. RAG-based grounded generation
5. Source/evidence citations
6. Permission-aware retrieval
7. Incremental indexing
8. User-friendly interface
9. Application security
10. Evaluation of retrieval and answer quality
11. Deployment and maintainability

---

# 33. Recommended Implementation Order

```text
1. Finalize repository structure
        ↓
2. Set up React frontend
   + FastAPI backend
   + Python ingestion environment
        ↓
3. Define API + metadata contracts
        ↓
4. Build RAG prototype with sample documents
        ↓
5. Build Google Drive + n8n ingestion
        ↓
6. Connect FastAPI to RAG
        ↓
7. Connect React to FastAPI
        ↓
8. Add authentication + permissions
        ↓
9. Add evaluation + logging
        ↓
10. Dockerize and deploy
```

---

# 34. Instructions for AI Coding Tools

When using Antigravity, Cursor, Claude Code, Gemini, Copilot, or another AI coding agent with this file:

### Read this entire `context.md` first.

Treat it as the project's source of truth.

### Do not arbitrarily change the architecture.

If a change is genuinely necessary, explain:
1. What is being changed.
2. Why it is needed.
3. Which modules it affects.

### Maintain module boundaries

```text
frontend/
backend/
ingestion/
n8n/
```

### Do not create fake production functionality.

If an API, database, Google Drive integration, Pinecone integration, or LLM integration is not implemented, do not pretend it is.

### Use environment variables for secrets.

Never hard-code:
- API keys
- Database passwords
- JWT secrets
- OAuth secrets

### Prefer maintainable code.

Use:
- Clear naming
- Type hints where useful
- Modular services
- Validation
- Error handling
- Logging
- Tests
- Documentation

### Build incrementally.

Before implementing a large feature:
1. Inspect the current repository.
2. Understand existing modules.
3. Identify dependencies.
4. Implement the smallest working version.
5. Test it.
6. Then extend it.

### Do not overwrite working code unnecessarily.

Preserve existing functionality unless a deliberate architectural change is required.

### Explain integration points.

Every major module should clearly state:
- What it receives
- What it produces
- Which API/service it uses
- Which other module consumes its output

---

# 35. Definition of Done

The final system should demonstrate:

```text
Authorized College User
        ↓
Login
        ↓
DocuMind AI
        ↓
Natural-language question
        ↓
FastAPI
        ↓
Permission-aware retrieval
        ↓
Pinecone
        ↓
Relevant institutional evidence
        ↓
LLM
        ↓
Grounded answer
        ↓
Source documents + page/section
        ↓
User
```

Document side:

```text
College uploads/updates document
        ↓
Google Drive
        ↓
n8n detects change
        ↓
Document processing
        ↓
Chunking + metadata
        ↓
Embeddings
        ↓
Pinecone
        ↓
Document becomes searchable
```

The final system should be demonstrable end-to-end using realistic college/accreditation documents.

---

# 36. Scope Control

## Core/MVP
- Login
- Roles
- React UI
- FastAPI
- Google Drive
- n8n ingestion
- PDF/DOCX processing
- Chunking
- Embeddings
- Pinecone
- RAG
- LLM
- Source citations
- Chat history
- Basic permissions
- Incremental indexing

## Advanced features only if time permits
- Hybrid keyword + semantic retrieval
- Advanced reranking
- OCR for scanned PDFs
- Table-aware extraction
- Multi-document comparison
- Evidence export/report generation
- Advanced analytics
- Feedback-based retrieval improvement
- More sophisticated admin monitoring

Do not let advanced features delay the reliable core pipeline.

---

# 37. Final One-Line Description

**DocuMind AI is a secure, source-grounded institutional knowledge assistant that automatically indexes authorized college documents from Google Drive and uses Retrieval-Augmented Generation to answer natural-language questions with relevant evidence and citations.**

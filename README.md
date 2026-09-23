# DocuMind AI

**Enterprise AI Knowledge Assistant using Retrieval-Augmented Generation (RAG) for Intelligent Document Retrieval and Question Answering**

Final-Year CSE Major Project | Academic Year 2026–27  
**Developer:** Siddhi Varma | **Guide:** Dr. Anil Surve, HoD CSE

---

## Overview

DocuMind AI is a secure, source-grounded institutional knowledge assistant that automatically indexes authorized college documents from Google Drive and uses Retrieval-Augmented Generation (RAG) to answer natural-language questions with relevant evidence and citations.

**Primary use case:** NAAC/NBA accreditation — faculty and committee members can quickly find relevant documents and evidence by asking natural-language questions instead of manually searching through files.

> "What evidence is available for student mentoring activities?"
>
> → DocuMind AI retrieves *Student_Mentoring_Report_2025-26.pdf* (Page 4) and generates a grounded answer with source citations.

---

## Architecture

```
DOCUMENT SIDE                          QUESTION SIDE
─────────────────────────────────────────────────────
College Documents                          User
       ↓                                    ↓
Google Drive                          React Frontend
       ↓                                    ↓
n8n (detects new/updated)              FastAPI Backend
       ↓                                    ↓
Document Processing                  Authentication
       ↓                                    ↓
Chunking + Metadata              Permission-aware Filter
       ↓                                    ↓
Embeddings                          Pinecone Search
       ↓                                    ↓
Pinecone ──────────────────────→   Relevant Chunks
                                            ↓
                                           LLM
                                            ↓
                                  Grounded Answer + Citations
                                            ↓
                                      React Frontend
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript (Vite) |
| Backend | Python + FastAPI |
| Database | PostgreSQL (SQLAlchemy 2.x async + Alembic) |
| Vector DB | Pinecone |
| Embeddings | OpenAI text-embedding-3-small (planned) |
| LLM | OpenAI GPT-4o-mini or Google Gemini (planned) |
| Automation | n8n |
| Document Source | Google Drive |
| Auth | JWT (python-jose + passlib) |

---

## Repository Structure

```
DocuMind-AI/
│
├── frontend/                   # React + TypeScript (Vite)
│   └── src/
│       ├── pages/              # Login, Dashboard, Chat, Documents, History, Admin
│       ├── components/layout/  # Sidebar, ProtectedRoute
│       ├── services/api.ts     # Axios API service layer
│       ├── store/authStore.ts  # Zustand auth state
│       └── router/index.tsx    # React Router v6
│
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── api/v1/             # Versioned REST endpoints
│   │   ├── auth/               # JWT handler + FastAPI dependencies
│   │   ├── core/               # Config (pydantic-settings) + logging
│   │   ├── database/           # SQLAlchemy engine + ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── rag/                # RAG pipeline modules (stubs → Phase 2)
│   └── tests/                  # pytest test suite
│
├── ingestion/                  # Document processing pipeline (independent)
│   ├── document_processor/     # Parser, cleaner, chunker, metadata
│   ├── embeddings/             # Embedding service
│   └── tests/                  # Chunker unit tests
│
├── n8n/workflows/              # n8n workflow JSON files (Phase 3)
├── docs/                       # Architecture + API contract
│
├── .env.example                # Environment variable template
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Random secret for signing JWT tokens |
| `PINECONE_API_KEY` | Pinecone vector DB key |
| `PINECONE_INDEX_NAME` | Pinecone index name |
| `OPENAI_API_KEY` | OpenAI API key (for embeddings + LLM) |
| `GOOGLE_CLIENT_ID/SECRET` | OAuth for Google Drive |

**Never commit `.env` to version control.**

---

## Running Locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`  
Health check: `http://localhost:8000/api/health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

### PostgreSQL (Docker)

```bash
docker-compose up postgres
```

---

## Running Tests

### Backend Tests

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

### Ingestion Tests

```bash
cd ingestion
python -m pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Auth | Status |
|---|---|---|---|
| GET | `/api/health` | None | ✅ Working |
| POST | `/api/auth/login` | None | ⚠ Stub (Phase 2) |
| POST | `/api/auth/register` | None | ⚠ Stub (Phase 2) |
| POST | `/api/chat` | Bearer | ⚠ RAG stubs (Phase 2) |
| GET | `/api/chat/history` | Bearer | ⚠ Stub (Phase 2) |
| GET | `/api/documents` | Bearer | ⚠ Stub (Phase 2) |
| GET | `/api/admin/indexing-status` | Admin | ⚠ Stub (Phase 2) |
| POST | `/api/admin/sync` | Admin | ⚠ Stub (Phase 3) |

See [docs/api_contract.md](docs/api_contract.md) for full request/response examples.

---

## Development Phases

### ✅ Phase 1 — Foundation (COMPLETE)
- Repository structure
- FastAPI backend with all route modules
- React frontend with all pages
- Database models (User, Department, Document, ChatSession, Message)
- RAG pipeline interfaces (stubs)
- Ingestion pipeline interfaces (chunker is functional)
- Environment configuration
- Basic test suite (5 backend + 8 ingestion tests)
- Docker Compose skeleton

### 🔲 Phase 2 — Core AI Pipeline
- PostgreSQL integration (Alembic migrations)
- JWT authentication (login, register)
- Pinecone connection + retrieval
- LLM integration (OpenAI / Gemini)
- End-to-end RAG chat
- Chat history persistence

### 🔲 Phase 3 — Google Drive + n8n
- Google Drive monitoring
- n8n workflow integration
- Automated document ingestion
- Incremental indexing (add/update/delete)

### 🔲 Phase 4 — Security + Production
- Role-based access control
- Permission-aware Pinecone retrieval
- Logging and monitoring
- Docker deployment
- RAG evaluation dataset

---

## Security Notes

- API keys are loaded from `.env` — never committed to Git
- Backend enforces authorization — hiding UI elements is NOT security
- Pinecone metadata filters are built by the backend from user role — not from client input
- Passwords will be hashed with bcrypt (passlib)

---

## Project Philosophy

The goal is NOT to build a chatbot that talks to PDFs.

The goal is to build a **secure, source-grounded institutional knowledge system** that automatically keeps its document knowledge base synchronized and allows authorized college users to retrieve reliable information using natural language.

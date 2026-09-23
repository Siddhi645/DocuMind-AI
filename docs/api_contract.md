# API Contract — DocuMind AI

## Version: v1
## Base URL: `http://localhost:8000/api`

This document defines the agreed API contract between frontend and backend.
**Both sides must remain in sync with this document.**

---

## 1. Health Check

```
GET /api/health
Authentication: None required
```

### Response 200 OK
```json
{
  "status": "ok",
  "service": "documind-backend",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 2. Authentication

### Login
```
POST /api/auth/login
Authentication: None required
```

**Request:**
```json
{
  "email": "faculty@college.edu",
  "password": "securepassword"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Response 401 Unauthorized:**
```json
{
  "success": false,
  "error": "INVALID_CREDENTIALS",
  "message": "Invalid email or password."
}
```

---

## 3. Core Chat Endpoint (Primary RAG Endpoint)

```
POST /api/chat
Authentication: Bearer token required
```

**Request:**
```json
{
  "question": "What evidence is available for student mentoring activities?",
  "filters": {
    "department": "CSE",
    "academic_year": "2025-26"
  },
  "session_id": "optional-uuid-to-continue-session"
}
```

**Response 200 OK — Evidence found:**
```json
{
  "success": true,
  "answer": "The institution conducts student mentoring activities as documented in...",
  "sources": [
    {
      "document_name": "Student_Mentoring_Report_2025-26.pdf",
      "document_id": "abc-123",
      "page": 4,
      "section": "Section 2: Mentoring Activities",
      "snippet": "Faculty mentors meet students at least once per month...",
      "academic_year": "2025-26",
      "department": "CSE",
      "score": 0.9241
    },
    {
      "document_name": "Faculty_Mentor_Record.pdf",
      "document_id": "def-456",
      "page": 2,
      "section": null,
      "snippet": "Mentoring sessions conducted: 48 sessions in 2025-26...",
      "academic_year": "2025-26",
      "department": "CSE",
      "score": 0.8873
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What evidence is available for student mentoring activities?"
}
```

**Response 200 OK — No evidence found:**
```json
{
  "success": true,
  "answer": "I could not find sufficient evidence in the indexed institutional documents to answer this question.",
  "sources": [],
  "session_id": "550e8400-...",
  "question": "What evidence is available for student mentoring activities?"
}
```

**Response 401 Unauthorized:**
```json
{
  "success": false,
  "error": "UNAUTHORIZED",
  "message": "Authentication required."
}
```

**Response 500 Internal Server Error:**
```json
{
  "success": false,
  "error": "PIPELINE_ERROR",
  "message": "The AI service encountered an error. Please try again."
}
```

---

## 4. Documents

### List Documents
```
GET /api/documents?page=1&page_size=20&department=CSE&academic_year=2025-26
Authentication: Bearer token required
```

**Response 200 OK:**
```json
{
  "documents": [
    {
      "id": "abc-123",
      "name": "NBA_Report_2025.pdf",
      "department": "CSE",
      "academic_year": "2025-26",
      "document_type": "accreditation",
      "access_level": "faculty",
      "status": "indexed",
      "chunk_count": 47,
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-01-15T11:45:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

---

## 5. Admin

### Trigger Sync
```
POST /api/admin/sync
Authentication: Bearer token required (admin role)
```

### Indexing Status
```
GET /api/admin/indexing-status
Authentication: Bearer token required (admin role)
```

**Response 200 OK:**
```json
{
  "total": 50,
  "indexed": 45,
  "pending": 3,
  "processing": 1,
  "failed": 1
}
```

---

## Standard Error Format

All API errors follow this format:
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error message.",
  "details": null
}
```

| Error Code | HTTP Status |
|---|---|
| `UNAUTHORIZED` | 401 |
| `FORBIDDEN` | 403 |
| `NOT_FOUND` | 404 |
| `PIPELINE_ERROR` | 500 |
| `INVALID_CREDENTIALS` | 401 |
| `NOT_IMPLEMENTED` | 501 |

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

The token is obtained from `POST /api/auth/login`.
Tokens expire after 60 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`).

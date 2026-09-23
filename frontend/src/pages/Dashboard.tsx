/**
 * DocuMind AI — Dashboard Page
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { api, type HealthResponse } from '../services/api';
import './Dashboard.css';

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState(false);

  useEffect(() => {
    api.health()
      .then((res) => setHealth(res.data))
      .catch(() => setHealthError(true));
  }, []);

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="dashboard fade-in">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">
          {greeting()}, <strong>{user?.name || 'User'}</strong>. Welcome to DocuMind AI.
        </p>
      </div>

      {/* Status banner */}
      <div className="dashboard-status">
        <div className={`status-dot ${healthError ? 'error' : 'ok'}`} />
        <span>
          Backend:{' '}
          {healthError ? (
            <span className="status-text-error">Offline (start uvicorn)</span>
          ) : health ? (
            <span className="status-text-ok">Online — {health.service} v{health.version} ({health.environment})</span>
          ) : (
            <span className="status-text-loading">Connecting…</span>
          )}
        </span>
        {health && (
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="status-link"
          >
            Swagger UI ↗
          </a>
        )}
      </div>

      {/* Quick actions */}
      <div className="dashboard-grid">
        <Link to="/chat" className="dashboard-card" id="dashboard-chat-card">
          <div className="dashboard-card-icon" style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa' }}>◎</div>
          <div>
            <h3 className="dashboard-card-title">Ask a Question</h3>
            <p className="dashboard-card-desc">Search institutional documents using AI</p>
          </div>
          <span className="dashboard-card-arrow">→</span>
        </Link>

        <Link to="/documents" className="dashboard-card" id="dashboard-docs-card">
          <div className="dashboard-card-icon" style={{ background: 'rgba(139,92,246,0.15)', color: '#a78bfa' }}>⊟</div>
          <div>
            <h3 className="dashboard-card-title">Documents</h3>
            <p className="dashboard-card-desc">Browse indexed institutional documents</p>
          </div>
          <span className="dashboard-card-arrow">→</span>
        </Link>

        <Link to="/history" className="dashboard-card" id="dashboard-history-card">
          <div className="dashboard-card-icon" style={{ background: 'rgba(6,182,212,0.15)', color: '#22d3ee' }}>⊙</div>
          <div>
            <h3 className="dashboard-card-title">Chat History</h3>
            <p className="dashboard-card-desc">Review previous questions and answers</p>
          </div>
          <span className="dashboard-card-arrow">→</span>
        </Link>

        {user?.role === 'admin' && (
          <Link to="/admin" className="dashboard-card" id="dashboard-admin-card">
            <div className="dashboard-card-icon" style={{ background: 'rgba(245,158,11,0.15)', color: '#fbbf24' }}>⚙</div>
            <div>
              <h3 className="dashboard-card-title">Administration</h3>
              <p className="dashboard-card-desc">Manage users, documents, and indexing</p>
            </div>
            <span className="dashboard-card-arrow">→</span>
          </Link>
        )}
      </div>

      {/* Phase info */}
      <div className="dashboard-phase-info card">
        <div className="dashboard-phase-header">
          <span className="badge badge-info">Phase 1 — Foundation</span>
          <span className="badge badge-success">Backend Running</span>
        </div>
        <p>
          The project foundation is complete. The backend API is running with structured
          stubs. In <strong>Phase 2</strong>, the RAG pipeline (Pinecone + LLM) and
          authentication will be connected.
        </p>
        <div className="dashboard-phase-items">
          <div className="phase-item done">✓ Repository structure</div>
          <div className="phase-item done">✓ FastAPI backend</div>
          <div className="phase-item done">✓ React frontend</div>
          <div className="phase-item done">✓ Database models</div>
          <div className="phase-item done">✓ RAG pipeline interfaces</div>
          <div className="phase-item done">✓ Ingestion interfaces</div>
          <div className="phase-item pending">○ Authentication (Phase 2)</div>
          <div className="phase-item pending">○ Pinecone + LLM (Phase 2)</div>
          <div className="phase-item pending">○ Google Drive + n8n (Phase 3)</div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

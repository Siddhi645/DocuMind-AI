/**
 * DocuMind AI — Chat History Page (Phase 1 Foundation)
 */

import React from 'react';
import './Placeholder.css';

const HistoryPage: React.FC = () => (
  <div className="placeholder-page fade-in">
    <div className="page-header">
      <h1 className="page-title">Chat History</h1>
      <p className="page-subtitle">Review your previous questions and answers</p>
    </div>

    <div className="placeholder-card card">
      <div className="placeholder-icon">⊙</div>
      <h2>Chat History — Phase 2</h2>
      <p>
        This page will show all your past conversation sessions with DocuMind AI,
        including the questions asked, answers received, and sources cited.
      </p>

      <div className="placeholder-features">
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          List of past chat sessions
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          View full conversation thread
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          See sources cited per answer
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Continue a previous session
        </div>
      </div>
    </div>

    <div className="alert alert-info">
      <span>ℹ</span>
      <span>
        The backend endpoint <code>GET /api/chat/history</code> is defined.
        Chat sessions will persist to PostgreSQL in Phase 2.
      </span>
    </div>
  </div>
);

export default HistoryPage;

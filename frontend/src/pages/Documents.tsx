/**
 * DocuMind AI — Documents Page (Phase 1 Foundation)
 */

import React from 'react';
import './Placeholder.css';

const DocumentsPage: React.FC = () => (
  <div className="placeholder-page fade-in">
    <div className="page-header">
      <h1 className="page-title">Documents</h1>
      <p className="page-subtitle">Browse and manage indexed institutional documents</p>
    </div>

    <div className="placeholder-card card">
      <div className="placeholder-icon">⊟</div>
      <h2>Documents — Phase 2</h2>
      <p>
        This page will display all indexed institutional documents with their status,
        department, academic year, and access level. Admins can trigger re-indexing here.
      </p>

      <div className="placeholder-features">
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Document list with pagination
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Filter by department, year, type
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Indexing status per document
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Admin: trigger re-index / archive
        </div>
      </div>
    </div>

    <div className="alert alert-info">
      <span>ℹ</span>
      <span>
        The backend endpoint <code>GET /api/documents</code> is defined and protected.
        Connect it to PostgreSQL in Phase 2 to populate this page.
      </span>
    </div>
  </div>
);

export default DocumentsPage;

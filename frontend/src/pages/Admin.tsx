/**
 * DocuMind AI — Admin Page (Phase 1 Foundation)
 */

import React from 'react';
import './Placeholder.css';

const AdminPage: React.FC = () => (
  <div className="placeholder-page fade-in">
    <div className="page-header">
      <h1 className="page-title">Administration</h1>
      <p className="page-subtitle">Manage users, documents, and system settings</p>
    </div>

    <div className="placeholder-card card">
      <div className="placeholder-icon">⚙</div>
      <h2>Admin Panel — Phase 2</h2>
      <p>
        The administration panel will allow admins to manage users, trigger Google Drive
        synchronization, view indexing status, and retry failed ingestion jobs.
      </p>

      <div className="placeholder-features">
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          User management (list, create, update roles)
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Document indexing status dashboard
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Trigger Google Drive sync (n8n)
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          Retry failed indexing jobs
        </div>
        <div className="placeholder-feature">
          <span className="badge badge-purple">Planned</span>
          System health and performance metrics
        </div>
      </div>
    </div>

    <div className="alert alert-info">
      <span>ℹ</span>
      <span>
        Admin endpoints <code>GET /api/admin/indexing-status</code> and{' '}
        <code>POST /api/admin/sync</code> are defined with admin-role protection.
        They will be fully implemented in Phase 2.
      </span>
    </div>
  </div>
);

export default AdminPage;

/**
 * DocuMind AI — Protected Route
 *
 * Phase 2B: Handles isInitializing state to prevent flash-redirect to /login
 * while the application is validating a stored token via GET /api/auth/me.
 *
 * Flow:
 *   isInitializing = true  → render loading spinner (token restore in progress)
 *   isAuthenticated = false → redirect to /login
 *   adminOnly + not admin  → redirect to /dashboard
 *   otherwise              → render the protected page inside the app layout
 */

import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import Sidebar from './Sidebar';

interface ProtectedRouteProps {
  adminOnly?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ adminOnly = false }) => {
  const { isAuthenticated, isInitializing, user } = useAuthStore();
  const location = useLocation();

  // While initializeAuth() is running, show a minimal loading state.
  // This prevents an incorrect redirect to /login before the stored token
  // has been validated against the backend.
  if (isInitializing) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: 'var(--bg-primary, #0f1117)',
          color: 'var(--text-secondary, #94a3b8)',
          gap: '0.75rem',
          fontFamily: 'system-ui, sans-serif',
        }}
        aria-live="polite"
        aria-label="Restoring session"
      >
        <span
          style={{
            width: 20,
            height: 20,
            border: '2px solid currentColor',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            display: 'inline-block',
            animation: 'spin 0.7s linear infinite',
          }}
          aria-hidden="true"
        />
        Restoring session…
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (adminOnly && user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main">
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default ProtectedRoute;

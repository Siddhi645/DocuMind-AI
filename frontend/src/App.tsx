/**
 * DocuMind AI — Root Application Component
 *
 * Phase 2B: Calls initializeAuth() on mount to restore the user session
 * from a stored token by validating it against GET /api/auth/me.
 */

import { useEffect } from 'react';
import AppRouter from './router/index';
import { useAuthStore } from './store/authStore';
import './styles/globals.css';

function App() {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    // Run once on app load: validate any stored token and restore auth state.
    // ProtectedRoute waits for isInitializing to be false before deciding to
    // redirect, so there is no flash-redirect to /login on valid sessions.
    initializeAuth();
  }, [initializeAuth]);

  return <AppRouter />;
}

export default App;

/**
 * DocuMind AI — Auth Store (Zustand)
 * Global auth state: user info, token, login/logout, and session restore.
 *
 * Phase 2B: User profile is now sourced from GET /api/auth/me (database),
 * replacing the Phase 1 workaround of decoding the JWT payload client-side.
 *
 * Session restore flow (on page reload):
 *   initializeAuth() → reads stored token → calls GET /api/auth/me
 *   → success: restore auth state
 *   → failure: clear token and force re-login
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api, type UserProfile } from '../services/api';

// Re-export so components can import User type from the store
export type { UserProfile as User };

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  /** True while initializeAuth() is running — prevents ProtectedRoute from
   *  flash-redirecting to /login before the token restore check completes. */
  isInitializing: boolean;

  // Actions
  setAuth: (user: UserProfile, token: string) => void;
  logout: () => void;
  /**
   * Called once on application mount (in App.tsx).
   * If a stored token exists, calls GET /api/auth/me to validate it and
   * restore the full user profile from the database.
   * If the token is expired or invalid the store is cleared.
   */
  initializeAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isInitializing: true, // start as true — resolved after first initializeAuth()

      setAuth: (user, token) => {
        localStorage.setItem('documind_access_token', token);
        set({ user, token, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem('documind_access_token');
        set({ user: null, token: null, isAuthenticated: false });
      },

      initializeAuth: async () => {
        const token = localStorage.getItem('documind_access_token');

        if (!token) {
          // No stored token — not authenticated
          set({ user: null, token: null, isAuthenticated: false, isInitializing: false });
          return;
        }

        // A token exists — validate it by calling /auth/me
        // The token will be attached by the Axios request interceptor
        try {
          const response = await api.getMe();
          set({
            user: response.data,
            token,
            isAuthenticated: true,
            isInitializing: false,
          });
        } catch {
          // Token is expired, revoked, or user was deleted — clear everything
          localStorage.removeItem('documind_access_token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isInitializing: false,
          });
        }
      },
    }),
    {
      name: 'documind-auth',
      // Only persist user + token. isInitializing is always reset to true on
      // hydration because we always need to re-validate the token on reload.
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      // After persisted state is rehydrated, mark isInitializing = true so
      // ProtectedRoute waits for initializeAuth() to finish
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isInitializing = true;
        }
      },
    }
  )
);

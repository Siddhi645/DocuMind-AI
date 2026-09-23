/**
 * DocuMind AI — Login Page
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { api } from '../services/api';
import './Login.css';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { setAuth } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await api.login({ email, password });
      const { access_token } = response.data;

      // Phase 1: Decode basic user info from token payload
      // Phase 2: Fetch full user profile from /api/users/me
      const payload = JSON.parse(atob(access_token.split('.')[1]));
      setAuth(
        {
          id: payload.sub || 'unknown',
          name: payload.name || email.split('@')[0],
          email: payload.email || email,
          role: payload.role || 'faculty',
        },
        access_token
      );
      navigate(from, { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 501) {
        setError('Authentication is not yet implemented (Phase 1). The full login system will be available in Phase 2.');
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Background decoration */}
      <div className="login-bg-glow" aria-hidden="true" />
      <div className="login-bg-grid" aria-hidden="true" />

      <div className="login-container">
        {/* Logo */}
        <div className="login-logo" aria-label="DocuMind AI">
          <div className="login-logo-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div>
            <h1 className="login-logo-name">DocuMind AI</h1>
            <p className="login-logo-tagline">Institutional Knowledge Assistant</p>
          </div>
        </div>

        {/* Card */}
        <div className="login-card card-glass">
          <h2 className="login-title">Welcome back</h2>
          <p className="login-subtitle">Sign in to access institutional documents</p>

          {error && (
            <div className="alert alert-error" role="alert" id="login-error">
              <span>⚠</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="login-field">
              <label htmlFor="login-email" className="input-label">
                Email address
              </label>
              <input
                id="login-email"
                type="email"
                className="input"
                placeholder="faculty@college.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
                disabled={isLoading}
              />
            </div>

            <div className="login-field">
              <label htmlFor="login-password" className="input-label">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                className="input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                disabled={isLoading}
              />
            </div>

            <button
              id="login-submit-btn"
              type="submit"
              className="btn btn-primary btn-lg login-btn"
              disabled={isLoading || !email || !password}
            >
              {isLoading ? (
                <>
                  <span className="spinner spinner-sm" aria-hidden="true" />
                  Signing in…
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          <p className="login-phase-note">
            <span className="badge badge-info">Phase 1</span>
            &nbsp;Authentication endpoint is a stub. Full login arrives in Phase 2.
          </p>
        </div>

        <p className="login-footer">
          DocuMind AI · Final Year CSE Project · Academic Year 2026–27
        </p>
      </div>
    </div>
  );
};

export default LoginPage;

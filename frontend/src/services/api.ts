/**
 * DocuMind AI — API Service Layer
 * Centralized Axios instance with auth token injection and error handling.
 *
 * All backend communication goes through this module.
 * Never import axios directly in components — always use this service.
 */

import axios, { type AxiosInstance, type AxiosResponse } from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// ---- Axios instance ----
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ---- Request interceptor: attach JWT ----
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('documind_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ---- Response interceptor: handle 401 ----
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('documind_access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ---- Types ----
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChatFilters {
  department?: string;
  academic_year?: string;
  document_type?: string;
}

export interface ChatRequest {
  question: string;
  filters?: ChatFilters;
  session_id?: string;
}

export interface SourceCitation {
  document_name: string;
  document_id?: string;
  page?: number;
  section?: string;
  snippet?: string;
  academic_year?: string;
  department?: string;
  score?: number;
}

export interface ChatResponse {
  success: boolean;
  answer: string;
  sources: SourceCitation[];
  session_id?: string;
  question?: string;
}

// ---- API functions ----

export const api = {
  // Health
  health: (): Promise<AxiosResponse<HealthResponse>> =>
    apiClient.get('/health'),

  // Auth
  login: (data: LoginRequest): Promise<AxiosResponse<TokenResponse>> =>
    apiClient.post('/auth/login', data),

  // Chat
  chat: (data: ChatRequest): Promise<AxiosResponse<ChatResponse>> =>
    apiClient.post('/chat', data),

  getChatHistory: (page = 1, pageSize = 20) =>
    apiClient.get(`/chat/history?page=${page}&page_size=${pageSize}`),

  getChatSession: (sessionId: string) =>
    apiClient.get(`/chat/${sessionId}`),

  // Documents
  listDocuments: (params?: Record<string, string | number>) =>
    apiClient.get('/documents', { params }),

  getDocument: (id: string) =>
    apiClient.get(`/documents/${id}`),

  // Admin
  triggerSync: () =>
    apiClient.post('/admin/sync'),

  getIndexingStatus: () =>
    apiClient.get('/admin/indexing-status'),

  // Users (admin)
  listUsers: (page = 1) =>
    apiClient.get(`/users?page=${page}`),
};

export default apiClient;

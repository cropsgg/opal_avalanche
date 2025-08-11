import axios from 'axios';
import {
  DocumentHashRequest,
  DocumentHashResponse,
  SubnetNotarizeRequest,
  SubnetNotarizeResponse,
  NotarizationStatus,
  AuditData,
  BlockchainStatus,
  QdrantSearchRequest,
  QdrantSearchResponse,
  HealthStatus,
  Metrics,
  ReleaseRegistration,
  KnowledgeGraphData,
  GraphFilterRequest,
  GraphStats,
} from '@/types';

const API_BASE_URL = process.env.SERVER_API_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth token management
let authToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Blockchain API calls
export const blockchainApi = {
  // Hash documents and compute Merkle root
  hashDocuments: async (data: DocumentHashRequest): Promise<DocumentHashResponse> => {
    const response = await api.post('/api/v1/documents/hash', data);
    return response.data;
  },

  // Notarize data on subnet
  notarize: async (data: SubnetNotarizeRequest): Promise<SubnetNotarizeResponse> => {
    const response = await api.post('/api/v1/subnet/notarize', data);
    return response.data;
  },

  // Get notarization status
  getNotarization: async (runId: string): Promise<NotarizationStatus> => {
    const response = await api.get(`/api/v1/subnet/notary/${runId}`);
    return response.data;
  },

  // Get audit data
  getAuditData: async (runId: string): Promise<AuditData> => {
    const response = await api.get(`/api/v1/subnet/audit/${runId}`);
    return response.data;
  },

  // Get blockchain status
  getStatus: async (): Promise<BlockchainStatus> => {
    const response = await api.get('/api/v1/status');
    return response.data;
  },

  // Register project release
  registerRelease: async (
    version: string,
    sourceHash: string,
    artifactHash: string
  ): Promise<ReleaseRegistration> => {
    const response = await api.post('/api/v1/register-release', {
      version,
      source_hash: sourceHash,
      artifact_hash: artifactHash,
    });
    return response.data;
  },
};

// Search API calls
export const searchApi = {
  // Search vectors in Qdrant
  search: async (data: QdrantSearchRequest): Promise<QdrantSearchResponse> => {
    const response = await api.post('/api/v1/search', data);
    return response.data;
  },
};

// Health and monitoring API calls
export const healthApi = {
  // Basic health check
  getHealth: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  },

  // Detailed health check
  getDetailedHealth: async (): Promise<HealthStatus> => {
    const response = await api.get('/health/detailed');
    return response.data;
  },

  // Get metrics
  getMetrics: async (): Promise<Metrics> => {
    const response = await api.get('/metrics');
    return response.data;
  },
};

// Knowledge Graph API
export const knowledgeGraphApi = {
  async getKnowledgeGraph(params?: {
    limit?: number;
    min_similarity?: number;
    search_query?: string;
    cluster_count?: number;
  }): Promise<KnowledgeGraphData> {
    const response = await api.get('/api/v1/knowledge-graph/', { params });
    return response.data;
  },

  async getGraphStats(): Promise<GraphStats> {
    const response = await api.get('/api/v1/knowledge-graph/stats');
    return response.data;
  },

  async searchKnowledgeGraph(filterRequest: GraphFilterRequest): Promise<KnowledgeGraphData> {
    const response = await api.post('/api/v1/knowledge-graph/search', filterRequest);
    return response.data;
  }
};

// Authentication API
export const authApi = {
  // Login
  login: async (user_id: string, password: string): Promise<{
    access_token: string;
    token_type: string;
    expires_in: number;
    user_id: string;
  }> => {
    const response = await api.post('/api/v1/auth/login', {
      user_id,
      password,
    });
    return response.data;
  },

  // Logout
  logout: async (token: string): Promise<void> => {
    const tempApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    await tempApi.post('/api/v1/auth/logout');
  },

  // Get current user
  getCurrentUser: async (token: string): Promise<{
    user_id: string;
    authenticated: boolean;
    session_created: string;
  }> => {
    const tempApi = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    const response = await tempApi.get('/api/v1/auth/me');
    return response.data;
  },

  // Get auth status
  getAuthStatus: async (): Promise<{
    auth_enabled: boolean;
    active_sessions: number;
    session_timeout: number;
  }> => {
    const response = await api.get('/api/v1/auth/status');
    return response.data;
  },
};

// Utility functions
export const apiUtils = {
  // Test API connectivity
  testConnection: async (): Promise<boolean> => {
    try {
      const response = await api.get('/');
      return response.status === 200;
    } catch {
      return false;
    }
  },

  // Format error messages
  formatError: (error: any): string => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.response?.data?.error) {
      return error.response.data.error;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  },

  // Check if error is a network error
  isNetworkError: (error: any): boolean => {
    return !error.response && error.request;
  },
};

export default api;

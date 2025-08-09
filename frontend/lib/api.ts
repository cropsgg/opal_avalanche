const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    try {
      // For client-side use, we need to get the token from Clerk
      if (typeof window !== 'undefined') {
        // Get token from window.Clerk if available
        const clerk = (window as any).Clerk;
        if (clerk && clerk.session) {
          const token = await clerk.session.getToken();
          return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
          };
        }
      }
      
      return {
        'Content-Type': 'application/json',
      };
    } catch (error) {
      console.warn('Failed to get auth token:', error);
      return {
        'Content-Type': 'application/json',
      };
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const headers = await this.getAuthHeaders();
      const url = `${this.baseURL}${endpoint}`;

      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 500,
      };
    }
  }

  // Health check
  async health() {
    return this.request<{ ok: boolean }>('/health');
  }

  // Matters API
  async createMatter(data: { title: string; language?: string }) {
    return this.request<{ id: string; title: string }>('/v1/matters', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMatters() {
    return this.request<Array<{
      id: string;
      user_id: string;
      title: string;
      language: 'en' | 'hi';
      created_at: string;
      documents_count?: number;
      last_analysis?: string;
      status?: 'active' | 'archived' | 'draft';
    }>>('/v1/matters');
  }

  async getMatter(id: string) {
    return this.request<{
      id: string;
      user_id: string;
      title: string;
      language: 'en' | 'hi';
      created_at: string;
      documents_count?: number;
      last_analysis?: string;
      status?: 'active' | 'archived' | 'draft';
    }>(`/v1/matters/${id}`);
  }

  // Documents API
  async uploadDocument(matterId: string, file: File) {
    try {
      const headers = await this.getAuthHeaders();
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseURL}/v1/matters/${matterId}/documents`, {
        method: 'POST',
        headers: {
          // Remove Content-Type to let browser set it with boundary for FormData
          ...((headers as any).Authorization && { 'Authorization': (headers as any).Authorization }),
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || `HTTP ${response.status}`,
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      console.error('Document upload failed:', error);
      return {
        error: error instanceof Error ? error.message : 'Upload failed',
        status: 500,
      };
    }
  }

  async getDocuments(matterId: string) {
    return this.request<Array<{
      id: string;
      matter_id: string;
      storage_path: string;
      filetype: string;
      size: number;
      ocr_status: string;
      created_at: string;
    }>>(`/v1/matters/${matterId}/documents`);
  }

  // Chat API
  async sendChatMessage(data: {
    matterId: string;
    message: string;
    mode: 'general' | 'precedent' | 'limitation' | 'draft';
    filters?: Record<string, any>;
  }) {
    return this.request<{
      answer: string;
      citations: Array<{
        authority_id: string;
        court: string;
        cite: string;
        para_ids: number[];
        title?: string;
        neutral_cite?: string;
        reporter_cite?: string;
      }>;
      evidence_merkle_root?: string;
      run_id: string;
      confidence?: number;
    }>('/v1/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Runs API
  async getRun(runId: string) {
    return this.request<{
      id: string;
      query_id: string;
      answer_text: string;
      confidence: number;
      retrieval_set_json: any[];
      created_at: string;
      agent_votes?: Array<{
        agent: string;
        decision_json: any;
        confidence: number;
        aligned: boolean;
      }>;
    }>(`/v1/runs/${runId}`);
  }

  // Export API
  async exportRun(runId: string, format: 'pdf' | 'docx' | 'json') {
    return this.request<{ download_url: string }>(`/v1/runs/${runId}/export`, {
      method: 'POST',
      body: JSON.stringify({ format }),
    });
  }

  // Notarization API
  async notarizeRun(runId: string) {
    return this.request<{
      tx_hash: string;
      block_number: number;
      merkle_root: string;
    }>(`/v1/runs/${runId}/notarize`, {
      method: 'POST',
    });
  }

  async getNotarization(runId: string) {
    return this.request<{
      run_id: string;
      merkle_root: string;
      tx_hash: string;
      network: string;
      block_number: number;
      created_at: string;
    }>(`/v1/notary/${runId}`);
  }

  // User API
  async getUser() {
    return this.request<{
      id: string;
      clerk_id: string;
      email: string;
      role: string;
      wallet_address?: string;
      created_at: string;
    }>('/v1/users/me');
  }

  async updateUser(data: { wallet_address?: string }) {
    return this.request<{
      id: string;
      wallet_address?: string;
    }>('/v1/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Analytics API
  async getAnalytics() {
    return this.request<{
      total_queries: number;
      total_documents: number;
      avg_confidence: number;
      credits_used: number;
      recent_activity: Array<{
        type: 'query' | 'upload' | 'export' | 'notarization';
        description: string;
        timestamp: string;
        run_id?: string;
        matter_id?: string;
      }>;
    }>('/v1/analytics');
  }

  // Subscriptions API
  async getSubscription() {
    return this.request<{
      plan: string;
      credits_balance: number;
      renews_at?: string;
    }>('/v1/subscriptions');
  }
}

export const apiClient = new ApiClient();
export default apiClient;

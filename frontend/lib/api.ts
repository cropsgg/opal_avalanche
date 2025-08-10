const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://648cd54b91d1.ngrok-free.app';

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
            'ngrok-skip-browser-warning': 'true',
            ...(token && { 'Authorization': `Bearer ${token}` }),
          };
        }
      }

      return {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
      };
    } catch (error) {
      console.warn('Failed to get auth token:', error);
      return {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
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
    return this.request<{ status: string }>('/');
  }

  // FastAPI Endpoints - New Backend Integration
  
  // Get case types
  async getCaseTypes() {
    return this.request<string[]>('/case-types');
  }

  // Get jurisdictions
  async getJurisdictions() {
    return this.request<string[]>('/jurisdictions');
  }

  // Matters API - Updated for FastAPI
  async createMatter(data: { title: string }) {
    const formData = new FormData();
    formData.append('title', data.title);
    
    const response = await this.request<{ matter_id: string; title: string }>('/matters', {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
      },
      body: formData,
    });

    // Transform response to match expected format
    if (response.data && response.data.matter_id) {
      return {
        ...response,
        data: {
          id: response.data.matter_id,
          title: response.data.title
        }
      };
    }

    return response;
  }

  // Legacy methods - FastAPI doesn't implement these yet
  async getMatters() {
    // For now, return empty array since FastAPI doesn't have this endpoint
    return { data: [], status: 200 };
  }

  async getMatter(id: string) {
    // For now, return a mock matter since FastAPI doesn't have this endpoint
    return {
      data: {
        id,
        user_id: 'current-user',
        title: `Matter ${id}`,
        language: 'en' as const,
        created_at: new Date().toISOString(),
        documents_count: 0,
        last_analysis: undefined,
        status: 'active' as const
      },
      status: 200
    };
  }

  // Documents API - Updated for FastAPI
  async uploadDocument(matterId: string, file: File, court?: string, caseNumber?: string) {
    try {
      const headers = await this.getAuthHeaders();
      const formData = new FormData();
      formData.append('file', file);
      if (court) formData.append('court', court);
      if (caseNumber) formData.append('case_number', caseNumber);

      const response = await fetch(`${this.baseURL}/matters/${matterId}/documents`, {
        method: 'POST',
        headers: {
          'ngrok-skip-browser-warning': 'true',
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

  async getDocuments(matterId: string): Promise<ApiResponse<any[]>> {
    // For now, return empty array since FastAPI doesn't have this endpoint
    return { data: [], status: 200 };
  }

  // Chat API - Updated for FastAPI
  async sendChatMessage(data: {
    matter_id: string;
    message: string;
    facts?: string;
    case_type?: string;
    jurisdiction_region?: string;
  }) {
    const formData = new FormData();
    formData.append('matter_id', data.matter_id);
    formData.append('message', data.message);
    if (data.facts) formData.append('facts', data.facts);
    if (data.case_type) formData.append('case_type', data.case_type);
    if (data.jurisdiction_region) formData.append('jurisdiction_region', data.jurisdiction_region);

    return this.request<{
      answer: string;
      citations?: Array<{
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
    }>('/chat', {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
      },
      body: formData,
    });
  }

  // Chat Follow-up API
  async sendChatFollowup(data: {
    matter_id: string;
    run_id: string;
    message: string;
  }) {
    const formData = new FormData();
    formData.append('matter_id', data.matter_id);
    formData.append('run_id', data.run_id);
    formData.append('message', data.message);

    return this.request<{
      answer: string;
      citations?: Array<{
        authority_id: string;
        court: string;
        cite: string;
        para_ids: number[];
        title?: string;
        neutral_cite?: string;
        reporter_cite?: string;
      }>;
      run_id: string;
      confidence?: number;
    }>('/chat-followup', {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
      },
      body: formData,
    });
  }

  // Runs API - Updated for FastAPI
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
    }>(`/runs/${runId}`);
  }

  // Export API - Updated for FastAPI
  async exportRun(runId: string, format: string = 'docx') {
    const formData = new FormData();
    formData.append('format', format);

    return this.request<{ download_url: string }>(`/runs/${runId}/export`, {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
      },
      body: formData,
    });
  }

  // Test Arbiter API
  async testArbiter(legalSubdomain: string = 'contract') {
    const formData = new FormData();
    formData.append('legal_subdomain', legalSubdomain);

    return this.request<any>('/test-arbiter', {
      method: 'POST',
      headers: {
        'ngrok-skip-browser-warning': 'true',
      },
      body: formData,
    });
  }

  // Conversation History API
  async getConversationHistory(matterId: string) {
    return this.request<{
      messages: Array<{
        role: 'user' | 'assistant';
        content: string;
        timestamp: string;
        run_id?: string;
      }>;
    }>(`/conversation/${matterId}`);
  }

  async clearConversationHistory(matterId: string) {
    return this.request<{ success: boolean }>(`/conversation/${matterId}`, {
      method: 'DELETE',
    });
  }

  async exportConversationHistory(matterId: string) {
    return this.request<{ download_url: string }>(`/conversation/${matterId}/export`);
  }

  // Notarization API - Phase 2 Subnet
  async notarizeRun(runId: string, usePrivateSubnet: boolean = true) {
    const endpoint = usePrivateSubnet
      ? `/v1/subnet/runs/${runId}/notarize`
      : `/v1/runs/${runId}/notarize`;

    return this.request<{
      tx_hash: string;
      block_number: number;
      merkle_root: string;
      network: string;
      network_id: number;
      contract_address?: string;
      gas_used?: number;
      confirmation_count?: number;
      is_private_subnet?: boolean;
    }>(endpoint, {
      method: 'POST',
      body: JSON.stringify({
        include_audit_commit: true
      }),
    });
  }

  async getNotarization(runId: string, usePrivateSubnet: boolean = true) {
    const endpoint = usePrivateSubnet
      ? `/v1/subnet/notary/${runId}`
      : `/v1/notary/${runId}`;

    return this.request<{
      run_id: string;
      merkle_root: string;
      tx_hash: string;
      network: string;
      network_id: number;
      block_number: number;
      contract_address?: string;
      gas_used?: number;
      confirmation_count?: number;
      created_at: string;
      is_private_subnet?: boolean;
    }>(endpoint);
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

  // Search API
  async search(query: string, filters?: {
    type?: 'case' | 'statute' | 'document' | 'precedent';
    date_from?: string;
    date_to?: string;
    limit?: number;
    offset?: number;
  }) {
    const params = new URLSearchParams();
    params.append('q', query);

    if (filters) {
      if (filters.type) params.append('type', filters.type);
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.offset) params.append('offset', filters.offset.toString());
    }

    return this.request<{
      results: Array<{
        id: string;
        title: string;
        description: string;
        type: 'case' | 'statute' | 'document' | 'precedent';
        date?: string;
        source?: string;
        relevance_score?: number;
        url?: string;
        excerpt?: string;
      }>;
      total: number;
      query: string;
      took: number; // search time in ms
    }>(`/v1/search?${params.toString()}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;

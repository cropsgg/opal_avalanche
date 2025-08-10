import { API_CONFIG } from './config';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface Matter {
  id: string;
  title: string;
}

export interface ChatResponse {
  run_id: string;
  response: string;
  message?: string;
  agents?: string[];
  explainability?: string;
  explanation?: string;
  citations?: any[];
}

export interface CaseTypesResponse {
  case_types: string[];
}

export interface JurisdictionsResponse {
  jurisdictions: string[];
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options.headers as Record<string, string>,
      };

      // Add ngrok-skip-browser-warning header if using ngrok
      if (this.baseUrl.includes('ngrok-free.app') || this.baseUrl.includes('ngrok.io')) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  private async formRequest<T>(
    endpoint: string,
    formData: Record<string, string>
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const headers: Record<string, string> = {};

      // Add ngrok-skip-browser-warning header if using ngrok
      if (this.baseUrl.includes('ngrok-free.app') || this.baseUrl.includes('ngrok.io')) {
        headers['ngrok-skip-browser-warning'] = 'true';
      }

      // Create FormData for multipart/form-data (matching your curl -F format)
      const form = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        form.append(key, value);
      });

      const response = await fetch(url, {
        method: 'POST',
        headers, // Don't set Content-Type, let browser set it for FormData
        body: form,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error(`API form request failed for ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // Chat methods
  async sendChat(matterId: string, message: string, caseType?: string, jurisdiction?: string): Promise<ApiResponse<ChatResponse>> {
    const formData: Record<string, string> = {
      matter_id: matterId,
      message: message,
    };

    if (caseType) formData.case_type = caseType;
    if (jurisdiction) formData.jurisdiction = jurisdiction; // Changed from jurisdiction_region to jurisdiction

    return this.formRequest<ChatResponse>(API_CONFIG.ENDPOINTS.CHAT, formData);
  }

  async sendFollowup(matterId: string, runId: string, message: string): Promise<ApiResponse<ChatResponse>> {
    return this.formRequest<ChatResponse>(API_CONFIG.ENDPOINTS.CHAT_FOLLOWUP, {
      matter_id: matterId,
      run_id: runId,
      message: message,
    });
  }

  // Matter methods
  async createMatter(title: string): Promise<ApiResponse<Matter>> {
    return this.formRequest<Matter>(API_CONFIG.ENDPOINTS.MATTERS, { title });
  }

  // Options methods
  async getCaseTypes(): Promise<ApiResponse<CaseTypesResponse>> {
    return this.request<CaseTypesResponse>(API_CONFIG.ENDPOINTS.CASE_TYPES);
  }

  async getJurisdictions(): Promise<ApiResponse<JurisdictionsResponse>> {
    return this.request<JurisdictionsResponse>(API_CONFIG.ENDPOINTS.JURISDICTIONS);
  }

  // Conversation methods
  async getConversationHistory(matterId: string) {
    return this.request(`${API_CONFIG.ENDPOINTS.CONVERSATION}/${matterId}`);
  }

  async clearConversationHistory(matterId: string) {
    return this.request(`${API_CONFIG.ENDPOINTS.CONVERSATION}/${matterId}`, {
      method: 'DELETE',
    });
  }

  // Test methods
  async testArbiter(legalSubdomain: string = 'contract') {
    return this.formRequest(API_CONFIG.ENDPOINTS.TEST_ARBITER, {
      legal_subdomain: legalSubdomain,
    });
  }
}

export const apiClient = new ApiClient();

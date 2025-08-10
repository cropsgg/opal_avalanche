// Core types for OPAL application

export interface User {
  id: string;
  clerk_id: string;
  email: string;
  role: 'lawyer' | 'admin' | 'paralegal' | 'client';
  wallet_address?: string;
  created_at: string;
  updated_at: string;
}

export interface Matter {
  id: string;
  user_id: string;
  title: string;
  language: 'en' | 'hi';
  created_at: string;
  documents_count?: number;
  last_analysis?: string;
  status?: 'active' | 'archived' | 'draft';
}

export interface Document {
  id: string;
  matter_id: string;
  storage_path: string;
  filetype: string;
  size: number;
  uploaded_by?: string;
  ocr_status: 'pending' | 'processing' | 'completed' | 'failed' | string;
  checksum_sha256?: string;
  created_at: string;
  name?: string;
}

export interface Authority {
  id: string;
  court: string;
  title: string;
  neutral_cite?: string;
  reporter_cite?: string;
  date?: string;
  bench?: string;
  url?: string;
  metadata_json: Record<string, any>;
  storage_path: string;
  hash_keccak256: string;
  created_at: string;
}

export interface Citation {
  authority_id: string;
  court: string;
  cite: string;
  para_ids: number[];
  title?: string;
  neutral_cite?: string;
  reporter_cite?: string;
  relevance?: 'High' | 'Medium' | 'Low';
  snippet?: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  evidence?: EvidenceItem[];
  run_id?: string;
  confidence?: number;
  mode?: ChatMode;
}

export type ChatMode = 'general' | 'precedent' | 'limitation' | 'draft';

export interface ChatRequest {
  matterId: string;
  message: string;
  mode: ChatMode;
  filters?: SearchFilters;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  evidence_merkle_root?: string;
  run_id: string;
  confidence?: number;
  agent_votes?: AgentVote[];
}

export interface AgentVote {
  agent: string;
  decision_json: Record<string, any>;
  confidence: number;
  aligned: boolean;
  reasoning?: string;
}

export interface SearchFilters {
  court?: string[];
  year_from?: number;
  year_to?: number;
  judge?: string[];
  statute_tags?: string[];
  has_citation?: boolean;
  jurisdiction?: string;
}

export interface Run {
  id: string;
  query_id: string;
  answer_text: string;
  confidence: number;
  retrieval_set_json: any[];
  created_at: string;
  agent_votes?: AgentVote[];
  notarization?: NotarizationProof;
}

export interface NotarizationProof {
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
}

export interface ExportOptions {
  format: 'pdf' | 'docx' | 'json';
  include_reasoning?: boolean;
  include_citations?: boolean;
}

export interface BillingAccount {
  user_id: string;
  plan: 'starter' | 'professional' | 'enterprise';
  credits_balance: number;
  renews_at?: string;
}

export interface Analytics {
  total_queries: number;
  total_documents: number;
  avg_confidence: number;
  credits_used: number;
  recent_activity: Activity[];
}

export interface Activity {
  type: 'query' | 'upload' | 'export' | 'notarization';
  description: string;
  timestamp: string;
  run_id?: string;
  matter_id?: string;
}

export interface EvidenceItem {
  case: string;
  citation: string;
  relevance: 'High' | 'Medium' | 'Low';
  paragraphs: string[];
  snippet?: string;
  authority_id: string;
  court: string;
  date?: string;
}

export interface MerkleBundle {
  runId: string;
  authorities: Array<{
    authorityId: string;
    neutralCite: string;
    reporter: string;
    paras: number[];
    paraHashes: string[];
  }>;
  metadata: {
    court: string;
    date: string;
  };
  merkleRoot: string;
  txHash: string;
  network: string;
}

// UI State types
export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  currentMode: ChatMode;
  selectedEvidence?: EvidenceItem;
  filters: SearchFilters;
}

export interface MatterState {
  currentMatter?: Matter;
  documents: Document[];
  isProcessing: boolean;
  uploadProgress?: number;
}

export interface NotarizationState {
  isNotarizing: boolean;
  proof?: NotarizationProof;
  error?: string;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}

// Form types
export interface MatterCreationForm {
  title: string;
  language: 'en' | 'hi';
  description?: string;
}

export interface DocumentUploadForm {
  files: File[];
  matterId: string;
}

// Constants
export const SUPPORTED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'image/png',
  'image/jpeg',
] as const;

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const MAX_FILES_PER_MATTER = 100;

export const COURTS = [
  'Supreme Court of India',
  'Delhi High Court',
  'Bombay High Court',
  'Calcutta High Court',
  'Madras High Court',
  'Karnataka High Court',
  'Kerala High Court',
  'Allahabad High Court',
  'Rajasthan High Court',
  'Gujarat High Court',
  'Punjab and Haryana High Court',
  'Andhra Pradesh High Court',
  'Telangana High Court',
  'Orissa High Court',
  'Jharkhand High Court',
  'Chhattisgarh High Court',
  'Uttarakhand High Court',
  'Himachal Pradesh High Court',
  'Jammu and Kashmir High Court',
  'Gauhati High Court',
  'Patna High Court',
  'Madhya Pradesh High Court',
  'Tripura High Court',
  'Manipur High Court',
  'Meghalaya High Court',
  'Sikkim High Court',
] as const;

export const AGENTS = [
  'statute',
  'precedent',
  'limitation',
  'risk',
  'devil',
  'ethics',
  'drafting',
] as const;

export type Agent = typeof AGENTS[number];
export type Court = typeof COURTS[number];

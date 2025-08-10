// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// Document Types
export interface Document {
  title?: string;
  content: string;
  metadata?: Record<string, any>;
}

export interface ProcessedDocument {
  index: number;
  title: string;
  content_preview: string;
  content_length: number;
  hash: string;
  metadata: Record<string, any>;
}

export interface DocumentHashRequest {
  documents: Document[];
}

export interface DocumentHashResponse {
  documents: ProcessedDocument[];
  merkle_root: string;
  total_documents: number;
  gas_estimate: GasEstimate;
}

export interface GasEstimate {
  notary: {
    gas_limit: number;
    gas_price_gwei: number;
    cost_wei: number;
    cost_avax: string;
  };
  commit: {
    gas_limit: number;
    gas_price_gwei: number;
    cost_wei: number;
    cost_avax: string;
    estimated_data_size_kb: number;
  };
  total: {
    gas_limit: number;
    cost_wei: number;
    cost_avax: string;
  };
  note: string;
}

// Blockchain Types
export interface SubnetNotarizeRequest {
  run_id: string;
  documents: Document[];
  retrieval_set?: EvidenceItem[];
  include_audit_commit?: boolean;
  metadata?: Record<string, any>;
}

export interface SubnetNotarizeResponse {
  run_id: string;
  merkle_root: string;
  notary_tx_hash: string;
  notary_block_number: number;
  commit_tx_hash?: string;
  commit_block_number?: number;
  network: string;
  gas_used: Record<string, number>;
  total_cost: string;
}

export interface NotarizationStatus {
  run_id: string;
  merkle_root?: string;
  verified: boolean;
  network: string;
  error?: string;
}

export interface AuditData {
  run_id: string;
  audit_data?: any;
  encrypted: boolean;
  available: boolean;
  ciphertext_size?: number;
}

export interface BlockchainStatus {
  network: string;
  connected: boolean;
  chain_id?: number;
  latest_block?: number;
  contract_addresses: Record<string, string>;
}

// Search Types
export interface QdrantSearchRequest {
  query_text: string;
  top_k: number;
  filters: SearchFilters;
}

export interface SearchFilters {
  court?: string;
  date_from?: string;
  date_to?: string;
  statute_tags?: string[];
  year?: number[];
}

export interface QdrantSearchResponse {
  results: SearchResult[];
  total_found: number;
  search_time_ms: number;
}

export interface SearchResult {
  id: string;
  score: number;
  payload: {
    court?: string;
    title?: string;
    text?: string;
    date?: string;
    authority_id?: string;
    statute_tags?: string[];
    [key: string]: any;
  };
}

export interface EvidenceItem {
  text: string;
  source?: string;
  authority_id?: string;
  para_ids?: number[];
  court?: string;
  title?: string;
  date?: string;
}

// Health and Status Types
export interface HealthStatus {
  service: string;
  version: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    qdrant?: ComponentStatus;
    subnet?: ComponentStatus;
    [key: string]: ComponentStatus | undefined;
  };
}

export interface ComponentStatus {
  status: 'healthy' | 'unhealthy';
  connected?: boolean;
  error?: string;
  [key: string]: any;
}

export interface Metrics {
  qdrant?: {
    name?: string;
    vectors_count?: number;
    points_count?: number;
    status?: string;
    error?: string;
  };
  timestamp?: string;
}

// UI Component Types
export interface NotarizeFormData {
  runId: string;
  evidenceText: string;
  includeAuditCommit: boolean;
}

export interface SearchFormData {
  query: string;
  topK: number;
  court: string;
  dateFrom: string;
  dateTo: string;
  statuteTags: string;
}

// Release Registration
export interface ReleaseRegistration {
  version: string;
  source_hash: string;
  artifact_hash: string;
  tx_hash?: string;
  block_number?: number;
  registered?: boolean;
}

// Knowledge Graph Types
export interface GraphNode {
  id: string;
  label: string;
  content: string;
  metadata: Record<string, any>;
  position: { x: number; y: number };
  cluster: number;
  size: number;
  color: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  label?: string;
}

export interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  clusters: Record<string, any>;
  metadata: Record<string, any>;
}

export interface GraphFilterRequest {
  search_query?: string;
  cluster_id?: number;
  limit: number;
  min_similarity: number;
}

export interface GraphStats {
  collection_exists: boolean;
  total_points?: number;
  vector_size?: number | string;
  payload_keys?: string[];
  collection_status?: string;
  optimizer_status?: string;
  available_collections?: string[];
}

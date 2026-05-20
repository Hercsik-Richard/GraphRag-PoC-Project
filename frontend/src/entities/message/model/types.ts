/**
 * Message entity types
 */
import type { ModelProvider } from "@/shared/config/constants";

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  retrieved_entities?: RetrievedEntity[] | null;
  retrieved_relationships?: RetrievedRelationship[] | null;
  retrieved_sources?: RetrievedSource[] | null;
  search_mode_used?: ResolvedSearchMode | null;
  search_mode_reason?: string | null;
}

export type SearchMode = 'auto' | 'local' | 'global' | 'drift' | 'source' | 'hybrid';
export type ResolvedSearchMode = 'local' | 'global' | 'drift' | 'source' | 'hybrid';

export interface RetrievedEntity {
  id: string;
  title?: string;
  type?: string;
  description?: string;
  index?: number; // Original GraphRAG index for citation matching
  [key: string]: unknown;
}

export interface RetrievedRelationship {
  id: string;
  source: string;
  target: string;
  description: string;
  weight: number;
  index?: number; // Original GraphRAG index for citation matching
  [key: string]: unknown;
}

export interface RetrievedSource {
  id: string;
  text_unit_id: string;
  source: string;
  excerpt: string;
  score?: number;
  index?: number;
  document_ids?: string[];
  [key: string]: unknown;
}

export interface QueryRequest {
  question: string;
  search_mode?: SearchMode;
  query_model_provider?: ModelProvider;
  query_chat_provider?: ModelProvider;
  query_embed_provider?: ModelProvider;
}

export interface QueryResponse {
  message: Message;
  retrieved_graph?: {
    entities: RetrievedEntity[];
    relationships: RetrievedRelationship[];
    sources?: RetrievedSource[];
  };
  search_mode_used: ResolvedSearchMode;
  search_mode_reason: string;
}

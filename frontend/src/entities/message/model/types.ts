/**
 * Message entity types
 */

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  retrieved_entities?: RetrievedEntity[] | null;
  retrieved_relationships?: RetrievedRelationship[] | null;
  search_mode_used?: ResolvedSearchMode | null;
  search_mode_reason?: string | null;
}

export type SearchMode = 'auto' | 'local' | 'global' | 'drift' | 'source';
export type ResolvedSearchMode = 'local' | 'global' | 'drift' | 'source';

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

export interface QueryRequest {
  question: string;
  search_mode?: SearchMode;
}

export interface QueryResponse {
  message: Message;
  retrieved_graph?: {
    entities: RetrievedEntity[];
    relationships: RetrievedRelationship[];
  };
  search_mode_used: ResolvedSearchMode;
  search_mode_reason: string;
}

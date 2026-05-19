/**
 * Message entity types
 */

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  retrieved_entities?: RetrievedEntity[];
  retrieved_relationships?: RetrievedRelationship[];
}

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
}

export interface QueryResponse {
  message: Message;
  retrieved_graph?: {
    entities: RetrievedEntity[];
    relationships: RetrievedRelationship[];
  };
}

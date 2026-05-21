/**
 * Conversation entity types
 */

export interface Conversation {
  id: string;
  graph_id: string | null;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface CreateConversationRequest {
  title: string;
  graph_id?: string | null;
}

export type CreateConversationResponse = Conversation;

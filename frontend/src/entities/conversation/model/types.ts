/**
 * Conversation entity types
 */

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface CreateConversationRequest {
  title: string;
}

export type CreateConversationResponse = Conversation;

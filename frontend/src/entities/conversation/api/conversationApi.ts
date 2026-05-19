/**
 * Conversation API hooks using SWR
 */
import useSWR from 'swr';
import useSWRMutation from 'swr/mutation';
import { apiClient } from '@/shared/api/client';
import { API_ENDPOINTS } from '@/shared/config/constants';
import type { Conversation, CreateConversationRequest } from '@/entities/conversation';
import type { Message } from '@/entities/message';

/**
 * Fetcher function for SWR
 */
async function fetcher<T>(url: string): Promise<T> {
  const response = await apiClient.get<T>(url);
  return response.data;
}

/**
 * Hook to fetch all conversations
 */
export function useConversations() {
  const { data, error, isLoading, mutate } = useSWR<Conversation[]>(
    API_ENDPOINTS.CHAT.CONVERSATIONS,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
    }
  );

  return {
    conversations: data,
    isLoading,
    isError: error,
    mutate,
  };
}

/**
 * Hook to fetch a specific conversation's messages
 */
export function useConversation(conversationId: string | null) {
  const { data, error, isLoading, mutate } = useSWR<Message[]>(
    conversationId ? API_ENDPOINTS.CHAT.MESSAGES(conversationId) : null,
    fetcher,
    {
      revalidateOnFocus: false,
      refreshInterval: 0,
    }
  );

  return {
    messages: data,
    isLoading,
    isError: error,
    mutate,
  };
}

/**
 * Hook to create a new conversation
 */
export function useCreateConversation() {
  const { trigger, isMutating } = useSWRMutation(
    API_ENDPOINTS.CHAT.CONVERSATIONS,
    async (url: string, { arg }: { arg: CreateConversationRequest }) => {
      const response = await apiClient.post<Conversation>(url, arg);
      return response.data;
    }
  );

  return {
    createConversation: trigger,
    isCreating: isMutating,
  };
}

/**
 * Hook to delete a conversation
 */
export function useDeleteConversation() {
  const { trigger, isMutating } = useSWRMutation(
    API_ENDPOINTS.CHAT.CONVERSATIONS,
    async (_url: string, { arg }: { arg: string }) => {
      await apiClient.delete(API_ENDPOINTS.CHAT.CONVERSATION(arg));
    }
  );

  return {
    deleteConversation: trigger,
    isDeleting: isMutating,
  };
}

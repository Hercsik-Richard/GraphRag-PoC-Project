/**
 * Send message API functionality
 */
import useSWRMutation from 'swr/mutation';
import { apiClient } from '@/shared/api/client';
import { API_ENDPOINTS } from '@/shared/config/constants';
import type { QueryRequest, QueryResponse } from '@/entities/message';

/**
 * Hook to send a message (query) in a conversation
 */
export function useSendMessage(conversationId: string | null) {
  const { trigger, isMutating, error } = useSWRMutation(
    conversationId ? API_ENDPOINTS.CHAT.QUERY(conversationId) : null,
    async (url: string, { arg }: { arg: QueryRequest }) => {
      const response = await apiClient.post<QueryResponse>(url, arg);
      return response.data;
    }
  );

  return {
    sendMessage: trigger,
    isSending: isMutating,
    error,
  };
}

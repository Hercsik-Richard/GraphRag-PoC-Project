/**
 * Upload document API functionality
 */
import useSWRMutation from 'swr/mutation';
import { apiClient } from '@/shared/api/client';
import { API_ENDPOINTS } from '@/shared/config/constants';

export interface UploadResponse {
  status: string;
  document_id: string;
  filename: string;
  progress: number;
  message: string;
  stats: {
    entity_count: number;
    relationship_count: number;
  } | null;
}

export interface IndexProgress {
  document_id: string;
  filename: string;
  status: string;
  progress: number;
  message: string;
  chunks_processed: number | null;
  total_chunks: number | null;
  current_chunk: number | null;
  current_chunk_progress: number | null;
  entity_count: number | null;
  relationship_count: number | null;
  error: string | null;
}

/**
 * Hook to upload a document for indexing
 */
export function useUploadDocument() {
  const { trigger, isMutating, error } = useSWRMutation(
    API_ENDPOINTS.INDEX.UPLOAD,
    async (url: string, { arg }: { arg: File }) => {
      const formData = new FormData();
      formData.append('file', arg);

      const response = await apiClient.post<UploadResponse>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes for indexing
      });

      return response.data;
    }
  );

  return {
    uploadDocument: trigger,
    isUploading: isMutating,
    error,
  };
}

export async function getIndexProgress(documentId: string) {
  const response = await apiClient.get<IndexProgress>(
    API_ENDPOINTS.INDEX.PROGRESS(documentId)
  );

  return response.data;
}

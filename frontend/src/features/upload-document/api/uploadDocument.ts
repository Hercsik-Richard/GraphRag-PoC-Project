/**
 * Upload document API functionality
 */
import useSWRMutation from 'swr/mutation';
import useSWR from 'swr';
import { apiClient } from '@/shared/api/client';
import { API_ENDPOINTS, type ModelProvider } from '@/shared/config/constants';

export interface UploadDocumentInput {
  file: File;
  indexChatProvider: ModelProvider;
  indexEmbedProvider: ModelProvider;
}

export interface UploadResponse {
  status: string;
  document_id: string;
  graph_id: string;
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
  graph_id: string;
  filename: string;
  status: string;
  progress: number;
  message: string;
  chunks_processed: number | null;
  total_chunks: number | null;
  current_chunk: number | null;
  current_chunk_progress: number | null;
  phase: string | null;
  phase_processed: number | null;
  phase_total: number | null;
  phase_progress: number | null;
  entity_count: number | null;
  relationship_count: number | null;
  error: string | null;
}

export interface IndexedDocumentStatus {
  id: string;
  graph_id: string | null;
  filename: string;
  indexed_at: string;
  status: string;
  entity_count: number | null;
  relationship_count: number | null;
}

export interface IndexStatusResponse {
  documents: IndexedDocumentStatus[];
  total_documents: number;
}

export interface DeleteCurrentIndexResponse {
  status: string;
  message: string;
}

export interface IndexedGraphStatus {
  id: string;
  name: string;
  source_filename: string;
  status: string;
  entity_count: number | null;
  relationship_count: number | null;
  index_chat_provider: string | null;
  index_embed_provider: string | null;
  index_chat_model: string | null;
  index_embed_model: string | null;
  is_active: boolean;
  created_at: string;
  indexed_at: string | null;
  activated_at: string | null;
  error: string | null;
}

export interface IndexedGraphListResponse {
  graphs: IndexedGraphStatus[];
  active_graph_id: string | null;
  total_graphs: number;
}

export interface ActivateGraphResponse {
  graph: IndexedGraphStatus;
}

async function fetcher<T>(url: string): Promise<T> {
  const response = await apiClient.get<T>(url);
  return response.data;
}

/**
 * Hook to upload a document for indexing
 */
export function useUploadDocument() {
  const { trigger, isMutating, error } = useSWRMutation(
    API_ENDPOINTS.INDEX.UPLOAD,
    async (url: string, { arg }: { arg: UploadDocumentInput }) => {
      const formData = new FormData();
      formData.append('file', arg.file);
      formData.append('index_chat_provider', arg.indexChatProvider);
      formData.append('index_embed_provider', arg.indexEmbedProvider);

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

export function useIndexStatus() {
  const { data, error, isLoading, mutate } = useSWR<IndexStatusResponse>(
    API_ENDPOINTS.INDEX.STATUS,
    fetcher,
    {
      revalidateOnFocus: false,
      refreshInterval: 30000,
    }
  );

  return {
    indexStatus: data,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useIndexedGraphs() {
  const { data, error, isLoading, mutate } = useSWR<IndexedGraphListResponse>(
    API_ENDPOINTS.INDEX.GRAPHS,
    fetcher,
    {
      revalidateOnFocus: false,
      refreshInterval: 30000,
    }
  );

  return {
    graphList: data,
    graphs: data?.graphs,
    activeGraphId: data?.active_graph_id ?? null,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useActiveGraph() {
  const { data, error, isLoading, mutate } = useSWR<IndexedGraphStatus | null>(
    API_ENDPOINTS.INDEX.ACTIVE_GRAPH,
    fetcher,
    {
      revalidateOnFocus: false,
      refreshInterval: 30000,
    }
  );

  return {
    activeGraph: data,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useActivateGraph() {
  const { trigger, isMutating, error } = useSWRMutation(
    API_ENDPOINTS.INDEX.GRAPHS,
    async (_url: string, { arg }: { arg: string }) => {
      const response = await apiClient.post<ActivateGraphResponse>(
        API_ENDPOINTS.INDEX.ACTIVATE_GRAPH(arg)
      );
      return response.data;
    }
  );

  return {
    activateGraph: trigger,
    isActivating: isMutating,
    error,
  };
}

export function useDeleteCurrentIndex() {
  const { trigger, isMutating, error } = useSWRMutation(
    API_ENDPOINTS.INDEX.CURRENT,
    async (url: string) => {
      const response = await apiClient.delete<DeleteCurrentIndexResponse>(url);
      return response.data;
    }
  );

  return {
    deleteCurrentIndex: trigger,
    isDeleting: isMutating,
    error,
  };
}

export async function getIndexProgress(documentId: string) {
  const response = await apiClient.get<IndexProgress>(
    API_ENDPOINTS.INDEX.PROGRESS(documentId)
  );

  return response.data;
}

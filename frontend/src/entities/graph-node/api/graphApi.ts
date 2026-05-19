/**
 * Graph data API hooks using SWR
 */
import useSWR from 'swr';
import { apiClient } from '@/shared/api/client';
import { API_ENDPOINTS } from '@/shared/config/constants';
import type { GraphApiResponse, GraphStats } from '@/entities/graph-node';

/**
 * Fetcher function for SWR
 */
async function fetcher<T>(url: string): Promise<T> {
  const response = await apiClient.get<T>(url);
  return response.data;
}

/**
 * Hook to fetch full graph data
 */
export function useGraphData() {
  const { data, error, isLoading, mutate } = useSWR<GraphApiResponse>(
    API_ENDPOINTS.GRAPH.FULL,
    fetcher,
    {
      revalidateOnFocus: false,
      refreshInterval: 0, // Don't auto-refresh, only on manual trigger
    }
  );

  return {
    graphData: data,
    isLoading,
    isError: error,
    mutate,
  };
}

/**
 * Hook to fetch graph statistics
 */
export function useGraphStats() {
  const { data, error, isLoading, mutate } = useSWR<GraphStats>(
    API_ENDPOINTS.GRAPH.STATS,
    fetcher,
    {
      revalidateOnFocus: false,
      refreshInterval: 30000, // Refresh every 30 seconds
    }
  );

  return {
    stats: data,
    isLoading,
    isError: error,
    mutate,
  };
}
